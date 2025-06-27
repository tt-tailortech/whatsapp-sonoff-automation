#!/usr/bin/env python3
"""
Manual signature generation test
"""

import json
import hmac
import hashlib
import base64

def test_signature_generation():
    """Test signature generation manually"""
    
    # Exact credentials
    app_secret = "KFyym4qw1glz4xjdUVN0UNOBvCNMmffo"
    
    # Test payload
    payload = {
        "email": "tt.tailortech@gmail.com",
        "password": "Qwerty.2025",
        "countryCode": "+56"
    }
    
    print("Testing signature generation:")
    print("=" * 50)
    
    # Method 1: Our current method
    json_payload = json.dumps(payload, separators=(',', ':')).encode()
    print(f"JSON payload: {json_payload}")
    
    signature = hmac.new(
        app_secret.encode(),
        json_payload,
        hashlib.sha256
    ).digest()
    
    result = base64.b64encode(signature).decode()
    print(f"Generated signature: {result}")
    
    # Method 2: Try different JSON encoding
    json_payload2 = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    print(f"JSON payload UTF-8: {json_payload2}")
    
    signature2 = hmac.new(
        app_secret.encode('utf-8'),
        json_payload2,
        hashlib.sha256
    ).digest()
    
    result2 = base64.b64encode(signature2).decode()
    print(f"Generated signature UTF-8: {result2}")
    
    # Method 3: Try different order
    payload3 = {
        "countryCode": "+56",
        "email": "tt.tailortech@gmail.com", 
        "password": "Qwerty.2025"
    }
    
    json_payload3 = json.dumps(payload3, separators=(',', ':')).encode()
    print(f"JSON payload ordered: {json_payload3}")
    
    signature3 = hmac.new(
        app_secret.encode(),
        json_payload3,
        hashlib.sha256
    ).digest()
    
    result3 = base64.b64encode(signature3).decode()
    print(f"Generated signature ordered: {result3}")
    
    # Method 4: Try without countryCode
    payload4 = {
        "email": "tt.tailortech@gmail.com",
        "password": "Qwerty.2025"
    }
    
    json_payload4 = json.dumps(payload4, separators=(',', ':')).encode()
    print(f"JSON payload no country: {json_payload4}")
    
    signature4 = hmac.new(
        app_secret.encode(),
        json_payload4,
        hashlib.sha256
    ).digest()
    
    result4 = base64.b64encode(signature4).decode()
    print(f"Generated signature no country: {result4}")

if __name__ == "__main__":
    test_signature_generation()