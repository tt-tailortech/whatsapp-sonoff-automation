import os
import uuid
import urllib.request
from typing import Optional
from PIL import Image
from app.config import settings

class ImageService:
    def __init__(self):
        self.temp_dir = settings.temp_audio_dir  # Reuse temp directory
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def download_image_from_url(self, image_url: str) -> Optional[str]:
        """
        Download image from URL and save to temp directory
        Returns the local file path
        """
        try:
            # Generate unique filename
            image_id = str(uuid.uuid4())
            temp_path = os.path.join(self.temp_dir, f"{image_id}_original")
            
            print(f"📥 Downloading image from URL...")
            print(f"   URL: {image_url}")
            print(f"   Temp path: {temp_path}")
            
            # Download image
            urllib.request.urlretrieve(image_url, temp_path)
            
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                print(f"✅ Image downloaded: {temp_path} ({file_size} bytes)")
                return temp_path
            else:
                print(f"❌ Failed to download image from URL")
                return None
                
        except Exception as e:
            print(f"❌ Image download error: {str(e)}")
            return None
    
    def convert_to_webp(self, image_path: str, quality: int = 85) -> Optional[str]:
        """
        Convert image to WebP format for optimized WhatsApp sending
        Returns the WebP file path
        """
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            # Generate WebP filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            webp_path = os.path.join(self.temp_dir, f"{base_name}.webp")
            
            print(f"🔄 Converting image to WebP format...")
            print(f"   Input: {image_path}")
            print(f"   Output: {webp_path}")
            print(f"   Quality: {quality}")
            
            # Open and convert image
            with Image.open(image_path) as img:
                # Get image info
                print(f"   Original: {img.size[0]}x{img.size[1]}, mode: {img.mode}")
                
                # Convert to RGB if necessary (WebP doesn't support all modes)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Save as WebP
                img.save(webp_path, format='WebP', quality=quality, optimize=True)
            
            if os.path.exists(webp_path):
                original_size = os.path.getsize(image_path)
                webp_size = os.path.getsize(webp_path)
                compression_ratio = (1 - webp_size / original_size) * 100
                
                print(f"✅ Converted to WebP: {webp_path}")
                print(f"   Size reduction: {original_size} → {webp_size} bytes ({compression_ratio:.1f}% smaller)")
                return webp_path
            else:
                print(f"❌ Failed to create WebP file: {webp_path}")
                return None
            
        except Exception as e:
            print(f"❌ WebP conversion error: {str(e)}")
            return None
    
    def resize_image(self, image_path: str, max_width: int = 1280, max_height: int = 1280) -> Optional[str]:
        """
        Resize image to optimize for WhatsApp (max 1280x1280 recommended)
        Returns the resized image path
        """
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            resized_path = os.path.join(self.temp_dir, f"{base_name}_resized.jpg")
            
            print(f"📐 Resizing image for WhatsApp...")
            print(f"   Input: {image_path}")
            print(f"   Output: {resized_path}")
            print(f"   Max size: {max_width}x{max_height}")
            
            with Image.open(image_path) as img:
                original_size = img.size
                print(f"   Original size: {original_size[0]}x{original_size[1]}")
                
                # Calculate new size maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                new_size = img.size
                
                print(f"   New size: {new_size[0]}x{new_size[1]}")
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Save resized image
                img.save(resized_path, format='JPEG', quality=90, optimize=True)
            
            if os.path.exists(resized_path):
                file_size = os.path.getsize(resized_path)
                print(f"✅ Image resized: {resized_path} ({file_size} bytes)")
                return resized_path
            else:
                print(f"❌ Failed to create resized image")
                return None
                
        except Exception as e:
            print(f"❌ Image resize error: {str(e)}")
            return None
    
    def process_image_for_whatsapp(self, image_path: str, convert_to_webp: bool = True) -> Optional[str]:
        """
        Complete image processing pipeline for WhatsApp
        1. Resize if too large
        2. Convert to WebP (optional)
        Returns the final processed image path
        """
        try:
            print(f"🖼️ Processing image for WhatsApp: {image_path}")
            
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            current_path = image_path
            
            # Step 1: Check if image needs resizing
            with Image.open(current_path) as img:
                width, height = img.size
                
                if width > 1280 or height > 1280:
                    print(f"📐 Image is {width}x{height}, resizing...")
                    resized_path = self.resize_image(current_path)
                    if resized_path:
                        current_path = resized_path
                    else:
                        print(f"❌ Failed to resize image")
                        return None
                else:
                    print(f"📐 Image size {width}x{height} is optimal for WhatsApp")
            
            # Step 2: Convert to WebP if requested
            if convert_to_webp:
                webp_path = self.convert_to_webp(current_path)
                if webp_path:
                    # Clean up intermediate file if it's not the original
                    if current_path != image_path:
                        self.cleanup_image_file(current_path)
                    current_path = webp_path
                else:
                    print(f"❌ Failed to convert to WebP, using current format")
            
            print(f"✅ Image processing complete: {current_path}")
            return current_path
            
        except Exception as e:
            print(f"❌ Image processing error: {str(e)}")
            return None
    
    def cleanup_image_file(self, file_path: str):
        """Clean up temporary image files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🧹 Cleaned up image file: {file_path}")
        except Exception as e:
            print(f"❌ Image cleanup error: {str(e)}")
    
    def save_image_from_base64(self, base64_data: str, filename: str = None) -> Optional[str]:
        """
        Save base64 image data to file
        Returns the saved file path
        """
        try:
            import base64
            
            if not filename:
                image_id = str(uuid.uuid4())
                filename = f"{image_id}.jpg"
            
            file_path = os.path.join(self.temp_dir, filename)
            
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',')[1]
            
            # Decode and save
            image_data = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✅ Saved base64 image: {file_path} ({file_size} bytes)")
                return file_path
            else:
                print(f"❌ Failed to save base64 image")
                return None
                
        except Exception as e:
            print(f"❌ Base64 image save error: {str(e)}")
            return None