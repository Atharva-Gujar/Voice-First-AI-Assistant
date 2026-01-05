"""Test script to verify all components work individually."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from audio import AudioInput
        from audio.output import AudioOutput
        from speech.stt import SpeechToText
        from speech.tts import TextToSpeech
        from llm.handler import LLMHandler
        from memory.manager import ConversationMemory
        import config
        print("✓ All imports successful\n")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}\n")
        return False

def test_config():
    """Test configuration."""
    print("Testing configuration...")
    try:
        import config
        
        # Check API keys
        if not config.ANTHROPIC_API_KEY:
            print("✗ ANTHROPIC_API_KEY not set")
            return False
        if not config.OPENAI_API_KEY:
            print("✗ OPENAI_API_KEY not set")
            return False
            
        print(f"✓ Configuration loaded")
        print(f"  - Whisper model: {config.WHISPER_MODEL}")
        print(f"  - TTS voice: {config.TTS_VOICE}")
        print(f"  - LLM model: {config.LLM_MODEL}\n")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}\n")
        return False

def test_audio_devices():
    """Test audio device availability."""
    print("Testing audio devices...")
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        print(f"✓ Found {len(devices)} audio devices")
        
        # Show default devices
        default_in = sd.query_devices(kind='input')
        default_out = sd.query_devices(kind='output')
        print(f"  - Default input: {default_in['name']}")
        print(f"  - Default output: {default_out['name']}\n")
        return True
    except Exception as e:
        print(f"✗ Audio device error: {e}\n")
        return False

def test_memory():
    """Test memory system."""
    print("Testing memory system...")
    try:
        from memory.manager import ConversationMemory
        
        mem = ConversationMemory()
        mem.add_message("user", "Test message")
        mem.add_message("assistant", "Test response")
        
        messages = mem.get_messages_for_llm()
        assert len(messages) >= 2
        
        print(f"✓ Memory system working")
        print(f"  - Short-term messages: {len(mem.short_term_messages)}")
        print(f"  - Message count: {mem.message_count}\n")
        return True
    except Exception as e:
        print(f"✗ Memory error: {e}\n")
        return False

def test_llm():
    """Test LLM connection (optional, costs API credits)."""
    print("Testing LLM connection (basic)...")
    try:
        from llm.handler import LLMHandler
        
        llm = LLMHandler()
        print("✓ LLM handler initialized")
        print("  Note: Run with --full-test to test API calls\n")
        return True
    except Exception as e:
        print(f"✗ LLM error: {e}\n")
        return False

def test_tts():
    """Test TTS connection (optional, costs API credits)."""
    print("Testing TTS connection (basic)...")
    try:
        from speech.tts import TextToSpeech
        
        tts = TextToSpeech()
        print("✓ TTS handler initialized")
        print("  Note: Run with --full-test to test API calls\n")
        return True
    except Exception as e:
        print(f"✗ TTS error: {e}\n")
        return False

def run_full_tests():
    """Run full API tests (costs credits)."""
    print("\n" + "="*60)
    print("FULL API TESTS (will use API credits)")
    print("="*60 + "\n")
    
    # Test TTS
    print("Testing TTS API...")
    try:
        from speech.tts import TextToSpeech
        tts = TextToSpeech()
        audio = tts.synthesize("This is a test.")
        assert len(audio) > 0
        print("✓ TTS API working\n")
    except Exception as e:
        print(f"✗ TTS API error: {e}\n")
    
    # Test LLM
    print("Testing LLM API...")
    try:
        from llm.handler import LLMHandler
        llm = LLMHandler()
        response = llm.generate_response([
            {"role": "user", "content": "Say 'test' if you can hear me."}
        ])
        assert len(response) > 0
        print(f"✓ LLM API working")
        print(f"  Response: {response[:100]}...\n")
    except Exception as e:
        print(f"✗ LLM API error: {e}\n")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Voice-First AI Assistant - Component Tests")
    print("="*60 + "\n")
    
    tests = [
        test_imports,
        test_config,
        test_audio_devices,
        test_memory,
        test_llm,
        test_tts,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All basic tests passed!")
        print("\nYou're ready to run: python main.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
    
    print("="*60)
    
    # Check for full test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--full-test":
        run_full_tests()
    else:
        print("\nTo test API connections (costs credits), run:")
        print("  python test_components.py --full-test\n")


if __name__ == "__main__":
    main()
