"""Text-to-speech module using OpenAI TTS."""
from openai import OpenAI
from typing import Iterator
import config


class TextToSpeech:
    """Handles text-to-speech synthesis."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        if not text:
            return b""
        
        try:
            response = self.client.audio.speech.create(
                model=config.TTS_MODEL,
                voice=config.TTS_VOICE,
                input=text,
                speed=config.TTS_SPEED
            )
            
            return response.content
            
        except Exception as e:
            print(f"TTS error: {e}")
            return b""
    
    def synthesize_streaming(self, text_stream: Iterator[str]) -> Iterator[bytes]:
        """
        Synthesize speech from streaming text tokens.
        Buffers tokens into sentences for natural speech.
        
        Args:
            text_stream: Iterator of text tokens
            
        Yields:
            Audio chunks as bytes
        """
        buffer = ""
        sentence_endings = {'.', '!', '?', '\n'}
        
        try:
            for token in text_stream:
                buffer += token
                
                # Check if we have a complete sentence
                if any(buffer.rstrip().endswith(end) for end in sentence_endings):
                    # Synthesize the complete sentence
                    if buffer.strip():
                        audio = self.synthesize(buffer.strip())
                        if audio:
                            yield audio
                    buffer = ""
            
            # Synthesize any remaining text
            if buffer.strip():
                audio = self.synthesize(buffer.strip())
                if audio:
                    yield audio
                    
        except Exception as e:
            print(f"Streaming TTS error: {e}")
