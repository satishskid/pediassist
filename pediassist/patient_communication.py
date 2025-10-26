"""
Patient Communication Templates for PediAssist
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

class CommunicationType(Enum):
    DIAGNOSIS_EXPLANATION = "diagnosis_explanation"
    TREATMENT_INSTRUCTIONS = "treatment_instructions"
    MEDICATION_GUIDANCE = "medication_guidance"
    FOLLOW_UP_PLAN = "follow_up_plan"
    RED_FLAGS = "red_flags"
    PREVENTION_TIPS = "prevention_tips"
    EMERGENCY_WARNING = "emergency_warning"

class AgeGroup(Enum):
    INFANT = "infant"  # 0-12 months
    TODDLER = "toddler"  # 1-3 years
    PRESCHOOL = "preschool"  # 3-5 years
    SCHOOL_AGE = "school_age"  # 5-12 years
    ADOLESCENT = "adolescent"  # 12-18 years

class Language(Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    PORTUGUESE = "pt"

@dataclass
class CommunicationContext:
    patient_age_months: int
    patient_name: Optional[str] = None
    parent_name: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[Dict[str, Any]] = None
    medications: Optional[list] = None
    follow_up_needed: bool = False
    urgency_level: str = "routine"
    language: Language = Language.ENGLISH
    cultural_considerations: Optional[Dict[str, Any]] = None

class PatientCommunicationGenerator:
    """Generate age-appropriate, culturally sensitive patient communications"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.age_adjustments = self._load_age_adjustments()
        self.cultural_adaptations = self._load_cultural_adaptations()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load communication templates"""
        return {
            CommunicationType.DIAGNOSIS_EXPLANATION: {
                "infant": {
                    "template": "Your baby has {diagnosis}. This is {simple_explanation}. {reassurance}",
                    "simple_explanations": {
                        "acute otitis media": "an ear infection that can cause pain and fever",
                        "viral upper respiratory infection": "a common cold virus",
                        "gastroenteritis": "a stomach virus causing vomiting or diarrhea",
                        "bronchiolitis": "a chest infection that causes wheezing and cough"
                    }
                },
                "toddler": {
                    "template": "Your child has {diagnosis}. This means {simple_explanation}. {reassurance}",
                    "simple_explanations": {
                        "acute otitis media": "their ear is infected and might be hurting",
                        "viral upper respiratory infection": "they have a cold virus",
                        "gastroenteritis": "their tummy is upset from a virus",
                        "bronchiolitis": "their chest is making wheezing sounds"
                    }
                },
                "preschool": {
                    "template": "{patient_name} has {diagnosis}. This is when {detailed_explanation}. {reassurance}",
                    "detailed_explanations": {
                        "acute otitis media": "the middle part of the ear gets infected and fills with fluid, causing pain and sometimes fever",
                        "viral upper respiratory infection": "a virus infects the nose, throat, and sinuses",
                        "gastroenteritis": "a virus causes inflammation in the stomach and intestines",
                        "bronchiolitis": "small airways in the lungs become inflamed and make it hard to breathe"
                    }
                },
                "school_age": {
                    "template": "{patient_name} has been diagnosed with {diagnosis}. This condition occurs when {medical_explanation}. {prognosis}",
                    "medical_explanations": {
                        "acute otitis media": "bacteria or viruses infect the middle ear, causing fluid buildup and pressure",
                        "viral upper respiratory infection": "viruses attack the upper respiratory tract",
                        "gastroenteritis": "viruses or bacteria irritate the digestive system",
                        "bronchiolitis": "respiratory syncytial virus (RSV) causes inflammation in the small airways"
                    }
                },
                "adolescent": {
                    "template": "The diagnosis for {patient_name} is {diagnosis}. {comprehensive_explanation}",
                    "comprehensive_explanations": {
                        "acute otitis media": "This is an infection of the middle ear space, often following a cold or allergies.",
                        "viral upper respiratory infection": "This common viral infection affects the nose, throat, and sinuses.",
                        "gastroenteritis": "This is inflammation of the stomach and intestines, usually caused by a viral infection.",
                        "bronchiolitis": "This viral infection causes inflammation in the small breathing tubes of the lungs."
                    }
                }
            },
            CommunicationType.TREATMENT_INSTRUCTIONS: {
                "infant": {
                    "template": "Here's how to help your baby feel better: {instructions}. Call us if you have any concerns.",
                    "instructions": {
                        "hydration": "Continue breastfeeding or formula feeding frequently",
                        "comfort": "Hold and comfort your baby, keep them upright when possible",
                        "monitoring": "Watch for fever, poor feeding, or unusual crying"
                    }
                },
                "toddler": {
                    "template": "To help {patient_name} get better: {instructions}. Contact us if symptoms worsen.",
                    "instructions": {
                        "hydration": "Offer small amounts of fluids frequently",
                        "rest": "Encourage quiet activities and extra rest",
                        "comfort": "Use comfort measures appropriate for their age"
                    }
                },
                "preschool": {
                    "template": "Treatment plan for {patient_name}: {instructions}. Follow up if needed.",
                    "instructions": {
                        "medications": "Give medications exactly as prescribed",
                        "activity": "Allow quiet activities but avoid strenuous play",
                        "diet": "Offer favorite healthy foods and plenty of fluids"
                    }
                },
                "school_age": {
                    "template": "Here's what {patient_name} needs to do: {instructions}. Questions? We're here to help.",
                    "instructions": {
                        "medications": "Take all medications as directed, even if feeling better",
                        "activity": "Rest as needed, gradually return to normal activities",
                        "monitoring": "Keep track of symptoms and temperature"
                    }
                },
                "adolescent": {
                    "template": "Treatment recommendations for {patient_name}: {instructions}. Follow up as scheduled.",
                    "instructions": {
                        "medications": "Complete the full course of prescribed medications",
                        "self_care": "Practice good self-care and rest",
                        "monitoring": "Monitor symptoms and seek care if they worsen"
                    }
                }
            },
            CommunicationType.MEDICATION_GUIDANCE: {
                "general": {
                    "template": "Medication instructions: {medication_info}. {safety_notes}",
                    "safety_notes": "Store medications safely out of children's reach. Never share medications."
                }
            },
            CommunicationType.RED_FLAGS: {
                "emergency": {
                    "template": "🚨 SEEK IMMEDIATE MEDICAL ATTENTION if: {emergency_signs}",
                    "emergency_signs": [
                        "difficulty breathing or shortness of breath",
                        "persistent high fever (>103°F)",
                        "severe pain that doesn't improve",
                        "confusion or altered mental state",
                        "signs of dehydration (dry mouth, no tears, no urination)"
                    ]
                },
                "urgent": {
                    "template": "⚠️ Contact your healthcare provider today if: {urgent_signs}",
                    "urgent_signs": [
                        "fever lasting more than 3 days",
                        "worsening symptoms",
                        "new concerning symptoms",
                        "poor response to treatment"
                    ]
                }
            }
        }
    
    def _load_age_adjustments(self) -> Dict[str, Dict[str, Any]]:
        """Load age-specific communication adjustments"""
        return {
            AgeGroup.INFANT: {
                "vocabulary_level": "very_simple",
                "sentence_length": "short",
                "focus": "parent_comfort",
                "detail_level": "minimal"
            },
            AgeGroup.TODDLER: {
                "vocabulary_level": "simple",
                "sentence_length": "short",
                "focus": "parent_action",
                "detail_level": "basic"
            },
            AgeGroup.PRESCHOOL: {
                "vocabulary_level": "moderate",
                "sentence_length": "medium",
                "focus": "parent_child",
                "detail_level": "moderate"
            },
            AgeGroup.SCHOOL_AGE: {
                "vocabulary_level": "age_appropriate",
                "sentence_length": "medium",
                "focus": "child_patient",
                "detail_level": "detailed"
            },
            AgeGroup.ADOLESCENT: {
                "vocabulary_level": "adult_level",
                "sentence_length": "complex",
                "focus": "patient_autonomy",
                "detail_level": "comprehensive"
            }
        }
    
    def _load_cultural_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """Load cultural communication adaptations"""
        return {
            "hispanic": {
                "family_focus": True,
                "extended_family": True,
                "religious_considerations": True,
                "language_preferences": ["Spanish", "English"]
            },
            "asian": {
                "family_focus": True,
                "elder_respect": True,
                "indirect_communication": True,
                "language_preferences": ["English", "Mandarin", "Cantonese", "Vietnamese"]
            },
            "african_american": {
                "community_focus": True,
                "historical_medical_distrust": True,
                "extended_family": True,
                "language_preferences": ["English"]
            }
        }
    
    def get_age_group(self, age_months: int) -> AgeGroup:
        """Determine age group from age in months"""
        if age_months < 12:
            return AgeGroup.INFANT
        elif age_months < 36:
            return AgeGroup.TODDLER
        elif age_months < 60:
            return AgeGroup.PRESCHOOL
        elif age_months < 144:
            return AgeGroup.SCHOOL_AGE
        else:
            return AgeGroup.ADOLESCENT
    
    def generate_communication(self, 
                             communication_type: CommunicationType,
                             context: CommunicationContext) -> str:
        """Generate age-appropriate communication"""
        
        age_group = self.get_age_group(context.patient_age_months)
        
        try:
            if communication_type == CommunicationType.DIAGNOSIS_EXPLANATION:
                return self._generate_diagnosis_explanation(context, age_group)
            elif communication_type == CommunicationType.TREATMENT_INSTRUCTIONS:
                return self._generate_treatment_instructions(context, age_group)
            elif communication_type == CommunicationType.MEDICATION_GUIDANCE:
                return self._generate_medication_guidance(context, age_group)
            elif communication_type == CommunicationType.RED_FLAGS:
                return self._generate_red_flags(context, age_group)
            elif communication_type == CommunicationType.FOLLOW_UP_PLAN:
                return self._generate_follow_up_plan(context, age_group)
            else:
                return self._generate_generic_message(context, age_group)
                
        except Exception as e:
            logger.error(f"Error generating communication: {e}")
            return self._generate_fallback_message(context, age_group)
    
    def _generate_diagnosis_explanation(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate diagnosis explanation"""
        template_data = self.templates[CommunicationType.DIAGNOSIS_EXPLANATION][age_group.value]
        template = template_data["template"]
        
        # Get appropriate explanation
        if context.diagnosis in template_data["simple_explanations"]:
            explanation = template_data["simple_explanations"][context.diagnosis]
        elif "detailed_explanations" in template_data and context.diagnosis in template_data["detailed_explanations"]:
            explanation = template_data["detailed_explanations"][context.diagnosis]
        elif "medical_explanations" in template_data and context.diagnosis in template_data["medical_explanations"]:
            explanation = template_data["medical_explanations"][context.diagnosis]
        elif "comprehensive_explanations" in template_data and context.diagnosis in template_data["comprehensive_explanations"]:
            explanation = template_data["comprehensive_explanations"][context.diagnosis]
        else:
            explanation = f"{context.diagnosis} - a medical condition requiring treatment"
        
        # Generate reassurance based on urgency
        if context.urgency_level == "emergency":
            reassurance = "This requires immediate medical attention."
        elif context.urgency_level == "urgent":
            reassurance = "This needs prompt medical treatment."
        else:
            reassurance = "With proper treatment, most children recover well."
        
        # Fill template
        return template.format(
            patient_name=context.patient_name or "Your child",
            diagnosis=context.diagnosis or "a medical condition",
            simple_explanation=explanation,
            detailed_explanation=explanation,
            medical_explanation=explanation,
            comprehensive_explanation=explanation,
            reassurance=reassurance
        )
    
    def _generate_treatment_instructions(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate treatment instructions"""
        template_data = self.templates[CommunicationType.TREATMENT_INSTRUCTIONS][age_group.value]
        template = template_data["template"]
        
        # Build instructions based on treatment plan
        instructions = []
        if context.treatment_plan:
            if "medications" in context.treatment_plan:
                instructions.append("give medications as prescribed")
            if "rest" in context.treatment_plan.get("recommendations", []):
                instructions.append("ensure plenty of rest")
            if "hydration" in context.treatment_plan.get("recommendations", []):
                instructions.append("maintain good hydration")
        
        if not instructions:
            instructions = ["follow the treatment plan as prescribed"]
        
        return template.format(
            patient_name=context.patient_name or "your child",
            instructions=", ".join(instructions)
        )
    
    def _generate_medication_guidance(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate medication guidance"""
        template_data = self.templates[CommunicationType.MEDICATION_GUIDANCE]["general"]
        template = template_data["template"]
        
        medication_info = []
        if context.medications:
            for med in context.medications:
                medication_info.append(f"{med.get('name', 'Medication')}: {med.get('instructions', 'Take as directed')}")
        
        medication_text = "; ".join(medication_info) if medication_info else "Take all medications as prescribed"
        
        return template.format(
            medication_info=medication_text,
            safety_notes=template_data["safety_notes"]
        )
    
    def _generate_red_flags(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate red flag warnings"""
        if context.urgency_level == "emergency":
            template_data = self.templates[CommunicationType.RED_FLAGS]["emergency"]
            template = template_data["template"]
            emergency_signs = template_data["emergency_signs"]
        else:
            template_data = self.templates[CommunicationType.RED_FLAGS]["urgent"]
            template = template_data["template"]
            emergency_signs = template_data["urgent_signs"]
        
        return template.format(
            emergency_signs="; ".join(emergency_signs),
            urgent_signs="; ".join(emergency_signs)
        )
    
    def _generate_follow_up_plan(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate follow-up plan"""
        if context.follow_up_needed:
            return f"Follow-up appointment is recommended. Please schedule within the timeframe discussed with your healthcare provider."
        else:
            return "No follow-up needed unless symptoms persist or worsen."
    
    def _generate_generic_message(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate generic message"""
        return f"Please follow your healthcare provider's recommendations for {context.patient_name or 'your child'}. Contact us with any questions."
    
    def _generate_fallback_message(self, context: CommunicationContext, age_group: AgeGroup) -> str:
        """Generate fallback message when template generation fails"""
        return f"Please consult with your healthcare provider about {context.patient_name or 'your child'}'s condition and treatment."
    
    def generate_comprehensive_communication(self, 
                                           context: CommunicationContext,
                                           include_types: Optional[list] = None) -> Dict[str, str]:
        """Generate comprehensive communication package"""
        
        if include_types is None:
            include_types = [
                CommunicationType.DIAGNOSIS_EXPLANATION,
                CommunicationType.TREATMENT_INSTRUCTIONS,
                CommunicationType.MEDICATION_GUIDANCE,
                CommunicationType.RED_FLAGS,
                CommunicationType.FOLLOW_UP_PLAN
            ]
        
        communications = {}
        
        for comm_type in include_types:
            communications[comm_type.value] = self.generate_communication(comm_type, context)
        
        return communications
    
    def translate_communication(self, communication: str, target_language: Language) -> str:
        """Translate communication to target language (placeholder for actual translation)"""
        # This would integrate with a translation service
        # For now, return the original communication with a note
        if target_language != Language.ENGLISH:
            return f"[Translation to {target_language.value} would be provided here]\n{communication}"
        return communication

# Global instance
communication_generator = PatientCommunicationGenerator()

def generate_patient_communication(communication_type: CommunicationType,
                                 patient_age_months: int,
                                 diagnosis: Optional[str] = None,
                                 treatment_plan: Optional[Dict[str, Any]] = None,
                                 **kwargs) -> str:
    """Convenience function for generating patient communications"""
    
    context = CommunicationContext(
        patient_age_months=patient_age_months,
        diagnosis=diagnosis,
        treatment_plan=treatment_plan,
        **kwargs
    )
    
    return communication_generator.generate_communication(communication_type, context)

def generate_comprehensive_patient_education(patient_age_months: int,
                                             diagnosis: str,
                                             treatment_plan: Dict[str, Any],
                                             **kwargs) -> Dict[str, str]:
    """Generate comprehensive patient education materials"""
    
    context = CommunicationContext(
        patient_age_months=patient_age_months,
        diagnosis=diagnosis,
        treatment_plan=treatment_plan,
        **kwargs
    )
    
    return communication_generator.generate_comprehensive_communication(context)