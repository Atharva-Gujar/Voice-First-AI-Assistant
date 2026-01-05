"""
LLM Engine with streaming support and intent resolution.
Handles conversation with LLM and generates streaming responses.
"""

import asyncio
from openai import OpenAI
from anthropic import Anthropic
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMEngine:
    """Handles LLM interactions with streaming support."""
    
    def __init__(self, config, memory_manager):
        self.config = config
        self.memory = memory_manager
        
        self.provider = config.get('LLM_PROVIDER', 'openai')
        self.model = config.get('LLM_MODEL', 'gpt-4-turbo-preview')
        
        # Initialize appropriate client
        if self.provider == 'openai':
            self.client = OpenAI(api_key=config.get('OPENAI_API_KEY'))
        elif self.provider == 'anthropic':
            self.client = Anthropic(api_key=config.get('ANTHROPIC_API_KEY'))
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        # System prompt for voice assistant personality
        self.system_prompt = """You are a helpful voice assistant. 
Keep responses concise and natural for spoken conversation.
Be friendly, clear, and to the point.
Avoid overly long explanations unless asked."""
        
        logger.info(f"LLMEngine initialized with {self.provider} - {self.model}")
    
    async def generate_streaming_response(self, user_input: str):
        """
        Generate streaming response from LLM.
        Yields tokens as they arrive.
        """
        try:
            # Get conversation context from memory
            messages = self._build_messages(user_input)
            
            # Stream response based on provider
            if self.provider == 'openai':
                async for token in self._stream_openai(messages):
                    yield token
            elif self.provider == 'anthropic':
                async for token in self._stream_anthropic(messages):
                    yield token
                    
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            yield "I apologize, but I encountered an error. Could you please try again?"
    
    def _build_messages(self, user_input: str) -> list:
        """Build message list with context from memory."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history from memory
        history = self.memory.get_context()
        messages.extend(history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    async def _stream_openai(self, messages: list):
        """Stream response from OpenAI."""
        loop = asyncio.get_event_loop()
        
        # Create streaming completion
        stream = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7
            )
        )
        
        # Yield tokens as they arrive
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _stream_anthropic(self, messages: list):
        """Stream response from Anthropic Claude."""
        # Convert system message format for Anthropic
        system_msg = messages[0]["content"]
        conversation = messages[1:]
        
        loop = asyncio.get_event_loop()
        
        # Create streaming completion
        stream = await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_msg,
                messages=conversation,
                stream=True
            )
        )
        
        # Yield tokens as they arrive
        for event in stream:
            if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                yield event.delta.text
    
    def resolve_intent(self, user_input: str) -> dict:
        """
        Analyze user input to determine intent.
        Useful for more complex routing or command handling.
        """
        # Simple intent classification (can be enhanced with dedicated model)
        intent = {
            "type": "conversation",
            "confidence": 1.0,
            "entities": {}
        }
        
        # Check for common command patterns
        lower_input = user_input.lower()
        
        if any(word in lower_input for word in ["stop", "quiet", "shut up"]):
            intent["type"] = "stop"
        elif any(word in lower_input for word in ["remember", "recall", "what did"]):
            intent["type"] = "memory_query"
        elif any(word in lower_input for word in ["forget", "clear", "reset"]):
            intent["type"] = "memory_clear"
        
        return intent
