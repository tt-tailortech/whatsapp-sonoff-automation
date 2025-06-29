#!/usr/bin/env python3
"""
Test webhook with manual URL input
"""

import asyncio
import httpx
import json

async def test_webhook():
    """Test the webhook deployment"""
    
    # Common Render URL pattern
    render_url = "https://alarm-system-tt.onrender.com"
    
    print(f"🧪 Testing webhook at: {render_url}")
    
    # Test health endpoint first
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("🏥 Testing health endpoint...")
            response = await client.get(f"{render_url}/health")
            
            print(f"📡 Health Status: {response.status_code}")
            print(f"📄 Health Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service is {data.get('status', 'unknown')}")
                print(f"🔧 Services: {data.get('services', 'unknown')}")
                
            else:
                print("❌ Health check failed")
                return
                
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test webhook endpoint
    webhook_url = f"{render_url}/whatsapp-webhook"
    
    # Test message that should trigger alarm
    test_message = {
        "messages": [{
            "chat_id": "test@example.com",
            "from": "test@example.com", 
            "from_name": "Test User",
            "text": {
                "body": "alarma"
            }
        }]
    }
    
    print(f"\n🚨 Testing alarm command...")
    print(f"📤 Sending: {test_message}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=test_message)
            
            print(f"📡 Webhook Status: {response.status_code}")
            print(f"📄 Webhook Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Webhook responded successfully!")
                
                try:
                    data = response.json()
                    print(f"📋 Response data: {json.dumps(data, indent=2)}")
                except:
                    print("📋 Response is not JSON")
                    
            else:
                print(f"❌ Webhook error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Webhook test error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_webhook())
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")