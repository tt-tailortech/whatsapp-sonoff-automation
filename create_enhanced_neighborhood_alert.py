#!/usr/bin/env python3
"""
Create an enhanced emergency alert with neighborhood name, better text hierarchy, 
and minimalistic city background lines
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import math

def create_enhanced_neighborhood_emergency_alert(
    # === REQUIRED DYNAMIC PARAMETERS ===
    street_address: str,
    phone_number: str, 
    contact_name: str,
    incident_type: str,
    neighborhood_name: str,  # NEW: This will be replaced by chat group name later
    
    # === OPTIONAL CUSTOMIZABLE PARAMETERS ===
    alert_title: str = "EMERGENCIA",
    system_name: str = "Sistema de Alarma Comunitaria", 
    status_text: str = "ACTIVO",
    emergency_number: str = "SAMU 131",  # Changed default to SAMU 131
    
    # === VISUAL CUSTOMIZATION PARAMETERS ===
    primary_color: str = "#1E3A8A",      # Dark blue
    accent_color: str = "#3B82F6",       # Bright blue  
    danger_color: str = "#DC2626",       # Red for emergencies
    success_color: str = "#059669",      # Green for status
    warning_color: str = "#D97706",      # Orange for warnings
    
    # === LAYOUT PARAMETERS ===
    show_timestamp: bool = False,         
    show_verification: bool = False,      
    card_style: str = "modern",          
    border_style: str = "elegant",
    show_city_background: bool = True    # NEW: Show minimalistic city lines
):
    """
    Create an enhanced emergency alert with neighborhood support and city background
    
    NEW FEATURES:
    - neighborhood_name: Name of the neighborhood (will be chat group name)
    - Better text hierarchy (no duplicate titles)
    - Minimalistic city skyline background
    - SAMU 131 as default emergency number
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
            r = int(15 + (30 - 15) * (ratio / 0.3))
            g = int(23 + (58 - 23) * (ratio / 0.3))  
            b = int(42 + (138 - 42) * (ratio / 0.3))
        elif ratio < 0.7:
            mid_ratio = (ratio - 0.3) / 0.4
            r = int(30 + (45 - 30) * mid_ratio)
            g = int(58 + (78 - 58) * mid_ratio)
            b = int(138 + (158 - 138) * mid_ratio)
        else:
            bottom_ratio = (ratio - 0.7) / 0.3
            r = int(45 + (20 - 45) * bottom_ratio)
            g = int(78 + (35 - 78) * bottom_ratio)
            b = int(158 + (65 - 158) * bottom_ratio)
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # === MINIMALISTIC CITY BACKGROUND ===
    if show_city_background:
        draw_minimalistic_city_background(draw, width, height, primary_color, accent_color)
    
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
    
    # Color palette
    colors = {
        'primary': primary_color,        
        'accent': accent_color,          
        'danger': danger_color,          
        'success': success_color,        
        'warning': warning_color,        
        'white': '#F8FAFC',             
        'gray_light': '#CBD5E1',        
        'gray_dark': '#475569',         
        'text_primary': '#F1F5F9',      
        'text_secondary': '#94A3B8'     
    }
    
    # Layout
    PADDING = 40
    ELEMENT_SPACING = 25
    y = PADDING + 20
    
    # === ELEGANT BORDER ===
    if border_style == "elegant":
        draw.rounded_rectangle([6, 6, width-7, height-7], radius=25, outline=colors['accent'], width=2)
        draw.rounded_rectangle([2, 2, width-3, height-3], radius=28, outline=colors['gray_dark'], width=1)
    
    # === WARNING ICON ===
    icon_size = 60
    icon_x = (width - icon_size) // 2
    
    draw.ellipse([icon_x, y, icon_x + icon_size, y + icon_size], 
                 fill=colors['danger'], outline=colors['accent'], width=3)
    
    mark_x = icon_x + icon_size // 2
    mark_y = y + icon_size // 2
    draw.line([(mark_x, mark_y - 12), (mark_x, mark_y + 4)], fill=colors['white'], width=4)
    draw.ellipse([mark_x - 2, mark_y + 8, mark_x + 2, mark_y + 12], fill=colors['white'])
    
    y += icon_size + ELEMENT_SPACING + 10
    
    # === IMPROVED TITLE HIERARCHY ===
    # Main title - just "EMERGENCIA" 
    draw_elegant_text(draw, alert_title, width//2, y, title_font, colors['text_primary'], center=True)
    y += 50
    
    # Incident type badge - more prominent, this is the main focus
    incident_bbox = draw.textbbox((0, 0), incident_type, font=subtitle_font)
    incident_width = incident_bbox[2] - incident_bbox[0]
    badge_width = incident_width + 50  # Wider for more prominence
    badge_height = 45  # Taller for more prominence
    badge_x = (width - badge_width) // 2
    
    # Enhanced incident badge with glow effect
    draw.rounded_rectangle([badge_x - 2, y - 2, badge_x + badge_width + 2, y + badge_height + 2],
                          radius=25, outline=colors['accent'], width=2)
    draw.rounded_rectangle([badge_x, y, badge_x + badge_width, y + badge_height],
                          radius=22, fill=colors['danger'], outline=colors['white'], width=1)
    
    text_x = (width - incident_width) // 2
    draw_elegant_text(draw, incident_type, text_x, y + 12, subtitle_font, colors['white'])
    y += badge_height + ELEMENT_SPACING + 5
    
    # === NEIGHBORHOOD SECTION ===
    # This will be replaced by WhatsApp chat group name later
    neighborhood_text = f"📍 {neighborhood_name}"  # Added location emoji
    draw_elegant_text(draw, neighborhood_text, width//2, y, header_font, colors['accent'], center=True)
    y += 25
    
    # === SYSTEM NAME ===
    draw_elegant_text(draw, system_name, width//2, y, small_font, colors['text_secondary'], center=True)
    y += 25
    
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
        ("Dirección", street_address, colors['accent']),
        ("Reportado por", contact_name, colors['warning']),
        ("Contacto directo", phone_number, colors['primary'])
    ]
    
    card_height = 70
    card_spacing = 15
    card_margin = PADDING
    
    for label, content, accent_color in card_data:
        card_x = card_margin
        card_width = width - (2 * card_margin)
        
        # Modern dark cards with subtle glow
        draw.rounded_rectangle([card_x - 1, y - 1, card_x + card_width + 1, y + card_height + 1],
                              radius=16, outline=accent_color, width=1)
        draw.rounded_rectangle([card_x, y, card_x + card_width, y + card_height],
                              radius=15, fill=(30, 41, 59, 200), outline=accent_color, width=2)
        
        # Accent line
        draw.rounded_rectangle([card_x + 15, y + 15, card_x + 18, y + card_height - 15],
                              radius=2, fill=accent_color)
        
        # Card text
        draw_elegant_text(draw, label.upper(), card_x + 30, y + 15, small_font, colors['text_secondary'])
        draw_elegant_text(draw, content, card_x + 30, y + 40, text_font, colors['text_primary'])
        
        y += card_height + card_spacing
    
    y += 25
    
    # === EMERGENCY CONTACT ===
    emergency_text = f"🚨 {emergency_number}"  # Added emoji for visual appeal
    emergency_bbox = draw.textbbox((0, 0), emergency_text, font=subtitle_font)
    emergency_width = emergency_bbox[2] - emergency_bbox[0]
    emergency_button_width = emergency_width + 60
    emergency_button_height = 50
    emergency_x = (width - emergency_button_width) // 2
    
    # Enhanced emergency button with pulse effect
    draw.rounded_rectangle([emergency_x - 3, y - 3, emergency_x + emergency_button_width + 3, y + emergency_button_height + 3],
                          radius=28, outline=colors['danger'], width=2)
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
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/enhanced_neighborhood_alert_{timestamp_file}.jpg"
    
    image.save(output_path, format='JPEG', quality=98, optimize=True)
    
    return output_path

def draw_minimalistic_city_background(draw, width, height, primary_color, accent_color):
    """
    Draw a minimalistic city skyline background with simple lines
    """
    # Convert hex colors to RGB tuples with low alpha for subtlety
    def hex_to_rgb_alpha(hex_color, alpha=30):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb + (alpha,)
    
    # City skyline at the bottom - very subtle
    skyline_height = height - 100
    building_widths = [40, 60, 45, 55, 35, 50, 40]
    building_heights = [80, 120, 90, 110, 70, 100, 85]
    
    x_pos = 50
    for i, (w, h) in enumerate(zip(building_widths, building_heights)):
        building_top = skyline_height - h
        
        # Draw building outline - very subtle
        draw.rectangle([x_pos, building_top, x_pos + w, skyline_height], 
                      outline=(59, 130, 246, 20), width=1)  # Very transparent blue
        
        # Add a few windows - tiny dots
        for window_y in range(building_top + 10, skyline_height - 10, 15):
            for window_x in range(x_pos + 8, x_pos + w - 8, 12):
                draw.point((window_x, window_y), fill=(100, 150, 255, 40))
        
        x_pos += w + 5
    
    # Add some very subtle grid lines - representing city blocks
    grid_spacing = 120
    for x in range(grid_spacing, width, grid_spacing):
        draw.line([(x, height - 150), (x, height - 50)], fill=(70, 140, 250, 15), width=1)
    
    # Add some minimal geometric shapes - very subtle
    for i in range(3):
        x = 50 + (i * 180)
        y = 80 + (i * 30)
        # Tiny circles representing distant city elements
        draw.ellipse([x, y, x + 3, y + 3], fill=(80, 160, 255, 25))

def draw_elegant_text(draw, text, x, y, font, color, center=False):
    """Draw text with elegant styling"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Subtle glow for dark theme
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 30))
    draw.text((x, y), text, font=font, fill=color)

def test_enhanced_neighborhood_design():
    """Test the enhanced neighborhood design"""
    
    print("🏙️ Testing ENHANCED NEIGHBORHOOD Emergency Alert Design")
    print("=" * 70)
    print("🌆 With neighborhood name, better hierarchy, and city background")
    
    test_case = {
        "street_address": "Avenida Las Condes 2024",
        "phone_number": "+56 9 1234 5678",
        "contact_name": "Dr. Ana Martínez",
        "incident_type": "EMERGENCIA MÉDICA",
        "neighborhood_name": "Las Condes Norte",  # This will be chat group name later
        "alert_title": "EMERGENCIA",
        "emergency_number": "SAMU 131",
        "show_city_background": True
    }
    
    print(f"\n🎯 Test Case: {test_case['incident_type']}")
    print(f"   🏘️ Neighborhood: {test_case['neighborhood_name']} (will be chat group name)")
    print(f"   📍 Street: {test_case['street_address']}")
    print(f"   📱 Phone: {test_case['phone_number']}")
    print(f"   👤 Contact: {test_case['contact_name']}")
    print(f"   🚑 Emergency: {test_case['emergency_number']}")
    
    try:
        print(f"\n🏙️ Generating enhanced neighborhood alert...")
        
        image_path = create_enhanced_neighborhood_emergency_alert(**test_case)
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ Enhanced Image created: {os.path.basename(image_path)}")
            print(f"📊 Size: {file_size} bytes")
            
            print(f"\n🏙️ Enhancement Features:")
            print(f"   🏘️ Neighborhood name integration (chat group placeholder)")
            print(f"   ✨ Better text hierarchy (no duplicate titles)")
            print(f"   🌆 Minimalistic city background lines")
            print(f"   🚑 SAMU 131 as default emergency number")
            print(f"   💎 Enhanced visual polish")
            print(f"   📱 Optimized spacing and layout")
            
            print(f"\n🔧 CUSTOMIZABLE PARAMETERS:")
            print(f"   📝 neighborhood_name: Will be replaced by WhatsApp chat group name")
            print(f"   🚑 emergency_number: Default 'SAMU 131', customizable per incident")
            print(f"   🌆 show_city_background: Toggle city skyline background")
            print(f"   🎨 All colors and layout options remain customizable")
            
            return image_path
        else:
            print("❌ Failed to create enhanced neighborhood alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_enhanced_neighborhood_design()
    if result:
        print(f"\n🏆 ENHANCED NEIGHBORHOOD design test completed!")
        print(f"🏙️ Ready for integration with WhatsApp chat group names!")
    else:
        print(f"\n❌ Test failed!")