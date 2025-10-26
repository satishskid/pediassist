#!/usr/bin/env python3
"""Test updated prompt system with simplified schema"""

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
        self.llm.max_tokens = 1000
        self.llm.monthly_budget = settings.monthly_budget
        self.llm.daily_budget = getattr(settings, 'daily_budget', 10.0)
        self.debug = settings.debug
        self.data_dir = settings.data_dir
        self.app_name = settings.app_name
        self.app_version = settings.app_version

async def test_updated_prompt():
    """Test the updated prompt system"""
    
    try:
        # Initialize client with wrapped config
        config_wrapper = ConfigWrapper(settings)
        client = LLMClient(config_wrapper)
        
        # Get prompt engine
        engine = get_prompt_engine()
        
        # Render treatment plan prompt
        prompt = engine.render_treatment_plan_prompt(
            diagnosis="ear pain",
            patient_age=5,
            severity_level="moderate"
        )
        
        print("Rendered prompt:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("\n" + "="*50 + "\n")
        
        # Generate treatment plan
        response = await client.generate_treatment_plan(
            diagnosis="ear pain",
            age=5,
            context="moderate severity",
            detail_level="detailed"
        )
        
        print("Response received!")
        print(f"Content length: {len(response.content)}")
        print(f"Content preview:\n{response.content[:300]}...")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(response.content)
            print(f"\\n✅ JSON parsed successfully!")
            print(f"Type: {type(parsed)}")
            if isinstance(parsed, dict):
                print(f"Keys: {list(parsed.keys())}")
                for key, value in parsed.items():
                    print(f"  {key}: {type(value)} = {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
            return True
        except Exception as e:
            print(f"\\n❌ JSON parsing failed: {e}")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_updated_prompt())
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")