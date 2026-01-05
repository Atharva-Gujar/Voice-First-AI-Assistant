"""
Memory Manager for conversation history.
Implements short-term buffer and long-term summarization.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import deque
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryManager:
    """Manages conversation memory with short-term and long-term storage."""
    
    def __init__(self, config):
        self.config = config
        
        # Short-term memory (full messages)
        self.short_term_size = config.get_int('SHORT_TERM_MEMORY_SIZE', 20)
        self.short_term_memory = deque(maxlen=self.short_term_size)
        
        # Long-term memory (summaries)
        self.long_term_memory = []
        self.summary_threshold = config.get_int('LONG_TERM_SUMMARY_THRESHOLD', 30)
        
        # Memory file path
        self.memory_file = Path.home() / '.voice_assistant' / 'memory.json'
        self.memory_file.parent.mkdir(exist_ok=True)
        
        # Load existing memory
        self._load_from_disk()
        
        logger.info("MemoryManager initialized")
    
    def add_message(self, role: str, content: str):
        """Add a message to memory."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.short_term_memory.append(message)
        
        # Check if we need to summarize
        if len(self.short_term_memory) >= self.summary_threshold:
            self._summarize_and_archive()
    
    def get_context(self) -> list:
        """
        Get conversation context for LLM.
        Returns messages formatted for LLM API.
        """
        context = []
        
        # Add long-term summary if exists
        if self.long_term_memory:
            summary = self._create_summary_message()
            context.append(summary)
        
        # Add recent short-term messages
        for msg in self.short_term_memory:
            context.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return context
    
    def _create_summary_message(self) -> dict:
        """Create a system message with conversation summary."""
        summary_text = "Previous conversation summary:\n"
        
        for summary in self.long_term_memory[-3:]:  # Last 3 summaries
            summary_text += f"- {summary['summary']}\n"
        
        return {
            "role": "system",
            "content": summary_text
        }
    
    def _summarize_and_archive(self):
        """Summarize old messages and move to long-term memory."""
        # Take first half of short-term memory to summarize
        messages_to_summarize = list(self.short_term_memory)[:self.short_term_size // 2]
        
        # Create simple summary
        summary = self._generate_summary(messages_to_summarize)
        
        # Store in long-term memory
        self.long_term_memory.append({
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "message_count": len(messages_to_summarize)
        })
        
        # Remove summarized messages from short-term
        for _ in range(len(messages_to_summarize)):
            if self.short_term_memory:
                self.short_term_memory.popleft()
        
        logger.info(f"Archived {len(messages_to_summarize)} messages to long-term memory")
    
    def _generate_summary(self, messages: list) -> str:
        """Generate a summary of messages."""
        # Simple extractive summary
        # In production, could use LLM for better summaries
        
        topics = []
        for msg in messages:
            if msg["role"] == "user":
                # Extract key phrases (simple approach)
                content = msg["content"][:100]  # First 100 chars
                topics.append(content)
        
        if not topics:
            return "General conversation"
        
        return f"Discussion about: {', '.join(topics[:3])}"
    
    def clear_memory(self):
        """Clear all memory."""
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        logger.info("Memory cleared")
    
    def _load_from_disk(self):
        """Load memory from disk."""
        if not self.memory_file.exists():
            return
        
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
                
                self.long_term_memory = data.get('long_term', [])
                
                # Load recent short-term messages
                recent_messages = data.get('short_term', [])
                self.short_term_memory.extend(recent_messages[-10:])  # Last 10
                
                logger.info("Loaded memory from disk")
                
        except Exception as e:
            logger.error(f"Error loading memory: {e}", exc_info=True)
    
    def save_to_disk(self):
        """Save memory to disk."""
        try:
            data = {
                'short_term': list(self.short_term_memory),
                'long_term': self.long_term_memory,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info("Saved memory to disk")
            
        except Exception as e:
            logger.error(f"Error saving memory: {e}", exc_info=True)
    
    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            'short_term_count': len(self.short_term_memory),
            'long_term_count': len(self.long_term_memory),
            'total_messages': sum(s['message_count'] for s in self.long_term_memory) + len(self.short_term_memory)
        }
