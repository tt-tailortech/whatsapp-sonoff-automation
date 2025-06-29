#!/usr/bin/env python3
import asyncio
import os
import hmac
import hashlib
import base64
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

async def exact_signature_match():
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    
    # Use the EXACT same seq that was in the auth URL: 1750992536004
    seq = "1750992536004"
    code = "9b2c3776-7585-4699-bc8e-f42828826aa5"
    redirect_url = "http://localhost:3000/callback"
    nonce = "zt123456"
    
    # Use the exact same signature method as authorization
    message = f"{app_id}_{seq}"
    signature = base64.b64encode(
        hmac.new(app_secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    
    url = "https://us-apia.coolkit.cc/v2/user/oauth/token"
    
    # Try adding seq parameter to the token request
    payload = {
        "code": code,
        "redirectUrl": redirect_url,
        "grantType": "authorization_code",
        "seq": seq
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": app_id,
        "Authorization": f"Sign {signature}",
        "X-CK-Nonce": nonce
    }
    
    print(f"🔄 Using exact same seq: {seq}")
    print(f"🔗 Message: {message}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 Payload: {payload}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("error") == 0:
                access_token = data["data"]["accessToken"]
                refresh_token = data["data"].get("refreshToken")
                
                print("✅ SUCCESS!")
                print(f"🎫 Access Token: {access_token}")
                if refresh_token:
                    print(f"🔄 Refresh Token: {refresh_token}")
                
                # Add to .env
                print("\n📝 Add these to .env:")
                print(f"EWELINK_ACCESS_TOKEN={access_token}")
                if refresh_token:
                    print(f"EWELINK_REFRESH_TOKEN={refresh_token}")
                
                return True
            else:
                print(f"❌ Error: {data.get('msg', 'Unknown error')}")

asyncio.run(exact_signature_match())