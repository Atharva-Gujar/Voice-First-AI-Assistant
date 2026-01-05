"""Conversation memory management module."""
import json
from typing import List, Dict, Optional
from datetime import datetime
import config


class ConversationMemory:
    """Manages short-term and long-term conversation memory."""
    
    def __init__(self, memory_file: str = config.MEMORY_FILE):
        self.memory_file = memory_file
        self.short_term_messages: List[Dict[str, str]] = []
        self.long_term_context: str = ""
        self.message_count = 0
        self.load_memory()
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to short-term memory.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.short_term_messages.append(message)
        self.message_count += 1
        
        # Trim short-term memory if it exceeds the limit
        if len(self.short_term_messages) > config.SHORT_TERM_MEMORY_SIZE:
            self.short_term_messages = self.short_term_messages[-config.SHORT_TERM_MEMORY_SIZE:]
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """
        Get messages formatted for LLM (without timestamps).
        
        Returns:
            List of messages with role and content
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.short_term_messages
        ]
    
    def get_long_term_context(self) -> Optional[str]:
        """
        Get long-term context summary.
        
        Returns:
            Context summary or None
        """
        return self.long_term_context if self.long_term_context else None
    
    def update_long_term_context(self, summary: str) -> None:
        """
        Update long-term context with new summary.
        
        Args:
            summary: New context summary
        """
        if self.long_term_context:
            self.long_term_context += "\n\n" + summary
        else:
            self.long_term_context = summary
        
        # Keep long-term context under control (last 500 words)
        words = self.long_term_context.split()
        if len(words) > 500:
            self.long_term_context = " ".join(words[-500:])
    
    def should_summarize(self) -> bool:
        """
        Check if we should create a summary for long-term memory.
        
        Returns:
            True if summarization threshold is reached
        """
        return self.message_count >= config.LONG_TERM_SUMMARY_THRESHOLD
    
    def reset_message_count(self) -> None:
        """Reset the message count after summarization."""
        self.message_count = 0
    
    def save_memory(self) -> None:
        """Save memory to disk."""
        memory_data = {
            "short_term": self.short_term_messages,
            "long_term_context": self.long_term_context,
            "message_count": self.message_count,
            "last_saved": datetime.now().isoformat()
        }
        
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def load_memory(self) -> None:
        """Load memory from disk."""
        try:
            with open(self.memory_file, 'r') as f:
                memory_data = json.load(f)
                self.short_term_messages = memory_data.get("short_term", [])
                self.long_term_context = memory_data.get("long_term_context", "")
                self.message_count = memory_data.get("message_count", 0)
                
                print(f"Loaded memory from {self.memory_file}")
                print(f"  - {len(self.short_term_messages)} messages in short-term")
                print(f"  - Long-term context: {len(self.long_term_context)} chars")
        except FileNotFoundError:
            print("No existing memory file found. Starting fresh.")
        except Exception as e:
            print(f"Error loading memory: {e}")
    
    def clear_memory(self) -> None:
        """Clear all memory."""
        self.short_term_messages = []
        self.long_term_context = ""
        self.message_count = 0
        self.save_memory()
