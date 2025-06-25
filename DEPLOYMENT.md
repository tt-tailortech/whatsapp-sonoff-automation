# 🚀 Deployment Guide for WhatsApp-Sonoff Voice Automation

## ✅ **System Status**
- **Voice Generation**: ✅ Working (ElevenLabs API tested)
- **Audio Conversion**: ✅ Working (MP3 → OGG/Opus)
- **Webhook Processing**: ✅ Working (Message parsing tested)
- **FastAPI Server**: ✅ Working (Server starts successfully)
- **eWeLink Integration**: ✅ Ready (Requires authentication)
- **WhatsApp Integration**: ✅ Ready (Token configured)

## 🌐 **Deploy to Render.com**

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Use these settings:
   - **Name**: `whatsapp-sonoff-automation`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free` (512MB RAM, 750 hours/month)

### Step 3: Set Environment Variables
In Render dashboard, add these environment variables:

```
WHAPI_TOKEN=XQEoTE5p8D0cyEKuwyCM6m3qndywillq
WHAPI_BASE_URL=https://gate.whapi.cloud
ELEVENLABS_API_KEY=sk_b1a62f1ef23910f58d35fed90ef3cebfeff6a46dd71079cb
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
EWELINK_APP_ID=q9sI9m4qpC49UqjBSeA004INiA45jzu6
EWELINK_APP_SECRET=XFyym4qwTglz4xjdUVN0UNQBvCNMmf18
EWELINK_BASE_URL=https://eu-apia.coolkit.cc
TEST_DEVICE_ID=10011eafd1
HOST=0.0.0.0
PORT=$PORT
DEBUG=False
TEMP_AUDIO_DIR=./temp_audio
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your deployment URL: `https://your-app-name.onrender.com`

## 📱 **Configure WHAPI.co Webhook**

### Step 1: Set Webhook URL
1. Go to your WHAPI.co dashboard
2. Find "Webhook Settings" or "Settings"
3. Set webhook URL to: `https://your-app-name.onrender.com/whatsapp-webhook`
4. Enable webhook events for "Messages"

### Step 2: Test Webhook
Send a test message to your WhatsApp number with:
- `ON` - Should turn on your Sonoff device
- `OFF` - Should turn off your Sonoff device  
- `STATUS` - Should get device status
- `BLINK` - Should activate blink mode

## 🔐 **eWeLink Authentication Setup**

The system needs to authenticate with your eWeLink account. You have two options:

### Option A: Manual Authentication (Recommended for testing)
1. Run the authentication script on your local machine:
```bash
python3 test_ewelink_real.py
```
2. Enter your eWeLink email and password
3. Test device control

### Option B: App-based Authentication (For production)
- Use the App ID and App Secret (already configured)
- This method requires OAuth flow implementation

## 🧪 **Testing Your Deployment**

### 1. Health Check
Visit: `https://your-app-name.onrender.com/health`
Should return: `{"status": "healthy", "services": "operational"}`

### 2. Test Voice Generation
```bash
curl -X POST "https://your-app-name.onrender.com/whatsapp-webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "id": "test123",
      "from": "+1234567890",
      "type": "text", 
      "text": {"body": "STATUS"},
      "timestamp": "1640995200"
    }],
    "contacts": [{"profile": {"name": "Test User"}}]
  }'
```

### 3. Send Test WhatsApp Message
Send "STATUS" to your WhatsApp number and check if you receive a voice response.

## 📊 **Monitoring & Logs**

### Render.com Logs
- Go to your service dashboard
- Click "Logs" tab
- Monitor for errors or successful message processing

### Common Log Messages
- ✅ `Processing message from Test User: ON`
- ✅ `Generated voice audio: ./temp_audio/xxx.mp3`
- ✅ `Device 10011eafd1 command ON successful`
- ✅ `Voice message sent to +1234567890`

## 🔧 **Troubleshooting**

### Issue: Voice generation fails
- Check ElevenLabs API key and quota
- Monitor ElevenLabs usage at elevenlabs.io

### Issue: Device control fails  
- Verify eWeLink credentials
- Check if device is online in eWeLink app
- Test device ID: `10011eafd1`

### Issue: WhatsApp messages not received
- Verify webhook URL in WHAPI.co dashboard
- Check webhook format in logs
- Test with curl command above

### Issue: Deployment fails
- Check requirements.txt for dependency conflicts
- Verify all environment variables are set
- Check Render build logs

## 📈 **Free Tier Limits**

- **Render.com**: 750 hours/month (enough for 24/7 operation)
- **ElevenLabs**: 20,000 characters/month
- **WHAPI.co**: Check your plan limits

## 🔄 **Next Steps After Deployment**

1. **Test all commands**: ON, OFF, BLINK, STATUS
2. **Monitor voice responses**: Ensure Spanish audio is generated
3. **Check device control**: Verify Sonoff responds correctly
4. **Set up monitoring**: Watch logs for any errors
5. **Scale if needed**: Upgrade plans if you hit limits

## 📞 **Support**

If you encounter issues:
1. Check the deployment logs in Render
2. Test individual components with the test scripts
3. Verify all API credentials are correct
4. Ensure your Sonoff device is online

---

**Your system is ready for deployment! 🎉**

The voice automation will respond in Spanish to your WhatsApp commands and control your Sonoff device seamlessly.