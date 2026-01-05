"""
Utility functions for the Voice Assistant
"""

import time
from datetime import datetime


def format_timestamp():
    """Return formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_speaking_time(text, words_per_minute=150):
    """
    Estimate speaking time for given text
    
    Args:
        text: Text to speak
        words_per_minute: Average speaking rate
        
    Returns:
        Estimated time in seconds
    """
    word_count = len(text.split())
    return (word_count / words_per_minute) * 60


def chunk_text(text, max_length=500):
    """
    Split text into chunks for streaming TTS
    
    Args:
        text: Text to split
        max_length: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


class Timer:
    """Simple timer utility"""
    def __init__(self):
        self.start_time = None
        
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        
    def elapsed(self):
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time
        
    def stop(self):
        """Stop timer and return elapsed time"""
        elapsed = self.elapsed()
        self.start_time = None
        return elapsed
