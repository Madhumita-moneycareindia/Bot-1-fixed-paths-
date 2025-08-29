#!/usr/bin/env python3
"""
Update NSE DataSync Pro Icons
Generates all required icon formats from the base design
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_nse_icon():
    """Create the NSE DataSync Pro icon"""
    # Create a 512x512 canvas with blue gradient background
    size = 512
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create blue gradient circle
    center = size // 2
    radius = size // 2 - 10
    
    # Draw the blue circle background
    draw.ellipse([10, 10, size-10, size-10], fill='#1E90FF', outline=None)
    
    # Try to use a system font for text
    try:
        # Try different font paths
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf", 
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]
        
        main_font = None
        sub_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    main_font = ImageFont.truetype(font_path, 90)
                    sub_font = ImageFont.truetype(font_path, 55)
                    break
                except:
                    continue
        
        if main_font is None:
            main_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
            
    except:
        main_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
    
    # Draw "NSE" text
    nse_text = "NSE"
    nse_bbox = draw.textbbox((0, 0), nse_text, font=main_font)
    nse_width = nse_bbox[2] - nse_bbox[0]
    nse_height = nse_bbox[3] - nse_bbox[1]
    nse_x = (size - nse_width) // 2
    nse_y = center - 80
    
    draw.text((nse_x, nse_y), nse_text, fill='white', font=main_font)
    
    # Draw "DataSync Pro" text
    datasync_text = "DataSync Pro"
    datasync_bbox = draw.textbbox((0, 0), datasync_text, font=sub_font)
    datasync_width = datasync_bbox[2] - datasync_bbox[0]
    datasync_height = datasync_bbox[3] - datasync_bbox[1]
    datasync_x = (size - datasync_width) // 2
    datasync_y = center + 20
    
    draw.text((datasync_x, datasync_y), datasync_text, fill='white', font=sub_font)
    
    return img

def main():
    """Generate all icon formats"""
    print("Creating NSE DataSync Pro icon...")
    
    # Create the base icon
    base_icon = create_nse_icon()
    
    # Save as main icon
    base_icon.save('icon.png', 'PNG')
    print("✅ Created icon.png")
    
    # Save as nse_icon.png (what the launcher expects)
    base_icon.save('nse_icon.png', 'PNG')
    print("✅ Created nse_icon.png")
    
    # Create different sizes
    sizes = [16, 24, 32, 48, 64, 128, 256]
    for size in sizes:
        resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'nse_icon_{size}x{size}.png', 'PNG')
        print(f"✅ Created nse_icon_{size}x{size}.png")
    
    # Create ICO file for Windows
    try:
        # Create multiple sizes for ICO
        ico_sizes = [16, 32, 48, 128, 256]
        ico_images = []
        for size in ico_sizes:
            ico_images.append(base_icon.resize((size, size), Image.Resampling.LANCZOS))
        
        # Save as ICO
        ico_images[0].save('nse_icon.ico', format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print("✅ Created nse_icon.ico")
        
    except Exception as e:
        print(f"⚠️  Could not create ICO file: {e}")
        # Fallback: save largest PNG as ICO
        try:
            base_icon.resize((256, 256), Image.Resampling.LANCZOS).save('nse_icon.ico', 'ICO')
            print("✅ Created nse_icon.ico (fallback)")
        except:
            print("❌ Failed to create ICO file")
    
    print("\n🎉 Icon generation complete!")
    print("The launcher will now use the new NSE DataSync Pro icon for desktop shortcuts.")

if __name__ == "__main__":
    main() 