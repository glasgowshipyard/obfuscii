"""
OBFUSCII Video Processing Module

Clean video-to-ASCII conversion optimized for compression:
1. Progressive smoothing (bilateral → gaussian → median)
2. Character boundary hysteresis
3. Modular cleanup pipeline
4. Temporal smoothing
"""

import cv2
import numpy as np
import time
import os
import sys
from typing import List, Tuple, Optional
from . import moc

# Character set - dark to light progression
ASCII_CHARS = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']

# Character boundary hysteresis threshold (pixels)
HYSTERESIS_THRESHOLD = 8

def load_video(filename: str) -> Tuple[cv2.VideoCapture, float, int]:
    """Load video file and extract metadata"""
    cap = cv2.VideoCapture(filename)
    
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {filename}")
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    return cap, fps, frame_count

def parse_resolution(resolution: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Parse resolution string like "140x80" into width, height"""
    if not resolution:
        return None, None
        
    try:
        width_str, height_str = resolution.split('x')
        return int(width_str), int(height_str)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid resolution format: {resolution}. Use WIDTHxHEIGHT (e.g. 140x80)")

def progressive_smoothing(frame: np.ndarray) -> np.ndarray:
    """
    Progressive smoothing cascade for ASCII compression optimization
    
    1. Bilateral filter - preserves edges, removes noise
    2. Gaussian blur - eliminates texture patterns  
    3. Median filter - removes salt-and-pepper artifacts
    4. Light contrast enhancement for viewability
    """
    # Bilateral filter - preserves structural edges
    smooth1 = cv2.bilateralFilter(frame, 15, 80, 80)
    
    # Gaussian blur - creates smooth gradients
    smooth2 = cv2.GaussianBlur(smooth1, (9, 9), 0)
    
    # Median filter - removes remaining artifacts
    smooth3 = cv2.medianBlur(smooth2, 5)
    
    # Convert to greyscale
    gray = cv2.cvtColor(smooth3, cv2.COLOR_BGR2GRAY)
    
    # Light contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    return enhanced

def frame_to_ascii_with_hysteresis(frame: np.ndarray, target_width: Optional[int] = None, 
                                  target_height: Optional[int] = None, 
                                  prev_ascii_frame: Optional[List[List[str]]] = None) -> List[List[str]]:
    """Convert video frame to ASCII using progressive smoothing and character boundary hysteresis"""
    
    # Apply progressive smoothing
    processed_frame = progressive_smoothing(frame)
    
    # Determine target dimensions
    if target_width and target_height:
        new_width, new_height = target_width, target_height
    else:
        # Auto-size for terminal display
        height, width = processed_frame.shape
        aspect_ratio = height / width
        new_width = 120
        new_height = int(aspect_ratio * new_width * 0.55)  # Terminal compensation
    
    # Resize frame
    resized = cv2.resize(processed_frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # Convert pixels to ASCII with hysteresis
    ascii_frame = []
    for row_idx, row in enumerate(resized):
        ascii_row = []
        for col_idx, pixel in enumerate(row):
            
            # Standard pixel-to-character conversion
            char_index = min(int(pixel) * len(ASCII_CHARS) // 256, len(ASCII_CHARS) - 1)
            
            # Apply hysteresis if we have previous frame
            if (prev_ascii_frame and 
                row_idx < len(prev_ascii_frame) and 
                col_idx < len(prev_ascii_frame[row_idx])):
                
                prev_char = prev_ascii_frame[row_idx][col_idx]
                try:
                    prev_index = ASCII_CHARS.index(prev_char)
                    
                    if (0 <= char_index < len(ASCII_CHARS) and 
                        0 <= prev_index < len(ASCII_CHARS)):
                        
                        # Check for adjacent character boundary
                        if abs(char_index - prev_index) == 1:
                            boundary_pixel = (prev_index + 0.5) * (256 // len(ASCII_CHARS))
                            pixel_distance = abs(pixel - boundary_pixel)
                            
                            # Apply hysteresis threshold
                            if pixel_distance < HYSTERESIS_THRESHOLD:
                                char_index = prev_index
                            
                except ValueError:
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
    Clean up ASCII patterns for compression optimization
    
    4-stage modular pipeline:
    1. Isolated character replacement
    2. Run consolidation  
    3. Temporal smoothing
    4. Spatial coherence filtering
    """
    
    if not ascii_frames:
        return ascii_frames
    
    total_frames = len(ascii_frames)
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    
    if verbose:
        print(f"Character pattern cleanup: {total_frames} frames ({width}x{height})")
    
    cleaned_frames = ascii_frames.copy()
    total_changes = 0
    
    # Stage 1: Isolated character replacement
    if enable_isolated_replacement:
        if verbose:
            print("  Stage 1: Isolated character replacement...")
        
        for frame_idx, frame in enumerate(cleaned_frames):
            for row_idx, row in enumerate(frame):
                for col_idx, char in enumerate(row):
                    neighbours = get_character_neighbours(frame, row_idx, col_idx)
                    
                    if len(neighbours) >= 3:
                        char_counts = {}
                        for neighbour_char in neighbours:
                            char_counts[neighbour_char] = char_counts.get(neighbour_char, 0) + 1
                        
                        if char not in char_counts or char_counts[char] == 0:
                            most_common_char = max(char_counts.items(), key=lambda x: x[1])[0]
                            
                            if char_counts[most_common_char] >= len(neighbours) // 2:
                                cleaned_frames[frame_idx][row_idx][col_idx] = most_common_char
                                total_changes += 1
    
    # Stage 2: Run consolidation
    if enable_run_consolidation:
        if verbose:
            print("  Stage 2: Run consolidation...")
        
        for frame_idx, frame in enumerate(cleaned_frames):
            for row_idx, row in enumerate(frame):
                consolidated_row = consolidate_character_runs(row)
                cleaned_frames[frame_idx][row_idx] = consolidated_row
    
    # Stage 3: Temporal smoothing
    if enable_temporal_smoothing:
        if verbose:
            print("  Stage 3: Temporal smoothing...")
        
        if total_frames >= 3:
            for frame_idx in range(1, total_frames - 1):
                prev_frame = cleaned_frames[frame_idx - 1]
                curr_frame = cleaned_frames[frame_idx]
                next_frame = cleaned_frames[frame_idx + 1]
                
                for row_idx in range(height):
                    for col_idx in range(width):
                        prev_char = prev_frame[row_idx][col_idx]
                        curr_char = curr_frame[row_idx][col_idx]
                        next_char = next_frame[row_idx][col_idx]
                        
                        # Suppress A→B→A flicker patterns
                        if prev_char == next_char and curr_char != prev_char:
                            if is_temporal_noise(prev_char, curr_char, next_char):
                                cleaned_frames[frame_idx][row_idx][col_idx] = prev_char
                                total_changes += 1
    
    # Stage 4: Spatial coherence filtering
    if enable_spatial_coherence:
        if verbose:
            print("  Stage 4: Spatial coherence filtering...")
        
        for frame_idx, frame in enumerate(cleaned_frames):
            for row_idx in range(height):
                for col_idx in range(width):
                    char = frame[row_idx][col_idx]
                    
                    context_chars = get_spatial_context(frame, row_idx, col_idx, radius=2)
                    
                    if not fits_spatial_context(char, context_chars):
                        better_char = find_contextual_replacement(char, context_chars)
                        if better_char != char:
                            cleaned_frames[frame_idx][row_idx][col_idx] = better_char
                            total_changes += 1
    
    if verbose:
        change_percent = (total_changes / (total_frames * height * width)) * 100
        print(f"Pattern cleanup: {total_changes} corrections ({change_percent:.2f}%)")
    
    return cleaned_frames

def get_character_neighbours(frame: List[List[str]], row: int, col: int) -> List[str]:
    """Get characters in 3x3 neighbourhood"""
    neighbours = []
    height = len(frame)
    width = len(frame[0]) if frame else 0
    
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
                
            r, c = row + dr, col + dc
            if 0 <= r < height and 0 <= c < width:
                neighbours.append(frame[r][c])
    
    return neighbours

def consolidate_character_runs(row: List[str]) -> List[str]:
    """Consolidate interrupted character runs for better RLE compression"""
    if len(row) < 5:
        return row
    
    consolidated = row.copy()
    changed = True
    
    while changed:
        changed = False
        new_row = []
        i = 0
        
        while i < len(consolidated):
            if i < len(consolidated) - 4:
                # Look for A A B A A pattern
                if (consolidated[i] == consolidated[i+1] == consolidated[i+3] == consolidated[i+4] and
                    consolidated[i+2] != consolidated[i]):
                    
                    new_row.extend([consolidated[i]] * 5)
                    i += 5
                    changed = True
                    continue
            
            new_row.append(consolidated[i])
            i += 1
        
        consolidated = new_row
    
    return consolidated

def is_temporal_noise(prev_char: str, curr_char: str, next_char: str) -> bool:
    """Determine if character change is temporal noise"""
    try:
        prev_idx = ASCII_CHARS.index(prev_char)
        curr_idx = ASCII_CHARS.index(curr_char)
        next_idx = ASCII_CHARS.index(next_char)
        
        # Adjacent characters in progression are likely boundary noise
        if (abs(curr_idx - prev_idx) <= 1 or abs(curr_idx - next_idx) <= 1):
            return True
            
    except ValueError:
        pass
    
    return False

def get_spatial_context(frame: List[List[str]], row: int, col: int, radius: int = 2) -> List[str]:
    """Get characters in spatial context around position"""
    context = []
    height = len(frame)
    width = len(frame[0]) if frame else 0
    
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if dr == 0 and dc == 0:
                continue
                
            r, c = row + dr, col + dc
            if 0 <= r < height and 0 <= c < width:
                context.append(frame[r][c])
    
    return context

def fits_spatial_context(char: str, context_chars: List[str]) -> bool:
    """Check if character fits spatial context using salt-and-pepper detection"""
    if not context_chars:
        return True
    
    # Count character frequencies
    char_counts = {}
    for ctx_char in context_chars:
        char_counts[ctx_char] = char_counts.get(ctx_char, 0) + 1
    
    current_char_count = char_counts.get(char, 0)
    current_char_frequency = current_char_count / len(context_chars)
    
    # Character appears frequently in neighbourhood
    if current_char_frequency >= 0.15:
        return True
    
    # Check neighbourhood uniformity
    if char_counts:
        most_common_char = max(char_counts.items(), key=lambda x: x[1])[0]
        most_common_count = char_counts[most_common_char]
        neighbourhood_uniformity = most_common_count / len(context_chars)
        
        # Uniform region with isolated outlier
        if neighbourhood_uniformity >= 0.7:
            return False
    
    # Preserve facial features
    facial_feature_chars = ['#', '*', '%', '@']
    if char in facial_feature_chars:
        return True
    
    return True

def find_contextual_replacement(char: str, context_chars: List[str]) -> str:
    """Find replacement character using median-filter approach"""
    if not context_chars:
        return char
    
    char_counts = {}
    for ctx_char in context_chars:
        char_counts[ctx_char] = char_counts.get(ctx_char, 0) + 1
    
    if char_counts:
        most_common = max(char_counts.items(), key=lambda x: x[1])[0]
        return most_common
    
    return char

def play_ascii_video(ascii_frames: List[List[List[str]]], fps: float = 30.0) -> None:
    """Play ASCII video in terminal"""
    if not ascii_frames:
        return
        
    time_delta = 1.0 / fps
    
    print("Press Ctrl+C to stop")
    input("Press Enter to start playback...")
    
    # Clear screen
    sys.stdout.write('\033[2J')
    sys.stdout.flush()
    
    try:
        for frame_idx, ascii_frame in enumerate(ascii_frames):
            t0 = time.process_time()
            
            # Get terminal size
            try:
                rows, cols = os.popen('stty size', 'r').read().split()
                cols, rows = int(cols), int(rows)
            except:
                cols, rows = 80, 24
            
            # Move cursor to home
            sys.stdout.write('\u001b[0;0H')
            
            # Resize frame to fit terminal
            resized_frame = resize_frame_to_terminal(ascii_frame, (cols, rows))
            
            # Convert to string
            msg = ''
            for row in resized_frame:
                for char in row:
                    msg += char
                msg += '\r\n'
            
            # Frame rate limiting
            t1 = time.process_time()
            delta = time_delta - (t1 - t0)
            if delta > 0:
                time.sleep(delta)
                
            # Display frame
            sys.stdout.write(msg)
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\n\nPlayback stopped")
        sys.stdout.flush()

def resize_frame_to_terminal(ascii_frame: List[List[str]], dimensions: Tuple[int, int]) -> List[List[str]]:
    """Resize ASCII frame to fit terminal dimensions"""
    cols, rows = dimensions
    frame_height = len(ascii_frame)
    frame_width = len(ascii_frame[0]) if ascii_frame else 0
    
    if frame_height == 0 or frame_width == 0:
        return ascii_frame
    
    # Calculate scaling
    height_ratio = (rows - 1) / frame_height
    width_ratio = cols / frame_width
    scale_factor = min(height_ratio, width_ratio)
    
    # Calculate new dimensions
    new_height = int(frame_height * scale_factor)
    new_width = int(frame_width * scale_factor)
    
    # Sample original frame
    resized = []
    for new_row in range(new_height):
        orig_row = int(new_row / scale_factor)
        if orig_row >= len(ascii_frame):
            break
            
        row_chars = []
        for new_col in range(new_width):
            orig_col = int(new_col / scale_factor)
            if orig_col < len(ascii_frame[orig_row]):
                row_chars.append(ascii_frame[orig_row][orig_col])
            else:
                row_chars.append(' ')
        
        resized.append(row_chars)
    
    return resized

def process_video_to_compressed(input_file: str, target_width: Optional[int] = None, 
                               target_height: Optional[int] = None, 
                               max_frames: Optional[int] = None,
                               verbose: bool = False) -> moc.CompressedVideo:
    """
    Process video file to compressed ASCII video
    
    Returns CompressedVideo object ready for .txv export
    """
    
    if verbose:
        print(f"Loading video: {input_file}")
    
    # Load video
    cap, fps, frame_count = load_video(input_file)
    
    if verbose:
        print(f"Video loaded: {frame_count} frames at {fps:.1f} FPS")
    
    # Determine frame limit
    if max_frames:
        max_frames = min(max_frames, frame_count)
    else:
        max_frames = frame_count
    
    # Process frames to ASCII
    ascii_frames = []
    frame_index = 0
    prev_ascii_frame = None
    
    print("Converting to ASCII...")
    
    while frame_index < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        ascii_frame = frame_to_ascii_with_hysteresis(
            frame, target_width, target_height, prev_ascii_frame
        )
        ascii_frames.append(ascii_frame)
        prev_ascii_frame = ascii_frame
        
        if verbose and frame_index % 30 == 0:
            print(f"Processed frame {frame_index}/{max_frames}")
        elif not verbose and frame_index % 60 == 0:
            print(f"Processed frame {frame_index}/{max_frames}")
            
        frame_index += 1
    
    cap.release()
    
    if len(ascii_frames) == 0:
        raise ValueError("No frames processed")
    
    print(f"Conversion complete: {len(ascii_frames)} frames")
    
    # Apply cleanup
    print("Applying character cleanup...")
    ascii_frames = cleanup_ascii_patterns(
        ascii_frames, 
        verbose,
        enable_isolated_replacement=True,
        enable_run_consolidation=True,
        enable_temporal_smoothing=True,
        enable_spatial_coherence=True
    )
    
    # Compress
    print("Compressing...")
    if verbose:
        compressed_result = moc.compress_video_rle(ascii_frames, fps=fps, verbose=True)
        moc.analyze_compression_performance(ascii_frames, compressed_result)
    else:
        compressed_result = moc.compress_video_rle(ascii_frames, fps=fps, verbose=False)
    
    return compressed_result