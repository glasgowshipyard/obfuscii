#!/usr/bin/env python3
"""
Quick image-to-ASCII tester for OBFUSCII character mapping experiments
"""

import cv2
import numpy as np
from typing import List

# Test different character progressions
CHAR_SETS = {
    "current": [' ', '-', '#', '=', '+', '*', '%', '@'],
    "reversed": ['@', '%', '*', '+', '=', '#', '-', ' '],
    "reference": [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'],
}

def image_to_ascii(image_path: str, char_set_name: str = "current", width: int = 80) -> None:
    """Convert single image to ASCII and print result"""
    
    # Load and convert to greyscale
    img = cv2.imread(image_path)
    if img is None:
        print(f"Cannot load image: {image_path}")
        return
        
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate height maintaining aspect ratio
    height, orig_width = grey.shape
    aspect_ratio = orig_width / height
    new_height = int(width / aspect_ratio)
    
    # Resize
    resized = cv2.resize(grey, (width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # Get character set
    chars = CHAR_SETS[char_set_name]
    
    print(f"\n=== {char_set_name.upper()} CHARACTER SET ===")
    print(f"Characters: {chars}")
    print(f"Dimensions: {width}x{new_height}")
    print()
    
    # Convert to ASCII
    for row in resized:
        line = ""
        for pixel in row:
            char_index = min(pixel // (256 // len(chars)), len(chars) - 1)
            line += chars[char_index] * 2  # Double for terminal aspect
        print(line)

def compare_all_sets(image_path: str, width: int = 80) -> None:
    """Test all character sets on same image"""
    for set_name in CHAR_SETS.keys():
        image_to_ascii(image_path, set_name, width)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_image.py <image_file> [width]")
        print("Example: python test_image.py face.jpg 120")
        sys.exit(1)
    
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    # Test all character sets
    compare_all_sets(image_path, width)