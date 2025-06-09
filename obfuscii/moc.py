"""
OBFUSCII Compression Engine

RLE + LZMA compression targeting 10:1 ratio.
Exploits horizontal run-length patterns in ASCII art.
"""

import lzma
import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CompressionStats:
    """Compression statistics container"""
    total_frames: int
    original_video_size: int
    ascii_text_size: int
    total_compressed_size: int
    ascii_compression_ratio: float
    overall_compression_ratio: float
    ascii_expansion_factor: float
    ascii_size_mb: float
    compressed_size_mb: float
    original_size_mb: float
    space_saved_mb: float
    space_saved_percent: float

@dataclass
class FrameResult:
    """Single frame compression result"""
    frame_index: int
    frame_type: str  # 'I' (RLE) or 'P' (Delta)
    timestamp: float
    raw_size: int
    compressed_size: int
    compression_ratio: float
    compressed_data: bytes

class CompressedVideo:
    """Container for compressed ASCII video"""
    
    def __init__(self, width: int, height: int, fps: float, original_video_size: int = 0):
        self.width = width
        self.height = height
        self.fps = fps
        self.original_video_size = original_video_size
        self.frames: List[FrameResult] = []
        self.stats: Optional[CompressionStats] = None
        self.metadata = {
            'version': '3.0',
            'algorithm': 'middle-out-rle-lzma',
            'created_by': 'OBFUSCII'
        }

def compress_video_rle(ascii_frames: List[List[List[str]]], fps: float = 30.0, 
                      original_video_size: int = 0, verbose: bool = False) -> CompressedVideo:
    """
    Primary compression function using middle-out RLE + LZMA
    
    Shows both ASCII compression (text → compressed) and overall compression (video → compressed)
    """
    
    if not ascii_frames:
        raise ValueError("No frames to compress")
    
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    frame_char_count = width * height
    
    if verbose:
        print(f"Middle-out compression: {len(ascii_frames)} frames ({width}x{height})")
        print("Algorithm: ASCII Expansion + RLE + LZMA")
    
    compressed = CompressedVideo(width, height, fps, original_video_size)
    total_compressed_size = 0
    
    # Calculate raw ASCII text size
    total_ascii_chars = 0
    for frame in ascii_frames:
        for row in frame:
            total_ascii_chars += len(row) + 1  # +1 for newline
        total_ascii_chars -= 1  # Remove last newline
    
    ascii_text_size = total_ascii_chars  # bytes (1 char = 1 byte)
    
    if verbose:
        print(f"Raw ASCII text: {ascii_text_size:,} characters ({ascii_text_size / 1024 / 1024:.1f} MB)")
    
    # Process each frame with RLE compression
    for frame_idx, ascii_frame in enumerate(ascii_frames):
        timestamp = frame_idx / fps
        raw_size = frame_char_count
        
        # Apply run-length encoding
        rle_segments = encode_frame_rle(ascii_frame)
        
        # Compress with LZMA
        compressed_data = compress_rle_segments(rle_segments)
        compressed_size = len(compressed_data)
        
        # Calculate compression ratio for this frame
        compression_ratio = raw_size / compressed_size if compressed_size > 0 else 0
        
        # Store frame result
        frame_result = FrameResult(
            frame_index=frame_idx,
            frame_type='I',  # All frames are I-frames with RLE
            timestamp=timestamp,
            raw_size=raw_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compressed_data=compressed_data
        )
        
        compressed.frames.append(frame_result)
        total_compressed_size += compressed_size
        
        # Progress reporting - simplified
        if verbose and frame_idx % 30 == 0:
            progress = (frame_idx + 1) / len(ascii_frames) * 100
            print(f"Compressing: {frame_idx + 1}/{len(ascii_frames)} frames ({progress:.0f}%)")
        elif not verbose and frame_idx % 60 == 0:
            progress = (frame_idx + 1) / len(ascii_frames) * 100
            print(f"Compressing: {frame_idx + 1}/{len(ascii_frames)} frames ({progress:.0f}%)")
    
    # Calculate comprehensive statistics
    ascii_compression_ratio = ascii_text_size / total_compressed_size if total_compressed_size > 0 else 0
    overall_compression_ratio = original_video_size / total_compressed_size if original_video_size > 0 and total_compressed_size > 0 else 0
    ascii_expansion_factor = ascii_text_size / original_video_size if original_video_size > 0 else 0
    
    # Size conversions
    ascii_size_mb = ascii_text_size / 1024 / 1024
    compressed_size_mb = total_compressed_size / 1024 / 1024
    original_size_mb = original_video_size / 1024 / 1024
    space_saved_mb = original_size_mb - compressed_size_mb
    space_saved_percent = (space_saved_mb / original_size_mb * 100) if original_size_mb > 0 else 0
    
    compressed.stats = CompressionStats(
        total_frames=len(ascii_frames),
        original_video_size=original_video_size,
        ascii_text_size=ascii_text_size,
        total_compressed_size=total_compressed_size,
        ascii_compression_ratio=ascii_compression_ratio,
        overall_compression_ratio=overall_compression_ratio,
        ascii_expansion_factor=ascii_expansion_factor,
        ascii_size_mb=ascii_size_mb,
        compressed_size_mb=compressed_size_mb,
        original_size_mb=original_size_mb,
        space_saved_mb=space_saved_mb,
        space_saved_percent=space_saved_percent
    )
    
    # Print comprehensive results
    if verbose:
        print(f"\n=== MIDDLE-OUT COMPRESSION RESULTS ===")
        print(f"Total frames: {len(ascii_frames)}")
        if original_video_size > 0:
            print(f"Original video: {original_size_mb:.1f} MB")
            print(f"Raw ASCII text: {ascii_size_mb:.1f} MB ({ascii_expansion_factor:.1f}x expansion)")
        else:
            print(f"Raw ASCII text: {ascii_size_mb:.1f} MB")
        print(f"Compressed .txv: {compressed_size_mb:.1f} MB")
        print(f"")
        print(f"ASCII compression: {ascii_compression_ratio:.1f}:1 ({ascii_size_mb:.1f}MB → {compressed_size_mb:.1f}MB)")
        if original_video_size > 0:
            print(f"Overall compression: {overall_compression_ratio:.1f}:1 ({original_size_mb:.1f}MB → {compressed_size_mb:.1f}MB)")
            print(f"Space saved: {space_saved_mb:.1f} MB ({space_saved_percent:.1f}%)")
    else:
        if original_video_size > 0:
            print(f"ASCII compression: {ascii_compression_ratio:.1f}:1, Overall: {overall_compression_ratio:.1f}:1 ({compressed_size_mb:.1f} MB)")
        else:
            print(f"ASCII compression: {ascii_compression_ratio:.1f}:1 ({compressed_size_mb:.1f} MB)")
    
    # Performance assessment
    if ascii_compression_ratio >= 50.0:
        print("🎯 EXCELLENT: ASCII compression >50:1")
    elif ascii_compression_ratio >= 20.0:
        print("✅ VERY GOOD: ASCII compression >20:1")
    elif ascii_compression_ratio >= 10.0:
        print("⚠️  ACCEPTABLE: ASCII compression >10:1")
    else:
        print("❌ POOR: ASCII compression below 10:1")
    
    return compressed

def encode_frame_rle(ascii_frame: List[List[str]]) -> List[Tuple[str, int]]:
    """
    Encode ASCII frame using run-length encoding
    
    ASCII art has massive horizontal repetition.
    Faces have long runs of spaces, repeated texture patterns, etc.
    """
    
    rle_segments = []
    
    for row in ascii_frame:
        col = 0
        while col < len(row):
            char = row[col]
            run_length = 1
            
            # Count consecutive identical characters
            while (col + run_length < len(row) and 
                   row[col + run_length] == char):
                run_length += 1
            
            rle_segments.append((char, run_length))
            col += run_length
    
    return rle_segments

def compress_rle_segments(rle_segments: List[Tuple[str, int]]) -> bytes:
    """
    Compress RLE segments using LZMA
    
    Converts to JSON then applies LZMA compression.
    LZMA is extremely effective on the structured patterns.
    """
    
    # Convert to compact JSON representation
    segment_data = [[char, length] for char, length in rle_segments]
    
    # Serialize to JSON (minimal formatting)
    json_data = json.dumps(segment_data, separators=(',', ':')).encode('utf-8')
    
    # Apply LZMA compression (preset 6 = good compression/speed balance)
    compressed_data = lzma.compress(json_data, format=lzma.FORMAT_ALONE, preset=6)
    
    return compressed_data

def decompress_frame_rle(compressed_data: bytes, width: int, height: int) -> List[List[str]]:
    """
    Decompress RLE frame back to ASCII
    
    Args:
        compressed_data: LZMA compressed RLE segments
        width: Frame width in characters
        height: Frame height in characters
        
    Returns:
        2D ASCII character array
    """
    
    # Decompress LZMA
    json_data = lzma.decompress(compressed_data).decode('utf-8')
    rle_segments = json.loads(json_data)
    
    # Reconstruct frame from RLE segments
    frame = []
    current_row = []
    
    for char, run_length in rle_segments:
        for _ in range(run_length):
            current_row.append(char)
            
            # Check if row is complete
            if len(current_row) == width:
                frame.append(current_row)
                current_row = []
                
                # Check if frame is complete
                if len(frame) == height:
                    break
    
    return frame

def analyze_compression_performance(ascii_frames: List[List[List[str]]], 
                                  compressed_result: CompressedVideo) -> None:
    """Detailed compression performance analysis"""
    
    print(f"\n=== DETAILED MIDDLE-OUT ANALYSIS ===")
    
    stats = compressed_result.stats
    if not stats:
        print("No compression statistics available")
        return
    
    print(f"Input: {stats.total_frames} frames, {compressed_result.width}x{compressed_result.height}")
    
    if stats.original_video_size > 0:
        print(f"Original video: {stats.original_size_mb:.1f} MB")
        print(f"ASCII expansion: {stats.ascii_expansion_factor:.1f}x ({stats.original_size_mb:.1f}MB → {stats.ascii_size_mb:.1f}MB)")
    else:
        print(f"Raw ASCII text: {stats.ascii_size_mb:.1f} MB")
    
    print(f"Compressed output: {stats.compressed_size_mb:.1f} MB")
    print(f"ASCII compression ratio: {stats.ascii_compression_ratio:.1f}:1")
    
    if stats.original_video_size > 0:
        print(f"Overall compression ratio: {stats.overall_compression_ratio:.1f}:1")
        print(f"Space saved: {stats.space_saved_mb:.1f} MB ({stats.space_saved_percent:.1f}%)")
    
    # Frame-by-frame analysis
    ratios = [f.compression_ratio for f in compressed_result.frames]
    
    print(f"\nFrame compression statistics:")
    print(f"Best frame ratio: {max(ratios):.1f}:1")
    print(f"Worst frame ratio: {min(ratios):.1f}:1")
    print(f"Average frame ratio: {np.mean(ratios):.1f}:1")
    print(f"Ratio std deviation: {np.std(ratios):.1f}")
    
    # Performance assessment
    print(f"\n=== MIDDLE-OUT PERFORMANCE ASSESSMENT ===")
    if stats.ascii_compression_ratio >= 50.0:
        print("🎯 EXCELLENT: ASCII compression >50:1")
        print("   Middle-out algorithm highly effective")
    elif stats.ascii_compression_ratio >= 20.0:
        print("✅ VERY GOOD: ASCII compression >20:1")
        print("   Strong middle-out performance")
    elif stats.ascii_compression_ratio >= 10.0:
        print("⚠️  ACCEPTABLE: ASCII compression >10:1")
        print("   Moderate middle-out effectiveness")
    else:
        print("❌ POOR: ASCII compression below 10:1")
        print("   Content may not be suitable for middle-out compression")

# Legacy support
def compress_video(ascii_frames: List[List[List[str]]], fps: float = 30.0, 
                  i_frame_interval: int = 60) -> CompressedVideo:
    """Legacy function - redirects to RLE compression"""
    return compress_video_rle(ascii_frames, fps, verbose=False)

def calculate_compression_ratio(ascii_frames: List[List[List[str]]], 
                              compressed_result: CompressedVideo) -> Tuple[int, int, float]:
    """Legacy function - extract compression ratio from new format"""
    if not compressed_result.stats:
        return 0, 0, 0.0
    
    stats = compressed_result.stats
    return stats.ascii_text_size, stats.total_compressed_size, stats.ascii_compression_ratio