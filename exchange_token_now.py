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

async def exchange_now():
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    code = "543e7feb-6a05-4133-81b2-3af2fd495e6d"
    redirect_url = "http://localhost:3000/callback"
    
    url = "https://us-apia.coolkit.cc/v2/user/oauth/token"
    payload = {
        "code": code,
        "redirectUrl": redirect_url,
        "grantType": "authorization_code"
    }
    
    # Sign the payload
    json_payload = json.dumps(payload, separators=(',', ':'))
    signature = base64.b64encode(
        hmac.new(app_secret.encode(), json_payload.encode(), hashlib.sha256).digest()
    ).decode()
    
    headers = {
        "Content-Type": "application/json",
        "X-CK-Appid": app_id,
        "Authorization": f"Sign {signature}"
    }
    
    print(f"🔄 Exchanging code: {code}")
    print(f"🔗 URL: {url}")
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
                
                return True
            else:
                print(f"❌ Error: {data.get('msg', 'Unknown error')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    return False

asyncio.run(exchange_now())