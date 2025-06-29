#!/usr/bin/env python3
"""
Test eWeLink OAuth 2.0 authentication with your app credentials
"""

import asyncio
import sys
import os
from app.services.ewelink_service import EWeLinkService

# Your OAuth app credentials
APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"
BASE_URL = "https://us-apia.coolkit.cc"  # US region

async def test_oauth_login():
    """Test OAuth login with your credentials"""
    
    print("🔐 Testing eWeLink OAuth 2.0 Authentication")
    print("=" * 50)
    
    # Get user credentials from command line arguments or environment
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        # Check environment variables
        email = os.environ.get('EWELINK_EMAIL', '')
        password = os.environ.get('EWELINK_PASSWORD', '')
        
        if not email or not password:
            print("❌ Please provide credentials:")
            print("   python3 test_oauth_login.py <email> <password>")
            print("   OR set EWELINK_EMAIL and EWELINK_PASSWORD environment variables")
            return
    
    # Create service instance with your OAuth credentials
    service = EWeLinkService()
    service.app_id = APP_ID
    service.app_secret = APP_SECRET
    service.base_url = BASE_URL
    
    print(f"\n🔐 App ID: {APP_ID}")
    print(f"🔐 App Secret: {APP_SECRET[:10]}...")
    print(f"🔐 Base URL: {BASE_URL}")
    print(f"🔐 Email: {email}")
    
    # Test OAuth authentication
    success = await service.authenticate_oauth(email, password)
    
    if success:
        print("\n✅ OAuth authentication successful!")
        print(f"🔐 Access Token: {service.access_token[:30]}..." if service.access_token else "No token")
        print(f"🔐 User ID: {service.user_id}")
        
        # Test getting devices
        print("\n📱 Testing device list...")
        devices = await service.get_devices()
        if devices:
            print(f"✅ Found {len(devices)} devices:")
            for device in devices:
                print(f"  - {device.name} (ID: {device.deviceid}, Online: {device.online})")
        else:
            print("⚠️ No devices found or error getting devices")
            
    else:
        print("\n❌ OAuth authentication failed")
        
        # Try direct login as fallback
        print("\n🔄 Trying direct login as fallback...")
        direct_success = await service.authenticate_direct_login(email, password)
        
        if direct_success:
            print("✅ Direct login successful!")
            print(f"🔐 Access Token: {service.access_token[:30]}..." if service.access_token else "No token")
            print(f"🔐 User ID: {service.user_id}")
        else:
            print("❌ Direct login also failed")

if __name__ == "__main__":
    try:
        asyncio.run(test_oauth_login())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()