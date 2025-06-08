"""
OBFUSCII Video Processing Module - Progressive Smoothing Pipeline

Clean video-to-ASCII conversion optimized for compression and viewability:
1. Progressive blur cascade (bilateral → gaussian → median)
2. Greyscale conversion on clean data
3. Light contrast enhancement for viewability
4. Temporal smoothing for compression

Targets both facial recognition and 10:1 compression ratio.
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
    Main video processing function with progressive smoothing pipeline
    
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
    
    # Determine frame limit for preview mode
    if preview_mode:
        max_frames = min(30, frame_count)
        print(f"Preview mode: processing first {max_frames} frames")
    else:
        max_frames = frame_count
    
    # Process frames to ASCII with progressive smoothing pipeline
    ascii_frames = []
    frame_index = 0
    
    print("Converting to ASCII with progressive smoothing pipeline...")
    
    while frame_index < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert frame to ASCII using progressive smoothing
        ascii_frame = frame_to_ascii_progressive(frame, target_width, target_height)
        ascii_frames.append(ascii_frame)
        
        # Progress reporting
        if verbose and frame_index % 30 == 0:  # Every ~1 second
            print(f"Processed frame {frame_index}/{max_frames}")
        elif not verbose and frame_index % 60 == 0:  # Every ~2 seconds
            print(f"Processed frame {frame_index}/{max_frames}")
            
        frame_index += 1
    
    cap.release()
    
    if len(ascii_frames) == 0:
        print("Error: No frames processed")
        return
    
    print(f"Conversion complete: {len(ascii_frames)} frames")
    
    # Apply temporal smoothing to reduce compression noise
    print("Applying temporal smoothing...")
    ascii_frames = apply_temporal_smoothing(ascii_frames)
    
    # Play ASCII video - default behavior
    if preview_mode:
        print(f"\nPlaying ASCII preview...")
        play_ascii_video(ascii_frames, fps)
    else:
        print(f"\nPlaying ASCII video...")
        play_ascii_video(ascii_frames, fps)
    
    # Compression analysis
    print("\nStarting compression analysis...")
    if verbose:
        # Detailed compression analysis
        compressed_result = moc.compress_video_rle(ascii_frames, fps=fps, verbose=True)
        moc.analyze_compression_performance(ascii_frames, compressed_result)
    else:
        # Basic compression
        compressed_result = moc.compress_video_rle(ascii_frames, fps=fps, verbose=False)
    
    print(f"Output target: {output_file}")
    
    # TODO: Save to .txv format (next module: txv.py)
    print("ASCII conversion complete. .txv export not yet implemented.")


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


def progressive_smoothing_pipeline(frame: np.ndarray) -> np.ndarray:
    """
    Progressive smoothing cascade optimized for ASCII compression and viewability
    
    Three-stage smoothing approach:
    1. Bilateral filter preserves major edges whilst removing noise
    2. Gaussian blur eliminates texture without creating hard boundaries
    3. Median filter removes remaining artifacts that fragment RLE runs
    
    Then light contrast enhancement for facial feature definition.
    
    Args:
        frame: BGR input frame from OpenCV
        
    Returns:
        Optimized greyscale frame ready for ASCII conversion
    """
    
    # Stage 1: Bilateral filter - preserves structural edges, removes noise
    # Uses colour channel relationships for better edge detection
    smooth1 = cv2.bilateralFilter(frame, 15, 80, 80)
    
    # Stage 2: Gaussian blur - eliminates texture patterns
    # Creates smooth gradients that compress well with RLE
    smooth2 = cv2.GaussianBlur(smooth1, (9, 9), 0)
    
    # Stage 3: Median filter - removes remaining salt-and-pepper artifacts
    # Prevents single-pixel outliers that break RLE runs
    smooth3 = cv2.medianBlur(smooth2, 5)
    
    # Convert to greyscale on fully smoothed data
    gray = cv2.cvtColor(smooth3, cv2.COLOR_BGR2GRAY)
    
    # Light contrast enhancement for viewability (much gentler than before)
    # clipLimit=1.5 vs previous 3.0 to avoid fragmenting smooth regions
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    return enhanced


def frame_to_ascii_progressive(frame: np.ndarray, target_width: Optional[int] = None, 
                              target_height: Optional[int] = None) -> List[List[str]]:
    """
    Convert video frame to ASCII using progressive smoothing pipeline
    
    Args:
        frame: OpenCV frame (BGR format)
        target_width: Override width (None for auto)
        target_height: Override height (None for auto)
        
    Returns:
        2D array of ASCII characters
    """
    
    # Apply progressive smoothing pipeline
    processed_frame = progressive_smoothing_pipeline(frame)
    
    # Determine target dimensions using GPT's exact method
    if target_width and target_height:
        # Use specified resolution
        new_width, new_height = target_width, target_height
    else:
        # Auto-size using GPT's proven approach
        height, width = processed_frame.shape
        aspect_ratio = height / width  # GPT's height/width ratio
        new_width = 120  # GPT's default width
        new_height = int(aspect_ratio * new_width * 0.55)  # GPT's terminal compensation
    
    # Resize frame (OpenCV uses width, height order)
    resized = cv2.resize(processed_frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
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


def apply_temporal_smoothing(ascii_frames: List[List[List[str]]], 
                           window_size: int = 3) -> List[List[List[str]]]:
    """
    Apply temporal smoothing to reduce character flipping noise
    
    Uses median filter across temporal window to suppress noise-induced
    character boundary flipping that hurts compression.
    """
    
    if len(ascii_frames) <= window_size:
        return ascii_frames
    
    # Character to number mapping for median calculation
    char_map = {' ': 0, '.': 1, ':': 2, '-': 3, '=': 4, 
                '+': 5, '*': 6, '#': 7, '%': 8, '@': 9}
    num_map = {v: k for k, v in char_map.items()}
    
    smoothed = []
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    total_frames = len(ascii_frames)
    
    print(f"Temporal smoothing: {total_frames} frames...")
    
    for frame_idx in range(total_frames):
        smoothed_frame = []
        
        for row in range(height):
            smoothed_row = []
            
            for col in range(width):
                # Collect values in temporal window
                window_vals = []
                
                start_frame = max(0, frame_idx - window_size // 2)
                end_frame = min(len(ascii_frames), frame_idx + window_size // 2 + 1)
                
                for w_frame in range(start_frame, end_frame):
                    char = ascii_frames[w_frame][row][col]
                    window_vals.append(char_map.get(char, 0))
                
                # Use median to suppress noise
                median_val = int(np.median(window_vals))
                smoothed_char = num_map[median_val]
                smoothed_row.append(smoothed_char)
                
            smoothed_frame.append(smoothed_row)
        smoothed.append(smoothed_frame)
        
        # Progress bar every 10 frames or so
        if frame_idx % max(1, total_frames // 20) == 0 or frame_idx == total_frames - 1:
            progress = (frame_idx + 1) / total_frames
            bar_width = 40
            filled_width = int(bar_width * progress)
            bar = '█' * filled_width + '░' * (bar_width - filled_width)
            percent = progress * 100
            print(f"\r  Smoothing: |{bar}| {percent:5.1f}% ({frame_idx + 1}/{total_frames})", end='', flush=True)
    
    print()  # New line after progress bar
    return smoothed


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


# Image processing support
def process_image(input_file: str, output_file: str, resolution: Optional[str] = None,
                 verbose: bool = False) -> None:
    """
    Process single image to ASCII using same progressive smoothing pipeline as video
    
    Args:
        input_file: Path to input image file (jpg, png, etc.)
        output_file: Path to output .txv file
        resolution: Optional resolution override
        verbose: Print detailed analysis
    """
    
    if verbose:
        print(f"Loading image: {input_file}")
    
    # Load image
    img = cv2.imread(input_file)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {input_file}")
    
    # Parse resolution if provided
    target_width, target_height = parse_resolution(resolution)
    
    if verbose:
        height, width = img.shape[:2]
        print(f"Image loaded: {width}x{height}")
        if resolution:
            print(f"Target resolution: {target_width}x{target_height}")
    
    # Convert to ASCII using progressive smoothing pipeline
    print("Converting image to ASCII with progressive smoothing...")
    ascii_frame = frame_to_ascii_progressive(img, target_width, target_height)
    
    # Create single-frame "video" for compression
    ascii_frames = [ascii_frame]
    
    # Display ASCII result
    print("\nASCII conversion result:")
    print_ascii_frame(ascii_frame)
    
    # Compression analysis
    print("\nStarting compression analysis...")
    if verbose:
        compressed_result = moc.compress_video_rle(ascii_frames, fps=1.0, verbose=True)
        moc.analyze_compression_performance(ascii_frames, compressed_result)
    else:
        compressed_result = moc.compress_video_rle(ascii_frames, fps=1.0, verbose=False)
    
    print(f"Output target: {output_file}")
    print("ASCII conversion complete. .txv export not yet implemented.")


# Comparison and testing functions
def test_pipeline_comparison(video_path: str) -> None:
    """
    Compare progressive smoothing vs current corrected pipeline
    """
    
    print("=== PIPELINE COMPARISON TEST ===")
    
    # Load first frame for testing
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot load: {video_path}")
        return
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Cannot read first frame")
        return
    
    print(f"Testing on first frame of: {video_path}")
    
    # Test 1: Progressive smoothing pipeline
    print("\n--- 1. Progressive Smoothing Pipeline ---")
    ascii_progressive = frame_to_ascii_progressive(frame, 80, None)
    print_ascii_frame_sample(ascii_progressive, 15)
    
    # Test 2: Original corrected pipeline (for comparison)
    print("\n--- 2. Original Corrected Pipeline ---")
    ascii_original = frame_to_ascii_corrected_legacy(frame, 80, None)
    print_ascii_frame_sample(ascii_original, 15)
    
    # Compression comparison on single frame
    print("\n--- COMPRESSION COMPARISON ---")
    progressive_result = moc.compress_video_rle([ascii_progressive], fps=1.0, verbose=False)
    original_result = moc.compress_video_rle([ascii_original], fps=1.0, verbose=False)
    
    prog_ratio = progressive_result.stats.overall_ratio if progressive_result.stats else 0
    orig_ratio = original_result.stats.overall_ratio if original_result.stats else 0
    
    print(f"Progressive smoothing: {prog_ratio:.1f}:1")
    print(f"Original corrected:    {orig_ratio:.1f}:1")
    
    if prog_ratio > orig_ratio:
        improvement = prog_ratio - orig_ratio
        print(f"✅ Progressive wins by {improvement:.1f}:1")
    elif orig_ratio > prog_ratio:
        loss = orig_ratio - prog_ratio
        print(f"❌ Progressive loses by {loss:.1f}:1")
    else:
        print("🤝 Both approaches perform equally")


def frame_to_ascii_corrected_legacy(frame: np.ndarray, target_width: Optional[int] = None, 
                                   target_height: Optional[int] = None) -> List[List[str]]:
    """
    Legacy corrected pipeline for comparison
    """
    
    # Original corrected pipeline
    denoised_color = cv2.bilateralFilter(frame, 15, 80, 80)
    gray = cv2.cvtColor(denoised_color, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(contrasted, cv2.MORPH_CLOSE, kernel)
    
    # Convert to ASCII
    if target_width and target_height:
        new_width, new_height = target_width, target_height
    else:
        height, width = cleaned.shape
        aspect_ratio = height / width
        new_width = 120
        new_height = int(aspect_ratio * new_width * 0.55)
    
    resized = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    ascii_frame = []
    for row in resized:
        ascii_row = []
        for pixel in row:
            char_index = min(pixel // (256 // len(ASCII_CHARS)), len(ASCII_CHARS) - 1)
            ascii_row.append(ASCII_CHARS[char_index])
        ascii_frame.append(ascii_row)
    
    return ascii_frame


def print_ascii_frame_sample(ascii_frame: List[List[str]], lines: int = 10) -> None:
    """Print first N lines of ASCII frame for comparison"""
    for i, row in enumerate(ascii_frame[:lines]):
        line = ''.join(row)
        print(line)
    if len(ascii_frame) > lines:
        print(f"... ({len(ascii_frame) - lines} more lines)")


# Test functions for development
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
        ascii_frame = frame_to_ascii_progressive(frame, 120, None)
        print("First frame ASCII conversion (progressive smoothing):")
        print_ascii_frame(ascii_frame)
    
    cap.release()


def test_image(image_path: str, width: int = 120) -> None:
    """Test ASCII conversion on a single image using progressive smoothing"""
    process_image(image_path, "test_output.txv", f"{width}x", verbose=True)


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