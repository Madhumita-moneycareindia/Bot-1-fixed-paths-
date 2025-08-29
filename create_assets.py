#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE DataSync Pro - Icon Generator
Creates professional icons for the application
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_professional_icon():
    """Create a professional NSE DataSync Pro icon"""
    
    # Icon sizes to create
    sizes = [16, 24, 32, 48, 64, 128, 256]
    
    # Create assets directory
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    for size in sizes:
        # Create image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Professional color scheme
        primary_color = (0, 102, 204)    # Professional blue
        accent_color = (255, 165, 0)     # Gold accent
        text_color = (255, 255, 255)     # White text
        
        # Draw background circle
        margin = 2
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=primary_color, outline=accent_color, width=2)
        
        # Draw NSE text or symbol
        if size >= 32:
            try:
                # Try to load a font
                font_size = max(8, size // 4)
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Draw "NSE" text
            if size >= 48:
                text = "NSE"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size - text_width) // 2
                y = (size - text_height) // 2 - 2
                
                draw.text((x, y), text, fill=text_color, font=font)
            else:
                # Draw simple "N" for smaller sizes
                text = "N"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size - text_width) // 2
                y = (size - text_height) // 2
                
                draw.text((x, y), text, fill=text_color, font=font)
        else:
            # For very small sizes, draw a simple symbol
            center = size // 2
            radius = size // 4
            draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                        fill=accent_color)
        
        # Save PNG
        png_path = assets_dir / f"nse_icon_{size}x{size}.png"
        img.save(png_path, 'PNG')
        print(f"Created {png_path}")
    
    # Create ICO file for Windows
    try:
        # Load the largest PNG for ICO conversion
        large_img = Image.open(assets_dir / "nse_icon_256x256.png")
        
        # Create multi-resolution ICO
        ico_images = []
        for size in [16, 24, 32, 48, 64, 128, 256]:
            ico_img = large_img.resize((size, size), Image.Resampling.LANCZOS)
            ico_images.append(ico_img)
        
        ico_path = assets_dir / "nse_icon.ico"
        ico_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print(f"Created {ico_path}")
        
    except Exception as e:
        print(f"Could not create ICO file: {e}")
    
    # Create a main icon (copy of 64x64)
    try:
        main_icon = Image.open(assets_dir / "nse_icon_64x64.png")
        main_icon.save(assets_dir / "nse_icon.png")
        print(f"Created main icon: {assets_dir / 'nse_icon.png'}")
    except Exception as e:
        print(f"Could not create main icon: {e}")

def create_splash_screen():
    """Create a professional splash screen"""
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create splash screen image
    width, height = 400, 300
    img = Image.new('RGB', (width, height), (245, 245, 245))  # Light gray background
    draw = ImageDraw.Draw(img)
    
    # Professional colors
    primary_color = (0, 102, 204)
    accent_color = (255, 165, 0)
    text_color = (51, 51, 51)
    
    # Draw header background
    draw.rectangle([0, 0, width, 80], fill=primary_color)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        subtitle_font = ImageFont.truetype("arial.ttf", 14)
        version_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        version_font = ImageFont.load_default()
    
    # Draw title
    title = "NSE DataSync Pro"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    
    draw.text(((width - title_width) // 2, 20), title, fill=(255, 255, 255), font=title_font)
    
    # Draw subtitle
    subtitle = "Professional Edition v2.0"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    
    draw.text(((width - subtitle_width) // 2, 50), subtitle, fill=(255, 255, 255), font=subtitle_font)
    
    # Draw main content
    content_lines = [
        "Enterprise-grade NSE Data Synchronization",
        "",
        "Features:",
        "• Automated Scheduling with Smart Intervals",
        "• Professional File Organization",
        "• Secure Credential Management", 
        "• Real-time Monitoring & Analytics",
        "• Command-line Interface",
        "• Antivirus Compatible",
        "",
        "Loading application components..."
    ]
    
    y_pos = 120
    for line in content_lines:
        if line.startswith("•"):
            draw.text((40, y_pos), line, fill=text_color, font=version_font)
        elif line.startswith("Features:"):
            draw.text((20, y_pos), line, fill=primary_color, font=subtitle_font)
        elif line == "":
            pass  # Skip empty lines
        else:
            line_bbox = draw.textbbox((0, 0), line, font=version_font)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text(((width - line_width) // 2, y_pos), line, fill=text_color, font=version_font)
        
        y_pos += 18
    
    # Draw progress bar area
    progress_y = height - 40
    draw.rectangle([50, progress_y, width - 50, progress_y + 10], 
                  fill=(220, 220, 220), outline=primary_color)
    
    # Save splash screen
    splash_path = assets_dir / "splash_screen.png"
    img.save(splash_path, 'PNG')
    print(f"Created splash screen: {splash_path}")

if __name__ == "__main__":
    print("Creating NSE DataSync Pro professional assets...")
    print("=" * 50)
    
    create_professional_icon()
    create_splash_screen()
    
    print("\n✅ Professional assets created successfully!")
    print("Files created in assets/ directory:")
    
    assets_dir = Path("assets")
    if assets_dir.exists():
        for file in sorted(assets_dir.iterdir()):
            print(f"  - {file.name}")
