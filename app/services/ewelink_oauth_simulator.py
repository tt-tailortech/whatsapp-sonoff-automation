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

class EWeLinkOAuthSimulator:
    """
    Simulates OAuth 2.0 flow for eWeLink by programmatically handling the authorization.
    This is necessary because OAuth 2.0 apps can't use direct login.
    """
    
    def __init__(self, app_id: str, app_secret: str, email: str, password: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.email = email
        self.password = password
        self.base_url = "https://us-apia.coolkit.cc"
        self.auth_url = "https://c2ccdn.coolkit.cc"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.user_info = None
        
        # Token persistence file
        self.token_file = "/tmp/ewelink_tokens.json"
        self._load_tokens()
    
    def _load_tokens(self):
        """Load saved tokens from file"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.token_expires_at = data.get('expires_at')
                    self.user_info = data.get('user_info')
                    print(f"🔐 Loaded saved tokens (expires: {self.token_expires_at})")
        except Exception as e:
            print(f"⚠️ Could not load saved tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to file"""
        try:
            data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.token_expires_at,
                'user_info': self.user_info
            }
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
            print(f"💾 Saved tokens to {self.token_file}")
        except Exception as e:
            print(f"⚠️ Could not save tokens: {e}")
    
    def _generate_signature(self, message: str) -> str:
        """Generate HMAC-SHA256 signature"""
        signature = hmac.new(
            self.app_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    async def _simulate_browser_auth(self) -> Optional[str]:
        """
        Simulate browser-based OAuth authorization.
        This attempts to programmatically handle the OAuth flow.
        """
        try:
            print("🌐 Simulating OAuth browser flow...")
            
            # Step 1: Generate authorization request parameters
            timestamp = str(int(time.time() * 1000))
            nonce = base64.b64encode(os.urandom(8)).decode()[:8]
            seq = timestamp
            
            # Create signature for authorization
            sign_str = f"{self.app_id}_{seq}"
            authorization = self._generate_signature(sign_str)
            
            # Build OAuth authorization URL parameters
            auth_params = {
                "clientId": self.app_id,
                "seq": seq,
                "authorization": authorization,
                "redirectUrl": "http://localhost:3000/callback",
                "state": "automated_login",
                "nonce": nonce
            }
            
            # Step 2: Try to get authorization code through API simulation
            # This attempts to bypass the browser requirement
            async with httpx.AsyncClient() as client:
                # First, try to authenticate directly with eWeLink's internal API
                login_url = f"{self.base_url}/v2/user/login"
                
                # Create a signed request that mimics what the OAuth page would do
                login_payload = {
                    "email": self.email,
                    "password": self.password,
                    "countryCode": "+1"
                }
                
                # Try to get a session/auth code
                headers = {
                    "Content-Type": "application/json",
                    "X-CK-Appid": self.app_id,
                    "Authorization": f"Sign {self._generate_signature(json.dumps(login_payload, separators=(',', ':')))}",
                    "X-CK-Source": "oauth"  # Indicate OAuth source
                }
                
                print("🔐 Attempting programmatic OAuth simulation...")
                
                # Step 3: Exchange for OAuth token
                # Since we can't get a real auth code, we'll try alternative approaches
                
                # Approach 1: Try client credentials flow
                token_payload = {
                    "clientId": self.app_id,
                    "clientSecret": self.app_secret,
                    "grantType": "client_credentials",
                    "scope": "all"
                }
                
                token_url = f"{self.base_url}/v2/user/oauth/token"
                response = await client.post(
                    token_url,
                    json=token_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        return data.get("data", {}).get("accessToken")
                
                # Approach 2: Try resource owner password credentials
                token_payload = {
                    "clientId": self.app_id,
                    "clientSecret": self.app_secret,
                    "grantType": "password",
                    "username": self.email,
                    "password": self.password,
                    "scope": "all"
                }
                
                response = await client.post(
                    token_url,
                    json=token_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        return data.get("data", {}).get("accessToken")
                
            return None
            
        except Exception as e:
            print(f"❌ OAuth simulation error: {e}")
            return None
    
    async def authenticate(self) -> bool:
        """
        Main authentication method that handles token refresh and OAuth simulation
        """
        try:
            # Check if we have valid saved tokens
            if self.access_token and self.token_expires_at:
                expires_at = datetime.fromisoformat(self.token_expires_at)
                if datetime.now() < expires_at:
                    print("✅ Using valid saved access token")
                    return True
                elif self.refresh_token:
                    print("🔄 Token expired, attempting refresh...")
                    if await self._refresh_token():
                        return True
            
            # Try OAuth simulation
            print("🔐 Starting OAuth authentication simulation...")
            access_token = await self._simulate_browser_auth()
            
            if access_token:
                self.access_token = access_token
                # Set expiration to 30 days (eWeLink default)
                self.token_expires_at = (datetime.now() + timedelta(days=30)).isoformat()
                self._save_tokens()
                print("✅ OAuth simulation successful!")
                return True
            
            # Fallback: Try using pre-authorized token if available
            # This would require manual setup once
            print("⚠️ OAuth simulation failed. Manual token setup may be required.")
            return False
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    async def _refresh_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "clientId": self.app_id,
                    "clientSecret": self.app_secret,
                    "grantType": "refresh_token",
                    "refreshToken": self.refresh_token
                }
                
                response = await client.post(
                    f"{self.base_url}/v2/user/refresh",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        token_data = data.get("data", {})
                        self.access_token = token_data.get("accessToken")
                        self.refresh_token = token_data.get("refreshToken")
                        self.token_expires_at = (datetime.now() + timedelta(days=30)).isoformat()
                        self._save_tokens()
                        print("✅ Token refreshed successfully")
                        return True
                        
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            
        return False
    
    def get_access_token(self) -> Optional[str]:
        """Get the current access token"""
        return self.access_token
    
    async def setup_manual_token(self, access_token: str, refresh_token: str = None):
        """
        Manual setup for tokens obtained through browser OAuth flow.
        This is a one-time setup that can be done manually.
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        self._save_tokens()
        print("✅ Manual token setup complete")