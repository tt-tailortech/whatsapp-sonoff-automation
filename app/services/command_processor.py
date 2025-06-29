import asyncio
import re
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
        
        # Valid commands - SOS triggers emergency pipeline
        self.valid_commands = ["SOS"]
        
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
            # Clean and validate command - handle SOS with flexible formatting
            raw_text = message.text.strip()
            
            # Check if message starts with SOS (case insensitive, with optional spaces)
            if self._is_sos_command(raw_text):
                # Extract incident type from message (everything after SOS)
                incident_type = self._extract_incident_type(raw_text)
                await self._handle_sos_command(message, incident_type)
            else:
                # Ignore all other commands silently
                print(f"Ignoring command: {raw_text}")
                return
                
        except Exception as e:
            print(f"Command processing error: {str(e)}")
            await self._send_error_response(message, str(e))
    
    def _is_sos_command(self, text: str) -> bool:
        """Check if message starts with SOS (case insensitive, flexible spacing)"""
        # Remove leading/trailing spaces and check if starts with SOS
        cleaned_text = text.strip().upper()
        return cleaned_text.startswith('SOS')
    
    def _extract_incident_type(self, text: str) -> str:
        """Extract incident type from SOS message"""
        # Remove SOS from beginning and clean up
        cleaned_text = text.strip()
        # Remove SOS (case insensitive) from the start
        sos_pattern = re.compile(r'^sos\s*', re.IGNORECASE)
        incident_text = sos_pattern.sub('', cleaned_text).strip()
        
        if incident_text:
            # If there's text after SOS, use it as incident type
            return incident_text.upper()
        else:
            # Default if just "SOS" with no additional text
            return "EMERGENCIA GENERAL"
    
    async def _handle_sos_command(self, message: WhatsAppMessage, incident_type: str):
        """Handle SOS command - trigger full emergency pipeline"""
        try:
            print(f"🚨 SOS command received from {message.contact_name or message.from_phone}")
            print(f"🚨 Incident type: {incident_type}")
            
            # Import emergency pipeline
            from create_full_emergency_pipeline import execute_full_emergency_pipeline
            
            # Extract group info
            group_chat_id = message.chat_id
            group_name = "Grupo de Emergencia"  # Default, could be extracted from webhook
            if "@g.us" in group_chat_id:
                # This is a group chat
                print(f"🏘️ Emergency in group: {group_chat_id}")
            
            # Get device ID
            device_id = await self._get_device_id()
            if not device_id:
                print("⚠️ No device found, continuing with other alerts")
                device_id = "10011eafd1"  # Default fallback
            
            # Execute full emergency pipeline
            print(f"🚨 Executing emergency pipeline for: {incident_type}")
            
            success = await execute_full_emergency_pipeline(
                incident_type=incident_type,
                street_address="Ubicación por confirmar",
                emergency_number="SAMU 131",
                sender_phone=message.from_phone,
                sender_name=message.contact_name or "Usuario",
                group_chat_id=group_chat_id,
                group_name=group_name,
                device_id=device_id,
                blink_cycles=3,
                voice_text=f"Emergencia activada. {incident_type} reportada. Contacto de emergencia: SAMU uno tres uno. Reportado por {message.contact_name or 'usuario'}. Por favor manténganse seguros y sigan las instrucciones de las autoridades."
            )
            
            if success:
                print("✅ SOS emergency pipeline completed successfully")
            else:
                print("⚠️ SOS emergency pipeline completed with some limitations")
                
        except Exception as e:
            print(f"SOS command error: {str(e)}")
            # Send basic alert if pipeline fails
            await self._send_text_message(message.chat_id, f"🚨 EMERGENCIA ACTIVADA: {incident_type}")
    
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
                await self._send_text_message(message.chat_id, response_text)
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
                await asyncio.sleep(1.5)  # Slightly longer delay
                
                # Turn OFF
                off_success = await self.ewelink.control_device(device_id, "OFF")
                if not off_success:
                    print(f"❌ OFF failed in cycle {cycle}")
                    return False
                await asyncio.sleep(1.5)  # Slightly longer delay
            
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
    
    async def _send_error_response(self, message: WhatsAppMessage, error: str):
        """Send error response to WhatsApp"""
        try:
            error_text = f"❌ Error procesando comando: {error}"
            await self._send_text_message(message.chat_id, error_text)
        except Exception as e:
            print(f"❌ Failed to send error response: {e}")
    
    # Removed old alarm and voice methods - SOS triggers full pipeline now
    
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