#!/usr/bin/env python3
"""
Fixed token exchange using the signature method that worked for getting the code
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

def generate_oauth_signature(app_id: str, app_secret: str, timestamp: str) -> str:
    """Generate OAuth signature - the method that worked for getting the code"""
    sign_string = f"{app_id}_{timestamp}"
    signature = hmac.new(
        app_secret.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

async def exchange_code_fixed(auth_code: str):
    """Exchange code using the signature method that actually works"""
    
    print("🔄 Fixed token exchange (using working signature method)...")
    print(f"📝 Code: {auth_code}")
    
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # Use the same signature method that worked for getting the code
    signature = generate_oauth_signature(APP_ID, APP_SECRET, timestamp)
    
    # The response said region "us", so let's try US endpoint first
    endpoints = [
        "https://us-apia.coolkit.cc/v2/user/oauth/token",
        "https://cn-apia.coolkit.cn/v2/user/oauth/token", 
        "https://as-apia.coolkit.cc/v2/user/oauth/token",
        "https://eu-apia.coolkit.cc/v2/user/oauth/token"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Trying: {endpoint}")
        
        payload = {
            "clientId": APP_ID,
            "clientSecret": APP_SECRET,
            "grantType": "authorization_code",
            "code": auth_code,
            "redirectUrl": "http://localhost:3000/callback"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
            "X-CK-Nonce": nonce,
            "X-CK-Seq": timestamp,
            "Authorization": f"Sign {signature}"
        }
        
        print(f"🔐 Using OAuth signature method (not JSON payload)")
        print(f"🔐 Signature: {signature}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                
                print(f"📡 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        token_data = data.get("data", {})
                        access_token = token_data.get("accessToken")
                        refresh_token = token_data.get("refreshToken")
                        user_info = token_data.get("user", {})
                        
                        print("\n🎉 SUCCESS! Token exchange completed!")
                        print(f"🔑 Access Token: {access_token[:30]}...")
                        print(f"🔄 Refresh Token: {refresh_token[:30] if refresh_token else 'None'}...")
                        print(f"👤 User ID: {user_info.get('userId', 'Unknown')}")
                        print(f"📧 Email: {user_info.get('email', 'Unknown')}")
                        
                        # Save tokens
                        token_file = {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user_info": user_info,
                            "endpoint": endpoint
                        }
                        
                        with open("ewelink_tokens.json", "w") as f:
                            json.dump(token_file, f, indent=2)
                        
                        print("\n💾 Tokens saved to ewelink_tokens.json")
                        print("\n📋 For Render deployment:")
                        print(f"EWELINK_ACCESS_TOKEN={access_token}")
                        
                        return access_token, endpoint
                    else:
                        print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    return None, None

async def test_token(access_token: str, endpoint: str):
    """Test the access token"""
    
    print(f"\n🧪 Testing access token...")
    
    # Use the same signature method for API calls
    timestamp = str(int(time.time() * 1000))
    signature = generate_oauth_signature(APP_ID, APP_SECRET, timestamp)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID,
        "X-CK-Seq": timestamp,
        "Authorization": f"Sign {signature}"  # Some APIs need signature even with token
    }
    
    test_url = f"{endpoint.replace('/v2/user/oauth/token', '/v2/device/thing')}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(test_url, headers=headers)
            
            print(f"📡 Test Status: {response.status_code}")
            print(f"📄 Test Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"\n✅ Token works! Found {len(devices)} devices")
                    return True
                    
    except Exception as e:
        print(f"❌ Test Error: {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 exchange_code_fixed.py <auth_code>")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    
    try:
        access_token, endpoint = asyncio.run(exchange_code_fixed(auth_code))
        
        if access_token:
            success = asyncio.run(test_token(access_token, endpoint))
            
            if success:
                print("\n🎊 COMPLETE! eWeLink authentication working!")
            else:
                print("\n⚠️ Token received but may need Bearer auth instead")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")