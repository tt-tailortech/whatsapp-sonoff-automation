#!/usr/bin/env python3
"""
Token exchange using the forum solution: "encrypt the entire JSON body message as the sign"
"""

import asyncio
import httpx
import json
import hmac
import hashlib
import base64

APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"

async def forum_method_exchange(auth_code: str):
    """Use the forum solution: sign the entire JSON body"""
    
    print("🔄 Forum method: 'encrypt the entire JSON body message as the sign'")
    
    # Payload for token exchange
    payload = {
        "clientId": APP_ID,
        "clientSecret": APP_SECRET,
        "grantType": "authorization_code",
        "code": auth_code,
        "redirectUrl": "http://localhost:3000/callback"
    }
    
    # Forum solution: sign the entire JSON body
    json_body = json.dumps(payload, separators=(',', ':'))
    signature = base64.b64encode(
        hmac.new(APP_SECRET.encode(), json_body.encode(), hashlib.sha256).digest()
    ).decode()
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": APP_ID,
        "Authorization": f"Sign {signature}"
    }
    
    endpoints = [
        "https://us-apia.coolkit.cc/v2/user/oauth/token",
        "https://cn-apia.coolkit.cn/v2/user/oauth/token"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Trying: {endpoint}")
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
                        
                        if access_token:
                            print(f"\n🎉 SUCCESS with forum method!")
                            print(f"🔑 Access Token: {access_token}")
                            
                            with open("ewelink_success_token.json", "w") as f:
                                json.dump({
                                    "access_token": access_token,
                                    "refresh_token": token_data.get("refreshToken"),
                                    "user_info": token_data.get("user", {}),
                                    "method": "forum_json_body",
                                    "endpoint": endpoint
                                }, f, indent=2)
                            
                            print(f"\n📋 SET THIS IN RENDER:")
                            print(f"EWELINK_ACCESS_TOKEN={access_token}")
                            
                            return access_token
                    else:
                        error_msg = data.get('msg', 'Unknown error')
                        print(f"❌ Error: {error_msg}")
                else:
                    print(f"❌ HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    # Fresh code
    auth_code = "46da0a5d-a13f-4d40-98ab-fec920f9fc60"
    
    try:
        token = asyncio.run(forum_method_exchange(auth_code))
        
        if not token:
            print("\n❌ Forum method failed too")
            print("The authorization code may have expired")
            print("At this point, we have proven the OAuth flow works")
            print("We just need to solve the token exchange signature")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()