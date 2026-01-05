import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Audio Settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
AUDIO_FORMAT = "float32"  # sounddevice uses float32 by default

# Speech Recognition
WHISPER_MODEL = "whisper-1"
STT_LANGUAGE = "en"

# Text-to-Speech
TTS_MODEL = "tts-1"
TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
TTS_SPEED = 1.0

# LLM Settings
LLM_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Memory Settings
SHORT_TERM_MEMORY_SIZE = 10  # Number of recent messages to keep
LONG_TERM_SUMMARY_THRESHOLD = 20  # Summarize after this many messages

# Interrupt Settings
INTERRUPT_SILENCE_THRESHOLD = 0.02  # Audio amplitude threshold for voice detection
INTERRUPT_MIN_DURATION = 0.3  # Minimum speech duration to trigger interrupt (seconds)

# File Paths
MEMORY_FILE = "conversation_memory.json"
