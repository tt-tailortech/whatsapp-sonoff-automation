#!/usr/bin/env python3
"""
Quick OAuth flow - minimizes time between code generation and exchange
"""

import asyncio
import os
import time
import hmac
import hashlib
import base64
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

async def quick_oauth():
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    redirect_url = "http://localhost:3000/callback"
    
    # Generate fresh OAuth URL
    seq = str(int(time.time() * 1000))
    nonce = "zt123456"
    
    message = f"{app_id}_{seq}"
    signature = base64.b64encode(
        hmac.new(app_secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    
    auth_url = f"https://c2ccdn.coolkit.cc/oauth/index.html?state=10011&clientId={app_id}&authorization={signature}&seq={seq}&redirectUrl={redirect_url}&nonce={nonce}&grantType=authorization_code&showQRCode=false"
    
    print("🔐 Quick eWeLink OAuth")
    print("=" * 50)
    print("1. Open this URL NOW:")
    print(auth_url)
    print()
    print("2. Log in and authorize")
    print("3. When redirected to localhost, IMMEDIATELY paste the full URL here:")
    
    # Get the callback URL from user
    callback_url = input("Paste callback URL: ").strip()
    
    # Extract code
    try:
        code = callback_url.split("code=")[1].split("&")[0]
        print(f"📥 Extracted code: {code}")
    except:
        print("❌ Could not extract code from URL")
        return
    
    # Exchange immediately
    print("🔄 Exchanging code for token...")
    
    url = "https://us-apia.coolkit.cc/v2/user/oauth/token"
    payload = {
        "code": code,
        "redirectUrl": redirect_url,
        "grantType": "authorization_code"
    }
    
    # Sign the payload
    json_payload = json.dumps(payload, separators=(',', ':'))
    token_signature = base64.b64encode(
        hmac.new(app_secret.encode(), json_payload.encode(), hashlib.sha256).digest()
    ).decode()
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": app_id,
        "Authorization": f"Sign {token_signature}"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("error") == 0:
                access_token = data["data"]["accessToken"]
                refresh_token = data["data"].get("refreshToken")
                
                print("✅ SUCCESS! OAuth tokens received:")
                print(f"🎫 Access Token: {access_token}")
                if refresh_token:
                    print(f"🔄 Refresh Token: {refresh_token}")
                
                print("\n📝 Add these to your .env file:")
                print(f"EWELINK_ACCESS_TOKEN={access_token}")
                if refresh_token:
                    print(f"EWELINK_REFRESH_TOKEN={refresh_token}")
                
                return True
            else:
                print(f"❌ Error: {data.get('msg', 'Unknown error')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    return False

if __name__ == "__main__":
    asyncio.run(quick_oauth())