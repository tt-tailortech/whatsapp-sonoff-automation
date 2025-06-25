import os
import uuid
from typing import Optional
import requests
import httpx
from elevenlabs import generate, save
from app.config import settings
from pydub import AudioSegment

class VoiceService:
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = settings.elevenlabs_voice_id
        self.openai_api_key = settings.openai_api_key
        self.temp_dir = settings.temp_audio_dir
        self._text_only_mode = False
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech using ElevenLabs API
        Returns the file path of the generated audio file
        """
        try:
            # Check if we're in text-only mode (when ElevenLabs fails)
            if hasattr(self, '_text_only_mode') and self._text_only_mode:
                print("Text-only mode: Skipping voice generation")
                return None
            
            # Use default voice if none specified
            selected_voice_id = voice_id or self.voice_id
            
            # Generate unique filename
            audio_id = str(uuid.uuid4())
            mp3_path = os.path.join(self.temp_dir, f"{audio_id}.mp3")
            
            # Generate audio using ElevenLabs
            audio = generate(
                text=text,
                voice=selected_voice_id,
                api_key=self.api_key,
                model="eleven_multilingual_v2"  # Supports Spanish and English
            )
            
            # Save the audio file
            save(audio, mp3_path)
            
            print(f"Generated voice audio: {mp3_path}")
            return mp3_path
            
        except Exception as e:
            error_msg = str(e)
            print(f"Text-to-speech error: {error_msg}")
            
            # If ElevenLabs is blocked, try OpenAI TTS
            if "Unusual activity detected" in error_msg or "Free Tier usage disabled" in error_msg:
                print("ElevenLabs blocked - trying OpenAI TTS")
                if self.openai_api_key:
                    return await self._openai_text_to_speech(text)
                else:
                    print("No OpenAI API key - switching to text-only mode")
                    self._text_only_mode = True
            
            return None
    
    async def _openai_text_to_speech(self, text: str) -> Optional[str]:
        """Use OpenAI TTS as fallback"""
        try:
            # Generate unique filename
            audio_id = str(uuid.uuid4())
            mp3_path = os.path.join(self.temp_dir, f"{audio_id}.mp3")
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": "nova"  # Spanish-friendly voice
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    with open(mp3_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"Generated OpenAI voice audio: {mp3_path}")
                    return mp3_path
                else:
                    print(f"OpenAI TTS failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"OpenAI TTS error: {str(e)}")
            return None
    
    async def convert_to_whatsapp_format(self, mp3_path: str) -> Optional[str]:
        """
        Convert MP3 to OGG/Opus format for WhatsApp voice messages
        """
        try:
            # Generate OGG filename
            ogg_path = mp3_path.replace('.mp3', '.ogg')
            
            # Load and convert audio
            audio = AudioSegment.from_mp3(mp3_path)
            
            # Export as OGG with opus codec
            audio.export(
                ogg_path,
                format="ogg",
                codec="libopus",
                parameters=["-ar", "16000", "-ac", "1"]  # 16kHz mono for WhatsApp
            )
            
            print(f"Converted to WhatsApp format: {ogg_path}")
            return ogg_path
            
        except Exception as e:
            print(f"Audio conversion error: {str(e)}")
            return None
    
    async def generate_voice_message(self, text: str, voice_id: Optional[str] = None) -> Optional[str]:
        """
        Generate a complete voice message ready for WhatsApp
        """
        try:
            # Generate MP3 audio
            mp3_path = await self.text_to_speech(text, voice_id)
            if not mp3_path:
                return None
            
            # Convert to WhatsApp format
            ogg_path = await self.convert_to_whatsapp_format(mp3_path)
            if not ogg_path:
                return None
            
            # Clean up MP3 file
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
            
            return ogg_path
            
        except Exception as e:
            print(f"Voice message generation error: {str(e)}")
            return None
    
    def cleanup_audio_file(self, file_path: str):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up audio file: {file_path}")
        except Exception as e:
            print(f"Cleanup error: {str(e)}")
    
    def get_available_voices(self) -> dict:
        """Get list of available ElevenLabs voices"""
        try:
            url = "https://api.elevenlabs.io/v1/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get voices: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Get voices error: {str(e)}")
            return {}