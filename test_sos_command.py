#!/usr/bin/env python3
"""
Test SOS Command Processing
Tests the new SOS keyword functionality with various message formats
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.command_processor import CommandProcessor
from app.services.whatsapp_service import WhatsAppService
from app.services.ewelink_service import EWeLinkService
from app.models import WhatsAppMessage
from dotenv import load_dotenv

load_dotenv()

async def test_sos_command_processing():
    """Test SOS command detection and processing"""
    
    print("🧪 TESTING SOS COMMAND PROCESSING")
    print("=" * 60)
    
    # Initialize services
    try:
        whatsapp_service = WhatsAppService()
        ewelink_service = EWeLinkService()
        command_processor = CommandProcessor(whatsapp_service, ewelink_service)
        print("✅ Services initialized")
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        return False
    
    # Test cases for SOS detection
    test_messages = [
        "SOS",                          # Basic SOS
        "sos",                          # Lowercase
        "SoS",                          # Mixed case
        " SOS ",                        # With spaces
        "SOS INCENDIO",                 # SOS with incident type
        "sos incendio",                 # Lowercase with incident
        "SOS ACCIDENTE AUTO",           # Multiple words
        " sos emergencia médica ",      # Spaces and accents
        "SOSASALTO",                    # No space (should work)
        "EMERGENCIA",                   # Not SOS (should be ignored)
        "TEST",                         # Not SOS (should be ignored)
        "sos ayuda persona",            # Multiple words after SOS
    ]
    
    print(f"\n🎯 TESTING SOS DETECTION LOGIC:")
    print(f"{'Message':<25} {'Detected':<10} {'Incident Type':<20}")
    print("-" * 60)
    
    for msg_text in test_messages:
        # Test detection
        is_sos = command_processor._is_sos_command(msg_text)
        incident_type = command_processor._extract_incident_type(msg_text) if is_sos else "N/A"
        
        print(f"{msg_text:<25} {'✅' if is_sos else '❌':<10} {incident_type:<20}")
    
    print(f"\n🚨 TESTING FULL SOS PIPELINE:")
    
    # Create test WhatsApp message for SOS INCENDIO
    test_message = WhatsAppMessage(
        id="test_sos_001",
        from_phone="56940035815",
        chat_id="120363400467632358@g.us",  # TEST_ALARM group
        text="SOS INCENDIO",
        contact_name="Waldo",
        timestamp=str(int(asyncio.get_event_loop().time()))
    )
    
    print(f"📱 Test Message:")
    print(f"   Text: '{test_message.text}'")
    print(f"   From: {test_message.contact_name} ({test_message.from_phone})")
    print(f"   Chat: {test_message.chat_id}")
    
    # Test SOS processing
    try:
        print(f"\n🚨 Processing SOS command...")
        await command_processor._process_command(test_message)
        print(f"✅ SOS command processing completed")
        return True
        
    except Exception as e:
        print(f"❌ SOS command processing failed: {str(e)}")
        return False

def test_sos_detection_only():
    """Test just the SOS detection logic without full pipeline"""
    
    print("\n🔍 TESTING SOS DETECTION PATTERNS:")
    print("=" * 50)
    
    # Initialize minimal processor for testing
    whatsapp_service = WhatsAppService()
    ewelink_service = EWeLinkService()
    processor = CommandProcessor(whatsapp_service, ewelink_service)
    
    # Extended test cases
    test_cases = [
        # Basic cases
        ("SOS", True, "EMERGENCIA GENERAL"),
        ("sos", True, "EMERGENCIA GENERAL"),
        ("SoS", True, "EMERGENCIA GENERAL"),
        
        # With spaces
        (" SOS ", True, "EMERGENCIA GENERAL"),
        ("  sos  ", True, "EMERGENCIA GENERAL"),
        
        # With incident types
        ("SOS INCENDIO", True, "INCENDIO"),
        ("sos incendio", True, "INCENDIO"),
        ("SOS ACCIDENTE", True, "ACCIDENTE"),
        ("SOS EMERGENCIA MÉDICA", True, "EMERGENCIA MÉDICA"),
        ("sos ayuda", True, "AYUDA"),
        
        # Edge cases
        ("SOSINCENDIO", True, "INCENDIO"),  # No space
        ("SOS  INCENDIO", True, "INCENDIO"),  # Multiple spaces
        
        # Should NOT detect
        ("EMERGENCIA", False, "N/A"),
        ("TEST", False, "N/A"),
        ("AYUDA SOS", False, "N/A"),  # SOS not at start
        ("Mi SOS", False, "N/A"),  # SOS not at start
        ("", False, "N/A"),  # Empty
    ]
    
    print(f"{'Test Message':<25} {'Should Detect':<12} {'Expected Type':<18} {'Actual':<12} {'Result'}")
    print("-" * 90)
    
    all_passed = True
    
    for msg_text, should_detect, expected_type in test_cases:
        is_sos = processor._is_sos_command(msg_text)
        actual_type = processor._extract_incident_type(msg_text) if is_sos else "N/A"
        
        # Check if test passed
        detection_correct = (is_sos == should_detect)
        type_correct = (actual_type == expected_type) if should_detect else True
        test_passed = detection_correct and type_correct
        
        if not test_passed:
            all_passed = False
        
        status = "✅" if test_passed else "❌"
        print(f"{msg_text:<25} {should_detect:<12} {expected_type:<18} {actual_type:<12} {status}")
    
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed

if __name__ == "__main__":
    print("🚨 SOS COMMAND TESTING SUITE")
    print("=" * 80)
    
    # Test 1: Detection logic only
    print("\n🔍 PHASE 1: SOS DETECTION LOGIC")
    detection_passed = test_sos_detection_only()
    
    if detection_passed:
        print("\n🚨 PHASE 2: FULL SOS PIPELINE")
        # Test 2: Full pipeline (only if detection works)
        pipeline_result = asyncio.run(test_sos_command_processing())
        
        if pipeline_result:
            print(f"\n🏆 ALL TESTS PASSED - SOS SYSTEM READY!")
            print(f"🚨 Ready for production use with these formats:")
            print(f"   • SOS → EMERGENCIA GENERAL")
            print(f"   • SOS INCENDIO → INCENDIO")
            print(f"   • SOS ACCIDENTE → ACCIDENTE")
            print(f"   • sos emergencia médica → EMERGENCIA MÉDICA")
        else:
            print(f"\n⚠️ DETECTION PASSED but PIPELINE FAILED")
    else:
        print(f"\n❌ DETECTION FAILED - Fix detection logic first")