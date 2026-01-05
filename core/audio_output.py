"""
Audio output handling with Text-to-Speech.
Supports streaming TTS for real-time response.
"""

import asyncio
import io
from openai import OpenAI
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioOutput:
    """Handles text-to-speech conversion and audio playback."""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.get('OPENAI_API_KEY'))
        
        self.tts_provider = config.get('TTS_PROVIDER', 'openai')
        self.tts_voice = config.get('TTS_VOICE', 'alloy')
        
        self.text_buffer = ""
        self.audio_queue = asyncio.Queue()
        self.is_playing = False
        self.should_stop = False
        
        logger.info("AudioOutput initialized")
    
    async def speak_token(self, token: str):
        """
        Add token to speech buffer. 
        Converts to speech when buffer reaches sentence boundary.
        """
        self.text_buffer += token
        
        # Check for sentence boundaries
        if any(char in token for char in '.!?\n'):
            # We have a complete sentence, convert to speech
            await self._convert_and_play(self.text_buffer)
            self.text_buffer = ""
    
    async def finish(self):
        """Speak any remaining text in buffer."""
        if self.text_buffer.strip():
            await self._convert_and_play(self.text_buffer)
            self.text_buffer = ""
        
        # Wait for all audio to finish playing
        while not self.audio_queue.empty():
            await asyncio.sleep(0.1)
    
    async def stop(self):
        """Stop current playback immediately."""
        self.should_stop = True
        
        # Clear queues
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self.text_buffer = ""
        await asyncio.sleep(0.2)  # Let audio stop
        self.should_stop = False
    
    async def _convert_and_play(self, text: str):
        """Convert text to speech and play audio."""
        if not text.strip():
            return
        
        try:
            # Generate speech
            audio_data = await self._text_to_speech(text)
            
            # Play audio
            await self._play_audio(audio_data)
            
        except Exception as e:
            logger.error(f"Error in speak: {e}", exc_info=True)
    
    async def _text_to_speech(self, text: str) -> np.ndarray:
        """Convert text to speech audio."""
        loop = asyncio.get_event_loop()
        
        # Call OpenAI TTS API
        response = await loop.run_in_executor(
            None,
            lambda: self.client.audio.speech.create(
                model="tts-1",
                voice=self.tts_voice,
                input=text
            )
        )
        
        # Convert to numpy array for playback
        audio_bytes = response.content
        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        
        # Convert to numpy array
        samples = np.array(audio_segment.get_array_of_samples())
        
        # Reshape for channels
        if audio_segment.channels == 2:
            samples = samples.reshape((-1, 2))
        
        # Normalize
        samples = samples.astype(np.float32) / 32768.0
        
        return samples
    
    async def _play_audio(self, audio_data: np.ndarray):
        """Play audio data through speakers."""
        if self.should_stop:
            return
        
        self.is_playing = True
        
        try:
            # Play audio
            sd.play(audio_data, samplerate=24000)  # OpenAI TTS uses 24kHz
            
            # Wait for playback to complete or interruption
            while sd.get_stream().active and not self.should_stop:
                await asyncio.sleep(0.1)
            
            if self.should_stop:
                sd.stop()
                
        except Exception as e:
            logger.error(f"Playback error: {e}", exc_info=True)
        finally:
            self.is_playing = False
    
    def cleanup(self):
        """Cleanup resources."""
        sd.stop()
        logger.info("AudioOutput cleanup completed")
