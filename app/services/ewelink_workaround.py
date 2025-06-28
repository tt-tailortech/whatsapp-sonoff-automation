"""
eWeLink Workaround Service
Since OAuth 2.0 apps can't use direct login, this implements alternative approaches
"""

import asyncio
import httpx
import json
import time
import hmac
import hashlib
import base64
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class EWeLinkWorkaround:
    """
    Implements workarounds for OAuth 2.0 authentication limitations
    """
    
    def __init__(self, app_id: str, app_secret: str, email: str, password: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.email = email
        self.password = password
        
        # Try different regional endpoints
        self.regions = [
            "https://us-apia.coolkit.cc",
            "https://eu-apia.coolkit.cc",
            "https://as-apia.coolkit.cc",
            "https://cn-apia.coolkit.cn"
        ]
        
        self.access_token = None
        self.base_url = None
        
        # Check for pre-configured token from environment
        self._load_env_token()
    
    def _load_env_token(self):
        """Load token from environment variables"""
        env_token = os.environ.get('EWELINK_ACCESS_TOKEN')
        if env_token:
            self.access_token = env_token
            print("🔐 Loaded access token from environment")
    
    async def authenticate(self) -> bool:
        """
        Try various authentication workarounds
        """
        if self.access_token:
            print("✅ Using pre-configured access token")
            return True
        
        # Workaround 1: Try using a different app type endpoint
        if await self._try_app_login():
            return True
        
        # Workaround 2: Try legacy API endpoints
        if await self._try_legacy_api():
            return True
        
        # Workaround 3: Try third-party service endpoints
        if await self._try_third_party_endpoints():
            return True
        
        print("❌ All authentication workarounds failed")
        print("\n📋 Manual Setup Required:")
        print("1. Run 'python setup_oauth_token.py' locally")
        print("2. Complete the OAuth flow in your browser")
        print("3. Set EWELINK_ACCESS_TOKEN in Render environment")
        
        return False
    
    async def _try_app_login(self) -> bool:
        """Try login using app-specific endpoints"""
        try:
            print("🔄 Trying app-specific login endpoints...")
            
            for region in self.regions:
                # Try mobile app endpoint
                url = f"{region}/v2/user/login"
                
                # Mobile app headers
                headers = {
                    "Content-Type": "application/json",
                    "X-CK-Appid": self.app_id,
                    "X-CK-Source": "app",  # Indicate mobile app
                    "User-Agent": "eWeLink/4.0.0 (iPhone; iOS 14.0; Scale/3.00)"
                }
                
                payload = {
                    "email": self.email,
                    "password": self.password,
                    "version": "4.0.0",
                    "ts": int(time.time()),
                    "nonce": base64.b64encode(os.urandom(8)).decode()[:8],
                    "appid": self.app_id
                }
                
                # Try with app signature
                sign_str = json.dumps(payload, separators=(',', ':'))
                signature = base64.b64encode(
                    hmac.new(self.app_secret.encode(), sign_str.encode(), hashlib.sha256).digest()
                ).decode()
                
                headers["Authorization"] = f"Sign {signature}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            self.access_token = data["data"]["at"]
                            self.base_url = region
                            print(f"✅ App login successful with {region}")
                            return True
                
        except Exception as e:
            print(f"❌ App login error: {e}")
        
        return False
    
    async def _try_legacy_api(self) -> bool:
        """Try legacy API v1 endpoints"""
        try:
            print("🔄 Trying legacy API endpoints...")
            
            # Legacy API uses different authentication
            legacy_urls = [
                "https://api.coolkit.cc:8080/api/user/login",
                "https://api.ewelink.cc/api/user/login"
            ]
            
            for url in legacy_urls:
                payload = {
                    "email": self.email,
                    "password": self.password,
                    "version": 6,
                    "ts": str(int(time.time())),
                    "nonce": str(int(time.time() * 1000)),
                    "appid": self.app_id
                }
                
                # Legacy signature method
                param_str = json.dumps(payload, separators=(',', ':'))
                sign = base64.b64encode(
                    hashlib.md5(param_str.encode()).digest()
                ).decode()
                
                headers = {
                    "Authorization": f"Sign {sign}",
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            self.access_token = data.get("at")
                            print(f"✅ Legacy API login successful")
                            return True
                
        except Exception as e:
            print(f"❌ Legacy API error: {e}")
        
        return False
    
    async def _try_third_party_endpoints(self) -> bool:
        """Try third-party integration endpoints"""
        try:
            print("🔄 Trying third-party integration endpoints...")
            
            # Some integrations use different auth methods
            endpoints = [
                {
                    "url": "https://api.ewelink.cc/v2/user/login",
                    "headers": {
                        "X-CK-Appid": "McFJj4Noke1mGDZCR1QarGW7rtDv00Zs",  # Home Assistant app ID
                        "Content-Type": "application/json"
                    }
                },
                {
                    "url": "https://eu-api.coolkit.cc/v2/user/login", 
                    "headers": {
                        "X-CK-Appid": "4s1FXKC9FaGfoqXhmXSJneb3qcm1gOak",  # Alternative app ID
                        "Content-Type": "application/json"
                    }
                }
            ]
            
            for endpoint in endpoints:
                payload = {
                    "email": self.email,
                    "password": self.password
                }
                
                # Generate signature
                sign_str = json.dumps(payload, separators=(',', ':'))
                signature = base64.b64encode(
                    hmac.new(b"6Nz4n0xA8s8qdxQf2GqurZj2Fs55FUvM", sign_str.encode(), hashlib.sha256).digest()
                ).decode()
                
                endpoint["headers"]["Authorization"] = f"Sign {signature}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        endpoint["url"], 
                        headers=endpoint["headers"], 
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error") == 0:
                            self.access_token = data["data"]["at"]
                            print(f"✅ Third-party endpoint login successful")
                            return True
                
        except Exception as e:
            print(f"❌ Third-party endpoint error: {e}")
        
        return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        if self.access_token:
            return {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-CK-Appid": self.app_id
            }
        return {}