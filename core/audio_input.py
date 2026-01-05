"""
Audio input handling with Whisper-based Speech-to-Text.
Captures microphone input and converts to text.
"""

import asyncio
import numpy as np
import sounddevice as sd
from openai import OpenAI
import io
from scipy.io import wavfile
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioInput:
    """Handles microphone input and speech-to-text conversion."""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.get('OPENAI_API_KEY'))
        
        self.sample_rate = config.get_int('SAMPLE_RATE', 16000)
        self.channels = config.get_int('CHANNELS', 1)
        self.chunk_size = config.get_int('CHUNK_SIZE', 1024)
        
        self.is_recording = False
        self.audio_buffer = []
        
        logger.info("AudioInput initialized")
    
    async def listen(self) -> str:
        """
        Listen for speech input and convert to text.
        Returns the transcribed text or empty string if no speech detected.
        """
        try:
            # Record audio with voice activity detection
            audio_data = await self._record_with_vad()
            
            if audio_data is None or len(audio_data) == 0:
                return ""
            
            # Convert to WAV format for Whisper
            wav_buffer = self._to_wav_buffer(audio_data)
            
            # Transcribe with Whisper
            text = await self._transcribe(wav_buffer)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in listen: {e}", exc_info=True)
            return ""
    
    async def _record_with_vad(self) -> np.ndarray:
        """Record audio with voice activity detection."""
        self.audio_buffer = []
        self.is_recording = True
        
        silence_threshold = self.config.get_int('SILENCE_THRESHOLD', 500)
        silence_duration = 0
        has_speech = False
        
        def audio_callback(indata, frames, time_info, status):
            """Callback for audio stream."""
            if status:
                logger.warning(f"Audio callback status: {status}")
            
            # Add to buffer
            self.audio_buffer.append(indata.copy())
        
        # Start recording stream
        with sd.InputStream(callback=audio_callback,
                          channels=self.channels,
                          samplerate=self.sample_rate,
                          blocksize=self.chunk_size):
            
            # Monitor for speech and silence
            while self.is_recording:
                await asyncio.sleep(0.1)
                
                # Check if we have audio
                if len(self.audio_buffer) > 0:
                    # Simple energy-based VAD
                    recent_chunk = self.audio_buffer[-1]
                    energy = np.sum(recent_chunk ** 2) / len(recent_chunk)
                    
                    if energy > 0.01:  # Speech detected
                        has_speech = True
                        silence_duration = 0
                    elif has_speech:  # Silence after speech
                        silence_duration += 100  # 100ms per check
                        
                        if silence_duration >= silence_threshold:
                            self.is_recording = False
                            break
                
                # Timeout after 30 seconds
                if len(self.audio_buffer) * 0.1 > 30:
                    self.is_recording = False
                    break
        
        # Combine audio chunks
        if len(self.audio_buffer) > 0:
            return np.concatenate(self.audio_buffer, axis=0)
        return None
    
    def _to_wav_buffer(self, audio_data: np.ndarray) -> io.BytesIO:
        """Convert numpy array to WAV file buffer."""
        buffer = io.BytesIO()
        
        # Normalize to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Write WAV file to buffer
        wavfile.write(buffer, self.sample_rate, audio_int16)
        buffer.seek(0)
        
        return buffer
    
    async def _transcribe(self, audio_buffer: io.BytesIO) -> str:
        """Transcribe audio using Whisper API."""
        try:
            # Prepare the audio file
            audio_buffer.name = "audio.wav"
            
            # Call Whisper API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.audio.transcriptions.create(
                    model=self.config.get('STT_MODEL', 'whisper-1'),
                    file=audio_buffer,
                    language="en"
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return ""
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_recording = False
        logger.info("AudioInput cleanup completed")
