"""
OBFUSCII Video Processing Module - Character Boundary Hysteresis

Clean video-to-ASCII conversion optimized for compression and viewability:
1. Progressive blur cascade (bilateral → gaussian → median)
2. Greyscale conversion on clean data
3. Light contrast enhancement for viewability
4. Character boundary hysteresis to prevent flickering
5. Temporal smoothing for compression

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

# Character boundary hysteresis threshold (pixels)
HYSTERESIS_THRESHOLD = 8

def process_video(input_file: str, output_file: str, resolution: Optional[str] = None, 
                 preview_mode: bool = False, verbose: bool = False) -> None:
    """
    Main video processing function with character boundary hysteresis
    
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
    
    # Process frames to ASCII with character boundary hysteresis
    ascii_frames = []
    frame_index = 0
    prev_ascii_frame = None
    
    print("Converting to ASCII with character boundary hysteresis...")
    
    while frame_index < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert frame to ASCII using hysteresis
        ascii_frame = frame_to_ascii_with_hysteresis(
            frame, target_width, target_height, prev_ascii_frame
        )
        ascii_frames.append(ascii_frame)
        prev_ascii_frame = ascii_frame  # Track for next frame
        
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
    
    # Apply ASCII character pattern cleanup for compression optimization
    print("Applying ASCII character pattern cleanup...")
    ascii_frames = cleanup_ascii_patterns(
        ascii_frames, 
        verbose,
        enable_isolated_replacement=True,
        enable_run_consolidation=True,
        enable_temporal_smoothing=True,
        enable_spatial_coherence=False
    )
    
    # Note: cleanup_ascii_patterns() includes temporal smoothing in Stage 3
    # No additional temporal smoothing needed
    
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


def frame_to_ascii_with_hysteresis(frame: np.ndarray, target_width: Optional[int] = None, 
                                  target_height: Optional[int] = None, 
                                  prev_ascii_frame: Optional[List[List[str]]] = None) -> List[List[str]]:
    """
    Convert video frame to ASCII using progressive smoothing pipeline and character boundary hysteresis
    
    Args:
        frame: OpenCV frame (BGR format)
        target_width: Override width (None for auto)
        target_height: Override height (None for auto)
        prev_ascii_frame: Previous frame's ASCII for hysteresis comparison
        
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
    
    # Convert pixels to ASCII with character boundary hysteresis
    ascii_frame = []
    for row_idx, row in enumerate(resized):
        ascii_row = []
        for col_idx, pixel in enumerate(row):
            
            # Standard pixel-to-character conversion (safe from overflow)
            char_index = min(int(pixel) * len(ASCII_CHARS) // 256, len(ASCII_CHARS) - 1)
            
            # Apply character boundary hysteresis if we have previous frame
            if (prev_ascii_frame and 
                row_idx < len(prev_ascii_frame) and 
                col_idx < len(prev_ascii_frame[row_idx])):
                
                prev_char = prev_ascii_frame[row_idx][col_idx]
                try:
                    prev_index = ASCII_CHARS.index(prev_char)
                    
                    # Bounds check to prevent overflow
                    if (0 <= char_index < len(ASCII_CHARS) and 
                        0 <= prev_index < len(ASCII_CHARS)):
                        
                        # Check if this is an adjacent character boundary
                        if abs(char_index - prev_index) == 1:  # Adjacent character transition
                            
                            # Calculate pixel value at character boundary
                            boundary_pixel = (prev_index + 0.5) * (256 // len(ASCII_CHARS))
                            pixel_distance = abs(pixel - boundary_pixel)
                            
                            # Apply hysteresis: only change if pixel moved significantly
                            if pixel_distance < HYSTERESIS_THRESHOLD:
                                char_index = prev_index  # Stick with previous character
                            
                except ValueError:
                    # Previous character not in ASCII_CHARS - ignore hysteresis
                    pass
            
            ascii_row.append(ASCII_CHARS[char_index])
        ascii_frame.append(ascii_row)
    
    return ascii_frame


def cleanup_ascii_patterns(ascii_frames: List[List[List[str]]], verbose: bool = False, 
                         enable_isolated_replacement: bool = True,
                         enable_run_consolidation: bool = True,
                         enable_temporal_smoothing: bool = True,
                         enable_spatial_coherence: bool = True) -> List[List[List[str]]]:
    """
    Clean up ASCII character patterns to improve compression efficiency
    
    Removes character noise that fragments RLE runs while preserving facial features:
    1. Isolated character replacement
    2. Run consolidation  
    3. Temporal character smoothing
    4. Spatial coherence filtering
    
    Args:
        ascii_frames: List of 2D ASCII character arrays
        verbose: Print detailed cleanup statistics
        
    Returns:
        Cleaned ASCII frames with better compression characteristics
    """
    
    if not ascii_frames:
        return ascii_frames
    
    total_frames = len(ascii_frames)
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    
    print(f"Character pattern cleanup: {total_frames} frames ({width}x{height})")
    
    # Statistics tracking
    isolated_replacements = 0
    run_consolidations = 0
    temporal_smoothed = 0
    spatial_corrections = 0
    
    # Stage 1: Isolated character replacement (spatial cleanup)
    if enable_isolated_replacement:
        if verbose:
            print("  Stage 1: Isolated character replacement...")
    else:
        if verbose:
            print("  Stage 1: SKIPPED - Isolated character replacement disabled")
    
    cleaned_frames = []
    for frame_idx, frame in enumerate(ascii_frames):
        cleaned_frame = []
        
        for row_idx, row in enumerate(frame):
            cleaned_row = []
            
            for col_idx, char in enumerate(row):
                if enable_isolated_replacement:
                    # Check if this character is isolated (different from all neighbours)
                    neighbours = get_character_neighbours(frame, row_idx, col_idx)
                    
                    if len(neighbours) >= 3:  # Need enough neighbours to judge
                        # Count character frequencies in neighbourhood
                        char_counts = {}
                        for neighbour_char in neighbours:
                            char_counts[neighbour_char] = char_counts.get(neighbour_char, 0) + 1
                        
                        # If current character is alone and neighbours agree on replacement
                        if char not in char_counts or char_counts[char] == 0:
                            # Find most common neighbour character
                            most_common_char = max(char_counts.items(), key=lambda x: x[1])[0]
                            
                            # Replace if neighbours strongly agree (majority)
                            if char_counts[most_common_char] >= len(neighbours) // 2:
                                cleaned_row.append(most_common_char)
                                isolated_replacements += 1
                            else:
                                cleaned_row.append(char)  # Keep original if no clear majority
                        else:
                            cleaned_row.append(char)  # Keep character if it fits neighbourhood
                    else:
                        cleaned_row.append(char)  # Keep edge characters
                else:
                    cleaned_row.append(char)  # Skip replacement if disabled
                    
            cleaned_frame.append(cleaned_row)
        cleaned_frames.append(cleaned_frame)
        
        # Progress reporting
        if enable_isolated_replacement and frame_idx % max(1, total_frames // 10) == 0:
            progress = (frame_idx + 1) / total_frames
            print(f"    Cleanup progress: {progress*100:.0f}% ({frame_idx + 1}/{total_frames})")
    
    # Stage 2: Run consolidation (horizontal pattern cleanup)
    if enable_run_consolidation:
        if verbose:
            print("  Stage 2: Run consolidation...")
        
        for frame_idx, frame in enumerate(cleaned_frames):
            for row_idx, row in enumerate(frame):
                # Consolidate short interrupted runs
                consolidated_row = consolidate_character_runs(row)
                run_consolidations += len(row) - len(consolidated_row)  # Rough metric
                cleaned_frames[frame_idx][row_idx] = consolidated_row
    else:
        if verbose:
            print("  Stage 2: SKIPPED - Run consolidation disabled")
    
    # Stage 3: Temporal character smoothing (suppress single-frame flickers)
    if enable_temporal_smoothing:
        if verbose:
            print("  Stage 3: Temporal character smoothing...")
        
        if total_frames >= 3:  # Need multiple frames for temporal analysis
            for frame_idx in range(1, total_frames - 1):  # Skip first and last frames
                prev_frame = cleaned_frames[frame_idx - 1]
                curr_frame = cleaned_frames[frame_idx]
                next_frame = cleaned_frames[frame_idx + 1]
                
                for row_idx in range(height):
                    for col_idx in range(width):
                        prev_char = prev_frame[row_idx][col_idx]
                        curr_char = curr_frame[row_idx][col_idx]
                        next_char = next_frame[row_idx][col_idx]
                        
                        # Suppress single-frame character flickers (A→B→A pattern)
                        if prev_char == next_char and curr_char != prev_char:
                            # Check if this looks like temporal noise vs genuine motion
                            if is_temporal_noise(prev_char, curr_char, next_char):
                                cleaned_frames[frame_idx][row_idx][col_idx] = prev_char
                                temporal_smoothed += 1
    else:
        if verbose:
            print("  Stage 3: SKIPPED - Temporal character smoothing disabled")
    
    # Stage 4: Spatial coherence filtering (character context validation)
    if enable_spatial_coherence:
        if verbose:
            print("  Stage 4: Spatial coherence filtering...")
        
        for frame_idx, frame in enumerate(cleaned_frames):
            for row_idx in range(height):
                for col_idx in range(width):
                    char = frame[row_idx][col_idx]
                    
                    # Check if character fits spatial context
                    context_chars = get_spatial_context(frame, row_idx, col_idx, radius=2)
                    
                    if not fits_spatial_context(char, context_chars):
                        # Find better character that fits context
                        better_char = find_contextual_replacement(char, context_chars)
                        if better_char != char:
                            cleaned_frames[frame_idx][row_idx][col_idx] = better_char
                            spatial_corrections += 1
    else:
        if verbose:
            print("  Stage 4: SKIPPED - Spatial coherence filtering disabled")
    
    # Print cleanup statistics
    total_changes = isolated_replacements + run_consolidations + temporal_smoothed + spatial_corrections
    
    if verbose:
        print(f"\n=== ASCII PATTERN CLEANUP RESULTS ===")
        print(f"Isolated character replacements: {isolated_replacements}")
        print(f"Run consolidations: {run_consolidations}")
        print(f"Temporal smoothing corrections: {temporal_smoothed}")
        print(f"Spatial coherence corrections: {spatial_corrections}")
        print(f"Total pattern changes: {total_changes}")
        
        if total_changes > 0:
            change_percent = (total_changes / (total_frames * height * width)) * 100
            print(f"Pattern change percentage: {change_percent:.2f}%")
    else:
        print(f"Pattern cleanup: {total_changes} character corrections applied")
    
    return cleaned_frames


def get_character_neighbours(frame: List[List[str]], row: int, col: int) -> List[str]:
    """Get characters in 3x3 neighbourhood around position"""
    
    neighbours = []
    height = len(frame)
    width = len(frame[0]) if frame else 0
    
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:  # Skip center character
                continue
                
            r, c = row + dr, col + dc
            if 0 <= r < height and 0 <= c < width:
                neighbours.append(frame[r][c])
    
    return neighbours


def consolidate_character_runs(row: List[str]) -> List[str]:
    """
    Consolidate interrupted character runs to improve RLE compression
    
    Converts patterns like ['=', '=', '+', '=', '='] to ['=', '=', '=', '=', '=']
    Only consolidates if interruption is very short (1-2 characters)
    """
    
    if len(row) < 5:  # Too short to consolidate
        return row
    
    consolidated = row.copy()
    changed = True
    
    # Multiple passes to handle chains of interruptions
    while changed:
        changed = False
        new_row = []
        i = 0
        
        while i < len(consolidated):
            if i < len(consolidated) - 4:  # Need at least 5 characters to check pattern
                # Look for pattern: A A B A A (single character interruption)
                if (consolidated[i] == consolidated[i+1] == consolidated[i+3] == consolidated[i+4] and
                    consolidated[i+2] != consolidated[i]):
                    
                    # Replace interruption with surrounding character
                    new_row.extend([consolidated[i]] * 5)
                    i += 5
                    changed = True
                    continue
            
            new_row.append(consolidated[i])
            i += 1
        
        consolidated = new_row
    
    return consolidated


def is_temporal_noise(prev_char: str, curr_char: str, next_char: str) -> bool:
    """
    Determine if character change looks like temporal noise vs genuine motion
    
    Returns True if the middle character looks like noise that should be smoothed
    """
    
    # Character similarity - adjacent characters in ASCII progression are more likely noise
    ascii_order = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
    
    try:
        prev_idx = ascii_order.index(prev_char)
        curr_idx = ascii_order.index(curr_char)
        next_idx = ascii_order.index(next_char)
        
        # If curr_char is only 1 step away from prev/next, likely boundary noise
        if (abs(curr_idx - prev_idx) <= 1 or abs(curr_idx - next_idx) <= 1):
            return True
            
    except ValueError:
        # Character not in progression - treat conservatively
        pass
    
    # Default: assume genuine change
    return False


def get_spatial_context(frame: List[List[str]], row: int, col: int, radius: int = 2) -> List[str]:
    """Get characters in larger spatial context around position"""
    
    context = []
    height = len(frame)
    width = len(frame[0]) if frame else 0
    
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if dr == 0 and dc == 0:  # Skip center
                continue
                
            r, c = row + dr, col + dc
            if 0 <= r < height and 0 <= c < width:
                context.append(frame[r][c])
    
    return context


def fits_spatial_context(char: str, context_chars: List[str]) -> bool:
    """Check if character fits well with spatial context"""
    
    if not context_chars:
        return True  # No context to check against
    
    # Count character frequencies in context
    char_counts = {}
    for ctx_char in context_chars:
        char_counts[ctx_char] = char_counts.get(ctx_char, 0) + 1
    
    # Character fits if it appears in context or is adjacent to common context chars
    if char in char_counts:
        return True
    
    # Check if character is adjacent to common context characters
    ascii_order = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
    
    try:
        char_idx = ascii_order.index(char)
        
        for ctx_char, count in char_counts.items():
            if count >= len(context_chars) // 4:  # Reasonably common in context
                try:
                    ctx_idx = ascii_order.index(ctx_char)
                    if abs(char_idx - ctx_idx) <= 1:  # Adjacent characters
                        return True
                except ValueError:
                    continue
                    
    except ValueError:
        # Character not in progression
        pass
    
    return False


def find_contextual_replacement(char: str, context_chars: List[str]) -> str:
    """Find better character replacement based on spatial context"""
    
    if not context_chars:
        return char


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
                median_val = int(sorted(window_vals)[len(window_vals)//2])
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
    
    # Find most common character in context
    char_counts = {}
    for ctx_char in context_chars:
        char_counts[ctx_char] = char_counts.get(ctx_char, 0) + 1
    
    if char_counts:
        # Return most frequent context character
        most_common = max(char_counts.items(), key=lambda x: x[1])[0]
        return most_common
    
    return char
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


def test_hysteresis_effectiveness(video_path: str, max_frames: int = 60) -> None:
    """
    Test compression improvement from character boundary hysteresis
    """
    
    print("=== HYSTERESIS EFFECTIVENESS TEST ===")
    
    # Load video
    cap, fps, frame_count = load_video(video_path)
    max_frames = min(max_frames, frame_count)
    
    print(f"Testing {max_frames} frames from: {video_path}")
    
    # Process without hysteresis
    print("\n--- Without Hysteresis ---")
    ascii_frames_no_hyst = []
    frame_idx = 0
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start
    while frame_idx < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert without hysteresis (prev_ascii_frame=None)
        ascii_frame = frame_to_ascii_with_hysteresis(frame, None, None, None)
        ascii_frames_no_hyst.append(ascii_frame)
        frame_idx += 1
    
    # Compress and measure
    result_no_hyst = moc.compress_video_rle(ascii_frames_no_hyst, fps=fps, verbose=False)
    ratio_no_hyst = result_no_hyst.stats.overall_ratio if result_no_hyst.stats else 0
    
    print(f"Without hysteresis: {ratio_no_hyst:.1f}:1 compression")
    
    # Process with hysteresis
    print("\n--- With Hysteresis ---")
    ascii_frames_with_hyst = []
    prev_ascii_frame = None
    frame_idx = 0
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to start
    while frame_idx < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert with hysteresis
        ascii_frame = frame_to_ascii_with_hysteresis(frame, None, None, prev_ascii_frame)
        ascii_frames_with_hyst.append(ascii_frame)
        prev_ascii_frame = ascii_frame
        frame_idx += 1
    
    cap.release()
    
    # Compress and measure
    result_with_hyst = moc.compress_video_rle(ascii_frames_with_hyst, fps=fps, verbose=False)
    ratio_with_hyst = result_with_hyst.stats.overall_ratio if result_with_hyst.stats else 0
    
    print(f"With hysteresis: {ratio_with_hyst:.1f}:1 compression")
    
    # Compare results
    improvement = ratio_with_hyst - ratio_no_hyst
    improvement_percent = (improvement / ratio_no_hyst) * 100 if ratio_no_hyst > 0 else 0
    
    print(f"\n=== HYSTERESIS IMPACT ===")
    print(f"Improvement: +{improvement:.1f}:1 ({improvement_percent:.1f}%)")
    
    if improvement > 1.0:
        print("✅ SIGNIFICANT IMPROVEMENT - Hysteresis working well")
    elif improvement > 0.2:
        print("✅ MODEST IMPROVEMENT - Hysteresis helping")
    elif improvement > 0:
        print("⚠️  MINOR IMPROVEMENT - Small benefit")
    else:
        print("❌ NO IMPROVEMENT - Hysteresis not helping")
    
    # Check if we hit the 10:1 target
    if ratio_with_hyst >= 10.0:
        print("🎯 TARGET ACHIEVED: 10:1+ compression ratio reached!")
    elif ratio_with_hyst >= 7.0:
        print("🔥 CLOSE TO TARGET: 7:1+ compression, getting there")
    else:
        print(f"📈 PROGRESS: {ratio_with_hyst:.1f}:1 achieved, need {10.0 - ratio_with_hyst:.1f}:1 more")


def tune_hysteresis_threshold(video_path: str, max_frames: int = 30) -> int:
    """
    Find optimal hysteresis threshold for maximum compression
    """
    
    global HYSTERESIS_THRESHOLD
    
    print("=== HYSTERESIS THRESHOLD TUNING ===")
    
    # Load video sample
    cap, fps, frame_count = load_video(video_path)
    max_frames = min(max_frames, frame_count)
    
    # Load sample frames
    sample_frames = []
    frame_idx = 0
    while frame_idx < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        sample_frames.append(frame)
        frame_idx += 1
    
    cap.release()
    print(f"Testing on {len(sample_frames)} frames")
    
    # Test different threshold values
    thresholds = [4, 8, 12, 16, 20, 24]
    best_threshold = HYSTERESIS_THRESHOLD
    best_ratio = 0
    
    for threshold in thresholds:
        print(f"\nTesting threshold = {threshold}")
        HYSTERESIS_THRESHOLD = threshold
        
        # Process frames with this threshold
        ascii_frames = []
        prev_ascii_frame = None
        
        for frame in sample_frames:
            ascii_frame = frame_to_ascii_with_hysteresis(frame, None, None, prev_ascii_frame)
            ascii_frames.append(ascii_frame)
            prev_ascii_frame = ascii_frame
        
        # Test compression
        result = moc.compress_video_rle(ascii_frames, fps=fps, verbose=False)
        ratio = result.stats.overall_ratio if result.stats else 0
        
        print(f"Threshold {threshold}: {ratio:.1f}:1 compression")
        
        if ratio > best_ratio:
            best_ratio = ratio
            best_threshold = threshold
    
    # Restore optimal threshold
    HYSTERESIS_THRESHOLD = best_threshold
    
    print(f"\n=== OPTIMAL THRESHOLD ===")
    print(f"Best threshold: {best_threshold} pixels")
    print(f"Best compression: {best_ratio:.1f}:1")
    
    return best_threshold


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
    
    # Convert to ASCII (no hysteresis for single image)
    print("Converting image to ASCII with progressive smoothing...")
    ascii_frame = frame_to_ascii_with_hysteresis(img, target_width, target_height, None)
    
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
        ascii_frame = frame_to_ascii_with_hysteresis(frame, 120, None, None)
        print("First frame ASCII conversion (with hysteresis support):")
        print_ascii_frame(ascii_frame)
    
    cap.release()


def test_image(image_path: str, width: int = 120) -> None:
    """Test ASCII conversion on a single image using hysteresis-enabled pipeline"""
    process_image(image_path, "test_output.txv", f"{width}x", verbose=True)


if __name__ == "__main__":
    # Quick test when run directly
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].endswith(('.jpg', '.png', '.jpeg')):
            test_image(sys.argv[1])
        elif sys.argv[1] == "test_hysteresis":
            if len(sys.argv) > 2:
                test_hysteresis_effectiveness(sys.argv[2])
            else:
                print("Usage: python vid.py test_hysteresis <video_file>")
        elif sys.argv[1] == "tune_threshold":
            if len(sys.argv) > 2:
                tune_hysteresis_threshold(sys.argv[2])
            else:
                print("Usage: python vid.py tune_threshold <video_file>")
        else:
            test_single_frame(sys.argv[1])
    else:
        print("Usage: python vid.py <video_file_or_image>")
        print("       python vid.py test_hysteresis <video_file>")
        print("       python vid.py tune_threshold <video_file>")