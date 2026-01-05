"""
Interrupt Handler using Voice Activity Detection.
Detects when user speaks during assistant response.
"""

import asyncio
import numpy as np
import sounddevice as sd
import webrtcvad
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InterruptHandler:
    """Handles interruption detection using voice activity detection."""
    
    def __init__(self, config):
        self.config = config
        
        # VAD configuration
        self.vad = webrtcvad.Vad()
        self.vad_aggressiveness = config.get_int('VAD_AGGRESSIVENESS', 3)
        self.vad.set_mode(self.vad_aggressiveness)
        
        self.sample_rate = config.get_int('SAMPLE_RATE', 16000)
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        self.interrupted = False
        self.is_monitoring = False
        
        logger.info("InterruptHandler initialized")
    
    async def detect_speech(self) -> bool:
        """
        Detect if user is speaking.
        Returns True if speech detected, False otherwise.
        """
        try:
            # Record a short audio frame
            audio_frame = await self._capture_frame()
            
            if audio_frame is None:
                return False
            
            # Convert to bytes for VAD
            audio_bytes = (audio_frame * 32767).astype(np.int16).tobytes()
            
            # Check for speech
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
            
            return is_speech
            
        except Exception as e:
            logger.error(f"Error in detect_speech: {e}", exc_info=True)
            return False
    
    async def _capture_frame(self) -> np.ndarray:
        """Capture a single audio frame from microphone."""
        try:
            # Record audio frame
            audio_data = sd.rec(
                self.frame_size,
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            
            sd.wait()  # Wait for recording to complete
            
            return audio_data.flatten()
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}", exc_info=True)
            return None
    
    def trigger_interrupt(self):
        """Mark that an interruption has occurred."""
        self.interrupted = True
        logger.info("Interruption triggered")
    
    def was_interrupted(self) -> bool:
        """Check if interruption occurred."""
        return self.interrupted
    
    def reset(self):
        """Reset interrupt state."""
        self.interrupted = False
