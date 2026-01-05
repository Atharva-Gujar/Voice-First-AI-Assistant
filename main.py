"""Main orchestration module for the Voice-First AI Assistant."""
import time
import threading
from pynput import keyboard
from typing import Optional

from audio import AudioInput
from audio.output import AudioOutput
from speech.stt import SpeechToText
from speech.tts import TextToSpeech
from llm.handler import LLMHandler
from memory.manager import ConversationMemory
import config


class VoiceAssistant:
    """Main voice assistant orchestrator."""
    
    def __init__(self):
        # Initialize components
        self.audio_input = AudioInput()
        self.audio_output = AudioOutput()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.llm = LLMHandler()
        self.memory = ConversationMemory()
        
        # State management
        self.is_speaking = False
        self.is_listening = False
        self.should_interrupt = False
        self.running = True
        
        # Keyboard listener for push-to-talk
        self.listener: Optional[keyboard.Listener] = None
        
        print("\n" + "="*60)
        print("🎤 Voice-First AI Assistant")
        print("="*60)
        print("\nControls:")
        print("  SPACE - Hold to speak, release to send")
        print("  ESC - Exit the assistant")
        print("\nSay 'goodbye' or 'exit' to end the conversation")
        print("="*60 + "\n")
    
    def on_press(self, key) -> None:
        """Handle key press events."""
        try:
            if key == keyboard.Key.space and not self.is_listening:
                # Start listening
                self.is_listening = True
                
                # If assistant is speaking, interrupt it
                if self.is_speaking:
                    self.should_interrupt = True
                    self.audio_output.stop()
                    print("\n[Interrupted]")
                
                print("\n🎤 Listening... (release SPACE when done)")
                self.audio_input.start_recording()
                
            elif key == keyboard.Key.esc:
                # Exit the assistant
                self.running = False
                return False
                
        except AttributeError:
            pass
    
    def on_release(self, key) -> None:
        """Handle key release events."""
        try:
            if key == keyboard.Key.space and self.is_listening:
                # Stop listening and process
                self.is_listening = False
                print("Processing...\n")
                
                # Get audio and transcribe
                audio_data = self.audio_input.stop_recording()
                threading.Thread(target=self.process_input, args=(audio_data,)).start()
                
        except AttributeError:
            pass
    
    def process_input(self, audio_data) -> None:
        """Process user input and generate response."""
        # Transcribe audio
        user_text = self.stt.transcribe(audio_data)
        
        if not user_text:
            print("(No speech detected)\n")
            return
        
        print(f"You: {user_text}\n")
        
        # Check for exit commands
        if any(word in user_text.lower() for word in ['goodbye', 'exit', 'quit', 'bye']):
            print("Assistant: Goodbye! Have a great day!\n")
            self.running = False
            return
        
        # Add user message to memory
        self.memory.add_message("user", user_text)
        
        # Check if we should summarize for long-term memory
        if self.memory.should_summarize():
            print("[Updating long-term memory...]")
            messages = self.memory.get_messages_for_llm()
            summary = self.llm.generate_summary(messages)
            self.memory.update_long_term_context(summary)
            self.memory.reset_message_count()
        
        # Generate response
        self.generate_and_speak_response()
    
    def generate_and_speak_response(self) -> None:
        """Generate LLM response and speak it with streaming."""
        self.should_interrupt = False
        self.is_speaking = True
        
        # Get messages and context
        messages = self.memory.get_messages_for_llm()
        context = self.memory.get_long_term_context()
        
        # Generate streaming response
        response_text = ""
        text_buffer = []
        
        print("Assistant: ", end="", flush=True)
        
        try:
            # Stream tokens from LLM
            for token in self.llm.generate_response_streaming(messages, context):
                if self.should_interrupt:
                    break
                
                response_text += token
                text_buffer.append(token)
                print(token, end="", flush=True)
                
                # When we have a sentence, synthesize it
                if any(token.endswith(end) for end in ['.', '!', '?', '\n']):
                    sentence = "".join(text_buffer).strip()
                    if sentence:
                        audio = self.tts.synthesize(sentence)
                        if audio and not self.should_interrupt:
                            self.audio_output.play_audio(audio)
                            self.audio_output.wait_until_done()
                    text_buffer = []
            
            # Speak any remaining text
            if text_buffer and not self.should_interrupt:
                sentence = "".join(text_buffer).strip()
                if sentence:
                    audio = self.tts.synthesize(sentence)
                    if audio:
                        self.audio_output.play_audio(audio)
                        self.audio_output.wait_until_done()
            
            print("\n")
            
            # Add response to memory if not interrupted
            if not self.should_interrupt and response_text:
                self.memory.add_message("assistant", response_text)
                self.memory.save_memory()
            
        except Exception as e:
            print(f"\nError generating response: {e}\n")
        
        finally:
            self.is_speaking = False
    
    def run(self) -> None:
        """Run the assistant."""
        # Start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        
        # Keep running until exit
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        print("Cleaning up resources...")
        
        if self.listener:
            self.listener.stop()
        
        self.audio_input.cleanup()
        self.audio_output.cleanup()
        self.memory.save_memory()
        
        print("Goodbye!\n")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
