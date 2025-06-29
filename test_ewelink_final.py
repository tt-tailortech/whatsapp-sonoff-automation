#!/usr/bin/env python3
"""
Final test of eWeLink authentication with Home Assistant credentials
"""

import asyncio
from app.services.ewelink_service import EWeLinkService

async def test_ewelink_auth():
    """Test eWeLink authentication with the new credentials"""
    
    print("🧪 Testing eWeLink Authentication with Home Assistant Credentials")
    print("=" * 70)
    
    # Create service instance
    service = EWeLinkService()
    
    print(f"🔐 App ID: {service.app_id}")
    print(f"🔐 App Secret: {service.app_secret[:10]}...")
    print(f"🔐 Base URL: {service.base_url}")
    print(f"🔐 Email: {service.email}")
    
    # Test authentication
    print("\n🔄 Testing authentication...")
    success = await service.authenticate(service.email, service.password)
    
    if success:
        print("✅ Authentication successful!")
        print(f"🔑 Access Token: {service.access_token[:30]}..." if service.access_token else "No token")
        
        # Test getting devices
        print("\n📱 Testing device list...")
        devices = await service.get_devices()
        
        if devices:
            print(f"✅ Found {len(devices)} devices:")
            for device in devices:
                print(f"  - {device.name} (ID: {device.deviceid}, Online: {device.online})")
        else:
            print("⚠️ No devices found or error getting devices")
            
        # Test device control if we have devices
        if devices:
            test_device = devices[0]
            print(f"\n🎛️ Testing device control with: {test_device.name}")
            
            # Test ON command
            control_success = await service.control_device(test_device.deviceid, "ON")
            if control_success:
                print("✅ Device control test successful!")
            else:
                print("❌ Device control test failed")
                
    else:
        print("❌ Authentication failed")
        print("Check the error messages above for details")

if __name__ == "__main__":
    try:
        asyncio.run(test_ewelink_auth())
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()