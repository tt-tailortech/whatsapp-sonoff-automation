#!/usr/bin/env python3
"""
Create an ULTRA-professional emergency alert image with modern, sleek design
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math
from datetime import datetime

def create_ultra_professional_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino", incident_type: str = "ALERTA GENERAL"):
    """
    Create an ultra-professional, modern emergency alert image with advanced design
    
    Args:
        street_address: Street address to display
        phone_number: Phone number to display  
        contact_name: Name of the person reporting
        incident_type: Type of incident (e.g., "ROBO", "EMERGENCIA MÉDICA", "INCENDIO")
    
    Returns:
        str: Path to the generated image
    """
    
    # High-quality dimensions
    width, height = 1080, 1350  # Vertical format for mobile
    
    # Create base image
    image = Image.new('RGB', (width, height), color='#000000')
    draw = ImageDraw.Draw(image)
    
    # Create sophisticated gradient background (dark to bright red with subtle variations)
    for y in range(height):
        ratio = y / height
        # More complex gradient with multiple stops
        if ratio < 0.3:
            # Top section - darker red with blue tint
            r = int(50 + (120 - 50) * (ratio / 0.3))
            g = int(0 + (20 - 0) * (ratio / 0.3))
            b = int(20 + (30 - 20) * (ratio / 0.3))
        elif ratio < 0.7:
            # Middle section - bright red
            mid_ratio = (ratio - 0.3) / 0.4
            r = int(120 + (220 - 120) * mid_ratio)
            g = int(20 + (50 - 20) * mid_ratio)
            b = int(30 + (40 - 30) * mid_ratio)
        else:
            # Bottom section - darker red again
            bottom_ratio = (ratio - 0.7) / 0.3
            r = int(220 + (80 - 220) * bottom_ratio)
            g = int(50 + (15 - 50) * bottom_ratio)
            b = int(40 + (20 - 40) * bottom_ratio)
        
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Add subtle texture pattern
    for i in range(0, width + height, 60):
        draw.line([(i, 0), (i - height, height)], fill=(255, 255, 255, 8), width=1)
    for i in range(0, width + height, 80):
        draw.line([(0, i), (width, i - width)], fill=(255, 255, 255, 4), width=1)
    
    # Load premium fonts
    try:
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SF-Pro-Display-Bold.otf",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        
        mega_font = None      # Ultra large
        title_font = None     # Large title
        header_font = None    # Headers
        main_font = None      # Main text
        detail_font = None    # Details
        small_font = None     # Small text
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    mega_font = ImageFont.truetype(font_path, 95)    # Mega title
                    title_font = ImageFont.truetype(font_path, 75)   # Large title
                    header_font = ImageFont.truetype(font_path, 55)  # Headers
                    main_font = ImageFont.truetype(font_path, 42)    # Main text
                    detail_font = ImageFont.truetype(font_path, 35)  # Details
                    small_font = ImageFont.truetype(font_path, 26)   # Small text
                    break
                except Exception:
                    continue
        
        # Fallback
        if not mega_font:
            mega_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            main_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            
    except Exception:
        mega_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Premium color palette
    colors = {
        'white': '#FFFFFF',
        'gold': '#FFD700',
        'bright_gold': '#FFF700',
        'orange': '#FF8C00',
        'light_blue': '#87CEEB',
        'cyan': '#00FFFF',
        'lime': '#32CD32',
        'emergency_red': '#FF0000',
        'dark_red': '#8B0000',
        'silver': '#C0C0C0',
        'black': '#000000',
        'gray': '#808080'
    }
    
    # Add premium border with multiple layers
    border_configs = [
        (15, colors['white'], 8),    # Outer white border
        (8, colors['gold'], 4),      # Gold accent border
        (4, colors['white'], 2),     # Inner white border
    ]
    
    for border_width, border_color, line_width in border_configs:
        draw.rectangle(
            [border_width, border_width, width-border_width, height-border_width],
            outline=border_color,
            width=line_width
        )
    
    # === HEADER SECTION ===
    y_pos = 60
    
    # Draw premium warning symbol (hexagonal badge)
    badge_center_x = width // 2
    badge_center_y = y_pos + 80
    badge_radius = 50
    
    # Draw hexagonal warning badge
    draw_hexagon(draw, badge_center_x, badge_center_y, badge_radius, 
                fill=colors['gold'], outline=colors['white'], width=4)
    
    # Draw exclamation in badge
    draw.line([(badge_center_x, badge_center_y - 25), (badge_center_x, badge_center_y + 5)], 
              fill=colors['black'], width=8)
    draw.ellipse([(badge_center_x-5, badge_center_y + 15), (badge_center_x+5, badge_center_y + 25)], 
                 fill=colors['black'])
    
    y_pos += 180
    
    # === MAIN TITLE SECTION ===
    draw_premium_text(draw, "🚨 EMERGENCIA 🚨", width//2, y_pos, mega_font, colors['white'], center=True, glow=True)
    y_pos += 110
    
    # Incident type badge
    incident_width = len(incident_type) * 25 + 60
    draw_rounded_rectangle(draw, 
                          (width//2 - incident_width//2, y_pos - 15), 
                          (width//2 + incident_width//2, y_pos + 55), 
                          fill=colors['emergency_red'], 
                          outline=colors['gold'], 
                          corner_radius=30, 
                          width=4)
    draw_premium_text(draw, incident_type, width//2, y_pos + 20, header_font, colors['white'], center=True)
    y_pos += 120
    
    # System status
    draw_premium_text(draw, "SISTEMA DE ALARMA COMUNITARIA", width//2, y_pos, title_font, colors['gold'], center=True)
    y_pos += 80
    
    # Status indicator with animation-style elements
    status_rect = (width//2 - 200, y_pos - 15, width//2 + 200, y_pos + 55)
    draw_rounded_rectangle(draw, status_rect[:2], status_rect[2:], 
                          fill=colors['lime'], outline=colors['white'], corner_radius=35, width=3)
    draw_premium_text(draw, "⚡ ACTIVO ⚡", width//2, y_pos + 20, main_font, colors['black'], center=True, bold=True)
    y_pos += 120
    
    # === INFORMATION CARDS SECTION ===
    card_margin = 40
    card_width = width - (2 * card_margin)
    
    # Location Card
    card_y = y_pos
    draw_info_card(draw, card_margin, card_y, card_width, 100, "📍 UBICACIÓN", street_address.upper(), 
                   colors['light_blue'], colors['white'], colors['gold'], main_font, detail_font)
    y_pos += 140
    
    # Contact Card  
    draw_info_card(draw, card_margin, y_pos, card_width, 100, "👤 REPORTADO POR", contact_name.upper(), 
                   colors['cyan'], colors['white'], colors['white'], main_font, detail_font)
    y_pos += 140
    
    # Phone Card
    draw_info_card(draw, card_margin, y_pos, card_width, 100, "📞 CONTACTO DIRECTO", phone_number, 
                   colors['orange'], colors['white'], colors['gold'], main_font, detail_font)
    y_pos += 160
    
    # === EMERGENCY SECTION ===
    # Emergency contact - premium style
    emergency_rect = (card_margin, y_pos, width - card_margin, y_pos + 90)
    draw_rounded_rectangle(draw, emergency_rect[:2], emergency_rect[2:], 
                          fill=colors['emergency_red'], outline=colors['gold'], corner_radius=25, width=5)
    
    # Add pulse effect lines
    for i in range(3):
        offset = 10 + (i * 8)
        draw_rounded_rectangle(draw, 
                              (card_margin - offset, y_pos - offset), 
                              (width - card_margin + offset, y_pos + 90 + offset), 
                              fill=None, outline=colors['white'], corner_radius=25 + offset, width=2)
    
    draw_premium_text(draw, "🚨 EMERGENCIAS: 911 🚨", width//2, y_pos + 45, title_font, colors['white'], center=True, glow=True)
    y_pos += 130
    
    # === FOOTER SECTION ===
    # Timestamp with modern styling
    timestamp = datetime.now().strftime("%H:%M hrs • %d/%m/%Y")
    draw_premium_text(draw, f"⏰ {timestamp}", width//2, height - 80, small_font, colors['silver'], center=True)
    
    # Security badge
    draw_premium_text(draw, "🔒 SISTEMA VERIFICADO", width//2, height - 45, small_font, colors['gray'], center=True)
    
    # Generate unique filename
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/ultra_professional_alert_{timestamp_file}.jpg"
    
    # Save with maximum quality
    image.save(output_path, format='JPEG', quality=98, optimize=True)
    
    return output_path

def draw_hexagon(draw, center_x, center_y, radius, fill=None, outline=None, width=1):
    """Draw a hexagon shape"""
    points = []
    for i in range(6):
        angle = i * math.pi / 3
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill, outline=outline, width=width)

def draw_premium_text(draw, text, x, y, font, color, center=False, glow=False, bold=False):
    """Draw text with premium effects"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Add glow effect
    if glow:
        for offset in [4, 3, 2, 1]:
            glow_color = '#444444' if offset > 2 else '#666666'
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
    
    # Add shadow for depth
    draw.text((x + 3, y + 3), text, font=font, fill='#000000')
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=color)

def draw_info_card(draw, x, y, width, height, title, content, title_color, content_color, border_color, title_font, content_font):
    """Draw an information card with modern styling"""
    # Card background with subtle gradient
    for i in range(height):
        alpha = 1 - (i / height) * 0.3
        gray_value = int(40 + (20 * alpha))
        draw.line([(x, y + i), (x + width, y + i)], fill=(gray_value, gray_value, gray_value))
    
    # Card border
    draw_rounded_rectangle(draw, (x, y), (x + width, y + height), 
                          fill=None, outline=border_color, corner_radius=20, width=3)
    
    # Title
    draw_premium_text(draw, title, x + 20, y + 15, title_font, title_color)
    
    # Content
    draw_premium_text(draw, content, x + 20, y + 55, content_font, content_color, bold=True)

def draw_rounded_rectangle(draw, top_left, bottom_right, fill=None, outline=None, corner_radius=10, width=1):
    """Draw a rounded rectangle with better corner handling"""
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Main rectangle parts
    draw.rectangle([x1 + corner_radius, y1, x2 - corner_radius, y2], fill=fill, outline=outline, width=width)
    draw.rectangle([x1, y1 + corner_radius, x2, y2 - corner_radius], fill=fill, outline=outline, width=width)
    
    # Corner circles
    d = 2 * corner_radius
    draw.ellipse([x1, y1, x1 + d, y1 + d], fill=fill, outline=outline, width=width)
    draw.ellipse([x2 - d, y1, x2, y1 + d], fill=fill, outline=outline, width=width)
    draw.ellipse([x1, y2 - d, x1 + d, y2], fill=fill, outline=outline, width=width)
    draw.ellipse([x2 - d, y2 - d, x2, y2], fill=fill, outline=outline, width=width)

def test_ultra_professional_design():
    """Test the ultra-professional design"""
    
    print("🚀 Testing ULTRA-Professional Emergency Alert Design")
    print("=" * 70)
    
    # Test cases with different incident types
    test_cases = [
        {
            "street_address": "BOULEVARD CENTRAL 789",
            "phone_number": "56987654321",
            "contact_name": "Carlos Mendoza",
            "incident_type": "ROBO EN PROGRESO"
        },
        {
            "street_address": "CALLE LIBERTAD 456", 
            "phone_number": "56912345678",
            "contact_name": "Ana Torres",
            "incident_type": "EMERGENCIA MÉDICA"
        }
    ]
    
    generated_images = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}: {test_case['incident_type']}")
        print(f"   📍 Street: {test_case['street_address']}")
        print(f"   📱 Phone: {test_case['phone_number']}")
        print(f"   👤 Contact: {test_case['contact_name']}")
        
        try:
            image_path = create_ultra_professional_emergency_alert(
                test_case['street_address'],
                test_case['phone_number'],
                test_case['contact_name'],
                test_case['incident_type']
            )
            
            if os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                print(f"   ✅ Generated: {os.path.basename(image_path)}")
                print(f"   📊 Size: {file_size} bytes")
                generated_images.append(image_path)
            else:
                print(f"   ❌ Failed to create image")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎨 Ultra-Professional Features Added:")
    print(f"   • Hexagonal warning badge")
    print(f"   • Multi-layer gradient background")
    print(f"   • Information cards with shadows")
    print(f"   • Glow effects on important text")
    print(f"   • Premium border styling")
    print(f"   • Pulse effect on emergency section")
    print(f"   • Modern typography hierarchy")
    print(f"   • Security verification badge")
    
    print(f"\n📋 Results: {len(generated_images)}/{len(test_cases)} successful")
    
    return len(generated_images) > 0, generated_images

if __name__ == "__main__":
    success, images = test_ultra_professional_design()
    if success:
        print(f"\n🏆 ULTRA-Professional design test completed!")
        print(f"📁 Check the generated images - they look amazing!")
    else:
        print(f"\n❌ Test failed!")