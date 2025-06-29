#!/usr/bin/env python3
"""
Test device control with working token
"""

import asyncio
import httpx
import json

# Your working authentication details
ACCESS_TOKEN = "73d1a52ee534403fcfe294d0b5a26504dbd5bd8a"
BASE_URL = "https://us-apia.coolkit.cc"
DEVICE_ID = "10011eafd1"  # From your logs

async def control_device(command: str):
    """Control your SONOFF device"""
    
    print(f"🎛️ Sending {command} command to device {DEVICE_ID}")
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Convert command to switch state
    switch_state = "on" if command.upper() == "ON" else "off"
    
    control_payload = {
        "type": 1,
        "id": DEVICE_ID,
        "params": {"switch": switch_state}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v2/device/thing/status", 
                headers=headers, 
                json=control_payload
            )
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    print(f"✅ Device turned {command.upper()} successfully!")
                    return True
                else:
                    print(f"❌ Device control error: {data.get('msg', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Control error: {e}")
        return False

async def test_device_control():
    """Test turning device on and off"""
    
    print("🧪 Testing SONOFF Device Control")
    print("=" * 50)
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"🌐 Endpoint: {BASE_URL}")
    print(f"🔑 Token: {ACCESS_TOKEN[:20]}...")
    print()
    
    # Test ON command
    print("🔴➡️🔵 Testing ON command...")
    on_success = await control_device("ON")
    
    if on_success:
        print("✅ ON command successful!")
        
        # Wait 3 seconds
        print("⏳ Waiting 3 seconds...")
        await asyncio.sleep(3)
        
        # Test OFF command
        print("🔵➡️⚫ Testing OFF command...")
        off_success = await control_device("OFF")
        
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

async def test_alarm_simulation():
    """Simulate alarm activation"""
    
    print("\n🚨 Testing ALARM Simulation")
    print("=" * 40)
    
    print("🔥 ALARM ACTIVATED! Turning device ON...")
    alarm_success = await control_device("ON")
    
    if alarm_success:
        print("✅ Alarm activation successful!")
        
        # Keep on for 5 seconds (alarm duration)
        print("⏳ Alarm active for 5 seconds...")
        await asyncio.sleep(5)
        
        # Turn off
        print("🔵➡️⚫ Deactivating alarm...")
        deactivate_success = await control_device("OFF")
        
        if deactivate_success:
            print("✅ Alarm deactivated!")
            print("🎊 ALARM SYSTEM TEST SUCCESSFUL!")
            return True
        else:
            print("❌ Alarm deactivation failed")
            return False
    else:
        print("❌ Alarm activation failed")
        return False

if __name__ == "__main__":
    try:
        # Test basic control
        control_works = asyncio.run(test_device_control())
        
        if control_works:
            # Test alarm simulation
            alarm_works = asyncio.run(test_alarm_simulation())
            
            if alarm_works:
                print("\n🎊 ALL TESTS PASSED!")
                print("Your eWeLink device control is working perfectly!")
                print("The alarm system is ready for WhatsApp integration!")
            else:
                print("\n⚠️ Basic control works but alarm simulation needs attention")
        else:
            print("\n❌ Device control test failed")
            print("Check token and device ID")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()