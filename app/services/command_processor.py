import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from app.models import WhatsAppMessage, DeviceCommand
from app.services.whatsapp_service import WhatsAppService
from app.services.voice_service import VoiceService
from app.services.ewelink_service import EWeLinkService

class CommandProcessor:
    def __init__(self, whatsapp_service: WhatsAppService, voice_service: VoiceService, ewelink_service: EWeLinkService):
        self.whatsapp = whatsapp_service
        self.voice = voice_service
        self.ewelink = ewelink_service
        
        # Valid commands
        self.valid_commands = ["ON", "OFF", "BLINK", "STATUS", "ALARMA", "ALARM"]
        
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
            
            if command not in self.valid_commands:
                await self._send_invalid_command_response(message, command)
                return
            
            # Get device ID (use first device if no default set)
            device_id = await self._get_device_id()
            if not device_id:
                await self._send_no_device_response(message)
                return
            
            # Process specific commands
            if command == "STATUS":
                await self._handle_status_command(message, device_id)
            elif command in ["ALARMA", "ALARM"]:
                await self._handle_alarm_command(message)
            else:
                await self._handle_device_command(message, device_id, command)
                
        except Exception as e:
            print(f"Command processing error: {str(e)}")
            await self._send_error_response(message, str(e))
    
    async def _handle_device_command(self, message: WhatsAppMessage, device_id: str, command: str):
        """Handle device control commands (ON, OFF, BLINK)"""
        try:
            # Execute command on device
            success = await self.ewelink.control_device(device_id, command)
            
            if success:
                response_text = self._generate_success_message(message.contact_name, command)
            else:
                response_text = self._generate_failure_message(message.contact_name, command)
            
            # Generate and send voice response
            await self._send_voice_response(message.from_phone, response_text)
            
        except Exception as e:
            print(f"Device command error: {str(e)}")
            await self._send_error_response(message, str(e))
    
    async def _handle_status_command(self, message: WhatsAppMessage, device_id: str):
        """Handle status query command"""
        try:
            # Get device status
            status = await self.ewelink.get_device_status(device_id)
            
            if status:
                response_text = self._generate_status_message(message.contact_name, status)
            else:
                response_text = f"Lo siento {message.contact_name or 'usuario'}, no pude obtener el estado del dispositivo. Puede que esté desconectado."
            
            # Generate and send voice response
            await self._send_voice_response(message.from_phone, response_text)
            
        except Exception as e:
            print(f"Status command error: {str(e)}")
            await self._send_error_response(message, str(e))
    
    async def _handle_alarm_command(self, message: WhatsAppMessage):
        """Handle alarm activation command - turns ON all devices"""
        try:
            print(f"🚨 ALARM ACTIVATED by {message.contact_name or message.from_phone}!")
            
            # Get all devices
            devices = await self.ewelink.get_devices()
            
            if not devices:
                response_text = (
                    f"¡ALERTA! {message.contact_name or 'Usuario'}, "
                    f"recibí tu comando de alarma pero no hay dispositivos Sonoff disponibles. "
                    f"Por favor verifica tu conexión eWeLink."
                )
                await self._send_voice_response(message.from_phone, response_text)
                return
            
            # Activate all devices
            success_count = 0
            failed_devices = []
            
            for device in devices:
                print(f"🔴➡️🔵 Activating alarm device: {device.name}")
                success = await self.ewelink.control_device(device.deviceid, "ON")
                
                if success:
                    success_count += 1
                    print(f"✅ {device.name} activated")
                else:
                    failed_devices.append(device.name)
                    print(f"❌ {device.name} failed")
            
            # Generate response based on results
            if success_count == len(devices):
                response_text = (
                    f"¡ALARMA ACTIVADA! {message.contact_name or 'Usuario'}, "
                    f"he encendido todos los {len(devices)} dispositivos Sonoff. "
                    f"El sistema de alarma está completamente activo. "
                    f"Todos los dispositivos han respondido correctamente."
                )
            elif success_count > 0:
                response_text = (
                    f"¡ALARMA PARCIALMENTE ACTIVADA! {message.contact_name or 'Usuario'}, "
                    f"he activado {success_count} de {len(devices)} dispositivos. "
                    f"Algunos dispositivos pueden estar desconectados: {', '.join(failed_devices)}. "
                    f"Verifica la conexión de los dispositivos que fallaron."
                )
            else:
                response_text = (
                    f"¡ERROR DE ALARMA! {message.contact_name or 'Usuario'}, "
                    f"no pude activar ningún dispositivo. "
                    f"Todos los dispositivos están desconectados o hay problemas de conexión. "
                    f"Verifica tu conexión eWeLink inmediatamente."
                )
            
            # Send voice response
            await self._send_voice_response(message.from_phone, response_text)
            
            # Log alarm activation
            print(f"🚨 Alarm summary: {success_count}/{len(devices)} devices activated")
            
        except Exception as e:
            print(f"Alarm command error: {str(e)}")
            error_response = (
                f"¡ERROR CRÍTICO! {message.contact_name or 'Usuario'}, "
                f"ocurrió un error al activar la alarma. "
                f"El sistema puede estar comprometido. "
                f"Verifica manualmente los dispositivos."
            )
            await self._send_voice_response(message.from_phone, error_response)
    
    async def _send_voice_response(self, phone_number: str, text: str):
        """Generate and send voice message response"""
        try:
            # Generate voice message
            audio_file = await self.voice.generate_voice_message(text)
            
            if audio_file:
                # Try to send voice message
                voice_sent = await self.whatsapp.send_voice_message(phone_number, audio_file)
                
                if not voice_sent:
                    # Fallback to file upload method
                    voice_sent = await self.whatsapp.send_voice_message_with_file_upload(phone_number, audio_file)
                
                if not voice_sent:
                    # Ultimate fallback to text message
                    await self.whatsapp.send_text_message(phone_number, text)
                    print("Sent text message as voice fallback")
                
                # Clean up audio file
                self.voice.cleanup_audio_file(audio_file)
            else:
                # Fallback to text if voice generation fails
                await self.whatsapp.send_text_message(phone_number, text)
                print("Sent text message due to voice generation failure")
                
        except Exception as e:
            print(f"Voice response error: {str(e)}")
            # Emergency fallback to text
            try:
                await self.whatsapp.send_text_message(phone_number, text)
            except:
                pass
    
    async def _send_invalid_command_response(self, message: WhatsAppMessage, invalid_command: str):
        """Send response for invalid commands"""
        response_text = (
            f"Hola {message.contact_name or 'usuario'}. "
            f"No reconozco el comando '{invalid_command}'. "
            f"Los comandos disponibles son: ON para encender, OFF para apagar, "
            f"BLINK para modo parpadeo, STATUS para ver el estado, "
            f"y ALARMA para activar todos los dispositivos. "
            f"Por favor envía uno de estos comandos."
        )
        await self._send_voice_response(message.from_phone, response_text)
    
    async def _send_no_device_response(self, message: WhatsAppMessage):
        """Send response when no device is available"""
        response_text = (
            f"Lo siento {message.contact_name or 'usuario'}, "
            f"no hay dispositivos Sonoff disponibles en tu cuenta eWeLink. "
            f"Por favor verifica que tus dispositivos estén conectados y en línea."
        )
        await self._send_voice_response(message.from_phone, response_text)
    
    async def _send_error_response(self, message: WhatsAppMessage, error: str):
        """Send error response"""
        response_text = (
            f"Lo siento {message.contact_name or 'usuario'}, "
            f"ocurrió un error al procesar tu comando. "
            f"Por favor intenta nuevamente en unos momentos."
        )
        await self._send_voice_response(message.from_phone, response_text)
    
    def _generate_success_message(self, contact_name: Optional[str], command: str) -> str:
        """Generate success message for device commands"""
        name = contact_name or "usuario"
        
        if command == "ON":
            return f"¡Perfecto {name}! He encendido el dispositivo correctamente. El LED ya está encendido."
        elif command == "OFF":
            return f"¡Listo {name}! He apagado el dispositivo correctamente. El LED ya está apagado."
        elif command == "BLINK":
            return f"¡Excelente {name}! He activado el modo parpadeo en el dispositivo. El LED ahora está parpadeando."
        elif command in ["ALARMA", "ALARM"]:
            return f"¡ALARMA ACTIVADA {name}! Todos los dispositivos han sido encendidos. El sistema está activo."
        else:
            return f"¡Comando ejecutado correctamente {name}!"
    
    def _generate_failure_message(self, contact_name: Optional[str], command: str) -> str:
        """Generate failure message for device commands"""
        name = contact_name or "usuario"
        return (
            f"Lo siento {name}, no pude ejecutar el comando {command}. "
            f"El dispositivo puede estar desconectado o hay un problema de conexión. "
            f"Por favor verifica que esté encendido y conectado a WiFi."
        )
    
    def _generate_status_message(self, contact_name: Optional[str], status) -> str:
        """Generate status report message"""
        name = contact_name or "usuario"
        
        online_status = "en línea y funcionando" if status.online else "desconectado"
        switch_status = "encendido" if status.switch_state == "on" else "apagado"
        
        time_info = ""
        if status.last_update:
            try:
                # Format timestamp
                time_info = f" La última actualización fue hace unos momentos."
            except:
                pass
        
        return (
            f"Hola {name}! Aquí está el estado de tu dispositivo Sonoff: "
            f"El dispositivo está {online_status}. "
            f"El interruptor está {switch_status}.{time_info} "
            f"Puedes enviar ON, OFF o BLINK para controlarlo."
        )
    
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