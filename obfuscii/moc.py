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
    total_raw_size: int
    total_compressed_size: int
    overall_ratio: float
    raw_size_kb: float
    compressed_size_kb: float
    i_frame_count: int = 0
    p_frame_count: int = 0
    avg_i_frame_ratio: float = 0.0
    avg_p_frame_ratio: float = 0.0

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
    
    def __init__(self, width: int, height: int, fps: float):
        self.width = width
        self.height = height
        self.fps = fps
        self.frames: List[FrameResult] = []
        self.stats: Optional[CompressionStats] = None
        self.metadata = {
            'version': '3.0',
            'algorithm': 'spatial-rle-lzma',
            'created_by': 'OBFUSCII'
        }

def compress_video_rle(ascii_frames: List[List[List[str]]], fps: float = 30.0, 
                      verbose: bool = False, config: Optional['CompressionConfig'] = None) -> CompressedVideo:
    """
    Primary compression function using RLE + LZMA
    
    Targets 10:1 compression ratio by exploiting spatial redundancy
    in ASCII art rather than temporal prediction.
    
    Args:
        ascii_frames: List of ASCII frame arrays
        fps: Frames per second for output video
        verbose: Print progress information
        config: Compression configuration (uses defaults if None)
    """
    if config is None:
        from .config import CompressionConfig
        config = CompressionConfig()  # Use defaults
    
    if not ascii_frames:
        raise ValueError("No frames to compress")
    
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    frame_size = height * width
    
    if verbose:
        print(f"RLE compression: {len(ascii_frames)} frames ({width}x{height})")
        print("Algorithm: Run-Length Encoding + LZMA")
    
    compressed = CompressedVideo(width, height, fps)
    total_raw_size = 0
    total_compressed_size = 0
    
    # Process each frame with RLE compression
    for frame_idx, ascii_frame in enumerate(ascii_frames):
        timestamp = frame_idx / fps
        raw_size = frame_size
        
        # Apply run-length encoding
        rle_segments = encode_frame_rle(ascii_frame)
        
        # Compress with LZMA using configured settings
        compressed_data = compress_rle_segments(rle_segments, config)
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
        
        total_raw_size += raw_size
        total_compressed_size += compressed_size
        
        # Progress reporting
        if verbose and frame_idx % 30 == 0:
            print(f"Compressed frame {frame_idx}/{len(ascii_frames)} (ratio: {compression_ratio:.1f}:1)")
    
    # Calculate overall statistics
    overall_ratio = total_raw_size / total_compressed_size if total_compressed_size > 0 else 0
    
    compressed.stats = CompressionStats(
        total_frames=len(ascii_frames),
        total_raw_size=total_raw_size,
        total_compressed_size=total_compressed_size,
        overall_ratio=overall_ratio,
        raw_size_kb=total_raw_size / 1024,
        compressed_size_kb=total_compressed_size / 1024,
        i_frame_count=len(ascii_frames),  # All frames are I-frames
        p_frame_count=0,
        avg_i_frame_ratio=overall_ratio
    )
    
    # Print results
    if verbose:
        print(f"\n=== COMPRESSION RESULTS ===")
        print(f"Total frames: {len(ascii_frames)}")
        print(f"Raw size: {total_raw_size:,} chars ({total_raw_size/1024:.1f} KB)")
        print(f"Compressed: {total_compressed_size:,} bytes ({total_compressed_size/1024:.1f} KB)")
        print(f"Overall ratio: {overall_ratio:.1f}:1")
    else:
        print(f"Compression: {overall_ratio:.1f}:1 ratio ({total_compressed_size/1024:.1f} KB)")
    
    # Use configured thresholds for performance assessment
    if overall_ratio >= config.target_ratio:
        print(f"✅ TARGET ACHIEVED: {config.target_ratio}:1+ compression ratio")
    elif overall_ratio >= config.good_ratio:
        print(f"🔥 VERY GOOD: {config.good_ratio}:1+ compression ratio")
    elif overall_ratio >= config.acceptable_ratio:
        print(f"⚠️  ACCEPTABLE: {config.acceptable_ratio}:1+ compression ratio")
    else:
        print(f"❌ NEEDS WORK: Below {config.acceptable_ratio}:1 compression")
    
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

def compress_rle_segments(rle_segments: List[Tuple[str, int]], config: 'CompressionConfig') -> bytes:
    """
    Compress RLE segments using LZMA
    
    Converts to JSON then applies LZMA compression.
    LZMA is extremely effective on the structured patterns.
    
    Args:
        rle_segments: Run-length encoded segments
        config: Compression configuration
    """
    
    # Convert to compact JSON representation
    segment_data = [[char, length] for char, length in rle_segments]
    
    # Serialize to JSON (minimal formatting)
    json_data = json.dumps(segment_data, separators=(',', ':')).encode('utf-8')
    
    # Apply LZMA compression with configured settings
    lzma_format = lzma.FORMAT_ALONE if config.lzma_format == "alone" else lzma.FORMAT_XZ
    compressed_data = lzma.compress(json_data, format=lzma_format, preset=config.lzma_preset)
    
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
    
    print(f"\n=== DETAILED COMPRESSION ANALYSIS ===")
    
    stats = compressed_result.stats
    if not stats:
        print("No compression statistics available")
        return
    
    print(f"Input: {stats.total_frames} frames, {compressed_result.width}x{compressed_result.height}")
    print(f"Raw size: {stats.raw_size_kb:.1f} KB")
    print(f"Compressed size: {stats.compressed_size_kb:.1f} KB")
    print(f"Space saved: {stats.raw_size_kb - stats.compressed_size_kb:.1f} KB ({((stats.raw_size_kb - stats.compressed_size_kb) / stats.raw_size_kb * 100):.1f}%)")
    print(f"Overall compression ratio: {stats.overall_ratio:.1f}:1")
    
    # Frame-by-frame analysis
    ratios = [f.compression_ratio for f in compressed_result.frames]
    
    print(f"\nFrame compression statistics:")
    print(f"Best frame ratio: {max(ratios):.1f}:1")
    print(f"Worst frame ratio: {min(ratios):.1f}:1")
    print(f"Average frame ratio: {np.mean(ratios):.1f}:1")
    print(f"Ratio std deviation: {np.std(ratios):.1f}")
    
    # Performance assessment
    print(f"\n=== PERFORMANCE ASSESSMENT ===")
    if stats.overall_ratio >= 10.0:
        print("🎯 EXCELLENT: Target 10:1 ratio achieved")
        print("   Ready for production use")
    elif stats.overall_ratio >= 8.0:
        print("✅ VERY GOOD: Close to 10:1 target")
        print("   Minor optimizations possible")
    elif stats.overall_ratio >= 5.0:
        print("⚠️  ACCEPTABLE: 5:1+ compression")
        print("   Consider content optimization")
    else:
        print("❌ POOR: Below 5:1 compression")
        print("   Content may not be suitable for ASCII video")

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
    return stats.total_raw_size, stats.total_compressed_size, stats.overall_ratio