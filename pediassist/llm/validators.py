"""
Response validation and safety checks for LLM outputs
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import json
import structlog

logger = structlog.get_logger(__name__)

class ResponseValidator:
    """Validates and sanitizes LLM responses for medical safety"""
    
    def __init__(self):
        # Medical safety keywords and patterns
        self.safety_keywords = {
            "emergency": ["emergency", "911", "urgent", "immediate", "life-threatening", "critical"],
            "contraindications": ["contraindicated", "avoid", "do not use", "not recommended"],
            "warnings": ["warning", "caution", "monitor", "risk", "adverse", "side effect"],
            "dosage": ["mg", "ml", "units", "mcg", "kg", "dose", "dosage", "administer"],
            "referral": ["refer", "specialist", "consult", "admit", "hospitalize"]
        }
        
        # Patterns to detect potentially unsafe content
        self.unsafe_patterns = [
            r"\b\d+\s*mg\s*(?:/kg)?\s*(?:daily|bid|tid|qid)?\b",  # Dosage patterns
            r"\b\d+\s*ml\s*(?:/kg)?\s*(?:daily|bid|tid|qid)?\b",  # Liquid dosing
            r"\b\d+\s*units\s*(?:/kg)?\s*(?:daily|bid|tid|qid)?\b",  # Unit dosing
        ]
        
        # Required sections for structured responses
        self.required_sections = [
            "Quick Summary",
            "Detailed Protocol",
            "Safety Alerts",
            "When to Refer"
        ]
    
    def validate_response(self, response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive response validation"""
        context = context or {}
        
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "safety_flags": [],
            "structured_data": {}
        }
        
        # Basic content validation
        self._check_basic_content(response, validation_result)
        
        # Safety validation
        self._check_safety_content(response, validation_result)
        
        # Structure validation
        self._check_structure(response, validation_result)
        
        # Medical content validation
        self._check_medical_content(response, validation_result, context)
        
        # Dosage validation
        self._check_dosages(response, validation_result, context)
        
        # Determine final validity
        validation_result["is_valid"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    def _check_basic_content(self, response: str, result: Dict[str, Any]):
        """Check basic content requirements"""
        if not response or len(response.strip()) < 50:
            result["errors"].append("Response too short or empty")
        
        if len(response) > 10000:  # Reasonable upper limit
            result["warnings"].append("Response unusually long")
        
        # Check for repetitive content
        words = response.lower().split()
        if len(words) > 100:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:  # Less than 30% unique words
                result["warnings"].append("Potentially repetitive content detected")
    
    def _check_safety_content(self, response: str, result: Dict[str, Any]):
        """Check for safety-related content"""
        response_lower = response.lower()
        
        # Check for emergency warnings
        emergency_found = any(keyword in response_lower for keyword in self.safety_keywords["emergency"])
        if emergency_found:
            result["safety_flags"].append("emergency_mentioned")
        
        # Check for contraindications
        contraindication_found = any(keyword in response_lower for keyword in self.safety_keywords["contraindications"])
        if contraindication_found:
            result["safety_flags"].append("contraindications_mentioned")
        
        # Check for warnings
        warning_found = any(keyword in response_lower for keyword in self.safety_keywords["warnings"])
        if warning_found:
            result["safety_flags"].append("warnings_mentioned")
        
        # Check for referral recommendations
        referral_found = any(keyword in response_lower for keyword in self.safety_keywords["referral"])
        if referral_found:
            result["safety_flags"].append("referral_mentioned")
        
        # Validate that emergency situations are properly flagged
        if emergency_found and "emergency_mentioned" not in result["safety_flags"]:
            result["warnings"].append("Emergency keywords found but not properly flagged")
    
    def _check_structure(self, response: str, result: Dict[str, Any]):
        """Check response structure"""
        # Check for required sections
        missing_sections = []
        for section in self.required_sections:
            if section not in response:
                missing_sections.append(section)
        
        if missing_sections:
            result["warnings"].append(f"Missing sections: {', '.join(missing_sections)}")
        
        # Check for proper section formatting
        section_pattern = r'^###\s+(.+)$'
        sections = re.findall(section_pattern, response, re.MULTILINE)
        
        if len(sections) < 3:  # Should have multiple sections
            result["warnings"].append("Limited section structure detected")
    
    def _check_medical_content(self, response: str, result: Dict[str, Any], context: Dict[str, Any]):
        """Validate medical content appropriateness"""
        patient_age = context.get("patient_age")
        diagnosis = context.get("diagnosis", "").lower()
        
        # Age-appropriate content checks
        if patient_age is not None:
            if patient_age < 0 or patient_age > 18:
                result["warnings"].append(f"Patient age {patient_age} outside pediatric range")
        
        # Diagnosis consistency check
        if diagnosis:
            response_lower = response.lower()
            if diagnosis not in response_lower:
                result["warnings"].append(f"Diagnosis '{diagnosis}' not mentioned in response")
    
    def _check_dosages(self, response: str, result: Dict[str, Any], context: Dict[str, Any]):
        """Validate dosage information"""
        patient_age = context.get("patient_age")
        patient_weight = context.get("patient_weight")
        
        # Find dosage patterns
        dosage_matches = []
        for pattern in self.unsafe_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            dosage_matches.extend(matches)
        
        if dosage_matches:
            result["safety_flags"].append("dosage_mentioned")
            
            # Additional validation for specific medications would go here
            # This is a placeholder for more sophisticated dosage validation
            if not patient_weight and any("/kg" in match for match in dosage_matches):
                result["warnings"].append("Weight-based dosing found but patient weight not provided")
    
    def extract_structured_data(self, response: str) -> Dict[str, Any]:
        """Extract structured data from response"""
        structured = {}
        
        # Extract sections
        section_pattern = r'^###\s+(.+?)\n(.*?)(?=^###|\Z)'
        sections = re.findall(section_pattern, response, re.MULTILINE | re.DOTALL)
        
        for section_title, section_content in sections:
            section_key = section_title.lower().replace(" ", "_")
            structured[section_key] = section_content.strip()
        
        # Extract medications mentioned
        medication_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:\d+\.?\d*\s*(?:mg|ml|units|mcg))'
        medications = re.findall(medication_pattern, response)
        if medications:
            structured["medications_mentioned"] = list(set(medications))
        
        # Extract emergency indicators
        emergency_keywords = ["emergency", "911", "urgent", "immediate"]
        emergency_found = any(keyword in response.lower() for keyword in emergency_keywords)
        structured["emergency_indicated"] = emergency_found
        
        return structured
    
    def sanitize_response(self, response: str) -> str:
        """Sanitize response for display"""
        # Remove or modify potentially problematic content
        sanitized = response
        
        # Add disclaimer if not present
        if "This is not medical advice" not in sanitized:
            disclaimer = "\n\n---\n**Disclaimer**: This information is for clinical decision support only and should not replace professional medical judgment. Always consider individual patient factors and consult appropriate specialists when needed."
            sanitized += disclaimer
        
        # Ensure emergency warnings are prominent
        if any(keyword in sanitized.lower() for keyword in ["emergency", "911", "urgent"]):
            emergency_warning = "\n\n⚠️ **EMERGENCY WARNING**: This condition may require immediate medical attention. If the patient is experiencing severe symptoms, call emergency services immediately."
            if emergency_warning not in sanitized:
                sanitized = emergency_warning + "\n\n" + sanitized
        
        return sanitized

class ResponseCache:
    """Simple in-memory cache for responses"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        from datetime import datetime, timedelta
        self.timedelta = timedelta
        self.datetime = datetime
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response"""
        if key in self.cache:
            entry = self.cache[key]
            if self.datetime.utcnow() - entry["timestamp"] < self.timedelta(seconds=self.ttl_seconds):
                return entry["response"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, response: str):
        """Cache response"""
        # Simple LRU eviction
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "response": response,
            "timestamp": self.datetime.utcnow()
        }
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()

# Global validator and cache instances
_validator = ResponseValidator()
_cache = ResponseCache()

def validate_response(response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate an LLM response"""
    return _validator.validate_response(response, context)

def sanitize_response(response: str) -> str:
    """Sanitize an LLM response for display"""
    return _validator.sanitize_response(response)

def get_cached_response(key: str) -> Optional[str]:
    """Get a cached response"""
    return _cache.get(key)

def cache_response(key: str, response: str):
    """Cache a response"""
    _cache.set(key, response)

def extract_structured_data(response: str) -> Dict[str, Any]:
    """Extract structured data from response"""
    return _validator.extract_structured_data(response)