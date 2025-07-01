#!/usr/bin/env python3
"""
Test animated siren emergency alert and send to Waldo
"""

import asyncio
import os
from create_animated_siren_alert import create_animated_emergency_alert_gif
from app.services.whatsapp_service import WhatsAppService
from dotenv import load_dotenv

load_dotenv()

async def test_and_send_animated_siren_alert():
    """Create animated siren alert with Waldo's data and send it"""
    
    print("🚨 Testing Animated Siren Emergency Alert")
    print("=" * 60)
    
    # Test with Waldo's data (simulating sender info)
    test_case = {
        "street_address": "Avenida Las Condes 2024",
        "phone_number": "+56 9 4003 5815",  # Waldo's number formatted
        "contact_name": "Waldo",              # Sender name
        "incident_type": "EMERGENCIA MÉDICA",
        "neighborhood_name": "Comunidad Local",
        "alert_title": "EMERGENCIA",
        "emergency_number": "SAMU 131",
        "num_frames": 12,                     # 12-frame animation
        "frame_duration": 150                 # 150ms per frame
    }
    
    print(f"🎯 Creating animated alert with Waldo's data:")
    print(f"   📱 Contact: {test_case['contact_name']} ({test_case['phone_number']})")
    print(f"   🚨 Type: {test_case['incident_type']}")
    print(f"   📍 Location: {test_case['street_address']}")
    print(f"   🎬 Animation: {test_case['num_frames']} frames")
    
    # Step 1: Create animated GIF
    try:
        print(f"\n🚨 Generating animated siren alert...")
        gif_path = create_animated_emergency_alert_gif(**test_case)
        
        if not gif_path or not os.path.exists(gif_path):
            print("❌ Failed to create animated GIF")
            return False
        
        file_size = os.path.getsize(gif_path)
        print(f"✅ Animated GIF created: {os.path.basename(gif_path)}")
        print(f"📊 Size: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Error creating GIF: {str(e)}")
        return False
    
    # Step 2: Send to Waldo via WhatsApp
    print(f"\n📤 Sending animated siren alert to Waldo...")
    
    whatsapp_service = WhatsAppService()
    target_phone = "56940035815"  # Waldo's number for sending
    caption = f"🚨 ALERTA ANIMADA AVANZADA - {test_case['incident_type']}\n📍 {test_case['street_address']}\n👤 Reportado por: {test_case['contact_name']}"
    
    try:
        success = await whatsapp_service.send_gif_message(target_phone, gif_path, caption)
        
        if success:
            print(f"✅ Animated siren alert sent successfully to Waldo!")
            print(f"🎬 Features sent:")
            print(f"   🚨 Spinning modern siren with rotating light beams")
            print(f"   💫 Pulsing center light effect")
            print(f"   ⚡ Outer glow animation")
            print(f"   🌙 Night sky with stars and moon")
            print(f"   📱 Professional emergency layout")
            print(f"   👤 Populated with Waldo's contact info")
            return True
        else:
            print(f"❌ Failed to send animated alert to Waldo")
            return False
            
    except Exception as e:
        print(f"❌ Error sending GIF: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_and_send_animated_siren_alert())
    if result:
        print(f"\n🏆 SUCCESS! Animated siren emergency alert sent to Waldo!")
        print(f"🚨 Eye-catching spinning animation with professional emergency info!")
    else:
        print(f"\n❌ Test failed!")