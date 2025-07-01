#!/usr/bin/env python3
"""
Test OpenAI DALL-E API for creating safe neighborhood images
"""

import os
import asyncio
import aiohttp
import base64
from datetime import datetime

async def test_create_neighborhood_image():
    """Test creating a safe neighborhood image with OpenAI DALL-E"""
    
    print("🖼️ Testing OpenAI DALL-E API for neighborhood image generation")
    print("=" * 70)
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OpenAI API key not found in environment variables")
        print("💡 Set OPENAI_API_KEY environment variable first")
        return False
    
    print(f"✅ OpenAI API key found: {openai_api_key[:8]}...")
    
    # Create prompt for safe neighborhood image
    prompt = """Create a warm, friendly and safe neighborhood community image suitable for a WhatsApp group icon. 
    
    Style: Modern, clean, cartoon/illustration style
    Colors: Warm and welcoming (blues, greens, soft oranges)
    Elements: Small houses, trees, people, community feel, safety symbols
    Mood: Safe, friendly, neighborly, Chilean community vibes
    
    The image should represent:
    - A peaceful residential neighborhood
    - Sense of community and togetherness
    - Safety and security (subtle emergency elements like a small emergency vehicle)
    - Chilean cultural elements (mountains in background, Chilean architecture)
    - WhatsApp group icon suitable (clear, simple, recognizable at small sizes)
    
    Square format, high contrast, clear details visible even when small."""
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # DALL-E 3 payload
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",  # Square format for group icon
                "quality": "standard",  # or "hd" for higher quality
                "response_format": "url"  # Get URL instead of base64 for easier testing
            }
            
            print(f"🎨 Generating image with DALL-E 3...")
            print(f"📝 Prompt: {prompt[:100]}...")
            
            async with session.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload,
                timeout=60  # DALL-E can take time
            ) as response:
                
                print(f"📡 API Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Image generation successful!")
                    
                    # Extract image URL
                    image_url = result['data'][0]['url']
                    revised_prompt = result['data'][0].get('revised_prompt', 'No revised prompt')
                    
                    print(f"🖼️ Generated Image URL: {image_url}")
                    print(f"📝 Revised Prompt: {revised_prompt}")
                    
                    # Download and save the image for testing
                    print(f"💾 Downloading image for local testing...")
                    
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            image_data = await img_response.read()
                            
                            # Save image with timestamp
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"test_neighborhood_image_{timestamp}.png"
                            
                            with open(filename, 'wb') as f:
                                f.write(image_data)
                            
                            print(f"✅ Image saved as: {filename}")
                            print(f"📊 Image size: {len(image_data)} bytes")
                            
                            return True
                        else:
                            print(f"❌ Failed to download image: {img_response.status}")
                            return False
                
                else:
                    error_text = await response.text()
                    print(f"❌ DALL-E API Error {response.status}: {error_text}")
                    
                    # Try to parse error details
                    try:
                        error_json = await response.json()
                        error_message = error_json.get('error', {}).get('message', 'Unknown error')
                        print(f"📝 Error details: {error_message}")
                    except:
                        pass
                    
                    return False
                    
    except Exception as e:
        print(f"❌ Exception during image generation: {str(e)}")
        return False

async def test_dall_e_2_fallback():
    """Test with DALL-E 2 as fallback (cheaper option)"""
    
    print("\n🖼️ Testing DALL-E 2 (fallback option)")
    print("=" * 50)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return False
    
    # Simpler prompt for DALL-E 2
    prompt = """A safe, friendly neighborhood community icon. Cartoon style, warm colors, houses and trees, people walking, Chilean community feel. Square format, simple design for WhatsApp group icon."""
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # DALL-E 2 payload (cheaper)
            payload = {
                "model": "dall-e-2",
                "prompt": prompt,
                "n": 1,
                "size": "512x512",  # Smaller size for DALL-E 2
                "response_format": "url"
            }
            
            print(f"🎨 Generating image with DALL-E 2 (cheaper option)...")
            
            async with session.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload,
                timeout=60
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    image_url = result['data'][0]['url']
                    
                    print(f"✅ DALL-E 2 generation successful!")
                    print(f"🖼️ Image URL: {image_url}")
                    
                    # Download DALL-E 2 image
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            image_data = await img_response.read()
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"test_neighborhood_dalle2_{timestamp}.png"
                            
                            with open(filename, 'wb') as f:
                                f.write(image_data)
                            
                            print(f"✅ DALL-E 2 image saved as: {filename}")
                            return True
                
                else:
                    error_text = await response.text()
                    print(f"❌ DALL-E 2 Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ DALL-E 2 Exception: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🧪 OpenAI Image Generation Test Suite")
    print("=" * 80)
    
    # Test DALL-E 3 first (best quality)
    dalle3_success = await test_create_neighborhood_image()
    
    # Test DALL-E 2 as fallback
    dalle2_success = await test_dall_e_2_fallback()
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"🎨 DALL-E 3: {'✅ SUCCESS' if dalle3_success else '❌ FAILED'}")
    print(f"🎨 DALL-E 2: {'✅ SUCCESS' if dalle2_success else '❌ FAILED'}")
    
    if dalle3_success or dalle2_success:
        print(f"\n🎉 Image generation is working! Ready to implement group icon feature.")
        print(f"💰 Cost estimates:")
        print(f"   • DALL-E 3 (1024x1024): ~$0.040 per image")
        print(f"   • DALL-E 2 (512x512): ~$0.018 per image")
    else:
        print(f"\n❌ Image generation failed. Check API key and network connection.")
    
    return dalle3_success or dalle2_success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nTest completed: {'SUCCESS' if result else 'FAILURE'}")