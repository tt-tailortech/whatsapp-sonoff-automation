#!/usr/bin/env python3
"""
Backup and Recovery Service
Automated backup and recovery system for member data with versioning
"""

import json
import os
import zipfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

class BackupService:
    def __init__(self):
        """Initialize backup service"""
        self.service = None
        self.backup_folder_id = None
        self._initialize_google_drive()
    
    def _initialize_google_drive(self):
        """Initialize Google Drive API connection for backups"""
        try:
            from app.services.group_manager_service import GroupManagerService
            group_manager = GroupManagerService()
            
            self.service = group_manager.service
            
            if self.service:
                self._ensure_backup_folder()
                print("💾 Backup service initialized with Google Drive")
            else:
                print("⚠️ Google Drive not available, using local backup only")
                
        except Exception as e:
            print(f"⚠️ Could not initialize Google Drive for backup: {str(e)}")
            print("📁 Falling back to local file backup system")
    
    def _ensure_backup_folder(self):
        """Ensure backup folder exists in Google Drive"""
        try:
            # Find alarm_system folder first
            parent_folder_id = "1AKWPm5BM0N3a1l2lzUuDaOYl5Ut7PGN1"  # TT_projects folder
            
            # Find alarm_system folder
            alarm_results = self.service.files().list(
                q=f"'{parent_folder_id}' in parents and name='alarm_system' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if not alarm_results.get('files'):
                print("❌ alarm_system folder not found for backups")
                return
            
            alarm_folder_id = alarm_results['files'][0]['id']
            
            # Check if backups folder exists
            backup_results = self.service.files().list(
                q=f"'{alarm_folder_id}' in parents and name='backups' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if backup_results.get('files'):
                self.backup_folder_id = backup_results['files'][0]['id']
                print(f"✅ Found backups folder: {self.backup_folder_id}")
            else:
                # Create backups folder
                folder_metadata = {
                    'name': 'backups',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [alarm_folder_id]
                }
                
                backup_folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                self.backup_folder_id = backup_folder.get('id')
                print(f"✅ Created backups folder: {self.backup_folder_id}")
                
        except Exception as e:
            print(f"❌ Error ensuring backup folder: {str(e)}")
    
    async def create_full_system_backup(self, backup_name: str = None) -> Tuple[bool, str]:
        """
        Create a full backup of all member data
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            (success: bool, backup_path_or_error: str)
        """
        try:
            if not backup_name:
                backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            print(f"💾 Creating full system backup: {backup_name}")
            
            # Initialize services
            from app.services.group_manager_service import GroupManagerService
            group_manager = GroupManagerService()
            
            # Get all group data
            backup_data = {
                "backup_info": {
                    "created_at": datetime.now().isoformat(),
                    "backup_name": backup_name,
                    "backup_type": "full_system",
                    "version": "1.0"
                },
                "groups": {},
                "system_info": {
                    "total_groups": 0,
                    "total_members": 0,
                    "encryption_used": False
                }
            }
            
            # This is a simplified version - in production, you'd enumerate all groups
            # For now, we'll show the structure for known groups
            test_groups = [
                {
                    "group_chat_id": "120363400467632358@g.us",
                    "group_name": "TEST_ALARM"
                }
            ]
            
            total_members = 0
            total_groups = 0
            
            for group_info in test_groups:
                try:
                    group_data = await group_manager.get_group_member_data(
                        group_info["group_chat_id"], 
                        group_info["group_name"]
                    )
                    
                    if group_data:
                        backup_data["groups"][group_info["group_chat_id"]] = {
                            "group_name": group_info["group_name"],
                            "data": group_data,
                            "backup_timestamp": datetime.now().isoformat()
                        }
                        
                        total_groups += 1
                        total_members += len(group_data.get("members", {}))
                        
                        # Check if encryption was used
                        if group_data.get("encryption_info", {}).get("encrypted"):
                            backup_data["system_info"]["encryption_used"] = True
                        
                        print(f"✅ Backed up group: {group_info['group_name']} ({len(group_data.get('members', {}))} members)")
                
                except Exception as e:
                    print(f"⚠️ Could not backup group {group_info['group_name']}: {str(e)}")
            
            # Update system info
            backup_data["system_info"]["total_groups"] = total_groups
            backup_data["system_info"]["total_members"] = total_members
            
            # Create backup file
            backup_content = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            # Save backup
            if self.service and self.backup_folder_id:
                backup_path = await self._save_backup_to_drive(backup_name, backup_content)
            else:
                backup_path = await self._save_backup_locally(backup_name, backup_content)
            
            print(f"✅ Full system backup created: {backup_path}")
            print(f"📊 Backup contains: {total_groups} groups, {total_members} members")
            
            # Log the backup creation
            try:
                from app.services.audit_service import AuditService
                audit_service = AuditService()
                await audit_service.log_system_event(
                    event_type="backup_created",
                    description=f"Full system backup created: {backup_name}",
                    system_component="backup_service",
                    success=True,
                    additional_info={
                        "backup_name": backup_name,
                        "total_groups": total_groups,
                        "total_members": total_members,
                        "encryption_used": backup_data["system_info"]["encryption_used"]
                    }
                )
            except Exception as e:
                print(f"⚠️ Could not log backup creation: {str(e)}")
            
            return True, backup_path
            
        except Exception as e:
            error_msg = f"Error creating backup: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    async def create_group_backup(self, group_chat_id: str, group_name: str) -> Tuple[bool, str]:
        """
        Create a backup of a specific group
        
        Args:
            group_chat_id: WhatsApp group ID
            group_name: Group name
            
        Returns:
            (success: bool, backup_path_or_error: str)
        """
        try:
            backup_name = f"group_backup_{group_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"💾 Creating group backup: {backup_name}")
            
            from app.services.group_manager_service import GroupManagerService
            group_manager = GroupManagerService()
            
            # Get group data
            group_data = await group_manager.get_group_member_data(group_chat_id, group_name)
            
            if not group_data:
                return False, f"No data found for group: {group_name}"
            
            # Create backup structure
            backup_data = {
                "backup_info": {
                    "created_at": datetime.now().isoformat(),
                    "backup_name": backup_name,
                    "backup_type": "single_group",
                    "group_id": group_chat_id,
                    "group_name": group_name,
                    "version": "1.0"
                },
                "group_data": group_data
            }
            
            backup_content = json.dumps(backup_data, indent=2, ensure_ascii=False)
            
            # Save backup
            if self.service and self.backup_folder_id:
                backup_path = await self._save_backup_to_drive(backup_name, backup_content)
            else:
                backup_path = await self._save_backup_locally(backup_name, backup_content)
            
            print(f"✅ Group backup created: {backup_path}")
            print(f"📊 Backup contains: {len(group_data.get('members', {}))} members")
            
            return True, backup_path
            
        except Exception as e:
            error_msg = f"Error creating group backup: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    async def restore_from_backup(self, backup_path: str, restore_type: str = "full") -> Tuple[bool, str]:
        """
        Restore data from a backup
        
        Args:
            backup_path: Path to backup file
            restore_type: "full" or "selective"
            
        Returns:
            (success: bool, message: str)
        """
        try:
            print(f"🔄 Restoring from backup: {backup_path}")
            
            # Load backup data
            if backup_path.startswith("http") or backup_path in ["drive", "google_drive"]:
                backup_content = await self._load_backup_from_drive(backup_path)
            else:
                backup_content = await self._load_backup_locally(backup_path)
            
            if not backup_content:
                return False, "Could not load backup file"
            
            backup_data = json.loads(backup_content)
            backup_info = backup_data.get("backup_info", {})
            
            print(f"📋 Backup info: {backup_info.get('backup_name', 'Unknown')} ({backup_info.get('backup_type', 'Unknown')})")
            print(f"📅 Created: {backup_info.get('created_at', 'Unknown')}")
            
            # Initialize services
            from app.services.group_manager_service import GroupManagerService
            group_manager = GroupManagerService()
            
            restored_groups = 0
            restored_members = 0
            errors = []
            
            if backup_info.get("backup_type") == "full_system":
                # Restore all groups
                groups = backup_data.get("groups", {})
                
                for group_id, group_backup in groups.items():
                    try:
                        group_name = group_backup["group_name"]
                        group_data = group_backup["data"]
                        
                        # Restore group data
                        success = await group_manager.update_group_member_data(group_id, group_name, group_data)
                        
                        if success:
                            restored_groups += 1
                            restored_members += len(group_data.get("members", {}))
                            print(f"✅ Restored group: {group_name}")
                        else:
                            errors.append(f"Failed to restore group: {group_name}")
                            
                    except Exception as e:
                        errors.append(f"Error restoring group {group_id}: {str(e)}")
                        
            elif backup_info.get("backup_type") == "single_group":
                # Restore single group
                group_data = backup_data.get("group_data")
                group_id = backup_info.get("group_id")
                group_name = backup_info.get("group_name")
                
                if group_data and group_id and group_name:
                    success = await group_manager.update_group_member_data(group_id, group_name, group_data)
                    
                    if success:
                        restored_groups = 1
                        restored_members = len(group_data.get("members", {}))
                        print(f"✅ Restored group: {group_name}")
                    else:
                        errors.append(f"Failed to restore group: {group_name}")
                else:
                    errors.append("Invalid single group backup format")
            
            # Log the restore operation
            try:
                from app.services.audit_service import AuditService
                audit_service = AuditService()
                await audit_service.log_system_event(
                    event_type="backup_restored",
                    description=f"Data restored from backup: {backup_info.get('backup_name', 'Unknown')}",
                    system_component="backup_service",
                    success=len(errors) == 0,
                    error_details="; ".join(errors) if errors else None,
                    additional_info={
                        "backup_name": backup_info.get("backup_name"),
                        "restored_groups": restored_groups,
                        "restored_members": restored_members,
                        "errors_count": len(errors)
                    }
                )
            except Exception as e:
                print(f"⚠️ Could not log restore operation: {str(e)}")
            
            if errors:
                error_summary = f"Restore completed with {len(errors)} errors: {'; '.join(errors[:3])}"
                if len(errors) > 3:
                    error_summary += f" and {len(errors) - 3} more..."
                print(f"⚠️ {error_summary}")
                return False, error_summary
            else:
                success_msg = f"Restore completed successfully: {restored_groups} groups, {restored_members} members"
                print(f"✅ {success_msg}")
                return True, success_msg
                
        except Exception as e:
            error_msg = f"Error restoring from backup: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups
        
        Returns:
            List of backup information
        """
        try:
            backups = []
            
            # List Google Drive backups
            if self.service and self.backup_folder_id:
                drive_backups = await self._list_drive_backups()
                backups.extend(drive_backups)
            
            # List local backups
            local_backups = await self._list_local_backups()
            backups.extend(local_backups)
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"❌ Error listing backups: {str(e)}")
            return []
    
    async def cleanup_old_backups(self, keep_days: int = 30) -> Tuple[int, int]:
        """
        Clean up old backups older than specified days
        
        Args:
            keep_days: Number of days to keep backups
            
        Returns:
            (cleaned_count, error_count)
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            cleaned_count = 0
            error_count = 0
            
            print(f"🧹 Cleaning up backups older than {keep_days} days (before {cutoff_date.strftime('%Y-%m-%d')})")
            
            # Get all backups
            backups = await self.list_backups()
            
            for backup in backups:
                try:
                    backup_date = datetime.fromisoformat(backup.get("created_at", ""))
                    
                    if backup_date < cutoff_date:
                        # Delete the backup
                        if backup.get("location") == "google_drive":
                            await self._delete_drive_backup(backup.get("file_id"))
                        else:
                            await self._delete_local_backup(backup.get("file_path"))
                        
                        cleaned_count += 1
                        print(f"🗑️ Deleted old backup: {backup.get('name')}")
                        
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error deleting backup {backup.get('name')}: {str(e)}")
            
            print(f"✅ Cleanup completed: {cleaned_count} backups deleted, {error_count} errors")
            return cleaned_count, error_count
            
        except Exception as e:
            print(f"❌ Error during backup cleanup: {str(e)}")
            return 0, 1
    
    async def _save_backup_to_drive(self, backup_name: str, content: str) -> str:
        """Save backup to Google Drive"""
        try:
            filename = f"{backup_name}.json"
            
            file_metadata = {
                'name': filename,
                'parents': [self.backup_folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype='application/json'
            )
            
            backup_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name'
            ).execute()
            
            return f"Google Drive: {backup_file.get('name')}"
            
        except Exception as e:
            raise Exception(f"Failed to save backup to Google Drive: {str(e)}")
    
    async def _save_backup_locally(self, backup_name: str, content: str) -> str:
        """Save backup locally"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = f"{backup_name}.json"
            file_path = os.path.join(backup_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Failed to save backup locally: {str(e)}")
    
    async def _load_backup_from_drive(self, backup_identifier: str) -> Optional[str]:
        """Load backup from Google Drive"""
        try:
            # This would implement loading from Google Drive
            # For now, return None as placeholder
            return None
            
        except Exception as e:
            print(f"❌ Error loading backup from Google Drive: {str(e)}")
            return None
    
    async def _load_backup_locally(self, file_path: str) -> Optional[str]:
        """Load backup from local file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
            
        except Exception as e:
            print(f"❌ Error loading local backup: {str(e)}")
            return None
    
    async def _list_drive_backups(self) -> List[Dict[str, Any]]:
        """List backups in Google Drive"""
        try:
            # This would implement listing Google Drive backups
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            print(f"❌ Error listing Google Drive backups: {str(e)}")
            return []
    
    async def _list_local_backups(self) -> List[Dict[str, Any]]:
        """List local backup files"""
        try:
            backups = []
            backup_dir = "backups"
            
            if os.path.exists(backup_dir):
                for filename in os.listdir(backup_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(backup_dir, filename)
                        try:
                            # Get file modification time
                            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            
                            backups.append({
                                "name": filename,
                                "file_path": file_path,
                                "location": "local",
                                "created_at": mtime.isoformat(),
                                "size": os.path.getsize(file_path)
                            })
                        except Exception as e:
                            print(f"⚠️ Error reading backup file {filename}: {str(e)}")
            
            return backups
            
        except Exception as e:
            print(f"❌ Error listing local backups: {str(e)}")
            return []
    
    async def _delete_drive_backup(self, file_id: str):
        """Delete backup from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
        except Exception as e:
            raise Exception(f"Failed to delete Google Drive backup: {str(e)}")
    
    async def _delete_local_backup(self, file_path: str):
        """Delete local backup file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise Exception(f"Failed to delete local backup: {str(e)}")


# Test function
async def test_backup_service():
    """Test backup service functionality"""
    print("🧪 Testing Backup Service")
    print("=" * 50)
    
    backup_service = BackupService()
    
    # Test full system backup
    print("\n💾 Testing full system backup...")
    success, result = await backup_service.create_full_system_backup("test_full_backup")
    
    if success:
        print(f"✅ Full backup created: {result}")
    else:
        print(f"❌ Full backup failed: {result}")
    
    # Test group backup
    print("\n💾 Testing group backup...")
    success, result = await backup_service.create_group_backup(
        "120363400467632358@g.us", "TEST_ALARM"
    )
    
    if success:
        print(f"✅ Group backup created: {result}")
    else:
        print(f"❌ Group backup failed: {result}")
    
    # Test listing backups
    print("\n📋 Testing backup listing...")
    backups = await backup_service.list_backups()
    print(f"✅ Found {len(backups)} backups:")
    for backup in backups[:3]:  # Show first 3
        print(f"   📁 {backup.get('name')} ({backup.get('location')}) - {backup.get('created_at')}")
    
    print("\n✅ Backup service tests completed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_backup_service())