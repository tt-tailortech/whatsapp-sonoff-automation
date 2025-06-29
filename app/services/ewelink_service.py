import time
import hashlib
import hmac
import base64
import json
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.models import EWeLinkDevice, DeviceStatus
from app.services.ewelink_oauth_simulator import EWeLinkOAuthSimulator
from app.services.ewelink_workaround import EWeLinkWorkaround

class EWeLinkService:
    def __init__(self):
        self.app_id = settings.ewelink_app_id
        self.app_secret = settings.ewelink_app_secret
        self.base_url = settings.ewelink_base_url
        self.email = settings.ewelink_email
        self.password = settings.ewelink_password
        self.access_token = settings.ewelink_access_token or None
        self.user_id = None
        self._auth_attempted = False
        
        # If we have a pre-configured token, we're authenticated
        if self.access_token:
            print(f"🔐 Using pre-configured access token: {self.access_token[:20]}...")
        
        # Initialize OAuth simulator for OAuth 2.0 apps
        self.oauth_simulator = EWeLinkOAuthSimulator(
            app_id=self.app_id,
            app_secret=self.app_secret,
            email=self.email,
            password=self.password
        )
        
        # Initialize workaround service
        self.workaround = EWeLinkWorkaround(
            app_id=self.app_id,
            app_secret=self.app_secret,
            email=self.email,
            password=self.password
        )
    
    def _generate_signature(self, payload: dict) -> str:
        """Generate signature for eWeLink API authentication"""
        # Sign the JSON payload, not timestamp-based string
        json_payload = json.dumps(payload, separators=(',', ':')).encode()
        
        print(f"🔐 Signing JSON: {json_payload.decode()}")
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
            "Content-Type": "application/json",
            "X-CK-Appid": self.app_id,
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif payload:
            # For login requests, generate signature from JSON payload
            signature = self._generate_signature(payload)
            headers["Authorization"] = f"Sign {signature}"
        
        return headers
    
    async def authenticate_oauth(self, email: str, password: str) -> bool:
        """
        Authenticate with eWeLink API using OAuth2.0 flow
        For Standard Role OAuth2.0 apps, we need to simulate the authorization flow
        """
        try:
            print("🔐 Starting OAuth2.0 authentication flow...")
            print(f"🔐 Using App ID: {self.app_id}")
            print(f"🔐 Using App Secret: {self.app_secret[:10]}...")
            
            # Step 1: Try to get authorization via login simulation
            # For Standard Role apps, we can try direct token exchange
            url = f"{self.base_url}/v2/user/oauth/token"
            
            # Try different OAuth approaches for Standard Role
            approaches = [
                # Approach 1: Authorization code flow simulation
                {
                    "clientId": self.app_id,
                    "clientSecret": self.app_secret,
                    "grantType": "authorization_code",
                    "code": "dummy_code",  # This will fail but shows the expected format
                    "redirectUrl": "http://localhost:3000/callback"
                },
                # Approach 2: Direct credentials (some OAuth implementations support this)
                {
                    "clientId": self.app_id,
                    "clientSecret": self.app_secret,
                    "grantType": "password",
                    "username": email,
                    "password": password
                },
                # Approach 3: eWeLink specific format
                {
                    "clientId": self.app_id,
                    "clientSecret": self.app_secret,
                    "email": email,
                    "password": password,
                    "grantType": "password"
                }
            ]
            
            for i, payload in enumerate(approaches, 1):
                print(f"\n🔐 Trying OAuth approach {i}: {payload.get('grantType', 'unknown')}")
                
                headers = {
                    "Content-Type": "application/json",
                    "X-CK-Appid": self.app_id,
                }
                
                print(f"🔐 OAuth endpoint: {url}")
                print(f"🔐 OAuth payload keys: {list(payload.keys())}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    print(f"🔐 Response status: {response.status_code}")
                    print(f"🔐 Response text: {response.text}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            token_data = data.get("data", {})
                            self.access_token = token_data.get("accessToken") or token_data.get("access_token")
                            self.user_id = token_data.get("user", {}).get("userId") or token_data.get("userId")
                            
                            print("✅ eWeLink OAuth authentication successful")
                            print(f"🔐 Access token received: {self.access_token[:20]}..." if self.access_token else "No token")
                            print(f"🔐 User ID: {self.user_id}")
                            return True
                        else:
                            print(f"❌ eWeLink OAuth error: {data.get('msg', 'Unknown error')}")
                            # Continue to next approach
                    else:
                        print(f"❌ eWeLink OAuth failed: {response.status_code} - {response.text}")
                        # Continue to next approach
            
            return False
                    
        except Exception as e:
            print(f"❌ eWeLink OAuth authentication error: {str(e)}")
            return False

    async def authenticate(self, email: str, password: str) -> bool:
        """
        Main authentication method - tries multiple approaches for OAuth 2.0 apps
        """
        # Try workaround service first
        print("🔐 Trying authentication workarounds...")
        workaround_success = await self.workaround.authenticate()
        
        if workaround_success:
            self.access_token = self.workaround.access_token
            self.base_url = self.workaround.base_url or self.base_url
            print("✅ Authentication successful via workaround")
            return True
        
        # Try OAuth simulator
        print("🔐 Trying OAuth simulator...")
        auth_success = await self.oauth_simulator.authenticate()
        
        if auth_success:
            self.access_token = self.oauth_simulator.get_access_token()
            print("✅ Authentication successful via OAuth simulator")
            return True
        
        # Try legacy methods as fallback
        print("🔄 All OAuth methods failed, trying legacy approaches...")
        
        # Try OAuth2.0 flow
        oauth_success = await self.authenticate_oauth(email, password)
        if oauth_success:
            return True
        
        # Try direct login as last resort
        print("🔄 OAuth failed, falling back to direct login...")
        return await self.authenticate_direct_login(email, password)

    async def authenticate_direct_login(self, email: str, password: str) -> bool:
        """
        Direct login authentication (for non-OAuth apps)
        Try different regions and payload formats
        """
        try:
            # Try different regions
            regions = [
                "https://us-apia.coolkit.cc",
                "https://eu-apia.coolkit.cc", 
                "https://as-apia.coolkit.cc"
            ]
            
            # Try different payload formats
            payloads = [
                {
                    "email": email,
                    "password": password,
                    "countryCode": "+1"
                },
                {
                    "email": email,
                    "password": password
                }
            ]
            
            for region in regions:
                for payload in payloads:
                    print(f"\n🔐 Trying region: {region}")
                    print(f"🔐 Payload: {list(payload.keys())}")
                    
                    url = f"{region}/v2/user/login"
                    headers = self._get_auth_headers(payload)
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, headers=headers, json=payload)
                        
                        print(f"🔐 Response status: {response.status_code}")
                        print(f"🔐 Response text: {response.text}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("error") == 0:
                                self.access_token = data["data"]["at"]
                                self.user_id = data["data"]["user"]["id"]
                                self.base_url = region  # Update to working region
                                print(f"✅ eWeLink direct login successful with {region}")
                                return True
                            else:
                                print(f"❌ eWeLink auth error: {data.get('msg', 'Unknown error')}")
                                # Continue trying other combinations
                        else:
                            print(f"❌ eWeLink auth failed: {response.status_code} - {response.text}")
                            # Continue trying other combinations
            
            return False
                    
        except Exception as e:
            print(f"❌ eWeLink authentication error: {str(e)}")
            return False
    
    async def get_devices(self) -> List[EWeLinkDevice]:
        """Get list of devices from eWeLink account"""
        try:
            url = f"{self.base_url}/v2/device/thing"
            headers = self._get_auth_headers()
            
            # Don't use params - our direct tests worked without them
            print(f"🔍 Getting devices from: {url}")
            print(f"🔑 Using token: {self.access_token[:20] if self.access_token else 'None'}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                print(f"📡 Device API Response Status: {response.status_code}")
                print(f"📄 Device API Response Body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"📊 Device API Data: {data}")
                    
                    if data.get("error") == 0:
                        thing_list = data.get("data", {}).get("thingList", [])
                        print(f"📱 Raw device list: {thing_list}")
                        
                        devices = []
                        for device_data in thing_list:
                            # Extract device info from nested structure
                            item_data = device_data.get("itemData", {})
                            device = EWeLinkDevice(
                                deviceid=item_data.get("deviceid", ""),
                                name=item_data.get("name", ""),
                                type=item_data.get("productModel", ""),
                                online=item_data.get("online", False),
                                params=item_data.get("params", {})
                            )
                            devices.append(device)
                            print(f"✅ Found device: {device.name} (ID: {device.deviceid})")
                        
                        print(f"📊 Total devices parsed: {len(devices)}")
                        return devices
                    else:
                        print(f"❌ Get devices API error: {data.get('msg', 'Unknown error')}")
                        print(f"🔍 Full error response: {data}")
                        return []
                else:
                    print(f"❌ Get devices HTTP error: {response.status_code}")
                    print(f"📄 HTTP error response: {response.text}")
                    return []
                    
        except Exception as e:
            print(f"Get devices error: {str(e)}")
            return []
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we're authenticated before making API calls"""
        # First check OAuth simulator token
        if not self.access_token and self.oauth_simulator.access_token:
            self.access_token = self.oauth_simulator.get_access_token()
            
        if self.access_token:
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
                "type": 1,
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
                "type": 1,
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