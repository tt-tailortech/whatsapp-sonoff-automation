#!/usr/bin/env python3
"""
Member Lookup Service
Provides member data lookup for emergency alerts using JSON member database
"""

from typing import Optional, Dict, Any
from app.services.group_manager_service import GroupManagerService

class MemberLookupService:
    def __init__(self):
        """Initialize member lookup service"""
        self.group_manager = GroupManagerService()
    
    async def get_member_emergency_data(self, sender_phone: str, group_chat_id: str, 
                                      group_name: str) -> Dict[str, Any]:
        """
        Get comprehensive member data for emergency alerts
        
        Returns enriched member data or fallback data if not found
        """
        try:
            print(f"🔍 Looking up emergency data for {sender_phone} in {group_name}")
            
            # Get group member data
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            
            if not member_data:
                print(f"⚠️ No member data found for group {group_name}")
                return self._create_fallback_data(sender_phone, group_name)
            
            # Find the sender in member data
            members = member_data.get("members", {})
            sender_data = members.get(sender_phone)
            
            if not sender_data:
                print(f"⚠️ Sender {sender_phone} not found in member database")
                return self._create_fallback_data(sender_phone, group_name, member_data)
            
            # Create comprehensive emergency data
            emergency_data = self._create_emergency_data(sender_data, sender_phone, member_data)
            
            print(f"✅ Found comprehensive emergency data for {emergency_data['name']}")
            return emergency_data
            
        except Exception as e:
            print(f"❌ Error looking up member data: {str(e)}")
            return self._create_fallback_data(sender_phone, group_name)
    
    def _create_emergency_data(self, sender_data: Dict, sender_phone: str, 
                             member_data: Dict) -> Dict[str, Any]:
        """Create comprehensive emergency data from member JSON"""
        
        # Extract member information
        name = sender_data.get("name", "Usuario Desconocido")
        address = sender_data.get("address", {})
        contacts = sender_data.get("contacts", {})
        medical = sender_data.get("medical", {})
        emergency_info = sender_data.get("emergency_info", {})
        
        # Build complete address string
        address_parts = []
        if address.get("street"):
            address_parts.append(address["street"])
        if address.get("apartment"):
            address_parts.append(f"Apt {address['apartment']}")
        if address.get("floor"):
            address_parts.append(f"Piso {address['floor']}")
        if address.get("neighborhood"):
            address_parts.append(address["neighborhood"])
        if address.get("city"):
            address_parts.append(address["city"])
        
        full_address = ", ".join(address_parts) if address_parts else "Dirección no registrada"
        
        # Emergency contacts
        emergency_contact = contacts.get("emergency") or contacts.get("family") or "No registrado"
        
        # Medical information
        medical_conditions = medical.get("conditions", [])
        blood_type = medical.get("blood_type", "")
        allergies = medical.get("allergies", [])
        medications = medical.get("medications", [])
        
        # Create medical summary
        medical_summary = []
        if blood_type:
            medical_summary.append(f"Tipo sangre: {blood_type}")
        if medical_conditions:
            medical_summary.append(f"Condiciones: {', '.join(medical_conditions)}")
        if allergies:
            medical_summary.append(f"Alergias: {', '.join(allergies)}")
        if medications:
            medical_summary.append(f"Medicamentos: {', '.join(medications)}")
        
        medical_info = "; ".join(medical_summary) if medical_summary else "Sin información médica registrada"
        
        # Special needs for evacuation
        special_needs = emergency_info.get("special_needs", [])
        evacuation_assistance = emergency_info.get("evacuation_assistance", False)
        
        evacuation_notes = []
        if evacuation_assistance:
            evacuation_notes.append("REQUIERE ASISTENCIA PARA EVACUACIÓN")
        if special_needs:
            evacuation_notes.append(f"Necesidades especiales: {', '.join(special_needs)}")
        
        evacuation_info = "; ".join(evacuation_notes) if evacuation_notes else ""
        
        # Group information
        group_name = member_data.get("group_name", "Grupo Desconocido")
        total_members = len(member_data.get("members", {}))
        
        # Emergency contacts from group metadata
        emergency_contacts = member_data.get("emergency_contacts", {})
        
        return {
            # Basic info
            "name": name,
            "phone": sender_phone,
            "group_name": group_name,
            "total_members": total_members,
            
            # Address info
            "full_address": full_address,
            "street": address.get("street", ""),
            "apartment": address.get("apartment", ""),
            "floor": address.get("floor", ""),
            "neighborhood": address.get("neighborhood", ""),
            "city": address.get("city", ""),
            "coordinates": address.get("coordinates", {"lat": None, "lng": None}),
            
            # Contact info
            "emergency_contact": emergency_contact,
            "primary_contact": contacts.get("primary", sender_phone),
            "family_contact": contacts.get("family", ""),
            
            # Medical info
            "medical_info": medical_info,
            "blood_type": blood_type,
            "medical_conditions": medical_conditions,
            "allergies": allergies,
            "medications": medications,
            
            # Emergency info
            "evacuation_info": evacuation_info,
            "evacuation_assistance": evacuation_assistance,
            "special_needs": special_needs,
            "is_admin": emergency_info.get("is_admin", False),
            "response_role": emergency_info.get("response_role", "member"),
            
            # Enhanced for emergency use
            "has_medical_conditions": len(medical_conditions) > 0,
            "has_special_needs": len(special_needs) > 0 or evacuation_assistance,
            "is_high_priority": evacuation_assistance or len(medical_conditions) > 0,
            
            # Group emergency contacts
            "group_emergency_contacts": {
                "samu": emergency_contacts.get("samu", "131"),
                "bomberos": emergency_contacts.get("bomberos", "132"),
                "carabineros": emergency_contacts.get("carabineros", "133"),
                "group_emergency_contact": emergency_contacts.get("group_emergency_contact", ""),
                "emergency_coordinator": emergency_contacts.get("emergency_coordinator", "")
            }
        }
    
    def _create_fallback_data(self, sender_phone: str, group_name: str, 
                            member_data: Dict = None) -> Dict[str, Any]:
        """Create fallback data when member not found in database"""
        
        total_members = len(member_data.get("members", {})) if member_data else 1
        
        return {
            # Basic info
            "name": "Usuario No Registrado",
            "phone": sender_phone,
            "group_name": group_name,
            "total_members": total_members,
            
            # Address info (empty)
            "full_address": "Dirección no registrada en sistema",
            "street": "",
            "apartment": "",
            "floor": "",
            "neighborhood": "",
            "city": "",
            "coordinates": {"lat": None, "lng": None},
            
            # Contact info
            "emergency_contact": "No registrado",
            "primary_contact": sender_phone,
            "family_contact": "",
            
            # Medical info (empty)
            "medical_info": "Información médica no disponible",
            "blood_type": "",
            "medical_conditions": [],
            "allergies": [],
            "medications": [],
            
            # Emergency info
            "evacuation_info": "",
            "evacuation_assistance": False,
            "special_needs": [],
            "is_admin": False,
            "response_role": "member",
            
            # Enhanced flags
            "has_medical_conditions": False,
            "has_special_needs": False,
            "is_high_priority": False,
            
            # Default group emergency contacts
            "group_emergency_contacts": {
                "samu": "131",
                "bomberos": "132", 
                "carabineros": "133",
                "group_emergency_contact": "",
                "emergency_coordinator": ""
            }
        }
    
    async def get_nearby_members(self, group_chat_id: str, group_name: str, 
                               incident_location: str = None) -> list:
        """
        Get list of nearby members for emergency coordination
        """
        try:
            member_data = await self.group_manager.get_group_member_data(group_chat_id, group_name)
            
            if not member_data:
                return []
            
            nearby_members = []
            members = member_data.get("members", {})
            
            for phone, member in members.items():
                member_info = {
                    "name": member.get("name", "Usuario"),
                    "phone": phone,
                    "address": member.get("address", {}).get("street", "Sin dirección"),
                    "emergency_contact": member.get("contacts", {}).get("emergency", ""),
                    "response_role": member.get("emergency_info", {}).get("response_role", "member"),
                    "evacuation_assistance": member.get("emergency_info", {}).get("evacuation_assistance", False)
                }
                nearby_members.append(member_info)
            
            # Sort by response role (coordinators first)
            nearby_members.sort(key=lambda x: 0 if x["response_role"] == "coordinator" else 1)
            
            return nearby_members
            
        except Exception as e:
            print(f"❌ Error getting nearby members: {str(e)}")
            return []


# Test function
async def test_member_lookup():
    """Test the member lookup service"""
    print("🧪 Testing Member Lookup Service")
    print("=" * 50)
    
    lookup = MemberLookupService()
    
    # Test with existing member
    print("\n🧪 Testing with existing member:")
    emergency_data = await lookup.get_member_emergency_data(
        sender_phone="19012976001",
        group_chat_id="120363400467632358@g.us", 
        group_name="TEST_ALARM"
    )
    
    print(f"✅ Emergency data retrieved:")
    print(f"   👤 Name: {emergency_data['name']}")
    print(f"   📍 Address: {emergency_data['full_address']}")
    print(f"   📞 Emergency Contact: {emergency_data['emergency_contact']}")
    print(f"   🩺 Medical: {emergency_data['medical_info']}")
    print(f"   🚨 High Priority: {emergency_data['is_high_priority']}")
    
    # Test with unknown member
    print("\n🧪 Testing with unknown member:")
    fallback_data = await lookup.get_member_emergency_data(
        sender_phone="56999999999",
        group_chat_id="120363400467632358@g.us",
        group_name="TEST_ALARM" 
    )
    
    print(f"✅ Fallback data:")
    print(f"   👤 Name: {fallback_data['name']}")
    print(f"   📍 Address: {fallback_data['full_address']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_member_lookup())