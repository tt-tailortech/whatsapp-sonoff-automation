#!/usr/bin/env python3
"""
Exchange OAuth authorization code for access token
Based on research findings from eWeLink forum
"""

import asyncio
import httpx
import json
import hmac
import hashlib
import base64
import sys

# Your OAuth app credentials
APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"

async def exchange_code_for_token(auth_code: str):
    """
    Exchange authorization code for access token
    Uses research findings about proper signature method
    """
    
    print("🔄 Exchanging authorization code for access token...")
    print(f"📝 Code: {auth_code[:20]}...")
    
    # Try different regional endpoints based on research
    endpoints = [
        "https://cn-apia.coolkit.cn/v2/user/oauth/token",  # China (detected from CORS error)
        "https://as-apia.coolkit.cc/v2/user/oauth/token",  # Asia  
        "https://us-apia.coolkit.cc/v2/user/oauth/token",  # US
        "https://eu-apia.coolkit.cc/v2/user/oauth/token"   # EU
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Trying endpoint: {endpoint}")
        
        # Payload for token exchange
        payload = {
            "clientId": APP_ID,
            "clientSecret": APP_SECRET,
            "grantType": "authorization_code",
            "code": auth_code,
            "redirectUrl": "http://localhost:3000/callback"
        }
        
        # Based on forum research: "encrypt the entire json body message as the sign"
        json_body = json.dumps(payload, separators=(',', ':'))
        signature = base64.b64encode(
            hmac.new(APP_SECRET.encode(), json_body.encode(), hashlib.sha256).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
            "Authorization": f"Sign {signature}"
        }
        
        print(f"🔐 JSON Body: {json_body}")
        print(f"🔐 Signature: {signature[:20]}...")
        
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
                        
                        # Save tokens to file
                        token_file = {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user_info": user_info,
                            "endpoint": endpoint
                        }
                        
                        with open("ewelink_tokens.json", "w") as f:
                            json.dump(token_file, f, indent=2)
                        
                        print("\n💾 Tokens saved to ewelink_tokens.json")
                        print("\n📋 For Render deployment, set this environment variable:")
                        print(f"EWELINK_ACCESS_TOKEN={access_token}")
                        
                        return access_token, endpoint
                    else:
                        print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    print("\n❌ All endpoints failed. Check the authorization code and try again.")
    return None, None

async def test_token(access_token: str, endpoint: str):
    """Test the access token by getting device list"""
    
    print(f"\n🧪 Testing access token with {endpoint}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID
    }
    
    # Test endpoint - get device list
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
                    print(f"\n✅ Token works! Found {len(devices)} devices:")
                    for device in devices[:3]:  # Show first 3 devices
                        print(f"  - {device.get('name', 'Unknown')} (ID: {device.get('deviceid', 'Unknown')})")
                    return True
                else:
                    print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test Error: {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 exchange_oauth_code.py <authorization_code>")
        print("Example: python3 exchange_oauth_code.py abc123def456")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    
    try:
        access_token, endpoint = asyncio.run(exchange_code_for_token(auth_code))
        
        if access_token:
            # Test the token
            success = asyncio.run(test_token(access_token, endpoint))
            
            if success:
                print("\n🎊 COMPLETE! Your eWeLink OAuth setup is working!")
            else:
                print("\n⚠️ Token received but testing failed. Check device permissions.")
        else:
            print("\n❌ Failed to get access token")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()