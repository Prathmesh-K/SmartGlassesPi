#!/usr/bin/env python3
"""
Test the new capture_and_speak function
"""

from smartglasses_app import capture_and_speak

if __name__ == "__main__":
    print("🤖 Testing SmartGlasses capture_and_speak function")
    print("=" * 50)
    
    try:
        # Test the new function
        photo_path, audio_path = capture_and_speak(
            output_wav_path="test_output.wav",
            fallback_text="I couldn't find any text in this image."
        )
        
        print("\n🎉 Success!")
        print(f"📸 Photo: {photo_path}")
        print(f"🔊 Audio: {audio_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()