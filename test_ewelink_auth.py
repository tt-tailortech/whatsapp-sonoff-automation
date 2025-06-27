#!/usr/bin/env python3
"""
Test eWeLink authentication
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ewelink_service import EWeLinkService

load_dotenv()

async def test_ewelink_auth():
    """Test eWeLink authentication"""
    print("🔄 Testing eWeLink Authentication")
    print("=" * 50)
    
    # Check environment variables
    email = os.getenv('EWELINK_EMAIL')
    password = os.getenv('EWELINK_PASSWORD')
    app_id = os.getenv('EWELINK_APP_ID')
    app_secret = os.getenv('EWELINK_APP_SECRET')
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password) if password else 'NOT SET'}")
    print(f"🆔 App ID: {app_id}")
    print(f"🔐 App Secret: {app_secret[:10]}..." if app_secret else "NOT SET")
    
    if not email or not password:
        print("❌ eWeLink credentials not found in environment")
        return False
    
    # Initialize service
    print("\n🔧 Initializing eWeLink service...")
    ewelink_service = EWeLinkService()
    
    # Test authentication
    print(f"\n🔐 Attempting authentication for {email}...")
    success = await ewelink_service.authenticate(email, password)
    
    if success:
        print("✅ Authentication successful!")
        print(f"🎫 Access token: {ewelink_service.access_token[:20]}...")
        print(f"👤 User ID: {ewelink_service.user_id}")
        
        # Test getting devices
        print("\n📱 Getting devices...")
        devices = await ewelink_service.get_devices()
        print(f"📊 Found {len(devices)} devices:")
        
        for device in devices:
            print(f"  - {device.name} ({device.deviceid}) - {'🟢 Online' if device.online else '🔴 Offline'}")
        
        return True
    else:
        print("❌ Authentication failed!")
        return False

if __name__ == "__main__":
    asyncio.run(test_ewelink_auth())