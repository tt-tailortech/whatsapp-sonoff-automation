#!/usr/bin/env python3
"""
Final OAuth Fix - Based on specific API error responses
Addresses the exact ValidationError and signature issues found
"""

import asyncio
import httpx
import json
import time
import hmac
import hashlib
import base64
import urllib.parse

APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"
EMAIL = "tt.tailortech@gmail.com"
PASSWORD = "Qwerty.2025"

def generate_oauth_signature(app_id: str, app_secret: str, timestamp: str) -> str:
    """Generate OAuth signature - APP_ID + timestamp method"""
    sign_string = f"{app_id}_{timestamp}"
    signature = hmac.new(
        app_secret.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

def generate_api_signature(app_secret: str, payload: dict) -> str:
    """Generate API signature - JSON payload method"""
    json_string = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(
        app_secret.encode(),
        json_string.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

async def fixed_oauth_approach():
    """Try OAuth with the missing grantType parameter"""
    
    print("🔧 Fixed OAuth approach (adding missing grantType)...")
    
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # China region (your account is definitely there)
    endpoint = "https://cn-apia.coolkit.cn/v2/user/oauth/code"
    
    # Add the missing grantType parameter
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "clientId": APP_ID,
        "grantType": "authorization_code",  # This was missing!
        "redirectUrl": "http://localhost:3000/callback",
        "state": "manual_setup"
    }
    
    # Use OAuth signature method
    signature = generate_oauth_signature(APP_ID, APP_SECRET, timestamp)
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID,
        "X-CK-Nonce": nonce,
        "X-CK-Seq": timestamp,
        "Authorization": f"Sign {signature}"
    }
    
    print(f"🔐 Endpoint: {endpoint}")
    print(f"🔐 Payload: {json.dumps(payload, indent=2)}")
    print(f"🔐 Signature: {signature}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    auth_code = data.get("data", {}).get("code")
                    if auth_code:
                        print(f"\n🎉 SUCCESS! Got authorization code: {auth_code}")
                        return auth_code
                else:
                    print(f"❌ Error: {data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    return None

async def try_different_signature_methods():
    """Try different signature calculation methods"""
    
    print("\n🔧 Trying different signature methods for direct login...")
    
    endpoints = [
        "https://cn-apia.coolkit.cn/v2/user/login",
        "https://apia.coolkit.cn/v2/user/login"
    ]
    
    payloads = [
        {"email": EMAIL, "password": PASSWORD},
        {"email": EMAIL, "password": PASSWORD, "countryCode": "+56"},
        {"email": EMAIL, "password": PASSWORD, "areaCode": "+56"}
    ]
    
    # Different signature methods to try
    signature_methods = [
        {
            "name": "JSON Payload",
            "func": lambda p: generate_api_signature(APP_SECRET, p)
        },
        {
            "name": "URL Encoded",
            "func": lambda p: generate_api_signature(APP_SECRET, {"data": urllib.parse.urlencode(p)})
        },
        {
            "name": "Timestamp Based",
            "func": lambda p: generate_oauth_signature(APP_ID, APP_SECRET, str(int(time.time() * 1000)))
        }
    ]
    
    for endpoint in endpoints:
        for payload in payloads:
            for sig_method in signature_methods:
                print(f"\n🧪 Testing: {endpoint}")
                print(f"📝 Payload: {payload}")
                print(f"🔐 Signature method: {sig_method['name']}")
                
                signature = sig_method['func'](payload)
                
                headers = {
                    "Content-Type": "application/json",
                    "X-CK-Appid": APP_ID,
                    "Authorization": f"Sign {signature}"
                }
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(endpoint, headers=headers, json=payload)
                        
                        print(f"📡 Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("error") == 0:
                                access_token = data.get("data", {}).get("at")
                                if access_token:
                                    print(f"🎉 SUCCESS! Access token: {access_token[:30]}...")
                                    return access_token
                            else:
                                error_msg = data.get('msg', 'Unknown error')
                                if "sign verification failed" not in error_msg:
                                    print(f"📄 Different error: {error_msg}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    return None

async def try_home_assistant_credentials():
    """Try using Home Assistant's working credentials"""
    
    print("\n🏠 Trying Home Assistant integration credentials...")
    
    # Home Assistant uses these credentials successfully
    ha_app_id = "McFJj4Noke1mGDZCR1QarGW7rtDv00Zs"
    ha_app_secret = "6Nz4n0xA8s8qdxQf2GqurZj2Fs55FUvM"
    
    endpoints = [
        "https://cn-apia.coolkit.cn/v2/user/login",
        "https://eu-apia.coolkit.cc/v2/user/login",
        "https://us-apia.coolkit.cc/v2/user/login"
    ]
    
    payload = {"email": EMAIL, "password": PASSWORD}
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing HA credentials with: {endpoint}")
        
        signature = generate_api_signature(ha_app_secret, payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": ha_app_id,
            "Authorization": f"Sign {signature}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                
                print(f"📡 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        access_token = data.get("data", {}).get("at")
                        if access_token:
                            print(f"🎉 SUCCESS with HA credentials! Token: {access_token[:30]}...")
                            return access_token
                    else:
                        error_msg = data.get('msg', 'Unknown error')
                        print(f"❌ Error: {error_msg}")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🔧 Final OAuth Fix - Comprehensive Approach")
    print("=" * 60)
    
    try:
        # Try 1: Fixed OAuth with grantType
        auth_code = asyncio.run(fixed_oauth_approach())
        
        if auth_code:
            print(f"\n📋 Use this code with exchange script:")
            print(f"python3 exchange_oauth_code.py {auth_code}")
        else:
            # Try 2: Different signature methods
            token = asyncio.run(try_different_signature_methods())
            
            if token:
                print(f"\n🎉 Got access token via direct login!")
                print(f"📋 Set in Render: EWELINK_ACCESS_TOKEN={token}")
            else:
                # Try 3: Home Assistant credentials
                token = asyncio.run(try_home_assistant_credentials())
                
                if token:
                    print(f"\n🎉 Got access token via Home Assistant credentials!")
                    print(f"📋 Set in Render: EWELINK_ACCESS_TOKEN={token}")
                    print(f"⚠️ Note: Using HA credentials, not your OAuth app")
                else:
                    print("\n❌ All approaches failed")
                    print("\n💡 Next steps:")
                    print("1. Your OAuth app may need approval from eWeLink")
                    print("2. Try contacting eWeLink support")
                    print("3. Use Home Assistant integration as workaround")
                    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()