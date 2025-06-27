import time
import hashlib
import hmac
import base64
import json
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.models import EWeLinkDevice, DeviceStatus

class EWeLinkService:
    def __init__(self):
        self.app_id = settings.ewelink_app_id
        self.app_secret = settings.ewelink_app_secret
        self.base_url = settings.ewelink_base_url
        self.email = settings.ewelink_email
        self.password = settings.ewelink_password
        self.access_token = None
        self.user_id = None
        self._auth_attempted = False
    
    def _generate_signature(self, payload: dict) -> str:
        """Generate signature for eWeLink API authentication"""
        # Convert payload to compact JSON string (no spaces)
        import json
        json_payload = json.dumps(payload, separators=(',', ':')).encode()
        
        print(f"🔐 Signing JSON: {json_payload}")
        print(f"🔐 Using secret: {self.app_secret[:10]}...")
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.app_secret.encode(),
            json_payload,
            hashlib.sha256
        ).digest()
        
        result = base64.b64encode(signature).decode()
        print(f"🔐 Generated signature: {result}")
        return result
    
    def _get_auth_headers(self, payload: dict = None) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        headers = {
            "X-CK-Appid": self.app_id,
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            headers["Content-Type"] = "application/json"
        elif payload:
            # For login requests, generate signature from payload
            signature = self._generate_signature(payload)
            headers["Authorization"] = f"Sign {signature}"
        
        return headers
    
    async def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with eWeLink API using email and password
        Note: For production, consider using app-based authentication
        """
        try:
            # Try different regional endpoints
            endpoints_to_try = [
                f"{self.base_url}/v2/user/login",  # EU
                "https://cn-apia.coolkit.cc/v2/user/login",  # CN
                "https://as-apia.coolkit.cc/v2/user/login",  # AS  
                "https://us-apia.coolkit.cc/v2/user/login",  # US
            ]
            
            # Try payload without countryCode first
            payload = {
                "email": email,
                "password": password
            }
            
            # Try each endpoint until one works
            for url in endpoints_to_try:
                print(f"\n🔐 Trying endpoint: {url}")
                
                # Get headers with signature for login
                headers = self._get_auth_headers(payload)
                
                print(f"🔐 Login request headers: {headers}")
                print(f"🔐 Login payload: {payload}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    print(f"🔐 Response status: {response.status_code}")
                    print(f"🔐 Response text: {response.text}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            self.access_token = data["data"]["at"]
                            self.user_id = data["data"]["user"]["id"]
                            print("✅ eWeLink authentication successful")
                            return True
                        else:
                            error_msg = data.get('msg', 'Unknown error')
                            print(f"❌ eWeLink auth error: {error_msg}")
                            # Continue to next endpoint
                    else:
                        print(f"❌ eWeLink auth failed: {response.status_code} - {response.text}")
                        # Continue to next endpoint
            
            print("❌ All endpoints failed")
            return False
                    
        except Exception as e:
            print(f"❌ eWeLink authentication error: {str(e)}")
            return False
    
    async def get_devices(self) -> List[EWeLinkDevice]:
        """Get list of devices from eWeLink account"""
        try:
            url = f"{self.base_url}/v2/device/thing"
            headers = self._get_auth_headers()
            
            params = {
                "lang": "en",
                "num": 30,
                "beginIndex": 0
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        devices = []
                        for device_data in data.get("data", {}).get("thingList", []):
                            device = EWeLinkDevice(
                                deviceid=device_data.get("deviceid", ""),
                                name=device_data.get("name", ""),
                                type=device_data.get("productModel", ""),
                                online=device_data.get("online", False),
                                params=device_data.get("params", {})
                            )
                            devices.append(device)
                        return devices
                    else:
                        print(f"Get devices error: {data.get('msg', 'Unknown error')}")
                        return []
                else:
                    print(f"Get devices failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            print(f"Get devices error: {str(e)}")
            return []
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we're authenticated before making API calls"""
        if self.access_token and self.user_id:
            return True
            
        if self._auth_attempted:
            return False
            
        # Attempt authentication with user credentials
        if self.email and self.password:
            print(f"🔐 Attempting eWeLink authentication for {self.email}")
            success = await self.authenticate(self.email, self.password)
            self._auth_attempted = True
            return success
        else:
            print("⚠️ eWeLink email/password not configured - device control disabled")
            self._auth_attempted = True
            return False

    async def control_device(self, device_id: str, command: str) -> bool:
        """
        Control a Sonoff device
        Commands: ON, OFF, BLINK
        """
        try:
            if not await self._ensure_authenticated():
                print(f"❌ eWeLink not authenticated - cannot control device {device_id}")
                return False
            url = f"{self.base_url}/v2/device/thing/status"
            headers = self._get_auth_headers()
            
            # Map commands to device parameters
            params = {}
            if command == "ON":
                params = {"switch": "on"}
            elif command == "OFF":
                params = {"switch": "off"}
            elif command == "BLINK":
                # For blink, we'll turn on, wait, then off (handled by device firmware)
                # Some devices support pulse mode
                params = {"pulse": "on", "pulseWidth": 1000}  # 1 second pulse
                # Fallback to regular switch if pulse not supported
                if not params:
                    params = {"switch": "on"}
            
            payload = {
                "type": "1",
                "id": device_id,
                "params": params
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        print(f"Device {device_id} command {command} successful")
                        return True
                    else:
                        print(f"Device control error: {data.get('msg', 'Unknown error')}")
                        return False
                else:
                    print(f"Device control failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Device control error: {str(e)}")
            return False
    
    async def get_device_status(self, device_id: str) -> Optional[DeviceStatus]:
        """Get current status of a specific device"""
        try:
            url = f"{self.base_url}/v2/device/thing/status"
            headers = self._get_auth_headers()
            
            params = {
                "type": "1",
                "id": device_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        device_data = data.get("data", {})
                        params = device_data.get("params", {})
                        
                        return DeviceStatus(
                            device_id=device_id,
                            online=device_data.get("online", False),
                            switch_state=params.get("switch", "unknown"),
                            last_update=device_data.get("lastUpdateTime")
                        )
                    else:
                        print(f"Get device status error: {data.get('msg', 'Unknown error')}")
                        return None
                else:
                    print(f"Get device status failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Get device status error: {str(e)}")
            return None
    
    async def find_device_by_name(self, device_name: str) -> Optional[str]:
        """Find device ID by device name"""
        try:
            devices = await self.get_devices()
            for device in devices:
                if device.name.lower() == device_name.lower():
                    return device.deviceid
            return None
        except Exception as e:
            print(f"Find device by name error: {str(e)}")
            return None