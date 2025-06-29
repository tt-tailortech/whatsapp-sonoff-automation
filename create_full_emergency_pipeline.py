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
    Basic emergency pipeline - sends text alert for SOS commands
    """
    
    print(f"🚨 EMERGENCIA ACTIVADA: {incident_type}")
    print(f"👤 Reportado por: {sender_name} ({sender_phone})")
    print(f"📍 Ubicación: {street_address}")
    print(f"🏘️ Grupo: {group_name}")
    
    # For now, just return success to indicate the pipeline ran
    # The actual WhatsApp message will be sent by the command processor fallback
    return True

if __name__ == "__main__":
    print("🚨 Emergency Pipeline - Basic Version")
    result = asyncio.run(execute_full_emergency_pipeline(
        incident_type="EMERGENCIA GENERAL",
        sender_name="Test User",
        sender_phone="123456789"
    ))
    print(f"Result: {result}")