#!/usr/bin/env python3
"""Quick verification of all fixes implemented"""

import asyncio
import json
from pediassist.llm.safety import SafetyValidator

async def verify_safety_fixes():
    """Verify that safety validation fixes are working correctly"""
    
    validator = SafetyValidator()
    
    # Test cases
    test_cases = [
        {
            "name": "Legitimate medical treatment with disclaimers",
            "content": """For a 5-year-old with ear pain, the typical treatment includes:

**Medications:**
- Acetaminophen: 45-90 mg/kg/day divided every 4-6 hours as needed for pain
- Ibuprofen: 5-10 mg/kg/dose every 6-8 hours as needed

**Safety Information:**
This information is for educational purposes only and should not replace professional medical advice. Always consult your healthcare provider before starting any treatment. If symptoms worsen or red flags appear (high fever, severe pain, ear discharge), seek immediate medical attention or call 911.

**When to seek emergency care:**
- High fever (>102°F)
- Severe ear pain
- Ear discharge or bleeding""",
            "age": 5,
            "expected_safe": True,
            "expected_severity": "low"  # With proper disclaimers, should be low severity
        },
        {
            "name": "Unsafe direct dosage instruction",
            "content": "Give your child 500mg of acetaminophen right now.",
            "age": 5,
            "expected_safe": False,
            "expected_severity": "high"
        },
        {
            "name": "Medical advice without disclaimers",
            "content": "You should give your child antibiotics for this ear infection.",
            "age": 5,
            "expected_safe": True,  # Medium severity, still safe
            "expected_severity": "medium"
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        context = {'age': test_case['age']} if test_case['age'] else None
        result = await validator.validate_response(test_case['content'], context)
        
        print(f"  Safe: {result.is_safe} (expected: {test_case['expected_safe']})")
        print(f"  Severity: {result.severity} (expected: {test_case['expected_severity']})")
        
        if result.is_safe == test_case['expected_safe'] and result.severity == test_case['expected_severity']:
            print(f"  ✅ PASSED")
        else:
            print(f"  ❌ FAILED")
            all_passed = False
            if result.flagged_terms:
                print(f"  Flagged terms: {result.flagged_terms}")
            if result.recommendations:
                print(f"  Recommendations: {result.recommendations}")
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 ALL SAFETY FIXES VERIFIED SUCCESSFULLY!")
    else:
        print("❌ Some safety fixes need attention")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(verify_safety_fixes())