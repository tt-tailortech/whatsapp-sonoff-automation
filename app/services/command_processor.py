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
        
        # Lazy load services
        self._member_editor = None
        self._bulk_data_service = None
        self._backup_service = None
    
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
        """Check if message contains SOS in any combination (case insensitive, flexible spacing)"""
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
        
        # More precise SOS detection patterns - avoid false positives
        # Only match SOS at the very beginning of the message (not embedded in text)
        sos_patterns = [
            r'^\s*SOS\b',         # SOS at start of message
            r'^\s*S\.?O\.?S\.?\b',  # S.O.S at start of message
        ]
        
        print(f"🚨 SOS DEBUG - Testing patterns against: '{cleaned_text[:50]}...'")
        
        for pattern in sos_patterns:
            if re.search(pattern, cleaned_text):
                print(f"🚨 SOS DEBUG - MATCHED PATTERN: {pattern}")
                return True
        
        print(f"🚨 SOS DEBUG - NO PATTERNS MATCHED")
        return False
    
    def _extract_incident_type(self, text: str) -> str:
        """Extract incident type from SOS message (max 2 words after SOS)"""
        # Clean and normalize text
        cleaned_text = text.strip().upper()
        
        # Find SOS and extract text after it
        sos_patterns = [
            r'\bSOS\s+(.+)',      # SOS followed by space and text
            r'S\.?O\.?S\.?\s+(.+)',  # S.O.S variations followed by text
        ]
        
        incident_text = ""
        for pattern in sos_patterns:
            match = re.search(pattern, cleaned_text)
            if match:
                incident_text = match.group(1).strip()
                break
        
        if incident_text:
            # Split into words and take maximum 2 words
            words = incident_text.split()
            if len(words) > 2:
                # Take only first 2 words
                incident_text = " ".join(words[:2])
            
            print(f"🎯 Extracted incident type: '{incident_text}' from '{text}'")
            return incident_text
        else:
            # Default if just "SOS" with no additional text
            print(f"🎯 Using default incident type for: '{text}'")
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
            
            # Generate system information message
            info_message = f"""🚨{'='*60}
🚨 WHATSAPP EMERGENCY COMMAND SYSTEM INITIALIZED
🚨{'='*60}

📢 CONFIGURED TRIGGER KEYWORDS:
   1. 'SOS' - Activates emergency response system

🎯 SUPPORTED MESSAGE PATTERNS:
   • SOS → EMERGENCIA GENERAL
   • sos → EMERGENCIA GENERAL
   • SOS INCENDIO → INCENDIO
   • SOS EMERGENCIA MÉDICA → EMERGENCIA MÉDICA
   • SOS ACCIDENTE VEHICULAR → ACCIDENTE VEHICULAR (max 2 words)
   • S.O.S TERREMOTO → TERREMOTO
   • Any message containing SOS triggers emergency response

📱 TARGET GROUP CHAT: TEST_ALARM (120363400467632358@g.us)
🔧 DEVICE CONTROL: Sonoff switches integrated
🎤 VOICE ALERTS: OpenAI TTS (Spanish)
📷 IMAGE ALERTS: ✅ Available
⚡ STATUS: 🟢 OPERATIONAL

📝 AVAILABLE COMMANDS:
   • @info - Show this system information
   • @editar - Edit member data (admins only)
   • @exportar [csv/json] - Export member data
   • @importar - Import member data
   • @plantilla - Get CSV template
   • @backup [group/full] - Create backup
   • @restore [backup_name] - Restore backup
   • @backups - List available backups

🚨{'='*60}
🚨 EMERGENCY SYSTEM READY FOR WHATSAPP MESSAGES
🚨{'='*60}"""

            await self._send_text_message(message.chat_id, info_message)
            print("✅ @info system information sent")
                
        except Exception as e:
            print(f"❌ Error processing @info command: {str(e)}")
            await self._send_text_message(message.chat_id, f"❌ Error procesando comando @info: {str(e)}")
    
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