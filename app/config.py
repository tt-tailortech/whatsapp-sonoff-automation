from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # WhatsApp API Configuration
    whapi_token: str
    whapi_base_url: str = "https://gate.whapi.cloud"
    
    # ElevenLabs Configuration
    elevenlabs_api_key: str
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    
    # OpenAI Configuration (fallback TTS)
    openai_api_key: str = ""  # Rachel voice
    
    # eWeLink Configuration
    ewelink_app_id: str
    ewelink_app_secret: str
    ewelink_base_url: str = "https://eu-apia.coolkit.cc"
    ewelink_email: str = ""
    ewelink_password: str = ""
    
    # Application Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    temp_audio_dir: str = "./temp_audio"
    test_device_id: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()