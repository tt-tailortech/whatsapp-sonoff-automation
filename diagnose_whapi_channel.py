#!/usr/bin/env python3
"""
Diagnose WHAPI.cloud channel status and find working endpoints
"""

import asyncio
import httpx
from app.config import settings

async def test_whapi_endpoints():
    """Test various WHAPI endpoints to understand channel status"""
    
    headers = {
        "Authorization": f"Bearer {settings.whapi_token}",
        "Content-Type": "application/json"
    }
    
    # List of endpoints to test
    endpoints_to_test = [
        # Common endpoints
        {"method": "GET", "path": "/", "desc": "Root endpoint"},
        {"method": "GET", "path": "/status", "desc": "Status check"},
        {"method": "GET", "path": "/health", "desc": "Health check"},
        {"method": "GET", "path": "/me", "desc": "Current user/channel info"},
        {"method": "GET", "path": "/account", "desc": "Account information"},
        {"method": "GET", "path": "/settings", "desc": "Channel settings"},
        
        # Channel-specific endpoints
        {"method": "GET", "path": "/channels", "desc": "List channels"},
        {"method": "GET", "path": "/channel", "desc": "Current channel info"},
        {"method": "GET", "path": "/channel/status", "desc": "Channel status"},
        {"method": "GET", "path": "/channel/info", "desc": "Channel information"},
        
        # WhatsApp-specific endpoints
        {"method": "GET", "path": "/contacts", "desc": "Contact list"},
        {"method": "GET", "path": "/chats", "desc": "Chat list"},
        {"method": "GET", "path": "/groups", "desc": "Group list"},
        
        # Messages endpoints
        {"method": "GET", "path": "/messages", "desc": "Recent messages"},
    ]
    
    print(f"🔑 Testing with token: {settings.whapi_token[:20]}...")
    print(f"🌐 Base URL: {settings.whapi_base_url}")
    print("=" * 80)
    
    working_endpoints = []
    
    for endpoint in endpoints_to_test:
        method = endpoint["method"]
        path = endpoint["path"]
        desc = endpoint["desc"]
        url = f"{settings.whapi_base_url}{path}"
        
        print(f"🧪 {method} {path:<20} - {desc}")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, headers=headers)
                
                status = response.status_code
                
                if status == 200:
                    print(f"   ✅ {status} - SUCCESS")
                    print(f"   📄 Response: {response.text[:100]}...")
                    working_endpoints.append({"endpoint": path, "response": response.text})
                elif status == 404:
                    print(f"   ❌ {status} - Not Found")
                elif status == 401:
                    print(f"   🔒 {status} - Unauthorized (check token)")
                elif status == 403:
                    print(f"   🚫 {status} - Forbidden")
                else:
                    print(f"   ⚠️  {status} - {response.text[:100]}")
                    
        except Exception as e:
            print(f"   💥 Exception: {type(e).__name__}: {str(e)}")
        
        print()
    
    print("=" * 80)
    print(f"📊 Summary: Found {len(working_endpoints)} working endpoints")
    
    for endpoint in working_endpoints:
        print(f"✅ {endpoint['endpoint']}")
        
    return working_endpoints

async def test_message_formats():
    """Test different message sending formats"""
    
    print("\n🔍 Testing different message sending approaches...")
    
    headers = {
        "Authorization": f"Bearer {settings.whapi_token}",
        "Content-Type": "application/json"
    }
    
    # Different message API paths to try
    message_endpoints = [
        "/messages/text",
        "/message/text", 
        "/send/text",
        "/api/messages/text",
        "/api/send/text",
        "/whatsapp/send",
        "/send",
    ]
    
    test_payload = {
        "to": "56940035815",
        "body": "🧪 API format test",
        "typing_time": 1
    }
    
    for endpoint in message_endpoints:
        url = f"{settings.whapi_base_url}{endpoint}"
        print(f"🧪 Testing: {endpoint}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=test_payload)
                
                if response.status_code != 404:
                    print(f"   📡 {response.status_code}: {response.text[:100]}")
                else:
                    print(f"   ❌ 404 - Not found")
                    
        except Exception as e:
            print(f"   💥 {type(e).__name__}")
        
        print()

async def main():
    """Main diagnostic function"""
    
    print("🩺 WHAPI.cloud Channel Diagnostic Tool")
    print("=" * 80)
    
    # Test basic endpoints
    working_endpoints = await test_whapi_endpoints()
    
    # Test message sending formats
    await test_message_formats()
    
    print("\n🎯 Recommendations:")
    if working_endpoints:
        print("✅ Some endpoints are working - token appears valid")
        print("🔍 Check the working endpoints for channel status info")
    else:
        print("❌ No endpoints working - possible issues:")
        print("   • Token may be expired or invalid")
        print("   • Channel may be disconnected/suspended")
        print("   • Account may need reactivation")
        print("   • Check WHAPI.cloud panel: https://panel.whapi.cloud")

if __name__ == "__main__":
    asyncio.run(main())