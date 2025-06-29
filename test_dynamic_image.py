#!/usr/bin/env python3
"""
Test dynamic image generation - change text dynamically on a base emergency alert image
"""

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def create_dynamic_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino"):
    """
    Create a dynamic emergency alert image with custom street address, phone number, and contact name
    
    Args:
        street_address: Street address to display (e.g., "CALLE URGENTE 456")
        phone_number: Phone number to display (e.g., "56912345678")
        contact_name: Name of the person reporting (e.g., "Maria Rodriguez")
    
    Returns:
        str: Path to the generated image
    """
    
    # Create image dimensions
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='red')
    draw = ImageDraw.Draw(image)
    
    # Try to load system fonts
    font_large = None
    font_medium = None
    font_small = None
    
    font_paths = [
        "/System/Library/Fonts/Arial.ttf",  # macOS
        "/usr/share/fonts/truetype/arial.ttf",  # Linux
        "C:/Windows/Fonts/arial.ttf",  # Windows
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font_large = ImageFont.truetype(font_path, 60)
                font_medium = ImageFont.truetype(font_path, 40)
                font_small = ImageFont.truetype(font_path, 32)
                break
            except Exception:
                continue
    
    # Fallback to default font
    if not font_large:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add white border
    border_width = 20
    draw.rectangle(
        [border_width, border_width, width-border_width, height-border_width],
        outline='white',
        width=10
    )
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%H:%M - %d/%m/%Y")
    
    # Define text content with dynamic values
    texts = [
        ("ALERTA DE EMERGENCIA", 80, font_large, 'white'),
        ("ALARMA COMUNITARIA", 160, font_large, 'white'),
        ("Sistema de Seguridad Activado", 240, font_medium, 'cyan'),
        (street_address.upper(), 320, font_medium, 'yellow'),  # DYNAMIC
        (f"Reportado por: {contact_name}", 380, font_small, 'lightblue'),  # DYNAMIC
        ("Contacte autoridades inmediatamente", 430, font_medium, 'cyan'),
        (f"📞 Contacto: {phone_number}", 480, font_medium, 'yellow'),  # DYNAMIC
        ("🚨 Emergencias: 911", 530, font_medium, 'white'),
        (f"⏰ {timestamp}", 570, font_small, 'lightgray')  # DYNAMIC
    ]
    
    # Draw each text element
    for text, y_pos, font, color in texts:
        # Get text dimensions for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x_pos = (width - text_width) // 2
        
        # Add black outline for better visibility
        outline_width = 2
        for adj in range(-outline_width, outline_width + 1):
            for adj2 in range(-outline_width, outline_width + 1):
                if adj != 0 or adj2 != 0:  # Don't draw on the center
                    draw.text((x_pos + adj, y_pos + adj2), text, font=font, fill='black')
        
        # Add colored text on top
        draw.text((x_pos, y_pos), text, font=font, fill=color)
    
    # Generate unique filename with timestamp
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/dynamic_alert_{timestamp_file}.jpg"
    
    # Save the image
    image.save(output_path, format='JPEG', quality=95)
    
    return output_path

def test_dynamic_generation():
    """Test dynamic image generation with different data sets"""
    
    print("🧪 Testing Dynamic Emergency Alert Generation")
    print("=" * 60)
    
    # Test cases with different data
    test_cases = [
        {
            "street_address": "CALLE LIBERTAD 789",
            "phone_number": "56987654321", 
            "contact_name": "Ana Martinez"
        },
        {
            "street_address": "AVENIDA CENTRAL 456",
            "phone_number": "56912345678",
            "contact_name": "Carlos Rodriguez"
        },
        {
            "street_address": "PASEO DEL SOL 123",
            "phone_number": "56955566677",
            "contact_name": "Elena Gonzalez"
        }
    ]
    
    generated_images = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}:")
        print(f"   Street: {test_case['street_address']}")
        print(f"   Phone: {test_case['phone_number']}")
        print(f"   Contact: {test_case['contact_name']}")
        
        try:
            # Generate the dynamic image
            image_path = create_dynamic_emergency_alert(
                test_case['street_address'],
                test_case['phone_number'],
                test_case['contact_name']
            )
            
            # Check if file was created
            if os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                print(f"   ✅ Generated: {os.path.basename(image_path)}")
                print(f"   📊 Size: {file_size} bytes")
                generated_images.append(image_path)
            else:
                print(f"   ❌ Failed to create image")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Summary
    print(f"\n📋 Test Results:")
    print(f"   Total tests: {len(test_cases)}")
    print(f"   Successful: {len(generated_images)}")
    print(f"   Failed: {len(test_cases) - len(generated_images)}")
    
    if generated_images:
        print(f"\n📁 Generated Files:")
        for img_path in generated_images:
            print(f"   • {os.path.basename(img_path)}")
            
        print(f"\n💡 You can now check these images in your alarm system folder")
        print(f"   Location: /Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/")
    
    return len(generated_images) == len(test_cases)

if __name__ == "__main__":
    success = test_dynamic_generation()
    print(f"\n🏁 Overall Test: {'✅ PASSED' if success else '❌ FAILED'}")