#!/usr/bin/env python3
"""
Simple SOS test to verify the emergency pipeline works
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from create_full_emergency_pipeline import execute_full_emergency_pipeline

async def test_simple_sos():
    """Test SOS INCENDIO emergency pipeline"""
    
    print("🧪 TESTING SIMPLE SOS INCENDIO")
    print("=" * 50)
    
    # Test SOS INCENDIO
    success = await execute_full_emergency_pipeline(
        incident_type="INCENDIO",
        street_address="Calle de Prueba 123",
        emergency_number="BOMBEROS 132",
        sender_phone="56940035815",
        sender_name="Waldo",
        group_chat_id="120363400467632358@g.us",
        group_name="TEST_ALARM",
        device_id="10011eafd1",
        blink_cycles=2,  # Shorter for testing
        voice_text="Emergencia de incendio reportada en Calle de Prueba ciento veintitrés. Contacto de emergencia: Bomberos uno tres dos. Reportado por Waldo. Evacúen el área inmediatamente."
    )
    
    if success:
        print(f"\n✅ SOS INCENDIO test successful!")
        return True
    else:
        print(f"\n❌ SOS INCENDIO test failed!")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_simple_sos())
    if result:
        print(f"\n🏆 SOS SYSTEM READY FOR PRODUCTION!")
    else:
        print(f"\n⚠️ SOS SYSTEM NEEDS DEBUGGING")