#!/usr/bin/env python3
"""
Test eWeLink device endpoints directly with app credentials
"""

import asyncio
import sys
import os
import httpx
import hmac
import hashlib
import base64
import json
from dotenv import load_dotenv

load_dotenv()

async def test_device_endpoints():
    """Test device endpoints with different authentication methods"""
    
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    base_url = "https://eu-apia.coolkit.cc"
    
    print("🔄 Testing eWeLink Device Endpoints")
    print("=" * 50)
    
    # Test device list endpoint with different auth methods
    endpoints_to_test = [
        "/v2/device/thing",
        "/v2/family",
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📱 Testing endpoint: {endpoint}")
        
        # Try with just app credentials (no user auth)
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": app_id,
        }
        
        url = f"{base_url}{endpoint}"
        print(f"🔗 URL: {url}")
        print(f"📋 Headers: {headers}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if "authorization" in response.text.lower():
                print("💡 This endpoint requires user authorization")
            elif response.status_code == 200:
                print("✅ This endpoint works with app credentials only!")
            else:
                print("❌ This endpoint failed")

if __name__ == "__main__":
    asyncio.run(test_device_endpoints())