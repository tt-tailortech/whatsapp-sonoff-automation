import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings
from app.models import WhatsAppWebhookPayload
from app.services.whatsapp_service import WhatsAppService
from app.services.voice_service import VoiceService
from app.services.ewelink_service import EWeLinkService
from app.services.command_processor import CommandProcessor

# Create temp audio directory
os.makedirs(settings.temp_audio_dir, exist_ok=True)

app = FastAPI(
    title="WhatsApp-Sonoff Voice Automation",
    description="Voice-enabled WhatsApp automation for Sonoff device control",
    version="1.0.0"
)

# Initialize services
whatsapp_service = WhatsAppService()
voice_service = VoiceService()
ewelink_service = EWeLinkService()
command_processor = CommandProcessor(whatsapp_service, voice_service, ewelink_service)

@app.get("/")
async def root():
    return {"message": "WhatsApp-Sonoff Voice Automation System", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": "operational"}

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    try:
        payload = await request.json()
        
        # Process the incoming WhatsApp message
        await command_processor.process_whatsapp_message(payload)
        
        return JSONResponse(content={"status": "success"}, status_code=200)
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

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