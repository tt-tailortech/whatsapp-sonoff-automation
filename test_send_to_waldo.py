#!/usr/bin/env python3
"""
Test sending a message to Waldo using WHAPI credentials
"""

import asyncio
import httpx
import os
from app.config import settings

async def send_test_message():
    """Send a test message to Waldo"""
    
    # From the logs, Waldo's number is 56940035815
    phone_formats = [
        "56940035815",                  # Just the number
        "+56940035815",                # With country code
        "56940035815@s.whatsapp.net",  # Current format used in logs
        "56940035815@c.us",            # Alternative WhatsApp format
    ]
    
    message = "🤖 TEST: This is a test message from the alarm system debug script"
    
    headers = {
        "Authorization": f"Bearer {settings.whapi_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔑 Using token: {settings.whapi_token[:15]}...")
    print(f"🌐 Base URL: {settings.whapi_base_url}")
    print(f"📝 Message: {message}")
    print()
    
    for i, phone_format in enumerate(phone_formats, 1):
        print(f"🧪 Test {i}/4: Trying phone format: {phone_format}")
        
        url = f"{settings.whapi_base_url}/messages/text"
        payload = {
            "to": phone_format,
            "body": message,
            "typing_time": 1
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"   📡 Status: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS with format: {phone_format}")
                    return True, phone_format
                else:
                    print(f"   ❌ Failed with {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {str(e)} ({type(e).__name__})")
        
        print()
    
    return False, None

async def test_whapi_account():
    """Test WHAPI account status"""
    
    print("🔍 Testing WHAPI account status...")
    
    headers = {
        "Authorization": f"Bearer {settings.whapi_token}",
        "Content-Type": "application/json"
    }
    
    # Common WHAPI endpoints to test
    endpoints = [
        "/account",
        "/status", 
        "/me",
        "/settings",
    ]
    
    for endpoint in endpoints:
        url = f"{settings.whapi_base_url}{endpoint}"
        print(f"🧪 Testing: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                
                print(f"   📡 Status: {response.status_code}")
                if response.status_code < 400:
                    print(f"   📄 Response: {response.text[:200]}...")
                    if response.status_code == 200:
                        print(f"   ✅ {endpoint} endpoint works!")
                        return True
                else:
                    print(f"   ❌ Error: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()
    
    return False

async def main():
    """Main test function"""
    
    print("=" * 60)
    print("🧪 WHAPI.cloud Integration Test")
    print("=" * 60)
    print()
    
    # First test account access
    account_ok = await test_whapi_account()
    print()
    
    if account_ok:
        print("✅ Account access confirmed, proceeding with message test...")
        print()
        success, working_format = await send_test_message()
        
        if success:
            print(f"🎉 Message sent successfully using format: {working_format}")
        else:
            print("❌ All message formats failed")
    else:
        print("❌ Could not access WHAPI account - check token and connectivity")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())