#!/usr/bin/env python3
"""Minimal test for LLM response"""

import asyncio
import json
from pediassist.llm.client import LLMClient
from pediassist.config import settings
from types import SimpleNamespace

class ConfigWrapper:
    def __init__(self, settings):
        self.llm = SimpleNamespace()
        self.llm.provider = settings.llm_provider
        self.llm.model = settings.model
        self.llm.temperature = settings.temperature
        self.llm.max_tokens = settings.max_tokens
        self.llm.monthly_budget = settings.monthly_budget
        self.llm.daily_budget = getattr(settings, 'daily_budget', 10.0)
        self.debug = settings.debug
        self.data_dir = settings.data_dir
        self.app_name = settings.app_name
        self.app_version = settings.app_version

async def minimal_test():
    """Minimal test to see if LLM responds at all"""
    
    try:
        # Initialize client with wrapper
        config = ConfigWrapper(settings)
        client = LLMClient(config)
        
        print("Client initialized successfully")
        
        # Try a very simple prompt first
        simple_prompt = "What is the treatment for ear pain in a 5 year old? Please respond with JSON format."
        
        print(f"Sending simple prompt: {simple_prompt}")
        
        # Use the underlying litellm directly for testing
        import litellm
        response = await litellm.acompletion(
            model=f"{config.llm.provider}/{config.llm.model}",
            messages=[{"role": "user", "content": simple_prompt}],
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens
        )
        
        print(f"Response received: {response}")
        
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"Content: {content}")
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print(f"JSON parsed successfully: {type(parsed)}")
                return True
            except Exception as e:
                print(f"JSON parsing failed: {e}")
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
    success = asyncio.run(minimal_test())
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")