import os
import httpx
import base64
import time
from typing import Optional, Dict, Any
from app.config import settings
from app.models import WhatsAppMessage

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.whapi_base_url
        self.token = settings.whapi_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.processed_message_ids = set()  # Track processed message IDs
        self.max_processed_ids = 1000  # Limit to prevent memory issues
    
    def parse_whatsapp_webhook(self, payload: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """
        Parse WhatsApp webhook payload and extract message information
        Based on actual WHAPI.cloud webhook format analysis
        """
        try:
            # Debug: Print received payload structure
            print(f"📨 Webhook payload keys: {list(payload.keys())}")
            print(f"📨 Full payload: {payload}")
            print(f"📨 Currently processed message IDs: {list(self.processed_message_ids)[-10:]}")
            
            # Skip status updates (delivery confirmations)
            if "statuses" in payload:
                print("📨 Skipping status update webhook")
                return None
            
            # Handle direct messages format - this is the PRIMARY format, process first
            if "messages" in payload and payload["messages"]:
                message = payload["messages"][0]
                print(f"📨 Direct message found: {message}")
                
                # Only process incoming messages (from_me: False means it's TO us)
                # If from_me: True, it means we sent it, so ignore
                if message.get("from_me", True):
                    print(f"📨 Ignoring outgoing message (from_me: True)")
                    return None
                
                if message.get("type") == "text":
                    message_id = message.get("id", "")
                    
                    # Check for duplicate message
                    if message_id in self.processed_message_ids:
                        print(f"📨 Skipping duplicate message ID: {message_id}")
                        return None
                    
                    # Mark message as processed
                    self.processed_message_ids.add(message_id)
                    
                    # Clean up old IDs if set gets too large
                    if len(self.processed_message_ids) > self.max_processed_ids:
                        # Keep only the most recent 500 IDs
                        self.processed_message_ids = set(list(self.processed_message_ids)[-500:])
                    
                    print(f"📨 Processing incoming text message")
                    
                    return WhatsAppMessage(
                        id=message_id,
                        from_phone=message.get("from", ""),
                        chat_id=message.get("chat_id", ""),
                        text=message.get("text", {}).get("body", "") if isinstance(message.get("text"), dict) else message.get("text", ""),
                        contact_name=message.get("from_name", "Usuario"),
                        timestamp=str(message.get("timestamp", ""))
                    )
                
                # Return None for non-text messages in direct format
                return None
            
            # Handle chat updates format - ONLY if no direct messages were found
            if "chats_updates" in payload and payload["chats_updates"]:
                chat_updates = payload["chats_updates"]
                print(f"📨 Chat updates found: {len(chat_updates)}")
                
                for chat_update in chat_updates:
                    # Look for new incoming messages in after_update
                    if "after_update" in chat_update:
                        after_update = chat_update["after_update"]
                        if "last_message" in after_update:
                            message = after_update["last_message"]
                            print(f"📨 Chat update message: {message}")
                            
                            # Only process incoming messages
                            if message.get("from_me", True):
                                print(f"📨 Ignoring chat update outgoing message")
                                continue
                                
                            if message.get("type") == "text":
                                message_id = message.get("id", "")
                                message_timestamp = message.get("timestamp", 0)
                                current_time = int(time.time())
                                message_age = current_time - message_timestamp
                                
                                print(f"📨 Chat update message timestamp: {message_timestamp}, current: {current_time}, age: {message_age}s")
                                
                                # Skip messages older than 30 seconds to avoid processing old messages
                                if message_age > 30:
                                    print(f"📨 Skipping old chat update message (age: {message_age}s)")
                                    continue
                                
                                # Check for duplicate message
                                if message_id in self.processed_message_ids:
                                    print(f"📨 Skipping duplicate chat update message ID: {message_id}")
                                    continue
                                
                                # Mark message as processed
                                self.processed_message_ids.add(message_id)
                                print(f"📨 Processing chat update incoming message")
                                
                                return WhatsAppMessage(
                                    id=message_id,
                                    from_phone=message.get("from", ""),
                                    chat_id=message.get("chat_id", ""),
                                    text=message.get("text", {}).get("body", "") if isinstance(message.get("text"), dict) else message.get("text", ""),
                                    contact_name=message.get("from_name", "Usuario"),
                                    timestamp=str(message.get("timestamp", ""))
                                )
                    
                    # Check if this chat update contains direct messages array
                    if "messages" in chat_update and chat_update["messages"]:
                        messages = chat_update["messages"]
                        print(f"📨 Messages in chat update: {len(messages)}")
                        
                        for message in messages:
                            print(f"📨 Message keys: {list(message.keys())}")
                            print(f"📨 Message type: {message.get('type')}")
                            
                            if message.get("type") == "text" and not message.get("from_me", True):
                                return WhatsAppMessage(
                                    id=message.get("id", ""),
                                    from_phone=message.get("from", ""),
                                    chat_id=message.get("chat_id", ""),
                                    text=message.get("text", {}).get("body", "") if isinstance(message.get("text"), dict) else message.get("text", ""),
                                    contact_name=message.get("from_name", "Usuario"),
                                    timestamp=str(message.get("timestamp", ""))
                                )
            
            # Handle other possible formats (keeping existing logic as fallback)
            if "messages" in payload and payload["messages"]:
                # Direct messages format
                message = payload["messages"][0]
                
                # Temporarily bypass from_me check for testing
                # if message.get("from_me", False):
                #     print("📨 Skipping direct message from us (from_me: True)")
                #     return None
                print(f"📨 Processing direct message (from_me: {message.get('from_me', False)})")
                
                if message.get("type") == "text":
                    return WhatsAppMessage(
                        id=message.get("id", ""),
                        from_phone=message.get("from", ""),
                        chat_id=message.get("chat_id", ""),
                        text=message.get("text", {}).get("body", ""),
                        contact_name=payload.get("contacts", [{}])[0].get("profile", {}).get("name"),
                        timestamp=str(message.get("timestamp", ""))
                    )
            
            elif "entry" in payload:
                # Business API format (similar to n8n)
                entry = payload["entry"][0]
                changes = entry.get("changes", [])
                
                if changes:
                    value = changes[0].get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    
                    if messages and messages[0].get("type") == "text":
                        message = messages[0]
                        contact = contacts[0] if contacts else {}
                        
                        return WhatsAppMessage(
                            id=message.get("id", ""),
                            from_phone=message.get("from", ""),
                            chat_id=message.get("chat_id", ""),
                            text=message.get("text", {}).get("body", ""),
                            contact_name=contact.get("profile", {}).get("name"),
                            timestamp=message.get("timestamp", "")
                        )
            
            print("❌ No valid message format found in webhook payload")
            return None
            
            print("❌ No valid incoming message found in webhook payload")
            return None
            
        except Exception as e:
            print(f"WhatsApp webhook parsing error: {str(e)}")
            return None
    
    async def send_text_message(self, phone_number: str, message: str) -> bool:
        """
        Send a text message via WhatsApp using WHAPI.cloud API
        """
        try:
            url = f"{self.base_url}/messages/text"
            
            # Correct payload format based on WHAPI.cloud documentation
            payload = {
                "to": phone_number,
                "body": message,
                "typing_time": 1  # Simulate 1 second typing for more natural feel
            }
            
            print(f"📤 Sending message to {phone_number}: {message[:50]}...")
            print(f"📤 URL: {url}")
            print(f"📤 Payload: {payload}")
            print(f"📤 Headers: {self.headers}")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:  # Increased timeout for WHAPI
                    response = await client.post(url, headers=self.headers, json=payload)
                    
                    print(f"📤 Response status: {response.status_code}")
                    print(f"📤 Response body: {response.text}")
                    
                    if response.status_code == 200:
                        print(f"✅ Text message sent to {phone_number}")
                        return True
                    else:
                        print(f"❌ Failed to send text message: {response.status_code} - {response.text}")
                        return False
            except Exception as http_err:
                print(f"❌ HTTP request failed: {str(http_err)}")
                print(f"❌ HTTP error type: {type(http_err)}")
                raise http_err
                    
        except Exception as e:
            print(f"❌ Send text message error: {str(e)} | To: {phone_number} | Message: {message[:50]}...")
            return False
    
    async def send_voice_message(self, phone_number: str, audio_file_path: str) -> bool:
        """
        Send a voice message via WhatsApp using WHAPI.cloud API (Base64 method)
        """
        try:
            if not os.path.exists(audio_file_path):
                print(f"❌ Audio file not found: {audio_file_path}")
                return False
            
            file_size = os.path.getsize(audio_file_path)
            url = f"{self.base_url}/sendmessagevoice"
            
            print(f"🎤 Sending voice message (Base64) to {phone_number}")
            print(f"   File: {audio_file_path} ({file_size} bytes)")
            print(f"   URL: {url}")
            
            # Read audio file and encode as base64
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode()
            
            print(f"   Base64 length: {len(audio_base64)} characters")
            
            # Correct payload format based on WHAPI.cloud documentation
            payload = {
                "to": phone_number,
                "voice": f"data:audio/ogg;base64,{audio_base64}"
            }
            
            print(f"🎤 Payload: {{'to': '{phone_number}', 'voice': 'data:audio/ogg;base64,[{len(audio_base64)} chars]'}}")
            print(f"🎤 Headers: {self.headers}")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=self.headers, json=payload)
                    
                    print(f"🎤 Response status: {response.status_code}")
                    print(f"🎤 Response body: {response.text}")
                    
                    if response.status_code == 200:
                        print(f"✅ Voice message sent via Base64 to {phone_number}")
                        return True
                    else:
                        print(f"❌ Failed to send voice message via Base64: {response.status_code}")
                        return False
            except Exception as http_err:
                print(f"❌ HTTP request failed: {str(http_err)}")
                print(f"❌ HTTP error type: {type(http_err)}")
                raise http_err
                    
        except Exception as e:
            print(f"❌ Send voice message error (Base64): {str(e)} | File: {audio_file_path}")
            return False
    
    async def send_voice_message_with_file_upload(self, phone_number: str, audio_file_path: str) -> bool:
        """
        Alternative method: Send voice message using multipart file upload
        """
        try:
            if not os.path.exists(audio_file_path):
                print(f"❌ Audio file not found: {audio_file_path}")
                return False
            
            file_size = os.path.getsize(audio_file_path)
            url = f"{self.base_url}/sendmessagevoice"
            
            print(f"🎤 Sending voice message (File Upload) to {phone_number}")
            print(f"   File: {audio_file_path} ({file_size} bytes)")
            print(f"   URL: {url}")
            
            # Remove Content-Type header for multipart
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            data = {
                "to": phone_number
            }
            
            print(f"🎤 Data: {data}")
            print(f"🎤 Headers: {headers}")
            
            # Prepare multipart form data
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "voice": ("voice.ogg", audio_file.read(), "audio/ogg; codecs=opus")
                }
                
                print(f"🎤 Files: voice file ({len(files['voice'][1])} bytes)")
                
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(url, headers=headers, data=data, files=files)
                        
                        print(f"🎤 Response status: {response.status_code}")
                        print(f"🎤 Response body: {response.text}")
                        
                        if response.status_code == 200:
                            print(f"✅ Voice message sent via File Upload to {phone_number}")
                            return True
                        else:
                            print(f"❌ Failed to send voice message via File Upload: {response.status_code}")
                            return False
                except Exception as http_err:
                    print(f"❌ HTTP request failed: {str(http_err)}")
                    print(f"❌ HTTP error type: {type(http_err)}")
                    raise http_err
                        
        except Exception as e:
            print(f"❌ Send voice message error (File Upload): {str(e)} | File: {audio_file_path}")
            return False
    
    async def send_voice_message_via_upload_media(self, phone_number: str, audio_file_path: str) -> bool:
        """
        Send voice message using WHAPI's /uploadmedia + /sendmessagevoice approach
        """
        try:
            if not os.path.exists(audio_file_path):
                print(f"❌ Audio file not found: {audio_file_path}")
                return False
            
            file_size = os.path.getsize(audio_file_path)
            
            print(f"🎤 Sending voice message (Upload Media) to {phone_number}")
            print(f"   File: {audio_file_path} ({file_size} bytes)")
            
            # Step 1: Upload media file first
            upload_url = f"{self.base_url}/uploadmedia"
            
            headers_upload = {
                "Authorization": f"Bearer {self.token}"
            }
            
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "media": ("voice.ogg", audio_file.read(), "audio/ogg")
                }
                
                print(f"🎤 Step 1: Uploading media to {upload_url}")
                
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        upload_response = await client.post(upload_url, headers=headers_upload, files=files)
                        
                        print(f"🎤 Upload Response status: {upload_response.status_code}")
                        print(f"🎤 Upload Response body: {upload_response.text}")
                        
                        if upload_response.status_code != 200:
                            print(f"❌ Media upload failed: {upload_response.status_code}")
                            return False
                        
                        # Parse media ID from response
                        upload_data = upload_response.json()
                        media_id = upload_data.get("media_id") or upload_data.get("id")
                        
                        if not media_id:
                            print(f"❌ No media ID in upload response: {upload_data}")
                            return False
                        
                        print(f"✅ Media uploaded successfully, ID: {media_id}")
                        
                except Exception as upload_err:
                    print(f"❌ Upload request failed: {str(upload_err)}")
                    return False
            
            # Step 2: Send voice message using media ID
            send_url = f"{self.base_url}/sendmessagevoice"
            
            payload = {
                "to": phone_number,
                "media": media_id
            }
            
            headers_send = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            print(f"🎤 Step 2: Sending voice message to {send_url}")
            print(f"🎤 Payload: {payload}")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    send_response = await client.post(send_url, headers=headers_send, json=payload)
                    
                    print(f"🎤 Send Response status: {send_response.status_code}")
                    print(f"🎤 Send Response body: {send_response.text}")
                    
                    if send_response.status_code == 200:
                        print(f"✅ Voice message sent via Upload Media to {phone_number}")
                        return True
                    else:
                        print(f"❌ Failed to send voice message via Upload Media: {send_response.status_code}")
                        return False
            except Exception as send_err:
                print(f"❌ Send request failed: {str(send_err)}")
                return False
                        
        except Exception as e:
            print(f"❌ Send voice message error (Upload Media): {str(e)} | File: {audio_file_path}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get WhatsApp account information
        """
        try:
            url = f"{self.base_url}/account"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Failed to get account info: {response.status_code}")
                    return {}
                    
        except Exception as e:
            print(f"Get account info error: {str(e)}")
            return {}