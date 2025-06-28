#!/usr/bin/env python3
"""
Test Sonoff device control with current authentication setup
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ewelink_service import EWeLinkService

async def test_sonoff_devices():
    """Test Sonoff device discovery and control"""
    
    print("🔌 Testing Sonoff Device Control")
    print("=" * 50)
    
    # Create eWeLink service
    service = EWeLinkService()
    
    print(f"🔐 App ID: {service.app_id[:10]}...")
    print(f"🔐 Email: {service.email}")
    print(f"🌐 Base URL: {service.base_url}")
    
    # Test authentication
    print("\n🔄 Authenticating with eWeLink...")
    auth_success = await service.authenticate(service.email, service.password)
    
    if not auth_success:
        print("❌ Authentication failed - cannot test devices")
        print("💡 Make sure EWELINK_ACCESS_TOKEN is set in environment")
        return False
    
    print("✅ Authentication successful!")
    
    # Get device list
    print("\n📱 Discovering Sonoff devices...")
    devices = await service.get_devices()
    
    if not devices:
        print("❌ No devices found")
        print("💡 Check if devices are paired to your eWeLink account")
        return False
    
    print(f"✅ Found {len(devices)} devices:")
    
    # Display all devices
    for i, device in enumerate(devices, 1):
        status = "🟢 Online" if device.online else "🔴 Offline"
        print(f"  {i}. {device.name} ({device.deviceid}) - {status}")
        
        # Show current state if available
        switch_state = device.params.get('switch', 'unknown')
        if switch_state != 'unknown':
            state_emoji = "🔵 ON" if switch_state == 'on' else "⚫ OFF"
            print(f"     Current state: {state_emoji}")
    
    # Test device control
    if devices:
        test_device = devices[0]
        print(f"\n🎛️ Testing control with: {test_device.name}")
        
        # Get current status
        print("📊 Getting current device status...")
        current_status = await service.get_device_status(test_device.deviceid)
        
        if current_status:
            print(f"   Device: {test_device.name}")
            print(f"   Online: {'🟢 Yes' if current_status.online else '🔴 No'}")
            print(f"   Switch: {'🔵 ON' if current_status.switch_state == 'on' else '⚫ OFF'}")
        
        # Test ON command
        print(f"\n🔴➡️🔵 Testing ON command...")
        on_success = await service.control_device(test_device.deviceid, "ON")
        
        if on_success:
            print("✅ ON command successful!")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Test OFF command  
            print(f"🔵➡️⚫ Testing OFF command...")
            off_success = await service.control_device(test_device.deviceid, "OFF")
            
            if off_success:
                print("✅ OFF command successful!")
                print("🎉 Device control test completed!")
                return True
            else:
                print("❌ OFF command failed")
                return False
        else:
            print("❌ ON command failed")
            return False
    
    return False

async def test_alarm_scenario():
    """Test the full alarm scenario"""
    
    print("\n🚨 Testing Full Alarm Scenario")
    print("=" * 40)
    
    service = EWeLinkService()
    
    # Authenticate
    auth_success = await service.authenticate(service.email, service.password)
    if not auth_success:
        print("❌ Cannot test alarm - authentication failed")
        return False
    
    # Get devices
    devices = await service.get_devices()
    if not devices:
        print("❌ Cannot test alarm - no devices found")
        return False
    
    # Find alarm device (first available device)
    alarm_device = devices[0]
    print(f"🚨 Using device for alarm test: {alarm_device.name}")
    
    # Simulate alarm activation
    print("🔥 ALARM ACTIVATED! Turning on all devices...")
    
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
        print("✅ Alarm system functional!")
        
        # Wait and turn off
        print("\n⏳ Waiting 5 seconds then deactivating...")
        await asyncio.sleep(5)
        
        for device in devices:
            await service.control_device(device.deviceid, "OFF")
            print(f"   ⚫ {device.name} deactivated")
        
        return True
    else:
        print("❌ Alarm system not functional")
        return False

if __name__ == "__main__":
    try:
        print("🧪 Sonoff Device Control Test Suite")
        print("=" * 60)
        
        # Test basic device control
        device_test = asyncio.run(test_sonoff_devices())
        
        if device_test:
            # Test full alarm scenario
            alarm_test = asyncio.run(test_alarm_scenario())
            
            if alarm_test:
                print("\n🎊 ALL TESTS PASSED! Your alarm system is ready!")
            else:
                print("\n⚠️ Device control works but alarm scenario needs attention")
        else:
            print("\n❌ Device control test failed - check authentication and devices")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()