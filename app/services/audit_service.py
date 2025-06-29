#!/usr/bin/env python3
"""
Audit Service
Tracks all member data changes, emergency events, and system activities with timestamps
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from googleapiclient.http import MediaIoBaseUpload
import io

class AuditService:
    def __init__(self):
        """Initialize audit service"""
        self.service = None
        self.audit_folder_id = None
        self._initialize_google_drive()
    
    def _initialize_google_drive(self):
        """Initialize Google Drive API connection for audit logs"""
        try:
            # Import after ensuring Google Drive is available
            from app.services.group_manager_service import GroupManagerService
            group_manager = GroupManagerService()
            
            self.service = group_manager.service
            
            if self.service:
                # Find audit logs folder or create it
                self._ensure_audit_folder()
                print("🔍 Audit service initialized with Google Drive")
            else:
                print("⚠️ Google Drive not available, using local audit logging")
                
        except Exception as e:
            print(f"⚠️ Could not initialize Google Drive for audit: {str(e)}")
            print("📝 Falling back to local file audit logging")
    
    def _ensure_audit_folder(self):
        """Ensure audit logs folder exists in Google Drive"""
        try:
            # Find alarm_system folder first
            parent_folder_id = "1AKWPm5BM0N3a1l2lzUuDaOYl5Ut7PGN1"  # TT_projects folder
            
            # Find alarm_system folder
            alarm_results = self.service.files().list(
                q=f"'{parent_folder_id}' in parents and name='alarm_system' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if not alarm_results.get('files'):
                print("❌ alarm_system folder not found for audit logs")
                return
            
            alarm_folder_id = alarm_results['files'][0]['id']
            
            # Check if audit_logs folder exists
            audit_results = self.service.files().list(
                q=f"'{alarm_folder_id}' in parents and name='audit_logs' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            if audit_results.get('files'):
                self.audit_folder_id = audit_results['files'][0]['id']
                print(f"✅ Found audit_logs folder: {self.audit_folder_id}")
            else:
                # Create audit_logs folder
                folder_metadata = {
                    'name': 'audit_logs',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [alarm_folder_id]
                }
                
                audit_folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                self.audit_folder_id = audit_folder.get('id')
                print(f"✅ Created audit_logs folder: {self.audit_folder_id}")
                
        except Exception as e:
            print(f"❌ Error ensuring audit folder: {str(e)}")
    
    async def log_member_change(self, action: str, group_chat_id: str, group_name: str, 
                              admin_phone: str, admin_name: str, target_phone: str = None,
                              target_name: str = None, field_changed: str = None, 
                              old_value: Any = None, new_value: Any = None, 
                              additional_info: Dict = None):
        """
        Log member data changes
        
        Args:
            action: Type of action (add, update, delete, import, export)
            group_chat_id: WhatsApp group ID
            group_name: Group name
            admin_phone: Phone of person making change
            admin_name: Name of person making change
            target_phone: Phone of affected member
            target_name: Name of affected member
            field_changed: Specific field that was changed
            old_value: Previous value
            new_value: New value
            additional_info: Extra context information
        """
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "audit_type": "member_change",
                "action": action,
                "group_info": {
                    "group_id": group_chat_id,
                    "group_name": group_name
                },
                "actor": {
                    "phone": admin_phone,
                    "name": admin_name,
                    "ip_address": self._get_client_ip(),
                    "user_agent": "WhatsApp Bot"
                },
                "target": {
                    "phone": target_phone,
                    "name": target_name
                } if target_phone else None,
                "change_details": {
                    "field": field_changed,
                    "old_value": self._sanitize_sensitive_data(old_value),
                    "new_value": self._sanitize_sensitive_data(new_value)
                } if field_changed else None,
                "additional_info": additional_info or {},
                "session_id": self._generate_session_id(admin_phone),
                "audit_version": "1.0"
            }
            
            await self._store_audit_log(audit_entry, "member_changes")
            print(f"📝 Audit logged: {action} by {admin_name} on {target_name or 'group'}")
            
        except Exception as e:
            print(f"❌ Error logging member change audit: {str(e)}")
    
    async def log_emergency_event(self, incident_type: str, group_chat_id: str, group_name: str,
                                reporter_phone: str, reporter_name: str, 
                                actions_taken: List[str], success_rate: float,
                                member_data_used: bool = False, additional_info: Dict = None):
        """
        Log emergency events and system responses
        
        Args:
            incident_type: Type of emergency
            group_chat_id: WhatsApp group ID
            group_name: Group name
            reporter_phone: Phone of person reporting emergency
            reporter_name: Name of person reporting emergency
            actions_taken: List of actions the system took
            success_rate: Percentage of successful actions
            member_data_used: Whether member database was used
            additional_info: Extra context information
        """
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "audit_type": "emergency_event",
                "incident_type": incident_type,
                "group_info": {
                    "group_id": group_chat_id,
                    "group_name": group_name
                },
                "reporter": {
                    "phone": reporter_phone,
                    "name": reporter_name
                },
                "system_response": {
                    "actions_taken": actions_taken,
                    "success_rate": success_rate,
                    "member_data_used": member_data_used,
                    "response_time_ms": additional_info.get("response_time_ms") if additional_info else None
                },
                "additional_info": additional_info or {},
                "audit_version": "1.0"
            }
            
            await self._store_audit_log(audit_entry, "emergency_events")
            print(f"🚨 Emergency audit logged: {incident_type} by {reporter_name}, success: {success_rate}%")
            
        except Exception as e:
            print(f"❌ Error logging emergency event audit: {str(e)}")
    
    async def log_system_event(self, event_type: str, description: str, 
                             user_phone: str = None, user_name: str = None,
                             system_component: str = "general", 
                             success: bool = True, error_details: str = None,
                             additional_info: Dict = None):
        """
        Log general system events
        
        Args:
            event_type: Type of system event (startup, error, config_change, etc.)
            description: Human-readable description
            user_phone: Phone of user if applicable
            user_name: Name of user if applicable
            system_component: Component that generated the event
            success: Whether the event was successful
            error_details: Error details if applicable
            additional_info: Extra context information
        """
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "audit_type": "system_event",
                "event_type": event_type,
                "description": description,
                "system_component": system_component,
                "success": success,
                "user": {
                    "phone": user_phone,
                    "name": user_name
                } if user_phone else None,
                "error_details": error_details,
                "additional_info": additional_info or {},
                "audit_version": "1.0"
            }
            
            await self._store_audit_log(audit_entry, "system_events")
            status = "✅" if success else "❌"
            print(f"🔧 System audit logged: {status} {event_type} - {description}")
            
        except Exception as e:
            print(f"❌ Error logging system event audit: {str(e)}")
    
    async def log_security_event(self, event_type: str, user_phone: str, user_name: str,
                               group_chat_id: str, group_name: str, action_attempted: str,
                               success: bool, reason: str = None, 
                               additional_info: Dict = None):
        """
        Log security-related events (access attempts, permission checks, etc.)
        
        Args:
            event_type: Type of security event (permission_denied, unauthorized_access, etc.)
            user_phone: Phone of user
            user_name: Name of user
            group_chat_id: WhatsApp group ID
            group_name: Group name
            action_attempted: What the user tried to do
            success: Whether the action was allowed
            reason: Reason for denial if applicable
            additional_info: Extra context information
        """
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "audit_type": "security_event",
                "event_type": event_type,
                "user": {
                    "phone": user_phone,
                    "name": user_name,
                    "ip_address": self._get_client_ip()
                },
                "group_info": {
                    "group_id": group_chat_id,
                    "group_name": group_name
                },
                "action_attempted": action_attempted,
                "success": success,
                "denial_reason": reason,
                "additional_info": additional_info or {},
                "audit_version": "1.0"
            }
            
            await self._store_audit_log(audit_entry, "security_events")
            status = "✅" if success else "🚫"
            print(f"🔒 Security audit logged: {status} {event_type} by {user_name} - {action_attempted}")
            
        except Exception as e:
            print(f"❌ Error logging security event audit: {str(e)}")
    
    async def _store_audit_log(self, audit_entry: Dict, log_category: str):
        """Store audit log entry"""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            filename = f"{log_category}_{timestamp}.json"
            
            # Convert to JSON
            json_content = json.dumps(audit_entry, indent=2, ensure_ascii=False)
            
            if self.service and self.audit_folder_id:
                # Store in Google Drive
                await self._store_in_google_drive(filename, json_content)
            else:
                # Store locally
                await self._store_locally(filename, json_content, log_category)
                
        except Exception as e:
            print(f"❌ Error storing audit log: {str(e)}")
    
    async def _store_in_google_drive(self, filename: str, content: str):
        """Store audit log in Google Drive"""
        try:
            file_metadata = {
                'name': filename,
                'parents': [self.audit_folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype='application/json'
            )
            
            self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
        except Exception as e:
            print(f"❌ Error storing audit in Google Drive: {str(e)}")
            # Fallback to local storage
            await self._store_locally(filename, content, "fallback")
    
    async def _store_locally(self, filename: str, content: str, log_category: str):
        """Store audit log locally"""
        try:
            # Create audit logs directory if it doesn't exist
            audit_dir = "audit_logs"
            category_dir = os.path.join(audit_dir, log_category)
            os.makedirs(category_dir, exist_ok=True)
            
            # Write file
            file_path = os.path.join(category_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"❌ Error storing audit locally: {str(e)}")
    
    def _sanitize_sensitive_data(self, data: Any) -> Any:
        """Sanitize sensitive data for audit logs"""
        if isinstance(data, dict):
            sanitized = data.copy()
            # Remove or mask sensitive fields
            sensitive_fields = ["password", "token", "key", "secret"]
            for field in sensitive_fields:
                if field in sanitized:
                    sanitized[field] = "***REDACTED***"
            
            # Partially mask medical data
            if "conditions" in sanitized:
                if isinstance(sanitized["conditions"], list):
                    sanitized["conditions"] = [f"{c[:3]}***" if len(c) > 3 else "***" for c in sanitized["conditions"]]
            
            return sanitized
        elif isinstance(data, str) and len(data) > 10:
            # Partially mask long strings
            return f"{data[:3]}***{data[-2:]}"
        else:
            return data
    
    def _get_client_ip(self) -> str:
        """Get client IP address (placeholder for actual implementation)"""
        return "127.0.0.1"  # In real implementation, extract from request
    
    def _generate_session_id(self, user_phone: str) -> str:
        """Generate session ID for tracking user actions"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"{user_phone}_{timestamp}"
    
    async def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get audit summary for the last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Summary of audit events
        """
        try:
            # This would query the stored audit logs
            # For now, return a placeholder summary
            summary = {
                "period_days": days,
                "total_events": 0,
                "member_changes": 0,
                "emergency_events": 0,
                "system_events": 0,
                "security_events": 0,
                "top_admins": [],
                "top_groups": [],
                "error_rate": 0.0,
                "note": "Audit summary requires implementing log querying functionality"
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating audit summary: {str(e)}")
            return {"error": str(e)}


# Test function
async def test_audit_service():
    """Test audit service functionality"""
    print("🧪 Testing Audit Service")
    print("=" * 50)
    
    audit = AuditService()
    
    # Test member change audit
    print("\n📝 Testing member change audit...")
    await audit.log_member_change(
        action="add",
        group_chat_id="120363400467632358@g.us",
        group_name="TEST_ALARM",
        admin_phone="19012976001",
        admin_name="Test Admin",
        target_phone="+56912345678",
        target_name="Ana Martinez",
        field_changed="name",
        old_value=None,
        new_value="Ana Martinez"
    )
    
    # Test emergency event audit
    print("\n🚨 Testing emergency event audit...")
    await audit.log_emergency_event(
        incident_type="INCENDIO",
        group_chat_id="120363400467632358@g.us",
        group_name="TEST_ALARM",
        reporter_phone="+56912345678",
        reporter_name="Ana Martinez",
        actions_taken=["Device Blink", "Text Alert", "Image Alert", "Voice Alert"],
        success_rate=100.0,
        member_data_used=True
    )
    
    # Test security event audit
    print("\n🔒 Testing security event audit...")
    await audit.log_security_event(
        event_type="permission_denied",
        user_phone="+56999999999",
        user_name="Unauthorized User",
        group_chat_id="120363400467632358@g.us",
        group_name="TEST_ALARM",
        action_attempted="@editar add member",
        success=False,
        reason="User is not an admin"
    )
    
    # Test system event audit
    print("\n🔧 Testing system event audit...")
    await audit.log_system_event(
        event_type="service_startup",
        description="Audit service initialized successfully",
        system_component="audit_service",
        success=True
    )
    
    print("\n✅ Audit service tests completed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_audit_service())