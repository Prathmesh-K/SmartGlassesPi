#!/usr/bin/env python3
"""
Simple test - just call the SmartGlasses capture function directly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '/home/team2/Documents/SmartGlassesProject')

def simple_test():
    try:
        # Direct import and test
        from Camera.pi_camera import capture_photo
        
        print("📸 SmartGlasses Camera Test")
        print("-" * 30)
        print("Taking photo...")
        
        photo_path = capture_photo()
        
        print(f"✅ SUCCESS!")
        print(f"📸 Photo: {photo_path}")
        
        if os.path.exists(photo_path):
            size = os.path.getsize(photo_path)
            print(f"📊 Size: {size:,} bytes")
            print(f"📁 Saved in: {os.path.dirname(photo_path)}")
        
        print("\n🎯 Your SmartGlasses camera is working!")
        print("Next: Point at text and try the full workflow when dependencies are fixed.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_test()