#!/usr/bin/env python3
"""
Manual token setup - get access token through browser
"""

import asyncio
import httpx
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"

def get_oauth_url():
    """Generate OAuth URL for manual browser authentication"""
    
    oauth_url = (
        f"https://cn-apia.coolkit.cn/v2/user/oauth/authorize"
        f"?clientId={APP_ID}"
        f"&response_type=code"
        f"&redirect_uri=http://localhost:3000/callback"
        f"&state=manual_setup"
    )
    
    return oauth_url

async def exchange_manual_code(auth_code: str):
    """Exchange manually obtained code for token"""
    
    print(f"🔄 Exchanging code: {auth_code}")
    
    # Try direct token exchange without signature
    payload = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET, 
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": "http://localhost:3000/callback"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "https://cn-apia.coolkit.cn/v2/user/oauth/token",
        "https://us-apia.coolkit.cc/v2/user/oauth/token", 
        "https://eu-apia.coolkit.cc/v2/user/oauth/token"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Trying: {endpoint}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                
                print(f"📡 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        access_token = data.get("data", {}).get("access_token")
                        if access_token:
                            print(f"\n🎉 SUCCESS! Access Token: {access_token}")
                            
                            # Test the token
                            await test_token(endpoint.replace("/v2/user/oauth/token", ""), access_token)
                            return access_token
                            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

async def test_token(base_url: str, token: str):
    """Test access token with device API"""
    
    print(f"\n🧪 Testing token...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/v2/device/thing", headers=headers)
            
            print(f"📡 Device API Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:
                    devices = data.get("data", {}).get("thingList", [])
                    print(f"✅ Token works! Found {len(devices)} devices")
                    
                    for device in devices:
                        print(f"  - {device.get('name', 'Unknown')} (ID: {device.get('deviceid')})")
                        
                    return True
                else:
                    print(f"❌ API Error: {data.get('msg')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    return False

def main():
    """Main setup process"""
    
    print("🔐 Manual eWeLink OAuth Setup")
    print("=" * 50)
    
    # Generate OAuth URL
    oauth_url = get_oauth_url()
    print(f"\n🌐 OAuth URL: {oauth_url}")
    
    print("\n📋 Manual Steps:")
    print("1. Opening browser to eWeLink OAuth page...")
    print("2. Login with your eWeLink credentials")
    print("3. Copy the 'code' parameter from the callback URL")
    print("4. Paste it below")
    
    try:
        webbrowser.open(oauth_url)
        print("✅ Browser opened")
    except:
        print("❌ Could not open browser automatically")
        print(f"Please manually open: {oauth_url}")
    
    print("\n⏳ Waiting for you to complete OAuth flow...")
    print("After login, you'll be redirected to a URL like:")
    print("http://localhost:3000/callback?code=XXXXXXXX&state=manual_setup")
    
    callback_url = input("\n📎 Paste the full callback URL here: ").strip()
    
    if not callback_url:
        print("❌ No URL provided")
        return
    
    # Extract code from URL
    try:
        parsed = urlparse(callback_url)
        params = parse_qs(parsed.query)
        auth_code = params.get('code', [None])[0]
        
        if not auth_code:
            print("❌ No authorization code found in URL")
            return
            
        print(f"✅ Extracted code: {auth_code}")
        
        # Exchange for token
        token = asyncio.run(exchange_manual_code(auth_code))
        
        if token:
            print(f"\n🎊 SUCCESS! Your access token:")
            print(f"EWELINK_ACCESS_TOKEN={token}")
            print(f"\n📝 Add this to your Render environment variables:")
            print(f"1. Go to Render dashboard")
            print(f"2. Select your service: whatsapp-sonoff-automation") 
            print(f"3. Go to Environment tab")
            print(f"4. Add: EWELINK_ACCESS_TOKEN = {token}")
            print(f"5. Click 'Save Changes'")
            print(f"6. Service will restart automatically")
            
        else:
            print("\n❌ Failed to get access token")
            
    except Exception as e:
        print(f"❌ URL parsing error: {e}")

if __name__ == "__main__":
    main()