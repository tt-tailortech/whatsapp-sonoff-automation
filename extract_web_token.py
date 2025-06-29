#!/usr/bin/env python3
"""
Instructions to extract working token from eWeLink web interface
"""

print("🔐 Extract Working Token from eWeLink Web Interface")
print("=" * 60)
print()
print("Since your pro account is working in the web interface,")
print("we can extract the working Bearer token from there:")
print()
print("📋 STEP-BY-STEP INSTRUCTIONS:")
print()
print("1. **Open eWeLink Web Interface:**")
print("   Go to: https://web.ewelink.cc")
print("   Login with: tt.tailortech@gmail.com / Qwerty.2025")
print()
print("2. **Open Browser Developer Tools:**")
print("   - Press F12 (or right-click → Inspect)")
print("   - Go to 'Network' tab")
print("   - Make sure 'XHR' filter is selected")
print()
print("3. **Trigger Device Control:**")
print("   - Turn your SONOFF device ON/OFF in the web interface")
print("   - Watch for API calls in the Network tab")
print()
print("4. **Find API Call:**")
print("   - Look for calls to domains like:")
print("     * apia.coolkit.cc")
print("     * coolkit.cn")
print("   - Click on one of these API calls")
print()
print("5. **Extract Authorization Header:**")
print("   - In the request details, find 'Request Headers'")
print("   - Look for: 'Authorization: Bearer xxxxxxxx'")
print("   - Copy the token part (after 'Bearer ')")
print()
print("6. **Test the Token:**")
print("   Run: python3 test_manual_token.py YOUR_TOKEN_HERE")
print()
print("7. **Add to Render:**")
print("   - Go to Render dashboard")
print("   - Environment variables")
print("   - Add: EWELINK_ACCESS_TOKEN = your_token")
print()
print("🎯 This will give us the working token your web interface uses!")
print()
print("💡 Alternative: You can also look for WebSocket connections")
print("   in the 'WS' tab if the device control uses WebSockets.")
print()
print("Want me to create a token tester script for when you get the token?")

# Create a simple token tester
test_script = '''#!/usr/bin/env python3
"""
Test manually extracted token
"""

import asyncio
import httpx
import sys

async def test_token(token: str):
    """Test extracted token"""
    
    if not token:
        print("Usage: python3 test_manual_token.py YOUR_TOKEN")
        return
    
    print(f"🧪 Testing token: {token[:20]}...")
    
    endpoints = [
        "https://cn-apia.coolkit.cn",
        "https://us-apia.coolkit.cc", 
        "https://eu-apia.coolkit.cc"
    ]
    
    for endpoint in endpoints:
        print(f"\\n🌐 Testing {endpoint}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{endpoint}/v2/device/thing", headers=headers)
                
                print(f"📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") == 0:
                        devices = data.get("data", {}).get("thingList", [])
                        print(f"✅ SUCCESS! Found {len(devices)} devices")
                        
                        for device in devices:
                            print(f"  - {device.get('name')} (ID: {device.get('deviceid')})")
                        
                        print(f"\\n💾 Working token for Render:")
                        print(f"EWELINK_ACCESS_TOKEN={token}")
                        return True
                    else:
                        print(f"❌ API Error: {data.get('msg')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_manual_token.py YOUR_TOKEN")
        sys.exit(1)
    
    token = sys.argv[1]
    asyncio.run(test_token(token))
'''

with open('test_manual_token.py', 'w') as f:
    f.write(test_script)

print("✅ Created test_manual_token.py for testing extracted tokens")