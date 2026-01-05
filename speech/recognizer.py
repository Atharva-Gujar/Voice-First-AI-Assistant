"""
Speech Recognition Module
Handles real-time microphone input and Whisper-based speech-to-text conversion
"""

import sounddevice as sd
import numpy as np
import queue
import threading
from openai import OpenAI
import os
from dotenv import load_dotenv
import webrtcvad
import collections
import wave
import tempfile

load_dotenv()


class SpeechRecognizer:
    def __init__(self, sample_rate=16000, chunk_duration_ms=30):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        
        # Voice Activity Detection
        self.vad = webrtcvad.Vad(int(os.getenv('VAD_AGGRESSIVENESS', 3)))
        
        # Audio buffers
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.stream = None
        
        # Ring buffer for VAD
        self.ring_buffer = collections.deque(maxlen=50)
        self.triggered = False
        self.voiced_frames = []
        
        # Speech detection parameters
        self.num_padding_frames = 10
        self.num_window_frames = 10
        self.ratio = 0.75
        
    def start_listening(self):
        """Start listening to microphone input"""
        self.is_listening = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            if self.is_listening:
                self.audio_queue.put(bytes(indata))
        
        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            dtype='int16',
            channels=1,
            callback=audio_callback
        )
        self.stream.start()
        print("🎤 Listening...")
        
    def stop_listening(self):
        """Stop listening to microphone input"""
        self.is_listening = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        print("🛑 Stopped listening")
        
    def detect_speech(self, timeout=10):
        """
        Detect speech using VAD and return when speech ends
        Returns: audio data (bytes) or None if timeout
        """
        num_voiced = 0
        num_unvoiced = 0
        
        start_time = threading.Timer(timeout, lambda: None)
        start_time.start()
        
        while self.is_listening:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                
                # Check if chunk contains voice
                is_speech = self.vad.is_speech(chunk, self.sample_rate)
                
                if not self.triggered:
                    self.ring_buffer.append((chunk, is_speech))
                    num_voiced = len([f for f, speech in self.ring_buffer if speech])
                    
                    if num_voiced > self.ratio * self.ring_buffer.maxlen:
                        self.triggered = True
                        print("🗣️  Speech detected")
                        # Add buffered audio
                        for frame, _ in self.ring_buffer:
                            self.voiced_frames.append(frame)
                        self.ring_buffer.clear()
                else:
                    self.voiced_frames.append(chunk)
                    self.ring_buffer.append((chunk, is_speech))
                    num_unvoiced = len([f for f, speech in self.ring_buffer if not speech])
                    
                    if num_unvoiced > self.ratio * self.ring_buffer.maxlen:
                        self.triggered = False
                        print("🔇 Speech ended")
                        audio_data = b''.join(self.voiced_frames)
                        self.voiced_frames = []
                        self.ring_buffer.clear()
                        return audio_data
                        
            except queue.Empty:
                continue
                
        return None
        
    def transcribe(self, audio_data):
        """
        Transcribe audio data using Whisper
        """
        if not audio_data:
            return ""
            
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_path = temp_audio.name
            
            # Write WAV file
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
        
        try:
            # Transcribe with Whisper
            with open(temp_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            return transcript.text
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    def listen_and_transcribe(self):
        """
        Main method: listen for speech and transcribe it
        Returns the transcribed text
        """
        audio_data = self.detect_speech()
        if audio_data:
            text = self.transcribe(audio_data)
            return text
        return ""
