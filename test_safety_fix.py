#!/usr/bin/env python3
"""Test the safety validator fix for dosage information"""

import asyncio
import json
from pediassist.llm.safety import SafetyValidator

async def test_safety_validator():
    """Test the safety validator with legitimate medical dosage information"""
    
    validator = SafetyValidator()
    
    # Test case 1: Legitimate medical treatment response
    test_response = """
    {
      "primary_diagnosis": "Acute otitis media",
      "treatment_summary": "Antibiotic therapy for ear infection",
      "medications": [
        {
          "name": "Amoxicillin",
          "dose": "45-90 mg/kg/day",
          "route": "oral",
          "duration": "10 days"
        }
      ],
      "treatment_steps": [
        "Administer antibiotic as prescribed",
        "Monitor for improvement"
      ],
      "home_care": "Keep child comfortable",
      "when_to_see_doctor": "If symptoms worsen",
      "follow_up": "Return if no improvement in 48-72 hours",
      "safety_alerts": ["Always verify dosing with healthcare provider"]
    }
    """
    
    print("Testing safety validation with legitimate medical dosage information...")
    print("Response contains: 45-90 mg/kg/day")
    
    result = await validator.validate_response(test_response, context={'age': 5})
    
    print(f"Safety check result:")
    print(f"  Is safe: {result.is_safe}")
    print(f"  Severity: {result.severity}")
    print(f"  Reason: {result.reason}")
    print(f"  Flagged terms: {result.flagged_terms}")
    print(f"  Recommendations: {result.recommendations}")
    
    # Test case 2: Response without proper disclaimers (should be flagged)
    test_response_bad = """
    Give your child 500mg of acetaminophen every 6 hours.
    """
    
    print("\nTesting safety validation with potentially unsafe dosage information...")
    print("Response contains: 500mg")
    
    result_bad = await validator.validate_response(test_response_bad, context={'age': 5})
    
    print(f"Safety check result:")
    print(f"  Is safe: {result_bad.is_safe}")
    print(f"  Severity: {result_bad.severity}")
    print(f"  Reason: {result_bad.reason}")
    print(f"  Flagged terms: {result_bad.flagged_terms}")
    print(f"  Recommendations: {result_bad.recommendations}")

if __name__ == "__main__":
    asyncio.run(test_safety_validator())