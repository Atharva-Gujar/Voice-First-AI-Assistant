"""Audio output module for playing synthesized speech."""
import sounddevice as sd
import numpy as np
import threading
import queue
from typing import Optional
import config


class AudioOutput:
    """Handles audio playback with interrupt capability."""
    
    def __init__(self):
        self.is_playing = False
        self.should_stop = False
        self.playback_thread: Optional[threading.Thread] = None
        
    def play_audio(self, audio_data: bytes, sample_rate: int = 24000) -> None:
        """Play audio data with interrupt capability."""
        self.should_stop = False
        self.is_playing = True
        
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        def playback():
            try:
                sd.play(audio_array, samplerate=sample_rate)
                
                # Check for interrupts while playing
                while sd.get_stream().active and not self.should_stop:
                    sd.sleep(100)
                
                if self.should_stop:
                    sd.stop()
            finally:
                self.is_playing = False
        
        self.playback_thread = threading.Thread(target=playback)
        self.playback_thread.start()
    
    def play_streaming_audio(self, audio_stream) -> None:
        """Play audio from a streaming source."""
        self.should_stop = False
        self.is_playing = True
        
        def stream_playback():
            try:
                audio_queue = queue.Queue()
                
                def callback(outdata, frames, time, status):
                    if status:
                        print(f"Audio output status: {status}")
                    
                    if self.should_stop:
                        raise sd.CallbackStop()
                    
                    try:
                        data = audio_queue.get_nowait()
                        outdata[:len(data)] = data.reshape(-1, 1)
                    except queue.Empty:
                        outdata.fill(0)
                
                # Start output stream
                with sd.OutputStream(
                    samplerate=24000,
                    channels=1,
                    callback=callback,
                    dtype='int16'
                ):
                    # Feed audio chunks to queue
                    for chunk in audio_stream:
                        if self.should_stop:
                            break
                        audio_data = np.frombuffer(chunk, dtype=np.int16)
                        audio_queue.put(audio_data)
                    
                    # Wait for queue to empty
                    while not audio_queue.empty() and not self.should_stop:
                        sd.sleep(100)
                        
            finally:
                self.is_playing = False
        
        self.playback_thread = threading.Thread(target=stream_playback)
        self.playback_thread.start()
    
    def stop(self) -> None:
        """Stop current playback immediately."""
        self.should_stop = True
        sd.stop()
        
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
    
    def wait_until_done(self) -> None:
        """Wait until playback is complete."""
        if self.playback_thread:
            self.playback_thread.join()
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.stop()
