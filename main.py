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

# Initialize services with error handling
try:
    from app.config import settings
    from app.models import WhatsAppWebhookPayload
    from app.services.whatsapp_service import WhatsAppService
    from app.services.voice_service import VoiceService  # Re-enabled with OpenAI only
    from app.services.ewelink_service import EWeLinkService
    from app.services.command_processor import CommandProcessor

    # Create temp audio directory
    os.makedirs(settings.temp_audio_dir, exist_ok=True)

    # Initialize services
    whatsapp_service = WhatsAppService()
    voice_service = VoiceService()  # Re-enabled
    ewelink_service = EWeLinkService()
    command_processor = CommandProcessor(whatsapp_service, ewelink_service)
    
    SERVICES_INITIALIZED = True
except Exception as e:
    print(f"Service initialization error: {str(e)}")
    SERVICES_INITIALIZED = False
    whatsapp_service = None
    voice_service = None  # Re-enabled
    ewelink_service = None
    command_processor = None

@app.get("/")
async def root():
    return {"message": "WhatsApp-Sonoff TEST Automation System", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if SERVICES_INITIALIZED else "degraded",
        "services": "operational" if SERVICES_INITIALIZED else "error",
        "services_initialized": SERVICES_INITIALIZED
    }

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    try:
        if not SERVICES_INITIALIZED:
            return JSONResponse(content={"status": "error", "message": "Services not initialized"}, status_code=503)
            
        payload = await request.json()
        
        # Process the incoming WhatsApp message
        await command_processor.process_whatsapp_message(payload)
        
        return JSONResponse(content={"status": "success"}, status_code=200)
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

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