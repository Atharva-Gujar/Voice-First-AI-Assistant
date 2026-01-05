"""LLM integration module using Anthropic Claude."""
from anthropic import Anthropic
from typing import List, Dict, Iterator, Optional
import config


class LLMHandler:
    """Handles LLM interactions with streaming support."""
    
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the assistant."""
        return """You are a helpful voice assistant. You engage in natural, conversational dialogue.

Key behaviors:
- Keep responses concise and conversational (2-3 sentences typically)
- Speak naturally as if in a real conversation
- Be helpful, friendly, and engaging
- Remember context from earlier in the conversation
- If interrupted, gracefully handle context shifts

You communicate through voice, so format responses for natural speech without special formatting."""
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        conversation_context: Optional[str] = None
    ) -> str:
        """
        Generate a complete response.
        
        Args:
            messages: Conversation history
            conversation_context: Optional long-term context summary
            
        Returns:
            Generated response text
        """
        system_content = self.system_prompt
        if conversation_context:
            system_content += f"\n\nConversation context from earlier: {conversation_context}"
        
        try:
            response = self.client.messages.create(
                model=config.LLM_MODEL,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                system=system_content,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"LLM error: {e}")
            return "I'm sorry, I encountered an error processing that."
    
    def generate_response_streaming(
        self,
        messages: List[Dict[str, str]],
        conversation_context: Optional[str] = None
    ) -> Iterator[str]:
        """
        Generate a streaming response token by token.
        
        Args:
            messages: Conversation history
            conversation_context: Optional long-term context summary
            
        Yields:
            Response tokens as they're generated
        """
        system_content = self.system_prompt
        if conversation_context:
            system_content += f"\n\nConversation context from earlier: {conversation_context}"
        
        try:
            with self.client.messages.stream(
                model=config.LLM_MODEL,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                system=system_content,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            print(f"LLM streaming error: {e}")
            yield "I'm sorry, I encountered an error processing that."
    
    def generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a summary of the conversation for long-term memory.
        
        Args:
            messages: Messages to summarize
            
        Returns:
            Summary text
        """
        summary_prompt = """Summarize the key points and context from this conversation concisely. 
Focus on important facts, decisions, and topics discussed. Keep it under 100 words."""
        
        summary_messages = messages + [{"role": "user", "content": summary_prompt}]
        
        try:
            response = self.client.messages.create(
                model=config.LLM_MODEL,
                max_tokens=200,
                temperature=0.5,
                system="You are a conversation summarizer. Create concise summaries.",
                messages=summary_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return ""
