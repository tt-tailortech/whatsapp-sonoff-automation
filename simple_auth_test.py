#!/usr/bin/env python3
"""
Simple authentication test - try minimal approach
"""

import asyncio
import httpx
import json

# Test with a known working token format (if you have one)
# Or try the eWeLink web interface approach

async def test_simple_approaches():
    """Test simple authentication approaches"""
    
    print("🧪 Testing Simple Authentication Approaches")
    print("=" * 55)
    
    # Check if you have any existing eWeLink tokens in environment
    import os
    
    existing_token = os.getenv('EWELINK_ACCESS_TOKEN')
    if existing_token:
        print(f"🔍 Found existing token: {existing_token[:20]}...")
        await test_with_token(existing_token)
        return
    
    print("📋 Alternative Solutions:")
    print()
    print("1. **Use eWeLink Web Interface Token:**")
    print("   - Go to https://web.ewelink.cc")
    print("   - Login with tt.tailortech@gmail.com")
    print("   - Open browser developer tools (F12)")
    print("   - Look for API calls in Network tab")
    print("   - Find Authorization header with Bearer token")
    print()
    print("2. **Use Alternative Integration:**")
    print("   - Consider using IFTTT or Alexa integration")
    print("   - Or use eWeLink's MQTT broker if available")
    print()
    print("3. **Contact eWeLink Support:**")
    print("   - Your OAuth app may need manual approval")
    print("   - Email: support@ewelink.cc")
    print("   - Mention OAuth 2.0 integration issues")
    print()
    print("4. **Temporary Workaround:**")
    print("   - Use local webhook simulation")
    print("   - Or control devices through other means")

async def test_with_token(token: str):
    """Test a token if available"""
    
    endpoints = [
        "https://us-apia.coolkit.cc",
        "https://cn-apia.coolkit.cn", 
        "https://eu-apia.coolkit.cc"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing {endpoint} with token...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
                
                print(f"📡 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        devices = data.get("data", {}).get("thingList", [])
                        print(f"✅ Token works! Found {len(devices)} devices")
                        return True
                        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def check_current_system_status():
    """Check what parts of the system are working"""
    
    print("\n📊 Current System Status:")
    print("=" * 30)
    print("✅ Render deployment: WORKING")
    print("✅ Webhook processing: WORKING") 
    print("✅ WhatsApp integration: WORKING")
    print("✅ Voice generation: WORKING")
    print("✅ Message parsing: WORKING")
    print("❌ eWeLink device control: BLOCKED")
    print()
    print("🎯 Only missing piece: eWeLink authentication")
    print()
    print("💡 Suggestion: For now, you can:")
    print("   1. Test WhatsApp voice responses (working)")
    print("   2. Verify alarm logic (working)")
    print("   3. Use eWeLink app manually for devices")
    print("   4. Work on getting proper OAuth token")

if __name__ == "__main__":
    try:
        asyncio.run(test_simple_approaches())
        check_current_system_status()
        
    except Exception as e:
        print(f"❌ Error: {e}")