#!/usr/bin/env python3
"""
Cleanup temporary files created by the emergency system
"""

import os
import glob
from datetime import datetime, timedelta

def cleanup_temporary_files():
    """Remove temporary files older than 1 hour"""
    print("🧹 Starting temporary file cleanup...")
    
    # File patterns to clean up
    patterns = [
        "*.jpg",
        "*.png", 
        "*.gif",
        "*.ogg",
        "*.mp3",
        "*.wav",
        "*.webp"
    ]
    
    # Exclude these permanent files
    permanent_files = [
        "emergency_alert_professional.jpg",
        "emergency_alert_test.jpg", 
        "animated_emergency_siren.gif"
    ]
    
    cleaned_count = 0
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=1)  # 1 hour ago
    
    for pattern in patterns:
        files = glob.glob(pattern)
        for file_path in files:
            # Skip permanent files
            if os.path.basename(file_path) in permanent_files:
                continue
                
            try:
                # Check file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_time:
                    print(f"🗑️ Removing old temp file: {file_path}")
                    os.remove(file_path)
                    cleaned_count += 1
                else:
                    print(f"⏰ Keeping recent file: {file_path}")
                    
            except Exception as e:
                print(f"❌ Error cleaning {file_path}: {str(e)}")
    
    # Clean temp_audio directory
    temp_audio_dir = "./temp_audio"
    if os.path.exists(temp_audio_dir):
        audio_files = glob.glob(os.path.join(temp_audio_dir, "*"))
        for file_path in audio_files:
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_time:
                    print(f"🗑️ Removing old audio file: {file_path}")
                    os.remove(file_path)
                    cleaned_count += 1
            except Exception as e:
                print(f"❌ Error cleaning audio file {file_path}: {str(e)}")
    
    print(f"✅ Cleanup completed - removed {cleaned_count} temporary files")
    return cleaned_count

if __name__ == "__main__":
    cleanup_temporary_files()