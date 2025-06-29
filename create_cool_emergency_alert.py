#!/usr/bin/env python3
"""
Create a COOL emergency alert with amazing visual effects and modern styling
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
from datetime import datetime

def create_cool_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino", incident_type: str = "ALERTA GENERAL"):
    """
    Create a COOL emergency alert with awesome visual effects
    """
    
    # High-res dimensions for crisp details
    width = 600
    height = 800
    
    # Create base image
    image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # === EPIC BACKGROUND ===
    # Create multiple gradient layers for depth
    bg_image = Image.new('RGB', (width, height), color='#000000')
    bg_draw = ImageDraw.Draw(bg_image)
    
    # Layer 1: Deep red to bright red gradient
    for y in range(height):
        ratio = y / height
        # Complex multi-stop gradient
        if ratio < 0.2:
            r = int(60 + (140 - 60) * (ratio / 0.2))
            g = int(0 + (25 - 0) * (ratio / 0.2))
            b = int(0 + (25 - 0) * (ratio / 0.2))
        elif ratio < 0.4:
            mid_ratio = (ratio - 0.2) / 0.2
            r = int(140 + (220 - 140) * mid_ratio)
            g = int(25 + (60 - 25) * mid_ratio)
            b = int(25 + (60 - 25) * mid_ratio)
        elif ratio < 0.6:
            mid_ratio = (ratio - 0.4) / 0.2
            r = int(220 + (255 - 220) * mid_ratio)
            g = int(60 + (80 - 60) * mid_ratio)
            b = int(60 + (80 - 60) * mid_ratio)
        elif ratio < 0.8:
            mid_ratio = (ratio - 0.6) / 0.2
            r = int(255 + (200 - 255) * mid_ratio)
            g = int(80 + (40 - 80) * mid_ratio)
            b = int(80 + (40 - 80) * mid_ratio)
        else:
            bottom_ratio = (ratio - 0.8) / 0.2
            r = int(200 + (80 - 200) * bottom_ratio)
            g = int(40 + (10 - 40) * bottom_ratio)
            b = int(40 + (10 - 40) * bottom_ratio)
        
        bg_draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add COOL geometric patterns
    # Diagonal lines pattern
    for i in range(0, width + height, 40):
        bg_draw.line([(i, 0), (i - height, height)], fill=(255, 255, 255, 15), width=2)
    
    # Add circuit-like pattern
    for x in range(0, width, 80):
        for y in range(0, height, 80):
            # Draw tech-style corners
            corner_size = 10
            bg_draw.line([(x, y), (x + corner_size, y)], fill=(255, 255, 255, 20), width=1)
            bg_draw.line([(x, y), (x, y + corner_size)], fill=(255, 255, 255, 20), width=1)
    
    # Convert background to RGBA and add to main image
    bg_image = bg_image.convert('RGBA')
    image.paste(bg_image, (0, 0))
    
    # Load fonts
    try:
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        
        mega_font = None      # 52px - Epic titles
        title_font = None     # 40px - Main titles
        subtitle_font = None  # 28px - Subtitles
        header_font = None    # 22px - Headers
        text_font = None      # 18px - Text
        small_font = None     # 14px - Small text
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    mega_font = ImageFont.truetype(font_path, 52)
                    title_font = ImageFont.truetype(font_path, 40)
                    subtitle_font = ImageFont.truetype(font_path, 28)
                    header_font = ImageFont.truetype(font_path, 22)
                    text_font = ImageFont.truetype(font_path, 18)
                    small_font = ImageFont.truetype(font_path, 14)
                    break
                except Exception:
                    continue
        
        if not mega_font:
            mega_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            
    except Exception:
        mega_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # COOL color palette
    colors = {
        'neon_white': '#FFFFFF',
        'electric_gold': '#FFD700',
        'cyber_gold': '#FFF700',
        'plasma_orange': '#FF6600',
        'neon_blue': '#00CCFF',
        'electric_cyan': '#00FFFF',
        'laser_green': '#00FF00',
        'danger_red': '#FF0000',
        'deep_red': '#CC0000',
        'cyber_purple': '#CC00FF',
        'steel_gray': '#888888',
        'dark_steel': '#444444'
    }
    
    # Layout constants
    PADDING = 30
    MARGIN = 20
    y = PADDING + 15
    
    # === EPIC BORDER SYSTEM ===
    # Multiple glowing borders
    border_layers = [
        (8, colors['neon_white'], 6),      # Outer glow
        (4, colors['electric_gold'], 3),   # Middle glow
        (2, colors['cyber_gold'], 2),      # Inner glow
    ]
    
    for border_offset, border_color, border_width in border_layers:
        draw.rounded_rectangle(
            [border_offset, border_offset, width - border_offset - 1, height - border_offset - 1],
            radius=15, outline=border_color, width=border_width
        )
    
    # === EPIC WARNING SYSTEM ===
    # Multi-layer warning badge with glow effect
    badge_size = 70
    badge_x = (width - badge_size) // 2
    badge_y = y + 10
    
    # Outer glow rings
    for ring in range(3):
        ring_size = badge_size + (ring * 8)
        ring_x = (width - ring_size) // 2
        ring_y = badge_y - (ring * 4)
        alpha = 100 - (ring * 30)
        
        # Create temporary image for glow effect
        glow_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.ellipse([ring_x, ring_y, ring_x + ring_size, ring_y + ring_size], 
                         fill=(255, 215, 0, alpha))
        image = Image.alpha_composite(image, glow_img)
    
    # Main warning badge
    draw.ellipse([badge_x, badge_y, badge_x + badge_size, badge_y + badge_size], 
                 fill=colors['electric_gold'], outline=colors['neon_white'], width=4)
    
    # COOL exclamation mark with style
    mark_x = badge_x + badge_size // 2
    mark_y = badge_y + badge_size // 2
    
    # Exclamation shadow
    draw.line([(mark_x + 2, mark_y - 18), (mark_x + 2, mark_y + 6)], fill='#000000', width=8)
    draw.ellipse([mark_x - 1, mark_y + 12, mark_x + 5, mark_y + 18], fill='#000000')
    
    # Main exclamation
    draw.line([(mark_x, mark_y - 20), (mark_x, mark_y + 4)], fill='#000000', width=6)
    draw.ellipse([mark_x - 3, mark_y + 10, mark_x + 3, mark_y + 16], fill='#000000')
    
    y += badge_size + 35
    
    # === EPIC TITLE WITH GLOW ===
    title_text = "🚨 EMERGENCIA 🚨"
    draw_epic_text(draw, title_text, width//2, y, mega_font, colors['neon_white'], center=True, glow_color=colors['electric_gold'])
    y += 65
    
    # === INCIDENT TYPE WITH PLASMA EFFECT ===
    incident_bbox = draw.textbbox((0, 0), incident_type, font=subtitle_font)
    incident_width = incident_bbox[2] - incident_bbox[0]
    badge_width = incident_width + 50
    badge_height = 50
    badge_x = (width - badge_width) // 2
    
    # Create plasma-like background for incident badge
    plasma_img = Image.new('RGBA', (badge_width + 20, badge_height + 20), (0, 0, 0, 0))
    plasma_draw = ImageDraw.Draw(plasma_img)
    
    # Multiple colored layers for plasma effect
    for layer in range(3):
        layer_colors = [colors['danger_red'], colors['plasma_orange'], colors['electric_gold']]
        layer_radius = 25 - (layer * 3)
        plasma_draw.rounded_rectangle(
            [10 - layer, 10 - layer, badge_width + 10 + layer, badge_height + 10 + layer],
            radius=layer_radius, fill=layer_colors[layer], outline=colors['cyber_gold'], width=2
        )
    
    # Paste plasma badge
    image.paste(plasma_img, (badge_x - 10, y - 10), plasma_img)
    
    # Incident text with glow
    text_x = (width - incident_width) // 2
    draw_epic_text(draw, incident_type, text_x, y + 12, subtitle_font, colors['neon_white'])
    y += badge_height + 30
    
    # === SYSTEM TITLE WITH ELECTRIC EFFECT ===
    system_text = "SISTEMA DE ALARMA COMUNITARIA"
    draw_electric_text(draw, system_text, width//2, y, subtitle_font, colors['electric_gold'], center=True)
    y += 45
    
    # === STATUS WITH LASER EFFECT ===
    status_text = "⚡ ACTIVO ⚡"
    status_bbox = draw.textbbox((0, 0), status_text, font=text_font)
    status_width = status_bbox[2] - status_bbox[0]
    status_badge_width = status_width + 40
    status_badge_height = 40
    status_x = (width - status_badge_width) // 2
    
    # Laser-style status badge
    draw_laser_badge(draw, status_x, y, status_badge_width, status_badge_height, colors['laser_green'])
    
    text_x = (width - status_width) // 2
    draw_epic_text(draw, status_text, text_x, y + 10, text_font, colors['neon_white'])
    y += status_badge_height + 35
    
    # === CYBER INFO CARDS ===
    card_data = [
        ("📍 UBICACIÓN", street_address.upper(), colors['neon_blue']),
        ("👤 REPORTADO POR", contact_name.upper(), colors['electric_cyan']),
        ("📞 CONTACTO DIRECTO", phone_number, colors['plasma_orange'])
    ]
    
    card_height = 65
    card_spacing = 18
    
    for title, content, accent_color in card_data:
        draw_cyber_card(draw, PADDING, y, width - (2 * PADDING), card_height, 
                       title, content, accent_color, header_font, text_font)
        y += card_height + card_spacing
    
    y += 20
    
    # === EPIC EMERGENCY SECTION ===
    emergency_text = "🚨 EMERGENCIAS: 911 🚨"
    emergency_bbox = draw.textbbox((0, 0), emergency_text, font=title_font)
    emergency_width = emergency_bbox[2] - emergency_bbox[0]
    emergency_button_width = emergency_width + 60
    emergency_button_height = 60
    emergency_x = (width - emergency_button_width) // 2
    
    # Epic emergency button with multiple effects
    draw_epic_emergency_button(draw, emergency_x, y, emergency_button_width, emergency_button_height, colors)
    
    text_x = (width - emergency_width) // 2
    draw_epic_text(draw, emergency_text, text_x, y + 18, title_font, colors['neon_white'], glow_color=colors['danger_red'])
    y += emergency_button_height + 35
    
    # === FOOTER WITH STYLE ===
    timestamp = datetime.now().strftime("%H:%M hrs • %d/%m/%Y")
    
    # Timestamp with glow
    timestamp_text = f"⏰ {timestamp}"
    timestamp_bbox = draw.textbbox((0, 0), timestamp_text, font=small_font)
    timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
    timestamp_x = (width - timestamp_width) // 2
    draw_epic_text(draw, timestamp_text, timestamp_x, y, small_font, colors['steel_gray'])
    y += 25
    
    # Verification with cyber style
    verification = "🔒 SISTEMA VERIFICADO"
    verification_bbox = draw.textbbox((0, 0), verification, font=small_font)
    verification_width = verification_bbox[2] - verification_bbox[0]
    verification_x = (width - verification_width) // 2
    draw_epic_text(draw, verification, verification_x, y, small_font, colors['dark_steel'])
    
    # Convert to RGB for saving
    final_image = Image.new('RGB', (width, height), (255, 255, 255))
    final_image.paste(image, (0, 0), image)
    
    # Save image
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/cool_emergency_alert_{timestamp_file}.jpg"
    
    final_image.save(output_path, format='JPEG', quality=95, optimize=True)
    
    return output_path

def draw_epic_text(draw, text, x, y, font, color, center=False, glow_color=None):
    """Draw text with epic glow effects"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Add epic glow effect
    if glow_color:
        for glow_radius in [6, 4, 2]:
            glow_alpha = 60 - (glow_radius * 10)
            for dx in range(-glow_radius, glow_radius + 1):
                for dy in range(-glow_radius, glow_radius + 1):
                    if dx != 0 or dy != 0:
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance <= glow_radius:
                            draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
    
    # Shadow for depth
    draw.text((x + 2, y + 2), text, font=font, fill='#000000')
    
    # Main text
    draw.text((x, y), text, font=font, fill=color)

def draw_electric_text(draw, text, x, y, font, color, center=False):
    """Draw text with electric effect"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Electric glow layers
    electric_colors = ['#FFD700', '#FFF700', '#FFFF00']
    for i, electric_color in enumerate(electric_colors):
        offset = 3 - i
        draw.text((x + offset, y + offset), text, font=font, fill=electric_color)
    
    # Main text
    draw.text((x, y), text, font=font, fill=color)

def draw_laser_badge(draw, x, y, width, height, color):
    """Draw a laser-style badge with glow"""
    # Outer glow
    for glow in range(3):
        glow_offset = glow * 2
        glow_alpha = 80 - (glow * 25)
        glow_color = color + hex(glow_alpha)[2:].zfill(2)
        draw.rounded_rectangle([x - glow_offset, y - glow_offset, 
                               x + width + glow_offset, y + height + glow_offset],
                              radius=20 + glow_offset, outline=color, width=2)
    
    # Main badge
    draw.rounded_rectangle([x, y, x + width, y + height], 
                          radius=20, fill=color, outline='#FFFFFF', width=3)

def draw_cyber_card(draw, x, y, width, height, title, content, accent_color, title_font, content_font):
    """Draw a cyber-style information card"""
    
    # Card background with gradient effect
    for i in range(height):
        alpha = 0.8 - (i / height) * 0.4
        base_color = 50
        gray_val = int(base_color + (30 * alpha))
        draw.line([(x, y + i), (x + width, y + i)], fill=(gray_val, gray_val, gray_val))
    
    # Cyber border with corners
    draw.rounded_rectangle([x, y, x + width, y + height], 
                          radius=12, outline=accent_color, width=3)
    
    # Corner accents
    corner_size = 15
    # Top left
    draw.line([(x + corner_size, y), (x, y), (x, y + corner_size)], fill=accent_color, width=2)
    # Top right  
    draw.line([(x + width - corner_size, y), (x + width, y), (x + width, y + corner_size)], fill=accent_color, width=2)
    # Bottom left
    draw.line([(x, y + height - corner_size), (x, y + height), (x + corner_size, y + height)], fill=accent_color, width=2)
    # Bottom right
    draw.line([(x + width, y + height - corner_size), (x + width, y + height), (x + width - corner_size, y + height)], fill=accent_color, width=2)
    
    # Card content
    draw.text((x + 20, y + 12), title, font=title_font, fill=accent_color)
    draw.text((x + 20, y + 38), content, font=content_font, fill='#FFFFFF')

def draw_epic_emergency_button(draw, x, y, width, height, colors):
    """Draw an epic emergency button with multiple effects"""
    
    # Pulsing outer rings
    for ring in range(4):
        ring_offset = ring * 5
        ring_alpha = 100 - (ring * 20)
        draw.rounded_rectangle([x - ring_offset, y - ring_offset, 
                               x + width + ring_offset, y + height + ring_offset],
                              radius=30 + ring_offset, outline=colors['danger_red'], width=2)
    
    # Main button gradient
    for i in range(height):
        ratio = i / height
        r = int(220 + (180 - 220) * ratio)
        g = int(38 + (10 - 38) * ratio)
        b = int(38 + (10 - 38) * ratio)
        draw.line([(x, y + i), (x + width, y + i)], fill=(r, g, b))
    
    # Button border
    draw.rounded_rectangle([x, y, x + width, y + height], 
                          radius=30, outline=colors['electric_gold'], width=4)

def test_cool_design():
    """Test the COOL design"""
    
    print("🚀 Testing COOL Emergency Alert Design")
    print("=" * 60)
    print("✨ Adding EPIC visual effects and modern styling!")
    
    test_case = {
        "street_address": "Cyber Boulevard 2024",
        "phone_number": "56999888777",
        "contact_name": "Alex Neon",
        "incident_type": "SITUACIÓN CRÍTICA"
    }
    
    print(f"\n🎯 Test Case: {test_case['incident_type']}")
    print(f"   📍 Street: {test_case['street_address']}")
    print(f"   📱 Phone: {test_case['phone_number']}")
    print(f"   👤 Contact: {test_case['contact_name']}")
    
    try:
        print(f"\n🎨 Generating COOL emergency alert...")
        
        image_path = create_cool_emergency_alert(
            test_case['street_address'],
            test_case['phone_number'],
            test_case['contact_name'],
            test_case['incident_type']
        )
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ COOL Image created: {os.path.basename(image_path)}")
            print(f"📊 Size: {file_size} bytes")
            
            print(f"\n🎯 COOL Design Features:")
            print(f"   ⚡ Epic multi-layer gradient background")
            print(f"   🌟 Glowing warning badge with outer rings")
            print(f"   ✨ Text with glow and electric effects")
            print(f"   🎨 Plasma-style incident type badge")
            print(f"   💫 Laser-powered status indicator") 
            print(f"   🔮 Cyber-style information cards")
            print(f"   🚨 Epic emergency button with pulse rings")
            print(f"   🎪 Multiple border glow effects")
            print(f"   🌈 Modern color palette with neon accents")
            
            return image_path
        else:
            print("❌ Failed to create COOL alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_cool_design()
    if result:
        print(f"\n🏆 COOL design test completed!")
        print(f"🔥 This alert looks ABSOLUTELY AMAZING!")
    else:
        print(f"\n❌ Test failed!")