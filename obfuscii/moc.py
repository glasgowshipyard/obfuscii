"""
OBFUSCII Compression Engine - Final Implementation

RLE + LZMA compression targeting 10:1 ratio.

KEY INSIGHT: ASCII art has massive spatial redundancy. Exploit horizontal
run-length patterns rather than fighting temporal character boundaries.

This approach works WITH ASCII's discrete nature instead of against it.
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
                      verbose: bool = False) -> CompressedVideo:
    """
    Primary compression function using RLE + LZMA
    
    Targets 10:1 compression ratio by exploiting spatial redundancy
    in ASCII art rather than temporal prediction.
    
    Args:
        ascii_frames: List of 2D ASCII character arrays
        fps: Video frame rate
        verbose: Print detailed compression analysis
        
    Returns:
        CompressedVideo object with all frames compressed
    """
    
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
    
    if overall_ratio >= 10.0:
        print("✅ TARGET ACHIEVED: 10:1+ compression ratio")
    elif overall_ratio >= 5.0:
        print("⚠️  GOOD PROGRESS: 5:1+ compression ratio")
    else:
        print("❌ NEEDS WORK: Below 5:1 compression")
    
    return compressed

def encode_frame_rle(ascii_frame: List[List[str]]) -> List[Tuple[str, int]]:
    """
    Encode ASCII frame using run-length encoding
    
    The key insight: ASCII art has massive horizontal repetition.
    Faces have long runs of spaces, repeated texture patterns, etc.
    
    Returns:
        List of (character, run_length) tuples
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
    compressed_data = lzma.compress(json_data, preset=6)
    
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

def compress_video_hybrid(ascii_frames: List[List[List[str]]], fps: float = 30.0,
                         i_frame_interval: int = 90, verbose: bool = False) -> CompressedVideo:
    """
    Hybrid compression: RLE I-frames + Delta P-frames
    
    Use this for motion-heavy content where pure RLE might not be optimal.
    Most portrait/logo content should use pure RLE.
    
    Args:
        ascii_frames: List of 2D ASCII character arrays
        fps: Video frame rate  
        i_frame_interval: Frames between I-frames (every 3 seconds at 30fps)
        verbose: Print detailed analysis
    """
    
    if not ascii_frames:
        raise ValueError("No frames to compress")
    
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    frame_size = height * width
    
    if verbose:
        print(f"Hybrid compression: {len(ascii_frames)} frames ({width}x{height})")
        print(f"I-frame interval: every {i_frame_interval} frames ({i_frame_interval/fps:.1f}s)")
    
    compressed = CompressedVideo(width, height, fps)
    total_raw_size = 0
    total_compressed_size = 0
    i_frame_count = 0
    p_frame_count = 0
    
    previous_frame = None
    
    for frame_idx, ascii_frame in enumerate(ascii_frames):
        timestamp = frame_idx / fps
        raw_size = frame_size
        
        # Determine frame type
        is_i_frame = (frame_idx % i_frame_interval == 0)
        
        if is_i_frame or previous_frame is None:
            # I-frame: Use RLE compression
            rle_segments = encode_frame_rle(ascii_frame)
            compressed_data = compress_rle_segments(rle_segments)
            frame_type = 'I'
            i_frame_count += 1
            
        else:
            # P-frame: Use delta compression
            deltas = calculate_frame_deltas(previous_frame, ascii_frame)
            compressed_data = compress_delta_data(deltas)
            frame_type = 'P'
            p_frame_count += 1
        
        compressed_size = len(compressed_data)
        compression_ratio = raw_size / compressed_size if compressed_size > 0 else 0
        
        # Store frame result
        frame_result = FrameResult(
            frame_index=frame_idx,
            frame_type=frame_type,
            timestamp=timestamp,
            raw_size=raw_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compressed_data=compressed_data
        )
        
        compressed.frames.append(frame_result)
        
        total_raw_size += raw_size
        total_compressed_size += compressed_size
        previous_frame = ascii_frame
        
        if verbose and frame_idx % 30 == 0:
            print(f"Compressed frame {frame_idx}/{len(ascii_frames)} ({frame_type}-frame, ratio: {compression_ratio:.1f}:1)")
    
    # Calculate statistics
    overall_ratio = total_raw_size / total_compressed_size if total_compressed_size > 0 else 0
    
    i_frames = [f for f in compressed.frames if f.frame_type == 'I']
    p_frames = [f for f in compressed.frames if f.frame_type == 'P']
    
    avg_i_ratio = np.mean([f.compression_ratio for f in i_frames]) if i_frames else 0
    avg_p_ratio = np.mean([f.compression_ratio for f in p_frames]) if p_frames else 0
    
    compressed.stats = CompressionStats(
        total_frames=len(ascii_frames),
        total_raw_size=total_raw_size,
        total_compressed_size=total_compressed_size,
        overall_ratio=overall_ratio,
        raw_size_kb=total_raw_size / 1024,
        compressed_size_kb=total_compressed_size / 1024,
        i_frame_count=i_frame_count,
        p_frame_count=p_frame_count,
        avg_i_frame_ratio=avg_i_ratio,
        avg_p_frame_ratio=avg_p_ratio
    )
    
    if verbose:
        print(f"\n=== HYBRID COMPRESSION RESULTS ===")
        print(f"I-frames: {i_frame_count} (avg ratio: {avg_i_ratio:.1f}:1)")
        print(f"P-frames: {p_frame_count} (avg ratio: {avg_p_ratio:.1f}:1)")
        print(f"Overall ratio: {overall_ratio:.1f}:1")
    
    return compressed

def calculate_frame_deltas(prev_frame: List[List[str]], 
                          curr_frame: List[List[str]]) -> List[Tuple[int, int, str]]:
    """
    Calculate character differences between frames
    
    Returns:
        List of (row, col, new_char) tuples for changed positions
    """
    
    deltas = []
    
    for row in range(len(curr_frame)):
        for col in range(len(curr_frame[row])):
            if prev_frame[row][col] != curr_frame[row][col]:
                deltas.append((row, col, curr_frame[row][col]))
    
    return deltas

def compress_delta_data(deltas: List[Tuple[int, int, str]]) -> bytes:
    """
    Compress delta list using LZMA
    """
    
    # Convert to JSON
    delta_data = list(deltas)  # Already in the right format
    json_data = json.dumps(delta_data, separators=(',', ':')).encode('utf-8')
    
    # Apply LZMA compression
    compressed = lzma.compress(json_data, preset=6)
    
    return compressed

def analyze_compression_performance(ascii_frames: List[List[List[str]]], 
                                  compressed_result: CompressedVideo) -> None:
    """
    Detailed compression performance analysis
    """
    
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
    
    # RLE effectiveness analysis
    if all(f.frame_type == 'I' for f in compressed_result.frames):
        print(f"\nRLE Analysis:")
        print(f"Algorithm: Pure RLE + LZMA compression")
        print(f"All frames I-frames (spatial redundancy exploitation)")
        
        # Analyze spatial redundancy
        sample_frame = compressed_result.frames[0]
        print(f"Sample frame: {sample_frame.raw_size} chars → {sample_frame.compressed_size} bytes")
        print(f"Sample ratio: {sample_frame.compression_ratio:.1f}:1")
    
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
    
    # Recommendations
    print(f"\n=== RECOMMENDATIONS ===")
    if stats.overall_ratio < 5.0:
        print("• Try hybrid compression (RLE I-frames + Delta P-frames)")
        print("• Check for excessive motion or noise in source video")
        print("• Consider temporal smoothing preprocessing")
    elif stats.overall_ratio < 10.0:
        print("• Current compression is good but can be improved")
        print("• Consider increasing I-frame interval for motion content")
        print("• Verify source video has sufficient spatial repetition")
    else:
        print("• Compression performance is excellent")
        print("• Ready for .txv file format export")
        print("• Suitable for web distribution")

def test_compression_approaches(ascii_frames: List[List[List[str]]]) -> None:
    """
    Compare different compression approaches on the same content
    """
    
    print("=== COMPRESSION APPROACH COMPARISON ===")
    
    if len(ascii_frames) == 0:
        print("No frames to test")
        return
    
    # Test 1: Pure RLE compression
    print("\n--- Pure RLE Compression ---")
    rle_result = compress_video_rle(ascii_frames, verbose=False)
    rle_ratio = rle_result.stats.overall_ratio
    
    # Test 2: Hybrid compression (if enough frames)
    if len(ascii_frames) >= 90:
        print("\n--- Hybrid Compression (RLE + Delta) ---")
        hybrid_result = compress_video_hybrid(ascii_frames, i_frame_interval=60, verbose=False)
        hybrid_ratio = hybrid_result.stats.overall_ratio
    else:
        print("\n--- Hybrid Compression: Skipped (too few frames) ---")
        hybrid_ratio = 0
    
    # Comparison
    print(f"\n=== COMPARISON RESULTS ===")
    print(f"Pure RLE:     {rle_ratio:.1f}:1")
    if hybrid_ratio > 0:
        print(f"Hybrid:       {hybrid_ratio:.1f}:1")
        
        if rle_ratio > hybrid_ratio:
            print(f"✅ WINNER: Pure RLE ({rle_ratio - hybrid_ratio:.1f}x better)")
            print("   Recommendation: Use RLE compression for this content")
        elif hybrid_ratio > rle_ratio:
            print(f"✅ WINNER: Hybrid ({hybrid_ratio - rle_ratio:.1f}x better)")
            print("   Recommendation: Use hybrid compression for this content")
        else:
            print("🤝 TIE: Both approaches perform similarly")
    else:
        print("   Only RLE tested (insufficient frames for hybrid)")
    
    return rle_result

def estimate_file_sizes(compressed_result: CompressedVideo) -> None:
    """
    Estimate final .txv file sizes and web suitability
    """
    
    stats = compressed_result.stats
    if not stats:
        return
    
    print(f"\n=== FILE SIZE ESTIMATES ===")
    
    # Current compressed size
    base_size_kb = stats.compressed_size_kb
    
    # Add metadata overhead
    metadata_kb = 2.0  # Estimated metadata size
    total_size_kb = base_size_kb + metadata_kb
    
    print(f"Compressed frames: {base_size_kb:.1f} KB")
    print(f"Metadata overhead: {metadata_kb:.1f} KB")
    print(f"Total .txv size: {total_size_kb:.1f} KB")
    
    # Web suitability assessment
    print(f"\n=== WEB SUITABILITY ===")
    if total_size_kb < 50:
        print("🚀 EXCELLENT: <50KB - Perfect for web logos")
        print("   Loads instantly on any connection")
    elif total_size_kb < 200:
        print("✅ VERY GOOD: <200KB - Great for web use")
        print("   Fast loading on most connections")
    elif total_size_kb < 500:
        print("⚠️  ACCEPTABLE: <500KB - Usable for web")
        print("   May need loading indicator")
    else:
        print("❌ TOO LARGE: >500KB - Consider optimization")
        print("   Not suitable for responsive logos")
    
    # Usage recommendations
    duration_seconds = len(compressed_result.frames) / compressed_result.fps
    print(f"\nVideo duration: {duration_seconds:.1f} seconds")
    print(f"Size per second: {total_size_kb / duration_seconds:.1f} KB/s")
    
    if total_size_kb < 100 and duration_seconds <= 5:
        print("\n🎯 PERFECT for temporal portraits/logos")
    elif total_size_kb < 500:
        print("\n✅ SUITABLE for ASCII cinema/art")
    else:
        print("\n⚠️  CONSIDER shortening duration or increasing compression")

# Legacy support - keep the old function name for compatibility
def compress_video(ascii_frames: List[List[List[str]]], fps: float = 30.0, 
                  i_frame_interval: int = 60) -> CompressedVideo:
    """
    Legacy function - redirects to RLE compression
    """
    return compress_video_rle(ascii_frames, fps, verbose=False)

def calculate_compression_ratio(ascii_frames: List[List[List[str]]], 
                              compressed_result: CompressedVideo) -> Tuple[int, int, float]:
    """
    Legacy function - extract compression ratio from new format
    """
    if not compressed_result.stats:
        return 0, 0, 0.0
    
    stats = compressed_result.stats
    return stats.total_raw_size, stats.total_compressed_size, stats.overall_ratio

# Test function
def test_compression(ascii_frames: List[List[List[str]]]) -> None:
    """
    Legacy test function - runs full compression analysis
    """
    
    if not ascii_frames:
        print("No frames to test")
        return
    
    print("\n=== COMPRESSION TEST ===")
    
    # Run compression
    result = test_compression_approaches(ascii_frames)
    
    # Detailed analysis
    analyze_compression_performance(ascii_frames, result)
    
    # File size estimates
    estimate_file_sizes(result)

# Development/debugging functions
if __name__ == "__main__":
    # Create test data that mimics real ASCII art
    print("Creating test ASCII frames...")
    
    test_frames = []
    for frame_idx in range(60):  # 2 seconds at 30fps
        frame = []
        for row in range(40):
            frame_row = []
            for col in range(80):
                # Create realistic ASCII art pattern
                if col < 10 or col > 70:
                    # Background spaces
                    char = ' '
                elif 30 <= col <= 50 and 15 <= row <= 25:
                    # Face area with some variation
                    base_intensity = 4 + (row - 20) // 3
                    noise = (frame_idx + row + col) % 3 - 1  # Subtle animation
                    intensity = max(2, min(7, base_intensity + noise))
                    chars = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
                    char = chars[intensity]
                else:
                    # Structured background
                    if row % 4 == 0:
                        char = '-'
                    else:
                        char = ' '
                
                frame_row.append(char)
            frame.append(frame_row)
        test_frames.append(frame)
    
    # Run comprehensive test
    test_compression(test_frames)