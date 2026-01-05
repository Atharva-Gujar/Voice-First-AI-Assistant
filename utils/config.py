"""Configuration management."""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for the voice assistant."""
    
    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        self._config = {}
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load all environment variables."""
        self._config = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
            'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'openai'),
            'LLM_MODEL': os.getenv('LLM_MODEL', 'gpt-4-turbo-preview'),
            'STT_MODEL': os.getenv('STT_MODEL', 'whisper-1'),
            'TTS_PROVIDER': os.getenv('TTS_PROVIDER', 'openai'),
            'TTS_VOICE': os.getenv('TTS_VOICE', 'alloy'),
            'SAMPLE_RATE': os.getenv('SAMPLE_RATE', '16000'),
            'CHANNELS': os.getenv('CHANNELS', '1'),
            'CHUNK_SIZE': os.getenv('CHUNK_SIZE', '1024'),
            'SHORT_TERM_MEMORY_SIZE': os.getenv('SHORT_TERM_MEMORY_SIZE', '20'),
            'LONG_TERM_SUMMARY_THRESHOLD': os.getenv('LONG_TERM_SUMMARY_THRESHOLD', '30'),
            'VAD_AGGRESSIVENESS': os.getenv('VAD_AGGRESSIVENESS', '3'),
            'SILENCE_THRESHOLD': os.getenv('SILENCE_THRESHOLD', '500'),
        }
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self._config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get configuration value as integer."""
        value = self._config.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get configuration value as float."""
        value = self._config.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get configuration value as boolean."""
        value = self._config.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'on')
