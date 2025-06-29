#!/usr/bin/env python3
"""
Complete Emergency Alert Pipeline
Integrates all emergency response components in proper sequence
"""

import asyncio
import os
import time
from datetime import datetime

async def execute_full_emergency_pipeline(
    incident_type: str = "EMERGENCIA GENERAL",
    street_address: str = "Ubicación por confirmar", 
    emergency_number: str = "SAMU 131",
    sender_phone: str = "",
    sender_name: str = "Usuario",
    group_chat_id: str = "",
    group_name: str = "Grupo de Emergencia",
    device_id: str = "10011eafd1",
    blink_cycles: int = 3,
    voice_text: str = None
):
    """
    Execute complete emergency response pipeline:
    1. Device blink sequence (ending OFF)
    2. Voice message (OpenAI TTS)
    3. Emergency alert image (WebP format)
    4. Text summary with details
    5. Animated emergency GIF
    """
    
    print("🚨" + "="*80)
    print("🚨 INICIANDO PIPELINE COMPLETO DE EMERGENCIA")
    print("🚨" + "="*80)
    
    success_steps = []
    failed_steps = []
    
    # Initialize services
    try:
        from app.services.whatsapp_service import WhatsAppService
        from app.services.ewelink_service import EWeLinkService
        
        whatsapp_service = WhatsAppService()
        ewelink_service = EWeLinkService()
        
        print(f"✅ Servicios básicos inicializados")
    except Exception as e:
        print(f"❌ Error inicializando servicios básicos: {str(e)}")
        return False
    
    print(f"\n🎯 INFORMACIÓN DE EMERGENCIA:")
    print(f"   🚨 Tipo: {incident_type}")
    print(f"   📍 Ubicación: {street_address}")
    print(f"   📞 Emergencia: {emergency_number}")
    print(f"   👤 Reportado por: {sender_name} ({sender_phone})")
    print(f"   🏘️ Grupo: {group_name}")
    print(f"   🔌 Dispositivo: {device_id}")
    
    # === STEP 1: DEVICE BLINK SEQUENCE (ENDING OFF) ===
    print(f"\n🔴 PASO 1: SECUENCIA DE PARPADEO DEL DISPOSITIVO")
    try:
        # Turn device ON first
        print(f"🔄 Encendiendo dispositivo...")
        turn_on_result = await ewelink_service.control_device(device_id, "ON")
        if not turn_on_result:
            print(f"⚠️ Advertencia: No se pudo encender el dispositivo inicialmente")
        
        await asyncio.sleep(1)
        
        # Blink cycles
        for cycle in range(1, blink_cycles + 1):
            print(f"🔄 Ciclo de parpadeo {cycle}/{blink_cycles}")
            
            # OFF
            await ewelink_service.control_device(device_id, "OFF")
            await asyncio.sleep(0.5)
            
            # ON
            await ewelink_service.control_device(device_id, "ON")
            await asyncio.sleep(0.5)
        
        # Final state: OFF
        print(f"🔴 Estado final: APAGANDO dispositivo")
        final_off_result = await ewelink_service.control_device(device_id, "OFF")
        
        if final_off_result:
            print(f"✅ Secuencia de parpadeo completada - dispositivo APAGADO")
            success_steps.append("Device Blink Sequence")
        else:
            print(f"⚠️ Parpadeo completado pero el estado final podría no ser correcto")
            success_steps.append("Device Blink Sequence (partial)")
            
    except Exception as e:
        print(f"❌ Error en secuencia de parpadeo: {str(e)}")
        failed_steps.append("Device Blink Sequence")
    
    await asyncio.sleep(2)
    
    # === STEP 2: VOICE MESSAGE ===
    print(f"\n🎤 PASO 2: MENSAJE DE VOZ")
    
    try:
        # Try to import voice service
        from app.services.voice_service import VoiceService
        voice_service = VoiceService()
        
        if voice_text is None:
            voice_text = f"Alerta de emergencia. {incident_type} reportada en {street_address}. Contacto de emergencia: {emergency_number}. Reportado por {sender_name}. Por favor, manténganse seguros y sigan las instrucciones de las autoridades."
        
        print(f"🎙️ Generando mensaje de voz...")
        
        # Generate voice file
        voice_file = await voice_service.generate_voice_message(voice_text, voice="nova")
        if not voice_file:
            raise Exception("No se pudo generar el archivo de voz")
        
        print(f"✅ Archivo de voz creado: {voice_file}")
        
        # Send voice message to group
        print(f"📤 Enviando mensaje de voz al grupo...")
        voice_success = await whatsapp_service.send_voice_message(group_chat_id, voice_file)
        
        # Cleanup
        voice_service.cleanup_audio_file(voice_file)
        
        if voice_success:
            print(f"✅ Mensaje de voz enviado al grupo")
            success_steps.append("Voice Message")
        else:
            raise Exception("Falló el envío del mensaje de voz")
            
    except Exception as e:
        print(f"❌ Error enviando mensaje de voz: {str(e)}")
        print(f"⚠️ Continuando sin mensaje de voz...")
        failed_steps.append("Voice Message")
    
    await asyncio.sleep(2)
    
    # === STEP 3: EMERGENCY ALERT IMAGE ===
    print(f"\n📷 PASO 3: IMAGEN DE ALERTA DE EMERGENCIA")
    
    try:
        # Generate dynamic emergency alert image with placeholder data
        from create_emergency_alert_final import create_emergency_alert
        
        print(f"🖼️ Generating emergency alert image with dynamic data...")
        
        # Create emergency alert with populated fields
        image_path = create_emergency_alert(
            street_address=street_address,
            phone_number=sender_phone,
            contact_name=sender_name,
            incident_type=incident_type,
            neighborhood_name=group_name,
            alert_title="EMERGENCIA",
            emergency_number=emergency_number,
            show_night_sky=True,
            show_background_city=True
        )
        
        if os.path.exists(image_path):
            print(f"✅ Emergency alert image generated: {image_path}")
            
            # Process image for WhatsApp
            from app.services.image_service import ImageService
            image_service = ImageService()
            
            print(f"🔄 Processing image for WhatsApp...")
            processed_image = image_service.process_image_for_whatsapp(image_path, convert_to_webp=True)
            
            if processed_image:
                print(f"📤 Sending emergency alert image...")
                image_caption = f"🚨 EMERGENCIA: {incident_type} - {street_address}"
                
                # Send image to group
                image_success = await whatsapp_service.send_image_message_n8n_style(group_chat_id, processed_image, image_caption)
                
                # Cleanup processed image if different from original
                if processed_image != image_path:
                    image_service.cleanup_image_file(processed_image)
                
                # Cleanup original generated image
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"🧹 Cleaned up generated image: {image_path}")
                
                if image_success:
                    print(f"✅ Imagen de emergencia enviada al grupo")
                    success_steps.append("Emergency Alert Image")
                else:
                    raise Exception("Falló el envío de la imagen de emergencia")
            else:
                raise Exception("No se pudo procesar la imagen")
        else:
            raise Exception("No se pudo generar la imagen de emergencia")
            
    except Exception as e:
        print(f"❌ Error enviando imagen de emergencia: {str(e)}")
        print(f"⚠️ Continuando sin imagen...")
        failed_steps.append("Emergency Alert Image")
    
    await asyncio.sleep(2)
    
    # === STEP 4: TEXT SUMMARY ===
    print(f"\n📱 PASO 4: RESUMEN DE TEXTO")
    
    try:
        # Create comprehensive text summary
        text_summary = f"""🚨 EMERGENCIA ACTIVADA 🚨

📋 TIPO: {incident_type}
📍 UBICACIÓN: {street_address}
👤 REPORTADO POR: {sender_name}
📞 CONTACTO: {sender_phone}

🚑 EMERGENCIA: {emergency_number}
⏰ HORA: {datetime.now().strftime('%H:%M:%S')}
📅 FECHA: {datetime.now().strftime('%d/%m/%Y')}

⚠️ MANTÉNGANSE SEGUROS
📢 SIGAN INSTRUCCIONES OFICIALES"""
        
        print(f"📤 Enviando resumen de texto al grupo...")
        text_success = await whatsapp_service.send_text_message(group_chat_id, text_summary)
        
        if text_success:
            print(f"✅ Resumen de texto enviado al grupo")
            success_steps.append("Text Summary")
        else:
            raise Exception("Falló el envío del resumen de texto")
            
    except Exception as e:
        print(f"❌ Error enviando resumen de texto: {str(e)}")
        failed_steps.append("Text Summary")
    
    await asyncio.sleep(2)
    
    # === STEP 5: ANIMATED EMERGENCY GIF ===
    print(f"\n🎬 PASO 5: GIF ANIMADO DE EMERGENCIA")
    
    try:
        # Generate dynamic animated emergency alert GIF with placeholder data
        from create_final_animated_siren import create_animated_emergency_alert_gif
        
        print(f"🎬 Generating animated emergency alert GIF with dynamic data...")
        
        # Create animated emergency alert with populated fields
        gif_path = create_animated_emergency_alert_gif(
            street_address=street_address,
            phone_number=sender_phone,
            contact_name=sender_name,
            incident_type=incident_type,
            neighborhood_name=group_name,
            alert_title="EMERGENCIA",
            emergency_number=emergency_number,
            num_frames=12,
            frame_duration=150,
            show_night_sky=True
        )
        
        if os.path.exists(gif_path):
            print(f"✅ Animated emergency alert GIF generated: {gif_path}")
            
            # Send animated GIF to group
            print(f"📤 Enviando GIF animado al grupo...")
            gif_caption = f"🚨 ALERTA ANIMADA: {incident_type} 🚨"
            
            gif_success = await whatsapp_service.send_gif_message(group_chat_id, gif_path, gif_caption)
            
            # Cleanup generated GIF
            if os.path.exists(gif_path):
                os.remove(gif_path)
                print(f"🧹 Cleaned up generated GIF: {gif_path}")
            
            if gif_success:
                print(f"✅ GIF animado enviado al grupo")
                success_steps.append("Animated Emergency GIF")
            else:
                raise Exception("Falló el envío del GIF animado")
        else:
            raise Exception("No se pudo generar el GIF animado")
            
    except Exception as e:
        print(f"❌ Error enviando GIF animado: {str(e)}")
        print(f"⚠️ Continuando sin GIF...")
        failed_steps.append("Animated Emergency GIF")
    
    # === PIPELINE SUMMARY ===
    print(f"\n🏆" + "="*80)
    print(f"🏆 RESUMEN DEL PIPELINE DE EMERGENCIA")
    print(f"🏆" + "="*80)
    
    total_steps = len(success_steps) + len(failed_steps)
    success_rate = (len(success_steps) / total_steps) * 100 if total_steps > 0 else 0
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   ✅ Pasos exitosos: {len(success_steps)}")
    print(f"   ❌ Pasos fallidos: {len(failed_steps)}")
    print(f"   📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_steps:
        print(f"\n✅ PASOS COMPLETADOS:")
        for step in success_steps:
            print(f"   ✓ {step}")
    
    if failed_steps:
        print(f"\n❌ PASOS FALLIDOS:")
        for step in failed_steps:
            print(f"   ✗ {step}")
    
    print(f"\n🎯 DESTINATARIO: {group_name} ({group_chat_id})")
    print(f"👤 REPORTADO POR: {sender_name} ({sender_phone})")
    print(f"🚨 TIPO: {incident_type}")
    print(f"📍 UBICACIÓN: {street_address}")
    
    # Overall success if at least 3 out of 5 steps completed
    overall_success = len(success_steps) >= 3
    
    if overall_success:
        print(f"\n🏆 PIPELINE COMPLETADO EXITOSAMENTE")
        print(f"🚨 Sistema de emergencia activado correctamente")
    else:
        print(f"\n⚠️ PIPELINE COMPLETADO CON LIMITACIONES")
        print(f"🚨 Algunos componentes fallaron - revisar logs")
    
    return overall_success

if __name__ == "__main__":
    print("🚨 Emergency Pipeline - Basic Version")
    result = asyncio.run(execute_full_emergency_pipeline(
        incident_type="EMERGENCIA GENERAL",
        sender_name="Test User",
        sender_phone="123456789"
    ))
    print(f"Result: {result}")