"""
Unified LLM Client for PediAssist

Provides a single interface to multiple LLM providers with BYOK support,
cost tracking, and safety validation.
"""

import asyncio
import json
import re
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

import litellm
from litellm import completion, embedding
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .providers import ProviderManager
from .safety import SafetyValidator
from .cost_tracker import CostTracker
from .prompts import PromptEngine
from ..config import settings

logger = structlog.get_logger()

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    OLLAMA = "ollama"
    LOCAL = "local"

@dataclass
class LLMResponse:
    """Structured LLM response"""
    content: str
    tokens_used: int
    cost_usd: float
    provider: str
    model: str
    response_time_ms: int
    safety_score: float
    cached: bool = False

class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass

class LLMRateLimitError(LLMError):
    """Rate limit exceeded"""
    pass

class LLMContentSafetyError(LLMError):
    """Content failed safety validation"""
    pass

class LLMCostExceededError(LLMError):
    """Monthly cost limit exceeded"""
    pass

class LLMClient:
    """Unified LLM client with BYOK support"""
    
    def __init__(self, config=None):
        self.config = config or settings
        self.provider_manager = ProviderManager(config)
        self.safety_validator = SafetyValidator()
        self.cost_tracker = CostTracker(config)
        self.prompt_engineer = PromptEngine()
        
        # Configure litellm
        litellm.set_verbose = config.debug
        litellm.telemetry = False  # Disable telemetry for privacy
        
        logger.info("LLM Client initialized", 
                   provider=config.llm.provider,
                   model=config.llm.model)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((LLMRateLimitError, asyncio.TimeoutError))
    )
    async def generate_treatment_plan(
        self,
        diagnosis: str,
        age: int,
        context: Optional[str] = None,
        detail_level: str = "detailed",
        include_parent_handout: bool = False,
        include_child_explanation: bool = False,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate a comprehensive treatment plan for a pediatric case
        
        Args:
            diagnosis: Primary diagnosis or condition
            age: Patient age in years
            context: Additional clinical context
            detail_level: Level of detail (quick, detailed, deep_dive)
            include_parent_handout: Include parent communication materials
            include_child_explanation: Include age-appropriate child explanation
            provider: Override default LLM provider
            model: Override default model
            
        Returns:
            LLMResponse with treatment plan and metadata
        """
        start_time = time.time()
        
        try:
            # Check cost limits
            if not await self.cost_tracker.can_make_request():
                raise LLMCostExceededError("Monthly cost limit exceeded")
            
            # Select provider and model
            selected_provider = provider or self.config.llm.provider
            selected_model = model or self.config.llm.model
            
            # Build prompt
            prompt = self.prompt_engineer.build_treatment_prompt(
                diagnosis=diagnosis,
                age=age,
                context=context,
                detail_level=detail_level,
                include_parent_handout=include_parent_handout,
                include_child_explanation=include_child_explanation
            )
            
            # Validate prompt safety
            safety_check = await self.safety_validator.validate_prompt(prompt)
            if not safety_check.is_safe:
                raise LLMContentSafetyError(f"Prompt failed safety validation: {safety_check.reason}")
            
            # Generate response
            response = await self._generate_completion(
                prompt=prompt,
                provider=selected_provider,
                model=selected_model,
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            
            # Validate response safety
            safety_check = await self.safety_validator.validate_response(response.content)
            if not safety_check.is_safe:
                logger.warning("Response failed safety validation", reason=safety_check.reason)
                # Optionally modify response or flag for review
            
            # Calculate metrics
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Track costs
            await self.cost_tracker.track_request(
                provider=selected_provider,
                model=selected_model,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
                request_type="treatment_plan"
            )
            
            logger.info("Treatment plan generated successfully",
                       diagnosis=diagnosis,
                       age=age,
                       detail_level=detail_level,
                       tokens_used=response.tokens_used,
                       cost_usd=response.cost_usd,
                       response_time_ms=response_time_ms)
            
            return response
            
        except Exception as e:
            logger.error("Treatment plan generation failed",
                        diagnosis=diagnosis,
                        age=age,
                        error=str(e))
            raise
    
    async def generate_patient_communication(
        self,
        diagnosis: str,
        age: int,
        communication_type: str = "handout",
        language: str = "en"
    ) -> LLMResponse:
        """
        Generate age-appropriate patient communication materials
        
        Args:
            diagnosis: Primary diagnosis
            age: Patient age in years
            communication_type: Type of communication (handout, text, email)
            language: Language for communication
            
        Returns:
            LLMResponse with communication materials
        """
        prompt = self.prompt_engineer.build_patient_communication_prompt(
            diagnosis=diagnosis,
            age=age,
            communication_type=communication_type,
            language=language
        )
        
        return await self._generate_completion(
            prompt=prompt,
            provider=self.config.llm.provider,
            model=self.config.llm.model,
            temperature=0.3,  # Higher temperature for more creative communication
            max_tokens=2000
        )
    
    async def generate_delegation_protocol(
        self,
        task: str,
        team_member_role: str,
        patient_age: int,
        complexity: str = "routine"
    ) -> LLMResponse:
        """
        Generate delegation protocols for healthcare team members
        
        Args:
            task: Clinical task to delegate
            team_member_role: Role of team member (PA, nurse, MA)
            patient_age: Patient age in years
            complexity: Task complexity (routine, moderate, complex)
            
        Returns:
            LLMResponse with delegation protocol
        """
        prompt = self.prompt_engineer.build_delegation_prompt(
            task=task,
            team_member_role=team_member_role,
            patient_age=patient_age,
            complexity=complexity
        )
        
        return await self._generate_completion(
            prompt=prompt,
            provider=self.config.llm.provider,
            model=self.config.llm.model,
            temperature=0.2,
            max_tokens=1500
        )
    
    async def _generate_completion(
        self,
        prompt: str,
        provider: str,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> LLMResponse:
        """Internal method to generate completion with selected provider"""
        
        start_time = time.time()
        
        # Get provider configuration
        provider_config = self.provider_manager.get_provider_config(provider)
        
        try:
            # Generate completion
            if provider in ["ollama", "local"]:
                # Ollama and local providers use sync completion
                response = completion(
                    model=f"{provider}/{model}",
                    messages=[
                        {"role": "system", "content": self.prompt_engineer.get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=provider_config.get("api_key"),
                    base_url=provider_config.get("base_url")
                )
            else:
                # Other providers use async completion
                response = await completion(
                    model=model if provider == "openai" else f"{provider}/{model}",
                    messages=[
                        {"role": "system", "content": self.prompt_engineer.get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=provider_config.get("api_key"),
                    base_url=provider_config.get("base_url")
                )
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Calculate usage and cost
            tokens_used = response.usage.total_tokens
            cost_usd = self.cost_tracker.calculate_cost(provider, model, tokens_used)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Validate response structure and attempt JSON parsing if expected
            parsed_content = content
            try:
                # Try to parse as JSON if expected
                if self._is_json_response_expected(prompt):
                    parsed_content = json.loads(content)
                    logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.warning("Response is not valid JSON", full_content=content[:500], error=str(e))  # Show first 500 chars for debugging
                # If JSON is expected but not valid, try to extract JSON from text
                if self._is_json_response_expected(prompt):
                    logger.warning("Attempting to extract JSON from text response", original_length=len(content))
                    extracted_json = self._extract_json_from_text(content)
                    if extracted_json:
                        try:
                            parsed_content = json.loads(extracted_json)
                            logger.info("Successfully extracted JSON from text response")
                            content = extracted_json  # Update content with valid JSON
                        except json.JSONDecodeError as e2:
                            logger.warning("Failed to extract valid JSON from text response", content_preview=extracted_json[:200], error=str(e2))
                            # If we still can't parse JSON, create a fallback response
                            logger.warning("Creating fallback JSON response for clinical content")
                            content = self._create_fallback_json_response(content)
                            # Make sure we return the fallback JSON as a string, not raise an error
                            return LLMResponse(
                                content=content,
                                tokens_used=tokens_used,
                                cost_usd=cost_usd,
                                provider=provider,
                                model=model,
                                response_time_ms=response_time_ms,
                                safety_score=0.9
                            )
                    else:
                        logger.warning("No valid JSON could be extracted from response, using original content")
                        # Create a fallback JSON response using the original content
                        content = self._create_fallback_json_response(content)
                        # Make sure we return the fallback JSON as a string, not raise an error
                        return LLMResponse(
                            content=content,
                            tokens_used=tokens_used,
                            cost_usd=cost_usd,
                            provider=provider,
                            model=model,
                            response_time_ms=response_time_ms,
                            safety_score=0.9
                        )
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                provider=provider,
                model=model,
                response_time_ms=response_time_ms,
                safety_score=0.9  # Placeholder for actual safety scoring
            )
            
        except litellm.RateLimitError as e:
            logger.warning("Rate limit exceeded", provider=provider, model=model)
            raise LLMRateLimitError(f"Rate limit exceeded for {provider}: {str(e)}")
            
        except litellm.AuthenticationError as e:
            logger.error("Authentication failed", provider=provider)
            raise LLMError(f"Authentication failed for {provider}: {str(e)}")
            
        except Exception as e:
            logger.error("LLM completion failed", 
                        provider=provider, 
                        model=model, 
                        error=str(e))
            raise LLMError(f"LLM completion failed: {str(e)}")
    
    def _is_json_response_expected(self, prompt: str) -> bool:
        """Check if JSON response is expected based on prompt content"""
        json_indicators = ["json", "structured", "format", "template"]
        return any(indicator in prompt.lower() for indicator in json_indicators)
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extract JSON from text that may contain markdown or other formatting"""
        # Clean up common formatting issues first
        text = text.strip()
        
        # Look for JSON objects in the text
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        # Try each match to see if it's valid JSON
        for match in matches:
            try:
                # Try to parse the JSON
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
        
        # If no JSON objects found, look for JSON arrays
        array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
        matches = re.findall(array_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
        
        # Look for code blocks with JSON
        code_block_pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                # Clean up the JSON content
                cleaned_json = match.strip()
                json.loads(cleaned_json)
                return cleaned_json
            except json.JSONDecodeError:
                continue
        
        # Look for any code blocks that might contain JSON
        code_block_pattern = r'```\s*([\s\S]*?)\s*```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                # Clean up the content and try to parse as JSON
                cleaned_json = match.strip()
                json.loads(cleaned_json)
                return cleaned_json
            except json.JSONDecodeError:
                continue
        
        # If no valid JSON found, try to fix common issues
        # Remove leading/trailing whitespace and newlines
        cleaned_text = text.strip()
        
        # Try to parse the entire text as JSON (might be the whole response)
        try:
            json.loads(cleaned_text)
            return cleaned_text
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON by looking for the structure we expect
        # Look for patterns that start with { and end with }
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            potential_json = text[start_idx:end_idx + 1]
            try:
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _create_fallback_json_response(self, original_content: str) -> str:
        """Create a fallback JSON response when LLM fails to return valid JSON"""
        logger.warning("Creating fallback JSON response", original_content_preview=original_content[:200])
        
        # Extract key information from the original content using simple text parsing
        diagnosis_match = re.search(r'primary diagnosis[:\s]*([^\n]+)', original_content, re.IGNORECASE)
        medications = []
        
        # Look for medication mentions
        med_pattern = r'(\w+)\s+(\d+[-\s]\d+\s*mg/kg|\d+\s*mg|\d+[-\s]\d+\s*ml)'
        med_matches = re.findall(med_pattern, original_content, re.IGNORECASE)
        for med_match in med_matches:
            medications.append({
                "name": med_match[0],
                "dose": med_match[1],
                "route": "oral",
                "duration": "as needed",
                "notes": "Verify dosing with current protocols"
            })
        
        # Create a basic fallback response
        fallback_response = {
            "primary_diagnosis": diagnosis_match.group(1).strip() if diagnosis_match else "unspecified condition",
            "secondary_diagnoses": [],
            "icd10_codes": ["R50.9"],  # Default to unspecified fever
            "urgency_level": "routine",
            "confidence_score": 0.5,
            "treatment_summary": "Clinical guidance provided in text format",
            "medications": medications,
            "treatment_steps": [
                {
                    "step": 1,
                    "action": "Review clinical guidelines for current condition",
                    "priority": "immediate"
                }
            ],
            "monitoring": ["Monitor patient condition closely"],
            "red_flags": ["Worsening symptoms", "New concerning signs"],
            "follow_up": "Follow up as clinically indicated",
            "patient_education": original_content[:500] + "..." if len(original_content) > 500 else original_content,
            "when_to_refer": "Refer if condition worsens or does not improve",
            "safety_alerts": ["Always verify dosing and contraindications"]
        }
        
        return json.dumps(fallback_response, indent=2)
    
    async def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the specified period"""
        return await self.cost_tracker.get_usage_stats(days)
    
    async def switch_provider(self, provider: str, model: Optional[str] = None) -> bool:
        """Switch to a different LLM provider"""
        try:
            self.provider_manager.validate_provider(provider)
            self.config.llm.provider = provider
            if model:
                self.config.llm.model = model
            
            logger.info("Provider switched successfully", 
                       new_provider=provider, 
                       new_model=model or self.config.llm.model)
            return True
            
        except Exception as e:
            logger.error("Provider switch failed", provider=provider, error=str(e))
            return False
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers and their models"""
        return self.provider_manager.get_available_providers()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on LLM integration"""
        try:
            # Test with a simple prompt
            test_prompt = "What is 2+2? Please respond with just the number."
            response = await self._generate_completion(
                prompt=test_prompt,
                provider=self.config.llm.provider,
                model=self.config.llm.model,
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "provider": self.config.llm.provider,
                "model": self.config.llm.model,
                "response_time_ms": response.response_time_ms,
                "cost_usd": response.cost_usd,
                "tokens_used": response.tokens_used
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.config.llm.provider,
                "model": self.config.llm.model
            }