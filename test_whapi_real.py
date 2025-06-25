#!/usr/bin/env python3
"""
Test WHAPI.co API with real credentials
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.whatsapp_service import WhatsAppService

load_dotenv()

async def test_whapi_real():
    """Test WHAPI.co with real credentials"""
    print("📱 Testing WHAPI.co API")
    print("=" * 50)
    
    service = WhatsAppService()
    
    try:
        # Test account info
        print("🔍 Getting account information...")
        account_info = await service.get_account_info()
        
        if account_info:
            print("✅ Account info retrieved:")
            print(f"  Account: {account_info}")
        else:
            print("❌ Failed to get account info")
            print("This might be due to:")
            print("  - Invalid WHAPI_TOKEN")
            print("  - API endpoint changes")
            print("  - Network connectivity issues")
        
        # Test webhook parsing samples
        print("\n📨 Testing webhook parsing...")
        
        # Sample webhook data (like what you'd receive from WhatsApp)
        sample_webhook = {
            "messages": [{
                "id": "wamid.test123",
                "from": "+19012976001",
                "type": "text",
                "text": {"body": "ON"},
                "timestamp": "1640995200"
            }],
            "contacts": [{
                "profile": {"name": "Test User"}
            }]
        }
        
        parsed = service.parse_whatsapp_webhook(sample_webhook)
        if parsed:
            print(f"✅ Parsed message: '{parsed.text}' from {parsed.contact_name} ({parsed.from_phone})")
        else:
            print("❌ Failed to parse webhook")
        
        # Test sending (optional)
        send_test = input("\nDo you want to test sending a message? This will send a real WhatsApp message! (y/N): ")
        if send_test.lower() == 'y':
            phone_number = input("Enter phone number (with country code, e.g., +1234567890): ")
            message = "🤖 Test message from WhatsApp-Sonoff automation system!"
            
            print(f"Sending test message to {phone_number}...")
            success = await service.send_text_message(phone_number, message)
            
            if success:
                print("✅ Message sent successfully!")
            else:
                print("❌ Message sending failed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_whapi_real())