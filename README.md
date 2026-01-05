# 🎤 Voice-First AI Assistant

A sophisticated voice-enabled AI assistant featuring real-time streaming responses, intelligent interrupt handling, and persistent conversation memory.

## ✨ Key Features

### 1. **Streaming Intelligence**
- Token-by-token LLM responses (Claude Sonnet 4)
- Real-time text-to-speech synthesis
- No waiting for complete responses

### 2. **Smart Interruption**
- Interrupt mid-sentence by speaking
- Assistant stops immediately
- Context preserved for follow-up

### 3. **Conversation Memory**
- **Short-term buffer**: Recent 10 messages in full detail
- **Long-term context**: Summarized older conversations
- Persistent memory across sessions
- Remembers context from previous days

### 4. **Push-to-Talk Interface**
- Hold SPACE to speak
- Release to process
- Natural conversation flow

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Microphone │────▶│ Whisper STT  │────▶│   Claude    │
└─────────────┘     └──────────────┘     │   Sonnet    │
                                          └──────┬──────┘
                                                 │
┌─────────────┐     ┌──────────────┐            │
│   Speaker   │◀────│  OpenAI TTS  │◀───────────┘
└─────────────┘     └──────────────┘

       ┌───────────────────────────────┐
       │    Conversation Memory        │
       │  ┌─────────────────────────┐  │
       │  │  Short-term (10 msgs)   │  │
       │  │  + timestamps, full text  │  │
       │  └─────────────────────────┘  │
       │  ┌─────────────────────────┐  │
       │  │  Long-term (summaries)  │  │
       │  │  + persistent storage   │  │
       │  └─────────────────────────┘  │
       └───────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Microphone and speakers
- Anthropic API key
- OpenAI API key

### Installation

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the setup wizard** (recommended):
   ```bash
   python setup_assistant.py
   ```
   
   Or manually create `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the assistant**:
   ```bash
   python main.py
   ```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `SPACE` (hold) | Start recording your voice |
| `SPACE` (release) | Stop recording and process |
| `ESC` | Exit the assistant |
| Say "goodbye" | End conversation |

## 📋 How It Works

### Conversation Flow

1. **User speaks** → Hold SPACE
2. **Audio captured** → Release SPACE
3. **Whisper transcription** → Fast and accurate
4. **Context building** → Adds to memory
5. **Claude processes** → Streaming response
6. **TTS synthesis** → Sentence-by-sentence
7. **Audio playback** → Real-time output

### Interruption Flow

1. **Assistant speaking** → Audio playing
2. **User presses SPACE** → Playback stops immediately
3. **User speaks** → New input captured
4. **Context preserved** → Continues conversation naturally

### Memory Management

**Short-term Memory (10 messages)**:
- Stores recent conversation in full detail
- Includes timestamps
- Used for immediate context

**Long-term Memory (Summaries)**:
- Automatically summarizes after 20 messages
- Keeps last 500 words of context
- Persists across sessions
- Stored in `conversation_memory.json`

## 🔧 Configuration

Edit `config.py` to customize:

```python
# LLM Settings
LLM_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# TTS Voice Options
TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer

# Memory Settings
SHORT_TERM_MEMORY_SIZE = 10
LONG_TERM_SUMMARY_THRESHOLD = 20
```

## 📁 Project Structure

```
Voice-First AI Assistant/
├── main.py                 # Main orchestrator
├── config.py              # Configuration
├── setup_assistant.py     # Setup wizard
│
├── audio/                 # Audio I/O
│   ├── __init__.py       # AudioInput class
│   └── output.py         # AudioOutput class
│
├── speech/               # Speech processing
│   ├── stt.py           # Whisper integration
│   └── tts.py           # OpenAI TTS
│
├── llm/                  # LLM integration
│   └── handler.py       # Claude streaming
│
├── memory/              # Memory management
│   └── manager.py       # Conversation memory
│
└── tests/               # Test suite
    └── test_memory.py
```

## 🧪 Testing

### Basic Tests
```bash
python test_components.py
```

Tests:
- ✓ Module imports
- ✓ Configuration
- ✓ Audio devices
- ✓ Memory system
- ✓ API connections (basic)

### Full API Tests
```bash
python test_components.py --full-test
```

⚠️ **Warning**: Uses API credits

## 💡 Usage Tips

### Best Practices
1. **Short responses**: Ask for brief answers for faster playback
2. **Natural speech**: Speak naturally, the system handles it
3. **Interruptions**: Don't hesitate to interrupt if needed
4. **Context**: Reference earlier topics - memory persists

### Example Conversations

**Simple query**:
```
You: "What's the weather like today?"
Assistant: "I don't have access to real-time weather data..."
```

**With context**:
```
You: "Tell me about Python"
Assistant: "Python is a high-level programming language..."

[Later]
You: "What are some good libraries for that?"
Assistant: "For Python, some popular libraries are..."
```

**Interruption**:
```
Assistant: "Python was created by Guido van Rossum in 1991..."
[You press SPACE]
Assistant: [Stops immediately]
You: "Actually, tell me about JavaScript instead"
```

## 🐛 Troubleshooting

### No audio input/output
```bash
# Test audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### API errors
- Check `.env` file has valid API keys
- Verify keys at:
  - Anthropic: https://console.anthropic.com/
  - OpenAI: https://platform.openai.com/api-keys

### Memory not persisting
- Check `conversation_memory.json` exists
- Verify write permissions in directory

### Slow responses
- Check internet connection
- Try shorter prompts
- Reduce `MAX_TOKENS` in config

## 🔒 Privacy & Security

- **API Keys**: Never commit `.env` to version control
- **Conversation Data**: Stored locally in `conversation_memory.json`
- **Audio**: Not stored - processed in memory only
- **API Calls**: Sent to Anthropic and OpenAI servers

## 🎯 What Makes This Impressive

### Technical Excellence

1. **True Streaming**
   - Token-level streaming from Claude
   - Sentence-level TTS synthesis
   - Parallel processing pipeline

2. **Intelligent Interruption**
   - Immediate response to user input
   - Clean state management
   - Context preservation

3. **Memory Architecture**
   - Two-tier memory system
   - Automatic summarization
   - Persistent storage
   - Efficient context retrieval

4. **Production-Ready**
   - Error handling
   - Resource cleanup
   - Logging system
   - Configuration management

### User Experience

- **Natural**: Feels like talking to a person
- **Responsive**: No artificial delays
- **Smart**: Remembers previous conversations
- **Reliable**: Handles edge cases gracefully

## 📚 API Documentation

### Memory Manager

```python
memory = ConversationMemory()

# Add messages
memory.add_message("user", "Hello")
memory.add_message("assistant", "Hi there!")

# Get context for LLM
messages = memory.get_messages_for_llm()
context = memory.get_long_term_context()
```

### LLM Handler

```python
llm = LLMHandler()

# Streaming response
for token in llm.generate_response_streaming(messages, context):
    print(token, end='', flush=True)

# Generate summary
summary = llm.generate_summary(messages)
```

### Audio Components

```python
# Input
audio_input = AudioInput()
audio_input.start_recording()
audio_data = audio_input.stop_recording()

# Output
audio_output = AudioOutput()
audio_output.play_audio(audio_bytes)
audio_output.stop()  # Interrupt
```

## 🚀 Future Enhancements

### Planned Features
- [ ] Voice Activity Detection for hands-free operation
- [ ] Multi-language support
- [ ] Custom wake word
- [ ] Conversation export
- [ ] Emotion detection in voice
- [ ] Background noise cancellation
- [ ] Mobile app version

### Performance Improvements
- [ ] Optimize memory usage
- [ ] Cache common responses
- [ ] Parallel TTS synthesis
- [ ] WebSocket streaming

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Voice activity detection
- Better interrupt detection
- Memory optimization
- UI improvements
- Documentation

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review test output
3. Check API status pages
4. Open an issue on GitHub


## 🌟 Milestone Achievement

You can now:
✅ Have a conversation with an AI assistant
✅ Interrupt it mid-sentence
✅ Have it remember context tomorrow
