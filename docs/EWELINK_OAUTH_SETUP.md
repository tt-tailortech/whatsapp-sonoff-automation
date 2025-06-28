# eWeLink OAuth 2.0 Setup Guide

Since your app is configured as OAuth 2.0, it cannot use direct login. You need to obtain an access token through the OAuth flow.

## Option 1: Manual Token Setup (Recommended for Render)

### Step 1: Get Access Token Locally

1. Run the setup script on your local machine:
```bash
python3 setup_oauth_token.py
```

2. A browser window will open with the eWeLink login page
3. Log in with your credentials:
   - Email: tt.tailortech@gmail.com
   - Password: Qwerty.2025
4. Authorize the app when prompted
5. The script will save the tokens to `ewelink_tokens.json`

### Step 2: Set Environment Variable on Render

1. Go to your Render dashboard
2. Navigate to Environment Variables
3. Add:
   - Key: `EWELINK_ACCESS_TOKEN`
   - Value: (copy the access token from the setup script output)

### Step 3: Update Your Service

The service will automatically use the token from the environment variable.

## Option 2: Use a Different App Type

If you can create a new app in eWeLink developer portal:

1. Create a new app with type "Direct Login" instead of "OAuth2.0"
2. This will allow direct username/password authentication
3. Update your APP_ID and APP_SECRET in the code

## Option 3: Use Home Assistant Integration

The Home Assistant integration uses a different app ID that supports direct login:

```python
# In your .env file
EWELINK_APP_ID=McFJj4Noke1mGDZCR1QarGW7rtDv00Zs
EWELINK_APP_SECRET=6Nz4n0xA8s8qdxQf2GqurZj2Fs55FUvM
```

Note: This is a third-party integration and may have limitations.

## Current Limitation

OAuth 2.0 apps **require** the full browser-based authorization flow. They cannot authenticate with just username/password. This is a security feature of OAuth 2.0.

For automated services like yours on Render, you need either:
- A manually obtained access token (Option 1)
- A Direct Login app type (Option 2)
- Use alternative integrations (Option 3)