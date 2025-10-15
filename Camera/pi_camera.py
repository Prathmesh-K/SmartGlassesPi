#!/usr/bin/env python3
"""
Minimal Pi Camera module for SmartGlasses project
Simple photo capture for OCR processing
"""

import os
import time
from picamera2 import Picamera2


def capture_photo(output_path: str = None) -> str:
    """
    Capture a single photo for OCR processing
    
    Args:
        output_path: Where to save the photo (defaults to Camera/Captures folder)
        
    Returns:
        str: Path to captured photo
        
    Raises:
        Exception: If camera fails
    """
    # Set default path to Camera/Captures folder if none provided
    if output_path is None:
        captures_dir = "/home/team2/Documents/SmartGlassesProject/Camera/Captures"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(captures_dir, f"capture_{timestamp}.jpg")
    
    picam2 = Picamera2()
    
    try:
        # Configure for OCR-optimized capture
        config = picam2.create_still_configuration(
            main={"size": (1920, 1080)}  # Good resolution for OCR
        )
        picam2.configure(config)
        picam2.start()
        
        # Brief warm-up
        time.sleep(1)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Capture
        picam2.capture_file(output_path)
        
        return output_path
        
    finally:
        picam2.stop()
        picam2.close()


if __name__ == "__main__":
    # Quick test
    try:
        photo = capture_photo()
        print(f"Photo captured: {photo}")
    except Exception as e:
        print(f"Error: {e}")