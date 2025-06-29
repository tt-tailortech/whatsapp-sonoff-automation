#!/usr/bin/env python3
"""
Create a dark elegant emergency alert with bluish tones and customizable parameters
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_dark_elegant_emergency_alert(
    # === REQUIRED DYNAMIC PARAMETERS ===
    street_address: str,
    phone_number: str, 
    contact_name: str,
    incident_type: str,
    
    # === OPTIONAL CUSTOMIZABLE PARAMETERS ===
    alert_title: str = "EMERGENCIA",
    system_name: str = "Sistema de Alarma Comunitaria", 
    status_text: str = "ACTIVO",
    emergency_number: str = "911",
    
    # === VISUAL CUSTOMIZATION PARAMETERS ===
    primary_color: str = "#1E3A8A",      # Dark blue
    accent_color: str = "#3B82F6",       # Bright blue  
    danger_color: str = "#DC2626",       # Red for emergencies
    success_color: str = "#059669",      # Green for status
    warning_color: str = "#D97706",      # Orange for warnings
    
    # === LAYOUT PARAMETERS ===
    show_timestamp: bool = False,         # Hide timestamp for more space
    show_verification: bool = False,      # Hide verification for more space
    card_style: str = "modern",          # "modern", "minimal", "cards"
    border_style: str = "elegant"       # "elegant", "minimal", "bold"
):
    """
    Create a dark elegant emergency alert with full customization
    
    DYNAMIC PARAMETERS YOU CAN CHANGE:
    - street_address: The location of the emergency
    - phone_number: Contact number 
    - contact_name: Person reporting
    - incident_type: Type of emergency (e.g., "ROBO", "INCENDIO", "MÉDICA")
    - alert_title: Main title (default: "EMERGENCIA")
    - system_name: System identifier
    - status_text: Status indicator
    - emergency_number: Emergency contact (default: "911")
    - All colors can be customized
    - Layout options can be modified
    """
    
    # Dimensions
    width = 600
    height = 750 if not show_timestamp and not show_verification else 800
    
    # Create image with dark background
    image = Image.new('RGB', (width, height), color='#0F172A')
    draw = ImageDraw.Draw(image)
    
    # === DARK BLUISH GRADIENT ===
    for y in range(height):
        ratio = y / height
        if ratio < 0.3:
            # Top - dark slate to dark blue
            r = int(15 + (30 - 15) * (ratio / 0.3))
            g = int(23 + (58 - 23) * (ratio / 0.3))  
            b = int(42 + (138 - 42) * (ratio / 0.3))
        elif ratio < 0.7:
            # Middle - dark blue tones
            mid_ratio = (ratio - 0.3) / 0.4
            r = int(30 + (45 - 30) * mid_ratio)
            g = int(58 + (78 - 58) * mid_ratio)
            b = int(138 + (158 - 138) * mid_ratio)
        else:
            # Bottom - back to darker
            bottom_ratio = (ratio - 0.7) / 0.3
            r = int(45 + (20 - 45) * bottom_ratio)
            g = int(78 + (35 - 78) * bottom_ratio)
            b = int(158 + (65 - 158) * bottom_ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Load fonts
    try:
        font_paths = [
            "/System/Library/Fonts/SF-Pro-Display-Bold.otf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
        
        title_font = None
        subtitle_font = None
        header_font = None
        text_font = None
        small_font = None
        
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
    
    # Color palette (using parameters)
    colors = {
        'primary': primary_color,        # Main dark blue
        'accent': accent_color,          # Bright blue
        'danger': danger_color,          # Red
        'success': success_color,        # Green
        'warning': warning_color,        # Orange
        'white': '#F8FAFC',             # Clean white
        'gray_light': '#CBD5E1',        # Light gray
        'gray_dark': '#475569',         # Dark gray
        'text_primary': '#F1F5F9',      # Primary text
        'text_secondary': '#94A3B8'     # Secondary text
    }
    
    # Layout
    PADDING = 40
    ELEMENT_SPACING = 25
    y = PADDING + 20
    
    # === BORDER STYLES ===
    if border_style == "elegant":
        draw.rounded_rectangle([6, 6, width-7, height-7], radius=25, outline=colors['accent'], width=2)
        draw.rounded_rectangle([2, 2, width-3, height-3], radius=28, outline=colors['gray_dark'], width=1)
    elif border_style == "minimal":
        draw.rounded_rectangle([4, 4, width-5, height-5], radius=20, outline=colors['gray_light'], width=1)
    elif border_style == "bold":
        draw.rounded_rectangle([8, 8, width-9, height-9], radius=22, outline=colors['accent'], width=4)
    
    # === WARNING ICON ===
    icon_size = 60
    icon_x = (width - icon_size) // 2
    
    # Dark elegant warning circle
    draw.ellipse([icon_x, y, icon_x + icon_size, y + icon_size], 
                 fill=colors['danger'], outline=colors['accent'], width=3)
    
    # Warning mark
    mark_x = icon_x + icon_size // 2
    mark_y = y + icon_size // 2
    draw.line([(mark_x, mark_y - 12), (mark_x, mark_y + 4)], fill=colors['white'], width=4)
    draw.ellipse([mark_x - 2, mark_y + 8, mark_x + 2, mark_y + 12], fill=colors['white'])
    
    y += icon_size + ELEMENT_SPACING + 10
    
    # === TITLE ===
    draw_elegant_text(draw, alert_title, width//2, y, title_font, colors['text_primary'], center=True)
    y += 50
    
    # === INCIDENT BADGE ===
    incident_bbox = draw.textbbox((0, 0), incident_type, font=subtitle_font)
    incident_width = incident_bbox[2] - incident_bbox[0]
    badge_width = incident_width + 40
    badge_height = 40
    badge_x = (width - badge_width) // 2
    
    draw.rounded_rectangle([badge_x, y, badge_x + badge_width, y + badge_height],
                          radius=20, fill=colors['danger'], outline=colors['accent'], width=1)
    
    text_x = (width - incident_width) // 2
    draw_elegant_text(draw, incident_type, text_x, y + 10, subtitle_font, colors['white'])
    y += badge_height + ELEMENT_SPACING + 5
    
    # === SYSTEM NAME ===
    draw_elegant_text(draw, system_name, width//2, y, header_font, colors['text_secondary'], center=True)
    y += 30
    
    # === STATUS ===
    status_bbox = draw.textbbox((0, 0), status_text, font=text_font)
    status_width = status_bbox[2] - status_bbox[0]
    status_badge_width = status_width + 30
    status_badge_height = 30
    status_x = (width - status_badge_width) // 2
    
    draw.rounded_rectangle([status_x, y, status_x + status_badge_width, y + status_badge_height],
                          radius=15, fill=colors['success'], outline=colors['accent'], width=1)
    
    text_x = (width - status_width) // 2
    draw_elegant_text(draw, status_text, text_x, y + 7, text_font, colors['white'])
    y += status_badge_height + ELEMENT_SPACING + 15
    
    # === INFORMATION CARDS ===
    card_data = [
        ("Ubicación", street_address, colors['accent']),
        ("Reportado por", contact_name, colors['warning']),
        ("Contacto directo", phone_number, colors['primary'])
    ]
    
    card_height = 70
    card_spacing = 15
    card_margin = PADDING
    
    for label, content, accent_color in card_data:
        card_x = card_margin
        card_width = width - (2 * card_margin)
        
        if card_style == "modern":
            # Modern dark cards
            draw.rounded_rectangle([card_x, y, card_x + card_width, y + card_height],
                                  radius=15, fill=(30, 41, 59, 200), outline=accent_color, width=2)
            
            # Accent line
            draw.rounded_rectangle([card_x + 15, y + 15, card_x + 18, y + card_height - 15],
                                  radius=2, fill=accent_color)
            
        elif card_style == "minimal":
            # Minimal cards
            draw.rounded_rectangle([card_x, y, card_x + card_width, y + card_height],
                                  radius=10, outline=colors['gray_dark'], width=1)
            
        elif card_style == "cards":
            # Card-like style
            draw.rounded_rectangle([card_x, y, card_x + card_width, y + card_height],
                                  radius=12, fill=(45, 55, 72, 180), outline=accent_color, width=1)
        
        # Card text
        draw_elegant_text(draw, label.upper(), card_x + 30, y + 15, small_font, colors['text_secondary'])
        draw_elegant_text(draw, content, card_x + 30, y + 40, text_font, colors['text_primary'])
        
        y += card_height + card_spacing
    
    y += 25
    
    # === EMERGENCY CONTACT ===
    emergency_text = f"EMERGENCIAS: {emergency_number}"
    emergency_bbox = draw.textbbox((0, 0), emergency_text, font=subtitle_font)
    emergency_width = emergency_bbox[2] - emergency_bbox[0]
    emergency_button_width = emergency_width + 60
    emergency_button_height = 50
    emergency_x = (width - emergency_button_width) // 2
    
    draw.rounded_rectangle([emergency_x, y, emergency_x + emergency_button_width, y + emergency_button_height],
                          radius=25, fill=colors['danger'], outline=colors['accent'], width=2)
    
    text_x = (width - emergency_width) // 2
    draw_elegant_text(draw, emergency_text, text_x, y + 15, subtitle_font, colors['white'])
    y += emergency_button_height + 30
    
    # === OPTIONAL FOOTER ===
    if show_timestamp or show_verification:
        y += 20
        if show_timestamp:
            timestamp = datetime.now().strftime("%H:%M • %d %B %Y")
            draw_elegant_text(draw, timestamp, width//2, y, small_font, colors['text_secondary'], center=True)
            y += 20
        
        if show_verification:
            verification = "Sistema Verificado"
            draw_elegant_text(draw, verification, width//2, y, small_font, colors['text_secondary'], center=True)
    
    # Save image
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/dark_elegant_alert_{timestamp_file}.jpg"
    
    image.save(output_path, format='JPEG', quality=98, optimize=True)
    
    return output_path

def draw_elegant_text(draw, text, x, y, font, color, center=False):
    """Draw text with elegant styling"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Subtle glow for dark theme
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 30))
    draw.text((x, y), text, font=font, fill=color)

def test_dark_elegant_design():
    """Test the dark elegant design with customizable parameters"""
    
    print("🌙 Testing DARK ELEGANT Emergency Alert Design")
    print("=" * 60)
    print("🔷 Bluish dark theme with customizable parameters")
    
    # Example showing different customization options
    test_cases = [
        {
            "name": "Standard Emergency",
            "params": {
                "street_address": "Avenida Providencia 2024",
                "phone_number": "+56 9 1234 5678",
                "contact_name": "María González",
                "incident_type": "ROBO EN PROGRESO",
                # Using defaults for other parameters
            }
        },
        {
            "name": "Medical Emergency",
            "params": {
                "street_address": "Calle Las Condes 567",
                "phone_number": "+56 9 8765 4321",
                "contact_name": "Dr. Roberto Silva",
                "incident_type": "EMERGENCIA MÉDICA",
                "alert_title": "EMERGENCIA MÉDICA",
                "emergency_number": "SAMU 131",
                "primary_color": "#7C3AED",  # Purple theme
                "accent_color": "#A855F7",
                "danger_color": "#EF4444"
            }
        }
    ]
    
    generated_images = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}: {test_case['name']}")
        print(f"   📍 Street: {test_case['params']['street_address']}")
        print(f"   📱 Phone: {test_case['params']['phone_number']}")
        print(f"   👤 Contact: {test_case['params']['contact_name']}")
        print(f"   🚨 Type: {test_case['params']['incident_type']}")
        
        try:
            image_path = create_dark_elegant_emergency_alert(**test_case['params'])
            
            if os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                print(f"   ✅ Generated: {os.path.basename(image_path)}")
                print(f"   📊 Size: {file_size} bytes")
                generated_images.append(image_path)
            else:
                print(f"   ❌ Failed to create image")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🌙 CUSTOMIZABLE PARAMETERS:")
    print(f"   📝 REQUIRED: street_address, phone_number, contact_name, incident_type")
    print(f"   🎨 VISUAL: alert_title, system_name, status_text, emergency_number")
    print(f"   🎨 COLORS: primary_color, accent_color, danger_color, success_color, warning_color")
    print(f"   📐 LAYOUT: show_timestamp, show_verification, card_style, border_style")
    
    print(f"\n🎯 Dark Elegant Features:")
    print(f"   🌙 Bluish dark gradient background")
    print(f"   💎 Clean, spacious layout (no timestamp/verification)")
    print(f"   🔷 Elegant blue color scheme")
    print(f"   📱 Modern dark UI aesthetic")
    print(f"   ⚙️ Fully customizable parameters")
    
    return generated_images

if __name__ == "__main__":
    result = test_dark_elegant_design()
    if result:
        print(f"\n🏆 DARK ELEGANT design test completed!")
        print(f"🌙 Beautiful dark theme with maximum customization!")
    else:
        print(f"\n❌ Test failed!")