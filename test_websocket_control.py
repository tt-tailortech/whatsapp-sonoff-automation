#!/usr/bin/env python3
"""
Test eWeLink WebSocket control with pro account
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ewelink_websocket_service import EWeLinkWebSocketService

async def test_websocket_control():
    """Test WebSocket device control"""
    
    print("🧪 Testing eWeLink WebSocket Control")
    print("=" * 50)
    
    # Create WebSocket service
    service = EWeLinkWebSocketService()
    
    print(f"🔐 App ID: {service.app_id[:10]}...")
    print(f"📧 Email: {service.email}")
    print(f"📱 Test Device: {service.test_device_id}")
    print(f"🔑 API Key: {service.api_key[:10]}...")
    
    # Test authentication
    print("\n🔄 Authenticating with WebSocket...")
    auth_success = await service.authenticate(service.email, service.password)
    
    if not auth_success:
        print("❌ WebSocket authentication failed")
        return False
    
    print("✅ WebSocket authentication successful!")
    
    # Test device control
    print(f"\n🎛️ Testing device control...")
    
    try:
        # Test ON command
        print("🔴➡️🔵 Testing ON command...")
        on_success = await service.control_device(service.test_device_id, "ON")
        
        if on_success:
            print("✅ ON command successful!")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Test OFF command
            print("🔵➡️⚫ Testing OFF command...")
            off_success = await service.control_device(service.test_device_id, "OFF")
            
            if off_success:
                print("✅ OFF command successful!")
                print("🎉 WebSocket control test completed!")
                return True
            else:
                print("❌ OFF command failed")
                return False
        else:
            print("❌ ON command failed")
            return False
            
    except Exception as e:
        print(f"❌ Control test error: {e}")
        return False
    
    finally:
        # Disconnect WebSocket
        await service.disconnect()

async def test_alarm_scenario():
    """Test alarm scenario with WebSocket"""
    
    print("\n🚨 Testing WebSocket Alarm Scenario")
    print("=" * 40)
    
    service = EWeLinkWebSocketService()
    
    # Authenticate
    auth_success = await service.authenticate(service.email, service.password)
    if not auth_success:
        print("❌ Cannot test alarm - authentication failed")
        return False
    
    try:
        # Get devices
        devices = await service.get_devices()
        print(f"🎯 Found {len(devices)} devices for alarm test")
        
        # Test alarm activation
        print("🔥 ALARM ACTIVATED! Turning devices ON...")
        
        success_count = 0
        for device in devices:
            print(f"   🔴➡️🔵 Activating {device.name}...")
            success = await service.control_device(device.deviceid, "ON")
            if success:
                print(f"   ✅ {device.name} activated")
                success_count += 1
            else:
                print(f"   ❌ {device.name} failed")
        
        print(f"\n📊 Alarm test results: {success_count}/{len(devices)} devices activated")
        
        if success_count > 0:
            print("✅ WebSocket alarm system functional!")
            
            # Wait and turn off
            print("\n⏳ Waiting 3 seconds then deactivating...")
            await asyncio.sleep(3)
            
            for device in devices:
                await service.control_device(device.deviceid, "OFF")
                print(f"   ⚫ {device.name} deactivated")
            
            return True
        else:
            print("❌ WebSocket alarm system not functional")
            return False
            
    finally:
        await service.disconnect()

if __name__ == "__main__":
    try:
        print("🧪 eWeLink WebSocket Control Test Suite")
        print("=" * 60)
        
        # Test basic device control
        device_test = asyncio.run(test_websocket_control())
        
        if device_test:
            # Test full alarm scenario
            alarm_test = asyncio.run(test_alarm_scenario())
            
            if alarm_test:
                print("\n🎊 ALL WEBSOCKET TESTS PASSED!")
                print("Your alarm system is ready with WebSocket control!")
            else:
                print("\n⚠️ Device control works but alarm scenario needs attention")
        else:
            print("\n❌ WebSocket device control test failed")
            print("Check authentication and WebSocket connection")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()