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
    ewelink_app_id: str = "McFJj4Noke1mGDZCR1QarGW7rtDv00Zs"
    ewelink_app_secret: str = "6Nz4n0xA8s8qdxQf2GqurZj2Fs55FUvM"
    ewelink_base_url: str = "https://us-apia.coolkit.cc"  # US region - confirmed working
    ewelink_email: str = "tt.tailortech@gmail.com"
    ewelink_password: str = "Qwerty.2025"
    ewelink_access_token: str = "73d1a52ee534403fcfe294d0b5a26504dbd5bd8a"  # Working token from browser
    
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