#!/usr/bin/env python3
"""
Create a SUPER COOL emergency alert with amazing effects that actually work!
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math
from datetime import datetime

def create_super_cool_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino", incident_type: str = "ALERTA GENERAL"):
    """
    Create a SUPER COOL emergency alert with working visual effects
    """
    
    # Dimensions
    width = 600
    height = 800
    
    # Create image
    image = Image.new('RGB', (width, height), color='#000000')
    draw = ImageDraw.Draw(image)
    
    # === EPIC GRADIENT BACKGROUND ===
    for y in range(height):
        ratio = y / height
        if ratio < 0.3:
            # Top - dark red to bright red
            r = int(80 + (200 - 80) * (ratio / 0.3))
            g = int(10 + (50 - 10) * (ratio / 0.3))
            b = int(10 + (50 - 10) * (ratio / 0.3))
        elif ratio < 0.7:
            # Middle - bright red
            mid_ratio = (ratio - 0.3) / 0.4
            r = int(200 + (255 - 200) * mid_ratio)
            g = int(50 + (70 - 50) * mid_ratio)
            b = int(50 + (70 - 50) * mid_ratio)
        else:
            # Bottom - back to darker
            bottom_ratio = (ratio - 0.7) / 0.3
            r = int(255 + (120 - 255) * bottom_ratio)
            g = int(70 + (20 - 70) * bottom_ratio)
            b = int(70 + (20 - 70) * bottom_ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add COOL diagonal pattern
    for i in range(0, width + height, 50):
        draw.line([(i, 0), (i - height, height)], fill=(255, 255, 255, 25), width=2)
    
    # Add tech grid pattern
    for x in range(0, width, 100):
        for y_grid in range(0, height, 100):
            # Draw small tech corners
            corner_size = 8
            draw.line([(x, y_grid), (x + corner_size, y_grid)], fill=(255, 255, 255, 30), width=2)
            draw.line([(x, y_grid), (x, y_grid + corner_size)], fill=(255, 255, 255, 30), width=2)
    
    # Load fonts
    try:
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        
        mega_font = None
        title_font = None
        subtitle_font = None
        header_font = None
        text_font = None
        small_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    mega_font = ImageFont.truetype(font_path, 50)
                    title_font = ImageFont.truetype(font_path, 38)
                    subtitle_font = ImageFont.truetype(font_path, 28)
                    header_font = ImageFont.truetype(font_path, 20)
                    text_font = ImageFont.truetype(font_path, 16)
                    small_font = ImageFont.truetype(font_path, 12)
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
    
    # Colors
    WHITE = '#FFFFFF'
    GOLD = '#FFD700'
    CYAN = '#00FFFF'
    ORANGE = '#FF8C00'
    GREEN = '#00FF00'
    RED = '#FF0000'
    BLUE = '#4169E1'
    
    # Layout
    PADDING = 30
    y = PADDING + 15
    
    # === TRIPLE GLOW BORDER ===
    # Outer glow
    draw.rounded_rectangle([3, 3, width-4, height-4], radius=18, outline=WHITE, width=6)
    # Middle glow  
    draw.rounded_rectangle([8, 8, width-9, height-9], radius=15, outline=GOLD, width=4)
    # Inner glow
    draw.rounded_rectangle([12, 12, width-13, height-13], radius=12, outline=CYAN, width=2)
    
    # === GLOWING WARNING BADGE ===
    badge_size = 80
    badge_x = (width - badge_size) // 2
    
    # Outer glow rings
    for ring in [12, 8, 4]:
        ring_x = badge_x - ring
        ring_y = y - ring
        ring_size = badge_size + (ring * 2)
        draw.ellipse([ring_x, ring_y, ring_x + ring_size, ring_y + ring_size], 
                     outline=GOLD, width=2)
    
    # Main badge
    draw.ellipse([badge_x, y, badge_x + badge_size, y + badge_size], 
                 fill=GOLD, outline=WHITE, width=5)
    
    # Exclamation mark
    mark_x = badge_x + badge_size // 2
    mark_y = y + badge_size // 2
    draw.line([(mark_x, mark_y - 20), (mark_x, mark_y + 8)], fill='#000000', width=8)
    draw.ellipse([mark_x - 4, mark_y + 15, mark_x + 4, mark_y + 23], fill='#000000')
    
    y += badge_size + 40
    
    # === TITLE WITH EPIC GLOW ===
    title_text = "🚨 EMERGENCIA 🚨"
    draw_glow_text(draw, title_text, width//2, y, mega_font, WHITE, GOLD, center=True)
    y += 70
    
    # === INCIDENT BADGE ===
    incident_bbox = draw.textbbox((0, 0), incident_type, font=subtitle_font)
    incident_width = incident_bbox[2] - incident_bbox[0]
    badge_width = incident_width + 60
    badge_height = 55
    badge_x = (width - badge_width) // 2
    
    # Triple-layer incident badge
    draw.rounded_rectangle([badge_x - 3, y - 3, badge_x + badge_width + 3, y + badge_height + 3], 
                          radius=30, outline=ORANGE, width=3)
    draw.rounded_rectangle([badge_x, y, badge_x + badge_width, y + badge_height], 
                          radius=25, fill=RED, outline=GOLD, width=4)
    
    # Incident text
    text_x = (width - incident_width) // 2
    draw_glow_text(draw, incident_type, text_x, y + 15, subtitle_font, WHITE, RED)
    y += badge_height + 35
    
    # === SYSTEM TITLE ===
    system_text = "SISTEMA DE ALARMA COMUNITARIA"
    draw_glow_text(draw, system_text, width//2, y, subtitle_font, GOLD, ORANGE, center=True)
    y += 45
    
    # === STATUS BADGE WITH PULSE ===
    status_text = "⚡ ACTIVO ⚡"
    status_bbox = draw.textbbox((0, 0), status_text, font=text_font)
    status_width = status_bbox[2] - status_bbox[0]
    status_badge_width = status_width + 50
    status_badge_height = 45
    status_x = (width - status_badge_width) // 2
    
    # Pulse rings
    for pulse in [8, 5, 2]:
        pulse_x = status_x - pulse
        pulse_y = y - pulse
        pulse_w = status_badge_width + (pulse * 2)
        pulse_h = status_badge_height + (pulse * 2)
        draw.rounded_rectangle([pulse_x, pulse_y, pulse_x + pulse_w, pulse_y + pulse_h],
                              radius=25 + pulse, outline=GREEN, width=2)
    
    # Main status badge
    draw.rounded_rectangle([status_x, y, status_x + status_badge_width, y + status_badge_height],
                          radius=25, fill=GREEN, outline=WHITE, width=3)
    
    text_x = (width - status_width) // 2
    draw_glow_text(draw, status_text, text_x, y + 12, text_font, WHITE, GREEN)
    y += status_badge_height + 40
    
    # === NEON INFO CARDS ===
    card_data = [
        ("📍 UBICACIÓN", street_address.upper(), CYAN),
        ("👤 REPORTADO POR", contact_name.upper(), BLUE),
        ("📞 CONTACTO DIRECTO", phone_number, ORANGE)
    ]
    
    card_height = 70
    card_spacing = 20
    
    for title, content, neon_color in card_data:
        card_x = PADDING
        card_width = width - (2 * PADDING)
        
        # Neon card with glow
        draw.rounded_rectangle([card_x - 2, y - 2, card_x + card_width + 2, y + card_height + 2],
                              radius=15, outline=neon_color, width=3)
        
        # Card background
        for i in range(card_height):
            alpha = 0.8 - (i / card_height) * 0.4
            gray_val = int(40 + (30 * alpha))
            draw.line([(card_x, y + i), (card_x + card_width, y + i)], fill=(gray_val, gray_val, gray_val))
        
        # Neon corners
        corner_size = 12
        corners = [
            (card_x, y),  # Top left
            (card_x + card_width - corner_size, y),  # Top right
            (card_x, y + card_height - corner_size),  # Bottom left
            (card_x + card_width - corner_size, y + card_height - corner_size)  # Bottom right
        ]
        
        for corner_x, corner_y in corners:
            draw.line([(corner_x, corner_y), (corner_x + corner_size, corner_y)], fill=neon_color, width=3)
            draw.line([(corner_x, corner_y), (corner_x, corner_y + corner_size)], fill=neon_color, width=3)
        
        # Card text
        draw.text((card_x + 20, y + 15), title, font=header_font, fill=neon_color)
        draw.text((card_x + 20, y + 42), content, font=text_font, fill=WHITE)
        
        y += card_height + card_spacing
    
    y += 25
    
    # === EPIC EMERGENCY BUTTON ===
    emergency_text = "🚨 EMERGENCIAS: 911 🚨"
    emergency_bbox = draw.textbbox((0, 0), emergency_text, font=title_font)
    emergency_width = emergency_bbox[2] - emergency_bbox[0]
    button_width = emergency_width + 80
    button_height = 65
    button_x = (width - button_width) // 2
    
    # Emergency pulse rings
    for pulse in [15, 10, 5]:
        pulse_x = button_x - pulse
        pulse_y = y - pulse
        pulse_w = button_width + (pulse * 2)
        pulse_h = button_height + (pulse * 2)
        draw.rounded_rectangle([pulse_x, pulse_y, pulse_x + pulse_w, pulse_y + pulse_h],
                              radius=35 + pulse, outline=RED, width=3)
    
    # Main emergency button
    draw.rounded_rectangle([button_x, y, button_x + button_width, y + button_height],
                          radius=35, fill=RED, outline=GOLD, width=5)
    
    # Emergency text
    text_x = (width - emergency_width) // 2
    draw_glow_text(draw, emergency_text, text_x, y + 20, title_font, WHITE, RED)
    y += button_height + 40
    
    # === FOOTER ===
    timestamp = datetime.now().strftime("%H:%M hrs • %d/%m/%Y")
    
    # Timestamp
    timestamp_text = f"⏰ {timestamp}"
    timestamp_bbox = draw.textbbox((0, 0), timestamp_text, font=small_font)
    timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
    timestamp_x = (width - timestamp_width) // 2
    draw.text((timestamp_x, y), timestamp_text, font=small_font, fill='#CCCCCC')
    y += 20
    
    # Verification
    verification = "🔒 SISTEMA VERIFICADO"
    verification_bbox = draw.textbbox((0, 0), verification, font=small_font)
    verification_width = verification_bbox[2] - verification_bbox[0]
    verification_x = (width - verification_width) // 2
    draw.text((verification_x, y), verification, font=small_font, fill='#999999')
    
    # Save image
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/super_cool_alert_{timestamp_file}.jpg"
    
    image.save(output_path, format='JPEG', quality=95, optimize=True)
    
    return output_path

def draw_glow_text(draw, text, x, y, font, text_color, glow_color, center=False):
    """Draw text with glow effect"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Glow effect
    for glow_offset in [4, 3, 2, 1]:
        for dx in [-glow_offset, 0, glow_offset]:
            for dy in [-glow_offset, 0, glow_offset]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
    
    # Shadow
    draw.text((x + 2, y + 2), text, font=font, fill='#000000')
    
    # Main text
    draw.text((x, y), text, font=font, fill=text_color)

def test_super_cool_design():
    """Test the SUPER COOL design"""
    
    print("🔥 Testing SUPER COOL Emergency Alert Design")
    print("=" * 60)
    print("⚡ Epic effects that actually work!")
    
    test_case = {
        "street_address": "Neo Tokyo Street 2077",
        "phone_number": "56888999000",
        "contact_name": "Cyber Phoenix",
        "incident_type": "CÓDIGO ROJO"
    }
    
    print(f"\n🎯 Test Case: {test_case['incident_type']}")
    print(f"   📍 Street: {test_case['street_address']}")
    print(f"   📱 Phone: {test_case['phone_number']}")
    print(f"   👤 Contact: {test_case['contact_name']}")
    
    try:
        print(f"\n🔥 Generating SUPER COOL emergency alert...")
        
        image_path = create_super_cool_emergency_alert(
            test_case['street_address'],
            test_case['phone_number'],
            test_case['contact_name'],
            test_case['incident_type']
        )
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ SUPER COOL Image created: {os.path.basename(image_path)}")
            print(f"📊 Size: {file_size} bytes")
            
            print(f"\n🔥 SUPER COOL Features:")
            print(f"   ⚡ Epic multi-layer gradient background")
            print(f"   🌟 Triple glow border system")
            print(f"   💫 Glowing warning badge with pulse rings")
            print(f"   ✨ Text with working glow effects")
            print(f"   🎨 Neon-style information cards")
            print(f"   🚨 Epic emergency button with pulse animation")
            print(f"   🌈 Tech grid and diagonal patterns")
            print(f"   💎 Perfect spacing and layout")
            
            return image_path
        else:
            print("❌ Failed to create SUPER COOL alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_super_cool_design()
    if result:
        print(f"\n🏆 SUPER COOL design test completed!")
        print(f"🔥 This alert is ABSOLUTELY EPIC!")
    else:
        print(f"\n❌ Test failed!")