"""
LLM integration layer with BYOK (Bring Your Own Key) support
"""

import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
import os

# Try to import various LLM providers
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from litellm import acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

logger = structlog.get_logger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "gpt-3.5-turbo")
        self.max_tokens = config.get("max_tokens", 2000)
        self.temperature = config.get("temperature", 0.1)
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM"""
        pass
    
    @abstractmethod
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        self.client = AsyncOpenAI(api_key=config["api_key"])
        self._token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **kwargs
            )
            
            # Update token usage
            usage = response.usage
            if usage:
                self._token_usage["prompt_tokens"] += usage.prompt_tokens
                self._token_usage["completion_tokens"] += usage.completion_tokens
                self._token_usage["total_tokens"] += usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return self._token_usage.copy()

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available. Install with: pip install anthropic")
        
        self.client = AsyncAnthropic(api_key=config["api_key"])
        self._token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            # Update token usage (approximate)
            prompt_tokens = len(prompt.split()) * 1.3  # Rough approximation
            completion_tokens = len(response.content[0].text.split()) * 1.3
            
            self._token_usage["prompt_tokens"] += int(prompt_tokens)
            self._token_usage["completion_tokens"] += int(completion_tokens)
            self._token_usage["total_tokens"] += int(prompt_tokens + completion_tokens)
            
            return response.content[0].text
            
        except Exception as e:
            logger.error("Anthropic generation failed", error=str(e))
            raise
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return self._token_usage.copy()

class OllamaProvider(LLMProvider):
    """Local Ollama provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama2")
        self._token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            import aiohttp
            
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"Ollama API error: {response.status}")
                    
                    result = await response.json()
                    
                    # Update token usage (approximate)
                    prompt_tokens = len(prompt.split()) * 1.3
                    completion_tokens = len(result["response"].split()) * 1.3
                    
                    self._token_usage["prompt_tokens"] += int(prompt_tokens)
                    self._token_usage["completion_tokens"] += int(completion_tokens)
                    self._token_usage["total_tokens"] += int(prompt_tokens + completion_tokens)
                    
                    return result["response"]
                    
        except Exception as e:
            logger.error("Ollama generation failed", error=str(e))
            raise
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return self._token_usage.copy()

class LiteLLMProvider(LLMProvider):
    """LiteLLM provider for multiple model support"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM package not available. Install with: pip install litellm")
        
        self.api_key = config.get("api_key", "")
        self._token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using LiteLLM"""
        try:
            response = await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **kwargs
            )
            
            # Update token usage
            usage = response.get("usage", {})
            if usage:
                self._token_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
                self._token_usage["completion_tokens"] += usage.get("completion_tokens", 0)
                self._token_usage["total_tokens"] += usage.get("total_tokens", 0)
            
            return response["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error("LiteLLM generation failed", error=str(e))
            raise
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return self._token_usage.copy()

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "litellm": LiteLLMProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, config: Dict[str, Any]) -> LLMProvider:
        """Create an LLM provider instance"""
        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported provider: {provider_type}. Available: {list(cls._providers.keys())}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a new provider type"""
        cls._providers[name] = provider_class

class LLMManager:
    """Main LLM manager with BYOK support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup LLM providers from configuration"""
        # Primary provider
        primary_config = self.config.get("primary")
        if primary_config:
            provider_type = primary_config["provider"]
            self.primary_provider = provider_type
            self.providers[provider_type] = LLMProviderFactory.create_provider(
                provider_type, primary_config
            )
        
        # Fallback providers
        fallback_configs = self.config.get("fallbacks", [])
        for fallback_config in fallback_configs:
            provider_type = fallback_config["provider"]
            self.fallback_providers.append(provider_type)
            self.providers[provider_type] = LLMProviderFactory.create_provider(
                provider_type, fallback_config
            )
    
    async def generate_response(
        self, 
        prompt: str, 
        provider: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> str:
        """Generate response using specified or primary provider"""
        
        # Use specified provider or primary
        target_provider = provider or self.primary_provider
        
        if not target_provider or target_provider not in self.providers:
            raise ValueError(f"Provider {target_provider} not available")
        
        try:
            # Try primary provider
            logger.info(f"Generating response with provider: {target_provider}")
            result = await self.providers[target_provider].generate_response(prompt, **kwargs)
            logger.info(f"Response generated successfully with {target_provider}")
            return result
            
        except Exception as e:
            logger.error(f"Primary provider {target_provider} failed", error=str(e))
            
            if not use_fallback:
                raise
            
            # Try fallback providers
            for fallback_provider in self.fallback_providers:
                try:
                    logger.info(f"Trying fallback provider: {fallback_provider}")
                    result = await self.providers[fallback_provider].generate_response(prompt, **kwargs)
                    logger.info(f"Fallback provider {fallback_provider} succeeded")
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback provider {fallback_provider} failed", error=str(fallback_error))
                    continue
            
            # All providers failed
            raise RuntimeError("All LLM providers failed")
    
    def get_token_usage(self, provider: Optional[str] = None) -> Dict[str, int]:
        """Get token usage for a specific provider or total usage"""
        if provider:
            if provider in self.providers:
                return self.providers[provider].get_token_usage()
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        # Total usage across all providers
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        for provider_instance in self.providers.values():
            usage = provider_instance.get_token_usage()
            for key in total_usage:
                total_usage[key] += usage.get(key, 0)
        
        return total_usage
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_primary_provider(self) -> Optional[str]:
        """Get primary provider name"""
        return self.primary_provider
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on LLM integration"""
        try:
            # Test with a simple prompt
            test_prompt = "What is 2+2? Please respond with just the number."
            result = await self.generate_response(test_prompt, use_fallback=False)
            
            return {
                "status": "healthy",
                "provider": self.primary_provider,
                "response": result.strip(),
                "available_providers": list(self.providers.keys())
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.primary_provider,
                "available_providers": list(self.providers.keys())
            }

# Global LLM manager instance
_llm_manager: Optional[LLMManager] = None

def get_llm_manager(config: Optional[Dict[str, Any]] = None) -> LLMManager:
    """Get or create the global LLM manager"""
    global _llm_manager
    
    if _llm_manager is None and config:
        _llm_manager = LLMManager(config)
    
    if _llm_manager is None:
        raise RuntimeError("LLM manager not initialized. Provide configuration.")
    
    return _llm_manager