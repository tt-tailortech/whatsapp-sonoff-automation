import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.whatsapp_service import WhatsAppService
from app.models import WhatsAppMessage

@pytest.fixture
def whatsapp_service():
    return WhatsAppService()

def test_parse_whatsapp_webhook_direct_format(whatsapp_service):
    """Test parsing direct WhatsApp webhook format"""
    payload = {
        "messages": [{
            "id": "msg123",
            "from": "+1234567890",
            "type": "text",
            "text": {"body": "ON"},
            "timestamp": "1640995200"
        }],
        "contacts": [{
            "profile": {"name": "Test User"}
        }]
    }
    
    result = whatsapp_service.parse_whatsapp_webhook(payload)
    
    assert result is not None
    assert result.id == "msg123"
    assert result.from_phone == "+1234567890"
    assert result.text == "ON"
    assert result.contact_name == "Test User"

def test_parse_whatsapp_webhook_business_format(whatsapp_service):
    """Test parsing WhatsApp Business API format"""
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "msg456",
                        "from": "+9876543210",
                        "type": "text",
                        "text": {"body": "STATUS"},
                        "timestamp": "1640995300"
                    }],
                    "contacts": [{
                        "profile": {"name": "Business User"}
                    }]
                }
            }]
        }]
    }
    
    result = whatsapp_service.parse_whatsapp_webhook(payload)
    
    assert result is not None
    assert result.id == "msg456"
    assert result.from_phone == "+9876543210"
    assert result.text == "STATUS"
    assert result.contact_name == "Business User"

def test_parse_whatsapp_webhook_invalid_format(whatsapp_service):
    """Test parsing invalid webhook format"""
    payload = {"invalid": "format"}
    
    result = whatsapp_service.parse_whatsapp_webhook(payload)
    
    assert result is None

def test_parse_whatsapp_webhook_non_text_message(whatsapp_service):
    """Test parsing non-text message"""
    payload = {
        "messages": [{
            "id": "msg789",
            "from": "+1234567890",
            "type": "image",
            "timestamp": "1640995400"
        }]
    }
    
    result = whatsapp_service.parse_whatsapp_webhook(payload)
    
    assert result is None

@pytest.mark.asyncio
async def test_send_text_message_success(whatsapp_service):
    """Test successful text message sending"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await whatsapp_service.send_text_message("+1234567890", "Test message")
        
        assert result is True

@pytest.mark.asyncio
async def test_send_text_message_failure(whatsapp_service):
    """Test text message sending failure"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await whatsapp_service.send_text_message("+1234567890", "Test message")
        
        assert result is False

@pytest.mark.asyncio
async def test_send_voice_message_success(whatsapp_service):
    """Test successful voice message sending"""
    with patch('httpx.AsyncClient') as mock_client, \
         patch('builtins.open', create=True) as mock_open, \
         patch('base64.b64encode') as mock_b64encode:
        
        # Mock file reading and base64 encoding
        mock_open.return_value.__enter__.return_value.read.return_value = b"fake_audio_data"
        mock_b64encode.return_value.decode.return_value = "fake_base64_data"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await whatsapp_service.send_voice_message("+1234567890", "/fake/path/audio.ogg")
        
        assert result is True

@pytest.mark.asyncio
async def test_send_voice_message_with_file_upload_success(whatsapp_service):
    """Test successful voice message sending via file upload"""
    with patch('httpx.AsyncClient') as mock_client, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await whatsapp_service.send_voice_message_with_file_upload("+1234567890", "/fake/path/audio.ogg")
        
        assert result is True

@pytest.mark.asyncio
async def test_get_account_info_success(whatsapp_service):
    """Test successful account info retrieval"""
    mock_account_data = {
        "id": "123456789",
        "name": "Test Account",
        "status": "active"
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_account_data
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await whatsapp_service.get_account_info()
        
        assert result == mock_account_data

@pytest.mark.asyncio
async def test_get_account_info_failure(whatsapp_service):
    """Test account info retrieval failure"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await whatsapp_service.get_account_info()
        
        assert result == {}

if __name__ == "__main__":
    pytest.main([__file__])