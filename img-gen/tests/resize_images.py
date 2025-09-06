#!/usr/bin/env python3

from PIL import Image
import os

def resize_to_target_size(image_path, target_size_kb=15):
    """Resize image to approximately target size in KB"""
    img = Image.open(image_path)
    
    # Start with a reasonable size reduction
    quality = 85
    scale_factor = 0.5
    
    while True:
        # Resize image
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save temporarily to check size
        temp_path = image_path + ".tmp"
        resized_img.save(temp_path, "JPEG", quality=quality, optimize=True)
        
        # Check file size
        file_size_kb = os.path.getsize(temp_path) / 1024
        print(f"Size: {new_width}x{new_height}, Quality: {quality}, File size: {file_size_kb:.1f}KB")
        
        if file_size_kb <= target_size_kb:
            # Replace original file
            os.replace(temp_path, image_path)
            print(f"✓ Resized {image_path} to {file_size_kb:.1f}KB")
            break
        
        # Adjust parameters
        if file_size_kb > target_size_kb * 1.5:
            scale_factor *= 0.8  # Reduce size more aggressively
        else:
            quality -= 5  # Reduce quality slightly
        
        if quality < 30:
            # If quality gets too low, reduce scale instead
            quality = 60
            scale_factor *= 0.8
            
        if scale_factor < 0.1:
            print(f"Warning: couldn't get {image_path} below {target_size_kb}KB")
            os.replace(temp_path, image_path)
            break
        
        os.remove(temp_path)

if __name__ == "__main__":
    resize_to_target_size("chair.jpg")
    resize_to_target_size("table.jpg")