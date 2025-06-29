#!/usr/bin/env python3
"""
Direct eWeLink API test with app credentials
"""

import asyncio
import httpx
import json
import time
import hmac
import hashlib
import base64

# Your OAuth app credentials
APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"

# Your account credentials  
EMAIL = "tt.tailortech@gmail.com"
PASSWORD = "Qwerty.2025"

async def try_direct_login():
    """Try direct login to eWeLink API"""
    
    print("🔐 Testing Direct eWeLink API Access")
    print("=" * 50)
    
    endpoints = [
        "https://us-apia.coolkit.cc",
        "https://cn-apia.coolkit.cn", 
        "https://eu-apia.coolkit.cc",
        "https://as-apia.coolkit.cc"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        
        # Try different authentication methods
        success = await try_app_login(endpoint)
        if success:
            return True
            
        success = await try_user_login(endpoint)
        if success:
            return True
    
    return False

async def try_app_login(endpoint: str):
    """Try login using app credentials"""
    
    print("🔑 Method 1: App credential login")
    
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # App-based authentication
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "appid": APP_ID
    }
    
    # Sign the payload
    json_str = json.dumps(payload, separators=(',', ':'))
    signature = base64.b64encode(
        hmac.new(APP_SECRET.encode(), json_str.encode(), hashlib.sha256).digest()
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
            # Try app login endpoint
            response = await client.post(f"{endpoint}/v2/user/login", headers=headers, json=payload)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    user_data = data.get("data", {})
                    access_token = user_data.get("at")  # access token
                    
                    if access_token:
                        print(f"✅ SUCCESS! Got access token: {access_token}")
                        
                        # Test with devices
                        await test_devices(endpoint, access_token)
                        return access_token
                        
    except Exception as e:
        print(f"❌ App login error: {e}")
    
    return None

async def try_user_login(endpoint: str):
    """Try standard user login"""
    
    print("🔑 Method 2: Standard user login")
    
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # Standard user login
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    # Sign the payload
    json_str = json.dumps(payload, separators=(',', ':'))
    signature = base64.b64encode(
        hmac.new(APP_SECRET.encode(), json_str.encode(), hashlib.sha256).digest()
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
            response = await client.post(f"{endpoint}/v2/user/login", headers=headers, json=payload)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    user_data = data.get("data", {})
                    access_token = user_data.get("at")
                    
                    if access_token:
                        print(f"✅ SUCCESS! Got access token: {access_token}")
                        
                        # Test with devices
                        await test_devices(endpoint, access_token)
                        return access_token
                        
    except Exception as e:
        print(f"❌ User login error: {e}")
    
    return None

async def test_devices(endpoint: str, access_token: str):
    """Test device access with token"""
    
    print(f"\n🧪 Testing device access...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
            
            print(f"📡 Device Status: {response.status_code}")
            print(f"📄 Device Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"🎉 Found {len(devices)} devices!")
                    
                    for device in devices:
                        print(f"  - {device.get('name', 'Unknown')} (ID: {device.get('deviceid')})")
                    
                    # Test device control
                    if devices:
                        await test_device_control(endpoint, access_token, devices[0])
                    
                    print(f"\n💾 SAVE THIS TOKEN:")
                    print(f"EWELINK_ACCESS_TOKEN={access_token}")
                    
                    return True
                    
    except Exception as e:
        print(f"❌ Device test error: {e}")
    
    return False

async def test_device_control(endpoint: str, access_token: str, device: dict):
    """Test controlling a device"""
    
    device_id = device.get('deviceid')
    device_name = device.get('name', 'Unknown')
    
    print(f"\n🎛️ Testing control: {device_name}")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test ON command
    control_payload = {
        "type": "1",
        "id": device_id,
        "params": {"switch": "on"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{endpoint}/v2/device/thing/status", headers=headers, json=control_payload)
            
            print(f"📡 Control Status: {response.status_code}")
            print(f"📄 Control Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    print(f"✅ Device control works! {device_name} turned ON")
                    
                    # Turn back off
                    await asyncio.sleep(2)
                    control_payload["params"]["switch"] = "off"
                    response = await client.post(f"{endpoint}/v2/device/thing/status", headers=headers, json=control_payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            print(f"✅ {device_name} turned OFF - control test complete!")
                            
    except Exception as e:
        print(f"❌ Control error: {e}")

if __name__ == "__main__":
    try:
        success = asyncio.run(try_direct_login())
        
        if success:
            print("\n🎊 SUCCESS! eWeLink authentication working")
            print("Add the access token to your Render environment variables")
        else:
            print("\n❌ All authentication methods failed")
            print("eWeLink may have restricted OAuth 2.0 API access")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()