#!/usr/bin/env python3
"""
Bulk Data Service
Handles import/export of member data in various formats (CSV, JSON)
"""

import csv
import json
import io
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
from app.services.group_manager_service import GroupManagerService

class BulkDataService:
    def __init__(self):
        """Initialize bulk data service"""
        self.group_manager = GroupManagerService()
    
    async def export_group_members_csv(self, group_chat_id: str, group_name: str) -> Tuple[bool, str, str]:
        """
        Export group members to CSV format
        
        Returns (success: bool, csv_content: str, error_message: str)
        """
        try:
            print(f"📄 Exporting members for group: {group_name}")
            
            # Get member data
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not member_data:
                return False, "", "No se encontraron datos del grupo"
            
            members = member_data.get("members", {})
            if not members:
                return False, "", "No hay miembros para exportar"
            
            # Create CSV content
            csv_content = io.StringIO()
            writer = csv.writer(csv_content)
            
            # Write header
            headers = [
                "Teléfono", "Nombre", "Alias", "Calle", "Apartamento", "Piso", 
                "Barrio", "Ciudad", "Coordenadas", "Contacto Emergencia", 
                "Contacto Familia", "Condiciones Médicas", "Medicamentos", 
                "Alergias", "Tipo Sangre", "Es Admin", "Rol Respuesta", 
                "Asistencia Evacuación", "Necesidades Especiales", "Fecha Ingreso"
            ]
            writer.writerow(headers)
            
            # Write member data
            for phone, member in members.items():
                address = member.get("address", {})
                contacts = member.get("contacts", {})
                medical = member.get("medical", {})
                emergency_info = member.get("emergency_info", {})
                metadata = member.get("metadata", {})
                
                # Format coordinates
                coords = address.get("coordinates", {})
                coord_str = f"{coords.get('lat', '')},{coords.get('lng', '')}" if coords.get('lat') else ""
                
                row = [
                    phone,
                    member.get("name", ""),
                    "; ".join(member.get("alias", [])),
                    address.get("street", ""),
                    address.get("apartment", ""),
                    address.get("floor", ""),
                    address.get("neighborhood", ""),
                    address.get("city", ""),
                    coord_str,
                    contacts.get("emergency", ""),
                    contacts.get("family", ""),
                    "; ".join(medical.get("conditions", [])),
                    "; ".join(medical.get("medications", [])),
                    "; ".join(medical.get("allergies", [])),
                    medical.get("blood_type", ""),
                    emergency_info.get("is_admin", False),
                    emergency_info.get("response_role", "member"),
                    emergency_info.get("evacuation_assistance", False),
                    "; ".join(emergency_info.get("special_needs", [])),
                    metadata.get("joined_date", "")
                ]
                writer.writerow(row)
            
            csv_data = csv_content.getvalue()
            csv_content.close()
            
            print(f"✅ Exported {len(members)} members to CSV")
            return True, csv_data, ""
            
        except Exception as e:
            print(f"❌ Error exporting CSV: {str(e)}")
            return False, "", f"Error exportando CSV: {str(e)}"
    
    async def import_group_members_csv(self, group_chat_id: str, group_name: str, 
                                     csv_content: str, admin_phone: str) -> Tuple[bool, str]:
        """
        Import group members from CSV content
        
        Returns (success: bool, message: str)
        """
        try:
            print(f"📥 Importing members for group: {group_name}")
            
            # Check admin permissions
            if not await self._check_admin_permissions(admin_phone, group_chat_id, group_name):
                return False, "Solo los administradores pueden importar datos"
            
            # Get existing member data
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not member_data:
                return False, "Grupo no encontrado. Envía un mensaje para inicializar."
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            imported_count = 0
            updated_count = 0
            errors = []
            
            members = member_data.get("members", {})
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    phone = row.get("Teléfono", "").strip()
                    name = row.get("Nombre", "").strip()
                    
                    if not phone or not name:
                        errors.append(f"Fila {row_num}: Teléfono y nombre son requeridos")
                        continue
                    
                    # Parse coordinates
                    coord_str = row.get("Coordenadas", "").strip()
                    lat, lng = None, None
                    if coord_str and "," in coord_str:
                        try:
                            lat_str, lng_str = coord_str.split(",", 1)
                            lat = float(lat_str.strip()) if lat_str.strip() else None
                            lng = float(lng_str.strip()) if lng_str.strip() else None
                        except ValueError:
                            pass
                    
                    # Create member structure
                    member = {
                        "name": name,
                        "alias": [a.strip() for a in row.get("Alias", "").split(";") if a.strip()],
                        "address": {
                            "street": row.get("Calle", "").strip(),
                            "apartment": row.get("Apartamento", "").strip(),
                            "floor": row.get("Piso", "").strip(),
                            "neighborhood": row.get("Barrio", "").strip(),
                            "city": row.get("Ciudad", "").strip(),
                            "coordinates": {"lat": lat, "lng": lng}
                        },
                        "contacts": {
                            "primary": phone,
                            "emergency": row.get("Contacto Emergencia", "").strip(),
                            "family": row.get("Contacto Familia", "").strip()
                        },
                        "medical": {
                            "conditions": [c.strip() for c in row.get("Condiciones Médicas", "").split(";") if c.strip()],
                            "medications": [m.strip() for m in row.get("Medicamentos", "").split(";") if m.strip()],
                            "allergies": [a.strip() for a in row.get("Alergias", "").split(";") if a.strip()],
                            "blood_type": row.get("Tipo Sangre", "").strip()
                        },
                        "emergency_info": {
                            "is_admin": str(row.get("Es Admin", "")).lower() in ["true", "1", "sí", "si", "yes"],
                            "response_role": row.get("Rol Respuesta", "member").strip() or "member",
                            "evacuation_assistance": str(row.get("Asistencia Evacuación", "")).lower() in ["true", "1", "sí", "si", "yes"],
                            "special_needs": [s.strip() for s in row.get("Necesidades Especiales", "").split(";") if s.strip()]
                        },
                        "metadata": {
                            "joined_date": row.get("Fecha Ingreso", "").strip() or datetime.now().isoformat(),
                            "last_active": datetime.now().isoformat(),
                            "data_version": "1.0"
                        }
                    }
                    
                    # Check if member exists
                    if phone in members:
                        updated_count += 1
                    else:
                        imported_count += 1
                    
                    members[phone] = member
                    
                    # Add to admins if is_admin is true
                    if member["emergency_info"]["is_admin"]:
                        admins = member_data.setdefault("admins", [])
                        if phone not in admins:
                            admins.append(phone)
                    
                except Exception as e:
                    errors.append(f"Fila {row_num}: {str(e)}")
            
            # Update member data
            member_data["members"] = members
            success = await self.group_manager.update_group_member_data(group_chat_id, group_name, member_data)
            
            if success:
                message = f"✅ Importación completada:\n"
                message += f"   📥 Nuevos miembros: {imported_count}\n"
                message += f"   🔄 Miembros actualizados: {updated_count}"
                
                if errors:
                    message += f"\n⚠️ Errores ({len(errors)}):\n"
                    message += "\n".join(errors[:5])  # Show first 5 errors
                    if len(errors) > 5:
                        message += f"\n... y {len(errors) - 5} errores más"
                
                return True, message
            else:
                return False, "Error guardando datos importados"
                
        except Exception as e:
            print(f"❌ Error importing CSV: {str(e)}")
            return False, f"Error importando CSV: {str(e)}"
    
    async def export_group_members_json(self, group_chat_id: str, group_name: str) -> Tuple[bool, str, str]:
        """
        Export group members to JSON format
        
        Returns (success: bool, json_content: str, error_message: str)
        """
        try:
            print(f"📄 Exporting JSON for group: {group_name}")
            
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not member_data:
                return False, "", "No se encontraron datos del grupo"
            
            # Add export metadata
            export_data = {
                "export_info": {
                    "exported_at": datetime.now().isoformat(),
                    "group_name": group_name,
                    "group_id": group_chat_id,
                    "total_members": len(member_data.get("members", {})),
                    "export_version": "1.0"
                },
                "group_data": member_data
            }
            
            json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported JSON for group: {group_name}")
            return True, json_content, ""
            
        except Exception as e:
            print(f"❌ Error exporting JSON: {str(e)}")
            return False, "", f"Error exportando JSON: {str(e)}"
    
    async def import_group_members_json(self, group_chat_id: str, group_name: str, 
                                      json_content: str, admin_phone: str) -> Tuple[bool, str]:
        """
        Import group members from JSON content
        
        Returns (success: bool, message: str)
        """
        try:
            print(f"📥 Importing JSON for group: {group_name}")
            
            # Check admin permissions
            if not await self._check_admin_permissions(admin_phone, group_chat_id, group_name):
                return False, "Solo los administradores pueden importar datos"
            
            # Parse JSON
            import_data = json.loads(json_content)
            
            # Validate JSON structure
            if "group_data" not in import_data:
                return False, "Formato JSON inválido: falta 'group_data'"
            
            imported_group_data = import_data["group_data"]
            
            if "members" not in imported_group_data:
                return False, "Formato JSON inválido: falta 'members'"
            
            # Get current data
            current_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not current_data:
                return False, "Grupo no encontrado. Envía un mensaje para inicializar."
            
            # Merge imported data with current data
            imported_members = imported_group_data["members"]
            current_members = current_data.get("members", {})
            
            imported_count = 0
            updated_count = 0
            
            for phone, member_data in imported_members.items():
                if phone in current_members:
                    updated_count += 1
                else:
                    imported_count += 1
                
                # Update metadata
                member_data.setdefault("metadata", {})
                member_data["metadata"]["last_active"] = datetime.now().isoformat()
                member_data["metadata"]["data_version"] = "1.0"
                
                current_members[phone] = member_data
            
            # Update group data
            current_data["members"] = current_members
            current_data["last_updated"] = datetime.now().isoformat()
            
            # Merge admins
            imported_admins = imported_group_data.get("admins", [])
            current_admins = current_data.get("admins", [])
            for admin in imported_admins:
                if admin not in current_admins:
                    current_admins.append(admin)
            current_data["admins"] = current_admins
            
            # Merge emergency contacts if not already configured
            if "emergency_contacts" in imported_group_data:
                current_data.setdefault("emergency_contacts", {}).update(imported_group_data["emergency_contacts"])
            
            # Save updated data
            success = await self.group_manager.update_group_member_data(group_chat_id, group_name, current_data)
            
            if success:
                export_info = import_data.get("export_info", {})
                source_group = export_info.get("group_name", "grupo desconocido")
                
                message = f"✅ Importación JSON completada:\n"
                message += f"   📥 Nuevos miembros: {imported_count}\n"
                message += f"   🔄 Miembros actualizados: {updated_count}\n"
                message += f"   🔗 Origen: {source_group}"
                
                return True, message
            else:
                return False, "Error guardando datos importados"
                
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {str(e)}"
        except Exception as e:
            print(f"❌ Error importing JSON: {str(e)}")
            return False, f"Error importando JSON: {str(e)}"
    
    async def create_member_template_csv(self) -> str:
        """
        Create a CSV template for member data entry
        
        Returns CSV template content
        """
        template_data = [
            [
                "Teléfono", "Nombre", "Alias", "Calle", "Apartamento", "Piso",
                "Barrio", "Ciudad", "Coordenadas", "Contacto Emergencia",
                "Contacto Familia", "Condiciones Médicas", "Medicamentos",
                "Alergias", "Tipo Sangre", "Es Admin", "Rol Respuesta",
                "Asistencia Evacuación", "Necesidades Especiales", "Fecha Ingreso"
            ],
            [
                "+56912345678", "Ana Martinez", "Anita", "Av. Las Condes 123", "15B", "3",
                "Las Condes", "Santiago", "-33.4242,-70.5694", "+56987654321",
                "+56956789012", "Diabetes; Hipertensión", "Metformina; Losartán",
                "Penicilina", "O+", "false", "coordinator", "false", "Movilidad reducida", "2025-01-01T00:00:00"
            ],
            [
                "+56923456789", "Carlos Rodriguez", "", "Calle Principal 456", "", "",
                "Providencia", "Santiago", "", "+56934567890",
                "", "", "", "", "A-", "true", "member", "true", "", "2025-01-01T00:00:00"
            ]
        ]
        
        csv_content = io.StringIO()
        writer = csv.writer(csv_content)
        for row in template_data:
            writer.writerow(row)
        
        template = csv_content.getvalue()
        csv_content.close()
        
        return template
    
    async def _check_admin_permissions(self, sender_phone: str, group_chat_id: str, group_name: str) -> bool:
        """Check if sender has admin permissions"""
        try:
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            if not member_data:
                return False
            
            # Check if sender is in admins list
            admins = member_data.get("admins", [])
            is_admin = sender_phone in admins
            
            # Also check if sender has admin flag
            members = member_data.get("members", {})
            sender_data = members.get(sender_phone, {})
            has_admin_flag = sender_data.get("emergency_info", {}).get("is_admin", False)
            
            return is_admin or has_admin_flag
            
        except Exception as e:
            print(f"❌ Error checking admin permissions: {str(e)}")
            return False


# Test functions
async def test_bulk_export():
    """Test bulk export functionality"""
    print("🧪 Testing Bulk Export")
    print("=" * 50)
    
    bulk_service = BulkDataService()
    
    # Test CSV export
    print("\n📄 Testing CSV export...")
    success, csv_content, error = await bulk_service.export_group_members_csv(
        "120363400467632358@g.us", "TEST_ALARM"
    )
    
    if success:
        print(f"✅ CSV export successful: {len(csv_content)} characters")
        print(f"📝 First 200 chars: {csv_content[:200]}...")
    else:
        print(f"❌ CSV export failed: {error}")
    
    # Test JSON export
    print("\n📄 Testing JSON export...")
    success, json_content, error = await bulk_service.export_group_members_json(
        "120363400467632358@g.us", "TEST_ALARM"
    )
    
    if success:
        print(f"✅ JSON export successful: {len(json_content)} characters")
    else:
        print(f"❌ JSON export failed: {error}")
    
    # Test template creation
    print("\n📋 Testing template creation...")
    template = await bulk_service.create_member_template_csv()
    print(f"✅ Template created: {len(template)} characters")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_bulk_export())