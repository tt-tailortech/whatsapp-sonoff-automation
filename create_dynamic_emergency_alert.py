#!/usr/bin/env python3
"""
Dynamic Emergency Alert Generator - Populated from WhatsApp message data
Integrates with WhatsApp sender to auto-populate contact info
"""

from create_emergency_alert_final import create_emergency_alert
from app.models import WhatsAppMessage
import os

def create_dynamic_emergency_alert_from_whatsapp(
    whatsapp_message: WhatsAppMessage,
    incident_type: str = "EMERGENCIA GENERAL",
    street_address: str = "Dirección por confirmar",
    emergency_number: str = "SAMU 131"
):
    """
    Create emergency alert populated with real WhatsApp sender data
    
    Args:
        whatsapp_message: WhatsApp message object with sender info
        incident_type: Type of emergency (customizable)
        street_address: Emergency location (placeholder until GPS integration)
        emergency_number: Emergency contact (customizable)
    """
    
    # Extract real data from WhatsApp message
    phone_number = whatsapp_message.from_phone or "Número no disponible"
    contact_name = whatsapp_message.contact_name or "Usuario WhatsApp"
    chat_id = whatsapp_message.chat_id or "Chat Comunitario"
    
    # Clean up phone number formatting
    if phone_number.startswith("+"):
        display_phone = phone_number
    elif phone_number.endswith("@s.whatsapp.net"):
        clean_number = phone_number.replace("@s.whatsapp.net", "")
        display_phone = f"+{clean_number}" if len(clean_number) > 8 else clean_number
    else:
        display_phone = phone_number
    
    # Determine neighborhood name from chat context
    if "@g.us" in chat_id:
        # Group chat - use group name or generic
        neighborhood_name = "Grupo Comunitario"
    else:
        # Individual chat - use generic neighborhood
        neighborhood_name = "Comunidad Local"
    
    print(f"🚨 Creating emergency alert from WhatsApp message:")
    print(f"   📱 From: {contact_name} ({display_phone})")
    print(f"   🏘️ Chat: {neighborhood_name}")
    print(f"   🚨 Type: {incident_type}")
    print(f"   📍 Location: {street_address}")
    
    # Call the main emergency alert generator with populated data
    try:
        image_path = create_emergency_alert(
            # === REQUIRED PARAMETERS IN ORDER ===
            street_address=street_address,
            phone_number=display_phone,
            contact_name=contact_name,
            neighborhood_name=neighborhood_name,
            incident_type=incident_type,
            
            # === OPTIONAL CUSTOMIZATIONS ===
            emergency_number=emergency_number,
            
            # === OPTIONAL CUSTOMIZATIONS (keep defaults) ===
            alert_title="EMERGENCIA",
            system_name="Sistema de Alarma Comunitaria",
            status_text="ACTIVO",
            show_night_sky=True,
            show_background_city=True
        )
        
        if image_path and os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ Dynamic emergency alert created: {os.path.basename(image_path)}")
            print(f"📊 Size: {file_size} bytes")
            return image_path
        else:
            print("❌ Failed to create dynamic emergency alert")
            return None
            
    except Exception as e:
        print(f"❌ Error creating dynamic alert: {str(e)}")
        return None

def create_test_emergency_alert_with_waldo():
    """Test with Waldo's data for demonstration"""
    
    # Simulate WhatsApp message from Waldo
    from app.models import WhatsAppMessage
    
    waldo_message = WhatsAppMessage(
        id="test_123",
        from_phone="56940035815",
        chat_id="56940035815@s.whatsapp.net", 
        text="Emergency test message",
        contact_name="Waldo",
        timestamp="1234567890"
    )
    
    print("🧪 Testing dynamic emergency alert with Waldo's data")
    print("=" * 60)
    
    # Create emergency alert with different scenarios
    test_scenarios = [
        {
            "incident_type": "EMERGENCIA MÉDICA",
            "street_address": "Avenida Las Condes 2024",
            "emergency_number": "SAMU 131"
        },
        {
            "incident_type": "INCENDIO REPORTADO", 
            "street_address": "Calle Providencia 1234",
            "emergency_number": "BOMBEROS 132"
        },
        {
            "incident_type": "SEGURIDAD COMUNITARIA",
            "street_address": "Plaza Central s/n",
            "emergency_number": "CARABINEROS 133"
        }
    ]
    
    created_alerts = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 Test Scenario {i}: {scenario['incident_type']}")
        
        image_path = create_dynamic_emergency_alert_from_whatsapp(
            whatsapp_message=waldo_message,
            **scenario
        )
        
        if image_path:
            created_alerts.append(image_path)
    
    print(f"\n📋 Results:")
    print(f"   ✅ Created {len(created_alerts)} dynamic emergency alerts")
    print(f"   📱 Populated with Waldo's contact info")
    print(f"   🎨 Beautiful night-themed design")
    print(f"   📱 Ready for WhatsApp sending")
    
    return created_alerts

if __name__ == "__main__":
    alerts = create_test_emergency_alert_with_waldo()
    if alerts:
        print(f"\n🚀 Dynamic emergency alert system ready!")
        print(f"💫 Automatically populates sender data from WhatsApp messages")
        print(f"🎯 Ready for group message integration")
    else:
        print(f"\n❌ Test failed!")