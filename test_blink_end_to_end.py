#!/usr/bin/env python3
"""
Test complete blink pattern functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ewelink_service import EWeLinkService
from app.services.command_processor import CommandProcessor
from app.services.whatsapp_service import WhatsAppService

async def test_blink_pattern():
    """Test the blink pattern directly"""
    
    print("🧪 Testing Complete Blink Pattern")
    print("=" * 50)
    
    try:
        # Initialize services
        ewelink = EWeLinkService()
        whatsapp = WhatsAppService()
        processor = CommandProcessor(whatsapp, ewelink)
        
        print("✅ Services initialized")
        
        # Get device ID
        device_id = await processor._get_device_id()
        if not device_id:
            print("❌ No device found")
            return False
            
        print(f"🔍 Using device: {device_id}")
        
        # Test blink pattern
        print("🔄 Starting blink pattern test...")
        success = await processor._perform_blink_pattern(device_id)
        
        if success:
            print("✅ Blink pattern completed successfully!")
        else:
            print("❌ Blink pattern failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_commands():
    """Test individual device commands"""
    
    print("\n🧪 Testing Individual Device Commands")
    print("=" * 40)
    
    try:
        ewelink = EWeLinkService()
        
        # Get first device
        devices = await ewelink.get_devices()
        if not devices:
            print("❌ No devices found")
            return False
            
        device_id = devices[0].deviceid
        print(f"🔍 Testing device: {devices[0].name} ({device_id})")
        
        # Test ON command
        print("🔄 Testing ON command...")
        on_result = await ewelink.control_device(device_id, "ON")
        print(f"ON result: {'✅' if on_result else '❌'}")
        
        await asyncio.sleep(2)
        
        # Test OFF command
        print("🔄 Testing OFF command...")
        off_result = await ewelink.control_device(device_id, "OFF")
        print(f"OFF result: {'✅' if off_result else '❌'}")
        
        await asyncio.sleep(2)
        
        # Test final ON
        print("🔄 Testing final ON command...")
        final_on = await ewelink.control_device(device_id, "ON")
        print(f"Final ON result: {'✅' if final_on else '❌'}")
        
        return on_result and off_result and final_on
        
    except Exception as e:
        print(f"❌ Individual command test error: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Starting End-to-End Blink Test")
        print("=" * 60)
        
        # Test 1: Individual commands
        individual_success = asyncio.run(test_individual_commands())
        
        # Test 2: Complete blink pattern
        blink_success = asyncio.run(test_blink_pattern())
        
        print(f"\n📊 Test Results:")
        print(f"Individual commands: {'✅ PASS' if individual_success else '❌ FAIL'}")
        print(f"Blink pattern: {'✅ PASS' if blink_success else '❌ FAIL'}")
        
        if individual_success and blink_success:
            print("\n🎉 ALL TESTS PASSED! System ready for WhatsApp integration.")
        else:
            print("\n⚠️ Some tests failed. Check device connection and API credentials.")
            
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        import traceback
        traceback.print_exc()