"""
OBFUSCII Video Processing Module

Handles video loading, frame extraction, and ASCII conversion using GPT's 
clean greyscale approach. No color processing, no complexity - just fast 
video-to-ASCII conversion optimized for middle-out compression.
"""

import cv2
import numpy as np
import time
import os
import sys
from typing import List, Tuple, Optional
from . import moc

# GPT's proven character set - dark to light progression
ASCII_CHARS = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']

def process_video(input_file: str, output_file: str, resolution: Optional[str] = None, 
                 preview_mode: bool = False, verbose: bool = False) -> None:
    """
    Main video processing function
    
    Args:
        input_file: Path to input video file
        output_file: Path to output .txv file  
        resolution: Optional resolution override (e.g. "140x80")
        preview_mode: True = short clip (30 frames), False = full video
        verbose: Print compression stats and detailed progress
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
            
        # Convert frame to ASCII using GPT's proven approach
        ascii_frame = frame_to_ascii(frame, target_width, target_height)
        ascii_frames.append(ascii_frame)
        
        # Show text preview only in preview mode (first 10 frames)
        if preview_mode and frame_index < 10:
            print(f"\n--- Frame {frame_index} ---")
            print_ascii_frame(ascii_frame)
        
        if verbose and frame_index % 30 == 0:  # Progress every ~1 second
            print(f"Processed frame {frame_index}/{frame_count}")
            
        frame_index += 1
    
    cap.release()
    
    if verbose:
        print(f"Conversion complete: {len(ascii_frames)} frames")
    
    # Play ASCII video - default behavior
    if preview_mode:
        # Preview mode: short clip (30 frames)
        frame_count = min(30, len(ascii_frames))
        print(f"\nPlaying ASCII preview ({frame_count} frames)...")
        play_ascii_video(ascii_frames[:frame_count], fps)
    else:
        # Default: play full video
        print(f"\nPlaying ASCII video ({len(ascii_frames)} frames)...")
        play_ascii_video(ascii_frames, fps)
    
    # Compression analysis
    if verbose:
        print("\nStarting compression analysis...")
        compressed = moc.compress_video(ascii_frames, fps=fps)
        moc.test_compression(ascii_frames)
    else:
        # Still compress but don't show detailed stats
        compressed = moc.compress_video(ascii_frames, fps=fps)
    
    if verbose:
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
    Convert video frame to ASCII using GPT's proven approach
    
    Args:
        frame: OpenCV frame (BGR format)
        target_width: Override width (None for auto)
        target_height: Override height (None for auto)
        
    Returns:
        2D array of ASCII characters
    """
    
    # Convert BGR to greyscale (GPT's approach)
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Determine target dimensions using GPT's exact method
    if target_width and target_height:
        # Use specified resolution
        new_width, new_height = target_width, target_height
    else:
        # Auto-size using GPT's proven approach
        height, width = grey.shape
        aspect_ratio = height / width  # GPT's height/width ratio
        new_width = 120  # GPT's default width
        new_height = int(aspect_ratio * new_width * 0.55)  # GPT's terminal compensation
    
    # Resize frame (OpenCV uses width, height order)
    resized = cv2.resize(grey, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # Convert pixels to ASCII using GPT's exact mapping
    ascii_frame = []
    for row in resized:
        ascii_row = []
        for pixel in row:
            # GPT's mapping: pixel // (256 // len(chars))
            char_index = min(pixel // (256 // len(ASCII_CHARS)), len(ASCII_CHARS) - 1)
            ascii_row.append(ASCII_CHARS[char_index])
        ascii_frame.append(ascii_row)
    
    return ascii_frame


def print_ascii_frame(ascii_frame: List[List[str]]) -> None:
    """
    Print ASCII frame to terminal for preview
    """
    for row in ascii_frame:
        # Single character output (GPT's approach, no doubling)
        line = ''.join(row)
        print(line)


def play_ascii_video(ascii_frames: List[List[List[str]]], fps: float = 30.0) -> None:
    """
    Play ASCII video using exact video-to-ascii approach
    """
    
    if not ascii_frames:
        return
        
    time_delta = 1.0 / fps
    
    print("Press Ctrl+C to stop")
    input("Press Enter to start playback...")
    
    # Clear screen once at start (video-to-ascii approach)
    sys.stdout.write('\033[2J')
    sys.stdout.flush()
    
    try:
        for frame_idx, ascii_frame in enumerate(ascii_frames):
            t0 = time.process_time()
            
            # Get terminal size every frame (video-to-ascii approach)
            try:
                rows, cols = os.popen('stty size', 'r').read().split()
                cols, rows = int(cols), int(rows)
            except:
                cols, rows = 80, 24  # Fallback
            
            # Move cursor to home position (video-to-ascii method)
            sys.stdout.write('\u001b[0;0H')
            
            # Resize frame to fit terminal (video-to-ascii approach)
            resized_frame = resize_frame_to_terminal(ascii_frame, (cols, rows))
            
            # Convert to string without headers (pure ASCII like video-to-ascii)
            msg = ''
            for row in resized_frame:
                for char in row:
                    msg += char
                msg += '\r\n'  # Use \r\n like video-to-ascii
            
            # Frame rate limiting (video-to-ascii timing)
            t1 = time.process_time()
            delta = time_delta - (t1 - t0)
            if delta > 0:
                time.sleep(delta)
                
            # Write the frame (video-to-ascii approach)
            sys.stdout.write(msg)
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\n\nPlayback stopped")
        sys.stdout.flush()


def resize_frame_to_terminal(ascii_frame: List[List[str]], dimensions: Tuple[int, int]) -> List[List[str]]:
    """
    Resize ASCII frame to fit terminal dimensions (proportional scaling like video-to-ascii)
    """
    cols, rows = dimensions
    frame_height = len(ascii_frame)
    frame_width = len(ascii_frame[0]) if ascii_frame else 0
    
    if frame_height == 0 or frame_width == 0:
        return ascii_frame
    
    # Calculate scaling to fit both width and height (like video-to-ascii resize_frame)
    height_ratio = (rows - 1) / frame_height  # -1 for safety margin
    width_ratio = cols / frame_width
    
    # Use smaller ratio to ensure both dimensions fit
    scale_factor = min(height_ratio, width_ratio)
    
    # Calculate new dimensions
    new_height = int(frame_height * scale_factor)
    new_width = int(frame_width * scale_factor)
    
    # Sample the original frame at scaled intervals
    resized = []
    for new_row in range(new_height):
        # Map new row back to original frame
        orig_row = int(new_row / scale_factor)
        if orig_row >= len(ascii_frame):
            break
            
        row_chars = []
        for new_col in range(new_width):
            # Map new column back to original frame  
            orig_col = int(new_col / scale_factor)
            if orig_col < len(ascii_frame[orig_row]):
                row_chars.append(ascii_frame[orig_row][orig_col])
            else:
                row_chars.append(' ')
        
        resized.append(row_chars)
    
    return resized


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
        ascii_frame = frame_to_ascii(frame, 120, None)  # Use GPT's width, auto height
        print("First frame ASCII conversion:")
        print_ascii_frame(ascii_frame)
    
    cap.release()


def test_image(image_path: str, width: int = 120) -> None:
    """Test ASCII conversion on a single image using the same algorithm as video"""
    import cv2
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Cannot load image: {image_path}")
        return
    
    # Use the exact same conversion as video frames
    ascii_frame = frame_to_ascii(img, width, None)  # Let it auto-calculate height
    
    print("Image ASCII conversion:")
    print_ascii_frame(ascii_frame)


if __name__ == "__main__":
    # Quick test when run directly
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].endswith(('.jpg', '.png', '.jpeg')):
            test_image(sys.argv[1])
        else:
            test_single_frame(sys.argv[1])
    else:
        print("Usage: python vid.py <video_file_or_image>")