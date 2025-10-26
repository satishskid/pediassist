"""
Treatment plan generator for pediatric patients
"""

import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog
from enum import Enum

logger = structlog.get_logger(__name__)

class TreatmentLevel(Enum):
    """Treatment complexity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TreatmentPriority(Enum):
    """Treatment priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TreatmentStep:
    """Individual treatment step"""
    step_number: int
    action: str
    rationale: str
    duration: Optional[str] = None
    monitoring: Optional[str] = None
    follow_up: Optional[str] = None
    red_flags: Optional[List[str]] = None
    delegation_level: str = "RN"  # RN, LPN, MA, etc.

@dataclass
class TreatmentPlan:
    """Complete treatment plan"""
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
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class TreatmentGenerator:
    """Generates evidence-based treatment plans for pediatric patients"""
    
    def __init__(self):
        # Treatment protocols database (simplified)
        self.treatment_protocols = self._load_treatment_protocols()
        
        # Medication dosing guidelines
        self.medication_guidelines = self._load_medication_guidelines()
        
        # Age-appropriate treatment modifications
        self.age_modifications = self._load_age_modifications()
    
    def _load_treatment_protocols(self) -> Dict[str, Dict[str, Any]]:
        """Load evidence-based treatment protocols"""
        return {
            "asthma": {
                "basic": {
                    "steps": [
                        {
                            "step_number": 1,
                            "action": "Assess respiratory status and oxygen saturation",
                            "rationale": "Establish baseline respiratory function",
                            "delegation_level": "RN",
                            "monitoring": "Respiratory rate, oxygen saturation, work of breathing",
                            "duration": "5 minutes"
                        },
                        {
                            "step_number": 2,
                            "action": "Administer bronchodilator (albuterol 2.5mg nebulizer or 4-8 puffs MDI with spacer)",
                            "rationale": "Relieve bronchospasm and improve airflow",
                            "delegation_level": "RN",
                            "monitoring": "Response to treatment, heart rate, tremors",
                            "duration": "15 minutes",
                            "red_flags": ["No improvement after 2 treatments", "Oxygen saturation <92%", "Severe wheezing"]
                        },
                        {
                            "step_number": 3,
                            "action": "Reassess respiratory status post-treatment",
                            "rationale": "Evaluate treatment effectiveness",
                            "delegation_level": "RN",
                            "monitoring": "Respiratory rate, oxygen saturation, peak flow if age appropriate",
                            "duration": "5 minutes",
                            "follow_up": "If improved, discharge with follow-up instructions"
                        }
                    ],
                    "medications": ["albuterol", "ipratropium"],
                    "monitoring": ["respiratory_rate", "oxygen_saturation", "peak_flow"],
                    "follow_up": "Return if symptoms worsen or no improvement in 24 hours",
                    "red_flags": ["Persistent wheezing", "Oxygen saturation <92%", "Inability to speak in sentences"],
                    "duration_estimate": "30-45 minutes",
                    "priority": "medium"
                },
                "intermediate": {
                    "steps": [
                        {
                            "step_number": 1,
                            "action": "Complete respiratory assessment including peak flow if >5 years",
                            "rationale": "Comprehensive evaluation of asthma severity",
                            "delegation_level": "RN",
                            "monitoring": "Peak flow, respiratory exam, oxygen saturation"
                        },
                        {
                            "step_number": 2,
                            "action": "Administer albuterol 2.5-5mg nebulizer q20min x 3 doses",
                            "rationale": "Aggressive bronchodilator therapy for moderate exacerbation",
                            "delegation_level": "RN",
                            "monitoring": "Continuous cardiac monitoring, response assessment"
                        },
                        {
                            "step_number": 3,
                            "action": "Add ipratropium 0.5mg nebulizer if poor response",
                            "rationale": "Additional bronchodilation with anticholinergic",
                            "delegation_level": "RN"
                        },
                        {
                            "step_number": 4,
                            "action": "Consider oral corticosteroids (prednisolone 1-2mg/kg)",
                            "rationale": "Systemic anti-inflammatory therapy",
                            "delegation_level": "MD/DO",
                            "red_flags": ["No response to bronchodilators", "Peak flow <50% predicted"]
                        }
                    ],
                    "medications": ["albuterol", "ipratropium", "prednisolone"],
                    "monitoring": ["peak_flow", "respiratory_rate", "oxygen_saturation", "heart_rate"],
                    "follow_up": "Primary care follow-up in 2-3 days",
                    "red_flags": ["Peak flow <50% predicted", "No response to treatment", "Altered mental status"],
                    "duration_estimate": "2-4 hours",
                    "priority": "high"
                }
            },
            "otitis_media": {
                "basic": {
                    "steps": [
                        {
                            "step_number": 1,
                            "action": "Perform otoscopic examination",
                            "rationale": "Confirm diagnosis and assess severity",
                            "delegation_level": "MD/DO",
                            "monitoring": "Tympanic membrane appearance, mobility"
                        },
                        {
                            "step_number": 2,
                            "action": "Prescribe antibiotic therapy (amoxicillin 45mg/kg/day divided BID)",
                            "rationale": "Treat bacterial infection",
                            "delegation_level": "MD/DO",
                            "duration": "10 days",
                            "follow_up": "Reassess in 10-14 days if symptoms persist"
                        },
                        {
                            "step_number": 3,
                            "action": "Provide pain management instructions",
                            "rationale": "Improve patient comfort",
                            "delegation_level": "RN",
                            "monitoring": "Pain level, response to analgesics"
                        }
                    ],
                    "medications": ["amoxicillin", "acetaminophen", "ibuprofen"],
                    "monitoring": ["pain_level", "fever"],
                    "follow_up": "Return if fever >101°F or pain persists >48 hours",
                    "red_flags": ["Mastoid tenderness", "Facial paralysis", "Severe headache"],
                    "duration_estimate": "10-14 days",
                    "priority": "medium"
                }
            },
            "gastroenteritis": {
                "basic": {
                    "steps": [
                        {
                            "step_number": 1,
                            "action": "Assess hydration status (capillary refill, mucous membranes, tears)",
                            "rationale": "Determine dehydration severity",
                            "delegation_level": "RN",
                            "monitoring": "Vital signs, capillary refill, mental status"
                        },
                        {
                            "step_number": 2,
                            "action": "Initiate oral rehydration (Pedialyte 5-10ml/kg q5-10min)",
                            "rationale": "Replace fluid losses",
                            "delegation_level": "RN",
                            "monitoring": "Tolerance of oral fluids, urine output",
                            "duration": "4-6 hours"
                        },
                        {
                            "step_number": 3,
                            "action": "Educate on continued oral rehydration at home",
                            "rationale": "Prevent further dehydration",
                            "delegation_level": "RN",
                            "follow_up": "Return if unable to maintain hydration"
                        }
                    ],
                    "medications": ["oral_rehydration_solution"],
                    "monitoring": ["hydration_status", "vital_signs", "urine_output"],
                    "follow_up": "Return if vomiting persists >24 hours or signs of dehydration",
                    "red_flags": ["Severe dehydration", "Bloody diarrhea", "Persistent vomiting"],
                    "duration_estimate": "24-48 hours",
                    "priority": "medium"
                }
            }
        }
    
    def _load_medication_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load medication dosing guidelines"""
        return {
            "albuterol": {
                "dosing": {
                    "nebulizer": {
                        "dose": "2.5-5mg",
                        "frequency": "q20min x 3, then q1-4h PRN",
                        "max_daily": "12mg"
                    },
                    "mdi": {
                        "dose": "4-8 puffs",
                        "frequency": "q20min x 3, then q1-4h PRN",
                        "notes": "Use with spacer device"
                    }
                },
                "age_restrictions": {
                    "min_age_months": 2,
                    "max_age_months": 216  # 18 years
                },
                "contraindications": ["hypersensitivity to albuterol", "tachycardia"],
                "monitoring": ["heart_rate", "blood_pressure", "tremors"]
            },
            "amoxicillin": {
                "dosing": {
                    "standard": {
                        "dose": "45mg/kg/day",
                        "frequency": "divided BID",
                        "duration": "10 days",
                        "max_daily": "1g"
                    },
                    "high_dose": {
                        "dose": "80-90mg/kg/day",
                        "frequency": "divided BID",
                        "indication": "resistant organisms"
                    }
                },
                "age_restrictions": {
                    "min_age_months": 1
                },
                "contraindications": ["penicillin allergy", "infectious mononucleosis"],
                "monitoring": ["allergic_reactions", "diarrhea"]
            }
        }
    
    def _load_age_modifications(self) -> Dict[str, Dict[str, Any]]:
        """Load age-appropriate treatment modifications"""
        return {
            "newborn": {
                "medication_adjustments": {
                    "dose_reduction": 0.5,  # 50% of standard dose
                    "frequency_increase": 1.5,  # 1.5x frequency
                    "special_considerations": ["immature metabolism", "renal function development"]
                },
                "monitoring_increased": ["vital_signs", "neurological_status", "feeding_tolerance"],
                "special_precautions": ["temperature_stability", "infection_risk", "parent_education"]
            },
            "infant": {
                "medication_adjustments": {
                    "dose_reduction": 0.7,
                    "frequency_increase": 1.3
                },
                "monitoring_increased": ["weight_gain", "developmental_milestones"],
                "special_precautions": ["oral_intake", "sleep_patterns"]
            },
            "toddler": {
                "medication_adjustments": {
                    "dose_reduction": 0.8,
                    "liquid_preparations": True
                },
                "special_precautions": ["choking_hazard", "behavioral_changes"]
            }
        }
    
    def generate_treatment_plan(
        self,
        diagnosis: str,
        patient_age_months: int,
        severity: str = "moderate",
        comorbidities: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        complexity_level: TreatmentLevel = TreatmentLevel.BASIC
    ) -> TreatmentPlan:
        """Generate a treatment plan based on diagnosis and patient characteristics"""
        
        # Determine appropriate treatment level
        treatment_level = self._determine_treatment_level(
            diagnosis, severity, patient_age_months, comorbidities
        )
        
        # Get base protocol
        protocol = self._get_treatment_protocol(diagnosis, treatment_level)
        if not protocol:
            raise ValueError(f"No treatment protocol found for {diagnosis} at {treatment_level.value} level")
        
        # Apply age-appropriate modifications
        modified_protocol = self._apply_age_modifications(protocol, patient_age_months)
        
        # Apply allergy considerations
        if allergies:
            modified_protocol = self._apply_allergy_modifications(modified_protocol, allergies)
        
        # Generate treatment steps
        steps = self._generate_treatment_steps(modified_protocol, patient_age_months)
        
        # Get medications with dosing
        medications = self._get_medications_with_dosing(
            modified_protocol["medications"], patient_age_months, allergies
        )
        
        # Calculate priority
        priority = self._calculate_priority(diagnosis, severity, patient_age_months)
        
        # Generate patient education
        patient_education = self._generate_patient_education(
            diagnosis, modified_protocol, patient_age_months
        )
        
        return TreatmentPlan(
            diagnosis=diagnosis,
            plan_type=treatment_level,
            priority=priority,
            steps=steps,
            medications=medications,
            monitoring_parameters=modified_protocol["monitoring"],
            follow_up_instructions=modified_protocol["follow_up"],
            patient_education=patient_education,
            red_flags=modified_protocol["red_flags"],
            duration_estimate=modified_protocol["duration_estimate"]
        )
    
    def _determine_treatment_level(
        self,
        diagnosis: str,
        severity: str,
        age_months: int,
        comorbidities: Optional[List[str]]
    ) -> TreatmentLevel:
        """Determine appropriate treatment complexity level"""
        
        # Age considerations
        if age_months < 6:  # Infants
            return TreatmentLevel.INTERMEDIATE
        
        # Severity considerations
        if severity == "severe":
            return TreatmentLevel.ADVANCED
        elif severity == "mild":
            return TreatmentLevel.BASIC
        
        # Comorbidity considerations
        if comorbidities and len(comorbidities) > 1:
            return TreatmentLevel.INTERMEDIATE
        
        # Default to basic for moderate cases
        return TreatmentLevel.BASIC
    
    def _get_treatment_protocol(self, diagnosis: str, level: TreatmentLevel) -> Optional[Dict[str, Any]]:
        """Get treatment protocol for diagnosis and level"""
        if diagnosis not in self.treatment_protocols:
            return None
        
        protocols = self.treatment_protocols[diagnosis]
        
        # Try to get the requested level, fall back to available levels
        if level.value in protocols:
            return protocols[level.value]
        elif TreatmentLevel.BASIC.value in protocols:
            return protocols[TreatmentLevel.BASIC.value]
        elif TreatmentLevel.INTERMEDIATE.value in protocols:
            return protocols[TreatmentLevel.INTERMEDIATE.value]
        
        return None
    
    def _apply_age_modifications(self, protocol: Dict[str, Any], age_months: int) -> Dict[str, Any]:
        """Apply age-appropriate modifications to protocol"""
        modified_protocol = protocol.copy()
        
        age_group = self._get_age_group(age_months)
        
        if age_group in self.age_modifications:
            age_mods = self.age_modifications[age_group]
            
            # Apply medication adjustments
            if "medication_adjustments" in age_mods:
                # This would modify medication dosing in a real implementation
                modified_protocol["age_specific_notes"] = age_mods["medication_adjustments"]
            
            # Add monitoring requirements
            if "monitoring_increased" in age_mods:
                modified_protocol["monitoring"].extend(age_mods["monitoring_increased"])
            
            # Add special precautions
            if "special_precautions" in age_mods:
                modified_protocol["special_precautions"] = age_mods["special_precautions"]
        
        return modified_protocol
    
    def _apply_allergy_modifications(self, protocol: Dict[str, Any], allergies: List[str]) -> Dict[str, Any]:
        """Apply allergy-related modifications to protocol"""
        modified_protocol = protocol.copy()
        
        # Check each medication against allergies
        safe_medications = []
        for medication in protocol.get("medications", []):
            if not self._has_allergy_conflict(medication, allergies):
                safe_medications.append(medication)
            else:
                # Find alternative medication
                alternative = self._find_alternative_medication(medication, allergies)
                if alternative:
                    safe_medications.append(alternative)
        
        modified_protocol["medications"] = safe_medications
        return modified_protocol
    
    def _generate_treatment_steps(self, protocol: Dict[str, Any], age_months: int) -> List[TreatmentStep]:
        """Generate treatment steps from protocol"""
        steps = []
        
        for step_data in protocol.get("steps", []):
            step = TreatmentStep(
                step_number=step_data["step_number"],
                action=step_data["action"],
                rationale=step_data["rationale"],
                duration=step_data.get("duration"),
                monitoring=step_data.get("monitoring"),
                follow_up=step_data.get("follow_up"),
                red_flags=step_data.get("red_flags", []),
                delegation_level=step_data.get("delegation_level", "RN")
            )
            steps.append(step)
        
        return steps
    
    def _get_medications_with_dosing(
        self, medication_names: List[str], age_months: int, allergies: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Get medications with age-appropriate dosing"""
        medications = []
        
        for med_name in medication_names:
            if med_name in self.medication_guidelines:
                med_guidelines = self.medication_guidelines[med_name]
                
                # Calculate age-appropriate dosing
                dosing = self._calculate_age_appropriate_dosing(med_guidelines, age_months)
                
                medications.append({
                    "name": med_name,
                    "dosing": dosing,
                    "monitoring": med_guidelines.get("monitoring", []),
                    "contraindications": med_guidelines.get("contraindications", [])
                })
        
        return medications
    
    def _calculate_age_appropriate_dosing(self, guidelines: Dict[str, Any], age_months: int) -> Dict[str, Any]:
        """Calculate age-appropriate medication dosing"""
        # This is a simplified implementation
        # In practice, this would use weight-based calculations
        
        age_group = self._get_age_group(age_months)
        
        if age_group in ["newborn", "infant"]:
            # Reduce dose for young patients
            return {
                "dose": "Reduced dose per protocol",
                "frequency": "Increased frequency per protocol",
                "notes": "Age-appropriate dosing required"
            }
        else:
            return guidelines.get("dosing", {})
    
    def _calculate_priority(self, diagnosis: str, severity: str, age_months: int) -> TreatmentPriority:
        """Calculate treatment priority"""
        
        # Age considerations
        if age_months < 3:
            return TreatmentPriority.HIGH
        
        # Severity considerations
        if severity == "severe":
            return TreatmentPriority.CRITICAL
        elif severity == "mild":
            return TreatmentPriority.LOW
        
        # Diagnosis-specific priorities
        high_priority_diagnoses = ["asthma", "pneumonia", "febrile_seizure"]
        if diagnosis in high_priority_diagnoses:
            return TreatmentPriority.HIGH
        
        return TreatmentPriority.MEDIUM
    
    def _generate_patient_education(self, diagnosis: str, protocol: Dict[str, Any], age_months: int) -> str:
        """Generate age-appropriate patient education"""
        
        age_group = self._get_age_group(age_months)
        
        base_education = f"""
        Your child has been diagnosed with {diagnosis.replace('_', ' ')}. 
        
        Key points for care at home:
        {protocol.get('follow_up', 'Follow up with your healthcare provider as recommended.')}
        
        Watch for these warning signs and return immediately if you notice:
        {', '.join(protocol.get('red_flags', ['worsening symptoms']))}
        """
        
        # Age-specific additions
        if age_group == "infant":
            base_education += "\n\nFor infants: Monitor feeding, wet diapers, and temperature closely."
        elif age_group == "toddler":
            base_education += "\n\nFor toddlers: Encourage fluids and watch for changes in behavior or activity level."
        
        return base_education.strip()
    
    def _get_age_group(self, age_months: int) -> str:
        """Get age group from months"""
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
    
    def _has_allergy_conflict(self, medication: str, allergies: List[str]) -> bool:
        """Check if medication conflicts with allergies"""
        # Simplified implementation
        med_lower = medication.lower()
        for allergy in allergies:
            if allergy.lower() in med_lower or med_lower in allergy.lower():
                return True
        return False
    
    def _find_alternative_medication(self, medication: str, allergies: List[str]) -> Optional[str]:
        """Find alternative medication for allergy"""
        # Simplified alternatives
        alternatives = {
            "amoxicillin": "azithromycin",
            "penicillin": "cephalexin",
            "sulfa": "clindamycin"
        }
        
        return alternatives.get(medication.lower())
    
    def estimate_cost(self, plan: TreatmentPlan) -> float:
        """Estimate treatment cost"""
        base_costs = {
            TreatmentLevel.BASIC: 100.0,
            TreatmentLevel.INTERMEDIATE: 250.0,
            TreatmentLevel.ADVANCED: 500.0
        }
        
        base_cost = base_costs.get(plan.plan_type, 100.0)
        
        # Add medication costs
        med_cost = len(plan.medications) * 25.0
        
        # Add monitoring costs
        monitoring_cost = len(plan.monitoring_parameters) * 15.0
        
        return base_cost + med_cost + monitoring_cost
    
    def validate_plan(self, plan: TreatmentPlan) -> Dict[str, Any]:
        """Validate treatment plan for safety and completeness"""
        
        validation = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for required components
        if not plan.steps:
            validation["errors"].append("Treatment plan has no steps")
            validation["is_valid"] = False
        
        if not plan.medications:
            validation["warnings"].append("No medications specified in treatment plan")
        
        # Check for red flags
        if not plan.red_flags:
            validation["warnings"].append("No red flags specified for treatment plan")
        
        # Check step completeness
        for i, step in enumerate(plan.steps):
            if not step.action:
                validation["errors"].append(f"Step {i+1} has no action specified")
                validation["is_valid"] = False
            
            if not step.rationale:
                validation["warnings"].append(f"Step {i+1} has no rationale provided")
        
        # Check priority vs. complexity alignment
        if plan.priority == TreatmentPriority.CRITICAL and plan.plan_type == TreatmentLevel.BASIC:
            validation["warnings"].append("Critical priority with basic treatment level may be insufficient")
        
        return validation