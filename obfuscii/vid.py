"""
OBFUSCII Video Processing Module

Handles video loading, frame extraction, and ASCII conversion using GPT's 
clean greyscale approach. No color processing, no complexity - just fast 
video-to-ASCII conversion optimized for middle-out compression.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional

# OBFUSCII 8-character set optimized for compression
ASCII_CHARS = [' ', '-', '#', '=', '+', '*', '%', '@']

def process_video(input_file: str, output_file: str, resolution: Optional[str] = None, 
                 preview: bool = False, verbose: bool = False) -> None:
    """
    Main video processing function
    
    Args:
        input_file: Path to input video file
        output_file: Path to output .txv file  
        resolution: Optional resolution override (e.g. "140x80")
        preview: Show ASCII output in terminal
        verbose: Print detailed progress
    """
    
    if verbose:
        print(f"Loading video: {input_file}")
    
    # Load video and get metadata
    cap, fps, frame_count = load_video(input_file)
    
    if verbose:
        print(f"Video loaded: {frame_count} frames at {fps:.1f} FPS")
    
    # Parse resolution if provided
    target_width, target_height = parse_resolution(resolution)
    
    if verbose and resolution:
        print(f"Target resolution: {target_width}x{target_height}")
    
    # Process all frames to ASCII
    ascii_frames = []
    frame_index = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert frame to ASCII using GPT's approach
        ascii_frame = frame_to_ascii(frame, target_width, target_height)
        ascii_frames.append(ascii_frame)
        
        # Show preview if requested
        if preview and frame_index < 10:  # Only show first 10 frames to avoid spam
            print(f"\n--- Frame {frame_index} ---")
            print_ascii_frame(ascii_frame)
        
        if verbose and frame_index % 30 == 0:  # Progress every ~1 second
            print(f"Processed frame {frame_index}/{frame_count}")
            
        frame_index += 1
    
    cap.release()
    
    if verbose:
        print(f"Conversion complete: {len(ascii_frames)} frames")
        print(f"Output: {output_file}")
    
    # TODO: Save to .txv format (next module: txv.py)
    print(f"ASCII conversion complete. .txv export not yet implemented.")


def load_video(filename: str) -> Tuple[cv2.VideoCapture, float, int]:
    """
    Load video file and extract metadata
    
    Returns:
        (video_capture, fps, frame_count)
    """
    cap = cv2.VideoCapture(filename)
    
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {filename}")
    
    # Get video metadata
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0  # Default to 30 if unknown
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    return cap, fps, frame_count


def parse_resolution(resolution: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse resolution string like "140x80" into width, height
    
    Returns:
        (width, height) or (None, None) if not specified
    """
    if not resolution:
        return None, None
        
    try:
        width_str, height_str = resolution.split('x')
        return int(width_str), int(height_str)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid resolution format: {resolution}. Use WIDTHxHEIGHT (e.g. 140x80)")


def frame_to_ascii(frame: np.ndarray, target_width: Optional[int] = None, 
                  target_height: Optional[int] = None) -> List[List[str]]:
    """
    Convert video frame to ASCII using GPT's clean approach
    
    Args:
        frame: OpenCV frame (BGR format)
        target_width: Override width (None for auto)
        target_height: Override height (None for auto)
        
    Returns:
        2D array of ASCII characters
    """
    
    # Convert BGR to greyscale (GPT's approach)
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Determine target dimensions
    if target_width and target_height:
        # Use specified resolution
        new_width, new_height = target_width, target_height
    else:
        # Auto-size based on frame aspect ratio
        height, width = grey.shape
        aspect_ratio = height / width
        new_width = 120  # Default width
        new_height = int(aspect_ratio * new_width * 0.55)  # Terminal aspect correction
    
    # Resize frame
    resized = cv2.resize(grey, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # Convert pixels to ASCII using GPT's direct mapping
    ascii_frame = []
    for row in resized:
        ascii_row = []
        for pixel in row:
            # GPT's simple mapping: pixel // (256 // len(chars))
            char_index = min(pixel // (256 // len(ASCII_CHARS)), len(ASCII_CHARS) - 1)
            ascii_row.append(ASCII_CHARS[char_index])
        ascii_frame.append(ascii_row)
    
    return ascii_frame


def print_ascii_frame(ascii_frame: List[List[str]]) -> None:
    """
    Print ASCII frame to terminal for preview
    """
    for row in ascii_frame:
        # Double each character for better aspect ratio in terminal
        line = ''.join(char * 2 for char in row)
        print(line)


# Test function for development
def test_single_frame(video_path: str) -> None:
    """
    Quick test: convert and display first frame only
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open: {video_path}")
        return
        
    ret, frame = cap.read()
    if ret:
        ascii_frame = frame_to_ascii(frame, 80, 40)  # Small test size
        print("First frame ASCII conversion:")
        print_ascii_frame(ascii_frame)
    
    cap.release()


if __name__ == "__main__":
    # Quick test when run directly
    import sys
    if len(sys.argv) > 1:
        test_single_frame(sys.argv[1])
    else:
        print("Usage: python video.py <video_file>")