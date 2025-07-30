from PyCharacterAI import get_client
from modules.data_handlers.handle_data import *
import asyncio
from dotenv import load_dotenv
import os


class AI:
    def __init__(self) -> None:
        load_dotenv()  
        self.client_token = os.getenv("CHARACTER_AI_TOKEN")
        self.character_id = "Ce2mdN0e7xozlZ8dKl75rCOoRJTWE2FI5Ha7gN7QEgE"
    
    async def create_chatroom(self, user_id: str) -> str | None:
        try:
            client = await get_client(token=self.client_token)
            manage_data = EditData()
            chat, greeting_message = await client.chat.create_chat(self.character_id)
            chat_id = chat.chat_id
            manage_data.add_chatroom(user_id, chat_id)
            return chat_id
        except Exception as e:
            print(f"Error creating chatroom: {e}")
            return None

    async def generate_response(self, message: str, chat_id: str) -> dict:
        """
        Generates both text and voice response from CharacterAI
        Returns: {
            'text': str, 
            'audio': bytes,
            'turn_id': str,
            'candidate_id': str,
            'has_audio': bool
        }
        """
        try:
            client = await get_client(token=self.client_token)
            
            # Get text response with streaming to ensure we get all metadata
            answer = await client.chat.send_message(
                self.character_id, 
                chat_id, 
                message, 
                streaming=True
            )
            
            # Collect the full response text and metadata
            full_text = ""
            turn_id = None
            candidate_id = None
            has_audio = False
            
            async for msg in answer:
                full_text = msg.get_primary_candidate().text
                if hasattr(msg, 'turn_id') and msg.turn_id:
                    turn_id = msg.turn_id
                candidate_id = msg.get_primary_candidate().candidate_id
            
            # Get voice data if we have the required IDs
            voices = await client.utils.search_voices("Makise Kurisu")
            for voice in voices:
                print(f"{voice.name} [{voice.voice_id}]")
          
            audio_bytes = None
            if turn_id and candidate_id:
                try:
                    audio_bytes = await client.utils.generate_speech(
                        chat_id,
                        turn_id,
                        candidate_id,
                        '01efecb5-77c9-43ed-b262-39b331be488f'
                    )
                    has_audio = True
                except Exception as e:
                    print(f"Couldn't generate speech: {e}")
            
            return {
                'text': full_text,
                'audio': audio_bytes,
                'turn_id': turn_id,
                'candidate_id': candidate_id,
                'has_audio': has_audio
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'text': "Sorry, I couldn't process that request.",
                'audio': None,
                'turn_id': None,
                'candidate_id': None,
                'has_audio': False
            }