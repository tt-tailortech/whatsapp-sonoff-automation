#!/bin/bash

# Test WHAPI.cloud connectivity using curl
# This helps isolate if it's a Python/httpx issue or general connectivity

echo "🧪 Testing WHAPI.cloud connectivity with curl..."
echo

# Get the token from environment or config
TOKEN=$(python3 -c "from app.config import settings; print(settings.whapi_token)")
BASE_URL="https://gate.whapi.cloud"

echo "🔑 Token (first 15 chars): ${TOKEN:0:15}..."
echo "🌐 Base URL: $BASE_URL"
echo

# Test 1: Basic connectivity
echo "1️⃣ Testing basic connectivity..."
curl -v --connect-timeout 10 --max-time 30 "$BASE_URL" 2>&1 | head -20
echo

# Test 2: Account endpoint
echo "2️⃣ Testing account endpoint..."
curl -X GET \
  --connect-timeout 10 \
  --max-time 30 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$BASE_URL/account" \
  -v
echo

# Test 3: Send message to Waldo
echo "3️⃣ Testing message send..."
curl -X POST \
  --connect-timeout 10 \
  --max-time 30 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "56940035815",
    "body": "🧪 Test message from curl script",
    "typing_time": 1
  }' \
  "$BASE_URL/messages/text" \
  -v
echo

echo "✅ Curl tests completed!"