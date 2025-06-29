#!/usr/bin/env python3
"""
OAuth Setup Helper for eWeLink
Run this once to get your refresh token for automation
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

def setup_oauth():
    """Guide user through OAuth setup"""
    
    app_id = os.getenv('EWELINK_APP_ID')
    redirect_url = "http://localhost:3000/callback"  # From your app config
    
    print("🔐 eWeLink OAuth2.0 Setup")
    print("=" * 50)
    print()
    print("Your OAuth app requires manual authorization. Follow these steps:")
    print()
    # Calculate authorization signature according to documentation
    import time
    import hmac
    import hashlib
    import base64
    
    seq = str(int(time.time() * 1000))  # milliseconds timestamp
    nonce = "zt123456"  # 8-char alphanumeric
    app_secret = os.getenv('EWELINK_APP_SECRET')
    
    # Sign according to docs: {clientId}_{seq}
    message = f"{app_id}_{seq}"
    signature = base64.b64encode(
        hmac.new(app_secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    
    auth_url = f"https://c2ccdn.coolkit.cc/oauth/index.html?state=10011&clientId={app_id}&authorization={signature}&seq={seq}&redirectUrl={redirect_url}&nonce={nonce}&grantType=authorization_code&showQRCode=false"
    
    print("1. 📱 Open this URL in your browser:")
    print(f"   {auth_url}")
    print()
    print("2. 🔑 Log in with your eWeLink account:")
    print(f"   Email: tt.tailortech@gmail.com")
    print(f"   Password: Qwerty.2025")
    print()
    print("3. ✅ Authorize your app")
    print()
    print("4. 📋 Copy the 'code' parameter from the redirect URL")
    print(f"   (You'll be redirected to: {redirect_url}?code=AUTHORIZATION_CODE)")
    print()
    print("5. 🔄 Run this script again with the code:")
    print("   python oauth_setup.py YOUR_AUTHORIZATION_CODE")
    print()
    
    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(f"📥 Received authorization code: {code}")
        print()
        print("🔄 Now exchanging code for access token...")
        
        # Import and use our eWeLink service to exchange code for token
        sys.path.insert(0, os.path.dirname(__file__))
        from app.services.ewelink_service import EWeLinkService
        import asyncio
        
        async def exchange_code():
            service = EWeLinkService()
            
            # Exchange code for token - use US region since that's where auth happened
            url = "https://us-apia.coolkit.cc/v2/user/oauth/token"
            
            payload = {
                "code": code,
                "redirectUrl": redirect_url,
                "grantType": "authorization_code"
            }
            
            # Generate signature for token exchange (sign the JSON payload)
            import json
            json_payload = json.dumps(payload, separators=(',', ':'))
            signature = base64.b64encode(
                hmac.new(app_secret.encode(), json_payload.encode(), hashlib.sha256).digest()
            ).decode()
            
            headers = {
                "Content-Type": "application/json",
                "X-CK-Appid": service.app_id,
                "Authorization": f"Sign {signature}"
            }
            
            print(f"🔐 Token exchange endpoint: {url}")
            print(f"🔐 Payload: {payload}")
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"🔐 Response status: {response.status_code}")
                print(f"🔐 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        access_token = data["data"]["access_token"]
                        refresh_token = data["data"].get("refresh_token")
                        
                        print("✅ SUCCESS! OAuth tokens received:")
                        print(f"🎫 Access Token: {access_token}")
                        print(f"🔄 Refresh Token: {refresh_token}")
                        print()
                        print("📝 Add these to your .env file:")
                        print(f"EWELINK_ACCESS_TOKEN={access_token}")
                        if refresh_token:
                            print(f"EWELINK_REFRESH_TOKEN={refresh_token}")
                        
                        return True
                    else:
                        print(f"❌ Error: {data.get('msg', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
                    return False
        
        asyncio.run(exchange_code())
    else:
        print("💡 Once you have the authorization code, run:")
        print("   python oauth_setup.py YOUR_CODE_HERE")

if __name__ == "__main__":
    setup_oauth()