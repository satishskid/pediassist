"""
Delegation manager for routing complex cases to appropriate specialists
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

class UrgencyLevel(Enum):
    """Case urgency levels"""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    SEMI_URGENT = "semi_urgent"
    ROUTINE = "routine"

class ComplexityLevel(Enum):
    """Case complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    HIGHLY_COMPLEX = "highly_complex"

class SpecialistType(Enum):
    """Types of specialists"""
    PEDIATRICIAN = "pediatrician"
    PEDIATRIC_SPECIALIST = "pediatric_specialist"
    EMERGENCY_PHYSICIAN = "emergency_physician"
    INTENSIVIST = "intensivist"
    SURGEON = "surgeon"
    CARDIOLOGIST = "cardiologist"
    NEUROLOGIST = "neurologist"
    ONCOLOGIST = "oncologist"
    ENDOCRINOLOGIST = "endocrinologist"
    GASTROENTEROLOGIST = "gastroenterologist"
    NEPHROLOGIST = "nephrologist"
    HEMATOLOGIST = "hematologist"
    IMMUNOLOGIST = "immunologist"
    INFECTIOUS_DISEASE = "infectious_disease"
    PSYCHIATRIST = "psychiatrist"
    PSYCHOLOGIST = "psychologist"
    SOCIAL_WORKER = "social_worker"

@dataclass
class DelegationRule:
    """Delegation rule structure"""
    rule_id: str
    name: str
    description: str
    conditions: List[str]  # Medical conditions that trigger this rule
    symptoms: List[str]      # Specific symptoms
    age_groups: List[str]    # Applicable age groups
    urgency_levels: List[str]
    complexity_levels: List[str]
    specialist_types: List[SpecialistType]
    time_frame: str         # When to see specialist (e.g., "within_24_hours")
    rationale: str          # Why this delegation is recommended
    confidence_score: float
    is_active: bool

@dataclass
class DelegationRecommendation:
    """Delegation recommendation output"""
    recommendation_id: str
    case_summary: str
    primary_specialist: SpecialistType
    secondary_specialists: List[SpecialistType]
    urgency_level: UrgencyLevel
    time_frame: str
    rationale: str
    red_flags: List[str]
    required_information: List[str]
    preparation_instructions: List[str]
    confidence_score: float
    generated_at: datetime
    metadata: Dict[str, Any]

class DelegationManager:
    """Advanced case delegation and routing system"""
    
    def __init__(self):
        self.delegation_rules = self._load_delegation_rules()
        self.specialist_capabilities = self._load_specialist_capabilities()
        self.urgency_criteria = self._load_urgency_criteria()
        self.complexity_indicators = self._load_complexity_indicators()
    
    def _load_delegation_rules(self) -> List[DelegationRule]:
        """Load evidence-based delegation rules"""
        rules = [
            DelegationRule(
                rule_id="cardiac_emergency",
                name="Cardiac Emergency",
                description="Immediate cardiology consultation for cardiac emergencies",
                conditions=["cardiac arrest", "severe arrhythmia", "cardiogenic shock", "myocarditis"],
                symptoms=["chest pain", "irregular heartbeat", "syncope", "cyanosis", "tachycardia >180"],
                age_groups=["newborn", "infant", "toddler", "preschool", "school_age", "adolescent"],
                urgency_levels=["emergency"],
                complexity_levels=["complex", "highly_complex"],
                specialist_types=[SpecialistType.CARDIOLOGIST, SpecialistType.EMERGENCY_PHYSICIAN],
                time_frame="immediately",
                rationale="Cardiac emergencies require immediate specialist intervention",
                confidence_score=0.95,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="neurological_emergency",
                name="Neurological Emergency",
                description="Immediate neurology consultation for neurological emergencies",
                conditions=["seizure", "meningitis", "encephalitis", "stroke", "head trauma"],
                symptoms=["altered mental status", "seizure activity", "severe headache", "neck stiffness", "focal neurological deficits"],
                age_groups=["newborn", "infant", "toddler", "preschool", "school_age", "adolescent"],
                urgency_levels=["emergency"],
                complexity_levels=["complex", "highly_complex"],
                specialist_types=[SpecialistType.NEUROLOGIST, SpecialistType.EMERGENCY_PHYSICIAN],
                time_frame="immediately",
                rationale="Neurological emergencies require immediate specialist evaluation",
                confidence_score=0.95,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="neonatal_emergency",
                name="Neonatal Emergency",
                description="Immediate neonatology consultation for newborn emergencies",
                conditions=["neonatal sepsis", "respiratory distress", "necrotizing enterocolitis", "patent ductus arteriosus"],
                symptoms=["fever in <28 days", "breathing difficulty", "feeding intolerance", "lethargy", "poor feeding"],
                age_groups=["newborn"],
                urgency_levels=["emergency", "urgent"],
                complexity_levels=["complex", "highly_complex"],
                specialist_types=[SpecialistType.INTENSIVIST, SpecialistType.PEDIATRIC_SPECIALIST],
                time_frame="immediately",
                rationale="Neonates require specialized care due to immature organ systems",
                confidence_score=0.98,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="oncology_urgent",
                name="Oncology Urgent",
                description="Urgent oncology consultation for suspected malignancy",
                conditions=["leukemia", "lymphoma", "brain tumor", "neuroblastoma", "wilms tumor"],
                symptoms=["persistent unexplained fever", "weight loss", "night sweats", "bone pain", "unusual masses", "easy bruising"],
                age_groups=["infant", "toddler", "preschool", "school_age", "adolescent"],
                urgency_levels=["urgent", "semi_urgent"],
                complexity_levels=["complex", "highly_complex"],
                specialist_types=[SpecialistType.ONCOLOGIST, SpecialistType.HEMATOLOGIST],
                time_frame="within_48_hours",
                rationale="Suspected malignancy requires prompt oncology evaluation",
                confidence_score=0.90,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="endocrine_routine",
                name="Endocrine Routine",
                description="Routine endocrinology consultation for endocrine disorders",
                conditions=["diabetes", "thyroid disorder", "growth hormone deficiency", "precocious puberty", "adrenal insufficiency"],
                symptoms=["excessive thirst", "frequent urination", "weight changes", "growth concerns", "early puberty signs"],
                age_groups=["toddler", "preschool", "school_age", "adolescent"],
                urgency_levels=["routine"],
                complexity_levels=["moderate", "complex"],
                specialist_types=[SpecialistType.ENDOCRINOLOGIST],
                time_frame="within_2_weeks",
                rationale="Endocrine disorders benefit from specialist management but are rarely urgent",
                confidence_score=0.85,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="mental_health_urgent",
                name="Mental Health Urgent",
                description="Urgent mental health consultation for acute psychiatric issues",
                conditions=["depression", "anxiety", "suicidal ideation", "self-harm", "eating disorder"],
                symptoms=["persistent sadness", "anxiety attacks", "self-harm behaviors", "suicidal thoughts", "significant weight loss"],
                age_groups=["school_age", "adolescent"],
                urgency_levels=["urgent", "semi_urgent"],
                complexity_levels=["complex", "highly_complex"],
                specialist_types=[SpecialistType.PSYCHIATRIST, SpecialistType.PSYCHOLOGIST],
                time_frame="within_24_hours",
                rationale="Mental health crises require prompt intervention",
                confidence_score=0.88,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="complex_chronic",
                name="Complex Chronic Disease",
                description="Specialist consultation for complex chronic conditions",
                conditions=["cystic fibrosis", "sickle cell disease", "juvenile arthritis", "inflammatory bowel disease"],
                symptoms=["multiple organ involvement", "frequent hospitalizations", "complex medication regimens", "poor growth"],
                age_groups=["infant", "toddler", "preschool", "school_age", "adolescent"],
                urgency_levels=["routine", "semi_urgent"],
                complexity_levels=["highly_complex"],
                specialist_types=[SpecialistType.PEDIATRIC_SPECIALIST],
                time_frame="within_1_week",
                rationale="Complex chronic conditions require multidisciplinary specialist care",
                confidence_score=0.92,
                is_active=True
            ),
            
            DelegationRule(
                rule_id="surgical_consultation",
                name="Surgical Consultation",
                description="Surgical consultation for conditions requiring potential surgery",
                conditions=["appendicitis", "intussusception", "hernia", "fracture", "tumor"],
                symptoms=["abdominal pain", "vomiting", "visible mass", "deformity", "limited mobility"],
                age_groups=["infant", "toddler", "preschool", "school_age", "adolescent"],
                urgency_levels=["urgent", "semi_urgent"],
                complexity_levels=["moderate", "complex"],
                specialist_types=[SpecialistType.SURGEON],
                time_frame="within_24_hours",
                rationale="Surgical conditions require prompt evaluation for intervention timing",
                confidence_score=0.90,
                is_active=True
            )
        ]
        
        return rules
    
    def _load_specialist_capabilities(self) -> Dict[SpecialistType, List[str]]:
        """Load specialist capabilities and expertise areas"""
        return {
            SpecialistType.PEDIATRICIAN: [
                "general_pediatrics", "well_child_care", "routine_infections", "growth_monitoring",
                "developmental_screening", "immunizations", "common_childhood_illnesses"
            ],
            SpecialistType.PEDIATRIC_SPECIALIST: [
                "complex_pediatric_conditions", "rare_diseases", "multidisciplinary_care",
                "chronic_disease_management", "specialized_diagnostics"
            ],
            SpecialistType.EMERGENCY_PHYSICIAN: [
                "acute_medical_emergencies", "trauma", "resuscitation", "acute_stabilization",
                "emergency_procedures", "critical_care_initial_management"
            ],
            SpecialistType.INTENSIVIST: [
                "critical_care", "mechanical_ventilation", "hemodynamic_monitoring", "multi_organ_support",
                "sepsis_management", "post_surgical_care"
            ],
            SpecialistType.CARDIOLOGIST: [
                "congenital_heart_disease", "arrhythmias", "heart_failure", "cardiac_catheterization",
                "echocardiography", "electrophysiology"
            ],
            SpecialistType.NEUROLOGIST: [
                "seizures", "epilepsy", "neuromuscular_disorders", "neurodevelopmental_disorders",
                "headaches", "movement_disorders", "neurogenetic_conditions"
            ],
            SpecialistType.ONCOLOGIST: [
                "leukemia", "lymphoma", "solid_tumors", "chemotherapy", "radiation_therapy",
                "stem_cell_transplant", "late_effects_of_treatment"
            ],
            SpecialistType.ENDOCRINOLOGIST: [
                "diabetes", "thyroid_disorders", "growth_disorders", "pubertal_disorders",
                "adrenal_disorders", "calcium_metabolism", "pituitary_disorders"
            ],
            SpecialistType.SURGEON: [
                "general_surgery", "minimally_invasive_surgery", "trauma_surgery", "oncologic_surgery",
                "congenital_anomaly_repair", "transplant_surgery"
            ],
            SpecialistType.PSYCHIATRIST: [
                "mood_disorders", "anxiety_disorders", "psychotic_disorders", "eating_disorders",
                "substance_abuse", "crisis_intervention", "medication_management"
            ]
        }
    
    def _load_urgency_criteria(self) -> Dict[UrgencyLevel, List[str]]:
        """Load criteria for determining case urgency"""
        return {
            UrgencyLevel.EMERGENCY: [
                "life_threatening", "airway_compromise", "severe_respiratory_distress", 
                "cardiac_arrest", "severe_trauma", "uncontrolled_bleeding", "septic_shock",
                "status_epilepticus", "anaphylaxis"
            ],
            UrgencyLevel.URGENT: [
                "moderate_respiratory_distress", "dehydration", "febrile_seizure", "severe_pain",
                "altered_mental_status", "high_fever_infant", "suspected_sepsis", "fracture",
                "acute_abdominal_pain", "suspected_appendicitis"
            ],
            UrgencyLevel.SEMI_URGENT: [
                "persistent_fever", "moderate_pain", "vomiting_diarrhea", "ear_infection",
                "urinary_tract_infection", "skin_infection", "asthma_exacerbation_mild",
                "allergic_reaction_mild", "minor_trauma"
            ],
            UrgencyLevel.ROUTINE: [
                "well_child_visit", "routine_immunization", "growth_monitoring", "developmental_screening",
                "chronic_condition_follow_up", "medication_refill", "minor_skin_conditions",
                "behavioral_concerns", "sleep_issues"
            ]
        }
    
    def _load_complexity_indicators(self) -> Dict[ComplexityLevel, List[str]]:
        """Load indicators for determining case complexity"""
        return {
            ComplexityLevel.SIMPLE: [
                "single_organ_system", "well_defined_diagnosis", "standard_treatment_protocol",
                "good_response_to_initial_treatment", "minimal_diagnostic_uncertainty"
            ],
            ComplexityLevel.MODERATE: [
                "multiple_symptoms", "uncertain_diagnosis", "requires_specialized_testing",
                "chronic_condition_acute_exacerbation", "multiple_treatment_options",
                "requires_coordinated_care"
            ],
            ComplexityLevel.COMPLEX: [
                "multiple_organ_systems", "rare_condition", "requires_multidisciplinary_care",
                "significant_diagnostic_uncertainty", "treatment_resistant",
                "multiple_comorbidities", "requires_specialized_procedures"
            ],
            ComplexityLevel.HIGHLY_COMPLEX: [
                "life_threatening_condition", "requires_intensive_care", "experimental_treatment",
                "multiple_specialists_required", "significant_ethical_considerations",
                "requires_major_surgery", "terminal_condition", "rare_genetic_disorder"
            ]
        }
    
    def assess_case_urgency(self, diagnosis: str, symptoms: List[str], age_group: str, red_flags: List[str]) -> UrgencyLevel:
        """Assess the urgency level of a case"""
        # Check for emergency criteria first
        for emergency_criterion in self.urgency_criteria[UrgencyLevel.EMERGENCY]:
            if (emergency_criterion in diagnosis.lower() or 
                any(emergency_criterion in symptom.lower() for symptom in symptoms) or
                any(emergency_criterion in red_flag.lower() for red_flag in red_flags)):
                return UrgencyLevel.EMERGENCY
        
        # Check for urgent criteria
        for urgent_criterion in self.urgency_criteria[UrgencyLevel.URGENT]:
            if (urgent_criterion in diagnosis.lower() or 
                any(urgent_criterion in symptom.lower() for symptom in symptoms) or
                any(urgent_criterion in red_flag.lower() for red_flag in red_flags)):
                return UrgencyLevel.URGENT
        
        # Check for semi-urgent criteria
        for semi_urgent_criterion in self.urgency_criteria[UrgencyLevel.SEMI_URGENT]:
            if (semi_urgent_criterion in diagnosis.lower() or 
                any(semi_urgent_criterion in symptom.lower() for symptom in symptoms)):
                return UrgencyLevel.SEMI_URGENT
        
        # Default to routine
        return UrgencyLevel.ROUTINE
    
    def assess_case_complexity(self, diagnosis: str, symptoms: List[str], age_group: str, 
                              comorbidities: List[str] = None) -> ComplexityLevel:
        """Assess the complexity level of a case"""
        complexity_score = 0
        
        # Check for highly complex indicators
        for complex_indicator in self.complexity_indicators[ComplexityLevel.HIGHLY_COMPLEX]:
            if (complex_indicator in diagnosis.lower() or 
                any(complex_indicator in symptom.lower() for symptom in symptoms)):
                return ComplexityLevel.HIGHLY_COMPLEX
        
        # Check for complex indicators
        for complex_indicator in self.complexity_indicators[ComplexityLevel.COMPLEX]:
            if (complex_indicator in diagnosis.lower() or 
                any(complex_indicator in symptom.lower() for symptom in symptoms)):
                complexity_score += 3
        
        # Check for moderate complexity indicators
        for moderate_indicator in self.complexity_indicators[ComplexityLevel.MODERATE]:
            if (moderate_indicator in diagnosis.lower() or 
                any(moderate_indicator in symptom.lower() for symptom in symptoms)):
                complexity_score += 2
        
        # Age-related complexity (neonates and complex adolescents)
        if age_group == "newborn":
            complexity_score += 2
        
        # Comorbidities add complexity
        if comorbidities:
            complexity_score += len(comorbidities)
        
        # Determine complexity level based on score
        if complexity_score >= 5:
            return ComplexityLevel.COMPLEX
        elif complexity_score >= 2:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE
    
    def find_matching_rules(self, diagnosis: str, symptoms: List[str], age_group: str, 
                          urgency_level: UrgencyLevel, complexity_level: ComplexityLevel) -> List[DelegationRule]:
        """Find matching delegation rules"""
        matching_rules = []
        
        for rule in self.delegation_rules:
            if not rule.is_active:
                continue
            
            # Check age group match
            if age_group.lower() not in [ag.lower() for ag in rule.age_groups]:
                continue
            
            # Check urgency level match
            if urgency_level.value not in rule.urgency_levels:
                continue
            
            # Check complexity level match
            if complexity_level.value not in rule.complexity_levels:
                continue
            
            # Check condition match
            condition_match = False
            for condition in rule.conditions:
                if condition.lower() in diagnosis.lower():
                    condition_match = True
                    break
            
            # Check symptom match
            symptom_match = False
            for rule_symptom in rule.symptoms:
                for patient_symptom in symptoms:
                    if rule_symptom.lower() in patient_symptom.lower():
                        symptom_match = True
                        break
                if symptom_match:
                    break
            
            # Match if either condition or symptoms match
            if condition_match or symptom_match:
                matching_rules.append(rule)
        
        return matching_rules
    
    def generate_delegation_recommendation(self, diagnosis: str, symptoms: List[str], age_group: str,
                                         red_flags: List[str] = None, comorbidities: List[str] = None,
                                         patient_context: Dict[str, Any] = None) -> DelegationRecommendation:
        """Generate delegation recommendation"""
        logger.info("Generating delegation recommendation", 
                   diagnosis=diagnosis, 
                   age_group=age_group,
                   symptoms_count=len(symptoms))
        
        # Set defaults
        red_flags = red_flags or []
        comorbidities = comorbidities or []
        
        # Assess case characteristics
        urgency_level = self.assess_case_urgency(diagnosis, symptoms, age_group, red_flags)
        complexity_level = self.assess_case_complexity(diagnosis, symptoms, age_group, comorbidities)
        
        # Find matching rules
        matching_rules = self.find_matching_rules(diagnosis, symptoms, age_group, urgency_level, complexity_level)
        
        if matching_rules:
            # Use the highest confidence matching rule
            best_rule = max(matching_rules, key=lambda r: r.confidence_score)
            primary_specialist = best_rule.specialist_types[0]
            secondary_specialists = best_rule.specialist_types[1:] if len(best_rule.specialist_types) > 1 else []
            time_frame = best_rule.time_frame
            rationale = best_rule.rationale
            confidence_score = best_rule.confidence_score
        else:
            # Default to pediatrician for simple cases, pediatric specialist for complex cases
            if complexity_level == ComplexityLevel.SIMPLE:
                primary_specialist = SpecialistType.PEDIATRICIAN
                secondary_specialists = []
                time_frame = "within_1_week"
                rationale = "Simple condition appropriate for general pediatric management"
                confidence_score = 0.8
            else:
                primary_specialist = SpecialistType.PEDIATRIC_SPECIALIST
                secondary_specialists = []
                time_frame = "within_48_hours"
                rationale = "Complex condition requiring specialist evaluation"
                confidence_score = 0.7
        
        # Generate additional recommendations
        red_flag_criteria = self._generate_red_flags(urgency_level)
        required_info = self._generate_required_information(primary_specialist, diagnosis)
        preparation_instructions = self._generate_preparation_instructions(primary_specialist, urgency_level)
        
        # Create case summary
        case_summary = self._generate_case_summary(diagnosis, symptoms, age_group, urgency_level, complexity_level)
        
        recommendation = DelegationRecommendation(
            recommendation_id=f"del_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            case_summary=case_summary,
            primary_specialist=primary_specialist,
            secondary_specialists=secondary_specialists,
            urgency_level=urgency_level,
            time_frame=time_frame,
            rationale=rationale,
            red_flags=red_flag_criteria,
            required_information=required_info,
            preparation_instructions=preparation_instructions,
            confidence_score=confidence_score,
            generated_at=datetime.utcnow(),
            metadata={
                "diagnosis": diagnosis,
                "symptoms": symptoms,
                "age_group": age_group,
                "red_flags": red_flags,
                "comorbidities": comorbidities,
                "matching_rules_count": len(matching_rules),
                "patient_context": patient_context or {}
            }
        )
        
        logger.info("Delegation recommendation generated successfully",
                   primary_specialist=primary_specialist.value,
                   urgency_level=urgency_level.value,
                   confidence_score=confidence_score)
        
        return recommendation
    
    def _generate_red_flags(self, urgency_level: UrgencyLevel) -> List[str]:
        """Generate red flags for the recommendation"""
        red_flags = []
        
        if urgency_level == UrgencyLevel.EMERGENCY:
            red_flags.extend([
                "Seek immediate medical attention if condition worsens",
                "Call 911 for severe symptoms",
                "Do not delay seeking emergency care"
            ])
        elif urgency_level == UrgencyLevel.URGENT:
            red_flags.extend([
                "Seek medical attention within 24 hours if symptoms persist",
                "Monitor for signs of deterioration",
                "Contact healthcare provider if new symptoms develop"
            ])
        else:
            red_flags.extend([
                "Monitor symptoms and seek care if condition worsens",
                "Follow up as recommended",
                "Contact healthcare provider with concerns"
            ])
        
        return red_flags
    
    def _generate_required_information(self, specialist: SpecialistType, diagnosis: str) -> List[str]:
        """Generate required information for specialist consultation"""
        required_info = [
            "Complete medical history",
            "Current medications",
            "Previous treatments and responses",
            "Family history relevant to condition"
        ]
        
        # Specialist-specific requirements
        if specialist == SpecialistType.CARDIOLOGIST:
            required_info.extend([
                "Previous ECGs or cardiac imaging",
                "Exercise tolerance history",
                "Family history of cardiac conditions"
            ])
        elif specialist == SpecialistType.NEUROLOGIST:
            required_info.extend([
                "Detailed seizure history if applicable",
                "Developmental milestones",
                "Previous neurological imaging"
            ])
        elif specialist == SpecialistType.ENDOCRINOLOGIST:
            required_info.extend([
                "Growth charts",
                "Pubertal development history",
                "Previous hormone levels"
            ])
        
        return required_info
    
    def _generate_preparation_instructions(self, specialist: SpecialistType, urgency_level: UrgencyLevel) -> List[str]:
        """Generate preparation instructions for specialist visit"""
        instructions = []
        
        if urgency_level == UrgencyLevel.EMERGENCY:
            instructions.extend([
                "Go to nearest emergency room immediately",
                "Bring all current medications",
                "Have someone drive you if possible",
                "Bring insurance information"
            ])
        else:
            instructions.extend([
                "Schedule appointment as recommended",
                "Bring all current medications",
                "Bring insurance card and ID",
                "Arrive 15 minutes early for paperwork"
            ])
        
        # Specialist-specific preparation
        if specialist == SpecialistType.CARDIOLOGIST:
            instructions.append("Wear comfortable clothing for possible ECG")
        elif specialist == SpecialistType.NEUROLOGIST:
            instructions.append("Bring someone who has observed symptoms if possible")
        
        return instructions
    
    def _generate_case_summary(self, diagnosis: str, symptoms: List[str], age_group: str,
                             urgency_level: UrgencyLevel, complexity_level: ComplexityLevel) -> str:
        """Generate concise case summary"""
        summary_parts = [
            f"{age_group.title()} patient with {diagnosis}",
            f"Presenting symptoms: {', '.join(symptoms[:3])}{'...' if len(symptoms) > 3 else ''}",
            f"Urgency: {urgency_level.value.title()}",
            f"Complexity: {complexity_level.value.title()}"
        ]
        
        return "; ".join(summary_parts)

class DelegationValidator:
    """Validates delegation recommendations for safety and appropriateness"""
    
    def __init__(self):
        self.emergency_conditions = [
            "cardiac arrest", "respiratory failure", "septic shock", "anaphylaxis",
            "severe trauma", "status epilepticus", "coma"
        ]
        
        self.time_frame_requirements = {
            "immediately": 0,
            "within_2_hours": 2,
            "within_24_hours": 24,
            "within_48_hours": 48,
            "within_1_week": 168,
            "within_2_weeks": 336
        }
    
    def validate_emergency_routing(self, recommendation: DelegationRecommendation) -> List[str]:
        """Validate that emergencies are properly routed"""
        warnings = []
        
        # Check if emergency cases are routed to appropriate specialists
        if recommendation.urgency_level == UrgencyLevel.EMERGENCY:
            emergency_specialists = [SpecialistType.EMERGENCY_PHYSICIAN, SpecialistType.INTENSIVIST]
            
            if recommendation.primary_specialist not in emergency_specialists:
                # Check if any secondary specialists are emergency-appropriate
                has_emergency_specialist = any(spec in emergency_specialists for spec in recommendation.secondary_specialists)
                
                if not has_emergency_specialist:
                    warnings.append("Emergency case not routed to emergency-appropriate specialist")
            
            if recommendation.time_frame != "immediately":
                warnings.append("Emergency case should have immediate time frame")
        
        return warnings
    
    def validate_time_frame_appropriateness(self, recommendation: DelegationRecommendation) -> List[str]:
        """Validate that time frames are appropriate for urgency levels"""
        warnings = []
        
        urgency_time_requirements = {
            UrgencyLevel.EMERGENCY: ["immediately"],
            UrgencyLevel.URGENT: ["immediately", "within_2_hours", "within_24_hours"],
            UrgencyLevel.SEMI_URGENT: ["within_24_hours", "within_48_hours"],
            UrgencyLevel.ROUTINE: ["within_1_week", "within_2_weeks"]
        }
        
        allowed_timeframes = urgency_time_requirements.get(recommendation.urgency_level, [])
        
        if recommendation.time_frame not in allowed_timeframes:
            warnings.append(f"Time frame '{recommendation.time_frame}' not appropriate for {recommendation.urgency_level.value} urgency")
        
        return warnings
    
    def validate_specialist_availability(self, recommendation: DelegationRecommendation) -> List[str]:
        """Validate that recommended specialists are available for the condition"""
        warnings = []
        
        # This would ideally check actual specialist availability
        # For now, we'll check if the specialist type is appropriate for pediatric cases
        pediatric_inappropriate = [
            # This would be populated with specialists not appropriate for pediatric patients
        ]
        
        if recommendation.primary_specialist in pediatric_inappropriate:
            warnings.append(f"Specialist {recommendation.primary_specialist.value} may not be appropriate for pediatric patients")
        
        return warnings
    
    def validate(self, recommendation: DelegationRecommendation) -> Dict[str, Any]:
        """Comprehensive validation"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Emergency routing validation
        emergency_warnings = self.validate_emergency_routing(recommendation)
        validation_result["warnings"].extend(emergency_warnings)
        
        # Time frame validation
        timeframe_warnings = self.validate_time_frame_appropriateness(recommendation)
        validation_result["warnings"].extend(timeframe_warnings)
        
        # Specialist availability validation
        availability_warnings = self.validate_specialist_availability(recommendation)
        validation_result["warnings"].extend(availability_warnings)
        
        # Check confidence score
        if recommendation.confidence_score < 0.5:
            validation_result["warnings"].append("Low confidence score - review recommendation carefully")
        
        # Generate recommendations
        if emergency_warnings:
            validation_result["recommendations"].append("Ensure emergency cases are routed to appropriate emergency care")
        
        if timeframe_warnings:
            validation_result["recommendations"].append("Review time frame appropriateness for urgency level")
        
        return validation_result