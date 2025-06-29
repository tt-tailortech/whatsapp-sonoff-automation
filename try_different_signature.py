#!/usr/bin/env python3
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

async def try_different_signatures():
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    
    # Get fresh code first
    seq = str(int(time.time() * 1000))
    nonce = "zt123456"
    redirect_url = "http://localhost:3000/callback"
    
    message = f"{app_id}_{seq}"
    auth_signature = base64.b64encode(
        hmac.new(app_secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    
    auth_url = f"https://c2ccdn.coolkit.cc/oauth/index.html?state=10011&clientId={app_id}&authorization={auth_signature}&seq={seq}&redirectUrl={redirect_url}&nonce={nonce}&grantType=authorization_code&showQRCode=false"
    
    print("🔐 Fresh OAuth URL (you need to get a new code):")
    print(auth_url)
    print()
    print("Get a fresh code and replace it in the script below...")
    
    # Fresh code
    code = "9b2c3776-7585-4699-bc8e-f42828826aa5"
    
    url = "https://us-apia.coolkit.cc/v2/user/oauth/token"
    
    # Method 1: Try timestamp-based signature like authorization page
    token_seq = str(int(time.time() * 1000))
    token_message = f"{app_id}_{token_seq}"
    token_signature1 = base64.b64encode(
        hmac.new(app_secret.encode(), token_message.encode(), hashlib.sha256).digest()
    ).decode()
    
    payload1 = {
        "code": code,
        "redirectUrl": redirect_url,
        "grantType": "authorization_code"
    }
    
    headers1 = {
        "Content-Type": "application/json",
        "X-CK-Appid": app_id,
        "Authorization": f"Sign {token_signature1}",
        "X-CK-Nonce": nonce
    }
    
    print(f"🔄 Method 1: Timestamp signature")
    print(f"Message: {token_message}")
    print(f"Signature: {token_signature1}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers1, json=payload1)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("error") == 0:
                print("✅ SUCCESS with timestamp signature!")
                return True
    
    # Method 2: Try without Authorization header (maybe it doesn't need signature)
    headers2 = {
        "Content-Type": "application/json",
        "X-CK-Appid": app_id,
    }
    
    print(f"\n🔄 Method 2: No signature")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers2, json=payload1)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("error") == 0:
                print("✅ SUCCESS without signature!")
                return True

asyncio.run(try_different_signatures())