#!/usr/bin/env python3
"""
Simple test to create a custom emergency alert image with YOUR specified data
"""

from test_dynamic_image import create_dynamic_emergency_alert
import os

def create_custom_alert():
    """Create a custom emergency alert with user-specified data"""
    
    print("🎯 Custom Emergency Alert Generator")
    print("=" * 50)
    
    # You can change these values to whatever you want to test:
    street_address = "AVENIDA LIBERTADORES 456"  # ← Change this
    phone_number = "56988776655"                 # ← Change this  
    contact_name = "Sofia Ramirez"               # ← Change this
    
    print(f"📍 Street Address: {street_address}")
    print(f"📱 Phone Number: {phone_number}")
    print(f"👤 Contact Name: {contact_name}")
    print()
    
    try:
        # Generate the custom image
        print("🔄 Generating custom emergency alert...")
        image_path = create_dynamic_emergency_alert(street_address, phone_number, contact_name)
        
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ SUCCESS! Custom image created:")
            print(f"   📂 File: {os.path.basename(image_path)}")
            print(f"   📊 Size: {file_size} bytes")
            print(f"   📁 Location: {image_path}")
            print()
            print("🖼️  You can now view the image to see your custom data!")
            return image_path
        else:
            print("❌ Failed to create custom image")
            return None
            
    except Exception as e:
        print(f"❌ Error creating custom image: {str(e)}")
        return None

if __name__ == "__main__":
    result = create_custom_alert()
    
    if result:
        print(f"\n🏁 Test completed successfully!")
        print(f"💡 To test with different data, edit the values in this script and run again.")
    else:
        print(f"\n❌ Test failed!")