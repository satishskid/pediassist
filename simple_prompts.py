#!/usr/bin/env python3
"""Simplified prompt for testing JSON responses"""

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

# Simplified master prompt template
SIMPLE_MASTER_PROMPT = """
You are a pediatric healthcare assistant. Provide treatment guidance in JSON format.

Patient: {patient_age} years old, Diagnosis: {diagnosis}, Severity: {severity_level}

RESPOND ONLY WITH VALID JSON. No other text.

Required JSON format:
{{
  "diagnosis": "exact diagnosis name",
  "treatment_summary": "brief treatment overview",
  "medications": ["list of recommended medications"],
  "home_care": ["home care instructions"],
  "when_to_see_doctor": ["warning signs"],
  "follow_up": "follow-up instructions"
}}
"""

SIMPLE_TREATMENT_PROMPT = """
{master_prompt}

Create treatment plan for {diagnosis} in {patient_age}-year-old patient.
"""

class SimplePromptEngine:
    """Simplified prompt engine for testing"""
    
    def __init__(self):
        self.templates = {
            "master": PromptTemplate(SIMPLE_MASTER_PROMPT, {}),
            "treatment": PromptTemplate(SIMPLE_TREATMENT_PROMPT, {}),
        }
    
    def build_simple_treatment_prompt(self, diagnosis: str, patient_age: int) -> str:
        """Build simplified treatment prompt"""
        master_context = {
            "patient_age": patient_age,
            "diagnosis": diagnosis,
            "severity_level": "moderate"
        }
        
        master_rendered = self.templates["master"].render(**master_context)
        
        return self.templates["treatment"].render(
            master_prompt=master_rendered,
            diagnosis=diagnosis,
            patient_age=patient_age
        )

# Global instance
_simple_engine: Optional[SimplePromptEngine] = None

def get_simple_prompt_engine() -> SimplePromptEngine:
    """Get or create the simple prompt engine"""
    global _simple_engine
    
    if _simple_engine is None:
        _simple_engine = SimplePromptEngine()
    
    return _simple_engine

if __name__ == "__main__":
    engine = get_simple_prompt_engine()
    prompt = engine.build_simple_treatment_prompt("ear pain", 5)
    print("Generated prompt:")
    print(prompt)
    print("\nPrompt length:", len(prompt), "characters")