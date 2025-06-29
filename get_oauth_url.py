#!/usr/bin/env python3
import time
import hmac
import hashlib
import base64

APP_ID = "q0YhvVsyUyTB1MftWvqDnMLdUKVcvLYH"
APP_SECRET = "U4xfEhgyHtR1QDgQt2Flati3O8b97JhM"

# Generate OAuth URL
timestamp = str(int(time.time() * 1000))
nonce = base64.b64encode(str(time.time()).encode()).decode()[:8]

# Create signature
sign_str = f"{APP_ID}_{timestamp}"
signature = base64.b64encode(
    hmac.new(APP_SECRET.encode(), sign_str.encode(), hashlib.sha256).digest()
).decode()

# Build OAuth URL for South America/Chile
oauth_url = (
    f"https://c2ccdn.coolkit.cc/oauth/index.html"
    f"?clientId={APP_ID}"
    f"&seq={timestamp}"
    f"&authorization={signature}"
    f"&redirectUrl=http://localhost:3000/callback"
    f"&state=manual_setup"
    f"&nonce={nonce}"
    f"&region=us"  # Try US region but we'll also try others
)

# Also generate for other regions
oauth_url_asia = oauth_url.replace("&region=us", "&region=as")
oauth_url_eu = oauth_url.replace("&region=us", "&region=eu")
oauth_url_china = oauth_url.replace("&region=us", "&region=cn")

print("🔐 eWeLink OAuth URL Generator")
print("=" * 50)
print(f"\n🇨🇱 For Chilean account (+56), try these URLs:")
print("\n1️⃣ China Region (detected from error - try this first!):")
print(oauth_url_china)
print("\n2️⃣ Asia Region (sometimes works for South America):")
print(oauth_url_asia)
print("\n3️⃣ US Region:")
print(oauth_url)
print("\n4️⃣ EU Region (backup option):")
print(oauth_url_eu)
print("\n📌 After login, you'll be redirected to:")
print("http://localhost:3000/callback?code=XXXXX")
print("\n⚠️ Copy the 'code' parameter from the redirect URL")
print("\n⏱️ URLs expire in ~10 minutes")