import sys
import os

# Add the parent directory to the Python path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ai_cv import GeminiAI

def test_gemini_initialization():
    """Test if GeminiAI can be initialized properly"""
    try:
        ai = GeminiAI()
        print("✓ GeminiAI initialization successful")
        return ai
    except Exception as e:
        print(f"✗ GeminiAI initialization failed: {e}")
        return None

def test_text_generation(ai, prompt):
    """Test text generation with a given prompt"""
    print(f"\nTesting prompt: '{prompt}'")
    try:
        response = ai.generate_text(prompt)
        if response:
            print(f"✓ Response generated successfully:")
            print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            return True
        else:
            print("✗ No response generated")
            return False
    except Exception as e:
        print(f"✗ Text generation failed: {e}")
        return False

def main():
    print("=== GeminiAI Test Program ===\n")
    
    # Test initialization
    ai = test_gemini_initialization()
    if not ai:
        print("Cannot proceed with tests due to initialization failure")
        return
    
    # Test prompts
    test_prompts = [
        "Viết một câu chào ngắn gọn",
        "What is artificial intelligence?",
        "Tạo một mô tả ngắn về Python programming language"
    ]
    
    successful_tests = 0
    total_tests = len(test_prompts)
    
    for prompt in test_prompts:
        if test_text_generation(ai, prompt):
            successful_tests += 1
    
    print(f"\n=== Test Results ===")
    print(f"Successful tests: {successful_tests}/{total_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    main()
