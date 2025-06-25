import pytest
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from app.services.voice_service import VoiceService
from app.config import settings

@pytest.fixture
def voice_service():
    return VoiceService()

@pytest.fixture
def mock_temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.mark.asyncio
async def test_text_to_speech_success(voice_service, mock_temp_dir):
    """Test successful text-to-speech generation"""
    with patch('app.services.voice_service.generate') as mock_generate, \
         patch('app.services.voice_service.save') as mock_save, \
         patch.object(voice_service, 'temp_dir', mock_temp_dir):
        
        # Mock the ElevenLabs response
        mock_generate.return_value = b"fake_audio_data"
        
        # Test text-to-speech
        result = await voice_service.text_to_speech("Hello, this is a test message")
        
        # Assertions
        assert result is not None
        assert result.endswith('.mp3')
        assert mock_temp_dir in result
        mock_generate.assert_called_once()
        mock_save.assert_called_once()

@pytest.mark.asyncio
async def test_text_to_speech_failure(voice_service):
    """Test text-to-speech failure handling"""
    with patch('app.services.voice_service.generate', side_effect=Exception("API Error")):
        result = await voice_service.text_to_speech("Test message")
        assert result is None

@pytest.mark.asyncio
async def test_convert_to_whatsapp_format(voice_service, mock_temp_dir):
    """Test audio format conversion"""
    # Create a fake MP3 file
    fake_mp3_path = os.path.join(mock_temp_dir, "test.mp3")
    with open(fake_mp3_path, 'wb') as f:
        f.write(b"fake_mp3_data")
    
    with patch('app.services.voice_service.AudioSegment') as mock_audio_segment:
        mock_audio = Mock()
        mock_audio_segment.from_mp3.return_value = mock_audio
        
        result = await voice_service.convert_to_whatsapp_format(fake_mp3_path)
        
        # Should return OGG path
        assert result is not None
        assert result.endswith('.ogg')
        mock_audio_segment.from_mp3.assert_called_once_with(fake_mp3_path)
        mock_audio.export.assert_called_once()

@pytest.mark.asyncio
async def test_generate_voice_message_complete_flow(voice_service, mock_temp_dir):
    """Test complete voice message generation flow"""
    with patch.object(voice_service, 'text_to_speech') as mock_tts, \
         patch.object(voice_service, 'convert_to_whatsapp_format') as mock_convert, \
         patch('os.path.exists', return_value=True), \
         patch('os.remove') as mock_remove:
        
        # Mock the flow
        fake_mp3_path = os.path.join(mock_temp_dir, "test.mp3")
        fake_ogg_path = os.path.join(mock_temp_dir, "test.ogg")
        
        mock_tts.return_value = fake_mp3_path
        mock_convert.return_value = fake_ogg_path
        
        result = await voice_service.generate_voice_message("Test message")
        
        # Assertions
        assert result == fake_ogg_path
        mock_tts.assert_called_once_with("Test message", None)
        mock_convert.assert_called_once_with(fake_mp3_path)
        mock_remove.assert_called_once_with(fake_mp3_path)

def test_cleanup_audio_file(voice_service, mock_temp_dir):
    """Test audio file cleanup"""
    # Create a fake file
    fake_file_path = os.path.join(mock_temp_dir, "test.ogg")
    with open(fake_file_path, 'w') as f:
        f.write("fake content")
    
    # Cleanup should remove the file
    voice_service.cleanup_audio_file(fake_file_path)
    
    # File should be removed
    assert not os.path.exists(fake_file_path)

def test_cleanup_audio_file_nonexistent(voice_service):
    """Test cleanup of non-existent file"""
    # Should not raise an exception
    voice_service.cleanup_audio_file("/fake/path/nonexistent.ogg")

@pytest.mark.asyncio
async def test_get_available_voices(voice_service):
    """Test getting available voices"""
    mock_response = {
        "voices": [
            {"voice_id": "123", "name": "Rachel"},
            {"voice_id": "456", "name": "Josh"}
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        result = voice_service.get_available_voices()
        
        assert result == mock_response
        mock_get.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])