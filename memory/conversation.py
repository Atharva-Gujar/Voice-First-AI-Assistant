"""
Conversation Memory Module
Handles short-term and long-term conversation memory
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class ConversationMemory:
    def __init__(self, memory_file=None):
        self.memory_file = memory_file or os.getenv('MEMORY_FILE', 'conversation_memory.json')
        self.max_short_term = int(os.getenv('MAX_SHORT_TERM_MESSAGES', 20))
        
        # Short-term buffer (current conversation)
        self.short_term_memory = []
        
        # Long-term memory (summarized past conversations)
        self.long_term_memory = []
        
        # Load existing memory
        self.load_memory()
        
    def add_message(self, role: str, content: str):
        """Add a message to short-term memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.short_term_memory.append(message)
        
        # If short-term memory is full, summarize and move to long-term
        if len(self.short_term_memory) > self.max_short_term:
            self._compress_memory()
            
    def get_context(self) -> List[Dict]:
        """Get conversation context for LLM"""
        # Return messages in the format expected by Claude
        context = []
        
        # Add long-term memory summary if exists
        if self.long_term_memory:
            summary = self._create_summary()
            if summary:
                context.append({
                    "role": "user",
                    "content": f"Previous conversation summary: {summary}"
                })
                context.append({
                    "role": "assistant",
                    "content": "I remember our previous conversations."
                })
        
        # Add recent short-term messages
        for msg in self.short_term_memory:
            context.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            
        return context
        
    def _compress_memory(self):
        """Compress old messages into long-term memory"""
        # Take the oldest messages and create a summary
        messages_to_compress = self.short_term_memory[:self.max_short_term // 2]
        
        # Create a simple summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages_to_compress),
            "messages": messages_to_compress
        }
        
        self.long_term_memory.append(summary)
        
        # Keep only recent messages in short-term
        self.short_term_memory = self.short_term_memory[self.max_short_term // 2:]
        
        # Save to disk
        self.save_memory()
        
    def _create_summary(self) -> str:
        """Create a summary from long-term memory"""
        if not self.long_term_memory:
            return ""
            
        # Simple summary of topics discussed
        total_messages = sum(m["message_count"] for m in self.long_term_memory)
        return f"We've had {total_messages} previous exchanges."
        
    def save_memory(self):
        """Save memory to disk"""
        try:
            memory_data = {
                "short_term": self.short_term_memory,
                "long_term": self.long_term_memory,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
            
    def load_memory(self):
        """Load memory from disk"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    memory_data = json.load(f)
                    
                self.short_term_memory = memory_data.get("short_term", [])
                self.long_term_memory = memory_data.get("long_term", [])
                print(f"📚 Loaded memory: {len(self.short_term_memory)} recent messages")
        except Exception as e:
            print(f"Error loading memory: {e}")
            
    def clear_short_term(self):
        """Clear short-term memory (start fresh conversation)"""
        self.short_term_memory = []
        self.save_memory()
        
    def clear_all(self):
        """Clear all memory"""
        self.short_term_memory = []
        self.long_term_memory = []
        self.save_memory()
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
