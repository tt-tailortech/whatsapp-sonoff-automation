#!/usr/bin/env python3
"""
Create a simple 2-frame flashing emergency alert for instant visual impact
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_flash_alert_gif():
    """Create a simple 2-frame flashing emergency alert"""
    
    # Settings
    width, height = 400, 300
    frames = []
    
    # Colors
    bright_red = (255, 0, 0)
    dark_red = (120, 0, 0)
    bright_yellow = (255, 255, 0)
    dark_yellow = (180, 180, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    print(f"⚡ Creating 2-frame flashing emergency alert...")
    
    for frame_num in range(2):
        # Alternate between bright and dark
        is_bright = frame_num == 0
        
        # Create frame
        bg_color = bright_red if is_bright else dark_red
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Emergency border
        border_color = bright_yellow if is_bright else dark_yellow
        border_width = 15 if is_bright else 8
        
        draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=border_width)
        
        # Emergency text
        try:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None
        
        text_color = white if is_bright else (220, 220, 220)
        
        # Main emergency text
        main_text = "🚨 EMERGENCIA 🚨"
        if font_large:
            bbox = draw.textbbox((0, 0), main_text, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
        else:
            text_x = width // 2 - 80
        
        text_y = height // 2 - 40
        draw.text((text_x, text_y), main_text, fill=text_color, font=font_large)
        
        # Alert type
        alert_text = "ALERTA COMUNITARIA"
        if font_small:
            bbox = draw.textbbox((0, 0), alert_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
        else:
            text_x = width // 2 - 70
        
        text_y = height // 2 + 10
        draw.text((text_x, text_y), alert_text, fill=text_color, font=font_small)
        
        # Action text
        action_text = "ACTIVADO INMEDIATAMENTE"
        if font_small:
            bbox = draw.textbbox((0, 0), action_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
        else:
            text_x = width // 2 - 80
        
        text_y = height // 2 + 40
        draw.text((text_x, text_y), action_text, fill=text_color, font=font_small)
        
        frames.append(img)
        print(f"   Frame {frame_num + 1}/2 created ({'BRIGHT' if is_bright else 'DIM'})")
    
    # Save as fast-flashing GIF
    gif_path = "/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/flash_emergency_alert.gif"
    
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=150,  # 150ms per frame = very fast flash
        loop=0  # Loop forever
    )
    
    file_size = os.path.getsize(gif_path)
    print(f"✅ Fast-flashing emergency GIF created: {gif_path}")
    print(f"   Frames: 2")
    print(f"   Size: {file_size} bytes")
    print(f"   Duration: 300ms total (150ms each frame)")
    print(f"   Effect: Rapid red/yellow flashing")
    
    return gif_path

if __name__ == "__main__":
    create_flash_alert_gif()