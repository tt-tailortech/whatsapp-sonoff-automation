#!/usr/bin/env python3
"""
Create animated emergency alert with spinning modern siren instead of exclamation mark
FINAL VERSION with larger siren (120px) and 1.4x larger fonts for card content
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import random
import math

def create_animated_emergency_alert_gif(
    # === REQUIRED DYNAMIC PARAMETERS ===
    street_address: str,
    phone_number: str, 
    contact_name: str,
    incident_type: str,
    neighborhood_name: str,
    
    # === OPTIONAL CUSTOMIZABLE PARAMETERS ===
    alert_title: str = "EMERGENCIA",
    system_name: str = "Sistema de Alarma Comunitaria", 
    status_text: str = "ACTIVO",
    emergency_number: str = "SAMU 131",
    
    # === ANIMATION PARAMETERS ===
    num_frames: int = 12,           # Number of animation frames
    frame_duration: int = 150,      # Duration per frame in ms
    
    # === VISUAL CUSTOMIZATION PARAMETERS ===
    primary_color: str = "#1E3A8A",
    accent_color: str = "#3B82F6",
    danger_color: str = "#DC2626",
    success_color: str = "#059669",
    warning_color: str = "#D97706",
    
    # === LAYOUT PARAMETERS ===
    show_timestamp: bool = False,
    show_verification: bool = False,
    show_night_sky: bool = True
):
    """
    Create animated emergency alert with spinning siren
    
    Creates a GIF with spinning modern siren animation while keeping
    all other elements static and professional
    """
    
    # Dimensions
    width = 600
    height = 820
    
    # Create list to store all frames
    frames = []
    
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
                    text_font = ImageFont.truetype(font_path, int(16 * 1.4))  # Increased 1.4x for card content
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
    
    # Generate each frame of animation
    for frame_num in range(num_frames):
        # Create frame image
        image = Image.new('RGB', (width, height), color='#0F172A')
        draw = ImageDraw.Draw(image)
        
        # === BACKGROUND GRADIENT ===
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
        
        # === NIGHT SKY ===
        if show_night_sky:
            draw_cute_night_sky(draw, width, 150)
        
        # Layout
        PADDING = 40
        ELEMENT_SPACING = 25
        y = PADDING + 20
        
        # === BORDERS ===
        draw.rounded_rectangle([6, 6, width-7, height-7], radius=25, outline=colors['accent'], width=2)
        draw.rounded_rectangle([2, 2, width-3, height-3], radius=28, outline=colors['gray_dark'], width=1)
        
        # === ANIMATED SPINNING SIREN ===
        icon_size = 120  # Doubled from 60 to 120
        icon_x = (width - icon_size) // 2
        icon_y = y
        
        # Calculate rotation angle for this frame
        rotation_angle = (frame_num / num_frames) * 360
        
        # Draw animated siren
        draw_spinning_siren(draw, icon_x + icon_size//2, icon_y + icon_size//2, icon_size//2 - 5, 
                           rotation_angle, colors, frame_num)
        
        y += icon_size + ELEMENT_SPACING + 10
        
        # === STATIC CONTENT (same for all frames) ===
        
        # Title
        draw_elegant_text(draw, alert_title, width//2, y, title_font, colors['text_primary'], center=True)
        y += 50
        
        # Incident badge
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
        
        # Neighborhood
        neighborhood_text = f"📍 {neighborhood_name}"
        draw_elegant_text(draw, neighborhood_text, width//2, y, header_font, colors['accent'], center=True)
        y += 25
        
        # System name
        draw_elegant_text(draw, system_name, width//2, y, small_font, colors['text_secondary'], center=True)
        y += 25
        
        # Status
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
        
        # Information cards
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
        
        # Emergency contact
        emergency_text = f"🚨 {emergency_number}"
        emergency_bbox = draw.textbbox((0, 0), emergency_text, font=subtitle_font)
        emergency_width = emergency_bbox[2] - emergency_bbox[0]
        emergency_button_width = emergency_width + 60
        emergency_button_height = 50
        emergency_x = (width - emergency_button_width) // 2
        
        if y + emergency_button_height + 40 > height:
            y = height - emergency_button_height - 40
        
        draw.rounded_rectangle([emergency_x - 3, y - 3, emergency_x + emergency_button_width + 3, y + emergency_button_height + 3],
                              radius=28, outline=colors['danger'], width=2)
        draw.rounded_rectangle([emergency_x, y, emergency_x + emergency_button_width, y + emergency_button_height],
                              radius=25, fill=colors['danger'], outline=colors['accent'], width=2)
        
        text_x = (width - emergency_width) // 2
        draw_elegant_text(draw, emergency_text, text_x, y + 15, subtitle_font, colors['white'])
        
        # Add frame to list
        frames.append(image)
    
    # Save as animated GIF
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"animated_emergency_alert_{timestamp_file}.gif"
    
    # Save animated GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0,  # Infinite loop
        format='GIF'
    )
    
    return output_path

def draw_spinning_siren(draw, center_x, center_y, radius, rotation_angle, colors, frame_num):
    """
    Draw a modern spinning siren with rotating light effect
    """
    # Base siren circle
    draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], 
                 fill=colors['danger'], outline=colors['accent'], width=3)
    
    # Rotating light beam
    beam_length = radius - 5
    angle_rad = math.radians(rotation_angle)
    
    # Draw multiple light beams for effect
    for i in range(3):
        beam_angle = angle_rad + (i * math.pi * 2 / 3)  # 120 degrees apart
        beam_x = center_x + beam_length * math.cos(beam_angle)
        beam_y = center_y + beam_length * math.sin(beam_angle)
        
        # Light beam with varying intensity
        intensity = 255 - (i * 60)
        beam_color = (255, intensity, 0)  # Yellow to orange
        
        # Draw light beam
        draw.line([(center_x, center_y), (beam_x, beam_y)], fill=beam_color, width=4)
        
        # Draw light at the end
        light_size = 3
        draw.ellipse([beam_x - light_size, beam_y - light_size, 
                     beam_x + light_size, beam_y + light_size], fill=beam_color)
    
    # Center light with pulsing effect
    pulse_intensity = int(200 + 55 * math.sin(frame_num * 0.5))
    center_color = (255, pulse_intensity, pulse_intensity)
    center_size = 8
    draw.ellipse([center_x - center_size, center_y - center_size, 
                 center_x + center_size, center_y + center_size], fill=center_color)
    
    # Outer glow effect
    glow_radius = radius + 8
    glow_alpha = int(100 + 50 * math.sin(frame_num * 0.3))
    draw.ellipse([center_x - glow_radius, center_y - glow_radius, 
                 center_x + glow_radius, center_y + glow_radius], 
                 outline=(255, 0, 0, glow_alpha), width=2)

def draw_cute_night_sky(draw, width, sky_height):
    """Draw night sky with stars and moon"""
    # Moon
    moon_x = width - 80
    moon_y = 30
    moon_size = 25
    
    draw.ellipse([moon_x, moon_y, moon_x + moon_size, moon_y + moon_size], 
                 fill=(255, 255, 220, 200))
    
    crescent_x = moon_x + 6
    draw.ellipse([crescent_x, moon_y, crescent_x + moon_size, moon_y + moon_size], 
                 fill=(30, 58, 138))
    
    # Stars
    random.seed(42)
    star_positions = []
    for i in range(15):
        star_x = random.randint(20, width - 100)
        star_y = random.randint(15, sky_height - 20)
        star_size = random.choice([2, 3, 4])
        star_positions.append((star_x, star_y, star_size))
    
    for star_x, star_y, star_size in star_positions:
        draw.ellipse([star_x, star_y, star_x + star_size, star_y + star_size], 
                     fill=(255, 255, 255, 180))
        
        sparkle_length = star_size + 2
        draw.line([(star_x + star_size//2, star_y - sparkle_length//2), 
                   (star_x + star_size//2, star_y + star_size + sparkle_length//2)], 
                  fill=(255, 255, 255, 120), width=1)
        draw.line([(star_x - sparkle_length//2, star_y + star_size//2), 
                   (star_x + star_size + sparkle_length//2, star_y + star_size//2)], 
                  fill=(255, 255, 255, 120), width=1)
    
    # Clouds
    for i in range(2):
        cloud_x = 50 + (i * 200)
        cloud_y = 40 + (i * 20)
        
        for j in range(3):
            circle_x = cloud_x + (j * 8)
            circle_y = cloud_y + (j % 2) * 3
            draw.ellipse([circle_x, circle_y, circle_x + 15, circle_y + 8], 
                         fill=(255, 255, 255, 30))

def draw_elegant_text(draw, text, x, y, font, color, center=False):
    """Draw elegant text"""
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2
    
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 30))
    draw.text((x, y), text, font=font, fill=color)

def test_final_animated_siren():
    """Test the final animated siren emergency alert"""
    
    print("🚨 Testing FINAL ANIMATED SIREN Emergency Alert")
    print("=" * 60)
    print("🌟 Creating spinning siren animation GIF - FINAL VERSION")
    
    test_case = {
        "street_address": "Avenida Las Condes 2024",
        "phone_number": "+56 9 1234 5678",
        "contact_name": "Dr. Ana Martínez",
        "incident_type": "EMERGENCIA MÉDICA",
        "neighborhood_name": "Las Condes Norte",
        "alert_title": "EMERGENCIA",
        "emergency_number": "SAMU 131",
        "num_frames": 12,
        "frame_duration": 150
    }
    
    print(f"\n🎯 Test Case: {test_case['incident_type']}")
    print(f"   🏘️ Neighborhood: {test_case['neighborhood_name']}")
    print(f"   📍 Street: {test_case['street_address']}")
    print(f"   👤 Contact: {test_case['contact_name']}")
    print(f"   🚑 Emergency: {test_case['emergency_number']}")
    print(f"   🎬 Animation: {test_case['num_frames']} frames")
    
    try:
        print(f"\n🚨 Generating FINAL animated siren alert...")
        
        gif_path = create_animated_emergency_alert_gif(**test_case)
        
        if os.path.exists(gif_path):
            file_size = os.path.getsize(gif_path)
            print(f"✅ FINAL Animated GIF created: {os.path.basename(gif_path)}")
            print(f"📊 Size: {file_size} bytes")
            
            print(f"\n🚨 FINAL Animation Features:")
            print(f"   🌟 LARGE spinning siren (120px) with rotating light beams")
            print(f"   💫 Pulsing center light effect")
            print(f"   ⚡ Outer glow animation")
            print(f"   📝 1.4x LARGER fonts for address, name, and phone")
            print(f"   🎬 Smooth 12-frame animation loop")
            print(f"   📱 Professional layout with enhanced readability")
            print(f"   🌙 Beautiful night sky atmosphere")
            
            return gif_path
        else:
            print("❌ Failed to create FINAL animated siren alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_final_animated_siren()
    if result:
        print(f"\n🏆 FINAL ANIMATED SIREN alert created successfully!")
        print(f"🚨 Perfect emergency alert with large siren and enhanced fonts!")
    else:
        print(f"\n❌ Test failed!")