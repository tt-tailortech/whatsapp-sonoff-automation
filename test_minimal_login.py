#!/usr/bin/env python3
"""
Test with minimal parameters and verify app credentials
"""

import asyncio
import os
import hmac
import hashlib
import base64
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_minimal_login():
    """Test with minimal payload"""
    
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    email = os.getenv('EWELINK_EMAIL')
    password = os.getenv('EWELINK_PASSWORD')
    
    print("🔐 Testing Minimal Login Approach")
    print("=" * 50)
    print(f"App ID: {app_id}")
    print(f"App Secret: {app_secret[:10]}...")
    print(f"Email: {email}")
    
    # Test different payload combinations
    payloads_to_try = [
        # Minimal - just email/password
        {
            "email": email,
            "password": password
        },
        # With different country codes
        {
            "email": email,
            "password": password,
            "countryCode": "+1"
        },
        {
            "email": email,
            "password": password,
            "countryCode": "+86"
        },
        # Try with phoneNumber instead (though we don't have one)
        # Try with different parameter order
        {
            "password": password,
            "email": email,
            "countryCode": "+56"
        }
    ]
    
    base_url = "https://us-apia.coolkit.cc"  # Use US since OAuth worked there
    url = f"{base_url}/v2/user/login"
    
    for i, payload in enumerate(payloads_to_try):
        print(f"\n🔄 Attempt {i+1}: {payload}")
        
        # Sign JSON payload
        json_payload = json.dumps(payload, separators=(',', ':'))
        signature = base64.b64encode(
            hmac.new(app_secret.encode(), json_payload.encode(), hashlib.sha256).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": app_id,
            "Authorization": f"Sign {signature}"
        }
        
        print(f"📋 JSON: {json_payload}")
        print(f"🔐 Signature: {signature}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"📊 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        print("✅ SUCCESS!")
                        access_token = data["data"]["at"]
                        print(f"🎫 Access Token: {access_token}")
                        return True
                    else:
                        error_msg = data.get('msg', 'Unknown error')
                        if error_msg != "sign verification failed":
                            print(f"⚠️ Different error: {error_msg}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n❌ All attempts failed")
    print("\n🔍 This suggests either:")
    print("1. The App Secret is incorrect")
    print("2. The app is OAuth-only and doesn't support direct login")  
    print("3. There's a specific signature format we're missing")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_minimal_login())