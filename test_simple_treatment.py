#!/usr/bin/env python3
"""Test with shorter timeout and simpler approach"""

import asyncio
import json
import signal
import sys
from pediassist.llm.client import LLMClient
from pediassist.config import settings
from types import SimpleNamespace

class ConfigWrapper:
    def __init__(self, settings):
        self.llm = SimpleNamespace()
        self.llm.provider = settings.llm_provider
        self.llm.model = settings.model
        self.llm.temperature = settings.temperature
        self.llm.max_tokens = 500  # Reduced max tokens
        self.llm.monthly_budget = settings.monthly_budget
        self.llm.daily_budget = getattr(settings, 'daily_budget', 10.0)
        self.debug = settings.debug
        self.data_dir = settings.data_dir
        self.app_name = settings.app_name
        self.app_version = settings.app_version

def timeout_handler(signum, frame):
    print("Test timed out after 15 seconds")
    sys.exit(1)

async def test_simple_treatment():
    """Test with simpler parameters"""
    
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(15)
    
    try:
        # Initialize client with wrapper
        config = ConfigWrapper(settings)
        client = LLMClient(config)
        
        print("Client initialized successfully")
        
        # Test with simpler parameters
        response = await client.generate_treatment_plan(
            'ear pain', 
            5, 
            detail_level='quick'  # Use quick instead of detailed
        )
        
        print(f"Response received. Type: {type(response)}")
        print(f"Content length: {len(response.content) if hasattr(response, 'content') else 'No content'}")
        
        if hasattr(response, 'content') and response.content:
            print(f"Content preview (first 300 chars):")
            print(response.content[:300])
            
            # Try to parse as JSON
            try:
                parsed = json.loads(response.content) if isinstance(response.content, str) else response.content
                print(f"\\nSuccessfully parsed JSON: {type(parsed)}")
                if isinstance(parsed, dict):
                    print(f"Keys: {list(parsed.keys())}")
                    return True
                else:
                    print("Parsed content is not a dictionary")
                    return False
            except Exception as e:
                print(f"\\nJSON parsing failed: {e}")
                return False
        else:
            print("No content in response")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        signal.alarm(0)  # Cancel timeout

if __name__ == "__main__":
    success = asyncio.run(test_simple_treatment())
    sys.exit(0 if success else 1)