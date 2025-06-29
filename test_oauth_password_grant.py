#!/usr/bin/env python3
"""
Test OAuth password grant type from documentation
"""

import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def test_oauth_password_grant():
    """Test OAuth password grant according to documentation"""
    
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    email = os.getenv('EWELINK_EMAIL')
    password = os.getenv('EWELINK_PASSWORD')
    
    print("🔐 Testing OAuth Password Grant Type")
    print("=" * 50)
    
    # Regional endpoints from documentation
    endpoints = [
        "https://eu-apia.coolkit.cc",
        "https://us-apia.coolkit.cc", 
        "https://as-apia.coolkit.cc",
        "https://cn-apia.coolkit.cn"
    ]
    
    for base_url in endpoints:
        print(f"\n🌐 Testing region: {base_url}")
        
        url = f"{base_url}/v2/user/oauth/token"
        
        # Password grant type from documentation
        payload = {
            "grant_type": "password",
            "client_id": app_id,
            "client_secret": app_secret,
            "username": email,
            "password": password
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": app_id,
        }
        
        print(f"🔗 URL: {url}")
        print(f"📋 Payload: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"📊 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        print("✅ SUCCESS! Password grant works!")
                        access_token = data["data"]["accessToken"]
                        print(f"🎫 Access Token: {access_token}")
                        
                        # Test getting devices with this token
                        print(f"\n🔄 Testing device list with token...")
                        device_url = f"{base_url}/v2/device/thing"
                        device_headers = {
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-CK-Appid": app_id,
                        }
                        
                        device_response = await client.get(device_url, headers=device_headers)
                        print(f"📊 Device list status: {device_response.status_code}")
                        print(f"📄 Device response: {device_response.text}")
                        
                        return True
                    else:
                        print(f"❌ Error: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"❌ Failed: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_oauth_password_grant())