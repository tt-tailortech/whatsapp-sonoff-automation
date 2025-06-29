#!/usr/bin/env python3
"""
Create a test emergency alert image for testing image sending functionality
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_emergency_alert_image():
    """Create a test emergency alert image similar to the user's example"""
    
    # Create image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='red')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default
    try:
        # Try different font paths for different systems
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/arial.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
        ]
        
        font_large = None
        font_medium = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font_large = ImageFont.truetype(font_path, 60)
                font_medium = ImageFont.truetype(font_path, 40)
                break
        
        # Fallback to default font if no system font found
        if not font_large:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Add white border
    border_width = 20
    draw.rectangle(
        [border_width, border_width, width-border_width, height-border_width],
        outline='white',
        width=10
    )
    
    # Add text content
    texts = [
        ("ALERTA DE EMERGENCIA", 80, font_large),
        ("ALARMA COMUNITARIA", 180, font_large),
        ("Sistema de Seguridad Activado", 280, font_medium),
        ("CALLE URGENTE 123", 350, font_medium),
        ("Contacte autoridades inmediatamente", 420, font_medium),
        ("📞 Emergencias: 911", 480, font_medium)
    ]
    
    for text, y_pos, font in texts:
        # Get text dimensions for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x_pos = (width - text_width) // 2
        
        # Add black outline for better visibility
        for adj in range(-2, 3):
            for adj2 in range(-2, 3):
                draw.text((x_pos + adj, y_pos + adj2), text, font=font, fill='black')
        
        # Add white text on top
        draw.text((x_pos, y_pos), text, font=font, fill='white')
    
    # Save the image
    image_path = "/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/emergency_alert_test.jpg"
    image.save(image_path, format='JPEG', quality=90)
    
    print(f"✅ Emergency alert test image created: {image_path}")
    print(f"   Size: {width}x{height}")
    print(f"   File size: {os.path.getsize(image_path)} bytes")
    
    return image_path

if __name__ == "__main__":
    create_emergency_alert_image()