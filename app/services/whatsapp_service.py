import os
import httpx
import base64
import time
import asyncio
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
        
        # DEVELOPMENT MODE: Allow processing own messages for testing
        self.development_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
        if self.development_mode:
            print("🔧 DEVELOPMENT MODE ENABLED - Processing own messages for testing")
        
        # Initialize Group Manager (lazy loading to avoid circular imports)
        self.group_manager = None
    
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
            
            # Skip status updates, delivery confirmations, and other non-message events
            if "statuses" in payload:
                print("📨 Skipping status update webhook")
                return None
            
            # Skip non-text message types early
            message_type = None
            if "messages" in payload and payload["messages"]:
                message_type = payload["messages"][0].get("type", "")
            elif "chats_updates" in payload and payload["chats_updates"]:
                for chat_update in payload["chats_updates"]:
                    if "after_update" in chat_update and "last_message" in chat_update["after_update"]:
                        message_type = chat_update["after_update"]["last_message"].get("type", "")
                        break
            
            # Only process text messages
            if message_type and message_type != "text":
                print(f"📨 Skipping non-text message type: {message_type}")
                return None
            
            # Handle direct messages format - this is the PRIMARY format, process first
            if "messages" in payload and payload["messages"]:
                message = payload["messages"][0]
                print(f"📨 Direct message found: {message}")
                
                # Only process incoming messages (from_me: False means it's TO us)
                # If from_me: True, it means we sent it, so ignore (UNLESS in development mode)
                if message.get("from_me", True) and not self.development_mode:
                    print(f"📨 Ignoring outgoing message (from_me: True)")
                    return None
                elif message.get("from_me", True) and self.development_mode:
                    print(f"🔧 DEVELOPMENT MODE: Processing own message for testing")
                
                if message.get("type") == "text":
                    message_id = message.get("id", "")
                    message_timestamp = message.get("timestamp", 0)
                    current_time = int(time.time())
                    message_age = current_time - message_timestamp
                    
                    print(f"📨 Direct message timestamp: {message_timestamp}, current: {current_time}, age: {message_age}s")
                    
                    # Skip messages older than 30 seconds to avoid processing old messages
                    if message_age > 30:
                        print(f"📨 Skipping old direct message (age: {message_age}s)")
                        return None
                    
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
                    
                    # Extract chat name - prioritize group chat name for groups, contact name for individual chats
                    chat_name = None
                    if message.get("chat_id", "").endswith("@g.us"):
                        # Group chat - try multiple possible fields for group name
                        chat_name = message.get("chat_name") or message.get("chat_title") or "Grupo"
                        print(f"📨 Group chat detected: {chat_name}")
                    else:
                        # Individual chat - use contact name
                        chat_name = message.get("from_name", "Usuario")
                        print(f"📨 Individual chat detected: {chat_name}")
                    
                    return WhatsAppMessage(
                        id=message_id,
                        from_phone=message.get("from", ""),
                        chat_id=message.get("chat_id", ""),
                        text=message.get("text", {}).get("body", "") if isinstance(message.get("text"), dict) else message.get("text", ""),
                        contact_name=message.get("from_name", "Usuario"),
                        chat_name=chat_name,
                        timestamp=str(message.get("timestamp", ""))
                    )
                
                # Return None for non-text messages in direct format
                return None
            
            # Handle chat updates format - ONLY if no direct messages were found
            if "chats_updates" in payload and payload["chats_updates"]:
                chat_updates = payload["chats_updates"]
                print(f"📨 Chat updates found: {len(chat_updates)}")
                
                for chat_update in chat_updates:
                    # Skip chat updates that are just timestamp changes without new messages
                    changes = chat_update.get("changes", [])
                    if changes == ["timestamp"]:
                        print(f"📨 Skipping timestamp-only chat update")
                        continue
                    # Look for new incoming messages in after_update
                    if "after_update" in chat_update:
                        after_update = chat_update["after_update"]
                        if "last_message" in after_update:
                            message = after_update["last_message"]
                            print(f"📨 Chat update message: {message}")
                            
                            # Only process incoming messages (UNLESS in development mode)
                            if message.get("from_me", True) and not self.development_mode:
                                print(f"📨 Ignoring chat update outgoing message")
                                continue
                            elif message.get("from_me", True) and self.development_mode:
                                print(f"🔧 DEVELOPMENT MODE: Processing own chat update message for testing")
                                
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
                                
                                # Extract chat name for chat updates
                                chat_name = None
                                if message.get("chat_id", "").endswith("@g.us"):
                                    # Group chat - try to get name from chat update or message
                                    chat_name = (chat_update.get("after_update", {}).get("name") or 
                                               message.get("chat_name") or 
                                               message.get("chat_title") or 
                                               "Grupo")
                                    print(f"📨 Chat update group: {chat_name}")
                                else:
                                    # Individual chat
                                    chat_name = message.get("from_name", "Usuario")
                                    print(f"📨 Chat update individual: {chat_name}")
                                
                                return WhatsAppMessage(
                                    id=message_id,
                                    from_phone=message.get("from", ""),
                                    chat_id=message.get("chat_id", ""),
                                    text=message.get("text", {}).get("body", "") if isinstance(message.get("text"), dict) else message.get("text", ""),
                                    contact_name=message.get("from_name", "Usuario"),
                                    chat_name=chat_name,
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
                                # Extract chat name for messages in chat updates
                                chat_name = None
                                if message.get("chat_id", "").endswith("@g.us"):
                                    # Group chat
                                    chat_name = (message.get("chat_name") or 
                                               message.get("chat_title") or 
                                               chat_update.get("name") or
                                               "Grupo")
                                    print(f"📨 Chat update message group: {chat_name}")
                                else:
                                    # Individual chat
                                    chat_name = message.get("from_name", "Usuario")
                                    print(f"📨 Chat update message individual: {chat_name}")
                                
                                return WhatsAppMessage(
                                    id=message.get("id", ""),
                                    from_phone=message.get("from", ""),
                                    chat_id=message.get("chat_id", ""),
                                    text=message.get("text", {}).get("body", "") if isinstance(message.get("text"), dict) else message.get("text", ""),
                                    contact_name=message.get("from_name", "Usuario"),
                                    chat_name=chat_name,
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
                    # Extract chat name for direct messages fallback
                    contact_name = payload.get("contacts", [{}])[0].get("profile", {}).get("name")
                    chat_name = None
                    if message.get("chat_id", "").endswith("@g.us"):
                        # Group chat
                        chat_name = (message.get("chat_name") or 
                                   message.get("chat_title") or 
                                   "Grupo")
                        print(f"📨 Direct message group: {chat_name}")
                    else:
                        # Individual chat
                        chat_name = contact_name or "Usuario"
                        print(f"📨 Direct message individual: {chat_name}")
                    
                    return WhatsAppMessage(
                        id=message.get("id", ""),
                        from_phone=message.get("from", ""),
                        chat_id=message.get("chat_id", ""),
                        text=message.get("text", {}).get("body", ""),
                        contact_name=contact_name,
                        chat_name=chat_name,
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
                        
                        # Extract chat name for business API format
                        contact_name = contact.get("profile", {}).get("name")
                        chat_name = None
                        if message.get("chat_id", "").endswith("@g.us"):
                            # Group chat
                            chat_name = (message.get("chat_name") or 
                                       message.get("chat_title") or 
                                       "Grupo")
                            print(f"📨 Business API group: {chat_name}")
                        else:
                            # Individual chat
                            chat_name = contact_name or "Usuario"
                            print(f"📨 Business API individual: {chat_name}")
                        
                        return WhatsAppMessage(
                            id=message.get("id", ""),
                            from_phone=message.get("from", ""),
                            chat_id=message.get("chat_id", ""),
                            text=message.get("text", {}).get("body", ""),
                            contact_name=contact_name,
                            chat_name=chat_name,
                            timestamp=message.get("timestamp", "")
                        )
            
            print("❌ No valid message format found in webhook payload")
            return None
            
        except Exception as e:
            print(f"WhatsApp webhook parsing error: {str(e)}")
            return None
    
    async def process_group_management(self, message: WhatsAppMessage) -> bool:
        """
        Process group management - ensure group folder exists for group messages
        """
        try:
            # Only process group messages
            if not message.chat_id.endswith("@g.us"):
                return True  # Individual messages don't need group management
            
            # Lazy load group manager to avoid circular imports
            if self.group_manager is None:
                from app.services.group_manager_service import GroupManagerService
                self.group_manager = GroupManagerService()
            
            # Ensure group folder exists
            print(f"🏘️ Processing group management for: {message.chat_name}")
            result = await self.group_manager.ensure_group_folder_exists(
                group_chat_id=message.chat_id,
                group_name=message.chat_name or "Unknown Group",
                sender_phone=message.from_phone,
                sender_name=message.contact_name or "Unknown User"
            )
            
            if result:
                print(f"✅ Group management completed for: {message.chat_name}")
                return True
            else:
                print(f"⚠️ Group management failed for: {message.chat_name}")
                return False
                
        except Exception as e:
            print(f"❌ Group management error: {str(e)}")
            return False
    
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
            url = f"{self.base_url}/messages/voice"
            
            print(f"🎤 Sending voice message (Base64) to {phone_number}")
            print(f"   File: {audio_file_path} ({file_size} bytes)")
            print(f"   URL: {url}")
            
            # Read audio file and encode as base64
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode()
            
            print(f"   Base64 length: {len(audio_base64)} characters")
            
            # Try voice message format similar to text messages
            payload = {
                "to": phone_number,
                "media": f"data:audio/ogg;base64,{audio_base64}",
                "type": "voice"
            }
            
            print(f"🎤 Payload: {{'to': '{phone_number}', 'media': 'data:audio/ogg;base64,[{len(audio_base64)} chars]', 'type': 'voice'}}")
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
            url = f"{self.base_url}/messages/voice"
            
            print(f"🎤 Sending voice message (File Upload) to {phone_number}")
            print(f"   File: {audio_file_path} ({file_size} bytes)")
            print(f"   URL: {url}")
            
            # Remove Content-Type header for multipart
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            data = {
                "to": phone_number,
                "type": "voice"
            }
            
            print(f"🎤 Data: {data}")
            print(f"🎤 Headers: {headers}")
            
            # Prepare multipart form data
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "media": ("voice.ogg", audio_file.read(), "audio/ogg; codecs=opus")
                }
                
                print(f"🎤 Files: media file ({len(files['media'][1])} bytes)")
                
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
            upload_url = f"{self.base_url}/messages/media"
            
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
    
    async def send_image_message(self, phone_number: str, image_file_path: str, caption: str = "") -> bool:
        """
        Send an image message via WhatsApp using WHAPI.cloud API (Base64 method)
        """
        try:
            if not os.path.exists(image_file_path):
                print(f"❌ Image file not found: {image_file_path}")
                return False
            
            file_size = os.path.getsize(image_file_path)
            url = f"{self.base_url}/messages/image"
            
            print(f"📷 Sending image message (Base64) to {phone_number}")
            print(f"   File: {image_file_path} ({file_size} bytes)")
            print(f"   Caption: {caption}")
            print(f"   URL: {url}")
            
            # Read image file and encode as base64
            with open(image_file_path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode()
            
            print(f"   Base64 length: {len(image_base64)} characters")
            
            # Determine MIME type based on file extension
            file_ext = os.path.splitext(image_file_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(file_ext, 'image/jpeg')
            
            # Payload format for image messages (following WHAPI.cloud pattern)
            payload = {
                "to": phone_number,
                "media": f"data:{mime_type};base64,{image_base64}"
            }
            
            if caption:
                payload["caption"] = caption
            
            print(f"📷 Payload: {{'to': '{phone_number}', 'media': 'data:{mime_type};base64,[{len(image_base64)} chars]', 'type': 'image', 'caption': '{caption}'}}")
            print(f"📷 Headers: {self.headers}")
            
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for images
                    response = await client.post(url, headers=self.headers, json=payload)
                    
                    print(f"📷 Response status: {response.status_code}")
                    print(f"📷 Response body: {response.text}")
                    
                    if response.status_code == 200:
                        print(f"✅ Image message sent via Base64 to {phone_number}")
                        return True
                    else:
                        print(f"❌ Failed to send image message via Base64: {response.status_code}")
                        return False
            except Exception as http_err:
                print(f"❌ HTTP request failed: {str(http_err)}")
                print(f"❌ HTTP error type: {type(http_err)}")
                raise http_err
                    
        except Exception as e:
            print(f"❌ Send image message error (Base64): {str(e)} | File: {image_file_path}")
            return False
    
    async def send_image_message_via_media_endpoint(self, phone_number: str, image_file_path: str, caption: str = "") -> bool:
        """
        Alternative method: Send image via /messages/media/image endpoint
        """
        try:
            if not os.path.exists(image_file_path):
                print(f"❌ Image file not found: {image_file_path}")
                return False
            
            file_size = os.path.getsize(image_file_path)
            url = f"{self.base_url}/messages/media/image"
            
            print(f"📷 Sending image message (Media Endpoint) to {phone_number}")
            print(f"   File: {image_file_path} ({file_size} bytes)")
            print(f"   Caption: {caption}")
            print(f"   URL: {url}")
            
            # Remove Content-Type header for multipart
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            data = {
                "to": phone_number
            }
            
            if caption:
                data["caption"] = caption
            
            print(f"📷 Data: {data}")
            print(f"📷 Headers: {headers}")
            
            # Prepare multipart form data
            with open(image_file_path, "rb") as image_file:
                files = {
                    "media": (os.path.basename(image_file_path), image_file.read(), "image/webp")
                }
                
                print(f"📷 Files: media file ({len(files['media'][1])} bytes)")
                
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(url, headers=headers, data=data, files=files)
                        
                        print(f"📷 Response status: {response.status_code}")
                        print(f"📷 Response body: {response.text}")
                        
                        if response.status_code == 200:
                            print(f"✅ Image message sent via Media Endpoint to {phone_number}")
                            return True
                        else:
                            print(f"❌ Failed to send image message via Media Endpoint: {response.status_code}")
                            return False
                except Exception as http_err:
                    print(f"❌ HTTP request failed: {str(http_err)}")
                    print(f"❌ HTTP error type: {type(http_err)}")
                    raise http_err
                        
        except Exception as e:
            print(f"❌ Send image message error (Media Endpoint): {str(e)} | File: {image_file_path}")
            return False
    
    async def send_image_message_n8n_style(self, phone_number: str, image_file_path: str, caption: str = "") -> bool:
        """
        Send image using n8n-style approach: /messages/media/image?to=PHONE with binary body
        Based on working n8n implementation pattern
        """
        try:
            if not os.path.exists(image_file_path):
                print(f"❌ Image file not found: {image_file_path}")
                return False
            
            file_size = os.path.getsize(image_file_path)
            
            # n8n-style URL with query parameters
            url = f"{self.base_url}/messages/media/image"
            
            print(f"📷 Sending image message (n8n style) to {phone_number}")
            print(f"   File: {image_file_path} ({file_size} bytes)")
            print(f"   Caption: {caption}")
            print(f"   URL: {url}")
            
            # Headers with authentication but no Content-Type (let httpx auto-detect)
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            # Query parameters (n8n style)
            params = {
                "to": phone_number
            }
            
            if caption:
                params["caption"] = caption
            
            print(f"📷 Params: {params}")
            print(f"📷 Headers: {headers}")
            
            # Read file as binary data (n8n style)
            with open(image_file_path, "rb") as image_file:
                file_data = image_file.read()
                
                print(f"📷 Binary data size: {len(file_data)} bytes")
                
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        # Send binary data as body with query parameters (n8n approach)
                        response = await client.post(
                            url, 
                            headers=headers, 
                            params=params,
                            content=file_data
                        )
                        
                        print(f"📷 Response status: {response.status_code}")
                        print(f"📷 Response body: {response.text}")
                        
                        if response.status_code == 200:
                            print(f"✅ Image message sent via n8n style to {phone_number}")
                            return True
                        else:
                            print(f"❌ Failed to send image message via n8n style: {response.status_code}")
                            return False
                except Exception as http_err:
                    print(f"❌ HTTP request failed: {str(http_err)}")
                    print(f"❌ HTTP error type: {type(http_err)}")
                    raise http_err
                        
        except Exception as e:
            print(f"❌ Send image message error (n8n style): {str(e)} | File: {image_file_path}")
            return False
    
    async def send_gif_message(self, phone_number: str, gif_file_path: str, caption: str = "") -> bool:
        """
        Send an animated GIF message via WhatsApp using WHAPI.cloud API
        """
        try:
            if not os.path.exists(gif_file_path):
                print(f"❌ GIF file not found: {gif_file_path}")
                return False
            
            file_size = os.path.getsize(gif_file_path)
            url = f"{self.base_url}/messages/gif"
            
            print(f"🎬 Sending GIF message (Base64) to {phone_number}")
            print(f"   File: {gif_file_path} ({file_size} bytes)")
            print(f"   Caption: {caption}")
            print(f"   URL: {url}")
            
            # Read GIF file and encode as base64
            with open(gif_file_path, "rb") as gif_file:
                gif_data = gif_file.read()
                gif_base64 = base64.b64encode(gif_data).decode()
            
            print(f"   Base64 length: {len(gif_base64)} characters")
            
            # Payload format for GIF messages
            payload = {
                "to": phone_number,
                "media": f"data:image/gif;base64,{gif_base64}"
            }
            
            if caption:
                payload["caption"] = caption
            
            print(f"🎬 Payload: {{'to': '{phone_number}', 'media': 'data:image/gif;base64,[{len(gif_base64)} chars]', 'caption': '{caption}'}}")
            print(f"🎬 Headers: {self.headers}")
            
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for GIFs
                    response = await client.post(url, headers=self.headers, json=payload)
                    
                    print(f"🎬 Response status: {response.status_code}")
                    print(f"🎬 Response body: {response.text}")
                    
                    if response.status_code == 200:
                        print(f"✅ GIF message sent via Base64 to {phone_number}")
                        return True
                    else:
                        print(f"❌ Failed to send GIF message via Base64: {response.status_code}")
                        return False
            except Exception as http_err:
                print(f"❌ HTTP request failed: {str(http_err)}")
                print(f"❌ HTTP error type: {type(http_err)}")
                raise http_err
                    
        except Exception as e:
            print(f"❌ Send GIF message error (Base64): {str(e)} | File: {gif_file_path}")
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