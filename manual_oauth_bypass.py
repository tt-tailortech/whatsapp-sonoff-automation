#!/usr/bin/env python3
"""
Manual OAuth bypass - directly simulate what the OAuth page does
Bypasses the CORS-broken OAuth interface
"""

import asyncio
import httpx
import json
import time
import hmac
import hashlib
import base64
import sys

APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"
EMAIL = "tt.tailortech@gmail.com"
PASSWORD = "Qwerty.2025"

async def direct_oauth_simulation():
    """
    Directly simulate what the OAuth page tries to do
    Bypass the CORS-broken browser interface
    """
    
    print("🔄 Direct OAuth simulation (bypassing CORS-broken interface)...")
    
    # Based on console logs, this is what the OAuth page tries to do
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # Try the exact endpoint that's failing with CORS
    oauth_endpoints = [
        "https://apia.coolkit.cn/v2/user/oauth/code",  # China (from error)
        "https://cn-apia.coolkit.cn/v2/user/oauth/code",  # Alternative China
        "https://as-apia.coolkit.cc/v2/user/oauth/code",  # Asia
        "https://us-apia.coolkit.cc/v2/user/oauth/code",  # US
    ]
    
    for endpoint in oauth_endpoints:
        print(f"\n🌐 Trying direct endpoint: {endpoint}")
        
        # Simulate what the OAuth page sends
        payload = {
            "email": EMAIL,
            "password": PASSWORD,
            "clientId": APP_ID,
            "redirectUrl": "http://localhost:3000/callback",
            "state": "manual_setup"
        }
        
        # Generate signature like OAuth page does
        sign_string = f"{APP_ID}_{timestamp}"
        signature = base64.b64encode(
            hmac.new(APP_SECRET.encode(), sign_string.encode(), hashlib.sha256).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
            "X-CK-Nonce": nonce,
            "X-CK-Seq": timestamp,
            "Authorization": f"Sign {signature}",
            "Origin": "https://c2ccdn.coolkit.cc",  # Simulate OAuth page origin
            "Referer": "https://c2ccdn.coolkit.cc/"
        }
        
        print(f"🔐 Headers: {json.dumps(headers, indent=2)}")
        print(f"🔐 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                
                print(f"📡 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        # Success! Extract authorization code or token
                        result_data = data.get("data", {})
                        auth_code = result_data.get("code")
                        access_token = result_data.get("accessToken")
                        
                        if auth_code:
                            print(f"\n✅ Got authorization code: {auth_code}")
                            return auth_code, "code"
                        elif access_token:
                            print(f"\n✅ Got direct access token: {access_token}")
                            return access_token, "token"
                        else:
                            print(f"✅ Response successful but no code/token found")
                    else:
                        print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    print("\n❌ All direct endpoints failed")
    return None, None

async def alternative_login_approaches():
    """Try alternative login methods that might work"""
    
    print("\n🔄 Trying alternative authentication approaches...")
    
    # Alternative approach 1: Direct login with different signature
    approaches = [
        {
            "name": "V2 Direct Login",
            "url": "https://cn-apia.coolkit.cn/v2/user/login",
            "payload": {"email": EMAIL, "password": PASSWORD}
        },
        {
            "name": "V2 Login with Country",
            "url": "https://cn-apia.coolkit.cn/v2/user/login", 
            "payload": {"email": EMAIL, "password": PASSWORD, "countryCode": "+56"}
        },
        {
            "name": "Legacy V1 Login",
            "url": "https://cn-api.coolkit.cn/api/user/login",
            "payload": {
                "email": EMAIL,
                "password": PASSWORD,
                "version": 6,
                "ts": str(int(time.time())),
                "nonce": str(int(time.time() * 1000)),
                "appid": APP_ID
            }
        }
    ]
    
    for approach in approaches:
        print(f"\n🧪 Trying: {approach['name']}")
        print(f"🌐 URL: {approach['url']}")
        
        # Generate signature for payload
        json_payload = json.dumps(approach['payload'], separators=(',', ':'))
        signature = base64.b64encode(
            hmac.new(APP_SECRET.encode(), json_payload.encode(), hashlib.sha256).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
            "Authorization": f"Sign {signature}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(approach['url'], headers=headers, json=approach['payload'])
                
                print(f"📡 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        access_token = data.get("data", {}).get("at") or data.get("at")
                        if access_token:
                            print(f"\n🎉 SUCCESS with {approach['name']}!")
                            print(f"🔑 Access Token: {access_token[:30]}...")
                            return access_token
                    else:
                        print(f"❌ Error: {data.get('msg', 'Unknown error')}")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🔧 Manual OAuth Bypass Tool")
    print("=" * 50)
    print("Attempting to bypass CORS-broken OAuth interface...")
    
    try:
        # Try direct OAuth simulation first
        result, result_type = asyncio.run(direct_oauth_simulation())
        
        if result:
            if result_type == "code":
                print(f"\n📋 Use this authorization code:")
                print(f"python3 exchange_oauth_code.py {result}")
            else:
                print(f"\n📋 Direct access token obtained!")
                print(f"Set this in Render: EWELINK_ACCESS_TOKEN={result}")
        else:
            # Try alternative approaches
            token = asyncio.run(alternative_login_approaches())
            
            if token:
                print(f"\n🎉 SUCCESS via alternative method!")
                print(f"📋 Set this in Render: EWELINK_ACCESS_TOKEN={token}")
            else:
                print("\n❌ All methods failed")
                print("\n💡 Possible solutions:")
                print("1. Contact eWeLink support about CORS issue")
                print("2. Use eWeLink mobile app API endpoints")
                print("3. Create new 'Direct Login' type app")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()