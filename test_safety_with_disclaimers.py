#!/usr/bin/env python3
"""Test safety validation with proper medical disclaimers"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pediassist.llm.safety import SafetyValidator

async def test_safety_with_disclaimers():
    """Test the safety validator with proper medical disclaimers"""
    
    # Initialize safety validator
    validator = SafetyValidator()
    
    # Test case: Legitimate medical treatment response WITH disclaimers
    medical_response_with_disclaimers = """
    {
      "diagnosis": "Acute Otitis Media (AOM) with Moderate Severity",
      "treatment_summary": "Combination of antibiotic therapy, analgesia, and close monitoring for resolution of symptoms. Immediate referral required for red flags. This information is for educational purposes only and should not replace professional medical advice.",
      "medications": [
        "Amoxicillin 45 mg/kg/day divided into two doses (e.g., 450 mg every 12 hours for a 20 kg child) - dosage must be confirmed by healthcare provider",
        "Ibuprofen 7.5 mg/kg every 6-8 hours for pain (max 40 mg/kg/day) - as prescribed by doctor",
        "Acetaminophen 15 mg/kg every 4-6 hours as needed (max 75 mg/kg/day) - under medical supervision"
      ],
      "disclaimer": "This treatment plan is for informational purposes only. Always consult your healthcare provider before starting any treatment. If symptoms worsen or red flags appear, seek immediate medical attention or call 911."
    }
    """
    
    print("Testing safety validation with proper disclaimers...")
    
    # Test legitimate medical response with disclaimers
    print("\nTesting legitimate medical treatment response WITH disclaimers:")
    result = await validator.validate_response(medical_response_with_disclaimers, context={'age': 5})
    print(f"   Is safe: {result.is_safe}")
    print(f"   Severity: {result.severity}")
    print(f"   Flagged terms: {result.flagged_terms}")
    print(f"   Recommendations: {result.recommendations}")
    
    # Verify results
    print("\n" + "="*50)
    if result.is_safe:
        print("✅ SUCCESS: Safety validator correctly accepts legitimate medical content with disclaimers")
    else:
        print("❌ FAILED: Safety validator still rejecting legitimate medical content")
    
    return result.is_safe

if __name__ == "__main__":
    success = asyncio.run(test_safety_with_disclaimers())
    sys.exit(0 if success else 1)