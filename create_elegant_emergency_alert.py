#!/usr/bin/env python3
"""
Create an elegant, sophisticated, and modern emergency alert 
Inspired by premium design aesthetics like Apple, Tesla, and luxury brands
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_elegant_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino", incident_type: str = "ALERTA GENERAL"):
    """
    Create an elegant, sophisticated emergency alert with premium design
    """
    
    # Premium dimensions (golden ratio inspired)
    width = 600
    height = 800
    
    # Create image with premium background
    image = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(image)
    
    # === SOPHISTICATED GRADIENT ===
    # Subtle, elegant gradient from light to darker tones
    for y in range(height):
        ratio = y / height
        # Elegant red gradient with sophistication
        if ratio < 0.4:
            # Top - subtle warm gray to light red
            r = int(248 + (240 - 248) * (ratio / 0.4))
            g = int(248 + (230 - 248) * (ratio / 0.4))
            b = int(248 + (230 - 248) * (ratio / 0.4))
        elif ratio < 0.6:
            # Middle - elegant red tones
            mid_ratio = (ratio - 0.4) / 0.2
            r = int(240 + (220 - 240) * mid_ratio)
            g = int(230 + (200 - 230) * mid_ratio)
            b = int(230 + (200 - 230) * mid_ratio)
        else:
            # Bottom - sophisticated darker red
            bottom_ratio = (ratio - 0.6) / 0.4
            r = int(220 + (200 - 220) * bottom_ratio)
            g = int(200 + (180 - 200) * bottom_ratio)
            b = int(200 + (180 - 200) * bottom_ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Subtle texture overlay (very refined)
    for i in range(0, width, 120):
        for j in range(0, height, 120):
            draw.point((i, j), fill=(255, 255, 255, 40))
    
    # Load premium fonts
    try:
        font_paths = [
            "/System/Library/Fonts/SF-Pro-Display-Bold.otf",  # macOS premium
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/segoeui.ttf",  # Windows premium
        ]
        
        title_font = None      # 42px - Elegant titles
        subtitle_font = None   # 28px - Subtitles  
        header_font = None     # 18px - Headers
        text_font = None       # 16px - Body text
        small_font = None      # 12px - Small text
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    title_font = ImageFont.truetype(font_path, 42)
                    subtitle_font = ImageFont.truetype(font_path, 28)
                    header_font = ImageFont.truetype(font_path, 18)
                    text_font = ImageFont.truetype(font_path, 16)
                    small_font = ImageFont.truetype(font_path, 12)
                    break
                except Exception:
                    continue
        
        if not title_font:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Sophisticated color palette
    colors = {
        'charcoal': '#2C2C2C',      # Deep, sophisticated dark
        'platinum': '#E8E8E8',      # Premium light gray
        'crimson': '#B91C1C',       # Elegant red
        'gold': '#D4AF37',          # Sophisticated gold
        'emerald': '#047857',       # Premium green
        'sapphire': '#1E40AF',      # Elegant blue
        'pearl': '#F8FAFC',         # Premium white
        'silver': '#94A3B8',        # Sophisticated gray
        'onyx': '#0F172A',          # Deep black
        'amber': '#F59E0B'          # Warm accent
    }
    
    # Layout with premium spacing
    PADDING = 40
    ELEMENT_SPACING = 25
    y = PADDING + 20
    
    # === MINIMALIST BORDER ===
    # Single, elegant border with subtle shadow
    draw.rounded_rectangle([8, 8, width-9, height-9], radius=20, outline=colors['silver'], width=1)
    draw.rounded_rectangle([4, 4, width-5, height-5], radius=24, outline=colors['platinum'], width=1)
    
    # === ELEGANT WARNING ICON ===
    icon_size = 60
    icon_x = (width - icon_size) // 2
    
    # Minimalist warning circle
    draw.ellipse([icon_x, y, icon_x + icon_size, y + icon_size], 
                 fill=colors['crimson'], outline=colors['charcoal'], width=2)
    
    # Refined exclamation mark
    mark_x = icon_x + icon_size // 2
    mark_y = y + icon_size // 2
    draw.line([(mark_x, mark_y - 12), (mark_x, mark_y + 4)], fill=colors['pearl'], width=4)
    draw.ellipse([mark_x - 2, mark_y + 8, mark_x + 2, mark_y + 12], fill=colors['pearl'])
    
    y += icon_size + ELEMENT_SPACING + 10
    
    # === SOPHISTICATED TITLE ===
    title_text = "EMERGENCIA"
    draw_elegant_text(draw, title_text, width//2, y, title_font, colors['charcoal'], center=True)
    y += 50
    
    # === REFINED INCIDENT BADGE ===
    incident_bbox = draw.textbbox((0, 0), incident_type, font=subtitle_font)
    incident_width = incident_bbox[2] - incident_bbox[0]
    badge_width = incident_width + 40
    badge_height = 40
    badge_x = (width - badge_width) // 2
    
    # Elegant incident container
    draw.rounded_rectangle([badge_x, y, badge_x + badge_width, y + badge_height],
                          radius=20, fill=colors['crimson'], outline=colors['charcoal'], width=1)
    
    # Incident text
    text_x = (width - incident_width) // 2
    draw_elegant_text(draw, incident_type, text_x, y + 10, subtitle_font, colors['pearl'])
    y += badge_height + ELEMENT_SPACING + 5
    
    # === SYSTEM IDENTIFIER ===
    system_text = "Sistema de Alarma Comunitaria"
    draw_elegant_text(draw, system_text, width//2, y, header_font, colors['charcoal'], center=True)
    y += 30
    
    # === STATUS INDICATOR ===
    status_text = "ACTIVO"
    status_bbox = draw.textbbox((0, 0), status_text, font=text_font)
    status_width = status_bbox[2] - status_bbox[0]
    status_badge_width = status_width + 30
    status_badge_height = 30
    status_x = (width - status_badge_width) // 2
    
    # Minimalist status badge
    draw.rounded_rectangle([status_x, y, status_x + status_badge_width, y + status_badge_height],
                          radius=15, fill=colors['emerald'], outline=colors['charcoal'], width=1)
    
    text_x = (width - status_width) // 2
    draw_elegant_text(draw, status_text, text_x, y + 7, text_font, colors['pearl'])
    y += status_badge_height + ELEMENT_SPACING + 15
    
    # === INFORMATION SECTION ===
    # Elegant information cards with premium styling
    card_data = [
        ("Ubicación", street_address, colors['sapphire']),
        ("Reportado por", contact_name, colors['amber']),
        ("Contacto directo", phone_number, colors['gold'])
    ]
    
    card_height = 60
    card_spacing = 15
    card_margin = PADDING
    
    for label, content, accent_color in card_data:
        card_x = card_margin
        card_width = width - (2 * card_margin)
        
        # Premium card background
        draw.rounded_rectangle([card_x, y, card_x + card_width, y + card_height],
                              radius=12, fill=colors['pearl'], outline=colors['platinum'], width=1)
        
        # Subtle accent line
        draw.rounded_rectangle([card_x + 15, y + 12, card_x + 18, y + card_height - 12],
                              radius=2, fill=accent_color)
        
        # Elegant typography
        draw_elegant_text(draw, label.upper(), card_x + 30, y + 12, small_font, colors['silver'])
        draw_elegant_text(draw, content, card_x + 30, y + 32, text_font, colors['charcoal'])
        
        y += card_height + card_spacing
    
    y += 20
    
    # === EMERGENCY CONTACT ===
    emergency_text = "EMERGENCIAS: 911"
    emergency_bbox = draw.textbbox((0, 0), emergency_text, font=subtitle_font)
    emergency_width = emergency_bbox[2] - emergency_bbox[0]
    emergency_button_width = emergency_width + 60
    emergency_button_height = 50
    emergency_x = (width - emergency_button_width) // 2
    
    # Premium emergency button
    draw.rounded_rectangle([emergency_x, y, emergency_x + emergency_button_width, y + emergency_button_height],
                          radius=25, fill=colors['crimson'], outline=colors['charcoal'], width=2)
    
    # Subtle inner highlight
    draw.rounded_rectangle([emergency_x + 2, y + 2, emergency_x + emergency_button_width - 2, y + emergency_button_height - 2],
                          radius=23, outline=colors['platinum'], width=1)
    
    # Emergency text
    text_x = (width - emergency_width) // 2
    draw_elegant_text(draw, emergency_text, text_x, y + 15, subtitle_font, colors['pearl'])
    y += emergency_button_height + ELEMENT_SPACING + 20
    
    # === SOPHISTICATED FOOTER ===
    timestamp = datetime.now().strftime("%H:%M • %d %B %Y")
    
    # Timestamp with elegant styling
    draw_elegant_text(draw, timestamp, width//2, y, small_font, colors['silver'], center=True)
    y += 20
    
    # Verification badge
    verification = "Sistema Verificado"
    draw_elegant_text(draw, verification, width//2, y, small_font, colors['silver'], center=True)
    
    # === SUBTLE BRANDING LINE ===
    # Thin line at bottom for premium feel
    draw.line([(PADDING, height - 15), (width - PADDING, height - 15)], fill=colors['platinum'], width=1)
    
    # Save image
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/elegant_emergency_alert_{timestamp_file}.jpg"
    
    image.save(output_path, format='JPEG', quality=98, optimize=True)
    
    return output_path

def draw_elegant_text(draw, text, x, y, font, color, center=False):
    """Draw text with elegant, refined styling"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Subtle shadow for depth (very minimal)
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 20))
    
    # Main text
    draw.text((x, y), text, font=font, fill=color)

def test_elegant_design():
    """Test the elegant, sophisticated design"""
    
    print("✨ Testing ELEGANT Emergency Alert Design")
    print("=" * 60)
    print("🎩 Sophisticated, modern, and refined aesthetics")
    
    test_case = {
        "street_address": "Boulevard Saint-Germain 156",
        "phone_number": "+56 9 8765 4321",
        "contact_name": "Isabella Montenegro",
        "incident_type": "Situación Crítica"
    }
    
    print(f"\n🎯 Test Case: {test_case['incident_type']}")
    print(f"   📍 Street: {test_case['street_address']}")
    print(f"   📱 Phone: {test_case['phone_number']}")
    print(f"   👤 Contact: {test_case['contact_name']}")
    
    try:
        print(f"\n✨ Generating elegant emergency alert...")
        
        image_path = create_elegant_emergency_alert(
            test_case['street_address'],
            test_case['phone_number'],
            test_case['contact_name'],
            test_case['incident_type']
        )
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ Elegant Image created: {os.path.basename(image_path)}")
            print(f"📊 Size: {file_size} bytes")
            
            print(f"\n✨ Elegant Design Features:")
            print(f"   🎨 Sophisticated gradient background")
            print(f"   💎 Minimalist border design")
            print(f"   🖤 Premium typography hierarchy")
            print(f"   🤍 Clean, refined color palette")
            print(f"   📋 Elegant information cards")
            print(f"   🎭 Subtle shadows and highlights")
            print(f"   💫 Apple-inspired aesthetics")
            print(f"   🏆 Luxury brand-level quality")
            
            return image_path
        else:
            print("❌ Failed to create elegant alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_elegant_design()
    if result:
        print(f"\n🏆 ELEGANT design test completed!")
        print(f"✨ This alert exudes sophistication and class!")
    else:
        print(f"\n❌ Test failed!")