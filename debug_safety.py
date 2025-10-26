#!/usr/bin/env python3
"""Debug safety validation to understand what's being flagged"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pediassist.llm.safety import SafetyValidator

async def debug_safety_validator():
    """Debug the safety validator to see what's being flagged"""
    
    # Initialize safety validator
    validator = SafetyValidator()
    
    # Test case: Legitimate medical treatment response
    medical_response = """
    {
      "diagnosis": "Acute Otitis Media (AOM) with Moderate Severity",
      "treatment_summary": "Combination of antibiotic therapy, analgesia, and close monitoring for resolution of symptoms. Immediate referral required for red flags.",
      "medications": [
        "Amoxicillin 45 mg/kg/day divided into two doses (e.g., 450 mg every 12 hours for a 20 kg child)",
        "Ibuprofen 7.5 mg/kg every 6-8 hours for pain (max 40 mg/kg/day)",
        "Acetaminophen 15 mg/kg every 4-6 hours as needed (max 75 mg/kg/day)"
      ]
    }
    """
    
    print("Debugging safety validation...")
    print(f"Response content: {medical_response[:200]}...")
    
    # Check individual safety components
    print("\n1. Checking for medical advice:")
    has_medical_advice = validator._contains_medical_advice(medical_response)
    print(f"   Contains medical advice: {has_medical_advice}")
    
    print("\n2. Checking for dosage information:")
    dosage_check = validator._validate_dosage_information(medical_response)
    print(f"   Dosage check result: {dosage_check}")
    
    print("\n3. Checking for emergency indicators:")
    has_emergency = validator._contains_emergency_indicators(medical_response)
    print(f"   Contains emergency indicators: {has_emergency}")
    
    print("\n4. Checking for emergency disclaimers:")
    has_emergency_disclaimer = validator._has_emergency_disclaimer(medical_response)
    print(f"   Has emergency disclaimers: {has_emergency_disclaimer}")
    
    print("\n5. Checking for medical disclaimers:")
    has_medical_disclaimer = validator._has_medical_disclaimer(medical_response)
    print(f"   Has medical disclaimers: {has_medical_disclaimer}")
    
    print("\n6. Checking age-appropriateness:")
    age_check = validator._validate_age_appropriate_response(medical_response, 5)
    print(f"   Age check result: {age_check}")
    
    # Full validation
    print("\n7. Full validation:")
    result = await validator.validate_response(medical_response, context={'age': 5})
    print(f"   Final result: {result}")

if __name__ == "__main__":
    asyncio.run(debug_safety_validator())