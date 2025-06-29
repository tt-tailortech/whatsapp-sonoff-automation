#!/usr/bin/env python3
"""
Simple test script to debug WHAPI message sending
"""

import asyncio
import os
from app.services.whatsapp_service import WhatsAppService

async def test_send_message():
    """Test sending a WhatsApp message via WHAPI"""
    whatsapp = WhatsAppService()
    
    # Test phone number from the logs
    phone_number = "56940035815@s.whatsapp.net"
    test_message = "DEBUG: Testing message sending from test script"
    
    print(f"🧪 Testing message send to {phone_number}")
    print(f"🧪 Message: {test_message}")
    print(f"🧪 Base URL: {whatsapp.base_url}")
    print(f"🧪 Token (first 10 chars): {whatsapp.token[:10]}...")
    
    success = await whatsapp.send_text_message(phone_number, test_message)
    
    if success:
        print("✅ Message sent successfully!")
    else:
        print("❌ Message sending failed!")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_send_message())
    print(f"Final result: {result}")