#!/usr/bin/env python3
"""
Test manually extracted token
"""

import asyncio
import httpx
import sys

async def test_token(token: str):
    """Test extracted token"""
    
    if not token:
        print("Usage: python3 test_manual_token.py YOUR_TOKEN")
        return
    
    print(f"🧪 Testing token: {token[:20]}...")
    
    endpoints = [
        "https://cn-apia.coolkit.cn",
        "https://us-apia.coolkit.cc", 
        "https://eu-apia.coolkit.cc"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing {endpoint}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
                
                print(f"📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        devices = data.get("data", {}).get("thingList", [])
                        print(f"✅ SUCCESS! Found {len(devices)} devices")
                        
                        for device in devices:
                            print(f"  - {device.get('name')} (ID: {device.get('deviceid')})")
                        
                        print(f"\n💾 Working token for Render:")
                        print(f"EWELINK_ACCESS_TOKEN={token}")
                        return True
                    else:
                        print(f"❌ API Error: {data.get('msg')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_manual_token.py YOUR_TOKEN")
        sys.exit(1)
    
    token = sys.argv[1]
    asyncio.run(test_token(token))
