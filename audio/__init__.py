"""Audio input module for capturing microphone audio."""
import sounddevice as sd
import numpy as np
import queue
import threading
from typing import Callable, Optional
import config


class AudioInput:
    """Handles microphone input with push-to-talk functionality."""
    
    def __init__(self):
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None
        self.recorded_frames = []
        
    def start_recording(self) -> None:
        """Start recording audio from microphone."""
        self.is_recording = True
        self.recorded_frames = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio input status: {status}")
            if self.is_recording:
                self.audio_queue.put(indata.copy())
        
        self.stream = sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype=config.AUDIO_FORMAT,
            callback=audio_callback,
            blocksize=config.CHUNK_SIZE
        )
        self.stream.start()
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return the audio data."""
        self.is_recording = False
        
        # Collect all recorded frames
        while not self.audio_queue.empty():
            self.recorded_frames.append(self.audio_queue.get())
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        if not self.recorded_frames:
            return np.array([], dtype=config.AUDIO_FORMAT)
        
        # Concatenate all frames
        audio_data = np.concatenate(self.recorded_frames, axis=0)
        return audio_data
    
    def get_audio_level(self) -> float:
        """Get current audio level for interrupt detection."""
        if not self.audio_queue.empty():
            data = self.audio_queue.get()
            return np.abs(data).mean()
        return 0.0
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
