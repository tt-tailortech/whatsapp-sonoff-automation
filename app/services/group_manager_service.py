#!/usr/bin/env python3
"""
Group Manager Service
Automatically manages Google Drive folders and member metadata for WhatsApp groups
"""

import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

class GroupManagerService:
    def __init__(self):
        """Initialize Google Drive service for group management"""
        self.service = None
        self.alarm_system_folder_id = None
        self.member_databases_folder_id = None
        self._initialize_google_drive()
    
    def _initialize_google_drive(self):
        """Initialize Google Drive API connection"""
        try:
            credentials_path = "./google_drive_credentials.json"
            if not os.path.exists(credentials_path):
                print("❌ Google Drive credentials not found")
                return False
            
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            
            # Get alarm_system folder ID
            parent_folder_id = "1AKWPm5BM0N3a1l2lzUuDaOYl5Ut7PGN1"  # TT_projects folder
            
            # Find alarm_system folder
            alarm_results = self.service.files().list(
                q=f"'{parent_folder_id}' in parents and name='alarm_system' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if alarm_results.get('files'):
                self.alarm_system_folder_id = alarm_results['files'][0]['id']
                print(f"✅ Found alarm_system folder: {self.alarm_system_folder_id}")
                
                # Find member_databases folder
                member_db_results = self.service.files().list(
                    q=f"'{self.alarm_system_folder_id}' in parents and name='member_databases' and mimeType='application/vnd.google-apps.folder'",
                    fields="files(id, name)"
                ).execute()
                
                if member_db_results.get('files'):
                    self.member_databases_folder_id = member_db_results['files'][0]['id']
                    print(f"✅ Found member_databases folder: {self.member_databases_folder_id}")
                    return True
            
            print("❌ Could not find required Google Drive folders")
            return False
            
        except Exception as e:
            print(f"❌ Google Drive initialization error: {str(e)}")
            return False
    
    def sanitize_folder_name(self, group_name: str) -> str:
        """
        Sanitize WhatsApp group name for use as Google Drive folder name
        """
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^\w\s-]', '', group_name)
        sanitized = re.sub(r'[\s]+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        # Limit length to 100 characters
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "Unknown_Group"
        
        return sanitized
    
    async def ensure_group_folder_exists(self, group_chat_id: str, group_name: str, sender_phone: str, sender_name: str) -> bool:
        """
        Ensure group folder exists in Google Drive, create if not found
        Returns True if folder exists or was created successfully
        """
        if not self.service or not self.member_databases_folder_id:
            print("❌ Google Drive service not initialized")
            return False
        
        try:
            # Sanitize group name for folder
            folder_name = self.sanitize_folder_name(group_name)
            
            print(f"🔍 Checking for group folder: {folder_name}")
            
            # Check if group folder already exists
            existing_folders = self.service.files().list(
                q=f"'{self.member_databases_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if existing_folders.get('files'):
                group_folder_id = existing_folders['files'][0]['id']
                print(f"✅ Group folder already exists: {folder_name} ({group_folder_id})")
                return True
            
            # Create new group folder
            print(f"🏗️ Creating new group folder: {folder_name}")
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.member_databases_folder_id]
            }
            
            group_folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            group_folder_id = group_folder.get('id')
            print(f"✅ Created group folder: {folder_name} ({group_folder_id})")
            
            # Create initial member metadata file
            await self._create_initial_member_metadata(
                group_folder_id, 
                group_chat_id, 
                group_name, 
                folder_name,
                sender_phone, 
                sender_name
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error ensuring group folder exists: {str(e)}")
            return False
    
    async def _create_initial_member_metadata(self, group_folder_id: str, group_chat_id: str, 
                                            group_name: str, folder_name: str, 
                                            sender_phone: str, sender_name: str):
        """
        Create initial member metadata file for new group
        """
        try:
            print(f"📄 Creating initial member metadata for {group_name}")
            
            # Create initial metadata structure
            initial_metadata = {
                "group_id": group_chat_id,
                "group_name": group_name,
                "folder_name": folder_name,
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "admins": [sender_phone],  # First person becomes admin
                "members": {
                    sender_phone: {
                        "name": sender_name,
                        "alias": [],
                        "address": {
                            "street": "",
                            "apartment": "",
                            "floor": "",
                            "neighborhood": "",
                            "city": "",
                            "coordinates": {"lat": None, "lng": None}
                        },
                        "contacts": {
                            "primary": sender_phone,
                            "emergency": "",
                            "family": ""
                        },
                        "medical": {
                            "conditions": [],
                            "medications": [],
                            "allergies": [],
                            "blood_type": ""
                        },
                        "emergency_info": {
                            "is_admin": True,
                            "response_role": "coordinator",
                            "evacuation_assistance": False,
                            "special_needs": []
                        },
                        "metadata": {
                            "joined_date": datetime.now().isoformat(),
                            "last_active": datetime.now().isoformat(),
                            "data_version": "1.0"
                        }
                    }
                },
                "group_settings": {
                    "emergency_alerts_enabled": True,
                    "auto_member_detection": True,
                    "require_admin_approval": False
                }
            }
            
            # Convert to JSON
            json_content = json.dumps(initial_metadata, indent=2, ensure_ascii=False)
            
            # Create file in Google Drive
            file_metadata = {
                'name': f'{folder_name}_members.json',
                'parents': [group_folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(json_content.encode('utf-8')),
                mimetype='application/json'
            )
            
            member_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name'
            ).execute()
            
            print(f"✅ Created member metadata file: {member_file.get('name')} ({member_file.get('id')})")
            
            # Log the creation
            await self._log_group_creation(group_chat_id, group_name, folder_name, sender_name)
            
            return member_file.get('id')
            
        except Exception as e:
            print(f"❌ Error creating initial member metadata: {str(e)}")
            return None
    
    async def _log_group_creation(self, group_chat_id: str, group_name: str, 
                                 folder_name: str, creator_name: str):
        """
        Log group creation to logs folder
        """
        try:
            # Find logs folder
            logs_results = self.service.files().list(
                q=f"'{self.alarm_system_folder_id}' in parents and name='logs' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if not logs_results.get('files'):
                print("⚠️ Logs folder not found, skipping log creation")
                return
            
            logs_folder_id = logs_results['files'][0]['id']
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "group_created",
                "group_id": group_chat_id,
                "group_name": group_name,
                "folder_name": folder_name,
                "creator": creator_name,
                "details": f"New WhatsApp group '{group_name}' added to member database system"
            }
            
            # Create log file
            log_filename = f"group_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            log_content = json.dumps(log_entry, indent=2, ensure_ascii=False)
            
            file_metadata = {
                'name': log_filename,
                'parents': [logs_folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(log_content.encode('utf-8')),
                mimetype='application/json'
            )
            
            log_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"📝 Logged group creation: {log_filename}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create log entry: {str(e)}")
    
    async def get_group_member_data(self, group_chat_id: str, group_name: str) -> Optional[Dict[str, Any]]:
        """
        Get member data for a specific group
        Returns None if group not found
        """
        if not self.service or not self.member_databases_folder_id:
            return None
        
        try:
            folder_name = self.sanitize_folder_name(group_name)
            
            # Find group folder
            group_folders = self.service.files().list(
                q=f"'{self.member_databases_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if not group_folders.get('files'):
                return None
            
            group_folder_id = group_folders['files'][0]['id']
            
            # Find member JSON file
            member_files = self.service.files().list(
                q=f"'{group_folder_id}' in parents and name='{folder_name}_members.json'",
                fields="files(id, name)"
            ).execute()
            
            if not member_files.get('files'):
                return None
            
            member_file_id = member_files['files'][0]['id']
            
            # Read file content
            file_content = self.service.files().get_media(fileId=member_file_id).execute()
            member_data = json.loads(file_content.decode('utf-8'))
            
            return member_data
            
        except Exception as e:
            print(f"❌ Error getting group member data: {str(e)}")
            return None
    
    def is_group_message(self, chat_id: str) -> bool:
        """
        Check if message is from a WhatsApp group
        Group chat IDs end with @g.us
        """
        return chat_id.endswith("@g.us")


# Test function
async def test_group_manager():
    """Test the group manager service"""
    print("🧪 Testing Group Manager Service")
    print("=" * 50)
    
    manager = GroupManagerService()
    
    # Test cases
    test_groups = [
        {
            "group_chat_id": "120363400467632358@g.us",
            "group_name": "Las Condes Norte",
            "sender_phone": "56940035815",
            "sender_name": "Waldo Rodriguez"
        },
        {
            "group_chat_id": "120363400467632359@g.us", 
            "group_name": "Providencia Sur - Emergencias",
            "sender_phone": "56987654321",
            "sender_name": "Ana Martinez"
        }
    ]
    
    for test_group in test_groups:
        print(f"\n🧪 Testing group: {test_group['group_name']}")
        
        # Test folder creation
        result = await manager.ensure_group_folder_exists(
            test_group["group_chat_id"],
            test_group["group_name"], 
            test_group["sender_phone"],
            test_group["sender_name"]
        )
        
        if result:
            print(f"✅ Group setup successful")
            
            # Test data retrieval
            member_data = await manager.get_group_member_data(
                test_group["group_chat_id"],
                test_group["group_name"]
            )
            
            if member_data:
                print(f"✅ Retrieved member data: {len(member_data.get('members', {}))} members")
            else:
                print(f"❌ Could not retrieve member data")
        else:
            print(f"❌ Group setup failed")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_group_manager())