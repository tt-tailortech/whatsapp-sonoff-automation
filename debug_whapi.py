#!/usr/bin/env python3
"""
Debug WHAPI.co API endpoints
"""

import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def debug_whapi():
    """Debug WHAPI.co API endpoints"""
    token = os.getenv("WHAPI_TOKEN")
    base_url = "https://gate.whapi.cloud"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Debugging WHAPI.co API endpoints")
    print(f"Token: {token[:20]}...")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Test different endpoints
    endpoints = [
        "/account",
        "/health",
        "/settings",
        "/status"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                print(f"\n🔗 Testing {endpoint}...")
                url = f"{base_url}{endpoint}"
                
                response = await client.get(url, headers=headers)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success: {data}")
                else:
                    print(f"❌ Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
    
    # Test webhook simulation
    print(f"\n📨 Testing webhook POST endpoint...")
    try:
        webhook_url = f"{base_url}/webhook"  # This would be your webhook
        test_payload = {
            "messages": [{
                "id": "test123",
                "from": "+19012976001",
                "type": "text",
                "text": {"body": "STATUS"},
                "timestamp": "1640995200"
            }]
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=test_payload, headers=headers)
            print(f"Webhook test status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Webhook test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_whapi())