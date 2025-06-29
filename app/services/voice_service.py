import os
import uuid
from typing import Optional
import httpx
from app.config import settings
from pydub import AudioSegment

class VoiceService:
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.temp_dir = settings.temp_audio_dir
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Validate OpenAI API key
        if not self.openai_api_key:
            print("⚠️ OpenAI API key not configured - voice messages will be disabled")
    
    async def text_to_speech(self, text: str, voice: str = "nova") -> Optional[str]:
        """
        Convert text to speech using OpenAI TTS API
        Returns the file path of the generated MP3 audio file
        
        Available voices: alloy, echo, fable, onyx, nova, shimmer
        """
        try:
            if not self.openai_api_key:
                print("❌ No OpenAI API key configured")
                return None
            
            # Generate unique filename
            audio_id = str(uuid.uuid4())
            mp3_path = os.path.join(self.temp_dir, f"{audio_id}.mp3")
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "tts-1",  # High quality: tts-1-hd, Standard: tts-1
                "input": text,
                "voice": voice  # nova is good for Spanish/English
            }
            
            print(f"🎙️ Generating OpenAI TTS audio...")
            print(f"   Text: {text[:50]}...")
            print(f"   Voice: {voice}")
            print(f"   Model: {payload['model']}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers=headers,
                    json=payload
                )
                
                print(f"🎙️ OpenAI TTS Response: {response.status_code}")
                
                if response.status_code == 200:
                    with open(mp3_path, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = os.path.getsize(mp3_path)
                    print(f"✅ Generated OpenAI voice audio: {mp3_path} ({file_size} bytes)")
                    return mp3_path
                else:
                    print(f"❌ OpenAI TTS failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ OpenAI TTS error: {str(e)}")
            return None
    
    async def convert_to_whatsapp_format(self, mp3_path: str) -> Optional[str]:
        """
        Convert MP3 to OGG/Opus format for WhatsApp voice messages
        WhatsApp requires: OGG container with Opus codec, 16kHz mono
        """
        try:
            if not os.path.exists(mp3_path):
                print(f"❌ MP3 file not found: {mp3_path}")
                return None
            
            # Generate OGG filename
            ogg_path = mp3_path.replace('.mp3', '.ogg')
            
            print(f"🔄 Converting MP3 to WhatsApp OGG format...")
            print(f"   Input: {mp3_path}")
            print(f"   Output: {ogg_path}")
            
            # Load and convert audio
            audio = AudioSegment.from_mp3(mp3_path)
            
            # Get audio info
            print(f"   Original: {audio.frame_rate}Hz, {audio.channels} channels, {len(audio)}ms")
            
            # Export as OGG with opus codec (WhatsApp requirements)
            audio.export(
                ogg_path,
                format="ogg",
                codec="libopus",
                parameters=["-ar", "16000", "-ac", "1"]  # 16kHz mono for WhatsApp
            )
            
            if os.path.exists(ogg_path):
                file_size = os.path.getsize(ogg_path)
                print(f"✅ Converted to WhatsApp format: {ogg_path} ({file_size} bytes)")
                return ogg_path
            else:
                print(f"❌ Failed to create OGG file: {ogg_path}")
                return None
            
        except Exception as e:
            print(f"❌ Audio conversion error: {str(e)}")
            return None
    
    async def generate_voice_message(self, text: str, voice: str = "nova") -> Optional[str]:
        """
        Generate a complete voice message ready for WhatsApp
        Returns OGG file path ready for WhatsApp sending
        """
        try:
            print(f"🎤 Generating voice message for: '{text}'")
            
            # Step 1: Generate MP3 audio using OpenAI TTS
            mp3_path = await self.text_to_speech(text, voice)
            if not mp3_path:
                print("❌ Failed to generate TTS audio")
                return None
            
            # Step 2: Convert to WhatsApp format (OGG/Opus)
            ogg_path = await self.convert_to_whatsapp_format(mp3_path)
            if not ogg_path:
                print("❌ Failed to convert to WhatsApp format")
                return None
            
            # Step 3: Clean up MP3 file (keep only OGG)
            self.cleanup_audio_file(mp3_path)
            
            print(f"✅ Voice message ready: {ogg_path}")
            return ogg_path
            
        except Exception as e:
            print(f"❌ Voice message generation error: {str(e)}")
            return None
    
    def cleanup_audio_file(self, file_path: str):
        """Clean up temporary audio files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🧹 Cleaned up audio file: {file_path}")
        except Exception as e:
            print(f"❌ Cleanup error: {str(e)}")
    
    def get_available_voices(self) -> list:
        """Get list of available OpenAI TTS voices"""
        return [
            {"name": "alloy", "description": "Neutral, balanced voice"},
            {"name": "echo", "description": "Male voice"},
            {"name": "fable", "description": "British accent"},
            {"name": "onyx", "description": "Deep male voice"},
            {"name": "nova", "description": "Female voice, good for Spanish/English"},
            {"name": "shimmer", "description": "Soft female voice"}
        ]
    
    async def test_voice_generation(self, test_text: str = "Hola, esto es una prueba de mensaje de voz en español.") -> dict:
        """
        Test the complete voice generation pipeline
        Returns detailed test results
        """
        results = {
            "test_text": test_text,
            "openai_api_key_configured": bool(self.openai_api_key),
            "temp_dir_exists": os.path.exists(self.temp_dir),
            "steps": {}
        }
        
        try:
            # Test OpenAI TTS
            print(f"🧪 Testing OpenAI TTS with: '{test_text}'")
            mp3_path = await self.text_to_speech(test_text)
            results["steps"]["tts_generation"] = {
                "success": bool(mp3_path),
                "file_path": mp3_path,
                "file_exists": os.path.exists(mp3_path) if mp3_path else False,
                "file_size": os.path.getsize(mp3_path) if mp3_path and os.path.exists(mp3_path) else 0
            }
            
            if not mp3_path:
                results["overall_success"] = False
                return results
            
            # Test format conversion
            print(f"🧪 Testing format conversion...")
            ogg_path = await self.convert_to_whatsapp_format(mp3_path)
            results["steps"]["format_conversion"] = {
                "success": bool(ogg_path),
                "file_path": ogg_path,
                "file_exists": os.path.exists(ogg_path) if ogg_path else False,
                "file_size": os.path.getsize(ogg_path) if ogg_path and os.path.exists(ogg_path) else 0
            }
            
            # Cleanup test files
            if mp3_path:
                self.cleanup_audio_file(mp3_path)
            if ogg_path:
                self.cleanup_audio_file(ogg_path)
            
            results["overall_success"] = bool(ogg_path)
            print(f"🧪 Voice generation test {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
            
        except Exception as e:
            results["error"] = str(e)
            results["overall_success"] = False
            print(f"🧪 Voice generation test ❌ FAILED: {str(e)}")
        
        return results