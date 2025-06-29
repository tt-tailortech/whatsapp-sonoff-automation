#!/usr/bin/env python3
"""
Test device control: Turn ON/OFF 3 times, then keep ON
"""

import asyncio
import httpx
import json

# Your working authentication details
ACCESS_TOKEN = "73d1a52ee534403fcfe294d0b5a26504dbd5bd8a"
BASE_URL = "https://us-apia.coolkit.cc"
DEVICE_ID = "10011eafd1"

async def control_device(command: str):
    """Control your SONOFF device"""
    
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
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    return True
                    
    except Exception as e:
        print(f"❌ Control error: {e}")
        
    return False

async def blink_test():
    """Turn ON/OFF 3 times, then keep ON"""
    
    print("🧪 SONOFF Blink Test Pattern")
    print("=" * 50)
    print(f"📱 Device ID: {DEVICE_ID}")
    print("🎯 Pattern: ON-OFF-ON-OFF-ON-OFF, then keep ON")
    print()
    
    # Blink 3 times (ON-OFF cycle x3)
    for cycle in range(1, 4):
        print(f"🔄 Cycle {cycle}/3:")
        
        # Turn ON
        print("   🔴➡️🔵 Turning ON...")
        on_success = await control_device("ON")
        if on_success:
            print("   ✅ ON successful")
        else:
            print("   ❌ ON failed")
            return False
            
        # Wait 1 second
        await asyncio.sleep(1)
        
        # Turn OFF
        print("   🔵➡️⚫ Turning OFF...")
        off_success = await control_device("OFF")
        if off_success:
            print("   ✅ OFF successful")
        else:
            print("   ❌ OFF failed")
            return False
            
        # Wait 1 second before next cycle
        await asyncio.sleep(1)
        print()
    
    # Final: Keep ON
    print("🔥 Final step: Keeping device ON...")
    final_on = await control_device("ON")
    if final_on:
        print("✅ Device is now ON and will stay ON")
        print("🎉 BLINK TEST COMPLETED!")
        print("💡 Your SONOFF device should now be ON and stay ON")
        return True
    else:
        print("❌ Final ON command failed")
        return False

async def main():
    """Main test function"""
    try:
        print("🚨 Starting SONOFF Blink Pattern Test")
        print("📋 This will blink your device 3 times, then keep it ON")
        print("⏳ Starting in 3 seconds...")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"   {i}...")
            await asyncio.sleep(1)
        
        print("🚀 Starting test now!\n")
        
        # Run the blink test
        success = await blink_test()
        
        if success:
            print("\n🎊 SUCCESS! Blink pattern completed!")
            print("🔵 Your device should now be ON and staying ON")
        else:
            print("\n❌ Blink test failed")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())