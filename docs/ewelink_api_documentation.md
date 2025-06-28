# Complete eWeLink API Documentation

## Platform Overview

**CoolKit** is a Chinese IoT solution provider specializing in smart home devices and platforms. The eWeLink API provides third-party developers with access to:

- Device statistics and control
- User management 
- Home and room management
- Scene management
- Real-time device monitoring via WebSocket

### Supported Application Scenarios
- Smart Logistics, Transportation, Security
- Smart Building, Home, Retailing
- Smart Agriculture

## Authentication Methods

### 1. OAuth 2.0 (Recommended)

**Developer Registration:**
1. Register at https://dev.ewelink.cc/
2. Create application in Platform → App Management
3. Obtain `APP_ID` and `APP_SECRET`
4. Configure redirect URL

**Authorization Flow:**
```javascript
// Step 1: Generate authorization URL
const authUrl = `https://c2ccdn.coolkit.cc/oauth/index.html?clientId=${APP_ID}&seq=${timestamp}&authorization=${signature}&redirectUrl=${redirectUrl}&state=${requestId}&nonce=${nonce}`;

// Step 2: Signature calculation (HMAC-SHA256)
const signature = crypto
  .createHmac('sha256', APP_SECRET)
  .update(`${APP_ID}_${timestamp}`)
  .digest('base64');

// Step 3: Exchange authorization code for token
const tokenResponse = await fetch('/v2/user/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    clientId: APP_ID,
    clientSecret: APP_SECRET,
    grantType: 'authorization_code',
    code: authorizationCode,
    redirectUrl: REDIRECT_URL
  })
});
```

### 2. Direct Login (Legacy)
```javascript
const loginResponse = await client.user.login({
  account: "user@example.com",
  password: "password123",
  areaCode: "+1"
});
```

## API Endpoints

### Base URLs by Region
- **China:** `https://apia.coolkit.cn`
- **Asia:** `https://apia.coolkit.cc` 
- **Americas:** `https://usapia.coolkit.cc`
- **Europe:** `https://euapia.coolkit.cc`

### Core API Categories

#### 1. User Management
- `POST /v2/user/register` - User registration
- `POST /v2/user/login` - User login
- `POST /v2/user/logout` - User logout
- `POST /v2/user/refresh` - Refresh access token
- `POST /v2/user/oauth/token` - OAuth token exchange

#### 2. Device Management
- `GET /v2/device/thing` - Get device list
- `POST /v2/device/thing/status` - Update device status
- `POST /v2/device/add` - Add device
- `DELETE /v2/device` - Remove device
- `POST /v2/device/share` - Share device
- `GET /v2/device/thing/history` - Get device history

#### 3. Home Management
- `GET /v2/family` - Get home list
- `POST /v2/family` - Create home
- `PUT /v2/family` - Update home
- `DELETE /v2/family` - Delete home

#### 4. Group Management
- `POST /v2/device/group` - Create device group
- `PUT /v2/device/group/update` - Update group
- `DELETE /v2/device/group` - Delete group

## Device Control Examples

### Single Channel Device
```javascript
// Turn device on/off
await client.device.setThingStatus({
  type: 1,
  id: deviceId,
  params: {
    switch: 'on'
  }
});
```

### Multi-Channel Device
```javascript
// Control 4-outlet device
await client.device.setThingStatus({
  type: 1,
  id: deviceId,
  params: {
    switches: [
      { switch: 'on', outlet: 0 },
      { switch: 'off', outlet: 1 },
      { switch: 'on', outlet: 2 },
      { switch: 'off', outlet: 3 }
    ]
  }
});
```

### RGB LED Bulb (UIID 22)
```javascript
// Set color mode
await client.device.setThingStatus({
  type: 1,
  id: deviceId,
  params: {
    switch: 'on',
    ltype: 'color',
    colorR: 255,
    colorG: 0,
    colorB: 0,
    bright: 50
  }
});

// Set white mode
await client.device.setThingStatus({
  type: 1,
  id: deviceId,
  params: {
    switch: 'on',
    ltype: 'white',
    white: 128,
    bright: 80
  }
});
```

## WebSocket Real-time Communication

### Connection Setup
```javascript
const wsClient = new eWeLink.Ws({
  appId: "your_app_id",
  appSecret: "your_app_secret", 
  region: "us"
});

// Connect with callbacks
wsClient.Connect.create({
  appId: wsClient.appId,
  at: accessToken,
  region: region,
  userApiKey: userApiKey
}, 
onConnect, 
onDisconnect, 
onError, 
onMessage);

// Update device state via WebSocket
wsClient.Connect.updateState(deviceId, {
  switch: "on"
});
```

### Message Handling
```javascript
function onMessage(message) {
  console.log('Device status update:', message);
  // Handle real-time device state changes
}

function onConnect() {
  console.log('WebSocket connected');
}

function onError(error) {
  console.error('WebSocket error:', error);
}
```

## UIID Protocol (Device Types)

The UIID protocol defines communication standards for 70+ device types:

### Common Device Types
- **UIID 1:** Single Channel Switch/Socket
- **UIID 2-4:** Multi-Channel Switch (2-4 channels)
- **UIID 6:** Touch Panel Switch
- **UIID 15:** TH10/TH16 Temperature/Humidity
- **UIID 22:** RGBCW LED Bulb
- **UIID 25:** Aroma Diffuser
- **UIID 28:** RF Bridge
- **UIID 34:** 4-Channel Pro R2/R3

### Device Control Parameters
```javascript
// Temperature/Humidity Sensor (UIID 15)
{
  switch: "on",
  mainSwitch: "on", 
  deviceType: "normal",
  temperature: "25.3",
  humidity: "60.2"
}

// Aroma Diffuser (UIID 25) 
{
  switch: "on",
  state: 1,        // Mist level
  lightbright: 50, // Light brightness
  lightswitch: 1   // Light switch
}
```

## Code Libraries and SDKs

### Official Library (Recommended)
```bash
npm install ewelink-api-next
```

```javascript
import eWeLink from "ewelink-api-next";

const client = new eWeLink.WebAPI({
  appId: "your_app_id",
  appSecret: "your_app_secret",
  region: "us",
  logObj: eWeLink.createLogger("us")
});
```

### Community Libraries
- **JavaScript:** `skydiver/ewelink-api` (older v1 API)
- **Go:** `NicklasWallgren/ewelink`
- **.NET:** `luisllamasbinaburo/EwelinkNET`
- **Node-RED:** `FloFlal/node-red-ewelink-v2-oauth`

## API Limits and Pricing

### Free Developer Account
- OAuth 2.0 login only
- 50,000 requests per month per region
- Limited technical support
- One year credentials validity

### Enterprise Developer ($2,000/year)
- Full OAuth 2.0 access
- Enhanced API limits
- Phone, email, WeChat support
- 90-day support period
- Business communication
- Extensive documentation

## Security and Data Protection

- **Encryption:** TLS 1.2, HTTPS, WSS protocols
- **Authentication:** Two-way cloud authentication
- **Data Storage:** AWS regional data centers
- **Compliance:** GDPR and regional privacy laws
- **Algorithm:** International mainstream cryptographic algorithms

## Error Handling

### Common Error Codes
- **400:** Bad Request - Invalid parameters
- **401:** Authentication failed
- **406:** Authentication error (wrong credentials)
- **429:** Rate limit exceeded
- **500:** Internal server error

### Authentication Troubleshooting
1. Verify APP_ID and APP_SECRET
2. Check signature calculation (HMAC-SHA256)
3. Ensure correct parameter order
4. Validate redirect URL configuration
5. Check token expiration (access: 1 month, refresh: 2 months)

## Contact and Support

- **Developer Portal:** https://dev.ewelink.cc/
- **Email:** bd@coolkit.cn
- **Phone:** 0755-86967464 / 18165721994
- **Hours:** 9:30-18:30 (Weekdays)
- **WeChat:** Technical support groups available

## Complete OAuth Example Repository

For complete working examples, refer to the official OAuth demo:
- **Repository:** https://github.com/coolkit-carl/eWeLinkOAuthLoginDemo
- **Setup:** Configure `config.js` with your credentials
- **Run:** `npm install && npm start`
- **Access:** http://127.0.0.1:8000/login

This comprehensive documentation covers all aspects of the eWeLink API including authentication methods, device control, WebSocket communication, device protocols, and practical implementation examples using the latest v2 API.