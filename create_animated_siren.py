#!/usr/bin/env python3
"""
Create an animated GIF with flashing siren for emergency alert
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_animated_siren_gif():
    """Create animated GIF with flashing emergency siren"""
    
    # Settings
    width, height = 400, 400
    frames = []
    frame_count = 8
    
    # Colors
    red = (255, 0, 0)
    dark_red = (150, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    print(f"🚨 Creating animated siren GIF...")
    
    for frame_num in range(frame_count):
        # Create frame
        img = Image.new('RGB', (width, height), color=black)
        draw = ImageDraw.Draw(img)
        
        # Determine if siren should be bright or dim (flashing effect)
        is_bright = frame_num % 2 == 0
        siren_color = red if is_bright else dark_red
        
        # Draw flashing background
        bg_color = (20, 0, 0) if is_bright else (5, 0, 0)
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw siren shape (dome)
        siren_radius = 80
        center_x, center_y = width // 2, height // 2 - 50
        
        # Siren dome
        draw.ellipse([
            center_x - siren_radius, center_y - siren_radius//2,
            center_x + siren_radius, center_y + siren_radius//2
        ], fill=siren_color, outline=white, width=3)
        
        # Siren base
        base_width = 60
        base_height = 20
        draw.rectangle([
            center_x - base_width//2, center_y + siren_radius//2 - 10,
            center_x + base_width//2, center_y + siren_radius//2 + base_height
        ], fill=(100, 100, 100), outline=white, width=2)
        
        # Light rays (when bright)
        if is_bright:
            ray_length = 40
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                start_x = center_x + int((siren_radius + 10) * math.cos(rad))
                start_y = center_y + int((siren_radius//2 + 10) * math.sin(rad))
                end_x = center_x + int((siren_radius + ray_length) * math.cos(rad))
                end_y = center_y + int((siren_radius//2 + ray_length) * math.sin(rad))
                
                draw.line([start_x, start_y, end_x, end_y], fill=(255, 255, 0), width=3)
        
        # Emergency text
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        text_color = white if is_bright else (200, 200, 200)
        emergency_text = "🚨 EMERGENCIA 🚨"
        
        # Get text size for centering
        if font:
            bbox = draw.textbbox((0, 0), emergency_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
        else:
            text_x = width // 2 - 50
        
        text_y = center_y + 100
        draw.text((text_x, text_y), emergency_text, fill=text_color, font=font)
        
        # Alert text
        alert_text = "ALERTA COMUNITARIA"
        if font:
            bbox = draw.textbbox((0, 0), alert_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
        else:
            text_x = width // 2 - 60
        
        text_y = center_y + 130
        draw.text((text_x, text_y), alert_text, fill=text_color, font=font)
        
        frames.append(img)
        print(f"   Frame {frame_num + 1}/{frame_count} created")
    
    # Save as animated GIF
    gif_path = "/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/animated_emergency_siren.gif"
    
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=300,  # 300ms per frame
        loop=0  # Loop forever
    )
    
    file_size = os.path.getsize(gif_path)
    print(f"✅ Animated siren GIF created: {gif_path}")
    print(f"   Frames: {frame_count}")
    print(f"   Size: {file_size} bytes")
    print(f"   Duration: {frame_count * 300}ms loop")
    
    return gif_path

if __name__ == "__main__":
    create_animated_siren_gif()