import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from app.models import WhatsAppMessage, DeviceCommand
from app.services.whatsapp_service import WhatsAppService
# from app.services.voice_service import VoiceService
from app.services.ewelink_service import EWeLinkService

class CommandProcessor:
    def __init__(self, whatsapp_service: WhatsAppService, ewelink_service: EWeLinkService):
        self.whatsapp = whatsapp_service
        # self.voice = voice_service  # Removed - no voice for now
        self.ewelink = ewelink_service
        
        # Valid commands - only TEST for now
        self.valid_commands = ["TEST"]
        
        # Default device ID - will be set from environment or first device found
        self.default_device_id = None
    
    async def process_whatsapp_message(self, payload: Dict[str, Any]):
        """Process incoming WhatsApp message and execute commands"""
        try:
            # Parse the WhatsApp message
            message = self.whatsapp.parse_whatsapp_webhook(payload)
            if not message:
                print("Failed to parse WhatsApp message")
                return
            
            print(f"Processing message from {message.contact_name or message.from_phone}: {message.text}")
            
            # Process the command
            await self._process_command(message)
            
        except Exception as e:
            print(f"Command processing error: {str(e)}")
    
    async def _process_command(self, message: WhatsAppMessage):
        """Process individual command and generate response"""
        try:
            # Clean and validate command
            command = message.text.strip().upper()
            
            # Only respond to TEST command
            if command == "TEST":
                await self._handle_test_command(message)
            else:
                # Ignore all other commands silently
                print(f"Ignoring command: {command}")
                return
                
        except Exception as e:
            print(f"Command processing error: {str(e)}")
            await self._send_error_response(message, str(e))
    
    async def _handle_test_command(self, message: WhatsAppMessage):
        """Handle TEST command - do blink pattern and send text response"""
        try:
            print(f"🧪 TEST command received from {message.contact_name or message.from_phone}")
            
            # Get device ID
            device_id = await self._get_device_id()
            if not device_id:
                print("❌ No device found for TEST")
                return
            
            print(f"🔄 Starting blink pattern on device {device_id}")
            
            # Perform blink pattern: ON-OFF 3 times, then keep ON
            blink_success = await self._perform_blink_pattern(device_id)
            
            if blink_success:
                # Send success message to WhatsApp
                response_text = "EL SENSOR HA SIDO ACTIVADO, POR FAVOR DESPETRENSE TODOS"
                await self._send_text_message(message.from_phone, response_text)
                print("✅ TEST command completed successfully")
            else:
                print("❌ Blink pattern failed")
                
        except Exception as e:
            print(f"TEST command error: {str(e)}")
    
    async def _perform_blink_pattern(self, device_id: str) -> bool:
        """Perform blink pattern: ON-OFF 3 times, then keep ON"""
        try:
            # Blink 3 times
            for cycle in range(1, 4):
                print(f"🔄 Blink cycle {cycle}/3")
                
                # Turn ON
                on_success = await self.ewelink.control_device(device_id, "ON")
                if not on_success:
                    print(f"❌ ON failed in cycle {cycle}")
                    return False
                await asyncio.sleep(1)
                
                # Turn OFF
                off_success = await self.ewelink.control_device(device_id, "OFF")
                if not off_success:
                    print(f"❌ OFF failed in cycle {cycle}")
                    return False
                await asyncio.sleep(1)
            
            # Final: Keep ON
            print("🔥 Final step: Keeping device ON")
            final_on = await self.ewelink.control_device(device_id, "ON")
            if final_on:
                print("✅ Blink pattern completed - device is ON")
                return True
            else:
                print("❌ Final ON command failed")
                return False
                
        except Exception as e:
            print(f"❌ Blink pattern error: {e}")
            return False
    
    async def _send_text_message(self, phone_number: str, text: str):
        """Send simple text message to WhatsApp"""
        try:
            await self.whatsapp.send_text_message(phone_number, text)
            print(f"📤 Sent text message to {phone_number}: {text}")
        except Exception as e:
            print(f"❌ Failed to send text message: {e}")
    
    # Removed old alarm and voice methods - only TEST command now
    
    async def _get_device_id(self) -> Optional[str]:
        """Get device ID to use for commands"""
        try:
            if self.default_device_id:
                return self.default_device_id
            
            # Get first available device
            devices = await self.ewelink.get_devices()
            if devices:
                self.default_device_id = devices[0].deviceid
                return self.default_device_id
            
            return None
            
        except Exception as e:
            print(f"Get device ID error: {str(e)}")
            return None
    
    async def set_default_device(self, device_name: str) -> bool:
        """Set default device by name"""
        try:
            device_id = await self.ewelink.find_device_by_name(device_name)
            if device_id:
                self.default_device_id = device_id
                print(f"Default device set to: {device_name} ({device_id})")
                return True
            return False
        except Exception as e:
            print(f"Set default device error: {str(e)}")
            return False