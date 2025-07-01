#!/usr/bin/env python3
"""
Group Icon Service
Automatically generates and sets safe neighborhood icons for WhatsApp groups
"""

import os
import aiohttp
import asyncio
from typing import Optional, Tuple
from datetime import datetime
import tempfile

class GroupIconService:
    def __init__(self):
        """Initialize the Group Icon Service"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.whapi_token = os.getenv("WHAPI_TOKEN")
        self.whapi_base_url = os.getenv("WHAPI_BASE_URL", "https://gate.whapi.cloud")
        
    async def check_and_create_group_icon(self, group_chat_id: str, group_name: str) -> bool:
        """
        Check if group has an icon, if not, create a safe neighborhood icon
        
        Returns True if icon was set or already exists, False if failed
        """
        try:
            print(f"🖼️ Checking group icon for: {group_name} ({group_chat_id})")
            
            # Check if group already has an icon
            has_icon = await self._check_group_has_icon(group_chat_id)
            
            if has_icon:
                print(f"✅ Group {group_name} already has an icon")
                return True
            
            print(f"🎨 Group {group_name} has no icon, generating safe neighborhood image...")
            
            # Generate neighborhood icon
            icon_path = await self._generate_neighborhood_icon(group_name)
            
            if not icon_path:
                print(f"❌ Failed to generate icon for {group_name}")
                return False
            
            # Set the group icon
            success = await self._set_group_icon(group_chat_id, icon_path)
            
            # Cleanup temporary file
            try:
                os.remove(icon_path)
                print(f"🧹 Cleaned up temporary icon file")
            except:
                pass
            
            if success:
                print(f"✅ Successfully set group icon for {group_name}")
                return True
            else:
                print(f"❌ Failed to set group icon for {group_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking/creating group icon: {str(e)}")
            return False
    
    async def _check_group_has_icon(self, group_chat_id: str) -> bool:
        """Check if the WhatsApp group already has an icon"""
        try:
            if not self.whapi_token:
                print("⚠️ WHAPI token not configured, cannot check group icon")
                return True  # Assume it has an icon to avoid errors
            
            headers = {
                "Authorization": f"Bearer {self.whapi_token}",
                "Content-Type": "application/json"
            }
            
            # Get group info from WHAPI
            url = f"{self.whapi_base_url}/groups/{group_chat_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        group_info = await response.json()
                        
                        # Check if group has profile picture/icon
                        has_icon = group_info.get("picture") is not None
                        print(f"🔍 Group icon status: {'Has icon' if has_icon else 'No icon'}")
                        return has_icon
                    else:
                        print(f"⚠️ Could not get group info: {response.status}")
                        return True  # Assume it has an icon to avoid errors
                        
        except Exception as e:
            print(f"❌ Error checking group icon: {str(e)}")
            return True  # Assume it has an icon to avoid errors
    
    async def _generate_neighborhood_icon(self, group_name: str) -> Optional[str]:
        """Generate a safe neighborhood icon using OpenAI DALL-E"""
        try:
            if not self.openai_api_key:
                print("❌ OpenAI API key not configured")
                return None
            
            # Create neighborhood-specific prompt
            prompt = f"""Create a safe, friendly neighborhood community icon for a WhatsApp group called "{group_name}".

Style: Modern, clean, cartoon illustration style
Format: Square, optimized for WhatsApp group icon (clear at small sizes)
Colors: Warm and welcoming (soft blues, greens, gentle oranges)
Theme: Chilean residential community with safety focus

Elements to include:
- Small houses with Chilean architectural style
- Trees and green spaces
- Subtle emergency/safety symbols (small emergency vehicle, safety signs)
- Mountains in background (Chilean landscape)
- Community feeling (people, pathways, gathering spaces)
- Sense of security and neighborliness

Mood: Safe, welcoming, community-oriented, professional but friendly
Requirements: High contrast, clear details, recognizable even at small WhatsApp icon size"""

            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # Use DALL-E 2 for cost efficiency (good enough for icons)
            payload = {
                "model": "dall-e-2",
                "prompt": prompt,
                "n": 1,
                "size": "512x512",  # Good size for WhatsApp icons
                "response_format": "url"
            }
            
            print(f"🎨 Generating neighborhood icon with DALL-E 2...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        image_url = result['data'][0]['url']
                        
                        print(f"✅ Icon generated successfully")
                        
                        # Download and save temporarily
                        async with session.get(image_url) as img_response:
                            if img_response.status == 200:
                                image_data = await img_response.read()
                                
                                # Save to temporary file
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                                    temp_file.write(image_data)
                                    temp_path = temp_file.name
                                
                                print(f"💾 Icon saved temporarily: {temp_path}")
                                return temp_path
                            else:
                                print(f"❌ Failed to download generated image")
                                return None
                    else:
                        error_text = await response.text()
                        print(f"❌ DALL-E API error: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error generating neighborhood icon: {str(e)}")
            return None
    
    async def _set_group_icon(self, group_chat_id: str, icon_path: str) -> bool:
        """Set the group icon using WHAPI"""
        try:
            if not self.whapi_token:
                print("⚠️ WHAPI token not configured, cannot set group icon")
                return False
            
            # Try multiple methods for setting group picture
            
            # Method 1: Direct file upload (most common)
            success = await self._try_set_icon_file_upload(group_chat_id, icon_path)
            if success:
                return True
            
            # Method 2: Base64 encoded (fallback)
            success = await self._try_set_icon_base64(group_chat_id, icon_path)
            if success:
                return True
            
            print(f"❌ All methods failed to set group icon")
            return False
                            
        except Exception as e:
            print(f"❌ Error setting group icon: {str(e)}")
            return False
    
    async def _try_set_icon_file_upload(self, group_chat_id: str, icon_path: str) -> bool:
        """Try setting icon via file upload"""
        try:
            headers = {
                "Authorization": f"Bearer {self.whapi_token}"
            }
            
            url = f"{self.whapi_base_url}/groups/{group_chat_id}/picture"
            print(f"📤 Method 1: File upload to {url}")
            
            # Use aiofiles for proper async file handling
            with open(icon_path, 'rb') as icon_file:
                data = aiohttp.FormData()
                data.add_field('picture', icon_file, filename='icon.png', content_type='image/png')
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url, 
                        headers=headers, 
                        data=data,
                        timeout=30
                    ) as response:
                        
                        response_text = await response.text()
                        print(f"📡 File upload response: {response.status} - {response_text}")
                        
                        if response.status == 200:
                            print(f"✅ Group icon set via file upload")
                            return True
                        elif response.status == 403:
                            print(f"🔒 Permission denied - bot may not be admin of the group")
                            return False
                        elif response.status == 404:
                            print(f"❓ Group not found or endpoint not available")
                            return False
                        else:
                            print(f"❌ File upload failed: {response.status}")
                            return False
                            
        except Exception as e:
            print(f"❌ File upload method failed: {str(e)}")
            return False
    
    async def _try_set_icon_base64(self, group_chat_id: str, icon_path: str) -> bool:
        """Try setting icon via base64 encoding"""
        try:
            import base64
            
            # Read and encode image
            with open(icon_path, 'rb') as icon_file:
                image_data = icon_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.whapi_token}",
                "Content-Type": "application/json"
            }
            
            # Try different endpoint formats
            endpoints_to_try = [
                f"{self.whapi_base_url}/groups/{group_chat_id}/picture",
                f"{self.whapi_base_url}/groups/{group_chat_id}/photo",
                f"{self.whapi_base_url}/groups/picture",
            ]
            
            for url in endpoints_to_try:
                print(f"📤 Method 2: Base64 to {url}")
                
                payload = {
                    "group_id": group_chat_id,
                    "picture": f"data:image/png;base64,{base64_image}"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url, 
                        headers=headers, 
                        json=payload,
                        timeout=30
                    ) as response:
                        
                        response_text = await response.text()
                        print(f"📡 Base64 response ({url}): {response.status} - {response_text}")
                        
                        if response.status == 200:
                            print(f"✅ Group icon set via base64")
                            return True
                        elif response.status == 403:
                            print(f"🔒 Permission denied - bot may not be admin")
                            continue  # Try next endpoint
                        else:
                            continue  # Try next endpoint
            
            return False
                            
        except Exception as e:
            print(f"❌ Base64 method failed: {str(e)}")
            return False


async def test_group_icon_service():
    """Test the group icon service"""
    print("🧪 Testing Group Icon Service")
    print("=" * 50)
    
    service = GroupIconService()
    
    # Test with a fake group (won't actually set icon)
    test_group_id = "120363400467632358@g.us"
    test_group_name = "Test Neighborhood Group"
    
    print(f"🧪 Testing icon generation for: {test_group_name}")
    
    # Just test the icon generation part
    icon_path = await service._generate_neighborhood_icon(test_group_name)
    
    if icon_path:
        print(f"✅ Icon generation test successful: {icon_path}")
        print(f"📊 File size: {os.path.getsize(icon_path)} bytes")
        
        # Cleanup
        os.remove(icon_path)
        print(f"🧹 Test icon cleaned up")
        return True
    else:
        print(f"❌ Icon generation test failed")
        return False

if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_group_icon_service())
    print(f"\nTest result: {'SUCCESS' if result else 'FAILURE'}")