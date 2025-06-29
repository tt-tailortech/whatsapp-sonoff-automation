#!/usr/bin/env python3
"""
Decode the eWeLink user token from localStorage
"""

import base64
import json

# The encoded user data from localStorage
encoded_user = "IntcInJlZ2lvblwiOlwidXNcIixcImFjY2Vzc1Rva2VuXCI6XCI3M2QxYTUyZWU1MzQ0MDNmY2ZlMjk0ZDBiNWEyNjUwNGRiZDViZDhhXCIsXCJyZWZyZXNoVG9rZW5cIjpcIjZmOWUzYzNiNzlmYWUwZDljZjk1MWRjM2ExOGFjMmFhNjRjYzkzM2RcIixcImNvdW50cnlDb2RlXCI6XCIrNTZcIixcImFjY291bnRcIjpcInR0LnRhaWxvcnRlY2hAZ21haWwuY29tXCIsXCJhY2NvdW50TGV2ZWxcIjoyMCxcImFjY2Vzc1Rva2VuRXhwaXJlVGltZVwiOjE3NTM3NDcxODUzODEsXCJsZXZlbEV4cGlyZWRBdFwiOjE3ODI2OTE4MDcwMDAsXCJhcGlrZXlcIjpcIjA0NzM5MjA5LTNjMTgtNDk5NS04YzJkLWRmOWQwMDJkYTgyMVwiLFwicGhvbmVOdW1iZXJcIjpcIlwiLFwiZW1haWxcIjpcInR0LnRhaWxvcnRlY2hAZ21haWwuY29tXCIsXCJ0aW1lem9uZVwiOntcImlkXCI6XCJBbWVyaWNhL1NhbnRpYWdvXCIsXCJvZmZzZXRcIjotNH19Ig=="

try:
    # Decode from base64
    decoded_bytes = base64.b64decode(encoded_user)
    decoded_string = decoded_bytes.decode('utf-8')
    
    print("🔓 Decoded user data:")
    print(decoded_string)
    print()
    
    # Parse as JSON (it's double-encoded)
    user_data = json.loads(json.loads(decoded_string))
    
    print("📋 Extracted Authentication Data:")
    print("=" * 50)
    print(f"🔑 Access Token: {user_data.get('accessToken')}")
    print(f"🔄 Refresh Token: {user_data.get('refreshToken')}")
    print(f"🗝️ API Key: {user_data.get('apikey')}")
    print(f"🌍 Region: {user_data.get('region')}")
    print(f"📧 Email: {user_data.get('email')}")
    print(f"📊 Account Level: {user_data.get('accountLevel')}")
    print()
    
    access_token = user_data.get('accessToken')
    
    if access_token:
        print("🎯 FOUND YOUR ACCESS TOKEN!")
        print("=" * 40)
        print(f"Token: {access_token}")
        print()
        print("📝 Add this to your Render environment variables:")
        print(f"EWELINK_ACCESS_TOKEN={access_token}")
        print()
        print("🧪 Test it with:")
        print(f"python3 test_manual_token.py {access_token}")
    else:
        print("❌ Access token not found in decoded data")
        
except Exception as e:
    print(f"❌ Error decoding: {e}")