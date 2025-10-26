#!/usr/bin/env python3
"""Quick test for safety validation fixes"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pediassist.llm.safety import SafetyValidator

async def test_safety_validator():
    """Test the safety validator with medical treatment context"""
    
    # Initialize safety validator
    validator = SafetyValidator()
    
    # Test case 1: Legitimate medical treatment response
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
    
    # Test case 2: Unsafe direct dosage instruction
    unsafe_response = """
    Give your child 500mg of acetaminophen every 6 hours.
    """
    
    print("Testing safety validation...")
    
    # Test legitimate medical response
    print("\n1. Testing legitimate medical treatment response:")
    result1 = await validator.validate_response(medical_response, context={'age': 5})
    print(f"   Is safe: {result1.is_safe}")
    print(f"   Severity: {result1.severity}")
    print(f"   Flagged terms: {result1.flagged_terms}")
    print(f"   Recommendations: {result1.recommendations}")
    
    # Test unsafe response
    print("\n2. Testing unsafe direct dosage instruction:")
    result2 = await validator.validate_response(unsafe_response, context={'age': 5})
    print(f"   Is safe: {result2.is_safe}")
    print(f"   Severity: {result2.severity}")
    print(f"   Flagged terms: {result2.flagged_terms}")
    print(f"   Recommendations: {result2.recommendations}")
    
    # Verify results
    print("\n" + "="*50)
    if result1.is_safe and not result2.is_safe:
        print("✅ SUCCESS: Safety validator correctly distinguishes legitimate medical content from unsafe content")
    else:
        print("❌ FAILED: Safety validator not working correctly")
        print(f"   Medical response should be safe: {result1.is_safe}")
        print(f"   Unsafe response should be unsafe: {not result2.is_safe}")
    
    return result1.is_safe and not result2.is_safe

if __name__ == "__main__":
    success = asyncio.run(test_safety_validator())
    sys.exit(0 if success else 1)