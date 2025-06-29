#!/usr/bin/env python3
"""
One-time setup script to obtain OAuth token for eWeLink.
Run this locally to get the initial token, then deploy to Render.
"""

import asyncio
import webbrowser
import time
import hmac
import hashlib
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import json

# Your OAuth app credentials
APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"
REDIRECT_URL = "http://localhost:3000/callback"

# Global variables to store OAuth response
auth_code = None
auth_state = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    def do_GET(self):
        global auth_code, auth_state
        
        # Parse the callback URL
        parsed = urlparse(self.path)
        if parsed.path == '/callback':
            params = parse_qs(parsed.query)
            auth_code = params.get('code', [None])[0]
            auth_state = params.get('state', [None])[0]
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if auth_code:
                message = f"""
                <html>
                <body style="font-family: Arial; padding: 20px;">
                <h1 style="color: green;">✅ Authorization Successful!</h1>
                <p>Authorization code received. You can close this window.</p>
                <p>Code: {auth_code[:20]}...</p>
                </body>
                </html>
                """
            else:
                message = """
                <html>
                <body style="font-family: Arial; padding: 20px;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p>No authorization code received.</p>
                </body>
                </html>
                """
            
            self.wfile.write(message.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def generate_signature(app_secret: str, message: str) -> str:
    """Generate HMAC-SHA256 signature"""
    signature = hmac.new(
        app_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

def run_callback_server():
    """Run local server to receive OAuth callback"""
    server = HTTPServer(('localhost', 3000), OAuthCallbackHandler)
    server.timeout = 60  # 60 second timeout
    server.handle_request()  # Handle one request then stop

async def get_oauth_token():
    """Interactive OAuth token setup"""
    global auth_code
    
    print("🔐 eWeLink OAuth Token Setup")
    print("=" * 50)
    print(f"App ID: {APP_ID}")
    print(f"Redirect URL: {REDIRECT_URL}")
    print()
    
    # Generate OAuth URL
    timestamp = str(int(time.time() * 1000))
    nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]
    state = "manual_setup"
    
    # Create signature
    sign_str = f"{APP_ID}_{timestamp}"
    authorization = generate_signature(APP_SECRET, sign_str)
    
    # Build OAuth URL
    oauth_url = (
        f"https://c2ccdn.coolkit.cc/oauth/index.html"
        f"?clientId={APP_ID}"
        f"&seq={timestamp}"
        f"&authorization={authorization}"
        f"&redirectUrl={REDIRECT_URL}"
        f"&state={state}"
        f"&nonce={nonce}"
    )
    
    print("📌 Steps to get OAuth token:")
    print("1. A browser window will open with the eWeLink login page")
    print("2. Log in with your eWeLink credentials")
    print("3. Authorize the app when prompted")
    print("4. You'll be redirected back to this script")
    print()
    
    # Start callback server in a thread
    server_thread = threading.Thread(target=run_callback_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open browser
    print(f"🌐 Opening browser to: {oauth_url[:80]}...")
    webbrowser.open(oauth_url)
    
    # Wait for callback
    print("⏳ Waiting for authorization (60 seconds timeout)...")
    server_thread.join(timeout=60)
    
    if auth_code:
        print(f"\n✅ Authorization code received: {auth_code[:20]}...")
        
        # Exchange code for token
        import httpx
        async with httpx.AsyncClient() as client:
            token_payload = {
                "clientId": APP_ID,
                "clientSecret": APP_SECRET,
                "grantType": "authorization_code",
                "code": auth_code,
                "redirectUrl": REDIRECT_URL
            }
            
            response = await client.post(
                "https://us-apia.coolkit.cc/v2/user/oauth/token",
                json=token_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    token_data = data.get("data", {})
                    access_token = token_data.get("accessToken")
                    refresh_token = token_data.get("refreshToken")
                    
                    print("\n🎉 Token exchange successful!")
                    print(f"Access Token: {access_token[:30]}...")
                    print(f"Refresh Token: {refresh_token[:30] if refresh_token else 'None'}...")
                    
                    # Save to file
                    token_file = {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_at": str(int(time.time()) + 30*24*60*60),  # 30 days
                        "user_info": token_data.get("user", {})
                    }
                    
                    with open("ewelink_tokens.json", "w") as f:
                        json.dump(token_file, f, indent=2)
                    
                    print("\n💾 Tokens saved to ewelink_tokens.json")
                    print("\n📋 Next steps:")
                    print("1. Copy the tokens to your Render environment")
                    print("2. Or set these environment variables:")
                    print(f"   EWELINK_ACCESS_TOKEN={access_token}")
                    print(f"   EWELINK_REFRESH_TOKEN={refresh_token}")
                    
                    return True
                else:
                    print(f"\n❌ Token exchange failed: {data.get('msg', 'Unknown error')}")
            else:
                print(f"\n❌ Token exchange HTTP error: {response.status_code}")
                print(f"Response: {response.text}")
    else:
        print("\n❌ No authorization code received")
    
    return False

if __name__ == "__main__":
    print("Starting eWeLink OAuth setup...")
    try:
        success = asyncio.run(get_oauth_token())
        if not success:
            print("\n⚠️ Setup failed. Please try again.")
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()