"""Test suite for Memory Manager."""

import pytest
from core.memory_manager import MemoryManager
from utils.config import Config


def test_memory_initialization():
    """Test memory manager initialization."""
    config = Config()
    memory = MemoryManager(config)
    
    assert memory.short_term_memory is not None
    assert memory.long_term_memory is not None
    assert len(memory.short_term_memory) == 0


def test_add_message():
    """Test adding messages to memory."""
    config = Config()
    memory = MemoryManager(config)
    
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")
    
    assert len(memory.short_term_memory) == 2
    assert memory.short_term_memory[0]["role"] == "user"
    assert memory.short_term_memory[1]["role"] == "assistant"


def test_get_context():
    """Test getting conversation context."""
    config = Config()
    memory = MemoryManager(config)
    
    memory.add_message("user", "Test message")
    context = memory.get_context()
    
    assert len(context) > 0
    assert context[0]["role"] == "user"
def test_memory_stats():
    """Test memory statistics."""
    config = Config()
    memory = MemoryManager(config)
    
    memory.add_message("user", "Message 1")
    memory.add_message("assistant", "Response 1")
    
    stats = memory.get_stats()
    
    assert stats["short_term_count"] == 2
    assert stats["total_messages"] >= 2


def test_clear_memory():
    """Test clearing memory."""
    config = Config()
    memory = MemoryManager(config)
    
    memory.add_message("user", "Test")
    memory.clear_memory()
    
    assert len(memory.short_term_memory) == 0
    assert len(memory.long_term_memory) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
