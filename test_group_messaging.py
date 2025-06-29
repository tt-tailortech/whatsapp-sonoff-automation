#!/usr/bin/env python3
"""
Test Group Messaging and Metadata Creation
Send WhatsApp messages to groups and verify metadata file creation
"""

import asyncio
import json
import httpx
from datetime import datetime

# Test webhook payloads simulating WhatsApp group messages
TEST_GROUP_MESSAGES = [
    {
        "name": "Test Group 1 - Simple SOS",
        "payload": {
            "messages": [{
                "id": "test_msg_001",
                "from": "56940035815",  # Waldo's number
                "chat_id": "120363400467632359@g.us",  # Group chat ID
                "from_me": False,
                "type": "text",
                "text": {"body": "SOS INCENDIO en mi edificio!"},
                "timestamp": int(datetime.now().timestamp()),
                "from_name": "Waldo Rodriguez",
                "chat_name": "Building Emergency Team"
            }]
        }
    },
    {
        "name": "Test Group 2 - Medical Emergency", 
        "payload": {
            "messages": [{
                "id": "test_msg_002",
                "from": "56987654321",  # Ana's number
                "chat_id": "120363400467632360@g.us",  # Different group
                "from_me": False,
                "type": "text", 
                "text": {"body": "SOS EMERGENCIA MÉDICA necesito ayuda urgente"},
                "timestamp": int(datetime.now().timestamp()),
                "from_name": "Ana Martinez",
                "chat_name": "Neighborhood Watch - Las Condes"
            }]
        }
    },
    {
        "name": "Test Group 3 - General Emergency",
        "payload": {
            "messages": [{
                "id": "test_msg_003",
                "from": "56912345678",  # Carlos' number
                "chat_id": "120363400467632361@g.us",  # Another group
                "from_me": False,
                "type": "text",
                "text": {"body": "SOS"},
                "timestamp": int(datetime.now().timestamp()),
                "from_name": "Carlos Silva",
                "chat_name": "Apartment Complex A - Floor 10"
            }]
        }
    },
    {
        "name": "Test Individual Chat (Should Skip Group Management)",
        "payload": {
            "messages": [{
                "id": "test_msg_004", 
                "from": "56940035815",
                "chat_id": "56940035815@s.whatsapp.net",  # Individual chat (not @g.us)
                "from_me": False,
                "type": "text",
                "text": {"body": "Hello individual message"},
                "timestamp": int(datetime.now().timestamp()),
                "from_name": "Waldo Rodriguez"
            }]
        }
    }
]

async def test_group_messaging():
    """Test group messaging and metadata creation"""
    print("🧪 Testing WhatsApp Group Messaging & Metadata Creation")
    print("=" * 70)
    
    # Test server endpoint
    webhook_url = "http://localhost:8000/whatsapp-webhook"
    
    results = []
    
    for test_case in TEST_GROUP_MESSAGES:
        print(f"\n🧪 {test_case['name']}")
        print("-" * 50)
        
        payload = test_case['payload']
        message = payload['messages'][0]
        
        print(f"📨 From: {message['from_name']} ({message['from']})")
        print(f"💬 Chat: {message.get('chat_name', 'N/A')} ({message['chat_id']})")
        print(f"📝 Message: {message['text']['body']}")
        print(f"🏘️ Is Group: {'✅' if message['chat_id'].endswith('@g.us') else '❌'}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook_url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                print(f"📤 Response: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ Webhook processed successfully")
                    result_status = "SUCCESS"
                else:
                    print(f"❌ Webhook failed: {response.text}")
                    result_status = "FAILED"
                    
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            result_status = "ERROR"
        
        results.append({
            "test": test_case['name'],
            "status": result_status,
            "group_name": message.get('chat_name', 'N/A'),
            "chat_id": message['chat_id'],
            "is_group": message['chat_id'].endswith('@g.us')
        })
        
        # Wait between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n🏆 TEST SUMMARY")
    print("=" * 70)
    
    for result in results:
        status_emoji = "✅" if result['status'] == "SUCCESS" else "❌"
        group_type = "GROUP" if result['is_group'] else "INDIVIDUAL"
        print(f"{status_emoji} {result['test']}")
        print(f"   📍 {group_type}: {result['group_name']}")
        print(f"   📋 Status: {result['status']}")
        print()
    
    success_count = len([r for r in results if r['status'] == "SUCCESS"])
    total_count = len(results)
    
    print(f"📊 Results: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("🎉 All tests passed! Group metadata system working correctly.")
    else:
        print("⚠️ Some tests failed. Check server logs for details.")
    
    return results

async def verify_group_folders():
    """Verify group folders were created in Google Drive"""
    print("\n🔍 Verifying Group Folders in Google Drive...")
    print("-" * 50)
    
    try:
        from app.services.group_manager_service import GroupManagerService
        
        manager = GroupManagerService()
        
        expected_groups = [
            ("120363400467632359@g.us", "Building Emergency Team"),
            ("120363400467632360@g.us", "Neighborhood Watch - Las Condes"), 
            ("120363400467632361@g.us", "Apartment Complex A - Floor 10")
        ]
        
        for group_id, group_name in expected_groups:
            print(f"\n🔍 Checking: {group_name}")
            
            member_data = await manager.get_group_member_data(group_id, group_name)
            
            if member_data:
                print(f"✅ Found metadata file")
                print(f"   📋 Group: {member_data.get('group_name')}")
                print(f"   👥 Members: {len(member_data.get('members', {}))}")
                print(f"   👑 Admins: {len(member_data.get('admins', []))}")
                print(f"   📅 Created: {member_data.get('created_date', 'Unknown')}")
            else:
                print(f"❌ Metadata file not found")
        
        print(f"\n✅ Google Drive verification complete")
        
    except Exception as e:
        print(f"❌ Google Drive verification error: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Starting WhatsApp Group Messaging Tests")
    print("=" * 70)
    
    # Test 1: Send webhook messages
    results = await test_group_messaging()
    
    # Wait for processing
    print("\n⏳ Waiting 5 seconds for Google Drive processing...")
    await asyncio.sleep(5)
    
    # Test 2: Verify Google Drive folders
    await verify_group_folders()
    
    print("\n🏁 Testing complete!")

if __name__ == "__main__":
    asyncio.run(main())