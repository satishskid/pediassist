"""
Treatment protocol generation engine
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
from datetime import datetime, timedelta
from decimal import Decimal

# Import TreatmentLevel from the main treatment_generator module
from ..treatment_generator import TreatmentLevel

logger = structlog.get_logger(__name__)

class TreatmentPriority(Enum):
    """Treatment priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TreatmentCategory(Enum):
    """Treatment categories"""
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    LIFESTYLE = "lifestyle"
    MONITORING = "monitoring"
    REFERRAL = "referral"
    EDUCATION = "education"

@dataclass
class MedicationDose:
    """Medication dosing information"""
    medication_name: str
    dose: str
    frequency: str
    duration: str
    route: str
    age_range: str
    weight_range: Optional[str]
    indications: List[str]
    contraindications: List[str]
    side_effects: List[str]
    monitoring_requirements: List[str]
    formulation: str
    brand_names: List[str]

@dataclass
class TreatmentStep:
    """Individual treatment step"""
    step_number: int
    title: str
    description: str
    priority: TreatmentPriority
    category: TreatmentCategory
    duration: Optional[str]
    monitoring: List[str]
    follow_up: Optional[str]
    conditions: List[str]  # Conditions under which this step applies
    evidence_level: str
    clinical_notes: str

@dataclass
class TreatmentProtocol:
    """Complete treatment protocol"""
    diagnosis: str
    plan_type: TreatmentLevel
    priority: TreatmentPriority
    steps: List[TreatmentStep]
    medications: List[Dict[str, Any]]
    monitoring_parameters: List[str]
    follow_up_instructions: str
    patient_education: str
    red_flags: List[str]
    duration_estimate: str
    cost_estimate: Optional[float] = None
    created_at: datetime = None
    # Keep original fields for backward compatibility
    age_group: str = ""
    urgency_level: str = ""
    primary_treatments: List[TreatmentStep] = None
    alternative_treatments: List[TreatmentStep] = None
    monitoring_plan: List[str] = None
    follow_up_schedule: List[str] = None
    red_flag_criteria: List[str] = None
    referral_criteria: List[str] = None
    evidence_summary: str = ""
    last_updated: datetime = None
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.primary_treatments is None:
            self.primary_treatments = []
        if self.alternative_treatments is None:
            self.alternative_treatments = []
        if self.monitoring_plan is None:
            self.monitoring_plan = []
        if self.follow_up_schedule is None:
            self.follow_up_schedule = []
        if self.red_flag_criteria is None:
            self.red_flag_criteria = []
        if self.referral_criteria is None:
            self.referral_criteria = []
        if self.metadata is None:
            self.metadata = {}

class TreatmentGenerator:
    """Advanced treatment protocol generator"""
    
    def __init__(self):
        self.medication_database = self._load_medication_database()
        self.protocol_templates = self._load_protocol_templates()
        self.evidence_database = self._load_evidence_database()
    
    def _load_medication_database(self) -> Dict[str, Any]:
        """Load medication database with pediatric dosing"""
        return {
            "acetaminophen": {
                "class": "analgesic/antipyretic",
                "dosing": {
                    "infant": {"dose": "10-15 mg/kg", "frequency": "q6-8h", "max_daily": "60 mg/kg"},
                    "child": {"dose": "10-15 mg/kg", "frequency": "q4-6h", "max_daily": "75 mg/kg"},
                    "adolescent": {"dose": "325-650 mg", "frequency": "q4-6h", "max_daily": "4g"}
                },
                "contraindications": ["severe hepatic impairment", "G6PD deficiency"],
                "side_effects": ["hepatotoxicity (rare)", "rash"],
                "monitoring": ["liver function if prolonged use"]
            },
            "ibuprofen": {
                "class": "NSAID",
                "dosing": {
                    "infant": {"dose": "5-10 mg/kg", "frequency": "q6-8h", "max_daily": "40 mg/kg"},
                    "child": {"dose": "5-10 mg/kg", "frequency": "q6-8h", "max_daily": "40 mg/kg"},
                    "adolescent": {"dose": "200-400 mg", "frequency": "q6-8h", "max_daily": "1200 mg"}
                },
                "contraindications": ["active bleeding", "renal disease", "aspirin allergy"],
                "side_effects": ["GI upset", "bleeding", "renal effects"],
                "monitoring": ["renal function if prolonged use"]
            },
            "amoxicillin": {
                "class": "antibiotic",
                "dosing": {
                    "infant": {"dose": "20-40 mg/kg/day", "frequency": "bid", "duration": "7-10 days"},
                    "child": {"dose": "20-50 mg/kg/day", "frequency": "bid", "duration": "7-10 days"},
                    "adolescent": {"dose": "250-500 mg", "frequency": "bid", "duration": "7-10 days"}
                },
                "contraindications": ["penicillin allergy"],
                "side_effects": ["diarrhea", "rash", "allergic reaction"],
                "monitoring": ["clinical response after 48-72 hours"]
            }
        }
    
    def _load_protocol_templates(self) -> Dict[str, Any]:
        """Load evidence-based protocol templates"""
        return {
            "respiratory_infection": {
                "immediate": [
                    {
                        "step": "Assess airway and breathing",
                        "priority": "immediate",
                        "category": "monitoring",
                        "description": "Evaluate respiratory rate, work of breathing, oxygen saturation"
                    }
                ],
                "high": [
                    {
                        "step": "Antibiotic therapy if indicated",
                        "priority": "high",
                        "category": "medication",
                        "description": "Consider antibiotics for bacterial infections"
                    }
                ],
                "medium": [
                    {
                        "step": "Supportive care",
                        "priority": "medium",
                        "category": "lifestyle",
                        "description": "Hydration, rest, humidified air"
                    }
                ]
            },
            "fever_management": {
                "immediate": [
                    {
                        "step": "Assess for serious bacterial infection",
                        "priority": "immediate",
                        "category": "monitoring",
                        "description": "Evaluate age, temperature, clinical appearance"
                    }
                ],
                "high": [
                    {
                        "step": "Antipyretic therapy",
                        "priority": "high",
                        "category": "medication",
                        "description": "Acetaminophen 10-15 mg/kg q4-6h PRN"
                    }
                ]
            }
        }
    
    def _load_evidence_database(self) -> Dict[str, str]:
        """Load evidence levels and sources"""
        return {
            "immediate_assessment": "AAP Guidelines 2023",
            "antibiotic_therapy": "IDSA Guidelines 2021",
            "fever_management": "AAP Clinical Practice Guidelines 2021",
            "pain_management": "WHO Guidelines on Pain Management in Children 2020"
        }
    
    def generate_medication_doses(self, diagnosis: str, age_group: str, weight_kg: Optional[float] = None) -> List[MedicationDose]:
        """Generate age-appropriate medication dosing"""
        medications = []
        
        # Determine which medications are appropriate for the diagnosis
        if "infection" in diagnosis.lower() or "fever" in diagnosis.lower():
            # Acetaminophen for fever/pain
            acetaminophen = self._create_medication_dose(
                "acetaminophen", age_group, weight_kg,
                indications=["fever", "pain"],
                contraindications=["severe hepatic impairment"],
                side_effects=["hepatotoxicity (rare)"]
            )
            medications.append(acetaminophen)
            
            # Ibuprofen for fever/pain (if >6 months)
            if age_group not in ["newborn", "infant"]:
                ibuprofen = self._create_medication_dose(
                    "ibuprofen", age_group, weight_kg,
                    indications=["fever", "pain", "inflammation"],
                    contraindications=["active bleeding", "renal disease"],
                    side_effects=["GI upset", "bleeding"]
                )
                medications.append(ibuprofen)
        
        if "bacterial" in diagnosis.lower() or "pneumonia" in diagnosis.lower():
            # Amoxicillin for bacterial infections
            amoxicillin = self._create_medication_dose(
                "amoxicillin", age_group, weight_kg,
                indications=["bacterial infection", "pneumonia", "otitis media"],
                contraindications=["penicillin allergy"],
                side_effects=["diarrhea", "rash", "allergic reaction"]
            )
            medications.append(amoxicillin)
        
        return medications
    
    def _create_medication_dose(self, medication_name: str, age_group: str, weight_kg: Optional[float], 
                              indications: List[str], contraindications: List[str], side_effects: List[str]) -> MedicationDose:
        """Create medication dose object"""
        med_info = self.medication_database.get(medication_name, {})
        dosing_info = med_info.get("dosing", {}).get(age_group, {})
        
        # Calculate specific dose if weight provided
        if weight_kg and "dose" in dosing_info and "mg/kg" in dosing_info["dose"]:
            dose_per_kg = float(dosing_info["dose"].split("-")[0].strip().split()[0])
            calculated_dose = f"{dose_per_kg * weight_kg:.0f} mg"
        else:
            calculated_dose = dosing_info.get("dose", "See dosing guidelines")
        
        return MedicationDose(
            medication_name=medication_name,
            dose=calculated_dose,
            frequency=dosing_info.get("frequency", "As directed"),
            duration=dosing_info.get("duration", "As clinically indicated"),
            route="oral",
            age_range=age_group,
            weight_range=f"{weight_kg} kg" if weight_kg else "Weight-based dosing",
            indications=indications,
            contraindications=contraindications + med_info.get("contraindications", []),
            side_effects=side_effects + med_info.get("side_effects", []),
            monitoring_requirements=med_info.get("monitoring", []),
            formulation="liquid/suspension" if age_group in ["infant", "toddler"] else "tablet/capsule",
            brand_names=self._get_brand_names(medication_name)
        )
    
    def _get_brand_names(self, medication_name: str) -> List[str]:
        """Get brand names for medications"""
        brand_names = {
            "acetaminophen": ["Tylenol", "Panadol"],
            "ibuprofen": ["Advil", "Motrin"],
            "amoxicillin": ["Amoxil", "Trimox"]
        }
        return brand_names.get(medication_name, [])
    
    def generate_treatment_steps(self, diagnosis: str, urgency_level: str, age_group: str) -> List[TreatmentStep]:
        """Generate treatment steps based on diagnosis and urgency"""
        steps = []
        step_number = 1
        
        # Determine protocol category
        if "respiratory" in diagnosis.lower():
            protocol_category = "respiratory_infection"
        elif "fever" in diagnosis.lower():
            protocol_category = "fever_management"
        else:
            protocol_category = "general"
        
        protocol = self.protocol_templates.get(protocol_category, {})
        
        # Generate steps based on urgency
        if urgency_level == "emergency":
            # Immediate priority steps
            for step_data in protocol.get("immediate", []):
                steps.append(self._create_treatment_step(step_number, step_data))
                step_number += 1
        
        if urgency_level in ["emergency", "urgent"]:
            # High priority steps
            for step_data in protocol.get("high", []):
                steps.append(self._create_treatment_step(step_number, step_data))
                step_number += 1
        
        # Always include medium priority steps
        for step_data in protocol.get("medium", []):
            steps.append(self._create_treatment_step(step_number, step_data))
            step_number += 1
        
        return steps
    
    def _create_treatment_step(self, step_number: int, step_data: Dict[str, Any]) -> TreatmentStep:
        """Create treatment step object"""
        return TreatmentStep(
            step_number=step_number,
            title=step_data.get("step", f"Step {step_number}"),
            description=step_data.get("description", ""),
            priority=TreatmentPriority(step_data.get("priority", "medium")),
            category=TreatmentCategory(step_data.get("category", "monitoring")),
            duration=None,
            monitoring=[],
            follow_up=None,
            conditions=[],
            evidence_level=self._get_evidence_level(step_data.get("step", "")),
            clinical_notes=""
        )
    
    def _get_evidence_level(self, step_title: str) -> str:
        """Get evidence level for treatment step"""
        if "assess" in step_title.lower():
            return "AAP Guidelines 2023"
        elif "antibiotic" in step_title.lower():
            return "IDSA Guidelines 2021"
        else:
            return "Clinical Practice Guidelines"
    
    def generate_monitoring_plan(self, diagnosis: str, urgency_level: str) -> List[str]:
        """Generate monitoring plan"""
        monitoring = []
        
        if urgency_level == "emergency":
            monitoring.extend([
                "Continuous vital signs monitoring",
                "Neurological assessments q15min",
                "Fluid balance monitoring"
            ])
        elif urgency_level == "urgent":
            monitoring.extend([
                "Vital signs q4h",
                "Clinical reassessment in 24 hours",
                "Symptom progression monitoring"
            ])
        else:
            monitoring.extend([
                "Vital signs as clinically indicated",
                "Follow-up in 1-2 weeks",
                "Patient education on warning signs"
            ])
        
        # Diagnosis-specific monitoring
        if "respiratory" in diagnosis.lower():
            monitoring.append("Respiratory rate and effort assessment")
            monitoring.append("Oxygen saturation monitoring")
        
        if "fever" in diagnosis.lower():
            monitoring.append("Temperature monitoring")
            monitoring.append("Hydration status assessment")
        
        return monitoring
    
    def generate_follow_up_schedule(self, diagnosis: str, urgency_level: str) -> List[str]:
        """Generate follow-up schedule"""
        follow_up = []
        
        if urgency_level == "emergency":
            follow_up.extend([
                "24-48 hours: Clinical reassessment",
                "1 week: Symptom resolution check"
            ])
        elif urgency_level == "urgent":
            follow_up.extend([
                "48-72 hours: Phone follow-up",
                "1-2 weeks: Clinical visit if needed"
            ])
        else:
            follow_up.extend([
                "1-2 weeks: Routine follow-up",
                "As needed for persistent symptoms"
            ])
        
        return follow_up
    
    def generate_red_flags(self, diagnosis: str, age_group: str) -> List[str]:
        """Generate red flag criteria"""
        red_flags = [
            "Worsening symptoms despite treatment",
            "New fever > 38.5°C",
            "Difficulty breathing or chest pain",
            "Altered mental status or confusion",
            "Inability to tolerate oral intake"
        ]
        
        # Age-specific red flags
        if age_group in ["newborn", "infant"]:
            red_flags.extend([
                "Temperature > 38°C in infant < 3 months",
                "Poor feeding or decreased urine output",
                "Persistent crying or irritability"
            ])
        
        return red_flags
    
    def generate_referral_criteria(self, diagnosis: str, urgency_level: str) -> List[str]:
        """Generate referral criteria"""
        referral_criteria = []
        
        if urgency_level == "emergency":
            referral_criteria.extend([
                "Immediate emergency department referral",
                "Critical care consultation if unstable"
            ])
        elif urgency_level == "urgent":
            referral_criteria.extend([
                "Pediatric specialist consultation within 24 hours",
                "Consider hospital admission if severe"
            ])
        else:
            referral_criteria.extend([
                "Specialist referral if symptoms persist > 1 week",
                "Consider second opinion if no improvement"
            ])
        
        return referral_criteria
    
    def generate_patient_education(self, diagnosis: str, age_group: str) -> List[str]:
        """Generate patient education points"""
        education = []
        
        # General education
        education.extend([
            "Complete full course of prescribed medications",
            "Return for follow-up as scheduled",
            "Contact provider if symptoms worsen"
        ])
        
        # Diagnosis-specific education
        if "infection" in diagnosis.lower():
            education.extend([
                "Practice good hand hygiene",
                "Avoid sharing personal items",
                "Stay home until fever-free for 24 hours"
            ])
        
        if "fever" in diagnosis.lower():
            education.extend([
                "Monitor temperature regularly",
                "Ensure adequate fluid intake",
                "Use antipyretics as directed"
            ])
        
        # Age-appropriate education
        if age_group in ["toddler", "preschool", "school_age"]:
            education.append("Explain procedure/treatment in age-appropriate language")
        
        return education
    
    def generate_protocol(self, diagnosis: str, age_group: str, urgency_level: str, 
                         weight_kg: Optional[float] = None, patient_context: Optional[Dict[str, Any]] = None) -> TreatmentProtocol:
        """Generate complete treatment protocol"""
        logger.info("Generating treatment protocol", 
                   diagnosis=diagnosis, 
                   age_group=age_group, 
                   urgency_level=urgency_level)

        # Generate protocol components
        medications = self.generate_medication_doses(diagnosis, age_group, weight_kg)
        primary_treatments = self.generate_treatment_steps(diagnosis, urgency_level, age_group)
        alternative_treatments = []  # Could be expanded based on evidence
        monitoring_plan = self.generate_monitoring_plan(diagnosis, urgency_level)
        follow_up_schedule = self.generate_follow_up_schedule(diagnosis, urgency_level)
        red_flag_criteria = self.generate_red_flags(diagnosis, age_group)
        referral_criteria = self.generate_referral_criteria(diagnosis, urgency_level)
        patient_education = self.generate_patient_education(diagnosis, age_group)

        # Calculate confidence score based on available evidence
        confidence_score = self._calculate_confidence_score(diagnosis, age_group, urgency_level)
        
        # Map urgency level to TreatmentPriority
        priority_map = {
            "immediate": TreatmentPriority.CRITICAL,
            "high": TreatmentPriority.HIGH,
            "medium": TreatmentPriority.MEDIUM,
            "low": TreatmentPriority.LOW
        }
        priority = priority_map.get(urgency_level, TreatmentPriority.MEDIUM)
        
        # Map complexity to TreatmentLevel (default to basic for now)
        plan_type = TreatmentLevel.BASIC  # Could be enhanced based on complexity

        # Convert medications to the expected format (List[Dict[str, Any]])
        medication_dicts = []
        for med in medications:
            medication_dicts.append({
                "name": med.medication_name,
                "dosing": f"{med.dose} {med.frequency}",
                "monitoring": med.monitoring_requirements,
                "route": med.route,
                "duration": med.duration
            })

        # Convert patient education list to string
        education_text = "\n".join(patient_education) if patient_education else ""
        
        # Convert follow up schedule to instructions string
        follow_up_text = "\n".join(follow_up_schedule) if follow_up_schedule else ""

        protocol = TreatmentProtocol(
            diagnosis=diagnosis,
            plan_type=plan_type,
            priority=priority,
            steps=primary_treatments,
            medications=medication_dicts,
            monitoring_parameters=monitoring_plan,
            follow_up_instructions=follow_up_text,
            patient_education=education_text,
            red_flags=red_flag_criteria,
            duration_estimate=follow_up_text,  # Could be enhanced
            cost_estimate=None,  # Could be calculated
            created_at=datetime.utcnow(),
            # Keep original fields for backward compatibility
            age_group=age_group,
            urgency_level=urgency_level,
            primary_treatments=primary_treatments,
            alternative_treatments=alternative_treatments,
            monitoring_plan=monitoring_plan,
            follow_up_schedule=follow_up_schedule,
            red_flag_criteria=red_flag_criteria,
            referral_criteria=referral_criteria,
            evidence_summary=self._generate_evidence_summary(diagnosis),
            last_updated=datetime.utcnow(),
            confidence_score=confidence_score,
            metadata={
                "generated_timestamp": datetime.utcnow().isoformat(),
                "patient_context": patient_context or {},
                "weight_used": weight_kg,
                "evidence_sources": list(self.evidence_database.values())
            }
        )

        logger.info("Treatment protocol generated successfully",
                   step_count=len(primary_treatments),
                   medication_count=len(medications),
                   confidence_score=confidence_score)

        return protocol
    
    def _calculate_confidence_score(self, diagnosis: str, age_group: str, urgency_level: str) -> float:
        """Calculate confidence score for treatment protocol"""
        base_score = 0.7
        
        # Increase score for well-established protocols
        if any(term in diagnosis.lower() for term in ["fever", "respiratory", "infection"]):
            base_score += 0.2
        
        # Decrease score for complex or rare conditions
        if any(term in diagnosis.lower() for term in ["rare", "complex", "atypical"]):
            base_score -= 0.1
        
        # Age group considerations
        if age_group in ["newborn", "infant"]:
            base_score -= 0.1  # Higher complexity for very young patients
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_evidence_summary(self, diagnosis: str) -> str:
        """Generate evidence summary"""
        return f"Treatment protocol based on current pediatric guidelines and evidence for {diagnosis}. Protocol includes age-appropriate dosing and monitoring recommendations."

class TreatmentValidator:
    """Validates treatment protocols for safety and appropriateness"""
    
    def __init__(self):
        self.drug_interactions = {
            "acetaminophen": ["warfarin", "seizure medications"],
            "ibuprofen": ["anticoagulants", "ACE inhibitors"],
            "amoxicillin": ["oral contraceptives", "warfarin"]
        }
        
        self.age_restrictions = {
            "aspirin": ["< 18 years", "contraindicated in children due to Reye syndrome"],
            "codeine": ["< 12 years", "FDA black box warning for respiratory depression"],
            "ibuprofen": ["< 6 months", "not approved for infants < 6 months"]
        }
    
    def validate_medication_safety(self, protocol: TreatmentProtocol) -> List[str]:
        """Validate medication safety"""
        warnings = []
        
        for medication in protocol.medications:
            # Check age restrictions
            for drug, restrictions in self.age_restrictions.items():
                if drug in medication.medication_name.lower():
                    if protocol.age_group in restrictions[0]:
                        warnings.append(f"{drug} contraindicated: {restrictions[1]}")
            
            # Check for duplicate medications in same class
            # (Implementation would check against current medications)
        
        return warnings
    
    def validate_dosing_appropriateness(self, protocol: TreatmentProtocol) -> List[str]:
        """Validate dosing appropriateness"""
        warnings = []
        
        for medication in protocol.medications:
            # Check if dose contains weight-based calculation
            if "mg/kg" in medication.dose:
                # This would need to be enhanced with actual weight validation
                pass
            
            # Check frequency appropriateness
            if medication.frequency not in ["q4-6h", "q6-8h", "q8-12h", "bid", "daily"]:
                warnings.append(f"Unusual frequency for {medication.medication_name}: {medication.frequency}")
        
        return warnings
    
    def validate_protocol_completeness(self, protocol: TreatmentProtocol) -> List[str]:
        """Validate protocol completeness"""
        warnings = []
        
        if not protocol.primary_treatments:
            warnings.append("No primary treatment steps defined")
        
        if not protocol.monitoring_plan:
            warnings.append("No monitoring plan specified")
        
        if not protocol.red_flag_criteria:
            warnings.append("No red flag criteria specified")
        
        if not protocol.follow_up_schedule:
            warnings.append("No follow-up schedule specified")
        
        return warnings
    
    def validate(self, protocol: TreatmentProtocol) -> Dict[str, Any]:
        """Comprehensive validation"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Medication safety validation
        medication_warnings = self.validate_medication_safety(protocol)
        validation_result["warnings"].extend(medication_warnings)
        
        # Dosing validation
        dosing_warnings = self.validate_dosing_appropriateness(protocol)
        validation_result["warnings"].extend(dosing_warnings)
        
        # Protocol completeness
        completeness_warnings = self.validate_protocol_completeness(protocol)
        validation_result["warnings"].extend(completeness_warnings)
        
        # Check confidence score
        if protocol.confidence_score < 0.5:
            validation_result["warnings"].append("Low confidence score - consider specialist consultation")
        
        # Generate recommendations
        if protocol.urgency_level == "emergency":
            validation_result["recommendations"].append("Consider immediate specialist consultation")
        
        if any("contraindicated" in warning for warning in medication_warnings):
            validation_result["recommendations"].append("Review medication selection with pharmacist")
        
        return validation_result