#!/usr/bin/env python3
"""
Member Editor Service
Processes @editar commands using ChatGPT to interpret Spanish natural language
and update member JSON data in Google Drive
"""

import os
import json
import aiohttp
from typing import Tuple, Dict, Any
from app.services.group_manager_service import GroupManagerService

class MemberEditorService:
    def __init__(self):
        """Initialize member editor service"""
        self.group_manager = GroupManagerService()
        self._audit_service = None
        self._initialize_audit()
    
    def _initialize_audit(self):
        """Initialize audit service"""
        try:
            from app.services.audit_service import AuditService
            self._audit_service = AuditService()
            print(f"📝 Audit service loaded for member editor")
        except ImportError as e:
            print(f"⚠️ Audit service not available: {str(e)}")
            self._audit_service = None
        
    async def process_editar_command(self, command_text: str, sender_phone: str, 
                                   group_chat_id: str, group_name: str, 
                                   sender_name: str) -> Tuple[bool, str]:
        """
        Process @editar command using ChatGPT to interpret and execute
        
        Returns (success: bool, response_message: str)
        """
        try:
            print(f"📝 Processing @editar command: {command_text}")
            
            # Check if sender has admin permissions
            if not await self._check_admin_permissions(sender_phone, group_chat_id, group_name):
                return False, "❌ Solo los administradores pueden usar comandos @editar"
            
            # Get current member data for context
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not member_data:
                return False, "❌ No se encontraron datos del grupo. Envía un mensaje para inicializar."
            
            # Use ChatGPT to interpret the command
            interpretation = await self._interpret_command_with_gpt(command_text, member_data)
            if not interpretation:
                return False, "❌ No se pudo interpretar el comando. Usa formato: @editar [acción] [miembro] [datos]"
            
            # Execute the interpreted command
            success, message = await self._execute_command(interpretation, member_data, group_chat_id, group_name, sender_phone, sender_name)
            
            if success:
                print(f"✅ @editar command executed successfully")
                return True, f"✅ {message}"
            else:
                print(f"❌ @editar command failed: {message}")
                return False, f"❌ {message}"
                
        except Exception as e:
            print(f"❌ Error processing @editar command: {str(e)}")
            return False, f"❌ Error procesando comando: {str(e)}"
    
    async def _check_admin_permissions(self, sender_phone: str, group_chat_id: str, group_name: str) -> bool:
        """Check if sender has admin permissions"""
        try:
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not member_data:
                return False
            
            # Check if sender is in admins list
            admins = member_data.get("admins", [])
            is_admin = sender_phone in admins
            
            # Also check if sender has admin flag in their member data
            members = member_data.get("members", {})
            sender_data = members.get(sender_phone, {})
            has_admin_flag = sender_data.get("emergency_info", {}).get("is_admin", False)
            
            return is_admin or has_admin_flag
            
        except Exception as e:
            print(f"❌ Error checking admin permissions: {str(e)}")
            return False
    
    async def _interpret_command_with_gpt(self, command_text: str, member_data: Dict) -> Dict[str, Any]:
        """Use ChatGPT to interpret Spanish @editar command"""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                print("❌ OpenAI API key not configured")
                return None
            
            # Get member list for context
            members = member_data.get("members", {})
            member_list = []
            for phone, data in members.items():
                name = data.get("name", "Sin nombre")
                member_list.append(f"- {name} ({phone})")
            
            member_context = "\n".join(member_list) if member_list else "- No hay miembros registrados"
            
            prompt = f"""Eres un asistente para interpretar comandos de edición de datos de miembros en español.

COMANDO A INTERPRETAR: {command_text}

MIEMBROS ACTUALES:
{member_context}

ACCIONES VÁLIDAS:
- agregar/añadir: agregar nuevo miembro
- actualizar/modificar/cambiar: modificar miembro existente  
- eliminar/borrar: eliminar miembro
- dirección/direccion: cambiar dirección
- teléfono/telefono/celular: cambiar número
- médico/medico/salud: información médica
- emergencia: contacto de emergencia
- admin/administrador: hacer administrador

FORMATO DE RESPUESTA (JSON):
{{
  "action": "agregar|actualizar|eliminar",
  "target_phone": "número de teléfono del miembro (si aplica)",
  "target_name": "nombre del miembro (si se menciona)",
  "field": "name|address|phone|medical|emergency_contact|admin",
  "value": "nuevo valor",
  "details": "explicación de lo que se hará"
}}

EJEMPLOS:
- "@editar agregar Ana teléfono +56912345678" → {{"action":"agregar", "target_phone":"+56912345678", "target_name":"Ana", "field":"name", "value":"Ana"}}
- "@editar cambiar dirección Carlos Av. Las Condes 123" → {{"action":"actualizar", "target_name":"Carlos", "field":"address", "value":"Av. Las Condes 123"}}
- "@editar eliminar usuario +56987654321" → {{"action":"eliminar", "target_phone":"+56987654321"}}

Interpreta el comando y responde SOLO con el JSON:"""

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Eres un experto en interpretar comandos en español para editar datos de miembros. Responde SIEMPRE con JSON válido."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.1
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        gpt_response = result['choices'][0]['message']['content'].strip()
                        print(f"🤖 GPT interpretation: {gpt_response}")
                        
                        # Clean and parse JSON response
                        if gpt_response.startswith("```json"):
                            gpt_response = gpt_response.replace("```json", "").replace("```", "").strip()
                        elif gpt_response.startswith("```"):
                            gpt_response = gpt_response.replace("```", "").strip()
                        
                        interpretation = json.loads(gpt_response)
                        return interpretation
                    else:
                        print(f"❌ OpenAI API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error interpreting command: {str(e)}")
            return None
    
    async def _execute_command(self, interpretation: Dict, member_data: Dict, 
                             group_chat_id: str, group_name: str, sender_phone: str, sender_name: str) -> Tuple[bool, str]:
        """Execute the interpreted command"""
        try:
            action = interpretation.get("action")
            target_phone = interpretation.get("target_phone", "").strip()
            target_name = interpretation.get("target_name", "").strip()
            field = interpretation.get("field")
            value = interpretation.get("value", "").strip()
            
            members = member_data.get("members", {})
            
            if action == "agregar":
                return await self._add_member(members, target_phone, target_name, member_data, group_chat_id, group_name, sender_phone, sender_name)
            elif action == "actualizar":
                return await self._update_member(members, target_phone, target_name, field, value, member_data, group_chat_id, group_name, sender_phone, sender_name)
            elif action == "eliminar":
                return await self._remove_member(members, target_phone, target_name, member_data, group_chat_id, group_name, sender_phone, sender_name)
            else:
                return False, f"Acción no reconocida: {action}"
                
        except Exception as e:
            return False, f"Error ejecutando comando: {str(e)}"
    
    async def _add_member(self, members: Dict, phone: str, name: str, member_data: Dict, 
                         group_chat_id: str, group_name: str, sender_phone: str, sender_name: str) -> Tuple[bool, str]:
        """Add new member"""
        if not phone or not name:
            return False, "Se requiere teléfono y nombre para agregar miembro"
        
        if phone in members:
            return False, f"El miembro {name} ({phone}) ya existe"
        
        # Add new member with basic structure
        members[phone] = {
            "name": name,
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
                "primary": phone,
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
                "is_admin": False,
                "response_role": "member",
                "evacuation_assistance": False,
                "special_needs": []
            },
            "metadata": {
                "joined_date": "2025-06-29T00:00:00",
                "last_active": "2025-06-29T00:00:00",
                "data_version": "1.0"
            }
        }
        
        # Update member data
        member_data["members"] = members
        success = await self.group_manager.update_group_member_data(group_chat_id, group_name, member_data)
        
        if success:
            # Log the audit event
            if self._audit_service:
                await self._audit_service.log_member_change(
                    action="add",
                    group_chat_id=group_chat_id,
                    group_name=group_name,
                    admin_phone=sender_phone,
                    admin_name=sender_name,
                    target_phone=phone,
                    target_name=name,
                    additional_info={"command_used": "@editar", "method": "natural_language"}
                )
            
            return True, f"Miembro {name} ({phone}) agregado exitosamente"
        else:
            return False, "Error guardando datos del nuevo miembro"
    
    async def _update_member(self, members: Dict, phone: str, name: str, field: str, value: str,
                           member_data: Dict, group_chat_id: str, group_name: str, sender_phone: str, sender_name: str) -> Tuple[bool, str]:
        """Update existing member"""
        # Find member by phone or name
        target_member = None
        target_phone = None
        
        if phone and phone in members:
            target_member = members[phone]
            target_phone = phone
        elif name:
            # Search by name
            for p, m in members.items():
                if m.get("name", "").lower() == name.lower():
                    target_member = m
                    target_phone = p
                    break
        
        if not target_member:
            return False, f"No se encontró miembro: {name or phone}"
        
        # Update specific field
        if field == "name":
            target_member["name"] = value
        elif field == "address":
            target_member["address"]["street"] = value
        elif field == "phone":
            # Move member data to new phone number
            del members[target_phone]
            target_member["contacts"]["primary"] = value
            members[value] = target_member
            target_phone = value
        elif field == "emergency_contact":
            target_member["contacts"]["emergency"] = value
        elif field == "medical":
            if "condición" in value.lower() or "condicion" in value.lower():
                target_member["medical"]["conditions"].append(value)
            else:
                target_member["medical"]["conditions"] = [value]
        elif field == "admin":
            target_member["emergency_info"]["is_admin"] = True
            if target_phone not in member_data.get("admins", []):
                member_data.setdefault("admins", []).append(target_phone)
        
        # Update member data
        member_data["members"] = members
        success = await self.group_manager.update_group_member_data(group_chat_id, group_name, member_data)
        
        if success:
            # Log the audit event
            if self._audit_service:
                await self._audit_service.log_member_change(
                    action="update",
                    group_chat_id=group_chat_id,
                    group_name=group_name,
                    admin_phone=sender_phone,
                    admin_name=sender_name,
                    target_phone=target_phone,
                    target_name=target_member['name'],
                    field_changed=field,
                    old_value="[PREVIOUS_VALUE]",  # Could store old value if needed
                    new_value=value,
                    additional_info={"command_used": "@editar", "method": "natural_language"}
                )
            
            return True, f"Miembro {target_member['name']} actualizado: {field} = {value}"
        else:
            return False, "Error guardando cambios"
    
    async def _remove_member(self, members: Dict, phone: str, name: str, member_data: Dict,
                           group_chat_id: str, group_name: str, sender_phone: str, sender_name: str) -> Tuple[bool, str]:
        """Remove member"""
        # Find member to remove
        target_phone = None
        target_name = ""
        
        if phone and phone in members:
            target_phone = phone
            target_name = members[phone].get("name", "")
        elif name:
            for p, m in members.items():
                if m.get("name", "").lower() == name.lower():
                    target_phone = p
                    target_name = m.get("name", "")
                    break
        
        if not target_phone:
            return False, f"No se encontró miembro: {name or phone}"
        
        # Remove member
        del members[target_phone]
        
        # Remove from admins if present
        admins = member_data.get("admins", [])
        if target_phone in admins:
            admins.remove(target_phone)
            member_data["admins"] = admins
        
        # Update member data
        member_data["members"] = members
        success = await self.group_manager.update_group_member_data(group_chat_id, group_name, member_data)
        
        if success:
            # Log the audit event
            if self._audit_service:
                await self._audit_service.log_member_change(
                    action="delete",
                    group_chat_id=group_chat_id,
                    group_name=group_name,
                    admin_phone=sender_phone,
                    admin_name=sender_name,
                    target_phone=target_phone,
                    target_name=target_name,
                    additional_info={"command_used": "@editar", "method": "natural_language"}
                )
            
            return True, f"Miembro {target_name} ({target_phone}) eliminado exitosamente"
        else:
            return False, "Error eliminando miembro"


# Test function
async def test_member_editor():
    """Test the member editor service"""
    print("🧪 Testing Member Editor Service")
    print("=" * 50)
    
    editor = MemberEditorService()
    
    # Test cases
    test_commands = [
        "@editar agregar Ana teléfono +56912345678",
        "@editar cambiar dirección Carlos Av. Las Condes 123",
        "@editar eliminar usuario +56987654321"
    ]
    
    for command in test_commands:
        print(f"\n🧪 Testing command: {command}")
        
        success, response = await editor.process_editar_command(
            command_text=command,
            sender_phone="19012976001",  # Test admin phone
            group_chat_id="120363400467632358@g.us",
            group_name="TEST_ALARM",
            sender_name="Test Admin"
        )
        
        print(f"✅ Result: {success}")
        print(f"📝 Response: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_member_editor())