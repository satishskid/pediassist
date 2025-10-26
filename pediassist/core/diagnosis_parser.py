"""
Core diagnosis parsing and analysis engine
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

class AgeGroup(Enum):
    """Pediatric age groups"""
    NEWBORN = "newborn"
    INFANT = "infant" 
    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    SCHOOL_AGE = "school_age"
    ADOLESCENT = "adolescent"

class UrgencyLevel(Enum):
    """Clinical urgency levels"""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"
    WELLNESS = "wellness"

@dataclass
class ParsedDiagnosis:
    """Structured diagnosis information"""
    primary_diagnosis: str
    secondary_diagnoses: List[str]
    differential_diagnoses: List[str]
    age_group: AgeGroup
    urgency_level: UrgencyLevel
    confidence_score: float
    key_symptoms: List[str]
    red_flags: List[str]
    system_category: str
    icd_codes: List[str]
    metadata: Dict[str, Any]

class DiagnosisParser:
    """Advanced diagnosis parsing engine"""
    
    def __init__(self):
        self.age_patterns = {
            AgeGroup.NEWBORN: r"\b(newborn|neonate|0\s*-\s*28\s*days?)\b",
            AgeGroup.INFANT: r"\b(infant|1\s*-\s*12\s*months?|baby)\b",
            AgeGroup.TODDLER: r"\b(toddler|1\s*-\s*3\s*years?|young\s*child)\b",
            AgeGroup.PRESCHOOL: r"\b(preschool|3\s*-\s*5\s*years?|pre\s*-?school)\b",
            AgeGroup.SCHOOL_AGE: r"\b(school\s*age|6\s*-\s*12\s*years?|child)\b",
            AgeGroup.ADOLESCENT: r"\b(adolescent|teen|13\s*-\s*18\s*years?|adolescent)\b"
        }
        
        self.urgency_patterns = {
            UrgencyLevel.EMERGENCY: [
                r"\b(emergency|urgent|immediate|life\s*threatening|critical|severe)\b",
                r"\b(sepsis|meningitis|anaphylaxis|cardiac\s*arrest|respiratory\s*failure)\b"
            ],
            UrgencyLevel.URGENT: [
                r"\b(urgent|prompt|asap|within\s*24\s*hours)\b",
                r"\b(pneumonia|dehydration|fracture|appendicitis)\b"
            ],
            UrgencyLevel.ROUTINE: [
                r"\b(routine|scheduled|follow\s*up|monitoring)\b",
                r"\b(chronic|stable|well\s*controlled)\b"
            ],
            UrgencyLevel.WELLNESS: [
                r"\b(wellness|preventive|screening|healthy)\b",
                r"\b(check\s*up|immunization|growth\s*monitoring)\b"
            ]
        }
        
        self.system_categories = {
            "cardiovascular": ["heart", "cardiac", "circulation", "blood pressure", "pulse"],
            "respiratory": ["lung", "breathing", "respiratory", "cough", "wheeze", "asthma"],
            "neurological": ["brain", "neurological", "seizure", "headache", "consciousness"],
            "gastrointestinal": ["stomach", "abdominal", "bowel", "diarrhea", "vomiting"],
            "infectious": ["infection", "fever", "bacterial", "viral", "antibiotic"],
            "dermatological": ["skin", "rash", "eczema", "dermatitis", "lesion"],
            "musculoskeletal": ["bone", "muscle", "joint", "fracture", "pain", "mobility"],
            "endocrine": ["hormone", "diabetes", "thyroid", "growth", "puberty"],
            "hematological": ["blood", "anemia", "bleeding", "clotting", "platelet"],
            "renal": ["kidney", "urinary", "renal", "urine", "nephrology"]
        }
        
        self.red_flag_patterns = [
            r"\b(fever\s*in\s*infant|temperature\s*>\s*38\s*°C\s*in\s*<\s*3\s*months?)\b",
            r"\b(seizure|convulsion|loss\s*of\s*consciousness)\b",
            r"\b(difficulty\s*breathing|respiratory\s*distress|cyanosis)\b",
            r"\b(persistent\s*vomiting|dehydration|no\s*urine\s*output)\b",
            r"\b(severe\s*pain|uncontrolled\s*pain)\b",
            r"\b(altered\s*mental\s*status|lethargy|irritability)\b",
            r"\b(rapid\s*heart\s*rate|tachycardia|bradycardia)\b",
            r"\b(signs\s*of\s*shock|hypotension|poor\s*perfusion)\b"
        ]
    
    def parse_age_group(self, query: str) -> AgeGroup:
        """Extract age group from query"""
        query_lower = query.lower()
        
        for age_group, pattern in self.age_patterns.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                return age_group
        
        # Default to school age if not specified
        return AgeGroup.SCHOOL_AGE
    
    def parse_urgency_level(self, query: str) -> UrgencyLevel:
        """Extract urgency level from query"""
        query_lower = query.lower()
        
        # Check emergency patterns first (highest priority)
        for pattern in self.urgency_patterns[UrgencyLevel.EMERGENCY]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return UrgencyLevel.EMERGENCY
        
        # Check urgent patterns
        for pattern in self.urgency_patterns[UrgencyLevel.URGENT]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return UrgencyLevel.URGENT
        
        # Check routine patterns
        for pattern in self.urgency_patterns[UrgencyLevel.ROUTINE]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return UrgencyLevel.ROUTINE
        
        # Default to routine
        return UrgencyLevel.ROUTINE
    
    def extract_system_category(self, query: str) -> str:
        """Extract primary body system category"""
        query_lower = query.lower()
        system_scores = {}
        
        for system, keywords in self.system_categories.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                system_scores[system] = score
        
        if system_scores:
            return max(system_scores.items(), key=lambda x: x[1])[0]
        
        return "general"
    
    def extract_red_flags(self, query: str) -> List[str]:
        """Extract red flag symptoms"""
        red_flags = []
        
        for pattern in self.red_flag_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            red_flags.extend(matches)
        
        return red_flags
    
    def extract_key_symptoms(self, query: str) -> List[str]:
        """Extract key symptoms from query"""
        # Common symptom patterns
        symptom_patterns = [
            r"\b(fever|temperature|pyrexia)\b",
            r"\b(cough|wheeze|breathing\s*difficulty)\b",
            r"\b(vomiting|nausea|diarrhea|constipation)\b",
            r"\b(rash|skin\s*changes|lesion)\b",
            r"\b(headache|pain|ache|discomfort)\b",
            r"\b(fatigue|lethargy|weakness)\b",
            r"\b(loss\s*of\s*appetite|poor\s*feeding)\b",
            r"\b(irritability|fussiness|behavior\s*changes)\b"
        ]
        
        symptoms = []
        for pattern in symptom_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            symptoms.extend(matches)
        
        return list(set(symptoms))  # Remove duplicates
    
    def parse_diagnosis_text(self, diagnosis_text: str) -> Dict[str, Any]:
        """Parse structured diagnosis from text"""
        parsed = {
            "primary_diagnosis": "",
            "secondary_diagnoses": [],
            "differential_diagnoses": [],
            "icd_codes": []
        }
        
        # Split by common delimiters
        lines = re.split(r'[\n\r]+', diagnosis_text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for primary diagnosis
            if re.match(r'^(primary\s*diagnosis|main\s*diagnosis|diagnosis):?\s*', line, re.IGNORECASE):
                parsed["primary_diagnosis"] = re.sub(r'^(primary\s*diagnosis|main\s*diagnosis|diagnosis):?\s*', '', line, flags=re.IGNORECASE)
            
            # Look for secondary diagnoses
            elif re.match(r'^(secondary|additional):?\s*', line, re.IGNORECASE):
                diagnosis = re.sub(r'^(secondary|additional):?\s*', '', line, flags=re.IGNORECASE)
                if diagnosis:
                    parsed["secondary_diagnoses"].append(diagnosis)
            
            # Look for differential diagnoses
            elif re.match(r'^(differential|consider):?\s*', line, re.IGNORECASE):
                diagnosis = re.sub(r'^(differential|consider):?\s*', '', line, flags=re.IGNORECASE)
                if diagnosis:
                    parsed["differential_diagnoses"].append(diagnosis)
            
            # Look for ICD codes
            icd_matches = re.findall(r'\b([A-Z]\d{2}(?:\.\d{1,2})?)\b', line)
            parsed["icd_codes"].extend(icd_matches)
        
        # If no structured format found, treat entire text as primary diagnosis
        if not parsed["primary_diagnosis"] and diagnosis_text.strip():
            parsed["primary_diagnosis"] = diagnosis_text.strip()
        
        # If still no primary diagnosis, use the query as fallback
        if not parsed["primary_diagnosis"]:
            parsed["primary_diagnosis"] = "unspecified fever"  # Default for fever cases
        
        return parsed
    
    def calculate_confidence_score(self, query: str, parsed_data: Dict[str, Any]) -> float:
        """Calculate confidence score for diagnosis"""
        score = 0.5  # Base score
        
        # Increase score for specific age mentions
        if self.parse_age_group(query) != AgeGroup.SCHOOL_AGE:
            score += 0.1
        
        # Increase score for specific symptoms mentioned
        if len(parsed_data.get("key_symptoms", [])) > 0:
            score += 0.2
        
        # Increase score for system category identification
        if parsed_data.get("system_category") != "general":
            score += 0.1
        
        # Decrease score for vague terms
        vague_terms = ["maybe", "possibly", "unclear", "unknown", "non-specific"]
        query_lower = query.lower()
        for term in vague_terms:
            if term in query_lower:
                score -= 0.1
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def parse(self, query: str, diagnosis_text: Optional[str] = None) -> ParsedDiagnosis:
        """Main parsing function"""
        logger.info("Parsing diagnosis query", query_length=len(query))
        
        # Extract basic information
        age_group = self.parse_age_group(query)
        urgency_level = self.parse_urgency_level(query)
        system_category = self.extract_system_category(query)
        red_flags = self.extract_red_flags(query)
        key_symptoms = self.extract_key_symptoms(query)
        
        # Parse diagnosis text if provided, otherwise use query as diagnosis text
        if diagnosis_text:
            parsed_text = self.parse_diagnosis_text(diagnosis_text)
        else:
            # Use query as fallback for diagnosis text parsing
            parsed_text = self.parse_diagnosis_text(query)
        
        # Calculate confidence
        temp_data = {
            "key_symptoms": key_symptoms,
            "system_category": system_category
        }
        confidence_score = self.calculate_confidence_score(query, temp_data)
        
        result = ParsedDiagnosis(
            primary_diagnosis=parsed_text["primary_diagnosis"],
            secondary_diagnoses=parsed_text["secondary_diagnoses"],
            differential_diagnoses=parsed_text["differential_diagnoses"],
            age_group=age_group,
            urgency_level=urgency_level,
            confidence_score=confidence_score,
            key_symptoms=key_symptoms,
            red_flags=red_flags,
            system_category=system_category,
            icd_codes=parsed_text["icd_codes"],
            metadata={
                "parsed_timestamp": datetime.utcnow().isoformat(),
                "query_length": len(query),
                "has_diagnosis_text": diagnosis_text is not None
            }
        )
        
        logger.info("Diagnosis parsing complete", 
                   age_group=age_group.value,
                   urgency_level=urgency_level.value,
                   confidence_score=confidence_score,
                   red_flags_count=len(red_flags))
        
        return result

class DiagnosisValidator:
    """Validates parsed diagnoses for safety and accuracy"""
    
    def __init__(self):
        self.age_appropriate_conditions = {
            AgeGroup.NEWBORN: ["jaundice", "sepsis", "respiratory distress", "feeding difficulties"],
            AgeGroup.INFANT: ["colic", "reflux", "ear infection", "viral illness"],
            AgeGroup.TODDLER: ["asthma", "eczema", "febrile seizures", "minor injuries"],
            AgeGroup.PRESCHOOL: ["strep throat", "hand foot mouth", "allergies", "behavioral issues"],
            AgeGroup.SCHOOL_AGE: ["ADHD", "learning disorders", "sports injuries", "obesity"],
            AgeGroup.ADOLESCENT: ["depression", "anxiety", "substance use", "eating disorders"]
        }
        
        self.contraindicated_combinations = [
            ("antibiotic", "viral infection"),
            ("cough suppressant", "productive cough"),
            ("aspirin", "child"),
            ("codeine", "child < 12 years")
        ]
    
    def validate_age_appropriateness(self, diagnosis: ParsedDiagnosis) -> bool:
        """Check if diagnosis is appropriate for age group"""
        primary = diagnosis.primary_diagnosis.lower()
        age_appropriate = self.age_appropriate_conditions.get(diagnosis.age_group, [])
        
        # Check if any age-appropriate conditions match
        for condition in age_appropriate:
            if condition in primary:
                return True
        
        # If no specific age-appropriate conditions found, check confidence
        return diagnosis.confidence_score >= 0.7
    
    def validate_red_flags(self, diagnosis: ParsedDiagnosis) -> List[str]:
        """Validate red flags and return warnings"""
        warnings = []
        
        # Check for high urgency without red flags
        if diagnosis.urgency_level in [UrgencyLevel.EMERGENCY, UrgencyLevel.URGENT]:
            if not diagnosis.red_flags:
                warnings.append("High urgency level but no red flags identified")
        
        # Check for red flags with low urgency
        if diagnosis.red_flags and diagnosis.urgency_level == UrgencyLevel.ROUTINE:
            warnings.append("Red flags identified but routine urgency level")
        
        return warnings
    
    def validate_confidence_threshold(self, diagnosis: ParsedDiagnosis, min_confidence: float = 0.3) -> bool:
        """Check if confidence meets minimum threshold"""
        return diagnosis.confidence_score >= min_confidence
    
    def validate(self, diagnosis: ParsedDiagnosis) -> Dict[str, Any]:
        """Comprehensive validation"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Age appropriateness check
        if not self.validate_age_appropriateness(diagnosis):
            validation_result["warnings"].append("Diagnosis may not be age-appropriate")
        
        # Red flag validation
        red_flag_warnings = self.validate_red_flags(diagnosis)
        validation_result["warnings"].extend(red_flag_warnings)
        
        # Confidence threshold
        if not self.validate_confidence_threshold(diagnosis):
            validation_result["errors"].append("Confidence score below minimum threshold")
            validation_result["is_valid"] = False
        
        # Check for empty primary diagnosis
        if not diagnosis.primary_diagnosis.strip():
            validation_result["errors"].append("No primary diagnosis identified")
            validation_result["is_valid"] = False
        
        # Generate recommendations
        if diagnosis.urgency_level == UrgencyLevel.EMERGENCY:
            validation_result["recommendations"].append("Immediate medical attention required")
        elif diagnosis.red_flags:
            validation_result["recommendations"].append("Consider urgent evaluation due to red flags")
        
        if diagnosis.confidence_score < 0.5:
            validation_result["recommendations"].append("Consider additional diagnostic workup")
        
        return validation_result