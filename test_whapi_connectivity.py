#!/usr/bin/env python3
"""
Test WHAPI.cloud connectivity and API status
"""

import asyncio
import httpx
from app.config import settings

async def test_whapi_connectivity():
    """Test basic connectivity to WHAPI.cloud"""
    
    print(f"🌐 Testing connectivity to {settings.whapi_base_url}")
    print(f"🔑 Using token: {settings.whapi_token[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {settings.whapi_token}",
        "Content-Type": "application/json"
    }
    
    # Test basic API status endpoint
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to get account info or status
            url = f"{settings.whapi_base_url}/account"
            print(f"🧪 Testing GET {url}")
            
            response = await client.get(url, headers=headers)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ WHAPI.cloud is reachable and token is valid")
                return True
            else:
                print(f"❌ WHAPI.cloud returned error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Connectivity test failed: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        return False

async def test_phone_format():
    """Test different phone number formats"""
    
    print("\n🔢 Testing phone number formats...")
    
    # The number from logs: 56940035815
    formats_to_test = [
        "56940035815@s.whatsapp.net",  # Current format
        "56940035815",                  # Just the number
        "+56940035815",                # With plus
        "56940035815@c.us",            # Alternative WhatsApp format
    ]
    
    for phone_format in formats_to_test:
        print(f"   📱 {phone_format}")
    
    print("📝 Recommendation: Test with the basic number format first")

if __name__ == "__main__":
    result1 = asyncio.run(test_whapi_connectivity())
    asyncio.run(test_phone_format())
    print(f"\nConnectivity test result: {result1}")