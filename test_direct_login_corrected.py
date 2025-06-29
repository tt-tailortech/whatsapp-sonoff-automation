#!/usr/bin/env python3
"""
Test direct login with corrected signature from documentation
"""

import asyncio
import os
import hmac
import hashlib
import base64
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_corrected_direct_login():
    """Test direct login with JSON payload signing"""
    
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    email = os.getenv('EWELINK_EMAIL')
    password = os.getenv('EWELINK_PASSWORD')
    
    print("🔐 Testing Direct Login with Corrected Signature")
    print("=" * 50)
    
    # Test all regions
    endpoints = [
        "https://us-apia.coolkit.cc",  # Try US first since OAuth went there
        "https://eu-apia.coolkit.cc",
        "https://as-apia.coolkit.cc",
    ]
    
    for base_url in endpoints:
        print(f"\n🌐 Testing region: {base_url}")
        
        url = f"{base_url}/v2/user/login"
        
        # Payload as per documentation
        payload = {
            "email": email,
            "password": password,
            "countryCode": "+56"
        }
        
        # Sign JSON payload according to documentation
        json_payload = json.dumps(payload, separators=(',', ':'))
        signature = base64.b64encode(
            hmac.new(app_secret.encode(), json_payload.encode(), hashlib.sha256).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": app_id,
            "Authorization": f"Sign {signature}"
        }
        
        print(f"🔗 URL: {url}")
        print(f"📋 JSON Payload: {json_payload}")
        print(f"🔐 Signature: {signature}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"📊 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        access_token = data["data"]["at"]
                        user_id = data["data"]["user"]["id"]
                        
                        print("✅ SUCCESS! Direct login works!")
                        print(f"🎫 Access Token: {access_token}")
                        print(f"👤 User ID: {user_id}")
                        
                        # Test getting devices
                        print(f"\n🔄 Testing device list...")
                        device_url = f"{base_url}/v2/device/thing"
                        device_headers = {
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-CK-Appid": app_id,
                        }
                        
                        device_response = await client.get(device_url, headers=device_headers)
                        print(f"📊 Device list status: {device_response.status_code}")
                        print(f"📄 Device response: {device_response.text}")
                        
                        if device_response.status_code == 200:
                            device_data = device_response.json()
                            if device_data.get("error") == 0:
                                devices = device_data.get("data", {}).get("thingList", [])
                                print(f"🎯 Found {len(devices)} devices/groups")
                                
                                for item in devices:
                                    if item.get("itemType") == 1:  # Device
                                        device_info = item.get("itemData", {})
                                        print(f"  📱 Device: {device_info.get('name')} (ID: {device_info.get('deviceid')})")
                        
                        # Update .env with working credentials
                        print(f"\n📝 Add these to .env:")
                        print(f"EWELINK_ACCESS_TOKEN={access_token}")
                        print(f"EWELINK_USER_ID={user_id}")
                        print(f"EWELINK_BASE_URL={base_url}")
                        
                        return True
                    else:
                        print(f"❌ Error: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"❌ Failed: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_corrected_direct_login())