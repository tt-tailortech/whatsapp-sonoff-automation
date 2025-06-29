#!/usr/bin/env python3
"""
Test your Render webhook deployment
"""

import asyncio
import httpx
import json

async def test_render_webhook():
    """Test the webhook on Render"""
    
    render_url = input("Enter your Render app URL (e.g., https://your-app.onrender.com): ").strip()
    
    if not render_url:
        print("❌ No URL provided")
        return
    
    # Test webhook endpoint
    webhook_url = f"{render_url}/webhook"
    
    # Test message that should trigger alarm
    test_message = {
        "messages": [{
            "chat_id": "test@example.com",
            "from": "test@example.com",
            "text": "alarma"
        }]
    }
    
    print(f"🧪 Testing webhook: {webhook_url}")
    print(f"📤 Sending test message: {test_message}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=test_message)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Webhook is responding!")
                
                # Check if it's a JSON response
                try:
                    data = response.json()
                    print(f"📋 Response data: {json.dumps(data, indent=2)}")
                except:
                    print("📋 Response is not JSON")
                    
            else:
                print(f"❌ Webhook error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Check if your Render app is deployed and running")

if __name__ == "__main__":
    try:
        asyncio.run(test_render_webhook())
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")