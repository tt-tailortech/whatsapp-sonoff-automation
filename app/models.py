from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class WhatsAppMessage(BaseModel):
    id: str
    from_phone: str
    text: str
    contact_name: Optional[str] = None
    timestamp: datetime

class DeviceCommand(BaseModel):
    command: str
    device_id: str
    phone_number: str
    contact_name: Optional[str] = None
    message_id: str

class DeviceStatus(BaseModel):
    device_id: str
    online: bool
    switch_state: str
    last_update: Optional[datetime] = None

class VoiceResponse(BaseModel):
    success: bool
    message: str
    phone_number: str
    audio_file_path: Optional[str] = None
    duration: Optional[float] = None

class WhatsAppWebhookPayload(BaseModel):
    messages: Optional[List[Dict[str, Any]]] = None
    entry: Optional[List[Dict[str, Any]]] = None

class EWeLinkDevice(BaseModel):
    deviceid: str
    name: str
    type: str
    online: bool
    params: Dict[str, Any]