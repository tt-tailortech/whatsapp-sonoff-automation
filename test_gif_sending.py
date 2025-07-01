#!/usr/bin/env python3
"""
Test GIF sending functionality directly
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.whatsapp_service import WhatsAppService

load_dotenv()

async def test_gif_sending():
    """Test sending animated siren GIF to Waldo"""
    
    print("🎬 Testing GIF sending functionality")
    print("=" * 50)
    
    # Initialize service
    whatsapp_service = WhatsAppService()
    
    # Test parameters
    gif_path = "/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/animated_emergency_siren.gif"
    phone_number = "56940035815"  # Waldo's number
    caption = "🚨 ALERTA ANIMADA - Prueba de siren GIF 🚨"
    
    print(f"🎬 GIF: {gif_path}")
    print(f"📱 To: {phone_number}")
    print(f"🏷️ Caption: {caption}")
    
    # Check if GIF exists
    if not os.path.exists(gif_path):
        print(f"❌ GIF file not found: {gif_path}")
        return False
    
    file_size = os.path.getsize(gif_path)
    print(f"📊 GIF size: {file_size} bytes")
    
    # Test different methods to send GIF
    print(f"\n📤 Method 1: Sending as GIF via /messages/gif...")
    success1 = await whatsapp_service.send_gif_message(phone_number, gif_path, caption)
    
    print(f"\n📤 Method 2: Sending as image via /messages/image...")
    success2 = await whatsapp_service.send_image_message(phone_number, gif_path, caption + " (as image)")
    
    print(f"\n📤 Method 3: Sending via n8n-style /messages/media/image...")
    success3 = await whatsapp_service.send_image_message_n8n_style(phone_number, gif_path, caption + " (n8n style)")
    
    success = success1 or success2 or success3
    
    # Results
    print(f"\n📋 Results:")
    print(f"   GIF sending: {'✅ Success' if success else '❌ Failed'}")
    
    if success:
        print(f"🎉 Animated siren GIF sent to Waldo successfully!")
    else:
        print(f"❌ Failed to send GIF - check token and API response above")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_gif_sending())