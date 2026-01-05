"""
Text-to-Speech Module
Handles streaming text-to-speech synthesis with interrupt capability
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import threading
import queue
import io

load_dotenv()


class TextToSpeech:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.is_playing = False
        self.should_stop = False
        self.audio_queue = queue.Queue()
        self.playback_thread = None
        
    def synthesize_streaming(self, text, voice="alloy"):
        """
        Synthesize text to speech with streaming
        voice options: alloy, echo, fable, onyx, nova, shimmer
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="pcm"
            )
            
            return response.content
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
            
    def play_audio(self, audio_data, sample_rate=24000):
        """Play audio data with interrupt capability"""
        if not audio_data:
            return
            
        self.is_playing = True
        self.should_stop = False
        
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        def playback():
            try:
                sd.play(audio_array, sample_rate, blocking=False)
                while sd.get_stream().active and not self.should_stop:
                    sd.sleep(100)
                if self.should_stop:
                    sd.stop()
            finally:
                self.is_playing = False
                
        self.playback_thread = threading.Thread(target=playback)
        self.playback_thread.start()
        
    def stop(self):
        """Stop current playback"""
        self.should_stop = True
        if self.playback_thread:
            self.playback_thread.join(timeout=1)
        sd.stop()
        self.is_playing = False
        print("⏸️  Audio stopped")
        
    def speak(self, text, voice="alloy"):
        """
        Complete speak method: synthesize and play
        """
        print(f"🔊 Speaking: {text[:50]}...")
        audio_data = self.synthesize_streaming(text, voice)
        if audio_data:
            self.play_audio(audio_data)
            # Wait for playback to complete
            if self.playback_thread:
                self.playback_thread.join()
