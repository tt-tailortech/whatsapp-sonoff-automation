#!/usr/bin/env python3
"""
Test eWeLink REST API with pro account
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

# From your logs
DEVICE_ID = "10011eafd1"
API_KEY = "04739209-3c18-4995-8c2d-df9d002da821"

async def test_pro_login():
    """Test login with pro account"""
    
    print("🔐 Testing eWeLink Pro Account Login")
    print("=" * 50)
    
    endpoints = [
        "https://cn-apia.coolkit.cn",
        "https://us-apia.coolkit.cc", 
        "https://eu-apia.coolkit.cc"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        
        timestamp = str(int(time.time() * 1000))
        nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
        
        # Login payload
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
                            
                            # Test device API with token
                            await test_device_api(endpoint, access_token)
                            
                            # Test device control
                            await test_device_control(endpoint, access_token)
                            
                            return access_token
                    else:
                        print(f"❌ Login error: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    return None

async def test_device_api(endpoint: str, access_token: str):
    """Test device API with access token"""
    
    print(f"\n📱 Testing device API...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
            
            print(f"📡 Device API Status: {response.status_code}")
            print(f"📄 Device API Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"✅ Found {len(devices)} devices!")
                    
                    for device in devices:
                        device_id = device.get('deviceid', 'Unknown')
                        device_name = device.get('name', 'Unknown')
                        online = device.get('online', False)
                        status = "🟢 Online" if online else "🔴 Offline"
                        
                        print(f"  - {device_name} (ID: {device_id}) - {status}")
                        
                        # Show device params
                        params = device.get('params', {})
                        switch_state = params.get('switch', 'unknown')
                        if switch_state != 'unknown':
                            state_emoji = "🔵 ON" if switch_state == 'on' else "⚫ OFF"
                            print(f"    Current state: {state_emoji}")
                    
                    return devices
                else:
                    print(f"❌ Device API error: {data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ Device API HTTP error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Device API error: {e}")
    
    return []

async def test_device_control(endpoint: str, access_token: str):
    """Test device control with access token"""
    
    print(f"\n🎛️ Testing device control...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test ON command
    control_payload = {
        "type": "1",
        "id": DEVICE_ID,
        "params": {"switch": "on"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("🔴➡️🔵 Testing ON command...")
            response = await client.post(f"{endpoint}/v2/device/thing/status", headers=headers, json=control_payload)
            
            print(f"📡 Control Status: {response.status_code}")
            print(f"📄 Control Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    print(f"✅ Device turned ON successfully!")
                    
                    # Wait and test OFF
                    await asyncio.sleep(2)
                    
                    control_payload["params"]["switch"] = "off"
                    print("🔵➡️⚫ Testing OFF command...")
                    response = await client.post(f"{endpoint}/v2/device/thing/status", headers=headers, json=control_payload)
                    
                    print(f"📡 OFF Status: {response.status_code}")
                    print(f"📄 OFF Response: {response.text}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            print(f"✅ Device turned OFF successfully!")
                            print("🎉 REST API device control working!")
                            return True
                        else:
                            print(f"❌ OFF command error: {data.get('msg', 'Unknown error')}")
                    else:
                        print(f"❌ OFF HTTP error: {response.status_code}")
                else:
                    print(f"❌ ON command error: {data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ Control HTTP error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Control error: {e}")
    
    return False

if __name__ == "__main__":
    try:
        print("🧪 eWeLink Pro Account API Test")
        print("=" * 60)
        print(f"📧 Email: {EMAIL}")
        print(f"🔐 App ID: {APP_ID}")
        print(f"📱 Test Device: {DEVICE_ID}")
        
        token = asyncio.run(test_pro_login())
        
        if token:
            print(f"\n🎊 SUCCESS! eWeLink Pro API is working!")
            print(f"💾 Access Token: {token}")
            print(f"\n📝 Add this to your Render environment:")
            print(f"EWELINK_ACCESS_TOKEN={token}")
        else:
            print(f"\n❌ Pro account login failed")
            print("Check if pro subscription is fully activated")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()