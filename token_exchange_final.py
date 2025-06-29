#!/usr/bin/env python3
"""
Final token exchange attempt - trying all possible signature variations
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

async def try_all_signature_methods(auth_code: str):
    """Try every possible signature method for token exchange"""
    
    print("🔄 Trying all signature methods for token exchange...")
    
    payload = {
        "clientId": APP_ID,
        "clientSecret": APP_SECRET,
        "grantType": "authorization_code",
        "code": auth_code,
        "redirectUrl": "http://localhost:3000/callback"
    }
    
    # Different signature methods to try
    signature_methods = [
        {
            "name": "Standard OAuth (APP_ID_timestamp)",
            "func": lambda: {
                "timestamp": str(int(time.time() * 1000)),
                "signature": base64.b64encode(
                    hmac.new(APP_SECRET.encode(), f"{APP_ID}_{str(int(time.time() * 1000))}".encode(), hashlib.sha256).digest()
                ).decode(),
                "use_nonce": True
            }
        },
        {
            "name": "JSON Payload",
            "func": lambda: {
                "timestamp": str(int(time.time() * 1000)),
                "signature": base64.b64encode(
                    hmac.new(APP_SECRET.encode(), json.dumps(payload, separators=(',', ':')).encode(), hashlib.sha256).digest()
                ).decode(),
                "use_nonce": False
            }
        },
        {
            "name": "No Signature (Basic Auth)",
            "func": lambda: {
                "timestamp": str(int(time.time() * 1000)),
                "signature": None,
                "use_nonce": False
            }
        },
        {
            "name": "Client Secret as Signature",
            "func": lambda: {
                "timestamp": str(int(time.time() * 1000)),
                "signature": APP_SECRET,
                "use_nonce": False
            }
        }
    ]
    
    endpoints = [
        "https://us-apia.coolkit.cc/v2/user/oauth/token",  # Response said region "us"
        "https://cn-apia.coolkit.cn/v2/user/oauth/token",
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Endpoint: {endpoint}")
        
        for method in signature_methods:
            print(f"\n🔐 Trying: {method['name']}")
            
            sig_info = method['func']()
            timestamp = sig_info['timestamp']
            signature = sig_info['signature']
            use_nonce = sig_info['use_nonce']
            
            headers = {
                "Content-Type": "application/json",
                "X-CK-Appid": APP_ID,
                "X-CK-Seq": timestamp
            }
            
            if use_nonce:
                nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
                headers["X-CK-Nonce"] = nonce
            
            if signature:
                headers["Authorization"] = f"Sign {signature}"
            
            print(f"🔐 Headers: {json.dumps(headers, indent=2)}")
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(endpoint, headers=headers, json=payload)
                    
                    print(f"📡 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"📄 Response: {response.text}")
                        
                        if data.get("error") == 0:
                            token_data = data.get("data", {})
                            access_token = token_data.get("accessToken")
                            
                            if access_token:
                                print(f"\n🎉 SUCCESS with {method['name']}!")
                                print(f"🔑 Access Token: {access_token[:30]}...")
                                
                                # Save the token
                                with open("ewelink_tokens.json", "w") as f:
                                    json.dump({
                                        "access_token": access_token,
                                        "refresh_token": token_data.get("refreshToken"),
                                        "user_info": token_data.get("user", {}),
                                        "method_used": method['name'],
                                        "endpoint": endpoint
                                    }, f, indent=2)
                                
                                print(f"\n📋 Set in Render: EWELINK_ACCESS_TOKEN={access_token}")
                                return access_token
                        else:
                            error_msg = data.get('msg', 'Unknown error')
                            if "sign verification failed" not in error_msg:
                                print(f"📄 Different error: {error_msg}")
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 token_exchange_final.py <auth_code>")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    
    try:
        token = asyncio.run(try_all_signature_methods(auth_code))
        
        if token:
            print("\n🎊 TOKEN EXCHANGE SUCCESSFUL!")
            print("Your eWeLink OAuth setup is now complete!")
        else:
            print("\n❌ All signature methods failed")
            print("The authorization code may have expired")
            print("Try getting a new code with: python3 final_oauth_fix.py")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()