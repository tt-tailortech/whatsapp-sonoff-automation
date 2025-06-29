import asyncio
import websockets
import json
import time
import hmac
import hashlib
import base64
from typing import Dict, List, Optional
from app.models import EWeLinkDevice, DeviceStatus
from app.config import settings

class EWeLinkWebSocketService:
    def __init__(self):
        self.app_id = settings.ewelink_app_id
        self.app_secret = settings.ewelink_app_secret
        self.email = settings.ewelink_email
        self.password = settings.ewelink_password
        self.base_url = settings.ewelink_base_url
        
        # WebSocket connection
        self.ws = None
        self.is_connected = False
        self.sequence = 0
        
        # From your logs - this is your actual device
        self.test_device_id = "10011eafd1"
        self.api_key = "04739209-3c18-4995-8c2d-df9d002da821"
        
        # Authentication token (we'll need to get this)
        self.access_token = None
        self.ws_url = None
        
    async def authenticate(self, email: str, password: str) -> bool:
        """Authenticate and get WebSocket URL"""
        try:
            print("🔐 Authenticating with eWeLink WebSocket...")
            
            # First, get access token via REST API
            access_token = await self._get_access_token(email, password)
            if not access_token:
                return False
                
            self.access_token = access_token
            
            # Get WebSocket dispatch info
            ws_info = await self._get_websocket_info()
            if not ws_info:
                return False
                
            self.ws_url = ws_info.get('domain')
            
            # Connect to WebSocket
            await self._connect_websocket()
            
            return self.is_connected
            
        except Exception as e:
            print(f"❌ WebSocket authentication error: {e}")
            return False
    
    async def _get_access_token(self, email: str, password: str) -> Optional[str]:
        """Get access token using REST API"""
        
        import httpx
        
        timestamp = str(int(time.time() * 1000))
        nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
        
        # Login payload
        payload = {
            "email": email,
            "password": password
        }
        
        # Sign the payload
        json_str = json.dumps(payload, separators=(',', ':'))
        signature = base64.b64encode(
            hmac.new(self.app_secret.encode(), json_str.encode(), hashlib.sha256).digest()
        ).decode()
        
        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": self.app_id,
            "X-CK-Nonce": nonce,
            "X-CK-Seq": timestamp,
            "Authorization": f"Sign {signature}"
        }
        
        endpoints = [
            "https://cn-apia.coolkit.cn/v2/user/login",
            "https://us-apia.coolkit.cc/v2/user/login", 
            "https://eu-apia.coolkit.cc/v2/user/login"
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(endpoint, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            user_data = data.get("data", {})
                            access_token = user_data.get("at")
                            
                            if access_token:
                                print(f"✅ Got access token from {endpoint}")
                                return access_token
                                
            except Exception as e:
                print(f"❌ Login error for {endpoint}: {e}")
                continue
        
        return None
    
    async def _get_websocket_info(self) -> Optional[Dict]:
        """Get WebSocket connection info"""
        
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/user/websocket/dispatch",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        return data.get("data", {})
                        
        except Exception as e:
            print(f"❌ WebSocket dispatch error: {e}")
        
        return None
    
    async def _connect_websocket(self):
        """Connect to eWeLink WebSocket"""
        
        if not self.ws_url:
            print("❌ No WebSocket URL available")
            return
            
        try:
            # WebSocket URL format: wss://domain:port/api/ws
            ws_full_url = f"wss://{self.ws_url}/api/ws"
            
            print(f"🔌 Connecting to WebSocket: {ws_full_url}")
            
            self.ws = await websockets.connect(ws_full_url)
            
            # Send authentication handshake
            auth_message = {
                "action": "userOnline",
                "at": self.access_token,
                "apikey": self.api_key,
                "appid": self.app_id,
                "nonce": base64.b64encode(str(time.time()).encode()).decode()[:8],
                "ts": int(time.time()),
                "version": 8,
                "sequence": str(int(time.time() * 1000))
            }
            
            await self.ws.send(json.dumps(auth_message))
            
            # Wait for response
            response = await self.ws.recv()
            response_data = json.loads(response)
            
            if response_data.get("error") == 0:
                print("✅ WebSocket connected and authenticated")
                self.is_connected = True
                return True
            else:
                print(f"❌ WebSocket auth failed: {response_data}")
                return False
                
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
    
    async def control_device(self, device_id: str, command: str) -> bool:
        """Control device via WebSocket"""
        
        if not self.is_connected or not self.ws:
            print("❌ WebSocket not connected")
            return False
        
        try:
            # Convert command to switch state
            switch_state = "on" if command.upper() == "ON" else "off"
            
            # Control message (based on your logs)
            control_message = {
                "action": "update",
                "deviceid": device_id,
                "apikey": self.api_key,
                "userAgent": "app",
                "sequence": str(int(time.time() * 1000)),
                "params": {
                    "switch": switch_state
                }
            }
            
            print(f"📤 Sending control command: {control_message}")
            
            await self.ws.send(json.dumps(control_message))
            
            # Wait for response
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            print(f"📥 Control response: {response_data}")
            
            if response_data.get("error") == 0:
                print(f"✅ Device {device_id} control successful")
                return True
            else:
                print(f"❌ Device control failed: {response_data}")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Control command timeout")
            return False
        except Exception as e:
            print(f"❌ Control error: {e}")
            return False
    
    async def get_devices(self) -> List[EWeLinkDevice]:
        """Get device list - for now return the known device"""
        
        # Based on your logs, return the known device
        device = EWeLinkDevice(
            deviceid=self.test_device_id,
            name="SONOFF Device",
            type="switch",
            online=True,
            params={"switch": "off"}  # Default state
        )
        
        return [device]
    
    async def get_device_status(self, device_id: str) -> Optional[DeviceStatus]:
        """Get device status"""
        
        # For now, return a basic status
        return DeviceStatus(
            device_id=device_id,
            online=True,
            switch_state="unknown",
            last_update=None
        )
    
    async def find_device_by_name(self, device_name: str) -> Optional[str]:
        """Find device by name"""
        
        # Return the test device ID
        return self.test_device_id
    
    async def disconnect(self):
        """Disconnect WebSocket"""
        
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            print("🔌 WebSocket disconnected")