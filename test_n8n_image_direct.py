#!/usr/bin/env python3
"""
Direct test of n8n-style image sending (skipping text connectivity check)
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.whatsapp_service import WhatsAppService
from app.services.image_service import ImageService

load_dotenv()

async def test_n8n_image_direct():
    """Test n8n-style image sending directly"""
    
    print("🧪 Testing n8n-style image sending (DIRECT)")
    print("=" * 50)
    
    # Initialize services
    whatsapp_service = WhatsAppService()
    image_service = ImageService()
    
    # Test parameters
    image_path = "/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/emergency_alert_test.jpg"
    phone_number = "56940035815"  # Waldo's number
    caption = "🚨 EMERGENCIA - Test n8n-style image sending"
    
    print(f"📷 Image: {image_path}")
    print(f"📱 To: {phone_number}")
    print(f"🏷️ Caption: {caption}")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return False
    
    original_size = os.path.getsize(image_path)
    print(f"📊 Original size: {original_size} bytes")
    
    # Process image for WhatsApp
    print(f"\n🔄 Processing image for WhatsApp...")
    processed_image = image_service.process_image_for_whatsapp(image_path, convert_to_webp=True)
    
    if not processed_image:
        print(f"❌ Failed to process image")
        return False
    
    processed_size = os.path.getsize(processed_image)
    print(f"✅ Processed: {processed_image} ({processed_size} bytes)")
    
    # Test all three methods
    results = {}
    
    print(f"\n📤 Method 1: n8n-style binary upload...")
    try:
        success1 = await whatsapp_service.send_image_message_n8n_style(phone_number, processed_image, caption)
        results["n8n_style"] = {"success": success1, "error": None}
        print(f"   Result: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    except Exception as e:
        results["n8n_style"] = {"success": False, "error": str(e)}
        print(f"   Result: ❌ EXCEPTION - {str(e)}")
    
    print(f"\n📤 Method 2: Base64 JSON...")
    try:
        success2 = await whatsapp_service.send_image_message(phone_number, processed_image, caption)
        results["base64_json"] = {"success": success2, "error": None}
        print(f"   Result: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    except Exception as e:
        results["base64_json"] = {"success": False, "error": str(e)}
        print(f"   Result: ❌ EXCEPTION - {str(e)}")
    
    print(f"\n📤 Method 3: Multipart form...")
    try:
        success3 = await whatsapp_service.send_image_message_via_media_endpoint(phone_number, processed_image, caption)
        results["multipart_form"] = {"success": success3, "error": None}
        print(f"   Result: {'✅ SUCCESS' if success3 else '❌ FAILED'}")
    except Exception as e:
        results["multipart_form"] = {"success": False, "error": str(e)}
        print(f"   Result: ❌ EXCEPTION - {str(e)}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up...")
    if processed_image != image_path:
        image_service.cleanup_image_file(processed_image)
    
    # Summary
    print(f"\n📋 Test Results Summary:")
    any_success = False
    for method, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"   {method}: {status}")
        if result["success"]:
            any_success = True
    
    print(f"\n🎯 Overall: {'✅ AT LEAST ONE METHOD WORKED!' if any_success else '❌ ALL METHODS FAILED'}")
    
    if not any_success:
        print(f"\n💡 Note: This might be due to the local token issue (ends with 'illq' instead of 'iIlq')")
        print(f"💡 The methods should work on your server with the correct token!")
    
    return any_success

if __name__ == "__main__":
    result = asyncio.run(test_n8n_image_direct())