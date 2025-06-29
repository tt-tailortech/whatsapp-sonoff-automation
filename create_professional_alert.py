#!/usr/bin/env python3
"""
Create a professional-looking emergency alert image with modern design
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_professional_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino"):
    """
    Create a professional, modern emergency alert image
    
    Args:
        street_address: Street address to display
        phone_number: Phone number to display  
        contact_name: Name of the person reporting
    
    Returns:
        str: Path to the generated image
    """
    
    # Modern dimensions (16:9 aspect ratio, Instagram-friendly)
    width, height = 1080, 1080
    
    # Create base image with gradient background
    image = Image.new('RGB', (width, height), color='#000000')
    draw = ImageDraw.Draw(image)
    
    # Create gradient background (dark red to red)
    for y in range(height):
        # Calculate gradient from dark red to bright red
        ratio = y / height
        r = int(139 + (255 - 139) * ratio)  # From dark red to bright red
        g = int(0 + (69 - 0) * ratio)       # Dark to slight red tint
        b = int(0 + (0 - 0) * ratio)        # Stay at 0
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add diagonal pattern overlay for texture
    for i in range(0, width + height, 40):
        draw.line([(i, 0), (i - height, height)], fill=(255, 255, 255, 20), width=1)
    
    # Load fonts
    try:
        # Try to load system fonts
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/System/Library/Fonts/Arial.ttf",      # macOS fallback
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",           # Windows
        ]
        
        title_font = None
        header_font = None
        main_font = None
        detail_font = None
        small_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    title_font = ImageFont.truetype(font_path, 85)   # Large title
                    header_font = ImageFont.truetype(font_path, 65)  # Headers
                    main_font = ImageFont.truetype(font_path, 45)    # Main text
                    detail_font = ImageFont.truetype(font_path, 38)  # Details
                    small_font = ImageFont.truetype(font_path, 28)   # Small text
                    break
                except Exception:
                    continue
        
        # Fallback to default font
        if not title_font:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            main_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            
    except Exception:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Define colors
    white = '#FFFFFF'
    yellow = '#FFD700'
    orange = '#FFA500'
    light_blue = '#87CEEB'
    bright_white = '#FFFFFF'
    emergency_red = '#FF0000'
    
    # Add main border with rounded corners effect
    border_width = 12
    draw.rectangle(
        [border_width, border_width, width-border_width, height-border_width],
        outline=white,
        width=border_width
    )
    
    # Add inner shadow effect
    shadow_width = 6
    draw.rectangle(
        [border_width + shadow_width, border_width + shadow_width, 
         width-border_width-shadow_width, height-border_width-shadow_width],
        outline='#CCCCCC',
        width=2
    )
    
    # Emergency icon area (top section)
    icon_y = 80
    
    # Draw emergency symbol (triangle with exclamation)
    triangle_size = 60
    triangle_x = width // 2
    triangle_y = icon_y + 40
    
    # Draw warning triangle
    triangle_points = [
        (triangle_x, triangle_y - triangle_size//2),
        (triangle_x - triangle_size//2, triangle_y + triangle_size//2),
        (triangle_x + triangle_size//2, triangle_y + triangle_size//2)
    ]
    draw.polygon(triangle_points, fill=yellow, outline=white, width=3)
    
    # Draw exclamation mark in triangle
    draw.line([(triangle_x, triangle_y - 15), (triangle_x, triangle_y + 5)], fill='#000000', width=6)
    draw.ellipse([(triangle_x-3, triangle_y + 12), (triangle_x+3, triangle_y + 18)], fill='#000000')
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%H:%M hrs - %d/%m/%Y")
    
    # Text content with professional spacing
    y_pos = 200
    
    # Main title
    draw_text_with_shadow(draw, "ALERTA DE EMERGENCIA", width//2, y_pos, title_font, white, center=True)
    y_pos += 120
    
    # Subtitle
    draw_text_with_shadow(draw, "SISTEMA DE ALARMA COMUNITARIA", width//2, y_pos, header_font, yellow, center=True)
    y_pos += 100
    
    # Status indicator
    draw_rounded_rectangle(draw, (width//2 - 180, y_pos - 10), (width//2 + 180, y_pos + 50), 
                          fill='#FF4444', outline=white, corner_radius=25, width=3)
    draw_text_with_shadow(draw, "🚨 ACTIVADO", width//2, y_pos + 20, main_font, white, center=True)
    y_pos += 120
    
    # Location section
    draw_text_with_shadow(draw, "📍 UBICACIÓN:", 80, y_pos, detail_font, light_blue)
    y_pos += 60
    draw_text_with_shadow(draw, street_address.upper(), 80, y_pos, main_font, yellow)
    y_pos += 100
    
    # Contact section
    draw_text_with_shadow(draw, "👤 REPORTADO POR:", 80, y_pos, detail_font, light_blue)
    y_pos += 60
    draw_text_with_shadow(draw, contact_name.upper(), 80, y_pos, main_font, white)
    y_pos += 100
    
    # Phone section
    draw_text_with_shadow(draw, "📞 CONTACTO DIRECTO:", 80, y_pos, detail_font, light_blue)
    y_pos += 60
    draw_text_with_shadow(draw, phone_number, 80, y_pos, main_font, yellow)
    y_pos += 80
    
    # Emergency contact
    draw_rounded_rectangle(draw, (80, y_pos), (width - 80, y_pos + 70), 
                          fill='#CC0000', outline=white, corner_radius=15, width=2)
    draw_text_with_shadow(draw, "🚨 EMERGENCIAS: 911", width//2, y_pos + 35, main_font, white, center=True)
    y_pos += 100
    
    # Timestamp at bottom
    draw_text_with_shadow(draw, f"⏰ {timestamp}", width//2, height - 60, small_font, '#CCCCCC', center=True)
    
    # Generate unique filename
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/professional_alert_{timestamp_file}.jpg"
    
    # Save with high quality
    image.save(output_path, format='JPEG', quality=95, optimize=True)
    
    return output_path

def draw_text_with_shadow(draw, text, x, y, font, color, center=False, shadow_color='#000000', shadow_offset=2):
    """Draw text with drop shadow for better readability"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Draw shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=color)

def draw_rounded_rectangle(draw, top_left, bottom_right, fill=None, outline=None, corner_radius=10, width=1):
    """Draw a rounded rectangle"""
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Draw main rectangle
    draw.rectangle([x1, y1 + corner_radius, x2, y2 - corner_radius], fill=fill, outline=outline, width=width)
    draw.rectangle([x1 + corner_radius, y1, x2 - corner_radius, y2], fill=fill, outline=outline, width=width)
    
    # Draw corners
    draw.ellipse([x1, y1, x1 + 2*corner_radius, y1 + 2*corner_radius], fill=fill, outline=outline, width=width)
    draw.ellipse([x2 - 2*corner_radius, y1, x2, y1 + 2*corner_radius], fill=fill, outline=outline, width=width)
    draw.ellipse([x1, y2 - 2*corner_radius, x1 + 2*corner_radius, y2], fill=fill, outline=outline, width=width)
    draw.ellipse([x2 - 2*corner_radius, y2 - 2*corner_radius, x2, y2], fill=fill, outline=outline, width=width)

def test_professional_design():
    """Test the new professional design"""
    
    print("🎨 Testing Professional Emergency Alert Design")
    print("=" * 60)
    
    # Test with sample data
    street_address = "AVENIDA PRINCIPAL 123"
    phone_number = "56912345678"
    contact_name = "Maria Rodriguez"
    
    print(f"📍 Street: {street_address}")
    print(f"📱 Phone: {phone_number}")
    print(f"👤 Contact: {contact_name}")
    
    try:
        print(f"\n🎨 Generating professional emergency alert...")
        image_path = create_professional_emergency_alert(street_address, phone_number, contact_name)
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ SUCCESS! Professional alert created:")
            print(f"   📂 File: {os.path.basename(image_path)}")
            print(f"   📊 Size: {file_size} bytes")
            print(f"   📁 Location: {image_path}")
            print(f"\n🎯 Much more professional design with:")
            print(f"   • Gradient background")
            print(f"   • Warning triangle icon")
            print(f"   • Rounded sections")
            print(f"   • Better typography")
            print(f"   • Visual hierarchy")
            print(f"   • Drop shadows")
            return image_path
        else:
            print("❌ Failed to create professional alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_professional_design()
    if result:
        print(f"\n🏁 Professional design test completed!")
    else:
        print(f"\n❌ Professional design test failed!")