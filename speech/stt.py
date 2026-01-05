"""Speech-to-text module using OpenAI Whisper."""
import io
import numpy as np
from openai import OpenAI
import soundfile as sf
import config


class SpeechToText:
    """Handles speech recognition using Whisper API."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: NumPy array of audio samples
            
        Returns:
            Transcribed text
        """
        if len(audio_data) == 0:
            return ""
        
        # Convert numpy array to audio file in memory
        audio_buffer = io.BytesIO()
        sf.write(
            audio_buffer,
            audio_data,
            config.SAMPLE_RATE,
            format='WAV',
            subtype='PCM_16'
        )
        audio_buffer.seek(0)
        audio_buffer.name = "audio.wav"
        
        try:
            # Call Whisper API
            transcript = self.client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_buffer,
                language=config.STT_LANGUAGE
            )
            
            return transcript.text.strip()
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def transcribe_streaming(self, audio_stream):
        """
        Transcribe streaming audio (future enhancement).
        Currently processes complete audio chunks.
        """
        # This is a placeholder for future streaming implementation
        # Whisper API doesn't support true streaming yet
        pass
