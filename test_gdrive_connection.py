#!/usr/bin/env python3
"""
Test Google Drive connection and create folder structure
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io

def test_google_drive_connection():
    """Test Google Drive API connection and create folder structure"""
    
    print("🔍 Testing Google Drive Connection...")
    print("=" * 60)
    
    try:
        # Load credentials
        credentials_path = "./google_drive_credentials.json"
        if not os.path.exists(credentials_path):
            print("❌ Credentials file not found!")
            return False
        
        print("✅ Loading credentials...")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build service
        print("🔧 Building Google Drive service...")
        service = build('drive', 'v3', credentials=credentials)
        
        # Test connection by listing files in parent folder
        parent_folder_id = "1AKWPm5BM0N3a1l2lzUuDaOYl5Ut7PGN1"
        
        print(f"📂 Testing access to parent folder: {parent_folder_id}")
        results = service.files().list(
            q=f"'{parent_folder_id}' in parents",
            pageSize=10,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        
        items = results.get('files', [])
        print(f"✅ Successfully accessed folder! Found {len(items)} items:")
        for item in items:
            print(f"   📁 {item['name']} (ID: {item['id']})")
        
        # Create alarm_system folder
        print("\n🏗️ Creating alarm_system folder structure...")
        
        # Check if alarm_system folder already exists
        existing_folders = service.files().list(
            q=f"'{parent_folder_id}' in parents and name='alarm_system' and mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)"
        ).execute()
        
        if existing_folders.get('files'):
            alarm_folder_id = existing_folders['files'][0]['id']
            print(f"✅ alarm_system folder already exists: {alarm_folder_id}")
        else:
            # Create alarm_system folder
            folder_metadata = {
                'name': 'alarm_system',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            alarm_folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            alarm_folder_id = alarm_folder.get('id')
            print(f"✅ Created alarm_system folder: {alarm_folder_id}")
        
        # Create subfolders
        subfolders = [
            'member_databases',
            'backups', 
            'logs'
        ]
        
        created_folders = {}
        
        for folder_name in subfolders:
            # Check if subfolder exists
            existing_subfolders = service.files().list(
                q=f"'{alarm_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if existing_subfolders.get('files'):
                subfolder_id = existing_subfolders['files'][0]['id']
                print(f"✅ {folder_name} subfolder already exists: {subfolder_id}")
            else:
                subfolder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [alarm_folder_id]
                }
                
                subfolder = service.files().create(
                    body=subfolder_metadata,
                    fields='id'
                ).execute()
                
                subfolder_id = subfolder.get('id')
                print(f"✅ Created {folder_name} subfolder: {subfolder_id}")
            
            created_folders[folder_name] = subfolder_id
        
        # Create a test member database file
        print("\n📄 Creating test member database file...")
        
        test_member_data = {
            "group_id": "120363400467632358@g.us",
            "group_name": "TEST_ALARM",
            "last_updated": "2024-06-29T15:30:00Z",
            "admins": ["56940035815"],
            "members": {
                "56940035815": {
                    "name": "Waldo Rodriguez",
                    "alias": ["waldo", "wal"],
                    "address": {
                        "street": "Av. Las Condes 2024",
                        "apartment": "Apt 15B",
                        "floor": "15",
                        "neighborhood": "Las Condes",
                        "city": "Santiago",
                        "coordinates": {"lat": -33.123, "lng": -70.456}
                    },
                    "contacts": {
                        "primary": "+56940035815",
                        "emergency": "+56912345678",
                        "family": "Ana Rodriguez +56987654321"
                    },
                    "medical": {
                        "conditions": ["diabetes tipo 1"],
                        "medications": ["insulin"],
                        "allergies": ["penicillin"],
                        "blood_type": "O+"
                    },
                    "emergency_info": {
                        "is_admin": True,
                        "response_role": "coordinator",
                        "evacuation_assistance": False,
                        "special_needs": []
                    },
                    "metadata": {
                        "joined_date": "2024-01-15",
                        "last_active": "2024-06-29",
                        "data_version": "1.0"
                    }
                }
            }
        }
        
        # Convert to JSON string
        json_content = json.dumps(test_member_data, indent=2, ensure_ascii=False)
        
        # Create file in Google Drive
        file_metadata = {
            'name': 'TEST_ALARM_members.json',
            'parents': [created_folders['member_databases']]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(json_content.encode('utf-8')),
            mimetype='application/json'
        )
        
        test_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name'
        ).execute()
        
        print(f"✅ Created test member database: {test_file.get('name')} (ID: {test_file.get('id')})")
        
        # Test reading the file back
        print("\n📖 Testing file read operation...")
        file_content = service.files().get_media(fileId=test_file.get('id')).execute()
        read_data = json.loads(file_content.decode('utf-8'))
        
        print(f"✅ Successfully read member data for group: {read_data['group_name']}")
        print(f"   👥 Members: {len(read_data['members'])}")
        print(f"   👤 First member: {list(read_data['members'].values())[0]['name']}")
        
        print("\n🎉 Google Drive Integration Test SUCCESSFUL!")
        print("=" * 60)
        print("✅ Connection established")
        print("✅ Folder structure created")
        print("✅ File operations working")
        print("✅ JSON data handling confirmed")
        print("\n🚀 Ready to implement member database system!")
        
        return {
            'success': True,
            'alarm_folder_id': alarm_folder_id,
            'subfolders': created_folders,
            'test_file_id': test_file.get('id')
        }
        
    except Exception as e:
        print(f"❌ Google Drive test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    result = test_google_drive_connection()
    if result:
        print(f"\n📋 Folder IDs for reference:")
        print(f"Main folder: {result.get('alarm_folder_id')}")
        for name, folder_id in result.get('subfolders', {}).items():
            print(f"{name}: {folder_id}")