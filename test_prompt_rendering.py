#!/usr/bin/env python3
"""Test prompt rendering without LLM call"""

from pediassist.llm.prompts import get_prompt_engine

def test_prompt_rendering():
    """Test if prompts render correctly"""
    
    try:
        engine = get_prompt_engine()
        
        # Test treatment plan prompt rendering
        prompt = engine.build_treatment_prompt(
            diagnosis='ear pain',
            age=5,
            detail_level='detailed'
        )
        
        print("Prompt rendered successfully!")
        print(f"Prompt length: {len(prompt)} characters")
        print("\nPrompt preview (first 500 chars):")
        print(prompt[:500])
        
        # Check for template issues
        if '{' in prompt and '}' in prompt:
            print("\n⚠️  Warning: Found unescaped braces in prompt")
            # Find lines with braces
            lines = prompt.split('\n')
            for i, line in enumerate(lines):
                if '{' in line or '}' in line:
                    print(f"Line {i+1}: {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"Prompt rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prompt_rendering()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")