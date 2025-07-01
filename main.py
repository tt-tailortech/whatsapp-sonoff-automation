import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Create app first
app = FastAPI(
    title="WhatsApp-Sonoff TEST Automation",
    description="WhatsApp TEST command automation for Sonoff device control",
    version="1.0.0"
)

# Ultra basic test - BEFORE any imports
@app.get("/emergency-test")
async def emergency_test():
    return {"message": "EMERGENCY TEST WORKS", "time": "now"}

@app.get("/gif-test")
async def gif_test():
    return {"message": "GIF endpoint accessible", "status": "ready"}

@app.get("/debug-status")
async def debug_status():
    """Simple debug endpoint to check server status"""
    import sys
    import os
    
    return {
        "server_status": "running",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "services_initialized": SERVICES_INITIALIZED,
        "available_commands": getattr(command_processor, 'valid_commands', []) if command_processor else [],
        "environment_check": {
            "whapi_token": "configured" if os.getenv("WHAPI_TOKEN") else "missing",
            "openai_key": "configured" if os.getenv("OPENAI_API_KEY") else "missing",
            "ewelink_email": "configured" if os.getenv("EWELINK_EMAIL") else "missing"
        }
    }

# Initialize services with error handling
SERVICES_INITIALIZED = False  # Define early to avoid scope issues

# Initialize service variables to avoid scope issues
whatsapp_service = None
voice_service = None
image_service = None
ewelink_service = None
command_processor = None
IMAGE_SERVICE_AVAILABLE = False

try:
    from app.config import settings
    from app.models import WhatsAppWebhookPayload
    from app.services.whatsapp_service import WhatsAppService
    from app.services.voice_service import VoiceService  # Re-enabled with OpenAI only
    from app.services.ewelink_service import EWeLinkService
    from app.services.command_processor import CommandProcessor
    
    # Try to import image service (might fail if Pillow not available)
    try:
        from app.services.image_service import ImageService
        IMAGE_SERVICE_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ ImageService not available: {str(e)}")
        IMAGE_SERVICE_AVAILABLE = False
        ImageService = None

    # Create temp audio directory
    os.makedirs(settings.temp_audio_dir, exist_ok=True)
    
    # Clean up old temporary files on startup
    try:
        from cleanup_temp_files import cleanup_temporary_files
        cleanup_temporary_files()
    except Exception as e:
        print(f"⚠️ Cleanup warning: {str(e)}")
    
    # Check for professional emergency alert image, fallback to creating test image
    professional_image_path = "./emergency_alert_professional.jpg"
    test_image_path = "./emergency_alert_test.jpg"
    
    if os.path.exists(professional_image_path):
        print(f"✅ Using professional emergency alert image: {professional_image_path}")
    elif not os.path.exists(test_image_path):
        try:
            from create_test_image import create_emergency_alert_image
            create_emergency_alert_image()
            print(f"✅ Created fallback emergency alert test image: {test_image_path}")
        except Exception as e:
            print(f"⚠️ Could not create emergency alert image: {str(e)}")

    # Initialize services with individual error handling
    print("🔄 Initializing WhatsApp service...")
    whatsapp_service = WhatsAppService()
    print("✅ WhatsApp service initialized")
    
    print("🔄 Initializing Voice service...")
    voice_service = VoiceService()  # Re-enabled
    print("✅ Voice service initialized")
    
    print("🔄 Initializing Image service...")
    image_service = ImageService() if IMAGE_SERVICE_AVAILABLE else None  # For image processing
    print(f"✅ Image service: {'initialized' if IMAGE_SERVICE_AVAILABLE else 'disabled'}")
    
    print("🔄 Initializing eWeLink service...")
    ewelink_service = EWeLinkService()
    print("✅ eWeLink service initialized")
    
    print("🔄 Initializing Command processor...")
    command_processor = CommandProcessor(whatsapp_service, ewelink_service)
    print("✅ Command processor initialized")
    
    # Display configured trigger commands
    print("\n🚨" + "="*60)
    print("🚨 WHATSAPP EMERGENCY COMMAND SYSTEM INITIALIZED")
    print("🚨" + "="*60)
    
    if hasattr(command_processor, 'valid_commands'):
        trigger_commands = command_processor.valid_commands
        print(f"📢 CONFIGURED TRIGGER KEYWORDS:")
        for i, cmd in enumerate(trigger_commands, 1):
            print(f"   {i}. '{cmd}' - Activates emergency response system")
        
        print(f"\n🎯 SUPPORTED MESSAGE PATTERNS:")
        print(f"   • SOS → EMERGENCIA GENERAL")
        print(f"   • sos → EMERGENCIA GENERAL") 
        print(f"   • SOS INCENDIO → INCENDIO")
        print(f"   • SOS EMERGENCIA MÉDICA → EMERGENCIA MÉDICA")
        print(f"   • SOS ACCIDENTE VEHICULAR → ACCIDENTE VEHICULAR (max 2 words)")
        print(f"   • S.O.S TERREMOTO → TERREMOTO")
        print(f"   • Any message containing SOS triggers emergency response")
        
        print(f"\n📱 TARGET GROUP CHAT: TEST_ALARM (120363400467632358@g.us)")
        print(f"🔧 DEVICE CONTROL: Sonoff switches integrated")
        print(f"🎤 VOICE ALERTS: OpenAI TTS (Spanish)")
        print(f"📷 IMAGE ALERTS: {'✅ Available' if IMAGE_SERVICE_AVAILABLE else '❌ Disabled'}")
        print(f"⚡ STATUS: 🟢 OPERATIONAL")  # Fixed - we know it's operational if we got here
    else:
        print(f"⚠️ Command processor configuration not accessible")
        print(f"⚡ STATUS: 🔴 DEGRADED")
    
    print("🚨" + "="*60)
    print("🚨 EMERGENCY SYSTEM READY FOR WHATSAPP MESSAGES")
    print("🚨" + "="*60 + "\n")
    
    # Store system info message for @info command (no longer sent automatically)
    # This message will be sent only when user types @info
    
    SERVICES_INITIALIZED = True
except Exception as e:
    print(f"\n🚨" + "="*60)
    print(f"🚨 EMERGENCY SYSTEM INITIALIZATION FAILED")
    print(f"🚨" + "="*60)
    print(f"❌ Service initialization error: {str(e)}")
    print(f"⚠️ WhatsApp emergency triggers will not work")
    print(f"🔧 Check server configuration and restart")
    print(f"🚨" + "="*60 + "\n")
    
    # Variables already initialized above, just ensure they stay None
    SERVICES_INITIALIZED = False

@app.get("/")
async def root():
    trigger_info = {}
    if SERVICES_INITIALIZED and command_processor and hasattr(command_processor, 'valid_commands'):
        trigger_info = {
            "triggers": command_processor.valid_commands,
            "examples": [
                f"{command_processor.valid_commands[0]} → EMERGENCIA GENERAL",
                f"{command_processor.valid_commands[0]} INCENDIO → INCENDIO",
                f"{command_processor.valid_commands[0]} EMERGENCIA MÉDICA → EMERGENCIA MÉDICA"
            ]
        }
    
    return {
        "message": "WhatsApp Emergency Command System", 
        "status": "running", 
        "services_initialized": SERVICES_INITIALIZED,
        "emergency_triggers": trigger_info,
        "target_group": "TEST_ALARM (120363400467632358@g.us)",
        "deployment_version": "SOS_SYSTEM_v1.0"
    }

@app.get("/health")
async def health_check():
    trigger_status = "none_configured"
    if SERVICES_INITIALIZED and command_processor and hasattr(command_processor, 'valid_commands'):
        trigger_status = f"configured: {', '.join(command_processor.valid_commands)}"
    
    return {
        "status": "healthy" if SERVICES_INITIALIZED else "degraded",
        "services": "operational" if SERVICES_INITIALIZED else "error",
        "services_initialized": SERVICES_INITIALIZED,
        "emergency_triggers": trigger_status,
        "whatsapp_webhook": "active" if SERVICES_INITIALIZED else "inactive",
        "device_control": "available" if SERVICES_INITIALIZED else "unavailable"
    }

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    try:
        if not SERVICES_INITIALIZED:
            error_msg = "Services not initialized - check server startup logs"
            print(f"🚨 Webhook rejected: {error_msg}")
            return JSONResponse(content={"status": "error", "message": error_msg}, status_code=503)
        
        if not command_processor:
            error_msg = "Command processor not available"
            print(f"🚨 Webhook rejected: {error_msg}")
            return JSONResponse(content={"status": "error", "message": error_msg}, status_code=503)
            
        payload = await request.json()
        print(f"📨 Webhook received - processing with SOS system...")
        
        # Process the incoming WhatsApp message
        await command_processor.process_whatsapp_message(payload)
        
        return JSONResponse(content={"status": "success"}, status_code=200)
    
    except Exception as e:
        error_msg = f"Webhook processing error: {str(e)}"
        print(f"❌ {error_msg}")
        return JSONResponse(content={"status": "error", "message": error_msg}, status_code=500)

@app.get("/send-test-message")
async def send_test_message():
    """Send a test message to Waldo via the server's WHAPI connection"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        # Test different phone number formats
        formats_to_test = [
            "56940035815",                  # Just the number
            "+56940035815",                # With country code
            "56940035815@s.whatsapp.net",  # Current format
            "56940035815@c.us"             # Alternative format
        ]
        
        results = []
        
        for phone_format in formats_to_test:
            message = f"🤖 Testing format: {phone_format} - Server test message!"
            
            print(f"📤 Testing format: {phone_format}")
            print(f"📤 Message: {message}")
            
            success = await whatsapp_service.send_text_message(phone_format, message)
            
            result = {
                "phone_format": phone_format,
                "success": success,
                "message": message
            }
            results.append(result)
            
            print(f"📤 Result for {phone_format}: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
            if success:
                # If one format works, return success immediately
                return JSONResponse(content={
                    "status": "success", 
                    "message": f"Message sent successfully using format: {phone_format}",
                    "working_format": phone_format,
                    "all_results": results
                })
        
        # If no format worked, return all results for debugging
        return JSONResponse(content={
            "status": "error", 
            "message": "All phone number formats failed",
            "all_results": results,
            "note": "Check server logs for detailed WHAPI API responses"
        })
            
    except Exception as e:
        print(f"❌ Manual send error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Exception occurred: {str(e)}"
        }, status_code=500)

@app.get("/test-voice-generation")
async def test_voice_generation():
    """Test OpenAI TTS voice generation pipeline"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        if not voice_service:
            return JSONResponse(content={"status": "error", "message": "Voice service not available"}, status_code=503)
        
        # Test voice generation pipeline
        test_text = "Hola, esto es una prueba de mensaje de voz generado con OpenAI TTS para WhatsApp."
        results = await voice_service.test_voice_generation(test_text)
        
        return JSONResponse(content={
            "status": "success" if results.get("overall_success") else "error",
            "message": "Voice generation test completed",
            "results": results
        })
        
    except Exception as e:
        print(f"❌ Voice generation test error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Voice test failed: {str(e)}"
        }, status_code=500)

@app.get("/send-voice-message")
async def send_voice_message():
    """Generate and send a voice message to Waldo"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        if not voice_service or not whatsapp_service:
            return JSONResponse(content={"status": "error", "message": "Voice or WhatsApp service not available"}, status_code=503)
        
        # Generate voice message
        test_text = "Hola Waldo, este es un mensaje de voz de prueba del sistema de alarma. El sistema está funcionando correctamente."
        phone_number = "56940035815"  # Waldo's number (working format)
        
        print(f"🎤 Generating voice message for: {phone_number}")
        print(f"📝 Text: {test_text}")
        
        # Step 1: Generate voice audio file
        voice_file = await voice_service.generate_voice_message(test_text, voice="nova")
        if not voice_file:
            return JSONResponse(content={
                "status": "error",
                "message": "Failed to generate voice message",
                "step": "voice_generation"
            })
        
        print(f"✅ Voice file generated: {voice_file}")
        
        # Step 2: Test voice message sending methods
        results = []
        
        # Method 1: Base64 encoding with /messages/voice
        print(f"📤 Testing Method 1: Base64 encoding...")
        success1 = await whatsapp_service.send_voice_message(phone_number, voice_file)
        results.append({
            "method": "base64_encoding",
            "success": success1
        })
        
        if success1:
            print(f"✅ Method 1 (Base64) succeeded!")
            voice_service.cleanup_audio_file(voice_file)
            return JSONResponse(content={
                "status": "success",
                "message": "Voice message sent successfully via Base64 method",
                "phone_number": phone_number,
                "text": test_text,
                "voice_file": voice_file,
                "method_used": "base64_encoding",
                "all_results": results
            })
        
        # Method 2: File upload with /messages/voice
        print(f"📤 Testing Method 2: File upload...")
        success2 = await whatsapp_service.send_voice_message_with_file_upload(phone_number, voice_file)
        results.append({
            "method": "file_upload",
            "success": success2
        })
        
        # Cleanup
        voice_service.cleanup_audio_file(voice_file)
        
        if success2:
            return JSONResponse(content={
                "status": "success",
                "message": "Voice message sent successfully via File Upload method",
                "phone_number": phone_number,
                "text": test_text,
                "voice_file": voice_file,
                "method_used": "file_upload",
                "all_results": results
            })
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "All voice message sending methods failed",
                "phone_number": phone_number,
                "text": test_text,
                "voice_file": voice_file,
                "all_results": results,
                "note": "Check server logs for detailed WHAPI API responses"
            })
        
    except Exception as e:
        print(f"❌ Voice message sending error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Voice message test failed: {str(e)}"
        }, status_code=500)

@app.get("/voice-debug")
async def voice_debug():
    """Debug voice service configuration"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        debug_info = {
            "voice_service_available": voice_service is not None,
            "openai_api_key_configured": bool(voice_service.openai_api_key) if voice_service else False,
            "openai_api_key_preview": voice_service.openai_api_key[:20] + "..." if voice_service and voice_service.openai_api_key else "None",
            "temp_dir": voice_service.temp_dir if voice_service else "None",
            "temp_dir_exists": os.path.exists(voice_service.temp_dir) if voice_service else False,
            "available_voices": voice_service.get_available_voices() if voice_service else []
        }
        
        print(f"🔍 Voice Debug Info: {debug_info}")
        
        return JSONResponse(content={
            "status": "success",
            "debug_info": debug_info,
            "note": "Voice service configuration details"
        })
        
    except Exception as e:
        print(f"❌ Voice debug error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Voice debug failed: {str(e)}"
        }, status_code=500)

@app.get("/whapi-debug")
async def whapi_debug():
    """Debug WHAPI configuration and test basic connectivity"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        debug_info = {
            "whapi_base_url": whatsapp_service.base_url,
            "whapi_token_preview": whatsapp_service.token[:20] + "..." if whatsapp_service.token else "None",
            "processed_message_ids_count": len(whatsapp_service.processed_message_ids),
            "recent_processed_ids": list(whatsapp_service.processed_message_ids)[-5:] if whatsapp_service.processed_message_ids else []
        }
        
        print(f"🔍 WHAPI Debug Info: {debug_info}")
        
        return JSONResponse(content={
            "status": "success",
            "debug_info": debug_info,
            "note": "This shows the current WHAPI configuration on the server"
        })
        
    except Exception as e:
        print(f"❌ WHAPI debug error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Debug failed: {str(e)}"
        }, status_code=500)

@app.get("/simple-test")
async def simple_test():
    """Ultra simple test endpoint"""
    return {"message": "Simple test works!", "timestamp": "2024"}

@app.get("/test-image-endpoint")
async def test_image_endpoint():
    """Simple test to check if image endpoint works"""
    try:
        from PIL import Image
        pillow_available = True
        pillow_error = None
    except Exception as e:
        pillow_available = False
        pillow_error = str(e)
    
    return JSONResponse(content={
        "status": "success",
        "message": "Image endpoint is working!",
        "image_service_available": IMAGE_SERVICE_AVAILABLE,
        "image_service_instance": image_service is not None,
        "pillow_available": pillow_available,
        "pillow_error": pillow_error,
        "services_initialized": SERVICES_INITIALIZED
    })

@app.get("/send-emergency-alert-image")
async def send_emergency_alert_image():
    """Send the emergency alert image that was created locally to Waldo"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        if not IMAGE_SERVICE_AVAILABLE or not whatsapp_service:
            return JSONResponse(content={
                "status": "error", 
                "message": "Image service not available - Pillow dependency missing",
                "image_service_available": IMAGE_SERVICE_AVAILABLE,
                "whatsapp_service_available": whatsapp_service is not None,
                "note": "Install Pillow dependency to enable image sending"
            }, status_code=503)
        
        # Use the professional emergency alert image
        local_image_path = "./emergency_alert_professional.jpg"
        phone_number = "56940035815"  # Waldo's number (working format)
        caption = "🚨 EMERGENCIA - Prueba de sistema de alarma comunitaria"
        
        print(f"📷 Sending emergency alert image to: {phone_number}")
        print(f"🏷️ Caption: {caption}")
        print(f"📂 Image: {local_image_path}")
        
        # Check if professional image exists, fallback to test image
        if not os.path.exists(local_image_path):
            fallback_path = "./emergency_alert_test.jpg"
            if os.path.exists(fallback_path):
                print(f"⚠️ Professional image not found, using fallback: {fallback_path}")
                local_image_path = fallback_path
            else:
                return JSONResponse(content={
                    "status": "error",
                    "message": f"No emergency alert image found. Tried: {local_image_path}, {fallback_path}",
                    "note": "Please upload emergency_alert_professional.jpg or the system will create a test image"
                })
        
        # Step 1: Process image for WhatsApp
        processed_image = image_service.process_image_for_whatsapp(local_image_path, convert_to_webp=True)
        if not processed_image:
            return JSONResponse(content={
                "status": "error",
                "message": "Failed to process emergency alert image",
                "step": "image_processing"
            })
        
        print(f"✅ Image processed: {processed_image}")
        
        # Step 2: Send image via WhatsApp (try n8n-style first)
        print(f"📤 Sending via n8n-style method...")
        success = await whatsapp_service.send_image_message_n8n_style(phone_number, processed_image, caption)
        method_used = "n8n_style_binary"
        
        if not success:
            print(f"📤 n8n-style failed, trying base64...")
            success = await whatsapp_service.send_image_message(phone_number, processed_image, caption)
            method_used = "base64_json"
            
        if not success:
            print(f"📤 Base64 failed, trying multipart...")
            success = await whatsapp_service.send_image_message_via_media_endpoint(phone_number, processed_image, caption)
            method_used = "multipart_form"
        
        # Step 3: Cleanup
        if processed_image != local_image_path:
            image_service.cleanup_image_file(processed_image)
        
        if success:
            return JSONResponse(content={
                "status": "success",
                "message": "Emergency alert image sent successfully!",
                "phone_number": phone_number,
                "caption": caption,
                "method_used": method_used,
                "original_image": local_image_path,
                "processed_image": processed_image
            })
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "All image sending methods failed",
                "phone_number": phone_number,
                "methods_tried": ["n8n_style_binary", "base64_json", "multipart_form"],
                "note": "Check server logs for detailed WHAPI API responses"
            })
        
    except Exception as e:
        print(f"❌ Emergency alert image sending error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Emergency alert failed: {str(e)}"
        }, status_code=500)

@app.get("/send-animated-siren")
async def send_animated_siren():
    """Send animated siren GIF to Waldo"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        if not whatsapp_service:
            return JSONResponse(content={"status": "error", "message": "WhatsApp service not available"}, status_code=503)
        
        # Create animated siren if it doesn't exist
        gif_path = "./animated_emergency_siren.gif"
        
        if not os.path.exists(gif_path):
            try:
                from create_animated_siren import create_animated_siren_gif
                create_animated_siren_gif()
                print(f"✅ Created animated siren GIF: {gif_path}")
            except Exception as e:
                return JSONResponse(content={
                    "status": "error",
                    "message": f"Failed to create animated siren: {str(e)}"
                })
        
        phone_number = "56940035815"  # Waldo's number
        caption = "🚨 ALERTA ANIMADA - Sistema de emergencia activado 🚨"
        
        print(f"🎬 Sending animated siren GIF to: {phone_number}")
        print(f"🏷️ Caption: {caption}")
        print(f"📂 GIF: {gif_path}")
        
        # Send GIF via WhatsApp
        success = await whatsapp_service.send_gif_message(phone_number, gif_path, caption)
        
        if success:
            return JSONResponse(content={
                "status": "success",
                "message": "Animated siren GIF sent successfully!",
                "phone_number": phone_number,
                "caption": caption,
                "gif_file": gif_path,
                "type": "animated_gif"
            })
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "Failed to send animated siren GIF",
                "phone_number": phone_number,
                "gif_file": gif_path,
                "note": "Check server logs for detailed WHAPI API responses"
            })
        
    except Exception as e:
        print(f"❌ Animated siren sending error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Animated siren failed: {str(e)}"
        }, status_code=500)

@app.post("/send-image-from-file")
async def send_image_from_file(request: Request):
    """Send image from uploaded file or local path"""
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
        
        if not image_service or not whatsapp_service:
            return JSONResponse(content={"status": "error", "message": "Image or WhatsApp service not available"}, status_code=503)
        
        payload = await request.json()
        local_image_path = payload.get("image_path", "")
        phone_number = payload.get("phone_number", "56940035815")  # Default to Waldo
        caption = payload.get("caption", "🚨 EMERGENCIA - Alerta del sistema")
        convert_to_webp = payload.get("convert_to_webp", True)
        
        if not local_image_path:
            return JSONResponse(content={
                "status": "error",
                "message": "image_path is required",
                "example": {
                    "image_path": "/path/to/emergency-alert.jpg",
                    "phone_number": "56940035815",
                    "caption": "🚨 Emergency alert",
                    "convert_to_webp": True
                }
            })
        
        print(f"📷 Sending image from file: {local_image_path}")
        print(f"📱 To: {phone_number}")
        print(f"🏷️ Caption: {caption}")
        print(f"🔄 Convert to WebP: {convert_to_webp}")
        
        # Step 1: Process image for WhatsApp
        processed_image = image_service.process_image_for_whatsapp(local_image_path, convert_to_webp)
        if not processed_image:
            return JSONResponse(content={
                "status": "error",
                "message": "Failed to process image for WhatsApp",
                "step": "image_processing"
            })
        
        print(f"✅ Image processed: {processed_image}")
        
        # Step 2: Send image via WhatsApp (try multiple methods)
        print(f"📤 Trying multiple sending methods...")
        
        # Try n8n-style method first (most likely to work based on user's example)
        success = await whatsapp_service.send_image_message_n8n_style(phone_number, processed_image, caption)
        method_used = "n8n_style_binary"
        
        if not success:
            print(f"📤 n8n-style failed, trying base64 method...")
            success = await whatsapp_service.send_image_message(phone_number, processed_image, caption)
            method_used = "base64_json"
            
        if not success:
            print(f"📤 Base64 failed, trying multipart method...")
            success = await whatsapp_service.send_image_message_via_media_endpoint(phone_number, processed_image, caption)
            method_used = "multipart_form"
        
        # Step 3: Cleanup processed image if it's different from original
        if processed_image != local_image_path:
            image_service.cleanup_image_file(processed_image)
        
        if success:
            return JSONResponse(content={
                "status": "success",
                "message": "Image message sent successfully",
                "phone_number": phone_number,
                "caption": caption,
                "original_image": local_image_path,
                "processed_image": processed_image,
                "converted_to_webp": convert_to_webp,
                "method_used": method_used
            })
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "All image sending methods failed",
                "phone_number": phone_number,
                "processed_image": processed_image,
                "methods_tried": ["n8n_style_binary", "base64_json", "multipart_form"],
                "note": "Check server logs for detailed WHAPI API responses"
            })
        
    except Exception as e:
        print(f"❌ Image sending error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Image sending failed: {str(e)}"
        }, status_code=500)

@app.post("/device-register")
async def device_register(request: Request):
    try:
        payload = await request.json()
        device_id = payload.get("device_id", "unknown")
        ip = request.client.host
        
        print(f"Device registered: {device_id} from IP {ip}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Device registration successful",
            "device_id": device_id,
            "ip": ip
        })
    
    except Exception as e:
        print(f"Device registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )