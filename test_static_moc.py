#!/usr/bin/env python3
"""
Test static ASCII image compression to get real baseline
"""

from obfuscii import moc

def load_static_ascii(filename):
    """Load .txt file and convert to 2D character array"""
    
    with open(filename, 'r') as f:
        content = f.read().strip()
    
    lines = content.split('\n')
    
    # Convert to 2D array
    ascii_frame = []
    for line in lines:
        char_row = list(line)  # Convert string to list of characters
        ascii_frame.append(char_row)
    
    return ascii_frame

def test_static_compression():
    """Test compression on the static benchmark image"""
    
    print("Loading static ASCII benchmark...")
    
    # Load the static image
    static_frame = load_static_ascii('ascii_face_background_at_only.txt')
    
    height = len(static_frame)
    width = len(static_frame[0]) if static_frame else 0
    
    print(f"Static image: {width}x{height} = {width*height} characters")
    
    # Convert to single-frame video format (list of frames)
    single_frame_video = [static_frame]
    
    print("\nTesting RLE compression on static image...")
    
    # Run compression
    result = moc.compress_video_rle(single_frame_video, fps=30.0, verbose=True)
    
    if result.stats:
        ratio = result.stats.overall_ratio
        print(f"\n=== STATIC IMAGE COMPRESSION RESULT ===")
        print(f"Compression ratio: {ratio:.1f}:1")
        
        if ratio >= 10.0:
            print("✅ CONFIRMED: 10:1+ achievable on static content")
        elif ratio >= 5.0:
            print("⚠️  DECENT: 5:1+ on static content")
        else:
            print("❌ POOR: Even static content below 5:1")
    
    return result

if __name__ == "__main__":
    test_static_compression()