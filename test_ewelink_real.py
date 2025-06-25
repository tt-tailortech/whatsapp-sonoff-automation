#!/usr/bin/env python3
"""
Test eWeLink API with real credentials
This requires your eWeLink account email and password
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ewelink_service import EWeLinkService

load_dotenv()

async def test_ewelink_real():
    """Test eWeLink with real authentication"""
    print("🏠 Testing eWeLink API with Real Authentication")
    print("=" * 50)
    
    service = EWeLinkService()
    
    try:
        # You need to provide your eWeLink account credentials
        email = input("Enter your eWeLink email: ")
        password = input("Enter your eWeLink password: ")
        
        print(f"\n🔐 Authenticating with eWeLink...")
        auth_success = await service.authenticate(email, password)
        
        if auth_success:
            print("✅ Authentication successful!")
            print(f"Access token: {service.access_token[:20]}...")
            print(f"User ID: {service.user_id}")
            
            # Get devices
            print("\n📱 Getting devices...")
            devices = await service.get_devices()
            print(f"Found {len(devices)} devices:")
            
            for device in devices:
                status = "🟢 Online" if device.online else "🔴 Offline"
                switch_state = device.params.get('switch', 'unknown')
                print(f"  - {device.name} ({device.deviceid}) - {status} - Switch: {switch_state}")
            
            # Test with specific device
            test_device_id = "10011eafd1"  # Your device ID
            print(f"\n🎯 Testing with device {test_device_id}...")
            
            # Get status
            status = await service.get_device_status(test_device_id)
            if status:
                print(f"✅ Device status: Online={status.online}, Switch={status.switch_state}")
                
                # Test command (be careful - this will actually control your device!)
                response = input(f"\nDo you want to test controlling device {test_device_id}? (y/N): ")
                if response.lower() == 'y':
                    command = input("Enter command (ON/OFF/STATUS): ").upper()
                    
                    if command in ['ON', 'OFF']:
                        print(f"Sending {command} command...")
                        success = await service.control_device(test_device_id, command)
                        if success:
                            print(f"✅ Command {command} sent successfully!")
                        else:
                            print(f"❌ Command {command} failed!")
                    elif command == 'STATUS':
                        new_status = await service.get_device_status(test_device_id)
                        if new_status:
                            print(f"✅ Current status: Online={new_status.online}, Switch={new_status.switch_state}")
            else:
                print(f"❌ Could not get status for device {test_device_id}")
                
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_ewelink_real())