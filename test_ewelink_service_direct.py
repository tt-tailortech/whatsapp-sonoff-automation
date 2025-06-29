#!/usr/bin/env python3
"""
Test eWeLink service directly with the token
"""

import asyncio
import httpx

# Direct test with working credentials
ACCESS_TOKEN = "73d1a52ee534403fcfe294d0b5a26504dbd5bd8a"
BASE_URL = "https://us-apia.coolkit.cc"

async def test_device_api_direct():
    """Test device API directly with Bearer token"""
    
    print("🧪 Testing eWeLink Device API Directly")
    print("=" * 50)
    print(f"🔑 Token: {ACCESS_TOKEN[:20]}...")
    print(f"🌐 URL: {BASE_URL}")
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/v2/device/thing", headers=headers)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"✅ Found {len(devices)} devices!")
                    
                    for device in devices:
                        # Extract from nested itemData structure
                        item_data = device.get('itemData', {})
                        name = item_data.get('name', 'Unknown')
                        device_id = item_data.get('deviceid', 'Unknown')
                        print(f"  - {name} (ID: {device_id})")
                    
                    return devices
                else:
                    print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Request error: {e}")
    
    return []

async def test_service_import():
    """Test importing and using the actual service"""
    
    print("\n🧪 Testing eWeLink Service Class")
    print("=" * 40)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.services.ewelink_service import EWeLinkService
        
        service = EWeLinkService()
        print(f"✅ Service created")
        print(f"🔑 Access token: {service.access_token[:20] if service.access_token else 'None'}...")
        print(f"🌐 Base URL: {service.base_url}")
        
        # Test get_devices
        print("\n📱 Testing get_devices()...")
        devices = await service.get_devices()
        
        print(f"📊 Found {len(devices)} devices")
        for device in devices:
            print(f"  - {device.name} (ID: {device.deviceid})")
        
        return devices
        
    except Exception as e:
        print(f"❌ Service test error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    try:
        # Test 1: Direct API call
        direct_devices = asyncio.run(test_device_api_direct())
        
        # Test 2: Service class
        service_devices = asyncio.run(test_service_import())
        
        print(f"\n📊 Summary:")
        print(f"Direct API: {len(direct_devices)} devices")
        print(f"Service class: {len(service_devices)} devices")
        
        if len(direct_devices) > 0 and len(service_devices) == 0:
            print("🔍 Issue is in the service class implementation")
        elif len(direct_devices) == 0:
            print("🔍 Issue is with the API call or token")
        else:
            print("✅ Both methods working!")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()