"""
Diagnosis parser for extracting and validating medical information
"""

import re
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import structlog
from datetime import datetime

logger = structlog.get_logger()

@dataclass
class ParsedDiagnosis:
    """Structured representation of a parsed diagnosis"""
    primary_diagnosis: str
    secondary_diagnoses: List[str]
    symptoms: List[str]
    severity: str  # 'mild', 'moderate', 'severe'
    urgency: str  # 'routine', 'urgent', 'emergency'
    age_group: str  # 'newborn', 'infant', 'toddler', 'preschool', 'school_age', 'adolescent'
    body_system: str  # 'respiratory', 'cardiovascular', 'gastrointestinal', etc.
    icd10_codes: List[str]
    confidence_score: float  # 0.0 to 1.0

class DiagnosisParser:
    """Parses and validates medical diagnoses"""
    
    def __init__(self):
        # Common pediatric symptoms and their patterns
        self.symptom_patterns = {
            'fever': [
                r'fever', r'febrile', r'temperature', r'pyrexia',
                r'\b\d+\.?\d*°?[CF]\b', r'\b\d+\.?\d* degrees?\b'
            ],
            'cough': [
                r'cough', r'coughing', r'hacking', r'productive cough',
                r'dry cough', r'wet cough', r'barking cough'
            ],
            'breathing_difficulty': [
                r'dyspnea', r'shortness of breath', r'sob', r'tachypnea',
                r'rapid breathing', r'labored breathing', r'breathing difficulty',
                r'wheezing', r'stridor', r'retractions'
            ],
            'vomiting': [
                r'vomiting', r'emesis', r'throwing up', r'puking',
                r'vomited', r'vomitus'
            ],
            'diarrhea': [
                r'diarrhea', r'diarrhoea', r'loose stools', r'watery stools',
                r'frequent stools', r'\d+ stools? per day'
            ],
            'rash': [
                r'rash', r'eruption', r'exanthem', r'maculopapular',
                r'vesicular', r'petechial', r'purpuric'
            ],
            'pain': [
                r'pain', r'ache', r'hurts', r'discomfort', r'tenderness',
                r'sore', r'throbbing', r'sharp pain', r'dull pain'
            ],
            'fatigue': [
                r'fatigue', r'tired', r'lethargy', r'weakness', r'malaise',
                r'exhausted', r'low energy'
            ]
        }
        
        # Common pediatric diagnoses and their patterns
        self.diagnosis_patterns = {
            'asthma': [
                r'asthma', r'reactive airway disease', r'rad', r'wheezing',
                r'bronchospasm', r'reversible airway obstruction'
            ],
            'pneumonia': [
                r'pneumonia', r'pneumonitis', r'lower respiratory infection',
                r'lung infection', r'consolidation'
            ],
            'bronchiolitis': [
                r'bronchiolitis', r'rsv', r'respiratory syncytial virus',
                r'bronchial inflammation'
            ],
            'otitis_media': [
                r'otitis media', r'ear infection', r'middle ear infection',
                r'acute otitis media', r'aom'
            ],
            'strep_throat': [
                r'streptococcal', r'strep throat', r'group a strep',
                r'pharyngitis', r'tonsillitis'
            ],
            'gastroenteritis': [
                r'gastroenteritis', r'stomach flu', r'viral gastroenteritis',
                r'acute gastroenteritis'
            ],
            'constipation': [
                r'constipation', r'functional constipation', r'encopresis',
                r'infrequent stools', r'hard stools'
            ],
            'eczema': [
                r'eczema', r'atopic dermatitis', r'atopic eczema',
                r'flexural eczema'
            ],
            'allergic_rhinitis': [
                r'allergic rhinitis', r'hay fever', r'nasal allergies',
                r'seasonal allergies', r'perennial allergies'
            ],
            'febrile_seizure': [
                r'febrile seizure', r'fever seizure', r'convulsion with fever',
                r'fever convulsion'
            ]
        }
        
        # Age group patterns
        self.age_patterns = {
            'newborn': [r'newborn', r'neonate', r'0-28 days', r'\b\d+ days? old\b'],
            'infant': [r'infant', r'baby', r'1-12 months', r'\b\d+ months? old\b'],
            'toddler': [r'toddler', r'1-3 years', r'\b1[\s-]?3 years? old\b'],
            'preschool': [r'preschool', r'3-5 years', r'\b3[\s-]?5 years? old\b'],
            'school_age': [r'school age', r'6-12 years', r'\b6[\s-]?12 years? old\b'],
            'adolescent': [r'adolescent', r'teen', r'13-18 years', r'\b1[3-8][\s-]?years? old\b']
        }
        
        # Body system patterns
        self.body_system_patterns = {
            'respiratory': [r'respiratory', r'lung', r'breathing', r'chest', r'pulmonary'],
            'cardiovascular': [r'cardiac', r'heart', r'cardiovascular', r'circulatory'],
            'gastrointestinal': [r'gi', r'gastrointestinal', r'stomach', r'intestinal', r'digestive'],
            'neurological': [r'neurological', r'brain', r'nervous system', r'neurologic'],
            'dermatological': [r'skin', r'dermatological', r'dermal', r'cutaneous'],
            'genitourinary': [r'genitourinary', r'gu', r'urinary', r'genital'],
            'musculoskeletal': [r'musculoskeletal', r'muscle', r'bone', r'joint', r'skeletal'],
            'hematological': [r'blood', r'hematological', r'hematologic', r'bone marrow'],
            'immunological': [r'immune', r'immunological', r'allergic', r'autoimmune'],
            'endocrine': [r'endocrine', r'hormonal', r'gland', r'metabolic']
        }
        
        # Severity indicators
        self.severity_patterns = {
            'mild': [r'mild', r'slight', r'minimal', r'low grade', r'subtle'],
            'moderate': [r'moderate', r'moderate severity', r'intermediate', r'moderately'],
            'severe': [r'severe', r'serious', r'critical', r'life-threatening', r'profound']
        }
        
        # Urgency indicators
        self.urgency_patterns = {
            'routine': [r'routine', r'scheduled', r'elective', r'non-urgent', r'follow-up'],
            'urgent': [r'urgent', r'urgently', r'asap', r'prompt', r'timely'],
            'emergency': [r'emergency', r'emergent', r'immediately', r'call 911', r'life-threatening']
        }
    
    def parse_diagnosis(self, text: str, patient_age: Optional[int] = None) -> ParsedDiagnosis:
        """Parse diagnosis from text input"""
        
        text_lower = text.lower()
        
        # Extract symptoms
        symptoms = self._extract_symptoms(text_lower)
        
        # Extract primary and secondary diagnoses
        primary_diagnosis, secondary_diagnoses = self._extract_diagnoses(text_lower)
        
        # Extract age group
        age_group = self._extract_age_group(text_lower)
        if patient_age is not None:
            age_group = self._get_age_group_from_age(patient_age)
        
        # Extract body system
        body_system = self._extract_body_system(text_lower)
        
        # Extract severity
        severity = self._extract_severity(text_lower)
        
        # Extract urgency
        urgency = self._extract_urgency(text_lower)
        
        # Extract ICD-10 codes if present
        icd10_codes = self._extract_icd10_codes(text)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            primary_diagnosis, symptoms, text
        )
        
        return ParsedDiagnosis(
            primary_diagnosis=primary_diagnosis or "unspecified",
            secondary_diagnoses=secondary_diagnoses,
            symptoms=symptoms,
            severity=severity,
            urgency=urgency,
            age_group=age_group,
            body_system=body_system,
            icd10_codes=icd10_codes,
            confidence_score=confidence_score
        )
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text"""
        symptoms = []
        
        for symptom_name, patterns in self.symptom_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    symptoms.append(symptom_name)
                    break
        
        return list(set(symptoms))  # Remove duplicates
    
    def _extract_diagnoses(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract primary and secondary diagnoses"""
        diagnoses = []
        
        for diagnosis_name, patterns in self.diagnosis_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    diagnoses.append(diagnosis_name)
                    break
        
        if not diagnoses:
            return None, []
        
        primary = diagnoses[0]
        secondary = diagnoses[1:] if len(diagnoses) > 1 else []
        
        return primary, secondary
    
    def _extract_age_group(self, text: str) -> str:
        """Extract age group from text"""
        for age_group, patterns in self.age_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return age_group
        
        return "unspecified"
    
    def _get_age_group_from_age(self, age_months: int) -> str:
        """Get age group from age in months"""
        if age_months < 1:
            return "newborn"
        elif age_months < 12:
            return "infant"
        elif age_months < 36:
            return "toddler"
        elif age_months < 72:
            return "preschool"
        elif age_months < 156:
            return "school_age"
        else:
            return "adolescent"
    
    def _extract_body_system(self, text: str) -> str:
        """Extract body system from text"""
        for system, patterns in self.body_system_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return system
        
        return "unspecified"
    
    def _extract_severity(self, text: str) -> str:
        """Extract severity from text"""
        for severity, patterns in self.severity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return severity
        
        return "moderate"  # Default to moderate
    
    def _extract_urgency(self, text: str) -> str:
        """Extract urgency from text"""
        for urgency, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return urgency
        
        return "routine"  # Default to routine
    
    def _extract_icd10_codes(self, text: str) -> List[str]:
        """Extract ICD-10 codes from text"""
        # ICD-10 code pattern: letter followed by 2-7 digits and optional letter
        icd10_pattern = r'\b[A-Z]\d{2,7}[A-Z]?\b'
        
        matches = re.findall(icd10_pattern, text)
        return [match.upper() for match in matches]
    
    def _calculate_confidence(self, primary_diagnosis: str, symptoms: List[str], text: str) -> float:
        """Calculate confidence score for the parsed diagnosis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we have a primary diagnosis
        if primary_diagnosis and primary_diagnosis != "unspecified":
            confidence += 0.2
        
        # Increase confidence if we have symptoms
        if symptoms:
            confidence += min(len(symptoms) * 0.05, 0.2)  # Max 0.2 bonus
        
        # Increase confidence if text mentions medical terms
        medical_terms = [
            r'diagnosis', r'symptom', r'sign', r'examination', r'assessment',
            r'plan', r'treatment', r'medication', r'prescription'
        ]
        
        medical_term_count = 0
        for pattern in medical_terms:
            if re.search(pattern, text, re.IGNORECASE):
                medical_term_count += 1
        
        confidence += min(medical_term_count * 0.02, 0.1)  # Max 0.1 bonus
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def validate_diagnosis(self, diagnosis: ParsedDiagnosis) -> Dict[str, Any]:
        """Validate the parsed diagnosis"""
        
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for missing primary diagnosis
        if not diagnosis.primary_diagnosis or diagnosis.primary_diagnosis == "unspecified":
            validation_result["errors"].append("Primary diagnosis is missing or unspecified")
            validation_result["is_valid"] = False
        
        # Check for low confidence
        if diagnosis.confidence_score < 0.6:
            validation_result["warnings"].append(f"Low confidence score: {diagnosis.confidence_score:.2f}")
            validation_result["recommendations"].append("Consider reviewing the diagnosis for accuracy")
        
        # Check for emergency urgency
        if diagnosis.urgency == "emergency":
            validation_result["warnings"].append("Emergency urgency detected")
            validation_result["recommendations"].append("Immediate medical attention may be required")
        
        # Check for severe symptoms in infants
        if diagnosis.age_group in ["newborn", "infant"] and diagnosis.severity == "severe":
            validation_result["warnings"].append("Severe symptoms in young infant")
            validation_result["recommendations"].append("Consider immediate evaluation")
        
        # Check for age-appropriate symptoms
        age_appropriate_warnings = self._check_age_appropriateness(diagnosis)
        validation_result["warnings"].extend(age_appropriate_warnings)
        
        return validation_result
    
    def _check_age_appropriateness(self, diagnosis: ParsedDiagnosis) -> List[str]:
        """Check if symptoms/diagnoses are age-appropriate"""
        warnings = []
        
        # Age-inappropriate conditions
        age_restrictions = {
            "newborn": ["febrile_seizure"],  # Febrile seizures don't occur in newborns
            "infant": ["strep_throat"],      # Rare in infants under 6 months
            "toddler": ["allergic_rhinitis"] # Uncommon in toddlers under 2
        }
        
        if diagnosis.age_group in age_restrictions:
            restricted_conditions = age_restrictions[diagnosis.age_group]
            if diagnosis.primary_diagnosis in restricted_conditions:
                warnings.append(f"{diagnosis.primary_diagnosis} is unusual in {diagnosis.age_group} patients")
        
        return warnings