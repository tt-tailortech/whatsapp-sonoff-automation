import asyncio
import re
import time
import os
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
        
        # Lazy load services
        self._member_editor = None
        self._bulk_data_service = None
        self._backup_service = None
        
        # Message cache for @tailor command (stores recent 7 messages per chat)
        self._message_cache = {}  # {chat_id: [message1, message2, ..., message7]}
    
    async def process_whatsapp_message(self, payload: Dict[str, Any]):
        """Process incoming WhatsApp message and execute commands"""
        try:
            # Parse the WhatsApp message
            message = self.whatsapp.parse_whatsapp_webhook(payload)
            if not message:
                # No message to process (could be status update, non-text message, etc.)
                return
            
            print(f"🔄 WEBHOOK DEBUG - Processing message from {message.contact_name or message.from_phone}")
            print(f"🔄 WEBHOOK DEBUG - Message text: '{message.text[:200]}...'")
            print(f"🔄 WEBHOOK DEBUG - Chat ID: {message.chat_id}")
            print(f"🔄 WEBHOOK DEBUG - From phone: {message.from_phone}")
            
            # First, handle group management (ensure group folders exist for group messages)
            # Skip group management for @info and all @ commands to avoid blocking
            if not message.text.strip().startswith('@'):
                print(f"🔄 WEBHOOK DEBUG - Processing group management...")
                await self.whatsapp.process_group_management(message)
            else:
                print(f"🔄 WEBHOOK DEBUG - Skipping group management for @ command")
            
            # Cache message for @tailor command (before processing commands)
            self._cache_message(message)
            
            # Auto-detect and add new members to database (groups only)
            if message.chat_id.endswith("@g.us"):
                await self._auto_detect_new_member(message)
            
            # Then process the command
            print(f"🔄 WEBHOOK DEBUG - About to process command...")
            await self._process_command(message)
            
        except Exception as e:
            print(f"Command processing error: {str(e)}")
    
    async def _process_command(self, message: WhatsAppMessage):
        """Process individual command and generate response"""
        try:
            # Clean and validate command - handle SOS with flexible formatting
            raw_text = message.text.strip()
            print(f"🔍 COMMAND DEBUG - Processing: '{raw_text}' (length: {len(raw_text)})")
            print(f"🔍 COMMAND DEBUG - First 100 chars: '{raw_text[:100]}...'")
            print(f"🔍 COMMAND DEBUG - Starts with @info: {raw_text.lower().startswith('@info')}")
            print(f"🔍 COMMAND DEBUG - Starts with @editar: {raw_text.lower().startswith('@editar')}")
            print(f"🔍 COMMAND DEBUG - Contains SOS: {'SOS' in raw_text.upper()}")
            print(f"🔍 COMMAND DEBUG - Contains SISTEMA: {'SISTEMA' in raw_text.upper()}")
            print(f"🔍 COMMAND DEBUG - Contains ACTUALIZADO: {'ACTUALIZADO' in raw_text.upper()}")
            print(f"🔍 COMMAND DEBUG - Is SOS command: {self._is_sos_command(raw_text)}")
            print(f"🔍 COMMAND DEBUG - Message type determination:")
            
            # Check if message starts with SOS (case insensitive, with optional spaces)
            if self._is_sos_command(raw_text):
                print(f"🚨 COMMAND DEBUG - TRIGGERING SOS PIPELINE")
                # SOS works in both individual and group chats
                # Extract incident type from message (everything after SOS)
                incident_type = self._extract_incident_type(raw_text)
                await self._handle_sos_command(message, incident_type)
            elif raw_text.lower().startswith('@info'):
                # Handle @info command to show system information (works everywhere)
                print(f"ℹ️ Detected @info command in: '{raw_text}'")
                await self._handle_info_command(message)
            elif not message.chat_id.endswith("@g.us"):
                # All other commands require group chats, silently ignore individual messages
                print(f"📨 Ignoring non-group command: {raw_text[:20]}... (individual chat)")
                return
            elif raw_text.lower().startswith('@editar'):
                # Handle @editar commands for member data editing (groups only)
                await self._handle_editar_command(message, raw_text)
            elif raw_text.lower().startswith('@exportar'):
                # Handle @exportar commands for bulk data export (groups only)
                await self._handle_export_command(message, raw_text)
            elif raw_text.lower().startswith('@importar'):
                # Handle @importar commands for bulk data import (groups only)
                await self._handle_import_command(message, raw_text)
            elif raw_text.lower().startswith('@plantilla'):
                # Handle @plantilla command for CSV template (groups only)
                await self._handle_template_command(message)
            elif raw_text.lower().startswith('@backup'):
                # Handle @backup commands for data backup (groups only)
                await self._handle_backup_command(message, raw_text)
            elif raw_text.lower().startswith('@restore'):
                # Handle @restore commands for data restoration (groups only)
                await self._handle_restore_command(message, raw_text)
            elif raw_text.lower().startswith('@backups'):
                # Handle @backups command to list available backups (groups only)
                await self._handle_list_backups_command(message)
            elif raw_text.lower().startswith('@infodb'):
                # Handle @infodb command to show database structure (groups only)
                await self._handle_infodb_command(message)
            elif raw_text.lower().startswith('@vecinos'):
                # Handle @vecinos command to list group members (groups only)
                await self._handle_vecinos_command(message)
            elif raw_text.lower().startswith('@tailor'):
                # Handle @tailor command for friendly AI neighbor chat (works everywhere)
                await self._handle_tailor_command(message, raw_text)
            else:
                # Ignore all other commands silently
                print(f"🔍 COMMAND DEBUG - IGNORING COMMAND: '{raw_text[:50]}...'")
                print(f"🔍 COMMAND DEBUG - Command ignored because:")
                print(f"   - Not SOS: {not self._is_sos_command(raw_text)}")
                print(f"   - Not @info: {not raw_text.lower().startswith('@info')}")
                print(f"   - Not @editar: {not raw_text.lower().startswith('@editar')}")
                print(f"   - Not in group: {not message.chat_id.endswith('@g.us')}")
                return
                
        except Exception as e:
            print(f"Command processing error: {str(e)}")
            await self._send_error_response(message, str(e))
    
    def _is_sos_command(self, text: str) -> bool:
        """Check if message contains SOS in any combination at the start (case insensitive, flexible)"""
        # Clean text and normalize
        cleaned_text = text.strip().upper()
        
        print(f"🚨 SOS DEBUG - Input text: '{text[:100]}...'")
        print(f"🚨 SOS DEBUG - Cleaned text: '{cleaned_text[:100]}...'")
        
        # Don't trigger SOS on @ commands
        if cleaned_text.startswith('@'):
            print(f"🚨 SOS DEBUG - REJECTED: Starts with @")
            return False
        
        # Don't trigger SOS on system messages (containing "SISTEMA" or "ACTUALIZADO" or "FUNCIONALIDADES")
        if "SISTEMA" in cleaned_text or "ACTUALIZADO" in cleaned_text or "FUNCIONALIDADES" in cleaned_text:
            print(f"🚨 SOS DEBUG - REJECTED: Contains system message keywords")
            return False
            
        # Don't trigger SOS on documentation/help messages (containing bullet points or explanations)
        if "•" in cleaned_text or "- AHORA USA" in cleaned_text or "BASE DE DATOS" in cleaned_text:
            print(f"🚨 SOS DEBUG - REJECTED: Contains documentation/help content")
            return False
        
        # Simple and flexible SOS detection - any combination of S, O, S letters at start
        # Accepts: SOS, S.O.S, SOZ, SOSS, S O S, etc.
        sos_pattern = r'^\s*S[.\s]*O[.\s]*S[.\s]*\w*\b'
        
        print(f"🚨 SOS DEBUG - Testing flexible SOS pattern against: '{cleaned_text[:50]}...'")
        
        if re.search(sos_pattern, cleaned_text):
            print(f"🚨 SOS DEBUG - MATCHED: SOS pattern detected")
            return True
        
        print(f"🚨 SOS DEBUG - NO SOS PATTERN MATCHED")
        return False
    
    def _extract_incident_type(self, text: str) -> str:
        """Extract incident type from SOS message (next 2 words after any SOS combination)"""
        # Clean and normalize text
        cleaned_text = text.strip().upper()
        
        print(f"🎯 EXTRACT DEBUG - Input: '{text}'")
        print(f"🎯 EXTRACT DEBUG - Cleaned: '{cleaned_text}'")
        
        # Find any SOS pattern and get everything after it
        # Matches SOS, S.O.S, SOSS, S O S, etc. and captures what follows
        sos_pattern = r'^\s*S[.\s]*O[.\s]*S[.\s]*\w*\s+(.+)'
        
        match = re.search(sos_pattern, cleaned_text)
        if match:
            # Get text after SOS pattern
            after_sos = match.group(1).strip()
            print(f"🎯 EXTRACT DEBUG - Text after SOS: '{after_sos}'")
            
            # Split into words and take first 2
            words = after_sos.split()
            if words:
                # Take maximum 2 words
                incident_text = " ".join(words[:2])
                print(f"🎯 EXTRACT DEBUG - Extracted incident: '{incident_text}' (from {len(words)} words)")
                return incident_text
        
        # If no text after SOS or no match, return default
        print(f"🎯 EXTRACT DEBUG - No incident text found, using default")
        return "EMERGENCIA GENERAL"
    
    async def _handle_sos_command(self, message: WhatsAppMessage, incident_type: str):
        """Handle SOS command - trigger full emergency pipeline"""
        try:
            print(f"🚨 SOS command received from {message.contact_name or message.from_phone}")
            print(f"🚨 Incident type: {incident_type}")
            
            # Import emergency pipeline with fallback
            try:
                from create_full_emergency_pipeline import execute_full_emergency_pipeline
            except ImportError as e:
                print(f"⚠️ Emergency pipeline not available: {str(e)}")
                # Fall back to basic text alert
                await self._send_text_message(message.chat_id, f"🚨 EMERGENCIA ACTIVADA: {incident_type}")
                return
            
            # Extract group info
            group_chat_id = message.chat_id
            group_name = message.chat_name or "Grupo de Emergencia"  # Use extracted chat name or default
            if "@g.us" in group_chat_id:
                # This is a group chat
                print(f"🏘️ Emergency in group: {group_name} ({group_chat_id})")
            else:
                # Individual chat
                print(f"🏘️ Emergency in individual chat: {group_name} ({group_chat_id})")
            
            # Get device ID
            device_id = await self._get_device_id()
            if not device_id:
                print("⚠️ No device found, continuing with other alerts")
                device_id = "10011eafd1"  # Default fallback
            
            # Execute full emergency pipeline
            print(f"🚨 Executing emergency pipeline for: {incident_type}")
            
            success = await execute_full_emergency_pipeline(
                incident_type=incident_type,
                street_address="Ubicación por confirmar",  # Will be updated with member data
                emergency_number="SAMU 131",
                sender_phone=message.from_phone,
                sender_name=message.contact_name or "Usuario",  # Will be updated with member data
                group_chat_id=group_chat_id,
                group_name=group_name,
                device_id=device_id,
                blink_cycles=3,
                voice_text=f"Emergencia activada. {incident_type} reportada. Contacto de emergencia: SAMU uno tres uno. Reportado por {message.contact_name or 'usuario'}. Por favor manténganse seguros y sigan las instrucciones de las autoridades.",
                use_member_data=True  # Enable member data lookup
            )
            
            if success:
                print("✅ SOS emergency pipeline completed successfully")
            else:
                print("⚠️ SOS emergency pipeline completed with some limitations")
                
        except Exception as e:
            print(f"SOS command error: {str(e)}")
            # Send basic alert if pipeline fails
            await self._send_text_message(message.chat_id, f"🚨 EMERGENCIA ACTIVADA: {incident_type}")
    
    async def _handle_editar_command(self, message: WhatsAppMessage, command_text: str):
        """Handle @editar command for member data editing"""
        try:
            print(f"📝 @editar command received from {message.contact_name or message.from_phone}")
            print(f"📝 Command: {command_text}")
            
            # Lazy load member editor service
            if not self._member_editor:
                try:
                    from app.services.member_editor_service import MemberEditorService
                    self._member_editor = MemberEditorService()
                    print(f"✅ Member editor service loaded")
                except ImportError as e:
                    print(f"❌ Member editor service not available: {str(e)}")
                    await self._send_text_message(message.chat_id, "❌ Sistema de edición no disponible")
                    return
            
            # Process the @editar command
            success, response = await self._member_editor.process_editar_command(
                command_text=command_text,
                sender_phone=message.from_phone,
                group_chat_id=message.chat_id,
                group_name=message.chat_name or "Grupo Desconocido",
                sender_name=message.contact_name or "Usuario"
            )
            
            # Send response back to the group
            if response:
                await self._send_text_message(message.chat_id, response)
                print(f"✅ @editar response sent: {success}")
            else:
                print(f"⚠️ No response generated for @editar command")
                
        except Exception as e:
            print(f"❌ Error processing @editar command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @editar: {str(e)}")
    
    async def _handle_export_command(self, message: WhatsAppMessage, command_text: str):
        """Handle @exportar command for bulk data export"""
        try:
            print(f"📤 @exportar command received from {message.contact_name or message.from_phone}")
            
            # Lazy load bulk data service
            if not self._bulk_data_service:
                try:
                    from app.services.bulk_data_service import BulkDataService
                    self._bulk_data_service = BulkDataService()
                    print(f"✅ Bulk data service loaded")
                except ImportError as e:
                    print(f"❌ Bulk data service not available: {str(e)}")
                    await self._send_text_message(message.chat_id, "❌ Servicio de exportación no disponible")
                    return
            
            # Parse export format
            parts = command_text.lower().split()
            export_format = "csv"  # default
            if len(parts) > 1 and parts[1] in ["csv", "json"]:
                export_format = parts[1]
            
            # Export data
            if export_format == "csv":
                success, content, error = await self._bulk_data_service.export_group_members_csv(
                    message.chat_id, message.chat_name or "Grupo"
                )
                if success:
                    # Save to file and send
                    filename = f"miembros_{message.chat_name or 'grupo'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Send file - Note: This would need WhatsApp file sending capability
                    response = f"✅ Datos exportados a CSV\n📁 Archivo: {filename}\n📊 {len(content.split(chr(10))-1)} miembros exportados"
                    await self._send_text_message(message.chat_id, response)
                else:
                    await self._send_text_message(message.chat_id, f"❌ Error exportando CSV: {error}")
            
            elif export_format == "json":
                success, content, error = await self._bulk_data_service.export_group_members_json(
                    message.chat_id, message.chat_name or "Grupo"
                )
                if success:
                    filename = f"miembros_{message.chat_name or 'grupo'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    response = f"✅ Datos exportados a JSON\n📁 Archivo: {filename}\n📊 Exportación completa realizada"
                    await self._send_text_message(message.chat_id, response)
                else:
                    await self._send_text_message(message.chat_id, f"❌ Error exportando JSON: {error}")
                    
        except Exception as e:
            print(f"❌ Error processing @exportar command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @exportar: {str(e)}")
    
    async def _handle_import_command(self, message: WhatsAppMessage, command_text: str):
        """Handle @importar command for bulk data import"""
        try:
            await self._send_text_message(message.chat_id, 
                "📥 Para importar datos:\n"
                "1. Usa @plantilla para obtener formato CSV\n"
                "2. Envía el archivo CSV como mensaje de texto\n"
                "3. Usa @importar [contenido CSV]\n\n"
                "⚠️ Solo administradores pueden importar datos"
            )
                    
        except Exception as e:
            print(f"❌ Error processing @importar command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @importar: {str(e)}")
    
    async def _handle_template_command(self, message: WhatsAppMessage):
        """Handle @plantilla command for CSV template"""
        try:
            print(f"📋 @plantilla command received from {message.contact_name or message.from_phone}")
            
            # Lazy load bulk data service
            if not self._bulk_data_service:
                try:
                    from app.services.bulk_data_service import BulkDataService
                    self._bulk_data_service = BulkDataService()
                except ImportError as e:
                    await self._send_text_message(message.chat_id, "❌ Servicio de plantillas no disponible")
                    return
            
            # Create template
            template = await self._bulk_data_service.create_member_template_csv()
            
            # Save template to file
            filename = f"plantilla_miembros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(template)
            
            response = f"""📋 Plantilla CSV creada: {filename}

📝 INSTRUCCIONES:
1. Descarga el archivo {filename}
2. Completa los datos de los miembros
3. Guarda como CSV (UTF-8)
4. Usa @importar para subir los datos

⚠️ IMPORTANTE:
- Teléfono y Nombre son obligatorios
- Coordenadas formato: latitud,longitud
- Listas separar con punto y coma (;)
- Es Admin: true/false
- Solo administradores pueden importar"""
            
            await self._send_text_message(message.chat_id, response)
                    
        except Exception as e:
            print(f"❌ Error processing @plantilla command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @plantilla: {str(e)}")
    
    async def _handle_backup_command(self, message: WhatsAppMessage, command_text: str):
        """Handle @backup command for data backup"""
        try:
            print(f"💾 @backup command received from {message.contact_name or message.from_phone}")
            
            # Check admin permissions
            if not self._member_editor:
                try:
                    from app.services.member_editor_service import MemberEditorService
                    self._member_editor = MemberEditorService()
                except ImportError:
                    await self._send_text_message(message.chat_id, "❌ Sistema de permisos no disponible")
                    return
            
            # Check if sender has admin permissions
            if not await self._member_editor._check_admin_permissions(message.from_phone, message.chat_id, message.chat_name or "Grupo"):
                await self._send_text_message(message.chat_id, "❌ Solo los administradores pueden crear backups")
                return
            
            # Lazy load backup service
            if not self._backup_service:
                try:
                    from app.services.backup_service import BackupService
                    self._backup_service = BackupService()
                    print(f"✅ Backup service loaded")
                except ImportError as e:
                    print(f"❌ Backup service not available: {str(e)}")
                    await self._send_text_message(message.chat_id, "❌ Servicio de backup no disponible")
                    return
            
            # Parse backup type
            parts = command_text.lower().split()
            backup_type = "group"  # default to group backup
            custom_name = None
            
            if len(parts) > 1:
                if "full" in parts[1] or "sistema" in parts[1] or "completo" in parts[1]:
                    backup_type = "full"
                elif len(parts) > 1 and parts[1] not in ["grupo", "group"]:
                    # Custom name provided
                    custom_name = " ".join(parts[1:])
            
            # Create backup
            if backup_type == "full":
                await self._send_text_message(message.chat_id, "💾 Creando backup completo del sistema...")
                success, result = await self._backup_service.create_full_system_backup(custom_name)
            else:
                await self._send_text_message(message.chat_id, f"💾 Creando backup del grupo {message.chat_name or 'Grupo'}...")
                success, result = await self._backup_service.create_group_backup(message.chat_id, message.chat_name or "Grupo")
            
            if success:
                response = f"✅ Backup creado exitosamente\n📁 Ubicación: {result}"
                if backup_type == "full":
                    response += "\n📊 Backup incluye todos los grupos del sistema"
                else:
                    response += f"\n📊 Backup del grupo: {message.chat_name or 'Grupo'}"
                await self._send_text_message(message.chat_id, response)
            else:
                await self._send_text_message(message.chat_id, f"❌ Error creando backup: {result}")
                
        except Exception as e:
            print(f"❌ Error processing @backup command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @backup: {str(e)}")
    
    async def _handle_restore_command(self, message: WhatsAppMessage, command_text: str):
        """Handle @restore command for data restoration"""
        try:
            print(f"🔄 @restore command received from {message.contact_name or message.from_phone}")
            
            # Check admin permissions
            if not self._member_editor:
                try:
                    from app.services.member_editor_service import MemberEditorService
                    self._member_editor = MemberEditorService()
                except ImportError:
                    await self._send_text_message(message.chat_id, "❌ Sistema de permisos no disponible")
                    return
            
            # Check if sender has admin permissions
            if not await self._member_editor._check_admin_permissions(message.from_phone, message.chat_id, message.chat_name or "Grupo"):
                await self._send_text_message(message.chat_id, "❌ Solo los administradores pueden restaurar backups")
                return
            
            # Lazy load backup service
            if not self._backup_service:
                try:
                    from app.services.backup_service import BackupService
                    self._backup_service = BackupService()
                    print(f"✅ Backup service loaded")
                except ImportError as e:
                    print(f"❌ Backup service not available: {str(e)}")
                    await self._send_text_message(message.chat_id, "❌ Servicio de backup no disponible")
                    return
            
            # Parse restore parameters
            parts = command_text.split()
            if len(parts) < 2:
                await self._send_text_message(message.chat_id, 
                    "❌ Uso: @restore [nombre_backup]\n"
                    "Ejemplo: @restore full_backup_20250629_123456\n"
                    "Usa @backups para ver backups disponibles"
                )
                return
            
            backup_path = " ".join(parts[1:])
            
            await self._send_text_message(message.chat_id, f"🔄 Restaurando desde backup: {backup_path}...")
            
            # Restore from backup
            success, result = await self._backup_service.restore_from_backup(backup_path)
            
            if success:
                await self._send_text_message(message.chat_id, f"✅ Backup restaurado exitosamente\n📊 {result}")
            else:
                await self._send_text_message(message.chat_id, f"❌ Error restaurando backup: {result}")
                
        except Exception as e:
            print(f"❌ Error processing @restore command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @restore: {str(e)}")
    
    async def _handle_list_backups_command(self, message: WhatsAppMessage):
        """Handle @backups command to list available backups"""
        try:
            print(f"📋 @backups command received from {message.contact_name or message.from_phone}")
            
            # Check admin permissions
            if not self._member_editor:
                try:
                    from app.services.member_editor_service import MemberEditorService
                    self._member_editor = MemberEditorService()
                except ImportError:
                    await self._send_text_message(message.chat_id, "❌ Sistema de permisos no disponible")
                    return
            
            # Check if sender has admin permissions
            if not await self._member_editor._check_admin_permissions(message.from_phone, message.chat_id, message.chat_name or "Grupo"):
                await self._send_text_message(message.chat_id, "❌ Solo los administradores pueden ver backups")
                return
            
            # Lazy load backup service
            if not self._backup_service:
                try:
                    from app.services.backup_service import BackupService
                    self._backup_service = BackupService()
                    print(f"✅ Backup service loaded")
                except ImportError as e:
                    print(f"❌ Backup service not available: {str(e)}")
                    await self._send_text_message(message.chat_id, "❌ Servicio de backup no disponible")
                    return
            
            # Get list of backups
            backups = await self._backup_service.list_backups()
            
            if not backups:
                await self._send_text_message(message.chat_id, "📋 No hay backups disponibles")
                return
            
            # Format backup list
            response = "📋 BACKUPS DISPONIBLES:\n\n"
            
            for i, backup in enumerate(backups[:10], 1):  # Show first 10
                name = backup.get('name', 'Unknown')
                location = backup.get('location', 'Unknown')
                created_at = backup.get('created_at', 'Unknown')
                size = backup.get('size', 0)
                
                # Format date
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(created_at)
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    formatted_date = created_at
                
                # Format size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} bytes"
                
                location_emoji = "☁️" if location == "google_drive" else "💾"
                
                response += f"{i}. {location_emoji} {name}\n"
                response += f"   📅 {formatted_date}\n"
                response += f"   📊 {size_str}\n\n"
            
            if len(backups) > 10:
                response += f"... y {len(backups) - 10} backups más\n\n"
            
            response += "💡 Usa @restore [nombre] para restaurar\n"
            response += "💡 Usa @backup para crear nuevo backup"
            
            await self._send_text_message(message.chat_id, response)
                
        except Exception as e:
            print(f"❌ Error processing @backups command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @backups: {str(e)}")
    
    async def _handle_info_command(self, message: WhatsAppMessage):
        """Handle @info command to show system information"""
        try:
            # @info works in both individual and group chats
            print(f"ℹ️ @info command received from {message.contact_name or message.from_phone}")
            
            # Generate system information message in Spanish
            info_message = f"""🚨{'='*60}
🚨 SISTEMA DE EMERGENCIAS WHATSAPP ACTIVADO
🚨{'='*60}

📢 PALABRA CLAVE CONFIGURADA:
   1. 'SOS' - Activa el sistema de respuesta de emergencia

🎯 PATRONES DE MENSAJE SOPORTADOS:
   • SOS → EMERGENCIA GENERAL
   • sos → EMERGENCIA GENERAL  
   • SOS INCENDIO → INCENDIO
   • SOS EMERGENCIA MÉDICA → EMERGENCIA MÉDICA
   • SOS ACCIDENTE VEHICULAR → ACCIDENTE VEHICULAR (máx 2 palabras)
   • S.O.S TERREMOTO → TERREMOTO
   • Cualquier mensaje que contenga SOS activa la respuesta de emergencia

🔧 CONTROL DE DISPOSITIVOS: Switches Sonoff integrados
🎤 ALERTAS DE VOZ: OpenAI TTS (Español)
📷 ALERTAS DE IMAGEN: ✅ Disponible
⚡ ESTADO: 🟢 OPERACIONAL

📝 COMANDOS DISPONIBLES:
   • @info - Mostrar información del sistema
   • @infodb - Mostrar estructura de base de datos
   • @vecinos - Listar miembros del grupo con datos básicos
   • @tailor [pregunta] - Chatea con Tailor, tu vecino amigable 🤖
   • @editar - Editar datos de miembros (solo administradores)
   • @exportar [csv/json] - Exportar datos de miembros
   • @importar - Importar datos de miembros
   • @plantilla - Obtener plantilla CSV
   • @backup [grupo/completo] - Crear respaldo
   • @restore [nombre_backup] - Restaurar desde respaldo
   • @backups - Listar respaldos disponibles

🚨{'='*60}
🚨 SISTEMA DE EMERGENCIAS LISTO PARA MENSAJES
🚨{'='*60}

💻 Desarrollado por Tailor Tech
🌐 https://tailortech.cl"""

            await self._send_text_message(message.chat_id, info_message)
            print("✅ @info system information sent")
                
        except Exception as e:
            print(f"❌ Error processing @info command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @info: {str(e)}")
    
    async def _handle_infodb_command(self, message: WhatsAppMessage):
        """Handle @infodb command to show database structure information"""
        try:
            print(f"🗄️ @infodb command received from {message.contact_name or message.from_phone}")
            
            # Create database structure explanation
            infodb_message = f"""🗄️ ESTRUCTURA DE BASE DE DATOS DE MIEMBROS

📊 INFORMACIÓN GENERAL:
• Almacenamiento: Google Drive (cifrado)
• Formato: JSON por grupo de WhatsApp  
• Ubicación: Carpeta 'member_databases'
• Respaldos automáticos: ✅ Activos

👤 DATOS DE CADA MIEMBRO:
• Información Personal:
  - Nombre completo y alias
  - Teléfono principal y de emergencia
  - Contacto familiar

📍 Información de Ubicación:
  - Dirección completa (calle, número, piso, depto)
  - Barrio y ciudad
  - Coordenadas GPS (opcional)

🩺 Información Médica (Cifrada):
  - Condiciones médicas importantes
  - Medicamentos actuales  
  - Alergias conocidas
  - Tipo de sangre
  - Necesidades especiales de evacuación

👥 Información de Emergencia:
  - Rol en emergencias (coordinador, asistente)
  - Permisos de administrador
  - Fechas de ingreso y última actividad

🔒 SEGURIDAD Y PRIVACIDAD:
• Datos médicos cifrados con AES-256
• Solo administradores pueden ver información completa
• Auditoría completa de todos los accesos
• Cumple normativas de protección de datos

📝 USO EN EMERGENCIAS:
• Lookup automático durante alertas SOS
• Información médica disponible para paramédicos
• Contactos de emergencia notificados automáticamente
• Ubicación exacta enviada a servicios de emergencia

💻 Desarrollado por Tailor Tech
🌐 https://tailortech.cl"""

            await self._send_text_message(message.chat_id, infodb_message)
            print("✅ @infodb database structure information sent")
                
        except Exception as e:
            print(f"❌ Error processing @infodb command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @infodb: {str(e)}")
    
    async def _handle_vecinos_command(self, message: WhatsAppMessage):
        """Handle @vecinos command to list group members with non-confidential data"""
        try:
            print(f"👥 @vecinos command received from {message.contact_name or message.from_phone}")
            
            # Lazy load member lookup service
            try:
                from app.services.member_lookup_service import MemberLookupService  
                from app.services.group_manager_service import GroupManagerService
                group_manager = GroupManagerService()
            except ImportError as e:
                print(f"❌ Member services not available: {str(e)}")
                await self._send_text_message(message.chat_id, "❌ Servicio de miembros no disponible")
                return
            
            # Get group member data
            member_data = await group_manager.get_group_member_data(message.chat_id, message.chat_name or "Grupo")
            
            if not member_data or not member_data.get("members"):
                await self._send_text_message(message.chat_id, 
                    f"👥 VECINOS DE {message.chat_name or 'ESTE GRUPO'}\n\n"
                    "❌ No hay miembros registrados en la base de datos\n\n"
                    "💡 Para registrar miembros usa:\n"
                    "• @editar nombre [teléfono] a [Nombre Completo]\n"
                    "• @editar dirección [teléfono] a [Dirección]"
                )
                return
            
            # Build member list with non-confidential data
            members = member_data.get("members", {})
            group_name = member_data.get("group_name", message.chat_name or "Grupo")
            admin_phones = member_data.get("admins", [])
            
            response = f"👥 VECINOS DE {group_name.upper()}\n"
            response += f"📊 Total: {len(members)} miembros registrados\n\n"
            
            # Sort members by name
            sorted_members = []
            for phone, data in members.items():
                name = data.get("name", "Sin nombre")
                sorted_members.append((name, phone, data))
            
            sorted_members.sort(key=lambda x: x[0])
            
            for i, (name, phone, data) in enumerate(sorted_members[:20], 1):  # Limit to 20 members
                # Get basic info
                address = data.get("address", {})
                street = address.get("street", "No registrada")
                apartment = address.get("apartment", "")
                neighborhood = address.get("neighborhood", "")
                
                # Check if admin
                is_admin = phone in admin_phones
                admin_icon = "👑" if is_admin else "👤"
                
                # Get alias
                aliases = data.get("alias", [])
                alias_text = f" ({', '.join(aliases)})" if aliases else ""
                
                # Build address text
                address_text = street
                if apartment:
                    address_text += f", {apartment}"
                if neighborhood:
                    address_text += f" - {neighborhood}"
                
                response += f"{i}. {admin_icon} {name}{alias_text}\n"
                response += f"   📱 {phone}\n"
                response += f"   📍 {address_text}\n"
                
                # Show if member has emergency info without revealing details
                emergency_info = data.get("emergency_info", {})
                medical = data.get("medical", {})
                
                # Non-confidential indicators
                has_emergency_contact = bool(data.get("contacts", {}).get("emergency"))
                has_medical_info = bool(medical.get("conditions") or medical.get("allergies") or medical.get("blood_type"))
                needs_assistance = emergency_info.get("evacuation_assistance", False)
                
                indicators = []
                if has_emergency_contact:
                    indicators.append("📞 Contacto emergencia")
                if has_medical_info:
                    indicators.append("🩺 Info médica")
                if needs_assistance:
                    indicators.append("🆘 Requiere asistencia")
                
                if indicators:
                    response += f"   ℹ️ {' | '.join(indicators)}\n"
                
                response += "\n"
            
            if len(members) > 20:
                response += f"... y {len(members) - 20} miembros más\n\n"
            
            response += f"💡 COMANDOS ÚTILES:\n"
            response += f"• @editar dirección [teléfono] a [nueva dirección]\n"
            response += f"• @editar teléfono emergencia [teléfono] a [contacto]\n"
            response += f"• @editar admin agregar [teléfono] - hacer admin\n"
            response += f"• @exportar csv - exportar todos los datos\n\n"
            response += f"🔒 Datos médicos y contactos de emergencia son confidenciales\n"
            response += f"💻 Desarrollado por Tailor Tech"

            await self._send_text_message(message.chat_id, response)
            print(f"✅ @vecinos member list sent for {group_name}")
                
        except Exception as e:
            print(f"❌ Error processing @vecinos command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @vecinos: {str(e)}")
    
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
    
    def _cache_message(self, message: WhatsAppMessage):
        """Cache message for @tailor command context (stores last 7 messages per chat)"""
        try:
            chat_id = message.chat_id
            
            # Don't cache @tailor commands or SOS messages to avoid confusion
            if message.text.lower().startswith('@tailor') or self._is_sos_command(message.text):
                return
            
            # Initialize chat cache if needed
            if chat_id not in self._message_cache:
                self._message_cache[chat_id] = []
            
            # Create message entry
            message_entry = {
                "text": message.text,
                "sender": message.contact_name or message.from_phone,
                "timestamp": time.time()
            }
            
            # Add to cache (keep only last 7 messages)
            self._message_cache[chat_id].append(message_entry)
            if len(self._message_cache[chat_id]) > 7:
                self._message_cache[chat_id].pop(0)
            
            print(f"💬 Cached message for chat {chat_id}: {len(self._message_cache[chat_id])} messages stored")
            
        except Exception as e:
            print(f"❌ Error caching message: {str(e)}")
    
    async def _handle_tailor_command(self, message: WhatsAppMessage, raw_text: str):
        """Handle @tailor command - friendly AI neighbor chat using OpenAI"""
        try:
            print(f"🤖 @tailor command received from {message.contact_name or message.from_phone}")
            
            # Extract the question/content after @tailor
            user_query = raw_text[7:].strip()  # Remove "@tailor" and whitespace
            
            if not user_query:
                await self._send_text_message(message.chat_id, 
                    "👋 ¡Hola! Soy Tailor, tu vecino digital del barrio 😄\n\n"
                    "Pregúntame lo que cachai después de @tailor:\n\n"
                    "💬 Conversa: @tailor ¿cómo andai?\n"
                    "🔧 Sistema: @tailor ¿cómo uso @editar?\n"
                    "🚨 Emergencias: @tailor ¿cómo funciona SOS?\n"
                    "📊 Datos: @tailor ¿qué info guarda el sistema?\n\n"
                    "¡Dale no más, pregunta lo que quieras! 🤖\n\n"
                    "💻 Desarrollado por Tailor Tech")
                return
            
            # Get recent message context (last 7 messages)
            chat_context = ""
            if message.chat_id in self._message_cache:
                recent_messages = self._message_cache[message.chat_id]
                if recent_messages:
                    chat_context = "Contexto de conversación reciente:\\n"
                    for msg in recent_messages:
                        chat_context += f"- {msg['sender']}: {msg['text'][:150]}...\\n"
            
            # Generate AI response using OpenAI
            try:
                ai_response = await self._generate_tailor_response(user_query, chat_context, message)
                
                # Send the response
                await self._send_text_message(message.chat_id, ai_response)
                print(f"✅ @tailor response sent to {message.contact_name or message.from_phone}")
                
            except Exception as ai_error:
                print(f"❌ AI generation failed: {str(ai_error)}")
                # Fallback response
                fallback_response = f"🤖 ¡Hola! Soy Tailor, tu vecino del barrio 👋\\n\\n" \
                                  f"Preguntaste: \"{user_query}\"\\n\\n" \
                                  f"¡Pucha! Ando un poco colapsado con los sistemas de emergencia en este momento, " \
                                  f"pero tu pregunta se ve terrible buena. ¿Cachai que me preguntes de nuevo en un ratito? " \
                                  f"Al tiro te respondo bien 😅\\n\\n" \
                                  f"💻 Desarrollado por Tailor Tech"
                
                await self._send_text_message(message.chat_id, fallback_response)
                
        except Exception as e:
            print(f"❌ Error processing @tailor command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @tailor: {str(e)}")
    
    async def _generate_tailor_response(self, user_query: str, chat_context: str, message: WhatsAppMessage) -> str:
        """Generate friendly AI response using OpenAI GPT-4o-mini (cheapest model)"""
        import aiohttp
        import json
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise Exception("OpenAI API key not configured")
        
        # Get sender info
        sender_name = message.contact_name or "Amigo"
        group_name = message.chat_name or "este grupo"
        
        # Create friendly neighbor prompt with system knowledge
        system_prompt = f"""Eres Tailor, un vecino digital súper amigable y divertido de una comunidad chilena. También eres el experto técnico del sistema de emergencias y conoces todos los comandos y funcionalidades.

PERSONALIDAD:
- Muy amigable, cercano y cálido como un buen vecino chileno
- Hablas en español chileno auténtico pero respetuoso
- Usas chilenismos naturalmente: bacán, fome, cachai, al tiro, terrible, la raja, etc.
- Eres servicial y siempre con buena onda, pero con humor chileno
- Te gusta hacer tallas suaves y comentarios tiernos
- Usas expresiones típicas: "oye", "sí po", "ya po", "pucha", "ah no cierto"
- Eres divertido pero cute, como un vecino querido del barrio

CONTEXTO COMUNITARIO:
- Vives en una comunidad que usa WhatsApp para emergencias
- Conoces a todos los vecinos y te importa su bienestar
- Eres parte del sistema de alertas de emergencia creado por Tailor Tech
- Puedes hablar de cualquier tema, no solo emergencias

CONOCIMIENTO TÉCNICO DEL SISTEMA:
Comandos Disponibles:
• @info - Información del sistema de emergencias
• @infodb - Estructura de base de datos de miembros
• @vecinos - Lista de vecinos con datos básicos
• @tailor [pregunta] - Chat contigo (este comando)
• @editar - Editar datos de miembros (solo admins)
• @exportar [csv/json] - Exportar datos de miembros
• @importar - Importar datos masivos
• @plantilla - Plantilla CSV para datos
• @backup [grupo/completo] - Crear respaldos
• @restore [nombre] - Restaurar desde respaldo
• @backups - Listar respaldos disponibles
• SOS [tipo] - Activar emergencia (usa base de datos)

Funcionalidades del Sistema:
- Pipeline de Emergencia: Dispositivo parpadea → Texto → Imagen → Voz
- Base de Datos: Google Drive con datos cifrados de miembros
- Auto-Detección: Nuevos miembros se agregan automáticamente al escribir
- Dispositivos Sonoff: Control remoto de switches/alarmas
- IA Inteligente: OpenAI para mensajes y respuestas de emergencia
- Webhooks WhatsApp: WHAPI.cloud para integración
- Generación de Imágenes: Alertas dinámicas con datos reales
- Mensajes de Voz: TTS en español para emergencias
- Administración: Permisos por roles (admin, moderador, miembro)

Base de Datos de Miembros:
- Información personal: nombre, alias, teléfonos
- Dirección completa: calle, depto, piso, barrio, coordenadas
- Datos médicos cifrados: condiciones, medicamentos, alergias, tipo sangre
- Contactos de emergencia: familia, coordinadores
- Configuración de evacuación: asistencia requerida, necesidades especiales

CUANDO PREGUNTEN SOBRE EL SISTEMA:
- Explica los comandos de forma clara y práctica
- Da ejemplos específicos de uso
- Menciona permisos necesarios (admin vs cualquier usuario)
- Sugiere flujos de trabajo útiles
- Explica beneficios de seguridad y funcionalidad

ESTILO DE RESPUESTA:
- Máximo 300 palabras para respuestas técnicas (250 para temas generales)
- Siempre amigable y positivo, con humor chileno sutil
- Si no sabes algo específico, lo admites con gracia chilena: "pucha, esa no me la cacho"
- Termina con el footer de Tailor Tech solo si la respuesta es larga
- Para respuestas cortas, no uses el footer
- Usa formato claro con emojis para comandos técnicos
- Incluye expresiones chilenas naturalmente en las respuestas

EJEMPLOS DE EXPRESIONES CHILENAS PARA USAR:
- "¡Bacán!" / "¡La raja!" (para algo genial)
- "Sí po" / "Ya po" (afirmaciones)
- "Cachai" / "¿cachai?" (¿entiendes?)
- "Al tiro" (inmediatamente)
- "Terrible bueno/malo" (muy bueno/malo)
- "Pucha" (expresión suave de sorpresa)
- "Oye" (para llamar atención)
- "Fome" (aburrido)
- "¿Cómo andai?" (¿cómo estás?)

CUANDO TE PREGUNTEN QUIÉN ERES:
Responde como vecino chileno simpático que maneja la tecnología:
"¡Hola! Soy Tailor, tu vecino digital del barrio 😄 Ando siempre por acá ayudando con el sistema de emergencias que armó Tailor Tech. Soy como el 'nerd' querido de la comunidad - me cacho toda la parte técnica pero con buena onda po. ¿En qué te puedo echar una mano?"

IMPORTANTE: Eres un vecino real chileno que maneja la tecnología. No menciones que eres AI a menos que te pregunten directamente. Usa el humor y las expresiones chilenas de forma natural y tierna."""

        user_prompt = f"""El vecino {sender_name} de {group_name} te pregunta: "{user_query}"

{chat_context}

Responde como Tailor, su vecino amigable. ¡Sé natural, cálido y útil!"""

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4o-mini",  # Cheapest OpenAI model
                    "messages": [
                        {
                            "role": "system", 
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "max_tokens": 350,  # Increased for technical responses
                    "temperature": 0.8  # Higher temperature for more personality
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions", 
                    headers=headers, 
                    json=payload,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_message = result['choices'][0]['message']['content'].strip()
                        
                        # Add Tailor Tech footer for longer responses
                        if len(ai_message) > 150:
                            ai_message += "\\n\\n💻 Desarrollado por Tailor Tech"
                        
                        print(f"🤖 Generated {len(ai_message)} character Tailor response")
                        return ai_message
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error {response.status}: {error_text}")
                        
        except Exception as e:
            print(f"❌ OpenAI request error: {str(e)}")
            raise e
    
    async def _auto_detect_new_member(self, message: WhatsAppMessage):
        """Automatically detect and add new group members to the database"""
        try:
            print(f"👥 AUTO-DETECT - Checking member: {message.from_phone} in {message.chat_name}")
            
            # Skip bot's own messages (don't add the bot as a member)
            # You can add your bot's phone number here to exclude it
            bot_numbers = [
                # Add your bot's phone numbers here if needed
                # "56999999999",  # Example bot number
            ]
            
            if message.from_phone in bot_numbers:
                print(f"👥 AUTO-DETECT - Skipping bot number: {message.from_phone}")
                return
            
            # Get current member data
            try:
                from app.services.group_manager_service import GroupManagerService
                group_manager = GroupManagerService()
                
                member_data = await group_manager.get_group_member_data(
                    message.chat_id, 
                    message.chat_name or "Unknown Group"
                )
                
                if not member_data:
                    print(f"👥 AUTO-DETECT - No group database found, member will be added when group is initialized")
                    return
                
                # Check if member already exists
                members = member_data.get("members", {})
                if message.from_phone in members:
                    print(f"👥 AUTO-DETECT - Member {message.from_phone} already exists")
                    return
                
                # Add new member with basic information
                print(f"🎯 AUTO-DETECT - Adding new member: {message.contact_name} ({message.from_phone})")
                
                new_member = {
                    "name": message.contact_name or "Vecino Nuevo",
                    "alias": [],
                    "address": {
                        "street": "",
                        "apartment": "",
                        "floor": "",
                        "neighborhood": "",
                        "city": "",
                        "coordinates": {"lat": None, "lng": None}
                    },
                    "contacts": {
                        "primary": message.from_phone,
                        "emergency": "",
                        "family": ""
                    },
                    "medical": {
                        "conditions": [],
                        "medications": [],
                        "allergies": [],
                        "blood_type": ""
                    },
                    "emergency_info": {
                        "is_admin": False,  # New members are not admins by default
                        "response_role": "member",
                        "evacuation_assistance": False,
                        "special_needs": []
                    },
                    "metadata": {
                        "joined_date": datetime.now().isoformat(),
                        "last_active": datetime.now().isoformat(),
                        "data_version": "1.0",
                        "auto_detected": True  # Flag to indicate this was auto-added
                    }
                }
                
                # Add to members dictionary
                member_data["members"][message.from_phone] = new_member
                
                # Update the database
                success = await group_manager.update_group_member_data(
                    message.chat_id,
                    message.chat_name or "Unknown Group", 
                    member_data
                )
                
                if success:
                    print(f"✅ AUTO-DETECT - Successfully added new member: {message.contact_name} ({message.from_phone})")
                    
                    # Optional: Send notification to group admins
                    admin_phones = member_data.get("admins", [])
                    if admin_phones:
                        notification = f"👥 NUEVO MIEMBRO DETECTADO\\n\\n" \
                                     f"📱 {message.contact_name or 'Usuario'} ({message.from_phone})\\n" \
                                     f"🏘️ Grupo: {message.chat_name}\\n" \
                                     f"📝 Agregado automáticamente al sistema\\n\\n" \
                                     f"💡 Usa @editar para completar su información\\n\\n" \
                                     f"💻 Sistema de Tailor Tech"
                        
                        # Send to first admin only to avoid spam
                        try:
                            await self._send_text_message(admin_phones[0], notification)
                        except Exception as notify_error:
                            print(f"⚠️ Could not notify admin: {notify_error}")
                else:
                    print(f"❌ AUTO-DETECT - Failed to add member to database")
                    
            except ImportError as e:
                print(f"❌ AUTO-DETECT - Group manager service not available: {str(e)}")
            except Exception as e:
                print(f"❌ AUTO-DETECT - Error accessing member database: {str(e)}")
                
        except Exception as e:
            print(f"❌ AUTO-DETECT - General error: {str(e)}")