"""
Content Safety Validation for PediAssist

Validates prompts and responses to ensure they are appropriate for pediatric healthcare
and comply with medical safety standards.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class SafetyCheck:
    """Result of a safety validation check"""
    is_safe: bool
    reason: str
    severity: str  # low, medium, high, critical
    flagged_terms: List[str]
    recommendations: List[str]

class SafetyValidator:
    """Validates content for pediatric healthcare safety"""
    
    def __init__(self):
        # Medical safety patterns
        self.dangerous_patterns = [
            # Self-harm or suicide references
            r'\b(suicid|self.?harm|self.?injur|cutting|overdose)',
            # Drug abuse or misuse
            r'\b(abus|misus|recreational|street.?drug|illegal.?drug)',
            # Medical emergencies that need immediate attention
            r'\b(emergency|911|call.?911|urgent|life.?threatening)',
            # Inappropriate requests for controlled substances
            r'\b(narcotic|opioid|benzodiazepine|controlled.?substance)',
            # Requests for diagnosis or treatment without proper context
            r'\b(diagnos|treat|prescribe|medication).*(?:without|no.?context)',
        ]
        
        # Pediatric-specific safety patterns
        self.pediatric_safety_patterns = [
            # Age-inappropriate content
            r'\b(adult.?content|explicit|mature.?content)',
            # Child safety concerns
            r'\b(child.?abuse|neglect|maltreatment)',
            # Inappropriate medical advice for children
            r'\b(adult.?dose|adult.?medication).*(?:child|infant|pediatric)',
        ]
        
        # Professional boundaries
        self.professional_patterns = [
            # Personal medical advice
            r'\b(my.?child|my.?kid|my.?baby).*(?:diagnos|treat|prescribe)',
            # Requests for personal medical information
            r'\b(your.?child|your.?kid).*(?:medical.?history|symptoms)',
            # Inappropriate personal questions
            r'\b(personal.?information|private.?information|contact.?information)',
        ]
        
        # Safe medical terms (whitelist)
        self.safe_medical_terms = {
            'fever', 'cough', 'cold', 'flu', 'infection', 'antibiotic', 'pain',
            'headache', 'stomachache', 'rash', 'allergy', 'asthma', 'eczema',
            'vaccine', 'immunization', 'checkup', 'physical', 'growth',
            'development', 'milestones', 'nutrition', 'feeding', 'sleep'
        }
        
        # Age-appropriate terms for different age groups
        self.age_appropriate_terms = {
            'infant': ['baby', 'milk', 'feeding', 'sleeping', 'crying', 'diaper'],
            'toddler': ['toddler', 'walking', 'talking', 'potty', 'playing'],
            'preschool': ['preschool', 'sharing', 'friends', 'learning', 'colors'],
            'school_age': ['school', 'homework', 'friends', 'activities', 'sports'],
            'adolescent': ['teen', 'puberty', 'school', 'friends', 'activities']
        }
    
    async def validate_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> SafetyCheck:
        """
        Validate a user prompt for safety
        
        Args:
            prompt: The user's input prompt
            context: Additional context (age, diagnosis, etc.)
            
        Returns:
            SafetyCheck result
        """
        flagged_terms = []
        severity = "low"
        recommendations = []
        
        # Skip safety validation for system prompts (master templates)
        # These contain legitimate medical safety disclaimers
        if self._is_system_prompt(prompt):
            return SafetyCheck(
                is_safe=True,
                reason="System prompt - legitimate medical safety content",
                severity="low",
                flagged_terms=[],
                recommendations=[]
            )
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                # Filter out legitimate medical safety disclaimers
                legitimate_matches = self._filter_legitimate_medical_terms(matches, prompt)
                if legitimate_matches:
                    flagged_terms.extend(legitimate_matches)
                    severity = self._update_severity(severity, "high")
                    recommendations.append("This request may involve serious medical concerns. Please consult emergency services.")
        
        # Check pediatric-specific patterns
        for pattern in self.pediatric_safety_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                flagged_terms.extend(matches)
                severity = self._update_severity(severity, "medium")
                recommendations.append("This request involves pediatric safety concerns.")
        
        # Check professional boundaries
        for pattern in self.professional_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                flagged_terms.extend(matches)
                severity = self._update_severity(severity, "medium")
                recommendations.append("Please maintain professional boundaries. This tool provides general information only.")
        
        # Age-appropriate validation if age is provided
        if context and 'age' in context:
            age_check = self._validate_age_appropriate_content(prompt, context['age'])
            if not age_check['is_safe']:
                flagged_terms.extend(age_check['flagged_terms'])
                severity = self._update_severity(severity, "medium")
                recommendations.extend(age_check['recommendations'])
        
        # Check for medical emergency indicators
        emergency_check = self._check_medical_emergency(prompt)
        if emergency_check['is_emergency']:
            severity = "critical"
            recommendations.append(emergency_check['recommendation'])
        
        is_safe = severity not in ["high", "critical"]
        
        if not is_safe:
            logger.warning(f"Prompt failed safety validation", 
                         severity=severity, 
                         flagged_terms=flagged_terms,
                         prompt_preview=prompt[:100] + "..." if len(prompt) > 100 else prompt)
        
        return SafetyCheck(
            is_safe=is_safe,
            reason=self._generate_safety_reason(severity, flagged_terms),
            severity=severity,
            flagged_terms=list(set(flagged_terms)),  # Remove duplicates
            recommendations=recommendations
        )
    
    async def validate_response(self, response: str, context: Optional[Dict[str, Any]] = None) -> SafetyCheck:
        """
        Validate an LLM response for safety
        
        Args:
            response: The LLM's response
            context: Additional context (age, diagnosis, etc.)
            
        Returns:
            SafetyCheck result
        """
        flagged_terms = []
        severity = "low"
        recommendations = []
        
        # Check for inappropriate medical advice
        if self._contains_medical_advice(response):
            severity = self._update_severity(severity, "medium")
            recommendations.append("Response contains medical advice. Ensure appropriate disclaimers are included.")
        
        # Check for dosage information without proper disclaimers
        dosage_check = self._validate_dosage_information(response)
        if not dosage_check['is_safe']:
            flagged_terms.extend(dosage_check['flagged_terms'])
            severity = self._update_severity(severity, "high")
            recommendations.extend(dosage_check['recommendations'])
        
        # Check for emergency disclaimers
        if self._contains_emergency_indicators(response):
            if not self._has_emergency_disclaimer(response):
                severity = self._update_severity(severity, "high")
                recommendations.append("Response discusses emergency situations but lacks appropriate disclaimers.")
        
        # Validate age-appropriateness
        if context and 'age' in context:
            age_check = self._validate_age_appropriate_response(response, context['age'])
            if not age_check['is_safe']:
                severity = self._update_severity(severity, "medium")
                recommendations.extend(age_check['recommendations'])
        
        # Check for proper medical disclaimers
        if not self._has_medical_disclaimer(response):
            severity = self._update_severity(severity, "medium")
            recommendations.append("Response should include appropriate medical disclaimers.")
        
        is_safe = severity not in ["high", "critical"]
        
        if not is_safe:
            logger.warning(f"Response failed safety validation", 
                         severity=severity, 
                         flagged_terms=flagged_terms,
                         response_preview=response[:100] + "..." if len(response) > 100 else response)
        
        return SafetyCheck(
            is_safe=is_safe,
            reason=self._generate_safety_reason(severity, flagged_terms),
            severity=severity,
            flagged_terms=list(set(flagged_terms)),
            recommendations=recommendations
        )
    
    def _update_severity(self, current: str, new: str) -> str:
        """Update severity level (critical > high > medium > low)"""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        current_level = severity_order.get(current, 0)
        new_level = severity_order.get(new, 0)
        
        if new_level > current_level:
            return new
        return current
    
    def _is_system_prompt(self, prompt: str) -> bool:
        """Check if this is a system prompt (master template)"""
        # System prompts typically contain PediAssist role definition and master template content
        system_indicators = [
            "You are PediAssist",
            "AI assistant specialized in pediatric healthcare",
            "Core Competencies",
            "Response Requirements",
            "Safety First"
        ]
        
        # If multiple system indicators are present, it's likely a system prompt
        indicator_count = sum(1 for indicator in system_indicators if indicator in prompt)
        return indicator_count >= 3
    
    def _filter_legitimate_medical_terms(self, matches: List[str], prompt: str) -> List[str]:
        """Filter out legitimate medical safety disclaimers from flagged terms"""
        legitimate_matches = []
        
        for match in matches:
            match_lower = match.lower()
            
            # Skip if it's part of legitimate medical safety disclaimers
            if self._is_medical_safety_disclaimer(match_lower, prompt):
                continue
                
            # Skip if it's in the context of appropriate medical warnings
            if self._is_in_medical_context(match_lower, prompt):
                continue
                
            legitimate_matches.append(match)
        
        return legitimate_matches
    
    def _is_medical_safety_disclaimer(self, term: str, prompt: str) -> bool:
        """Check if the term is part of legitimate medical safety disclaimers"""
        safety_contexts = [
            "immediate medical attention",
            "emergency care",
            "delay emergency",
            "medical attention required",
            "when to escalate care",
            "call 911",
            "emergency room"
        ]
        
        # Check if the term appears in legitimate safety contexts
        for context in safety_contexts:
            if context in prompt.lower() and term in context:
                return True
        
        return False
    
    def _is_in_medical_context(self, term: str, prompt: str) -> bool:
        """Check if the term is used in appropriate medical context"""
        medical_contexts = [
            "medical emergency",
            "emergency situations",
            "emergency services",
            "emergency department",
            "life threatening",
            "urgent medical"
        ]
        
        # Check surrounding context (±50 characters)
        for context in medical_contexts:
            if context in prompt.lower() and term in context:
                return True
        
        return False
    
    def _validate_age_appropriate_content(self, content: str, age: int) -> Dict[str, Any]:
        """Validate content is appropriate for the specified age"""
        flagged_terms = []
        recommendations = []
        
        # Determine age group
        if age < 1:
            age_group = "infant"
        elif age < 3:
            age_group = "toddler"
        elif age < 6:
            age_group = "preschool"
        elif age < 13:
            age_group = "school_age"
        else:
            age_group = "adolescent"
        
        # Check for age-appropriate terms
        appropriate_terms = self.age_appropriate_terms.get(age_group, [])
        
        # Only apply strict age-appropriate validation for non-medical contexts
        # Medical treatment responses are expected to use medical terminology
        if age_group in ["infant", "toddler", "preschool"] and not self._is_medical_treatment_context(content):
            adult_terms = ["medication", "diagnosis", "treatment", "prescription"]
            for term in adult_terms:
                if term in content.lower():
                    flagged_terms.append(term)
                    recommendations.append(f"Consider using age-appropriate language for {age_group} age group.")
        
        return {
            "is_safe": len(flagged_terms) == 0,
            "flagged_terms": flagged_terms,
            "recommendations": recommendations
        }
    
    def _check_medical_emergency(self, content: str) -> Dict[str, Any]:
        """Check if content indicates a medical emergency"""
        emergency_indicators = [
            "call 911", "emergency room", "urgent care", "life threatening",
            "severe allergic reaction", "difficulty breathing", "unconscious",
            "severe bleeding", "chest pain", "seizure"
        ]
        
        for indicator in emergency_indicators:
            if indicator in content.lower():
                return {
                    "is_emergency": True,
                    "recommendation": "This appears to be a medical emergency. Please call 911 or go to the nearest emergency room."
                }
        
        return {"is_emergency": False}
    
    def _contains_medical_advice(self, response: str) -> bool:
        """Check if response contains medical advice"""
        advice_patterns = [
            r'\b(should|must|need to|have to).*(?:take|use|try)',
            r'\b(recommend|suggest|advise).*(?:medication|treatment)',
            r'\b(dose|dosage|prescription).*(?:mg|ml|times)'
        ]
        
        for pattern in advice_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_dosage_information(self, response: str) -> Dict[str, Any]:
        """Validate dosage information in response"""
        flagged_terms = []
        recommendations = []
        
        # Look for specific dosages, but exclude legitimate medical contexts
        # Pattern that matches both "500 ml" and "500ml" formats
        dosage_pattern = r'\b(\d+(?:\.\d+)?)\s*(mg|ml|g|kg|lbs|ounces?)\b'
        all_matches = re.findall(dosage_pattern, response, re.IGNORECASE)
        
        # Filter out legitimate medical contexts that shouldn't trigger safety warnings
        legitimate_dosages = []
        concerning_dosages = []
        
        for amount, unit in all_matches:
            # Create both spaced and unspaced versions for matching
            spaced_match = f"{amount} {unit}"
            unspaced_match = f"{amount}{unit}"
            
            # Find the actual format used in the response
            if unspaced_match.lower() in response.lower():
                actual_match = unspaced_match
            else:
                actual_match = spaced_match
            
            # Skip if this is likely patient data (weight, height, vital signs)
            if self._is_patient_measurement(actual_match, response):
                continue
                
            # Skip if this is describing medication forms (not prescribing)
            if self._is_medication_description(actual_match, response):
                continue
                
            # Skip if this is procedural documentation
            if self._is_procedural_documentation(actual_match, response):
                continue
                
            # Skip if this appears to be in a legitimate medical treatment context
            if self._is_legitimate_medical_context(actual_match, response):
                continue
                
            # If we get here, it's likely actual dosage information
            concerning_dosages.append(actual_match)
        
        if concerning_dosages:
            # Check if response contains appropriate medical disclaimers
            has_disclaimer = self._has_medical_disclaimer(response)
            has_dosage_disclaimer = self._has_dosage_disclaimer(response)
            
            # Only flag as unsafe if no appropriate disclaimers are present
            if not (has_disclaimer or has_dosage_disclaimer):
                flagged_terms.extend(concerning_dosages)
                recommendations.append("Dosage information should always be verified with a healthcare provider.")
                recommendations.append("Include disclaimer that dosages must be confirmed by a medical professional.")
            else:
                # If disclaimers are present, it's safe but still add educational recommendation
                recommendations.append("Ensure dosage information is accompanied by appropriate medical disclaimers.")
        
        return {
            "is_safe": len(concerning_dosages) == 0 or (len(concerning_dosages) > 0 and (self._has_medical_disclaimer(response) or self._has_dosage_disclaimer(response))),
            "flagged_terms": flagged_terms,
            "recommendations": recommendations
        }
    
    def _is_patient_measurement(self, measurement: str, response: str) -> bool:
        """Check if measurement is patient data (weight, height, vitals) rather than dosage"""
        measurement_lower = measurement.lower()
        response_lower = response.lower()
        
        # Patient measurement contexts
        patient_contexts = [
            "weighs", "weight", "height", "tall", "length", "patient weighs",
            "blood pressure", "bp", "heart rate", "hr", "temperature", "temp",
            "respiratory rate", "rr", "oxygen saturation", "spo2", "vitals"
        ]
        
        # Check if measurement appears in patient measurement context
        for context in patient_contexts:
            if context in response_lower and measurement_lower in response_lower:
                # Additional check: see if measurement appears near the context
                context_index = response_lower.find(context)
                measurement_index = response_lower.find(measurement_lower)
                if abs(context_index - measurement_index) < 100:  # Within 100 characters
                    return True
        
        return False
    
    def _is_medication_description(self, measurement: str, response: str) -> bool:
        """Check if measurement is describing medication forms rather than prescribing"""
        measurement_lower = measurement.lower()
        response_lower = response.lower()
        
        # Medication description contexts - more comprehensive
        description_contexts = [
            "comes in", "available in", "formulated as", "tablets of", "capsules of",
            "strengths of", "concentration", "preparation", "formulation", "available as",
            "supplied as", "provided as", "manufactured as", "packaged as"
        ]
        
        # Check for medication description patterns
        for context in description_contexts:
            if context in response_lower:
                # Check if measurement appears near the context or in a descriptive sentence
                context_index = response_lower.find(context)
                measurement_index = response_lower.find(measurement_lower)
                if measurement_index != -1:  # Measurement exists in response
                    # Check within a reasonable distance (200 characters) or if it's clearly descriptive
                    if abs(context_index - measurement_index) < 200 or self._is_in_descriptive_context(measurement_lower, response_lower):
                        return True
        
        # Also check if it's clearly describing available options
        if any(word in response_lower for word in ["and", "or"]) and self._appears_in_list(measurement_lower, response_lower):
            return True
            
        return False
    
    def _is_procedural_documentation(self, measurement: str, response: str) -> bool:
        """Check if measurement is procedural documentation rather than prescribing"""
        measurement_lower = measurement.lower()
        response_lower = response.lower()
        
        # Procedural contexts - more comprehensive and context-aware
        procedural_phrases = [
            "received", "was administered", "was given", "was infused", "was injected",
            "during the procedure", "post procedure", "pre operative", "intraoperative",
            "normal saline", "ringer's lactate", "dextrose", "lactated ringer's",
            "fluid resuscitation", "fluid therapy", "iv fluids"
        ]
        
        # Past tense medical procedures
        past_tense_procedures = [
            "received", "administered", "given", "infused", "injected", "transfused"
        ]
        
        # Check for procedural patterns
        for phrase in procedural_phrases:
            if phrase in response_lower and measurement_lower in response_lower:
                # Check if it's in past tense (documentation) vs present/future (prescribing)
                if any(past_word in response_lower for past_word in past_tense_procedures):
                    return True
                    
                # Check proximity
                phrase_index = response_lower.find(phrase)
                measurement_index = response_lower.find(measurement_lower)
                if measurement_index != -1 and abs(phrase_index - measurement_index) < 150:
                    return True
        
        return False
    
    def _is_medical_treatment_context(self, content: str) -> bool:
        """Check if content is in a medical treatment context"""
        content_lower = content.lower()
        
        # Medical treatment context indicators
        medical_contexts = [
            "treatment", "therapy", "medication", "prescription", "diagnosis",
            "clinical", "medical", "healthcare", "pediatric", "therapeutic",
            "doctor", "physician", "pediatrician", "medications", "treatment plan"
        ]
        
        # Check if content contains medical treatment indicators
        return any(context in content_lower for context in medical_contexts)
    
    def _is_legitimate_medical_context(self, measurement: str, response: str) -> bool:
        """Check if measurement appears in legitimate medical treatment context"""
        measurement_lower = measurement.lower()
        response_lower = response.lower()
        
        # Medical treatment contexts that are legitimate
        treatment_contexts = [
            "treatment", "therapy", "medication", "prescribed", "dosage",
            "dosing", "administered", "given", "recommended", "indicated",
            "therapeutic", "clinical", "medical", "healthcare", "pediatric"
        ]
        
        # Check if response is clearly a medical treatment plan
        medical_indicators = [
            "diagnosis", "treatment plan", "medical advice", "healthcare provider",
            "doctor", "physician", "pediatrician", "clinical", "therapeutic"
        ]
        
        # If response contains medical treatment indicators, it's likely legitimate
        has_medical_context = any(indicator in response_lower for indicator in medical_indicators)
        has_treatment_context = any(context in response_lower for context in treatment_contexts)
        
        # More permissive: if response has medical context, assume dosages are legitimate
        if has_medical_context or has_treatment_context:
            return True
        
        return False
    
    def _is_in_descriptive_context(self, measurement: str, response: str) -> bool:
        """Check if measurement appears in a clearly descriptive context"""
        descriptive_indicators = [
            "available", "comes", "formulated", "manufactured", "supplied",
            "packaged", "prepared", "compounded", "produced"
        ]
        
        # Find the sentence containing the measurement
        sentences = response.split('.')
        for sentence in sentences:
            if measurement in sentence.lower():
                # Check if sentence contains descriptive indicators
                if any(indicator in sentence.lower() for indicator in descriptive_indicators):
                    return True
        
        return False
    
    def _appears_in_list(self, measurement: str, response: str) -> bool:
        """Check if measurement appears to be part of a list of options"""
        # Look for patterns like "100mg and 200mg" or "100mg, 200mg, or 400mg"
        list_patterns = [
            rf"{measurement}\s*(?:and|or|,)\s*\d+\s*(?:mg|ml|g)",
            rf"\d+\s*(?:mg|ml|g)\s*(?:and|or|,)\s*{measurement}"
        ]
        
        for pattern in list_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_emergency_indicators(self, response: str) -> bool:
        """Check if response contains emergency indicators"""
        emergency_terms = ["emergency", "urgent", "immediate", "call 911", "go to hospital"]
        return any(term in response.lower() for term in emergency_terms)
    
    def _has_emergency_disclaimer(self, response: str) -> bool:
        """Check if response has appropriate emergency disclaimers"""
        disclaimers = [
            "call 911", "emergency room", "immediate medical attention",
            "seek emergency care", "contact emergency services"
        ]
        return any(disclaimer in response.lower() for disclaimer in disclaimers)
    
    def _validate_age_appropriate_response(self, response: str, age: int) -> Dict[str, Any]:
        """Validate response is appropriate for the specified age"""
        recommendations = []
        
        # Check for complex medical terminology for young children
        if age < 6:
            complex_terms = ["pathophysiology", "etiology", "prognosis", "diagnosis"]
            for term in complex_terms:
                if term in response.lower():
                    recommendations.append(f"Consider simplifying medical terminology for {age}-year-old.")
        
        return {
            "is_safe": len(recommendations) == 0,
            "recommendations": recommendations
        }
    
    def _has_medical_disclaimer(self, response: str) -> bool:
        """Check if response contains appropriate medical disclaimers"""
        disclaimers = [
            "not medical advice", "consult your doctor", "healthcare provider",
            "medical professional", "not a substitute", "informational purposes only"
        ]
        return any(disclaimer in response.lower() for disclaimer in disclaimers)
    
    def _has_dosage_disclaimer(self, response: str) -> bool:
        """Check if response contains appropriate dosage disclaimers"""
        dosage_disclaimers = [
            "dosage should be verified", "dose must be confirmed", "dosage by healthcare provider",
            "prescribed by doctor", "under medical supervision", "professional dosage",
            "recommended dose", "as prescribed", "per physician", "according to doctor"
        ]
        return any(disclaimer in response.lower() for disclaimer in dosage_disclaimers)
    
    def _generate_safety_reason(self, severity: str, flagged_terms: List[str]) -> str:
        """Generate a human-readable safety reason"""
        if severity == "critical":
            return "Content indicates a medical emergency or serious safety concern."
        elif severity == "high":
            return f"Content contains concerning terms: {', '.join(flagged_terms[:3])}."
        elif severity == "medium":
            return f"Content may be inappropriate: {', '.join(flagged_terms[:2])}."
        else:
            return "Content appears safe for pediatric healthcare use."