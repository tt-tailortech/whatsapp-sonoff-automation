#!/usr/bin/env python3
"""
Create a professional emergency alert using HTML/CSS with perfect layout,
then convert to image for WhatsApp sending
"""

import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

def create_emergency_alert_html(street_address: str, phone_number: str, contact_name: str = "Vecino", incident_type: str = "ALERTA GENERAL"):
    """
    Generate HTML template for emergency alert with perfect CSS layout
    """
    
    timestamp = datetime.now().strftime("%H:%M hrs • %d/%m/%Y")
    
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerta de Emergencia</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 25%, #ef4444 50%, #dc2626 75%, #991b1b 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .alert-container {{
            width: 600px;
            background: linear-gradient(145deg, #7f1d1d 0%, #dc2626 30%, #ef4444 60%, #dc2626 90%, #991b1b 100%);
            border: 6px solid #ffffff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            overflow: hidden;
            position: relative;
        }}
        
        .alert-container::before {{
            content: '';
            position: absolute;
            top: 6px;
            left: 6px;
            right: 6px;
            bottom: 6px;
            border: 2px solid #ffd700;
            border-radius: 14px;
            pointer-events: none;
        }}
        
        .header-section {{
            text-align: center;
            padding: 40px 30px 30px;
            position: relative;
        }}
        
        .warning-badge {{
            width: 80px;
            height: 80px;
            background: #ffd700;
            border: 4px solid #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }}
        
        .warning-badge::before {{
            content: '!';
            font-size: 36px;
            font-weight: 900;
            color: #000000;
        }}
        
        .main-title {{
            font-size: 48px;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 20px;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.7);
            letter-spacing: 2px;
        }}
        
        .incident-badge {{
            background: #dc2626;
            border: 3px solid #ffd700;
            border-radius: 25px;
            padding: 15px 30px;
            margin: 0 auto 25px;
            display: inline-block;
        }}
        
        .incident-type {{
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        .system-title {{
            font-size: 32px;
            font-weight: 700;
            color: #ffd700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
        }}
        
        .status-badge {{
            background: #16a34a;
            border: 3px solid #ffffff;
            border-radius: 20px;
            padding: 12px 40px;
            display: inline-block;
            margin-bottom: 30px;
        }}
        
        .status-text {{
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }}
        
        .info-section {{
            padding: 0 30px 20px;
        }}
        
        .info-card {{
            background: linear-gradient(145deg, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.2));
            border: 2px solid;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .info-card.location {{
            border-color: #87ceeb;
        }}
        
        .info-card.contact {{
            border-color: #00ffff;
        }}
        
        .info-card.phone {{
            border-color: #ffa500;
        }}
        
        .card-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }}
        
        .card-content {{
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }}
        
        .location .card-title {{ color: #87ceeb; }}
        .contact .card-title {{ color: #00ffff; }}
        .phone .card-title {{ color: #ffa500; }}
        
        .emergency-section {{
            padding: 30px;
            text-align: center;
        }}
        
        .emergency-button {{
            background: #dc2626;
            border: 4px solid #ffd700;
            border-radius: 20px;
            padding: 20px 40px;
            display: block;
            margin: 0 auto 30px;
            position: relative;
            overflow: hidden;
        }}
        
        .emergency-button::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #ffd700, #ffffff, #ffd700, #ffffff);
            z-index: -1;
            border-radius: 20px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 0.8; }}
            50% {{ opacity: 1; }}
        }}
        
        .emergency-text {{
            font-size: 36px;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            letter-spacing: 1px;
        }}
        
        .footer-section {{
            text-align: center;
            padding: 0 30px 30px;
        }}
        
        .timestamp {{
            font-size: 16px;
            color: #d1d5db;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .verification {{
            font-size: 14px;
            color: #9ca3af;
            font-weight: 500;
        }}
        
        .texture-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 2px,
                    rgba(255, 255, 255, 0.02) 2px,
                    rgba(255, 255, 255, 0.02) 4px
                );
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="alert-container">
        <div class="texture-overlay"></div>
        
        <div class="header-section">
            <div class="warning-badge"></div>
            <h1 class="main-title">🚨 EMERGENCIA 🚨</h1>
            
            <div class="incident-badge">
                <div class="incident-type">{incident_type}</div>
            </div>
            
            <h2 class="system-title">SISTEMA DE ALARMA COMUNITARIA</h2>
            
            <div class="status-badge">
                <div class="status-text">⚡ ACTIVO ⚡</div>
            </div>
        </div>
        
        <div class="info-section">
            <div class="info-card location">
                <div class="card-title">📍 UBICACIÓN</div>
                <div class="card-content">{street_address.upper()}</div>
            </div>
            
            <div class="info-card contact">
                <div class="card-title">👤 REPORTADO POR</div>
                <div class="card-content">{contact_name.upper()}</div>
            </div>
            
            <div class="info-card phone">
                <div class="card-title">📞 CONTACTO DIRECTO</div>
                <div class="card-content">{phone_number}</div>
            </div>
        </div>
        
        <div class="emergency-section">
            <div class="emergency-button">
                <div class="emergency-text">🚨 EMERGENCIAS: 911 🚨</div>
            </div>
        </div>
        
        <div class="footer-section">
            <div class="timestamp">⏰ {timestamp}</div>
            <div class="verification">🔒 SISTEMA VERIFICADO</div>
        </div>
    </div>
</body>
</html>
    """
    
    return html_template

async def html_to_image(html_content: str, output_path: str):
    """
    Convert HTML to high-quality image using Playwright
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={{'width': 800, 'height': 1200}})
            
            await page.set_content(html_content)
            await page.wait_for_load_state('networkidle')
            
            # Take screenshot with high quality
            await page.screenshot(
                path=output_path,
                full_page=True,
                quality=95,
                type='jpeg'
            )
            
            await browser.close()
            return True
    except Exception as e:
        print(f"❌ Error converting HTML to image: {{str(e)}}")
        return False

async def create_html_emergency_alert(street_address: str, phone_number: str, contact_name: str = "Vecino", incident_type: str = "ALERTA GENERAL"):
    """
    Create professional emergency alert using HTML/CSS approach
    """
    
    print("🎨 Creating HTML-based emergency alert...")
    
    # Generate HTML
    html_content = create_emergency_alert_html(street_address, phone_number, contact_name, incident_type)
    
    # Save HTML file for debugging
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/emergency_alert_{timestamp_file}.html"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML saved: {{os.path.basename(html_path)}}")
    
    # Convert to image
    image_path = f"/Users/bmac/Library/CloudStorage/OneDrive-TheUniversityofMemphis/Other/TT/Alarm_system/html_emergency_alert_{timestamp_file}.jpg"
    
    success = await html_to_image(html_content, image_path)
    
    if success and os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"✅ Image created: {{os.path.basename(image_path)}}")
        print(f"📊 Size: {{file_size}} bytes")
        return image_path
    else:
        print("❌ Failed to create image from HTML")
        return None

async def test_html_design():
    """Test the HTML-based design"""
    
    print("🚀 Testing HTML-Based Emergency Alert Design")
    print("=" * 60)
    print("✨ Using HTML/CSS for pixel-perfect layout")
    
    test_case = {{
        "street_address": "Boulevard Central 789",
        "phone_number": "56987654321",
        "contact_name": "Elena Rodriguez",
        "incident_type": "EMERGENCIA MÉDICA"
    }}
    
    print(f"\\n🎯 Test Case: {{test_case['incident_type']}}")
    print(f"   📍 Street: {{test_case['street_address']}}")
    print(f"   📱 Phone: {{test_case['phone_number']}}")
    print(f"   👤 Contact: {{test_case['contact_name']}}")
    
    try:
        image_path = await create_html_emergency_alert(
            test_case['street_address'],
            test_case['phone_number'],
            test_case['contact_name'],
            test_case['incident_type']
        )
        
        if image_path:
            print(f"\\n🎯 HTML Design Advantages:")
            print(f"   ✅ Pixel-perfect CSS layout")
            print(f"   ✅ Professional typography")
            print(f"   ✅ Perfect margins and spacing")
            print(f"   ✅ Modern gradients and effects")
            print(f"   ✅ Responsive design principles")
            print(f"   ✅ Easy to modify and maintain")
            
            return image_path
        else:
            print("❌ Failed to create HTML-based alert")
            return None
            
    except Exception as e:
        print(f"❌ Error: {{str(e)}}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_html_design())
    if result:
        print(f"\\n🏆 HTML-based design test completed!")
        print(f"📱 Perfect layout with web-grade precision!")
    else:
        print(f"\\n❌ Test failed!")