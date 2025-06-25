import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.ewelink_service import EWeLinkService
from app.models import EWeLinkDevice, DeviceStatus

@pytest.fixture
def ewelink_service():
    return EWeLinkService()

def test_generate_signature(ewelink_service):
    """Test signature generation for API authentication"""
    timestamp = "1640995200000"
    nonce = "1640995200"
    
    # Mock the app_secret for testing
    with patch.object(ewelink_service, 'app_secret', 'test_secret'):
        signature = ewelink_service._generate_signature(timestamp, nonce)
        
        # Should return a base64 encoded string
        assert isinstance(signature, str)
        assert len(signature) > 0

def test_get_auth_headers(ewelink_service):
    """Test authentication headers generation"""
    with patch.object(ewelink_service, 'app_id', 'test_app_id'), \
         patch.object(ewelink_service, 'access_token', 'test_token'):
        
        headers = ewelink_service._get_auth_headers()
        
        # Check required headers
        assert 'Content-Type' in headers
        assert 'X-CK-Appid' in headers
        assert 'X-CK-Timestamp' in headers
        assert 'X-CK-Nonce' in headers
        assert 'X-CK-Signature' in headers
        assert 'Authorization' in headers
        
        assert headers['X-CK-Appid'] == 'test_app_id'
        assert headers['Authorization'] == 'Bearer test_token'

@pytest.mark.asyncio
async def test_authenticate_success(ewelink_service):
    """Test successful authentication"""
    mock_response_data = {
        "error": 0,
        "data": {
            "at": "test_access_token",
            "user": {"id": "user123"}
        }
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await ewelink_service.authenticate("test@example.com", "password123")
        
        assert result is True
        assert ewelink_service.access_token == "test_access_token"
        assert ewelink_service.user_id == "user123"

@pytest.mark.asyncio
async def test_authenticate_failure(ewelink_service):
    """Test authentication failure"""
    mock_response_data = {
        "error": 400,
        "msg": "Invalid credentials"
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await ewelink_service.authenticate("test@example.com", "wrong_password")
        
        assert result is False
        assert ewelink_service.access_token is None

@pytest.mark.asyncio
async def test_get_devices_success(ewelink_service):
    """Test successful device retrieval"""
    mock_response_data = {
        "error": 0,
        "data": {
            "thingList": [
                {
                    "deviceid": "device123",
                    "name": "Living Room Switch",
                    "productModel": "SONOFF_BASIC",
                    "online": True,
                    "params": {"switch": "on"}
                },
                {
                    "deviceid": "device456",
                    "name": "Bedroom Light",
                    "productModel": "SONOFF_S20",
                    "online": False,
                    "params": {"switch": "off"}
                }
            ]
        }
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        devices = await ewelink_service.get_devices()
        
        assert len(devices) == 2
        assert devices[0].deviceid == "device123"
        assert devices[0].name == "Living Room Switch"
        assert devices[0].online is True
        assert devices[1].deviceid == "device456"
        assert devices[1].online is False

@pytest.mark.asyncio
async def test_control_device_on_command(ewelink_service):
    """Test ON command execution"""
    mock_response_data = {"error": 0}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await ewelink_service.control_device("device123", "ON")
        
        assert result is True
        
        # Check that the correct payload was sent
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = call_args[1]['json']
        assert payload['params']['switch'] == 'on'

@pytest.mark.asyncio
async def test_control_device_off_command(ewelink_service):
    """Test OFF command execution"""
    mock_response_data = {"error": 0}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await ewelink_service.control_device("device123", "OFF")
        
        assert result is True
        
        # Check that the correct payload was sent
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = call_args[1]['json']
        assert payload['params']['switch'] == 'off'

@pytest.mark.asyncio
async def test_control_device_blink_command(ewelink_service):
    """Test BLINK command execution"""
    mock_response_data = {"error": 0}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await ewelink_service.control_device("device123", "BLINK")
        
        assert result is True
        
        # Check that pulse parameters were sent
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        payload = call_args[1]['json']
        assert 'pulse' in payload['params'] or 'switch' in payload['params']

@pytest.mark.asyncio
async def test_get_device_status_success(ewelink_service):
    """Test successful device status retrieval"""
    mock_response_data = {
        "error": 0,
        "data": {
            "online": True,
            "params": {"switch": "on"},
            "lastUpdateTime": "2024-01-01T12:00:00Z"
        }
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        status = await ewelink_service.get_device_status("device123")
        
        assert status is not None
        assert status.device_id == "device123"
        assert status.online is True
        assert status.switch_state == "on"

@pytest.mark.asyncio
async def test_get_device_status_failure(ewelink_service):
    """Test device status retrieval failure"""
    mock_response_data = {"error": 400, "msg": "Device not found"}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        status = await ewelink_service.get_device_status("nonexistent_device")
        
        assert status is None

@pytest.mark.asyncio
async def test_find_device_by_name_success(ewelink_service):
    """Test finding device by name"""
    # Mock the get_devices method
    mock_devices = [
        EWeLinkDevice(
            deviceid="device123",
            name="Living Room Switch",
            type="SONOFF_BASIC",
            online=True,
            params={"switch": "on"}
        ),
        EWeLinkDevice(
            deviceid="device456",
            name="Bedroom Light",
            type="SONOFF_S20",
            online=False,
            params={"switch": "off"}
        )
    ]
    
    with patch.object(ewelink_service, 'get_devices', return_value=mock_devices):
        device_id = await ewelink_service.find_device_by_name("Living Room Switch")
        
        assert device_id == "device123"

@pytest.mark.asyncio
async def test_find_device_by_name_not_found(ewelink_service):
    """Test finding non-existent device by name"""
    mock_devices = [
        EWeLinkDevice(
            deviceid="device123",
            name="Living Room Switch",
            type="SONOFF_BASIC",
            online=True,
            params={"switch": "on"}
        )
    ]
    
    with patch.object(ewelink_service, 'get_devices', return_value=mock_devices):
        device_id = await ewelink_service.find_device_by_name("Nonexistent Device")
        
        assert device_id is None

if __name__ == "__main__":
    pytest.main([__file__])