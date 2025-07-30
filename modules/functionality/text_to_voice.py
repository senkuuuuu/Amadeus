import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

class TextToVoice:
    def __init__(self, ai_response: dict) -> None:
        """
        ai_response: dict from AI.generate_response()
        """
        self.ai_response = ai_response
        load_dotenv()
        self.output_path = 'temp_output.mp3'
        
    def save_audio(self) -> bool:
        """Save the audio response to a file. Returns True if successful."""
        if not self.ai_response.get('audio'):
            print("No audio in response")
            return False
            
        try:
            with open(self.output_path, 'wb') as f:
                f.write(self.ai_response['audio'])
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def get_text(self) -> str:
        """Get the text response"""
        return self.ai_response.get('text', '...')
    
    def has_audio(self) -> bool:
        """Check if we have audio available"""
        return bool(self.ai_response.get('audio'))
    
    def get_audio_path(self) -> Path:
        """Get the path to the audio file"""
        return self.output_path if self.output_path.exists() else None