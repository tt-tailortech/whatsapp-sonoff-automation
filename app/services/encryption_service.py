#!/usr/bin/env python3
"""
Encryption Service
Handles encryption/decryption of sensitive member data (medical conditions, etc.)
"""

import os
import base64
import json
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionService:
    def __init__(self):
        """Initialize encryption service"""
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with key from environment or generate new one"""
        try:
            # Try to get encryption key from environment
            encryption_key = os.getenv("MEDICAL_DATA_ENCRYPTION_KEY")
            
            if encryption_key:
                print("🔐 Using encryption key from environment variable")
                # Decode the base64 key
                key = base64.urlsafe_b64decode(encryption_key.encode())
                self._fernet = Fernet(key)
            else:
                print("🔐 Generating new encryption key")
                # Generate new key and display warning
                key = Fernet.generate_key()
                self._fernet = Fernet(key)
                
                # Encode key for environment variable
                env_key = base64.urlsafe_b64encode(key).decode()
                
                print("🔐" + "="*80)
                print("🔐 NEW ENCRYPTION KEY GENERATED")
                print("🔐" + "="*80)
                print(f"🔐 Add this to your environment variables:")
                print(f"🔐 MEDICAL_DATA_ENCRYPTION_KEY={env_key}")
                print("🔐" + "="*80)
                print("🔐 ⚠️  WARNING: Save this key securely!")
                print("🔐 ⚠️  Data encrypted with this key cannot be recovered without it!")
                print("🔐" + "="*80)
                
        except Exception as e:
            print(f"❌ Error initializing encryption: {str(e)}")
            # Fall back to no encryption
            self._fernet = None
    
    def encrypt_sensitive_data(self, data: Union[str, Dict, list]) -> str:
        """
        Encrypt sensitive data
        
        Args:
            data: Data to encrypt (string, dict, or list)
            
        Returns:
            Encrypted data as base64 string, or original data if encryption fails
        """
        if not self._fernet:
            print("⚠️ Encryption not available, storing data unencrypted")
            return json.dumps(data) if not isinstance(data, str) else data
        
        try:
            # Convert data to JSON string if not already string
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, ensure_ascii=False)
            else:
                data_str = str(data)
            
            # Encrypt the data
            encrypted_data = self._fernet.encrypt(data_str.encode('utf-8'))
            
            # Return base64 encoded encrypted data
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"❌ Error encrypting data: {str(e)}")
            # Return original data if encryption fails
            return json.dumps(data) if not isinstance(data, str) else data
    
    def decrypt_sensitive_data(self, encrypted_data: str, expected_type: str = "auto") -> Union[str, Dict, list]:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            expected_type: Expected return type ("string", "dict", "list", "auto")
            
        Returns:
            Decrypted data in expected format, or original data if decryption fails
        """
        if not self._fernet:
            print("⚠️ Encryption not available, returning data as-is")
            return self._parse_unencrypted_data(encrypted_data, expected_type)
        
        try:
            # Check if data looks encrypted (base64 format)
            if not self._looks_encrypted(encrypted_data):
                print("🔓 Data appears unencrypted, parsing directly")
                return self._parse_unencrypted_data(encrypted_data, expected_type)
            
            # Decode base64 and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # Parse based on expected type
            if expected_type == "dict":
                return json.loads(decrypted_str)
            elif expected_type == "list":
                return json.loads(decrypted_str)
            elif expected_type == "string":
                return decrypted_str
            else:  # auto
                # Try to parse as JSON, fall back to string
                try:
                    return json.loads(decrypted_str)
                except json.JSONDecodeError:
                    return decrypted_str
                    
        except Exception as e:
            print(f"❌ Error decrypting data: {str(e)}")
            # Return original data if decryption fails
            return self._parse_unencrypted_data(encrypted_data, expected_type)
    
    def encrypt_medical_data(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive medical data in member record
        
        Args:
            member_data: Complete member data dictionary
            
        Returns:
            Member data with encrypted medical information
        """
        try:
            if "medical" not in member_data:
                return member_data
            
            medical_data = member_data["medical"]
            encrypted_member_data = member_data.copy()
            
            # Check if member has any sensitive medical data
            has_sensitive_data = self._has_sensitive_medical_data(medical_data)
            
            if not has_sensitive_data:
                print(f"🔓 No sensitive medical data found, skipping encryption")
                return member_data
            
            print(f"🔐 Sensitive medical data detected, applying encryption")
            
            # Encrypt sensitive medical fields
            sensitive_fields = ["conditions", "medications", "allergies", "blood_type"]
            
            for field in sensitive_fields:
                if field in medical_data and medical_data[field]:
                    # Only encrypt if field contains sensitive data
                    if self._is_field_sensitive(field, medical_data[field]):
                        encrypted_member_data["medical"][f"{field}_encrypted"] = True
                        encrypted_member_data["medical"][field] = self.encrypt_sensitive_data(medical_data[field])
                        print(f"🔐 Encrypted {field}: {medical_data[field]}")
                    else:
                        encrypted_member_data["medical"][f"{field}_encrypted"] = False
                        print(f"🔓 {field} not sensitive, storing unencrypted")
                elif field in medical_data:
                    # Mark as not encrypted for empty data
                    encrypted_member_data["medical"][f"{field}_encrypted"] = False
            
            return encrypted_member_data
            
        except Exception as e:
            print(f"❌ Error encrypting medical data: {str(e)}")
            return member_data
    
    def decrypt_medical_data(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive medical data in member record
        
        Args:
            member_data: Member data with potentially encrypted medical info
            
        Returns:
            Member data with decrypted medical information
        """
        try:
            if "medical" not in member_data:
                return member_data
            
            medical_data = member_data["medical"]
            decrypted_member_data = member_data.copy()
            
            # Decrypt sensitive medical fields
            sensitive_fields = ["conditions", "medications", "allergies", "blood_type"]
            
            for field in sensitive_fields:
                if medical_data.get(f"{field}_encrypted"):
                    # Decrypt the data
                    expected_type = "list" if field in ["conditions", "medications", "allergies"] else "string"
                    decrypted_data = self.decrypt_sensitive_data(medical_data[field], expected_type)
                    decrypted_member_data["medical"][field] = decrypted_data
                    
                    # Remove encryption flag for clean data
                    decrypted_member_data["medical"].pop(f"{field}_encrypted", None)
            
            return decrypted_member_data
            
        except Exception as e:
            print(f"❌ Error decrypting medical data: {str(e)}")
            return member_data
    
    def encrypt_member_data_for_storage(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt all member data before storage
        
        Args:
            member_data: Complete group member data
            
        Returns:
            Member data with encrypted sensitive information
        """
        try:
            encrypted_data = member_data.copy()
            members = encrypted_data.get("members", {})
            
            # Encrypt each member's medical data
            for phone, member in members.items():
                members[phone] = self.encrypt_medical_data(member)
            
            encrypted_data["members"] = members
            
            # Add encryption metadata
            encrypted_data["encryption_info"] = {
                "encrypted": True,
                "encryption_version": "1.0",
                "encrypted_fields": ["medical.conditions", "medical.medications", "medical.allergies", "medical.blood_type"],
                "encrypted_at": "2025-06-29T00:00:00"
            }
            
            print(f"🔐 Encrypted sensitive data for {len(members)} members")
            return encrypted_data
            
        except Exception as e:
            print(f"❌ Error encrypting member data for storage: {str(e)}")
            return member_data
    
    def decrypt_member_data_from_storage(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt member data after retrieval from storage
        
        Args:
            encrypted_data: Member data with encrypted sensitive information
            
        Returns:
            Member data with decrypted information
        """
        try:
            # Check if data is encrypted
            if not encrypted_data.get("encryption_info", {}).get("encrypted"):
                print("🔓 Data not encrypted, returning as-is")
                return encrypted_data
            
            decrypted_data = encrypted_data.copy()
            members = decrypted_data.get("members", {})
            
            # Decrypt each member's medical data
            for phone, member in members.items():
                members[phone] = self.decrypt_medical_data(member)
            
            decrypted_data["members"] = members
            
            # Remove encryption metadata from returned data
            decrypted_data.pop("encryption_info", None)
            
            print(f"🔓 Decrypted sensitive data for {len(members)} members")
            return decrypted_data
            
        except Exception as e:
            print(f"❌ Error decrypting member data from storage: {str(e)}")
            return encrypted_data
    
    def _looks_encrypted(self, data: str) -> bool:
        """Check if data looks like encrypted base64 data"""
        try:
            # Check if it's valid base64
            base64.urlsafe_b64decode(data.encode('utf-8'))
            # Check if it doesn't look like JSON
            return not (data.strip().startswith('{') or data.strip().startswith('['))
        except:
            return False
    
    def _parse_unencrypted_data(self, data: str, expected_type: str) -> Union[str, Dict, list]:
        """Parse unencrypted data based on expected type"""
        try:
            if expected_type == "dict":
                return json.loads(data)
            elif expected_type == "list":
                return json.loads(data)
            elif expected_type == "string":
                return data
            else:  # auto
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return data
        except:
            return data
    
    def is_encryption_available(self) -> bool:
        """Check if encryption is available"""
        return self._fernet is not None
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption status information"""
        return {
            "encryption_available": self.is_encryption_available(),
            "encryption_algorithm": "Fernet (AES 128)" if self._fernet else "None",
            "key_source": "Environment Variable" if os.getenv("MEDICAL_DATA_ENCRYPTION_KEY") else "Generated",
            "encrypted_fields": ["medical.conditions", "medical.medications", "medical.allergies", "medical.blood_type"]
        }
    
    def _has_sensitive_medical_data(self, medical_data: Dict[str, Any]) -> bool:
        \"\"\"
        Determine if medical data contains sensitive information requiring encryption
        
        Args:
            medical_data: Medical information dictionary
            
        Returns:
            True if sensitive data is present
        \"\"\"
        # Define sensitive medical indicators
        sensitive_conditions = [
            \"diabetes\", \"diabetico\", \"hiv\", \"vih\", \"cancer\", \"mental\", \"psych\", \"depression\",
            \"bipolar\", \"esquizofrenia\", \"alzheimer\", \"epilepsia\", \"hepatitis\", \"tuberculosis\",
            \"embarazo\", \"embarazada\", \"drogas\", \"adiccion\", \"alcoholismo\", \"suicidio\"
        ]
        
        # Check conditions
        conditions = medical_data.get(\"conditions\", [])
        if isinstance(conditions, list):
            for condition in conditions:
                if isinstance(condition, str):
                    condition_lower = condition.lower()
                    if any(sensitive in condition_lower for sensitive in sensitive_conditions):
                        print(f\"🔐 Sensitive condition detected: {condition}\")
                        return True
        
        # Check medications (many medications indicate sensitive conditions)
        medications = medical_data.get(\"medications\", [])
        if isinstance(medications, list) and len(medications) > 0:
            print(f\"🔐 Medications detected: {medications}\")
            return True
        
        # Check allergies (life-threatening information)
        allergies = medical_data.get(\"allergies\", [])
        if isinstance(allergies, list) and len(allergies) > 0:
            print(f\"🔐 Allergies detected: {allergies}\")
            return True
        
        return False
    
    def _is_field_sensitive(self, field: str, data: Any) -> bool:
        \"\"\"
        Determine if specific field data is sensitive
        
        Args:
            field: Field name (conditions, medications, allergies, blood_type)
            data: Field data
            
        Returns:
            True if field data is sensitive
        \"\"\"
        if field == \"blood_type\":
            # Blood type alone is not very sensitive
            return False
        
        if field in [\"conditions\", \"medications\", \"allergies\"]:
            if isinstance(data, list) and len(data) > 0:
                return True
            elif isinstance(data, str) and data.strip():
                return True
        
        return False


# Test function
def test_encryption():
    """Test encryption functionality"""
    print("🧪 Testing Encryption Service")
    print("=" * 50)
    
    encryption = EncryptionService()
    
    # Test status
    status = encryption.get_encryption_status()
    print(f"🔐 Encryption Status: {status}")
    
    # Test basic encryption
    test_data = ["Diabetes", "Hipertensión", "Asma"]
    print(f"\n📝 Original data: {test_data}")
    
    encrypted = encryption.encrypt_sensitive_data(test_data)
    print(f"🔐 Encrypted: {encrypted[:50]}...")
    
    decrypted = encryption.decrypt_sensitive_data(encrypted, "list")
    print(f"🔓 Decrypted: {decrypted}")
    
    # Test medical data encryption
    test_member = {
        "name": "Ana Martinez",
        "medical": {
            "conditions": ["Diabetes", "Hipertensión"],
            "medications": ["Metformina", "Losartán"],
            "allergies": ["Penicilina"],
            "blood_type": "O+"
        }
    }
    
    print(f"\n👤 Original member: {test_member['name']}")
    print(f"🩺 Medical conditions: {test_member['medical']['conditions']}")
    
    encrypted_member = encryption.encrypt_medical_data(test_member)
    print(f"🔐 Medical data encrypted: {encrypted_member['medical'].get('conditions_encrypted', False)}")
    
    decrypted_member = encryption.decrypt_medical_data(encrypted_member)
    print(f"🔓 Decrypted conditions: {decrypted_member['medical']['conditions']}")
    
    print(f"\n✅ Encryption test completed")

if __name__ == "__main__":
    test_encryption()