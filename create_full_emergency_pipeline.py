#!/usr/bin/env python3
"""
Complete Emergency Alert Pipeline
Integrates all emergency response components in proper sequence
"""

import asyncio
import os
import time
import json
import aiohttp
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
    voice_text: str = None,
    use_member_data: bool = True
):
    """
    Execute complete emergency response pipeline:
    1. Device blink sequence (ending OFF)
    2. Text summary (FAST - immediate alert)
    3. Emergency alert image (dynamic with real data)
    4. Voice message (OpenAI TTS - slower)
    5. Animated emergency GIF (dynamic with real data)
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
        from app.services.member_lookup_service import MemberLookupService
        
        whatsapp_service = WhatsAppService()
        ewelink_service = EWeLinkService()
        member_lookup = MemberLookupService()
        
        print(f"✅ Servicios básicos inicializados")
    except Exception as e:
        print(f"❌ Error inicializando servicios básicos: {str(e)}")
        return False
    
    # Get comprehensive member data if available
    member_data = None
    if use_member_data and sender_phone and group_chat_id:
        try:
            print(f"🔍 Obteniendo datos del miembro desde base de datos...")
            member_data = await member_lookup.get_member_emergency_data(
                sender_phone, group_chat_id, group_name
            )
            
            if member_data:
                # Update variables with rich member data
                sender_name = member_data.get("name", sender_name)
                street_address = member_data.get("full_address", street_address)
                
                print(f"✅ Datos del miembro obtenidos:")
                print(f"   👤 Nombre: {sender_name}")
                print(f"   📍 Dirección: {street_address}")
                print(f"   🩺 Info médica: {member_data.get('has_medical_conditions')}")
                print(f"   🚨 Alta prioridad: {member_data.get('is_high_priority')}")
            
        except Exception as e:
            print(f"⚠️ No se pudieron obtener datos del miembro: {str(e)}")
            print(f"📝 Continuando con datos básicos del mensaje")
    
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
    
    # === STEP 2: TEXT SUMMARY (FAST) ===
    print(f"\n📱 PASO 2: RESUMEN DE TEXTO")
    
    try:
        # Generate intelligent emergency message using OpenAI
        print(f"🤖 Generating intelligent emergency message with OpenAI...")
        
        try:
            # Try to generate AI-enhanced message with member data
            text_summary = await generate_intelligent_emergency_message(
                incident_type=incident_type,
                street_address=street_address,
                sender_name=sender_name,
                sender_phone=sender_phone,
                emergency_number=emergency_number,
                group_name=group_name,
                member_data=member_data
            )
            print(f"✅ AI-generated emergency message created")
        except Exception as ai_error:
            print(f"⚠️ AI message generation failed: {str(ai_error)}")
            print(f"📝 Using fallback template message...")
            
            # Fallback to template message with member data if available
            medical_info = ""
            if member_data and member_data.get('has_medical_conditions'):
                medical_info = f"\n🩺 INFO MÉDICA: {member_data.get('medical_info', '')}"
            
            evacuation_info = ""
            if member_data and member_data.get('evacuation_assistance'):
                evacuation_info = f"\n🚨 REQUIERE ASISTENCIA EVACUACIÓN"
            
            emergency_contact = ""
            if member_data and member_data.get('emergency_contact') != "No registrado":
                emergency_contact = f"\n📞 CONTACTO EMERGENCIA: {member_data.get('emergency_contact')}"
            
            # Get emergency numbers from member data
            emergency_numbers = ""
            if member_data and member_data.get('group_emergency_contacts'):
                contacts = member_data['group_emergency_contacts']
                emergency_numbers = f"""

🚑 SAMU: {contacts.get('samu', '131')}
🚒 BOMBEROS: {contacts.get('bomberos', '132')}
👮 CARABINEROS: {contacts.get('carabineros', '133')}"""
                
                if contacts.get('group_emergency_contact'):
                    emergency_numbers += f"\n📞 COORDINADOR GRUPO: {contacts['group_emergency_contact']}"
            else:
                emergency_numbers = f"""

🚑 SAMU: 131
🚒 BOMBEROS: 132
👮 CARABINEROS: 133"""
            
            text_summary = f"""🚨 EMERGENCIA ACTIVADA 🚨

📋 TIPO: {incident_type}
📍 UBICACIÓN: {street_address}
👤 REPORTADO POR: {sender_name}
📞 CONTACTO: {sender_phone}{medical_info}{evacuation_info}{emergency_contact}{emergency_numbers}

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
    
    # === STEP 3: EMERGENCY ALERT IMAGE ===
    print(f"\n📷 PASO 3: IMAGEN DE ALERTA DE EMERGENCIA")
    
    try:
        # Generate dynamic emergency alert image with placeholder data
        from create_emergency_alert_final import create_emergency_alert
        
        print(f"🖼️ Generating emergency alert image with dynamic data...")
        print(f"📊 Parameters: incident_type='{incident_type}', sender_name='{sender_name}', sender_phone='{sender_phone}'")
        
        # Create emergency alert with member data if available
        image_path = create_emergency_alert(
            street_address=street_address,
            phone_number=sender_phone,
            contact_name=sender_name,
            incident_type=incident_type,
            chat_group_name=group_name,
            alert_title="EMERGENCIA",
            emergency_number=emergency_number,
            show_night_sky=True,
            show_background_city=True,
            member_data=member_data  # Pass member data for enhanced content
        )
        
        print(f"🖼️ Generated image path: {image_path}")
        
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
                
                # Try multiple image sending methods
                print(f"📤 Trying image sending methods...")
                
                # Method 1: Base64 JSON (most reliable)
                image_success = await whatsapp_service.send_image_message(group_chat_id, processed_image, image_caption)
                
                if not image_success:
                    print(f"📤 Base64 failed, trying n8n style...")
                    image_success = await whatsapp_service.send_image_message_n8n_style(group_chat_id, processed_image, image_caption)
                
                if not image_success:
                    print(f"📤 n8n style failed, trying multipart...")
                    image_success = await whatsapp_service.send_image_message_via_media_endpoint(group_chat_id, processed_image, image_caption)
                
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
    
    # === STEP 4: VOICE MESSAGE (SLOWER) ===
    print(f"\n🎤 PASO 4: MENSAJE DE VOZ")
    
    try:
        # Try to import voice service
        from app.services.voice_service import VoiceService
        voice_service = VoiceService()
        
        if voice_text is None:
            # Generate intelligent voice message
            try:
                print(f"🤖 Generating intelligent voice message with OpenAI...")
                voice_text = await generate_intelligent_voice_message(
                    incident_type=incident_type,
                    street_address=street_address,
                    sender_name=sender_name,
                    emergency_number=emergency_number
                )
                print(f"✅ AI-generated voice message created")
            except Exception as ai_error:
                print(f"⚠️ AI voice generation failed: {str(ai_error)}")
                print(f"📝 Using fallback voice message...")
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
    
    # === STEP 5: ANIMATED EMERGENCY GIF ===
    print(f"\n🎬 PASO 5: GIF ANIMADO DE EMERGENCIA")
    
    try:
        # Generate dynamic animated emergency alert GIF with placeholder data
        from create_final_animated_siren import create_animated_emergency_alert_gif
        
        print(f"🎬 Generating animated emergency alert GIF with dynamic data...")
        print(f"📊 GIF Parameters: incident_type='{incident_type}', sender_name='{sender_name}', sender_phone='{sender_phone}'")
        
        # Create animated emergency alert with member data if available
        gif_path = create_animated_emergency_alert_gif(
            street_address=street_address,
            phone_number=sender_phone,
            contact_name=sender_name,
            incident_type=incident_type,
            chat_group_name=group_name,
            alert_title="EMERGENCIA",
            emergency_number=emergency_number,
            num_frames=12,
            frame_duration=150,
            show_night_sky=True,
            member_data=member_data  # Pass member data for enhanced content
        )
        
        print(f"🎬 Generated GIF path: {gif_path}")
        
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
    
    # === AUDIT LOGGING ===
    try:
        from app.services.audit_service import AuditService
        audit_service = AuditService()
        
        await audit_service.log_emergency_event(
            incident_type=incident_type,
            group_chat_id=group_chat_id,
            group_name=group_name,
            reporter_phone=sender_phone,
            reporter_name=sender_name,
            actions_taken=success_steps,
            success_rate=(len(success_steps) / (len(success_steps) + len(failed_steps))) * 100 if (len(success_steps) + len(failed_steps)) > 0 else 0,
            member_data_used=use_member_data and member_data is not None,
            additional_info={
                "failed_steps": failed_steps,
                "device_id": device_id,
                "blink_cycles": blink_cycles
            }
        )
        print(f"✅ Emergency event logged to audit system")
    except Exception as e:
        print(f"⚠️ Could not log emergency event to audit: {str(e)}")
    
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

async def generate_intelligent_emergency_message(
    incident_type: str,
    street_address: str,
    sender_name: str,
    sender_phone: str,
    emergency_number: str,
    group_name: str,
    member_data: dict = None
) -> str:
    """
    Generate intelligent, context-aware emergency message using OpenAI
    """
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OpenAI API key not configured")
    
    # Create intelligent prompt based on incident type
    current_time = datetime.now()
    
    # Add member data to prompt if available
    member_info = ""
    if member_data:
        contacts = member_data.get('group_emergency_contacts', {})
        member_info = f"""
MEMBER DATABASE INFO:
- Full Name: {member_data.get('name', 'N/A')}
- Complete Address: {member_data.get('full_address', 'N/A')}
- Emergency Contact: {member_data.get('emergency_contact', 'N/A')}
- Medical Info: {member_data.get('medical_info', 'N/A')}
- Blood Type: {member_data.get('blood_type', 'N/A')}
- Medical Conditions: {', '.join(member_data.get('medical_conditions', []))}
- Allergies: {', '.join(member_data.get('allergies', []))}
- Evacuation Assistance Needed: {member_data.get('evacuation_assistance', False)}
- Special Needs: {', '.join(member_data.get('special_needs', []))}
- Is High Priority: {member_data.get('is_high_priority', False)}
- Total Group Members: {member_data.get('total_members', 'Unknown')}

GROUP EMERGENCY CONTACTS:
- SAMU: {contacts.get('samu', '131')}
- BOMBEROS: {contacts.get('bomberos', '132')}
- CARABINEROS: {contacts.get('carabineros', '133')}
- Group Emergency Contact: {contacts.get('group_emergency_contact', 'Not configured')}
- Emergency Coordinator: {contacts.get('emergency_coordinator', 'Not configured')}"""
    
    prompt = f"""You are an emergency response system AI for a community alert network in Chile. Generate a professional, urgent, and helpful emergency alert message in Spanish.

EMERGENCY DETAILS:
- Incident Type: {incident_type}
- Location: {street_address}  
- Reported by: {sender_name}
- Contact: {sender_phone}
- Emergency Services: {emergency_number}
- Community Group: {group_name}
- Time: {current_time.strftime('%H:%M:%S')}
- Date: {current_time.strftime('%d/%m/%Y')}{member_info}

REQUIREMENTS:
1. Start with 🚨 EMERGENCIA ACTIVADA 🚨
2. Use appropriate emojis for the incident type
3. Include specific safety instructions based on the emergency type
4. Keep it under 350 words
5. Use urgent but professional tone
6. Include all provided details
7. End with community safety reminder
8. Format for WhatsApp readability
9. If member has medical conditions or special needs, highlight this prominently
10. If evacuation assistance is needed, emphasize this critically

INCIDENT-SPECIFIC INSTRUCTIONS:
- INCENDIO: Fire safety, evacuation routes, smoke precautions
- EMERGENCIA MÉDICA: Medical emergency protocols, space for ambulances, mention medical history if available
- ACCIDENTE: Traffic safety, avoid area, help emergency services
- TERREMOTO: Earthquake safety, aftershock warnings, safe areas
- EMERGENCIA GENERAL: General emergency protocols

SPECIAL INSTRUCTIONS:
- If member has medical conditions, include "🩺 ATENCIÓN MÉDICA: [conditions]"
- If evacuation assistance needed, include "🚨 REQUIERE ASISTENCIA PARA EVACUACIÓN"  
- If high priority member, emphasize urgency
- Include emergency contact if available and different from reporter
- ALWAYS include all emergency services: SAMU, BOMBEROS, CARABINEROS with their numbers
- Include group emergency contact and coordinator if configured
- Format emergency numbers clearly with emojis (🚑 🚒 👮 📞)

Generate the complete message now:"""

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a professional emergency response AI assistant for community safety alerts in Chile. Generate urgent, helpful, and appropriately formatted emergency messages in Spanish."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3  # Lower temperature for consistency and professionalism
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    message = result['choices'][0]['message']['content'].strip()
                    print(f"🤖 OpenAI generated {len(message)} character emergency message")
                    return message
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
                    
    except Exception as e:
        print(f"❌ OpenAI message generation error: {str(e)}")
        raise e

async def generate_intelligent_voice_message(
    incident_type: str,
    street_address: str,
    sender_name: str,
    emergency_number: str
) -> str:
    """
    Generate intelligent voice message for TTS using OpenAI
    """
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OpenAI API key not configured")
    
    prompt = f"""Generate a clear, urgent voice message in Spanish for emergency text-to-speech audio broadcast. This will be spoken aloud to the community.

EMERGENCY DETAILS:
- Incident Type: {incident_type}
- Location: {street_address}
- Reported by: {sender_name}
- Emergency Contact: {emergency_number}

VOICE MESSAGE REQUIREMENTS:
1. Clear, calm but urgent tone suitable for TTS
2. 30-60 seconds when spoken (around 100-200 words)
3. Include specific safety instructions for the incident type
4. Easy to understand when spoken aloud
5. Include emergency contact number clearly
6. End with safety reminder
7. Use simple, clear Spanish suitable for audio

INCIDENT-SPECIFIC VOICE INSTRUCTIONS:
- INCENDIO: Clear evacuation instructions, avoid smoke
- EMERGENCIA MÉDICA: Make space for ambulances, CPR if needed
- ACCIDENTE: Traffic warnings, alternative routes
- TERREMOTO: Drop-cover-hold, aftershock warnings
- EMERGENCIA GENERAL: General safety protocols

Generate ONLY the voice message text (no formatting, no emojis):"""

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a professional emergency voice system. Generate clear, urgent voice messages in Spanish for text-to-speech emergency broadcasts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.2  # Very low temperature for consistency in emergency situations
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    voice_message = result['choices'][0]['message']['content'].strip()
                    print(f"🤖 OpenAI generated {len(voice_message)} character voice message")
                    return voice_message
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
                    
    except Exception as e:
        print(f"❌ OpenAI voice generation error: {str(e)}")
        raise e

if __name__ == "__main__":
    print("🚨 Emergency Pipeline - Basic Version")
    result = asyncio.run(execute_full_emergency_pipeline(
        incident_type="EMERGENCIA GENERAL",
        sender_name="Test User",
        sender_phone="123456789"
    ))
    print(f"Result: {result}")