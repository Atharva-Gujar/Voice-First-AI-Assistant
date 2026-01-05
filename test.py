"""
Test script for Voice-First AI Assistant components
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from speech import SpeechRecognizer, TextToSpeech
        from llm import LLMHandler
        from memory import ConversationMemory
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_api_keys():
    """Test that API keys are configured"""
    print("\nTesting API keys...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not openai_key or openai_key == 'your_openai_key_here':
        print("❌ OPENAI_API_KEY not configured")
        return False
    else:
        print(f"✅ OPENAI_API_KEY configured ({openai_key[:8]}...)")
        
    if not anthropic_key or anthropic_key == 'your_anthropic_key_here':
        print("❌ ANTHROPIC_API_KEY not configured")
        return False
    else:
        print(f"✅ ANTHROPIC_API_KEY configured ({anthropic_key[:8]}...)")
        
    return True


def test_memory():
    """Test conversation memory"""
    print("\nTesting conversation memory...")
    try:
        from memory import ConversationMemory
        
        memory = ConversationMemory(memory_file="test_memory.json")
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")
        
        context = memory.get_context()
        assert len(context) >= 2
        
        memory.clear_all()
        
        print("✅ Memory system working")
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def test_llm():
    """Test LLM handler"""
    print("\nTesting LLM handler...")
    try:
        from llm import LLMHandler
        
        llm = LLMHandler()
        messages = [{"role": "user", "content": "Say 'test successful' and nothing else"}]
        
        response = llm.generate_complete_response(messages)
        
        if response:
            print(f"✅ LLM response: {response[:50]}...")
            return True
        else:
            print("❌ No response from LLM")
            return False
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def main():
    print("="*60)
    print("VOICE-FIRST AI ASSISTANT - TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("API Keys", test_api_keys()))
    results.append(("Memory", test_memory()))
    results.append(("LLM", test_llm()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        
    print("="*60)
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
