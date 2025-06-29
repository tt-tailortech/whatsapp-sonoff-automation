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
    # from app.services.voice_service import VoiceService  # Removed
    from app.services.ewelink_service import EWeLinkService
    from app.services.command_processor import CommandProcessor

    # Create temp audio directory
    os.makedirs(settings.temp_audio_dir, exist_ok=True)

    # Initialize services
    whatsapp_service = WhatsAppService()
    # voice_service = VoiceService()  # Removed
    ewelink_service = EWeLinkService()
    command_processor = CommandProcessor(whatsapp_service, ewelink_service)
    
    SERVICES_INITIALIZED = True
except Exception as e:
    print(f"Service initialization error: {str(e)}")
    SERVICES_INITIALIZED = False
    whatsapp_service = None
    # voice_service = None  # Removed
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
        
        # Waldo's number from the logs
        phone_number = "56940035815@s.whatsapp.net"
        message = "🤖 Manual test message from alarm system server! This message was sent via the /send-test-message endpoint."
        
        print(f"📤 Manual send request to {phone_number}")
        print(f"📤 Message: {message}")
        
        success = await whatsapp_service.send_text_message(phone_number, message)
        
        if success:
            return JSONResponse(content={
                "status": "success", 
                "message": "Message sent to Waldo successfully!",
                "to": phone_number,
                "text": message
            })
        else:
            return JSONResponse(content={
                "status": "error", 
                "message": "Failed to send message to Waldo",
                "to": phone_number
            })
            
    except Exception as e:
        print(f"❌ Manual send error: {str(e)}")
        return JSONResponse(content={
            "status": "error", 
            "message": f"Exception occurred: {str(e)}"
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