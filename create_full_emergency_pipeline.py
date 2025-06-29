#!/usr/bin/env python3
"""
Basic Emergency Pipeline for SOS Commands
Sends emergency text alert when SOS is detected
"""

import asyncio
import time
from datetime import datetime

async def execute_full_emergency_pipeline(
    incident_type: str = "EMERGENCIA GENERAL",
    street_address: str = "Ubicación por confirmar", 
    emergency_number: str = "SAMU 131",
    sender_phone: str = "",
    sender_name: str = "Usuario",
    group_chat_id: str = "",
    group_name: str = "Grupo de Emergencia",
    device_id: str = "10011eafd1",
    blink_cycles: int = 3,
    voice_text: str = None
):
    """
    Emergency pipeline with WhatsApp message response
    """
    
    print(f"🚨 EMERGENCIA ACTIVADA: {incident_type}")
    print(f"👤 Reportado por: {sender_name} ({sender_phone})")
    print(f"📍 Ubicación: {street_address}")
    print(f"🏘️ Grupo: {group_name}")
    
    # Import WhatsApp service to send response
    try:
        from app.services.whatsapp_service import WhatsAppService
        whatsapp_service = WhatsAppService()
        
        # Create emergency alert message
        alert_message = f"""🚨 EMERGENCIA ACTIVADA 🚨

📋 TIPO: {incident_type}
📍 UBICACIÓN: {street_address}
👤 REPORTADO POR: {sender_name}
📞 CONTACTO: {sender_phone}

🚑 EMERGENCIA: {emergency_number}
⏰ HORA: {datetime.now().strftime('%H:%M:%S')}
📅 FECHA: {datetime.now().strftime('%d/%m/%Y')}

⚠️ MANTÉNGANSE SEGUROS
📢 SIGAN INSTRUCCIONES OFICIALES"""

        # Send alert to group
        print(f"📤 Enviando alerta de emergencia al grupo...")
        success = await whatsapp_service.send_text_message(group_chat_id, alert_message)
        
        if success:
            print(f"✅ Alerta de emergencia enviada al grupo")
            return True
        else:
            print(f"❌ Falló el envío de la alerta al grupo")
            return False
            
    except Exception as e:
        print(f"❌ Error en pipeline de emergencia: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 Emergency Pipeline - Basic Version")
    result = asyncio.run(execute_full_emergency_pipeline(
        incident_type="EMERGENCIA GENERAL",
        sender_name="Test User",
        sender_phone="123456789"
    ))
    print(f"Result: {result}")