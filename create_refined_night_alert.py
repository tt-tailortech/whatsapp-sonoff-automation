#!/usr/bin/env python3
"""
Create refined night emergency alert with minimalistic city lines behind text
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import random
import math

def create_refined_night_emergency_alert(
    # === REQUIRED DYNAMIC PARAMETERS ===
    street_address: str,
    phone_number: str, 
    contact_name: str,
    incident_type: str,
    neighborhood_name: str,  # Will be replaced by chat group name later
    
    # === OPTIONAL CUSTOMIZABLE PARAMETERS ===
    alert_title: str = "EMERGENCIA",
    system_name: str = "Sistema de Alarma Comunitaria", 
    status_text: str = "ACTIVO",
    emergency_number: str = "SAMU 131",
    
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
    show_night_sky: bool = True,         # Stars and moon at top
    show_background_city: bool = True    # Minimalistic city lines behind text
):
    """
    Create refined night emergency alert with subtle city background lines
    
    IMPROVEMENTS:
    - City as white minimalistic curved lines behind text (not blocking)
    - Fixed message cutoff at bottom
    - More elegant and subtle design
    """
    
    # Increased dimensions to ensure nothing gets cut off
    width = 600
    height = 820  # Increased height to prevent cutoff
    
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
    
    # === MINIMALISTIC CITY BACKGROUND LINES ===
    # Removed city lines as requested
    # if show_background_city:
    #     draw_minimalistic_city_background(draw, width, height)
    
    # === CUTE NIGHT SKY AT THE TOP ===
    if show_night_sky:
        draw_cute_night_sky(draw, width, 150)  # Night sky in top 150px
    
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
    
    # Layout with more generous spacing
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
    
    # === TITLE HIERARCHY ===
    draw_elegant_text(draw, alert_title, width//2, y, title_font, colors['text_primary'], center=True)
    y += 50
    
    # === INCIDENT BADGE ===
    incident_bbox = draw.textbbox((0, 0), incident_type, font=subtitle_font)
    incident_width = incident_bbox[2] - incident_bbox[0]
    badge_width = incident_width + 50
    badge_height = 45
    badge_x = (width - badge_width) // 2
    
    draw.rounded_rectangle([badge_x - 2, y - 2, badge_x + badge_width + 2, y + badge_height + 2],
                          radius=25, outline=colors['accent'], width=2)
    draw.rounded_rectangle([badge_x, y, badge_x + badge_width, y + badge_height],
                          radius=22, fill=colors['danger'], outline=colors['white'], width=1)
    
    text_x = (width - incident_width) // 2
    draw_elegant_text(draw, incident_type, text_x, y + 12, subtitle_font, colors['white'])
    y += badge_height + ELEMENT_SPACING + 5
    
    # === NEIGHBORHOOD SECTION ===
    neighborhood_text = f"📍 {neighborhood_name}"
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
    
    # === EMERGENCY CONTACT - ENSURE NO CUTOFF ===
    emergency_text = f"🚨 {emergency_number}"
    emergency_bbox = draw.textbbox((0, 0), emergency_text, font=subtitle_font)
    emergency_width = emergency_bbox[2] - emergency_bbox[0]
    emergency_button_width = emergency_width + 60
    emergency_button_height = 50
    emergency_x = (width - emergency_button_width) // 2
    
    # Make sure there's enough space at bottom
    if y + emergency_button_height + 40 > height:
        y = height - emergency_button_height - 40
    
    draw.rounded_rectangle([emergency_x - 3, y - 3, emergency_x + emergency_button_width + 3, y + emergency_button_height + 3],
                          radius=28, outline=colors['danger'], width=2)
    draw.rounded_rectangle([emergency_x, y, emergency_x + emergency_button_width, y + emergency_button_height],
                          radius=25, fill=colors['danger'], outline=colors['accent'], width=2)
    
    text_x = (width - emergency_width) // 2
    draw_elegant_text(draw, emergency_text, text_x, y + 15, subtitle_font, colors['white'])
    
    # Save image
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/refined_night_alert_{timestamp_file}.jpg"
    
    image.save(output_path, format='JPEG', quality=98, optimize=True)
    
    return output_path

def draw_minimalistic_city_background(draw, width, height):
    """
    Draw very subtle minimalistic city lines as background behind text
    """
    # Very subtle white lines representing city skyline
    city_alpha = 25  # Very low opacity
    
    # Curved city skyline - flowing lines in upper half
    city_y_base = height // 2 - 100  # Position in upper half
    
    # Create flowing curved lines representing distant city
    points = []
    for x in range(0, width + 50, 30):
        # Create gentle wave-like city silhouette
        wave1 = math.sin(x * 0.01) * 15
        wave2 = math.sin(x * 0.008) * 25  
        wave3 = math.sin(x * 0.012) * 10
        
        y_pos = city_y_base + wave1 + wave2 + wave3
        points.append((x, y_pos))
    
    # Draw flowing city lines - very subtle
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, city_alpha), width=2)
    
    # Add some geometric building suggestions - very minimal
    building_positions = [100, 200, 350, 450]
    for x in building_positions:
        # Simple vertical lines suggesting buildings
        building_height = 40 + (x % 30)
        building_y = city_y_base - building_height
        
        # Very subtle building outline
        draw.line([(x, building_y), (x, city_y_base)], fill=(255, 255, 255, city_alpha), width=1)
        draw.line([(x + 20, building_y + 10), (x + 20, city_y_base)], fill=(255, 255, 255, city_alpha), width=1)
    
    # Add some horizontal lines suggesting urban infrastructure
    for y_line in [city_y_base + 50, city_y_base + 80]:
        draw.line([(50, y_line), (width - 50, y_line)], fill=(255, 255, 255, city_alpha//2), width=1)

def draw_cute_night_sky(draw, width, sky_height):
    """
    Draw a cute night sky with stars and moon at the top
    """
    # === CUTE CRESCENT MOON ===
    moon_x = width - 80
    moon_y = 30
    moon_size = 25
    
    # Outer moon circle (full moon)
    draw.ellipse([moon_x, moon_y, moon_x + moon_size, moon_y + moon_size], 
                 fill=(255, 255, 220, 200))  # Soft yellow moon
    
    # Inner circle to create crescent effect
    crescent_x = moon_x + 6
    draw.ellipse([crescent_x, moon_y, crescent_x + moon_size, moon_y + moon_size], 
                 fill=(30, 58, 138))  # Same as background to create crescent
    
    # === TWINKLING STARS ===
    random.seed(42)  # Consistent star positions
    
    star_positions = []
    for i in range(15):
        star_x = random.randint(20, width - 100)
        star_y = random.randint(15, sky_height - 20)
        star_size = random.choice([2, 3, 4])
        star_positions.append((star_x, star_y, star_size))
    
    # Draw stars with sparkle effect
    for star_x, star_y, star_size in star_positions:
        # Main star
        draw.ellipse([star_x, star_y, star_x + star_size, star_y + star_size], 
                     fill=(255, 255, 255, 180))
        
        # Sparkle cross
        sparkle_length = star_size + 2
        draw.line([(star_x + star_size//2, star_y - sparkle_length//2), 
                   (star_x + star_size//2, star_y + star_size + sparkle_length//2)], 
                  fill=(255, 255, 255, 120), width=1)
        draw.line([(star_x - sparkle_length//2, star_y + star_size//2), 
                   (star_x + star_size + sparkle_length//2, star_y + star_size//2)], 
                  fill=(255, 255, 255, 120), width=1)
    
    # === SUBTLE CLOUDS ===
    for i in range(2):
        cloud_x = 50 + (i * 200)
        cloud_y = 40 + (i * 20)
        
        for j in range(3):
            circle_x = cloud_x + (j * 8)
            circle_y = cloud_y + (j % 2) * 3
            draw.ellipse([circle_x, circle_y, circle_x + 15, circle_y + 8], 
                         fill=(255, 255, 255, 30))

def draw_elegant_text(draw, text, x, y, font, color, center=False):
    """Draw text with elegant styling"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    # Subtle glow for dark theme
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 30))
    draw.text((x, y), text, font=font, fill=color)

def test_refined_night_design():
    """Test the refined night design"""
    
    print("🌙 Testing REFINED NIGHT Emergency Alert Design")
    print("=" * 70)
    print("✨ With background city lines and fixed message display")
    
    test_case = {
        "street_address": "Avenida Las Condes 2024",
        "phone_number": "+56 9 1234 5678",
        "contact_name": "Dr. Ana Martínez",
        "incident_type": "EMERGENCIA MÉDICA",
        "neighborhood_name": "Las Condes Norte",
        "alert_title": "EMERGENCIA",
        "emergency_number": "SAMU 131",
        "show_night_sky": True,
        "show_background_city": True
    }
    
    print(f"\n🎯 Test Case: {test_case['incident_type']}")
    print(f"   🏘️ Neighborhood: {test_case['neighborhood_name']}")
    print(f"   📍 Street: {test_case['street_address']}")
    print(f"   👤 Contact: {test_case['contact_name']}")
    print(f"   🚑 Emergency: {test_case['emergency_number']}")
    
    try:
        print(f"\n🌙 Generating refined night alert...")
        
        image_path = create_refined_night_emergency_alert(**test_case)
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ Refined Night Image created: {os.path.basename(image_path)}")
            print(f"📊 Size: {file_size} bytes")
            
            print(f"\n🌙 Refined Features:")
            print(f"   ✨ Night sky with stars and moon at top")
            print(f"   🏙️ Minimalistic white curved city lines BEHIND text")
            print(f"   📱 Fixed message cutoff - everything visible")
            print(f"   💫 Subtle background elements don't interfere")
            print(f"   🎨 More elegant and refined appearance")
            print(f"   📐 Better spacing and layout")
            
            return image_path
        else:
            print("❌ Failed to create refined night alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_refined_night_design()
    if result:
        print(f"\n🏆 REFINED NIGHT design test completed!")
        print(f"🌙 Perfect balance of elegance and functionality!")
    else:
        print(f"\n❌ Test failed!")