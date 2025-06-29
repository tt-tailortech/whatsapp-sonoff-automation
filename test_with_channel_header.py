#!/usr/bin/env python3
"""
Test WHAPI with channel ID in headers
"""

import asyncio
import httpx

async def test_with_channel_headers():
    """Test including channel ID in headers"""
    
    token = "XQEoTE5p8D0cyEKuwyCM6m3qndywillq"
    base_url = "https://gate.whapi.cloud"
    channel_id = "NEBULA-CMU7E"
    
    # Try different header combinations
    header_variants = [
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Channel-ID": channel_id
        },
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json", 
            "Channel": channel_id
        },
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-API-Channel": channel_id
        },
        {
            "Authorization": f"Bearer {channel_id}:{token}",
            "Content-Type": "application/json"
        }
    ]
    
    payload = {
        "to": "56940035815",
        "body": "🧪 Testing with channel headers"
    }
    
    for i, headers in enumerate(header_variants, 1):
        print(f"🧪 Test {i}: Headers = {headers}")
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(f"{base_url}/messages/text", headers=headers, json=payload)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS!")
                    return True
        except Exception as e:
            print(f"   Error: {e}")
        print()
    
    # Try channel-specific URL
    print("🧪 Test 5: Channel-specific URL...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        channel_url = f"{base_url}/channels/{channel_id}/messages/text"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(channel_url, headers=headers, json=payload)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_with_channel_headers())