#!/usr/bin/env python3
"""
Test with exact token from WHAPI dashboard
"""

import asyncio
import httpx

async def test_with_dashboard_token():
    """Test using exact token from dashboard"""
    
    # Exact values from dashboard
    token = "XQEoTE5p8D0cyEKuwyCM6m3qndywillq"
    base_url = "https://gate.whapi.cloud"
    channel_id = "NEBULA-CMU7E"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"🧪 Testing with dashboard token: {token}")
    print(f"🌐 Base URL: {base_url}")
    print(f"📡 Channel ID: {channel_id}")
    print()
    
    # Test 1: Channel health check
    print("1️⃣ Testing channel health...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/health", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Try sending message to Waldo (from logs: 56940035815)
    print("2️⃣ Testing message send to Waldo...")
    payload = {
        "to": "56940035815",  # Just the number without @s.whatsapp.net
        "body": "🧪 Test from dashboard token - direct number format"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/messages/text", headers=headers, json=payload)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS! Message sent!")
            else:
                print("   ❌ Failed to send message")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Try with @s.whatsapp.net format
    print("3️⃣ Testing with WhatsApp format...")
    payload2 = {
        "to": "56940035815@s.whatsapp.net",
        "body": "🧪 Test from dashboard token - WhatsApp format"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/messages/text", headers=headers, json=payload2)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_dashboard_token())