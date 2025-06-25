#!/usr/bin/env python3
"""
Manual Testing Script for API Integrations
Run this script to test the integrations manually with real API calls
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.voice_service import VoiceService
from app.services.whatsapp_service import WhatsAppService
from app.services.ewelink_service import EWeLinkService
from app.config import settings

# Load environment variables
load_dotenv()

class ManualTester:
    def __init__(self):
        self.voice_service = VoiceService()
        self.whatsapp_service = WhatsAppService()
        self.ewelink_service = EWeLinkService()
    
    async def test_voice_service(self):
        """Test ElevenLabs voice generation"""
        print("\n🎵 Testing Voice Service...")
        
        try:
            # Test text-to-speech
            print("Generating voice message...")
            audio_file = await self.voice_service.generate_voice_message(
                "¡Hola! Esta es una prueba del sistema de automatización con WhatsApp y Sonoff. El comando ha sido ejecutado correctamente."
            )
            
            if audio_file:
                print(f"✅ Voice message generated: {audio_file}")
                print(f"File size: {os.path.getsize(audio_file)} bytes")
                
                # Clean up
                self.voice_service.cleanup_audio_file(audio_file)
                print("🧹 Audio file cleaned up")
            else:
                print("❌ Voice generation failed")
            
        except Exception as e:
            print(f"❌ Voice service error: {str(e)}")
    
    async def test_whatsapp_service(self):
        """Test WHAPI.co integration"""
        print("\n📱 Testing WhatsApp Service...")
        
        try:
            # Test account info
            print("Getting WhatsApp account info...")
            account_info = await self.whatsapp_service.get_account_info()
            
            if account_info:
                print(f"✅ Account info retrieved: {account_info.get('name', 'Unknown')}")
            else:
                print("❌ Failed to get account info")
            
            # Test webhook parsing
            print("Testing webhook parsing...")
            test_payload = {
                "messages": [{
                    "id": "test123",
                    "from": "+1234567890",
                    "type": "text",
                    "text": {"body": "ON"},
                    "timestamp": "1640995200"
                }],
                "contacts": [{
                    "profile": {"name": "Test User"}
                }]
            }
            
            parsed_message = self.whatsapp_service.parse_whatsapp_webhook(test_payload)
            if parsed_message:
                print(f"✅ Webhook parsed: {parsed_message.text} from {parsed_message.contact_name}")
            else:
                print("❌ Webhook parsing failed")
            
        except Exception as e:
            print(f"❌ WhatsApp service error: {str(e)}")
    
    async def test_ewelink_service(self):
        """Test eWeLink integration"""
        print("\n🏠 Testing eWeLink Service...")
        
        try:
            # Note: This requires actual eWeLink credentials
            print("Testing eWeLink authentication...")
            print("⚠️  Authentication requires real credentials - skipping for demo")
            
            # If you want to test with real credentials, uncomment:
            # email = input("Enter eWeLink email: ")
            # password = input("Enter eWeLink password: ")
            # auth_success = await self.ewelink_service.authenticate(email, password)
            # 
            # if auth_success:
            #     print("✅ eWeLink authentication successful")
            #     
            #     # Get devices
            #     devices = await self.ewelink_service.get_devices()
            #     print(f"📱 Found {len(devices)} devices")
            #     
            #     for device in devices:
            #         print(f"  - {device.name} ({device.deviceid}) - {'Online' if device.online else 'Offline'}")
            # else:
            #     print("❌ eWeLink authentication failed")
            
        except Exception as e:
            print(f"❌ eWeLink service error: {str(e)}")
    
    async def test_voice_message_complete_flow(self):
        """Test complete voice message flow"""
        print("\n🔄 Testing Complete Voice Message Flow...")
        
        try:
            # Generate voice message
            test_message = "¡Perfecto! He encendido el dispositivo correctamente. El LED ya está encendido."
            print(f"Generating voice for: {test_message}")
            
            audio_file = await self.voice_service.generate_voice_message(test_message)
            
            if audio_file:
                print(f"✅ Audio generated: {audio_file}")
                
                # Test WhatsApp voice sending (will fail without real phone number)
                print("Testing voice message sending...")
                print("⚠️  Voice sending requires real phone number - skipping for demo")
                
                # If you want to test with real phone number, uncomment:
                # phone_number = input("Enter phone number (with country code): ")
                # voice_sent = await self.whatsapp_service.send_voice_message(phone_number, audio_file)
                # 
                # if voice_sent:
                #     print("✅ Voice message sent successfully")
                # else:
                #     print("❌ Voice message sending failed")
                
                # Clean up
                self.voice_service.cleanup_audio_file(audio_file)
                print("🧹 Audio file cleaned up")
            else:
                print("❌ Voice generation failed")
            
        except Exception as e:
            print(f"❌ Complete flow error: {str(e)}")
    
    def test_webhook_samples(self):
        """Test webhook parsing with different samples"""
        print("\n📨 Testing Webhook Parsing...")
        
        # Test different webhook formats
        samples = [
            {
                "name": "WHAPI Direct Format",
                "payload": {
                    "messages": [{
                        "id": "msg123",
                        "from": "+1234567890",
                        "type": "text",
                        "text": {"body": "STATUS"},
                        "timestamp": "1640995200"
                    }],
                    "contacts": [{"profile": {"name": "Test User"}}]
                }
            },
            {
                "name": "Business API Format",
                "payload": {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "id": "msg456",
                                    "from": "+9876543210",
                                    "type": "text",
                                    "text": {"body": "OFF"},
                                    "timestamp": "1640995300"
                                }],
                                "contacts": [{"profile": {"name": "Business User"}}]
                            }
                        }]
                    }]
                }
            }
        ]
        
        for sample in samples:
            print(f"\nTesting {sample['name']}...")
            result = self.whatsapp_service.parse_whatsapp_webhook(sample['payload'])
            
            if result:
                print(f"✅ Parsed: '{result.text}' from {result.contact_name} ({result.from_phone})")
            else:
                print("❌ Parsing failed")

async def main():
    """Main test runner"""
    print("🚀 Starting Manual API Testing...")
    print("=" * 50)
    
    tester = ManualTester()
    
    # Run tests
    await tester.test_voice_service()
    await tester.test_whatsapp_service()
    await tester.test_ewelink_service()
    await tester.test_voice_message_complete_flow()
    tester.test_webhook_samples()
    
    print("\n" + "=" * 50)
    print("🏁 Manual testing completed!")
    print("\nTo test with real APIs, update your .env file with:")
    print("- ELEVENLABS_API_KEY")
    print("- WHAPI_TOKEN")
    print("- EWELINK_APP_ID and EWELINK_APP_SECRET")

if __name__ == "__main__":
    asyncio.run(main())