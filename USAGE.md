# Voice-First AI Assistant - Usage Guide

## Quick Start

1. **Setup Environment**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure API Keys**
   Edit `.env` file:
   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Run Tests**
   ```bash
   source venv/bin/activate
   python test.py
   ```

4. **Start Assistant**
   ```bash
   python main.py
   ```

## Features

### 1. Real-Time Speech Recognition
- Uses Whisper for accurate transcription
- Voice Activity Detection (VAD) automatically detects when you start/stop speaking
- No need to press buttons - just speak naturally

### 2. Streaming Responses
- LLM generates responses token-by-token
- No waiting for complete response
- More natural conversation flow
- Lower latency

### 3. Interrupt Handling
- **Key Feature**: Speak anytime to interrupt the assistant
- Assistant stops talking immediately
- No need to wait for response to finish
- Natural back-and-forth conversation

### 4. Conversation Memory
- **Short-term**: Recent conversation context (20 messages)
- **Long-term**: Summarized history saved to disk
- Remembers context across sessions
- Use `clear` command to reset

## Commands

While the assistant is listening:

- **"quit" / "exit" / "goodbye"** - End the conversation
- **"clear"** - Clear conversation memory
- **Ctrl+C** - Force stop

## Architecture Overview

```
┌─────────────┐
│ Microphone  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Speech-to-Text  │ (Whisper)
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ Context Resolver │
│  + Memory        │
└──────┬───────────┘
       │
       ▼
┌─────────────────┐
│ LLM (Claude)    │ ─┐
└──────┬──────────┘  │ Streaming
       │              │
       ▼              │
┌─────────────────┐  │
│ Text-to-Speech  │◄─┘
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│  Speakers   │
└─────────────┘
```

## Configuration

Edit `.env` to customize:

```bash
# Audio Settings
SAMPLE_RATE=16000        # Audio sample rate
CHANNELS=1               # Mono audio

# Voice Activity Detection
VAD_AGGRESSIVENESS=3     # 0-3 (3 = most aggressive)

# Memory
MAX_SHORT_TERM_MESSAGES=20    # Messages before compression
MEMORY_FILE=conversation_memory.json
```

## Troubleshooting

### No audio detected
- Check microphone permissions
- Verify correct audio input device
- Lower VAD_AGGRESSIVENESS to 1 or 2
- Speak louder or closer to microphone

### Interrupt not working
- Ensure microphone is working during playback
- Speak clearly and loudly
- VAD might need tuning (adjust VAD_AGGRESSIVENESS)

### API errors
- Verify API keys in `.env`
- Check API key permissions
- Ensure internet connection

### Memory issues
- Check disk space
- Verify write permissions
- Delete `conversation_memory.json` to reset

## Performance Tips

1. **Lower latency**: Use faster internet connection
2. **Better recognition**: Use quality microphone in quiet environment
3. **Smoother interrupts**: Increase VAD_AGGRESSIVENESS
4. **Longer memory**: Increase MAX_SHORT_TERM_MESSAGES

## Advanced Usage

### Custom System Prompt
Edit `main.py` and modify the `system_prompt`:
```python
self.system_prompt = """Your custom instructions here"""
```

### Different TTS Voice
Modify the voice in `synthesizer.py`:
```python
# Available voices: alloy, echo, fable, onyx, nova, shimmer
self.tts.speak(text, voice="nova")
```

### Different LLM Model
Edit `llm/handler.py`:
```python
self.model = "claude-opus-4-20250514"  # or other models
```

## What Makes This Impressive

### 1. True Streaming
- Most voice assistants wait for complete responses
- This streams tokens as they're generated
- Much more natural conversation

### 2. Real Interrupt Handling
- Detects when user speaks during response
- Stops immediately (not just after sentence)
- Handles interruption gracefully

### 3. Conversation Memory
- Maintains context across sessions
- Automatic compression of old messages
- Persistent storage

### 4. Voice Activity Detection
- No button pressing needed
- Automatically detects speech start/end
- Natural conversation flow

## Next Steps

Try having a conversation and:
1. Interrupt the assistant mid-sentence
2. Ask follow-up questions
3. Reference something from earlier in the conversation
4. Exit and restart - it should remember your chat

## Milestone Achieved

✅ You can have a conversation  
✅ Interrupt it mid-sentence  
✅ It remembers context tomorrow  

This is the foundation for voice-first AI applications!
