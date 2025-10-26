#!/usr/bin/env python3
"""Final validation test for the updated prompt system with safety fixes"""

import asyncio
import json
from pediassist.llm.client import LLMClient
from pediassist.llm.prompts import get_prompt_engine
from pediassist.config import settings
from types import SimpleNamespace

class ConfigWrapper:
    def __init__(self, settings):
        self.llm = SimpleNamespace()
        self.llm.provider = settings.llm_provider
        self.llm.model = settings.model
        self.llm.temperature = settings.temperature
        self.llm.max_tokens = 2000  # Increased for full response
        self.llm.monthly_budget = settings.monthly_budget
        self.llm.daily_budget = getattr(settings, 'daily_budget', 10.0)
        self.debug = settings.debug
        self.data_dir = settings.data_dir
        self.app_name = settings.app_name
        self.app_version = settings.app_version

async def test_final_validation():
    """Test the complete system with safety validation"""
    
    try:
        # Initialize client with wrapped config
        config_wrapper = ConfigWrapper(settings)
        client = LLMClient(config_wrapper)
        
        # Get prompt engine
        engine = get_prompt_engine()
        
        # Test case: Ear infection in 5-year-old
        print("Testing treatment plan generation for 5-year-old with ear pain...")
        
        # Generate treatment plan
        response = await client.generate_treatment_plan(
            diagnosis="ear pain",
            age=5,
            context="moderate severity",
            detail_level="detailed"
        )
        
        print(f"✅ Treatment plan generated successfully!")
        print(f"Response length: {len(response.content)} characters")
        print(f"Safety status: {'SAFE' if response.safety_check.is_safe else 'UNSAFE'}")
        print(f"Safety severity: {response.safety_check.severity}")
        
        if response.safety_check.flagged_terms:
            print(f"Flagged terms: {response.safety_check.flagged_terms}")
        
        if response.safety_check.recommendations:
            print(f"Safety recommendations: {response.safety_check.recommendations}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(response.content)
            print(f"\n✅ JSON parsed successfully!")
            print(f"Response type: {type(parsed)}")
            
            if isinstance(parsed, dict):
                print(f"Available keys: {list(parsed.keys())}")
                
                # Show key information
                if 'diagnosis' in parsed:
                    print(f"Primary diagnosis: {parsed['diagnosis']}")
                if 'treatment_summary' in parsed:
                    print(f"Treatment summary: {parsed['treatment_summary'][:100]}...")
                if 'medications' in parsed:
                    print(f"Medications: {len(parsed['medications'])} items")
                    for i, med in enumerate(parsed['medications'][:3]):  # Show first 3
                        print(f"  {i+1}. {med[:80]}...")
                if 'safety_alerts' in parsed:
                    print(f"Safety alerts: {len(parsed['safety_alerts'])} items")
                
            elif isinstance(parsed, list):
                print(f"Medications list: {len(parsed)} items")
                for i, item in enumerate(parsed[:3]):  # Show first 3
                    print(f"  {i+1}. {item[:80]}...")
                    
            return True
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON parsing failed: {e}")
            print(f"Content preview: {response.content[:300]}...")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_final_validation())
    print(f"\nFinal result: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)