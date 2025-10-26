"""
Prompt templates for PediAssist
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

class PromptTemplate:
    """Base class for prompt templates"""
    
    def __init__(self, template: str, variables: Dict[str, Any]):
        self.template = template
        self.variables = variables
    
    def render(self, **kwargs) -> str:
        """Render the template with provided variables"""
        context = {**self.variables, **kwargs}
        return self.template.format(**context)

# Master prompt template for PediAssist
MASTER_PROMPT_TEMPLATE = """
You are PediAssist, an AI assistant specialized in pediatric healthcare. Your role is to provide evidence-based clinical guidance for pediatric conditions while maintaining the highest standards of safety and accuracy.

## Core Competencies
- Expert knowledge across all pediatric subspecialties
- Evidence-based treatment recommendations
- Age-appropriate dosing calculations
- Patient communication in layman's terms
- Recognition of when specialist referral is needed

## Response Requirements

### 1. Safety First
- Always include appropriate safety warnings
- Specify contraindications and red flags
- Clearly state when immediate medical attention is required
- Never provide information that could delay emergency care

### 2. Evidence-Based Practice
- Base recommendations on established guidelines (AAP, CDC, WHO)
- Cite evidence levels when applicable
- Acknowledge limitations and areas of uncertainty
- Distinguish between established practice and emerging evidence

### 3. Practical Applicability
- Provide actionable, step-by-step guidance
- Include specific dosing when appropriate
- Consider real-world constraints (availability, cost, compliance)
- Address common clinical scenarios and variations

### 4. Communication Excellence
- Use clear, professional language
- Structure responses for easy scanning
- Include both clinical and patient-friendly explanations
- Provide templates for patient communication when requested

## Input Format
Patient Information:
- Age: {patient_age}
- Diagnosis: {diagnosis}
- Severity: {severity_level}
- Additional Context: {additional_context}

## Output Format - CRITICAL INSTRUCTIONS

### JSON Response Requirements (MANDATORY)
You MUST respond with a valid, well-formed JSON object. Your entire response should be parseable as JSON with no additional text before or after.

**CRITICAL JSON RULES:**
1. Response must start with opening brace and end with closing brace
2. No markdown formatting, explanations, or text outside the JSON
3. Use double quotes for all strings (not single quotes)
4. All numeric values must be valid numbers (not strings)
5. Arrays must contain properly formatted objects
6. All required fields must be present (see schema below)

### Required JSON Schema (Simplified)
Your response must include these fields:
- diagnosis: string with exact diagnosis name
- treatment_summary: string with brief overview
- medications: array of medication names/dosing
- treatment_steps: array of step instructions
- home_care: array of home care instructions
- when_to_see_doctor: array of warning signs
- follow_up: string with timing and conditions

### Validation Checklist (Use Before Responding)
Before providing your JSON response, verify:
- [ ] Response starts with opening brace and ends with closing brace
- [ ] All strings use double quotes
- [ ] No single quotes anywhere in the JSON
- [ ] All required fields are present (diagnosis, treatment_summary, medications, treatment_steps, home_care, when_to_see_doctor, follow_up)
- [ ] Arrays contain properly formatted strings
- [ ] No markdown code blocks or explanatory text

### Example Valid Response (Use as Template)
Remember to use proper JSON format with double quotes, required fields, and no markdown formatting.

Remember: This is clinical decision support, not a substitute for clinical judgment. Always consider individual patient factors and local protocols.
"""

# Specific prompt templates for different use cases
DIAGNOSIS_PROMPT_TEMPLATE = """
{master_prompt}

## Clinical Scenario
Provide comprehensive guidance for managing {diagnosis} in a {patient_age}-year-old patient.

Severity: {severity_level}
Additional clinical information: {additional_context}

Please provide a complete treatment approach following the output format above.
"""

TREATMENT_PLAN_PROMPT_TEMPLATE = """
{master_prompt}

## Treatment Plan Request
Create a detailed treatment plan for:
- Diagnosis: {diagnosis}
- Patient Age: {patient_age}
- Severity: {severity_level}
- Current Medications: {current_medications}
- Allergies: {allergies}
- Comorbidities: {comorbidities}

Focus on practical, implementable steps with specific medications, dosing, and monitoring parameters.
"""

PATIENT_COMMUNICATION_PROMPT_TEMPLATE = """
{master_prompt}

## Patient Communication Request
Create a parent-friendly explanation for:
- Diagnosis: {diagnosis}
- Patient Age: {patient_age}
- Key Points to Cover: {key_points}
- Parent Education Level: {education_level}

Provide clear, reassuring language that addresses common parent concerns and questions.
"""

MEDICATION_DOSE_PROMPT_TEMPLATE = """
{master_prompt}

## Medication Dosing Request
Calculate appropriate dosing for:
- Medication: {medication}
- Patient Age: {patient_age}
- Patient Weight: {patient_weight}
- Indication: {indication}
- Route: {route}

Provide specific dosing with evidence references and safety considerations.
"""

REFERRAL_CRITERIA_PROMPT_TEMPLATE = """
{master_prompt}

## Referral Criteria Request
Define clear criteria for when to refer {diagnosis} to subspecialist care.

Patient Age: {patient_age}
Subspecialty: {subspecialty}
Level of Care Available: {care_level}

Include both urgent and routine referral indications.
"""

class PromptEngine:
    """Engine for managing and rendering prompts"""
    
    def __init__(self):
        self.templates = {
            "master": PromptTemplate(MASTER_PROMPT_TEMPLATE, {}),
            "diagnosis": PromptTemplate(DIAGNOSIS_PROMPT_TEMPLATE, {}),
            "treatment_plan": PromptTemplate(TREATMENT_PLAN_PROMPT_TEMPLATE, {}),
            "patient_communication": PromptTemplate(PATIENT_COMMUNICATION_PROMPT_TEMPLATE, {}),
            "medication_dose": PromptTemplate(MEDICATION_DOSE_PROMPT_TEMPLATE, {}),
            "referral_criteria": PromptTemplate(REFERRAL_CRITERIA_PROMPT_TEMPLATE, {}),
        }
    
    def render_diagnosis_prompt(
        self,
        diagnosis: str,
        patient_age: int,
        severity_level: str = "moderate",
        additional_context: str = ""
    ) -> str:
        """Render diagnosis prompt"""
        master_context = {
            "patient_age": patient_age,
            "diagnosis": diagnosis,
            "severity_level": severity_level,
            "additional_context": additional_context
        }
        
        master_rendered = self.templates["master"].render(**master_context)
        
        return self.templates["diagnosis"].render(
            master_prompt=master_rendered,
            diagnosis=diagnosis,
            patient_age=patient_age,
            severity_level=severity_level,
            additional_context=additional_context
        )
    
    def render_treatment_plan_prompt(
        self,
        diagnosis: str,
        patient_age: int,
        severity_level: str,
        current_medications: str = "None",
        allergies: str = "None known",
        comorbidities: str = "None"
    ) -> str:
        """Render treatment plan prompt"""
        master_context = {
            "patient_age": patient_age,
            "diagnosis": diagnosis,
            "severity_level": severity_level,
            "additional_context": f"Current medications: {current_medications}, Allergies: {allergies}, Comorbidities: {comorbidities}"
        }
        
        master_rendered = self.templates["master"].render(**master_context)
        
        return self.templates["treatment_plan"].render(
            master_prompt=master_rendered,
            diagnosis=diagnosis,
            patient_age=patient_age,
            severity_level=severity_level,
            current_medications=current_medications,
            allergies=allergies,
            comorbidities=comorbidities
        )
    
    def render_patient_communication_prompt(
        self,
        diagnosis: str,
        patient_age: int,
        key_points: str,
        education_level: str = "general"
    ) -> str:
        """Render patient communication prompt"""
        master_context = {
            "patient_age": patient_age,
            "diagnosis": diagnosis,
            "severity_level": "general",
            "additional_context": f"Patient education focus on: {key_points}"
        }
        
        master_rendered = self.templates["master"].render(**master_context)
        
        return self.templates["patient_communication"].render(
            master_prompt=master_rendered,
            diagnosis=diagnosis,
            patient_age=patient_age,
            key_points=key_points,
            education_level=education_level
        )
    
    def render_medication_dose_prompt(
        self,
        medication: str,
        patient_age: int,
        patient_weight: float,
        indication: str,
        route: str = "oral"
    ) -> str:
        """Render medication dosing prompt"""
        master_context = {
            "patient_age": patient_age,
            "diagnosis": indication,
            "severity_level": "dosing calculation",
            "additional_context": f"Medication: {medication}, Weight: {patient_weight}kg, Route: {route}"
        }
        
        master_rendered = self.templates["master"].render(**master_context)
        
        return self.templates["medication_dose"].render(
            master_prompt=master_rendered,
            medication=medication,
            patient_age=patient_age,
            patient_weight=patient_weight,
            indication=indication,
            route=route
        )
    
    def render_referral_criteria_prompt(
        self,
        diagnosis: str,
        patient_age: int,
        subspecialty: str,
        care_level: str = "primary"
    ) -> str:
        """Render referral criteria prompt"""
        master_context = {
            "patient_age": patient_age,
            "diagnosis": diagnosis,
            "severity_level": "referral assessment",
            "additional_context": f"Subspecialty: {subspecialty}, Care level: {care_level}"
        }
        
        master_rendered = self.templates["master"].render(**master_context)
        
        return self.templates["referral_criteria"].render(
            master_prompt=master_rendered,
            diagnosis=diagnosis,
            patient_age=patient_age,
            subspecialty=subspecialty,
            care_level=care_level
        )
    
    def build_treatment_prompt(
        self,
        diagnosis: str,
        age: int,
        context: Optional[str] = None,
        detail_level: str = "detailed",
        include_parent_handout: bool = False,
        include_child_explanation: bool = False
    ) -> str:
        """Build treatment prompt (alias for render_treatment_plan_prompt)"""
        return self.render_treatment_plan_prompt(
            diagnosis=diagnosis,
            patient_age=age,
            severity_level=detail_level,
            current_medications="None" if context is None else context,
            allergies="None known",
            comorbidities="None"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for LLM interactions"""
        return MASTER_PROMPT_TEMPLATE

# Global prompt engine instance
_prompt_engine: Optional[PromptEngine] = None

def get_prompt_engine() -> PromptEngine:
    """Get or create the global prompt engine"""
    global _prompt_engine
    
    if _prompt_engine is None:
        _prompt_engine = PromptEngine()
    
    return _prompt_engine