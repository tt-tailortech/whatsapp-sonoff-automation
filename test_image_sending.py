#!/usr/bin/env python3
"""
Test image sending functionality with the emergency alert image
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.whatsapp_service import WhatsAppService
from app.services.image_service import ImageService

load_dotenv()

async def test_image_sending():
    """Test sending emergency alert image to Waldo"""
    
    print("🧪 Testing image sending functionality")
    print("=" * 50)
    
    # Initialize services
    whatsapp_service = WhatsAppService()
    image_service = ImageService()
    
    # Test parameters
    image_path = "/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/emergency_alert_test.jpg"
    phone_number = "56940035815"  # Waldo's number
    caption = "🚨 EMERGENCIA - Prueba de alerta comunitaria del sistema de alarma"
    
    print(f"📷 Original image: {image_path}")
    print(f"📱 Sending to: {phone_number}")
    print(f"🏷️ Caption: {caption}")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return False
    
    original_size = os.path.getsize(image_path)
    print(f"📊 Original size: {original_size} bytes")
    
    # Step 1: Process image for WhatsApp (resize and convert to WebP)
    print(f"\n🔄 Step 1: Processing image for WhatsApp...")
    processed_image = image_service.process_image_for_whatsapp(image_path, convert_to_webp=True)
    
    if not processed_image:
        print(f"❌ Failed to process image")
        return False
    
    processed_size = os.path.getsize(processed_image)
    print(f"✅ Image processed: {processed_image}")
    print(f"📊 Processed size: {processed_size} bytes")
    print(f"📉 Size reduction: {((original_size - processed_size) / original_size * 100):.1f}%")
    
    # Quick connectivity test with text message
    print(f"\n🔗 Testing WHAPI connectivity with text message...")
    text_success = await whatsapp_service.send_text_message(phone_number, "🧪 Testing connectivity before sending image...")
    print(f"   Text message: {'✅ Success' if text_success else '❌ Failed'}")
    
    if not text_success:
        print(f"❌ WHAPI connection failed - skipping image test")
        return False
    
    # Step 2: Send image via WhatsApp (try multiple methods)
    print(f"\n📤 Step 2: Sending image via WhatsApp...")
    
    # Method 1: Base64 method with /messages/image
    print(f"📤 Method 1: Base64 with /messages/image...")
    success1 = await whatsapp_service.send_image_message(phone_number, processed_image, caption)
    
    if success1:
        print(f"✅ Method 1 (Base64) succeeded!")
        success = True
    else:
        print(f"❌ Method 1 (Base64) failed, trying Method 2...")
        
        # Method 2: Multipart upload with /messages/media/image
        print(f"📤 Method 2: Multipart with /messages/media/image...")
        success2 = await whatsapp_service.send_image_message_via_media_endpoint(phone_number, processed_image, caption)
        
        if success2:
            print(f"✅ Method 2 (Media Endpoint) succeeded!")
            success = True
        else:
            print(f"❌ Method 2 (Media Endpoint) failed, trying Method 3...")
            
            # Method 3: n8n-style binary upload with query parameters
            print(f"📤 Method 3: n8n-style binary upload...")
            success3 = await whatsapp_service.send_image_message_n8n_style(phone_number, processed_image, caption)
            
            if success3:
                print(f"✅ Method 3 (n8n-style) succeeded!")
                success = True
            else:
                print(f"❌ All three methods failed")
                success = False
    
    # Step 3: Cleanup
    print(f"\n🧹 Step 3: Cleaning up temporary files...")
    if processed_image != image_path:
        image_service.cleanup_image_file(processed_image)
    
    # Results
    print(f"\n📋 Results:")
    print(f"   Image processing: ✅ Success")
    print(f"   WhatsApp sending: {'✅ Success' if success else '❌ Failed'}")
    print(f"   Overall test: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_image_sending())