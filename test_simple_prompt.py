#!/usr/bin/env python3
"""Test simplified prompt with LLM"""

import asyncio
import json
from simple_prompts import get_simple_prompt_engine
from pediassist.llm.client import LLMClient
from pediassist.config import settings
from types import SimpleNamespace

class ConfigWrapper:
    def __init__(self, settings):
        self.llm = SimpleNamespace()
        self.llm.provider = settings.llm_provider
        self.llm.model = settings.model
        self.llm.temperature = settings.temperature
        self.llm.max_tokens = 1000  # Reasonable limit
        self.llm.monthly_budget = settings.monthly_budget
        self.llm.daily_budget = getattr(settings, 'daily_budget', 10.0)
        self.debug = settings.debug
        self.data_dir = settings.data_dir
        self.app_name = settings.app_name
        self.app_version = settings.app_version

async def test_simple_prompt():
    """Test simplified prompt with LLM"""
    
    try:
        # Get simple prompt
        engine = get_simple_prompt_engine()
        prompt = engine.build_simple_treatment_prompt("ear pain", 5)
        
        print("Using simplified prompt:")
        print(prompt)
        print("\n" + "="*50 + "\n")
        
        # Use litellm directly for testing
        import litellm
        response = await litellm.acompletion(
            model=f"{settings.llm_provider}/{settings.model}",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        print("Response received!")
        
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"Content length: {len(content)}")
            print(f"Content:\n{content}")
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
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
        else:
            print("No response content")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_prompt())
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")