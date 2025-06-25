#!/usr/bin/env python3
"""
Setup script for WhatsApp-Sonoff Voice Automation System
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python 3.8+ is installed"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_environment():
    """Set up the development environment"""
    print("🚀 Setting up WhatsApp-Sonoff Voice Automation System")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        try:
            with open('.env.example', 'r') as template:
                with open('.env', 'w') as env_file:
                    env_file.write(template.read())
            print("✅ .env file created - please fill in your API credentials")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Create temp audio directory
    temp_dir = Path("temp_audio")
    if not temp_dir.exists():
        temp_dir.mkdir()
        print("✅ Created temp_audio directory")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Fill in your API credentials in the .env file:")
    print("   - WHAPI_TOKEN (from whapi.cloud)")
    print("   - ELEVENLABS_API_KEY (from elevenlabs.io)")
    print("   - EWELINK_APP_ID and EWELINK_APP_SECRET (from eWeLink)")
    print("\n2. Test the installation:")
    print("   python tests/test_api_manual.py")
    print("\n3. Run the application:")
    print("   uvicorn main:app --reload")
    print("\n4. Set up your webhook URL in WHAPI.co:")
    print("   https://your-domain.com/whatsapp-webhook")
    
    return True

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    # Test imports
    try:
        from app.services.voice_service import VoiceService
        from app.services.whatsapp_service import WhatsAppService
        from app.services.ewelink_service import EWeLinkService
        print("✅ All modules import successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test FastAPI startup
    try:
        from main import app
        print("✅ FastAPI app loads successfully")
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
        return False
    
    print("✅ Installation test passed!")
    return True

if __name__ == "__main__":
    if setup_environment():
        test_installation()
    else:
        print("❌ Setup failed!")
        sys.exit(1)