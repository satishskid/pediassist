"""
Patient communication engine for generating age-appropriate explanations
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import structlog
from datetime import datetime
import random

logger = structlog.get_logger(__name__)

class CommunicationStyle(Enum):
    """Communication style options"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    REASSURING = "reassuring"
    URGENT = "urgent"

class LanguageLevel(Enum):
    """Language complexity levels"""
    TODDLER = "toddler"  # 2-3 years
    PRESCHOOL = "preschool"  # 3-5 years
    SCHOOL_AGE = "school_age"  # 6-12 years
    ADOLESCENT = "adolescent"  # 13-18 years
    PARENT = "parent"  # Parent/caregiver level
    PROFESSIONAL = "professional"  # Healthcare professional level

@dataclass
class CommunicationTemplate:
    """Communication template structure"""
    template_id: str
    name: str
    description: str
    age_groups: List[str]
    conditions: List[str]
    style: CommunicationStyle
    language_level: LanguageLevel
    template_text: str
    key_points: List[str]
    call_to_action: str
    warnings: List[str]
    confidence_score: float
    last_updated: datetime

@dataclass
class GeneratedCommunication:
    """Generated communication output"""
    template_id: str
    title: str
    main_content: str
    key_points: List[str]
    call_to_action: str
    warnings: List[str]
    age_appropriate: bool
    language_level: LanguageLevel
    estimated_reading_time: int
    confidence_score: float
    metadata: Dict[str, Any]

class CommunicationEngine:
    """Advanced patient communication generator"""
    
    def __init__(self):
        self.templates = self._load_communication_templates()
        self.age_appropriate_explanations = self._load_age_appropriate_explanations()
        self.medical_translations = self._load_medical_translations()
        self.reassurance_phrases = self._load_reassurance_phrases()
    
    def _load_communication_templates(self) -> Dict[str, CommunicationTemplate]:
        """Load communication templates for various scenarios"""
        templates = {
            "fever_explanation": CommunicationTemplate(
                template_id="fever_explanation",
                name="Fever Explanation",
                description="Explain fever to parents and children",
                age_groups=["infant", "toddler", "preschool", "school_age"],
                conditions=["fever", "infection"],
                style=CommunicationStyle.REASSURING,
                language_level=LanguageLevel.PARENT,
                template_text="""
                Your child has a fever, which means their body temperature is higher than normal. 
                This is usually a sign that their body is fighting off an infection. 
                
                Think of fever like your child's body turning up the heat to fight off germs - 
                it's actually a good thing that shows their immune system is working hard to protect them.
                
                Most fevers in children are caused by viral infections and will go away on their own 
                in a few days. The fever itself isn't dangerous - it's just a symptom of the underlying illness.
                """,
                key_points=[
                    "Fever is the body's natural defense mechanism",
                    "Most fevers are caused by viral infections",
                    "Fever itself is not dangerous",
                    "Focus on keeping your child comfortable"
                ],
                call_to_action="Call us if fever lasts more than 3 days or your child seems very sick",
                warnings=["Seek immediate care for fever >104°F or in infants <3 months"],
                confidence_score=0.9,
                last_updated=datetime.utcnow()
            ),
            
            "medication_safety": CommunicationTemplate(
                template_id="medication_safety",
                name="Medication Safety",
                description="Explain medication safety to families",
                age_groups=["infant", "toddler", "preschool", "school_age", "adolescent"],
                conditions=["medication", "treatment"],
                style=CommunicationStyle.DETAILED,
                language_level=LanguageLevel.PARENT,
                template_text="""
                Medications can help your child feel better and fight off illness, but they must be used safely.
                
                Always follow these safety rules:
                - Give the exact dose prescribed by your doctor
                - Use the measuring device that came with the medicine
                - Give medicine at the right times
                - Never share medicines between family members
                - Keep all medicines out of children's reach
                
                If you miss a dose, don't double up on the next one. Just continue with the regular schedule.
                """,
                key_points=[
                    "Always use exact prescribed dose",
                    "Use proper measuring devices",
                    "Keep medicines out of reach",
                    "Don't share medicines"
                ],
                call_to_action="Call our office if you have any questions about giving medicine",
                warnings=["Call poison control immediately if too much medicine is given"],
                confidence_score=0.95,
                last_updated=datetime.utcnow()
            ),
            
            "procedure_explanation": CommunicationTemplate(
                template_id="procedure_explanation",
                name="Medical Procedure Explanation",
                description="Explain medical procedures to children and families",
                age_groups=["toddler", "preschool", "school_age", "adolescent"],
                conditions=["procedure", "test", "examination"],
                style=CommunicationStyle.SIMPLE,
                language_level=LanguageLevel.SCHOOL_AGE,
                template_text="""
                We're going to do a test to help figure out what's making you feel sick.
                
                This test won't hurt, but it might feel a little strange or uncomfortable for a moment.
                The doctor/nurse will explain everything they're doing before they do it.
                
                You can ask questions anytime, and we can take breaks if you need them.
                Your parent/caregiver can stay with you during the test.
                """,
                key_points=[
                    "Test helps find out what's wrong",
                    "Won't hurt but might feel strange",
                    "Can ask questions anytime",
                    "Parent can stay with you"
                ],
                call_to_action="Let us know if you feel scared or uncomfortable",
                warnings=["Some procedures may require preparation - follow instructions carefully"],
                confidence_score=0.85,
                last_updated=datetime.utcnow()
            ),
            
            "emergency_instructions": CommunicationTemplate(
                template_id="emergency_instructions",
                name="Emergency Instructions",
                description="Provide emergency care instructions",
                age_groups=["parent", "adolescent"],
                conditions=["emergency", "urgent"],
                style=CommunicationStyle.URGENT,
                language_level=LanguageLevel.PROFESSIONAL,
                template_text="""
                Your child needs immediate medical attention. Here are the steps to take right now:
                
                1. Call 911 or go to the nearest emergency room immediately
                2. Bring this information with you
                3. Do not give any food or drink unless specifically instructed
                4. Keep your child calm and comfortable
                5. Monitor breathing and consciousness
                
                Go to the emergency room NOW - do not wait to see if symptoms improve.
                """,
                key_points=[
                    "Seek immediate medical attention",
                    "Call 911 or go to ER",
                    "Bring this information",
                    "Monitor vital signs"
                ],
                call_to_action="Go to emergency room immediately - do not delay",
                warnings=["This is a medical emergency - do not wait for symptoms to improve"],
                confidence_score=0.98,
                last_updated=datetime.utcnow()
            )
        }
        
        return templates
    
    def _load_age_appropriate_explanations(self) -> Dict[str, Dict[str, str]]:
        """Load age-appropriate medical explanations"""
        return {
            "fever": {
                "toddler": "Your body is hot because it's fighting germs!",
                "preschool": "You have a fever - your body is working hard to fight off sickness.",
                "school_age": "A fever means your body temperature is higher than normal. Your body raises its temperature to fight off infections.",
                "adolescent": "Fever is an elevated body temperature that occurs when your immune system responds to infection or inflammation.",
                "parent": "Fever is your child's natural defense mechanism against infection. The elevated temperature helps fight off pathogens."
            },
            "infection": {
                "toddler": "Tiny germs are making you feel yucky.",
                "preschool": "Germs got into your body and are making you feel sick.",
                "school_age": "An infection happens when harmful microorganisms like bacteria or viruses enter your body and multiply.",
                "adolescent": "Infection occurs when pathogenic microorganisms invade body tissues and trigger an immune response.",
                "parent": "Infection is the invasion and multiplication of microorganisms in body tissues, causing illness."
            },
            "antibiotic": {
                "toddler": "This medicine helps fight the bad germs.",
                "preschool": "This medicine helps your body fight the germs that are making you sick.",
                "school_age": "Antibiotics are medicines that kill bacteria or stop them from growing.",
                "adolescent": "Antibiotics are antimicrobial agents that inhibit bacterial growth or destroy bacteria.",
                "parent": "Antibiotics are medications that treat bacterial infections by killing bacteria or preventing their reproduction."
            }
        }
    
    def _load_medical_translations(self) -> Dict[str, str]:
        """Load medical term translations to plain language"""
        return {
            "febrile": "has a fever",
            "afebrile": "no fever",
            "acute": "sudden or recent",
            "chronic": "ongoing or long-lasting",
            "benign": "not dangerous or cancerous",
            "malignant": "cancerous or dangerous",
            "symptomatic": "having symptoms",
            "asymptomatic": "no symptoms",
            "diagnosis": "what's causing your illness",
            "prognosis": "expected outcome",
            "therapeutic": "treatment",
            "prophylactic": "preventive",
            "systemic": "affects the whole body",
            "localized": "affects one area",
            "bilateral": "both sides",
            "unilateral": "one side",
            "contraindication": "reason not to use",
            "adverse reaction": "side effect",
            "efficacy": "how well it works",
            "tolerability": "how well it's tolerated"
        }
    
    def _load_reassurance_phrases(self) -> Dict[str, List[str]]:
        """Load reassuring phrases for different situations"""
        return {
            "general": [
                "This is a common condition in children",
                "Most children recover completely",
                "Your child is in good hands",
                "We're here to help your child feel better",
                "This treatment has helped many children"
            ],
            "procedure": [
                "This will be over quickly",
                "You're being very brave",
                "The doctor is very gentle",
                "We'll explain everything first",
                "You can ask us to stop if you need to"
            ],
            "illness": [
                "Your child's body is working hard to get better",
                "This is temporary and will pass",
                "Many children have gone through this successfully",
                "Your child is responding well to treatment",
                "We're seeing improvement already"
            ]
        }
    
    def select_template(self, condition: str, age_group: str, communication_style: str = "reassuring") -> Optional[CommunicationTemplate]:
        """Select appropriate communication template"""
        # Find templates matching the condition and age group
        matching_templates = []
        
        for template in self.templates.values():
            # Check if condition matches
            condition_match = any(cond.lower() in condition.lower() for cond in template.conditions)
            
            # Check if age group matches
            age_match = age_group.lower() in [ag.lower() for ag in template.age_groups]
            
            # Check if style matches (or use default)
            style_match = (template.style.value == communication_style or 
                          communication_style == "auto")
            
            if condition_match and age_match and style_match:
                matching_templates.append(template)
        
        if not matching_templates:
            # Return a generic template if no specific match
            return self._create_generic_template(condition, age_group, communication_style)
        
        # Return the best matching template (highest confidence score)
        return max(matching_templates, key=lambda t: t.confidence_score)
    
    def _create_generic_template(self, condition: str, age_group: str, style: str) -> CommunicationTemplate:
        """Create a generic template when no specific match is found"""
        return CommunicationTemplate(
            template_id="generic_explanation",
            name=f"Generic {condition.title()} Explanation",
            description=f"General explanation for {condition}",
            age_groups=[age_group],
            conditions=[condition],
            style=CommunicationStyle(style),
            language_level=self._get_language_level(age_group),
            template_text=f"Your child has {condition}. Here's what you need to know...",
            key_points=["Follow your doctor's instructions", "Monitor for changes", "Contact us with questions"],
            call_to_action="Contact our office if you have concerns",
            warnings=["Seek emergency care for severe symptoms"],
            confidence_score=0.5,
            last_updated=datetime.utcnow()
        )
    
    def _get_language_level(self, age_group: str) -> LanguageLevel:
        """Get appropriate language level for age group"""
        level_map = {
            "toddler": LanguageLevel.TODDLER,
            "preschool": LanguageLevel.PRESCHOOL,
            "school_age": LanguageLevel.SCHOOL_AGE,
            "adolescent": LanguageLevel.ADOLESCENT,
            "parent": LanguageLevel.PARENT
        }
        return level_map.get(age_group, LanguageLevel.PARENT)
    
    def adapt_language(self, text: str, language_level: LanguageLevel, age_group: str) -> str:
        """Adapt language complexity to appropriate level"""
        # Replace medical terms with age-appropriate explanations
        for medical_term, plain_language in self.medical_translations.items():
            text = re.sub(rf"\b{medical_term}\b", plain_language, text, flags=re.IGNORECASE)
        
        # Add age-specific explanations for medical concepts
        if language_level == LanguageLevel.TODDLER:
            text = self._simplify_for_toddler(text)
        elif language_level == LanguageLevel.PRESCHOOL:
            text = self._simplify_for_preschool(text)
        elif language_level == LanguageLevel.SCHOOL_AGE:
            text = self._simplify_for_school_age(text)
        elif language_level == LanguageLevel.ADOLESCENT:
            text = self._adapt_for_adolescent(text)
        
        return text
    
    def _simplify_for_toddler(self, text: str) -> str:
        """Simplify language for toddlers (2-3 years)"""
        # Use very simple words and short sentences
        simplifications = {
            "temperature": "temperature (how hot your body is)",
            "infection": "germs making you sick",
            "medicine": "medicine to help you feel better",
            "doctor": "doctor (the person who helps you feel better)"
        }
        
        for complex_term, simple_term in simplifications.items():
            text = text.replace(complex_term, simple_term)
        
        # Break into very short sentences
        sentences = text.split('. ')
        simplified_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 20:
                # Break long sentences
                words = sentence.split()
                if len(words) > 10:
                    mid_point = len(words) // 2
                    simplified_sentences.append(' '.join(words[:mid_point]) + '.')
                    simplified_sentences.append(' '.join(words[mid_point:]) + '.')
                else:
                    simplified_sentences.append(sentence + '.')
            else:
                simplified_sentences.append(sentence + '.')
        
        return ' '.join(simplified_sentences)
    
    def _simplify_for_preschool(self, text: str) -> str:
        """Simplify language for preschoolers (3-5 years)"""
        # Use simple analogies and concrete examples
        analogies = {
            "immune system": "your body's superhero team",
            "bacteria": "tiny bugs that can make you sick",
            "virus": "tiny germs that can make you sick",
            "fever": "your body getting hot to fight germs"
        }
        
        for complex_term, analogy in analogies.items():
            text = text.replace(complex_term, analogy)
        
        return text
    
    def _simplify_for_school_age(self, text: str) -> str:
        """Adapt language for school-age children (6-12 years)"""
        # Add explanations but keep it engaging
        explanations = {
            "immune system": "your immune system (your body's defense team)",
            "antibiotic": "antibiotic (medicine that kills bacteria)",
            "inflammation": "inflammation (when part of your body gets red and swollen)"
        }
        
        for complex_term, explanation in explanations.items():
            text = text.replace(complex_term, explanation)
        
        return text
    
    def _adapt_for_adolescent(self, text: str) -> str:
        """Adapt language for adolescents (13-18 years)"""
        # Use more sophisticated language but still clear
        return text  # Adolescents can usually handle adult-level explanations
    
    def add_reassurance(self, text: str, situation: str = "general") -> str:
        """Add appropriate reassurance to communication"""
        reassurance_phrases = self.reassurance_phrases.get(situation, self.reassurance_phrases["general"])
        
        # Add 1-2 reassuring phrases
        selected_phrases = random.sample(reassurance_phrases, min(2, len(reassurance_phrases)))
        
        # Insert reassurance at appropriate points
        sentences = text.split('. ')
        if len(sentences) > 2:
            # Insert after first sentence
            sentences.insert(1, selected_phrases[0])
            if len(selected_phrases) > 1 and len(sentences) > 4:
                sentences.insert(-2, selected_phrases[1])
        
        return '. '.join(sentences)
    
    def estimate_reading_time(self, text: str, language_level: LanguageLevel) -> int:
        """Estimate reading time in minutes"""
        word_count = len(text.split())
        
        # Reading speed estimates (words per minute)
        reading_speeds = {
            LanguageLevel.TODDLER: 30,
            LanguageLevel.PRESCHOOL: 50,
            LanguageLevel.SCHOOL_AGE: 80,
            LanguageLevel.ADOLESCENT: 120,
            LanguageLevel.PARENT: 150,
            LanguageLevel.PROFESSIONAL: 200
        }
        
        speed = reading_speeds.get(language_level, 150)
        reading_time = word_count / speed
        
        return max(1, int(round(reading_time)))
    
    def generate_communication(self, condition: str, age_group: str, communication_style: str = "reassuring", 
                             patient_context: Optional[Dict[str, Any]] = None) -> GeneratedCommunication:
        """Generate age-appropriate patient communication"""
        logger.info("Generating patient communication", 
                   condition=condition, 
                   age_group=age_group, 
                   style=communication_style)
        
        # Select appropriate template
        template = self.select_template(condition, age_group, communication_style)
        if not template:
            logger.warning("No template found, using generic template")
            template = self._create_generic_template(condition, age_group, communication_style)
        
        # Adapt language to appropriate level
        adapted_text = self.adapt_language(template.template_text, template.language_level, age_group)
        
        # Add reassurance if appropriate
        if communication_style == "reassuring":
            adapted_text = self.add_reassurance(adapted_text, "illness")
        
        # Personalize with patient context
        if patient_context:
            adapted_text = self._personalize_text(adapted_text, patient_context)
        
        # Estimate reading time
        reading_time = self.estimate_reading_time(adapted_text, template.language_level)
        
        # Create final communication
        communication = GeneratedCommunication(
            template_id=template.template_id,
            title=template.name,
            main_content=adapted_text.strip(),
            key_points=template.key_points,
            call_to_action=template.call_to_action,
            warnings=template.warnings,
            age_appropriate=True,
            language_level=template.language_level,
            estimated_reading_time=reading_time,
            confidence_score=template.confidence_score,
            metadata={
                "generated_timestamp": datetime.utcnow().isoformat(),
                "condition": condition,
                "age_group": age_group,
                "style": communication_style,
                "patient_context": patient_context or {}
            }
        )
        
        logger.info("Patient communication generated successfully",
                   template_id=template.template_id,
                   reading_time=reading_time,
                   confidence_score=template.confidence_score)
        
        return communication
    
    def _personalize_text(self, text: str, patient_context: Dict[str, Any]) -> str:
        """Personalize text with patient context"""
        # Replace placeholders with patient-specific information
        if "child_name" in patient_context:
            text = text.replace("your child", patient_context["child_name"])
            text = text.replace("Your child", patient_context["child_name"])
        
        if "age" in patient_context:
            text = text.replace("your child", f"your {patient_context['age']}-year-old")
        
        if "specific_symptoms" in patient_context:
            symptoms = patient_context["specific_symptoms"]
            if symptoms:
                text += f"\n\nBased on {patient_context.get('child_name', 'your child')}'s symptoms: {', '.join(symptoms)}"
        
        return text

class CommunicationValidator:
    """Validates generated communications for appropriateness and safety"""
    
    def __init__(self):
        self.inappropriate_terms = [
            "guarantee", "promise", "always works", "never fails",
            "100% effective", "completely safe", "no side effects"
        ]
        
        self.required_disclaimers = [
            "contact your healthcare provider",
            "seek medical attention",
            "emergency room"
        ]
    
    def validate_language_appropriateness(self, communication: GeneratedCommunication) -> List[str]:
        """Validate language appropriateness for age group"""
        warnings = []
        
        text = communication.main_content.lower()
        
        # Check for complex medical terms in toddler/preschool communications
        if communication.language_level in [LanguageLevel.TODDLER, LanguageLevel.PRESCHOOL]:
            complex_terms = ["pathophysiology", "etiology", "prognosis", "contraindication"]
            for term in complex_terms:
                if term in text:
                    warnings.append(f"Complex medical term '{term}' in {communication.language_level.value} communication")
        
        # Check for overly simplistic language in professional communications
        if communication.language_level == LanguageLevel.PROFESSIONAL:
            if len(text.split('.')) < 3:  # Too few sentences
                warnings.append("Professional communication may be too brief")
        
        return warnings
    
    def validate_safety_disclaimers(self, communication: GeneratedCommunication) -> List[str]:
        """Validate that safety disclaimers are present"""
        warnings = []
        text = communication.main_content.lower() + communication.call_to_action.lower()
        
        # Check for required disclaimers
        has_contact_provider = any(disclaimer in text for disclaimer in ["contact your healthcare provider", "call your doctor"])
        has_emergency_disclaimer = any(disclaimer in text for disclaimer in ["seek medical attention", "emergency room", "call 911"])
        
        if not has_contact_provider:
            warnings.append("Missing contact healthcare provider disclaimer")
        
        if not has_emergency_disclaimer:
            warnings.append("Missing emergency care disclaimer")
        
        return warnings
    
    def validate_inappropriate_claims(self, communication: GeneratedCommunication) -> List[str]:
        """Validate that communication doesn't make inappropriate claims"""
        warnings = []
        text = communication.main_content.lower()
        
        for inappropriate_term in self.inappropriate_terms:
            if inappropriate_term in text:
                warnings.append(f"Inappropriate claim: '{inappropriate_term}' - may create false expectations")
        
        return warnings
    
    def validate(self, communication: GeneratedCommunication) -> Dict[str, Any]:
        """Comprehensive validation"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Language appropriateness
        language_warnings = self.validate_language_appropriateness(communication)
        validation_result["warnings"].extend(language_warnings)
        
        # Safety disclaimers
        disclaimer_warnings = self.validate_safety_disclaimers(communication)
        validation_result["warnings"].extend(disclaimer_warnings)
        
        # Inappropriate claims
        claim_warnings = self.validate_inappropriate_claims(communication)
        validation_result["warnings"].extend(claim_warnings)
        
        # Check confidence score
        if communication.confidence_score < 0.5:
            validation_result["warnings"].append("Low confidence score - review content carefully")
        
        # Generate recommendations
        if disclaimer_warnings:
            validation_result["recommendations"].append("Add appropriate safety disclaimers")
        
        if claim_warnings:
            validation_result["recommendations"].append("Remove absolute or guarantee statements")
        
        return validation_result