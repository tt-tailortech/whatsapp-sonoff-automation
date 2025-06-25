# WhatsApp-Sonoff Voice Automation System

A Python-based automation system that recreates n8n workflow functionality for controlling Sonoff devices via WhatsApp with voice responses.

## 🚀 Features

- **WhatsApp Integration**: Receive commands via WHAPI.co webhooks
- **Voice Responses**: AI-generated voice messages using ElevenLabs TTS
- **Sonoff Control**: Control Sonoff devices through eWeLink API
- **Multi-language Support**: Spanish and English voice responses
- **Command Processing**: Handle ON, OFF, BLINK, and STATUS commands
- **Robust Error Handling**: Fallback to text if voice fails

## 📋 Supported Commands

- **ON**: Turn on the Sonoff device
- **OFF**: Turn off the Sonoff device  
- **BLINK**: Activate blink/pulse mode
- **STATUS**: Get current device status

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd Alarm_system
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required credentials:
- **WHAPI_TOKEN**: Your WHAPI.co API token
- **ELEVENLABS_API_KEY**: Your ElevenLabs API key
- **EWELINK_APP_ID**: Your eWeLink App ID
- **EWELINK_APP_SECRET**: Your eWeLink App Secret

### 3. Set Up Your Services

#### WHAPI.co Setup
1. Sign up at [whapi.cloud](https://whapi.cloud)
2. Get your API token from the dashboard
3. Set up webhook URL: `https://your-domain.com/whatsapp-webhook`

#### ElevenLabs Setup
1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Get your API key from account settings
3. Free tier includes 20,000 characters/month

#### eWeLink Setup
1. Create developer account at eWeLink
2. Get your App ID and App Secret
3. Connect your Sonoff devices to eWeLink app

### 4. Run the Application

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Manual API Testing
```bash
python tests/test_api_manual.py
```

### Test Individual Services
```bash
# Test voice service
python -m pytest tests/test_voice_service.py -v

# Test WhatsApp service  
python -m pytest tests/test_whatsapp_service.py -v

# Test eWeLink service
python -m pytest tests/test_ewelink_service.py -v
```

## 🚀 Deployment

### Railway.app (Recommended)
1. Connect your GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Render.com
1. Connect your GitHub repo to Render
2. Use the included `render.yaml` configuration
3. Set environment variables in Render dashboard

### Manual Deployment
```bash
# Using the Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📱 Usage

1. Send a WhatsApp message to your connected number
2. Use commands: `ON`, `OFF`, `BLINK`, or `STATUS`
3. Receive voice response confirming action
4. Device will be controlled automatically

### Example Conversation

**User**: "ON"  
**Bot**: 🎵 *Voice message*: "¡Perfecto! He encendido el dispositivo correctamente. El LED ya está encendido."

**User**: "STATUS"  
**Bot**: 🎵 *Voice message*: "Hola! El dispositivo está en línea y funcionando. El interruptor está encendido."

## 🏗️ Architecture

```
WhatsApp Message → WHAPI.co → Webhook → FastAPI → Command Processor
                                                        ↓
ElevenLabs TTS ← Voice Service ← Response Generator ← eWeLink API
       ↓
WHAPI.co Voice Message → WhatsApp User
```

## 🔧 Configuration

### Voice Settings
- Default voice: Rachel (English/Spanish)
- Audio format: OGG/Opus (WhatsApp compatible)
- Quality: 16kHz mono

### Device Settings
- Automatic device discovery
- Fallback to first available device
- Support for multiple device types

## 🚨 Troubleshooting

### Common Issues

1. **Voice messages not sending**
   - Check ElevenLabs API key and quota
   - Verify audio file permissions
   - Check WHAPI.co token validity

2. **Device control not working**
   - Verify eWeLink credentials
   - Ensure devices are online
   - Check device permissions in eWeLink app

3. **Webhook not receiving messages**
   - Verify webhook URL is publicly accessible
   - Check WHAPI.co webhook configuration
   - Ensure HTTPS is enabled

### Debug Mode
```bash
DEBUG=true uvicorn main:app --reload
```

## 📊 Free Tier Limitations

- **ElevenLabs**: 20,000 characters/month
- **WHAPI.co**: Check current plan limits
- **Railway/Render**: 500 hours/month

## 🔒 Security Notes

- Keep API keys secure and never commit to version control
- Use environment variables for all sensitive data
- Implement rate limiting for production use
- Monitor API usage to avoid quota exceeded

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation for each service
3. Open an issue with detailed error logs

---

**Made with ❤️ for home automation enthusiasts**