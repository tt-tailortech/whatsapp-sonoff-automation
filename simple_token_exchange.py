#!/usr/bin/env python3
"""
Simple token exchange using exact same method that worked for getting the code
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

async def simple_token_exchange(auth_code: str):
    """Use the EXACT same signature method that worked for getting the code"""
    
    print("🔄 Simple token exchange (using EXACT same method as code generation)...")
    
    # Use EXACT same approach as the working code generation
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    
    # EXACT same signature method that worked
    sign_string = f"{APP_ID}_{timestamp}"
    signature = base64.b64encode(
        hmac.new(APP_SECRET.encode(), sign_string.encode(), hashlib.sha256).digest()
    ).decode()
    
    # Payload for token exchange
    payload = {
        "clientId": APP_ID,
        "clientSecret": APP_SECRET,
        "grantType": "authorization_code",
        "code": auth_code,
        "redirectUrl": "http://localhost:3000/callback"
    }
    
    # EXACT same headers as working code generation
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID,
        "X-CK-Nonce": nonce,
        "X-CK-Seq": timestamp,
        "Authorization": f"Sign {signature}"
    }
    
    # Try US endpoint first (response said region "us")
    endpoint = "https://us-apia.coolkit.cc/v2/user/oauth/token"
    
    print(f"🌐 Endpoint: {endpoint}")
    print(f"🔐 Signature method: APP_ID_{timestamp}")
    print(f"🔐 Generated signature: {signature}")
    print(f"📝 Auth code: {auth_code}")
    
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
                    
                    if access_token:
                        print(f"\n🎉 SUCCESS!")
                        print(f"🔑 Access Token: {access_token}")
                        
                        # Save it
                        with open("ewelink_final_token.json", "w") as f:
                            json.dump({
                                "access_token": access_token,
                                "refresh_token": token_data.get("refreshToken"),
                                "user_info": token_data.get("user", {}),
                                "timestamp": timestamp
                            }, f, indent=2)
                        
                        print(f"\n📋 FOR RENDER DEPLOYMENT:")
                        print(f"EWELINK_ACCESS_TOKEN={access_token}")
                        
                        return access_token
                else:
                    print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    return None

if __name__ == "__main__":
    # Use the fresh code we just got
    auth_code = "46da0a5d-a13f-4d40-98ab-fec920f9fc60"
    
    try:
        token = asyncio.run(simple_token_exchange(auth_code))
        
        if token:
            print("\n🎊 COMPLETE! Your eWeLink OAuth is now working!")
        else:
            print("\n❌ Token exchange failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()