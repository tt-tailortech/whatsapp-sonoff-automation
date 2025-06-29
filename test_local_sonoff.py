#!/usr/bin/env python3
"""
Local Sonoff connection test - bypasses token exchange
Uses authorization code directly for device discovery and control
"""

import asyncio
import httpx
import json
import time
import hmac
import hashlib
import base64

APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"
EMAIL = "tt.tailortech@gmail.com"
PASSWORD = "Qwerty.2025"

# Fresh authorization code
AUTH_CODE = "2ad7d987-3185-492b-a93f-56737bf27a0c"

async def test_direct_device_api():
    """
    Test device API directly using different authentication methods
    """
    
    print("🔌 Testing Direct Sonoff Device API")
    print("=" * 50)
    
    # Try different endpoints and methods
    endpoints = [
        "https://us-apia.coolkit.cc",
        "https://cn-apia.coolkit.cn", 
        "https://eu-apia.coolkit.cc",
        "https://as-apia.coolkit.cc"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        
        # Method 1: Try with authorization code directly
        await test_with_auth_code(endpoint)
        
        # Method 2: Try with OAuth signature  
        await test_with_oauth_signature(endpoint)
        
        # Method 3: Try device discovery without auth
        await test_device_discovery(endpoint)

async def test_with_auth_code(endpoint: str):
    """Test using authorization code directly"""
    
    print("🔐 Method 1: Using authorization code directly")
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID,
        "Authorization": f"Code {AUTH_CODE}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to get device list
            response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"✅ Found {len(devices)} devices with auth code!")
                    
                    for device in devices:
                        print(f"  - {device.get('name', 'Unknown')} (ID: {device.get('deviceid', 'Unknown')})")
                    
                    return devices
                    
    except Exception as e:
        print(f"❌ Auth code method error: {e}")
    
    return []

async def test_with_oauth_signature(endpoint: str):
    """Test using OAuth signature method that works for getting codes"""
    
    print("🔐 Method 2: Using OAuth signature")
    
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # Use same signature method that works for getting auth codes
    sign_string = f"{APP_ID}_{timestamp}"
    signature = base64.b64encode(
        hmac.new(APP_SECRET.encode(), sign_string.encode(), hashlib.sha256).digest()
    ).decode()
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID,
        "X-CK-Nonce": nonce,
        "X-CK-Seq": timestamp,
        "Authorization": f"Sign {signature}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to get device list
            response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"✅ Found {len(devices)} devices with OAuth signature!")
                    
                    for device in devices:
                        print(f"  - {device.get('name', 'Unknown')} (ID: {device.get('deviceid', 'Unknown')})")
                    
                    # Test device control
                    if devices:
                        await test_device_control(endpoint, headers, devices[0])
                    
                    return devices
                    
    except Exception as e:
        print(f"❌ OAuth signature method error: {e}")
    
    return []

async def test_device_discovery(endpoint: str):
    """Test device discovery with minimal auth"""
    
    print("🔐 Method 3: Minimal authentication test")
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to get device list without auth
            response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code != 401:  # Any response other than unauthorized
                print("📋 Endpoint responds to minimal auth")
                    
    except Exception as e:
        print(f"❌ Minimal auth error: {e}")

async def test_device_control(endpoint: str, headers: dict, device: dict):
    """Test controlling a specific device"""
    
    device_id = device.get('deviceid')
    device_name = device.get('name', 'Unknown')
    
    print(f"\n🎛️ Testing device control: {device_name}")
    
    # Test ON command
    control_payload = {
        "type": "1",
        "id": device_id,
        "params": {"switch": "on"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{endpoint}/v2/device/thing/status", 
                headers=headers, 
                json=control_payload
            )
            
            print(f"📡 Control Status: {response.status_code}")
            print(f"📄 Control Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    print(f"✅ Successfully controlled {device_name}!")
                    
                    # Wait and test OFF
                    await asyncio.sleep(2)
                    
                    control_payload["params"]["switch"] = "off"
                    response = await client.post(
                        f"{endpoint}/v2/device/thing/status", 
                        headers=headers, 
                        json=control_payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            print(f"✅ Successfully turned OFF {device_name}!")
                            return True
                            
    except Exception as e:
        print(f"❌ Device control error: {e}")
    
    return False

async def test_alarm_scenario():
    """Test full alarm scenario if we find working method"""
    
    print("\n🚨 Testing Full Alarm Scenario")
    print("=" * 40)
    
    # Find working endpoint and get devices
    for endpoint in ["https://us-apia.coolkit.cc", "https://cn-apia.coolkit.cn"]:
        devices = await test_with_oauth_signature(endpoint)
        
        if devices:
            print(f"🎯 Found {len(devices)} devices on {endpoint}")
            
            # Test alarm - activate all devices
            print("🔥 ACTIVATING ALARM - All devices ON!")
            
            timestamp = str(int(time.time() * 1000))
            nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
            sign_string = f"{APP_ID}_{timestamp}"
            signature = base64.b64encode(
                hmac.new(APP_SECRET.encode(), sign_string.encode(), hashlib.sha256).digest()
            ).decode()
            
            headers = {
                "Content-Type": "application/json",
                "X-CK-Appid": APP_ID,
                "X-CK-Nonce": nonce,
                "X-CK-Seq": timestamp,
                "Authorization": f"Sign {signature}"
            }
            
            success_count = 0
            for device in devices:
                device_id = device.get('deviceid')
                device_name = device.get('name', 'Unknown')
                
                control_payload = {
                    "type": "1",
                    "id": device_id,
                    "params": {"switch": "on"}
                }
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{endpoint}/v2/device/thing/status", 
                            headers=headers, 
                            json=control_payload
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("error") == 0:
                                print(f"🔴➡️🔵 {device_name} ACTIVATED!")
                                success_count += 1
                            else:
                                print(f"❌ {device_name} failed: {data.get('msg', 'Unknown error')}")
                        else:
                            print(f"❌ {device_name} HTTP error: {response.status_code}")
                            
                except Exception as e:
                    print(f"❌ {device_name} error: {e}")
            
            print(f"\n🚨 ALARM SUMMARY: {success_count}/{len(devices)} devices activated")
            
            if success_count > 0:
                print("✅ ALARM SYSTEM WORKING!")
                
                # Deactivate after 5 seconds
                print("⏳ Deactivating in 5 seconds...")
                await asyncio.sleep(5)
                
                for device in devices:
                    device_id = device.get('deviceid')
                    control_payload = {
                        "type": "1",
                        "id": device_id,
                        "params": {"switch": "off"}
                    }
                    
                    try:
                        async with httpx.AsyncClient() as client:
                            await client.post(f"{endpoint}/v2/device/thing/status", headers=headers, json=control_payload)
                            print(f"⚫ {device.get('name', 'Unknown')} deactivated")
                    except:
                        pass
                
                return True
            else:
                print("❌ No devices could be controlled")
                return False
    
    print("❌ No working endpoint found")
    return False

if __name__ == "__main__":
    print("🧪 Local Sonoff Connection Test")
    print("=" * 60)
    print(f"🔐 App ID: {APP_ID}")
    print(f"📧 Email: {EMAIL}")
    print(f"🎟️ Auth Code: {AUTH_CODE}")
    
    try:
        # Test device APIs
        asyncio.run(test_direct_device_api())
        
        # Test full alarm scenario
        alarm_works = asyncio.run(test_alarm_scenario())
        
        if alarm_works:
            print("\n🎊 SUCCESS! Your Sonoff alarm system is fully functional!")
        else:
            print("\n⚠️ Need to debug authentication - devices not responding")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()