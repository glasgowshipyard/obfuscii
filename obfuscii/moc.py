"""
OBFUSCII Compression Engine

Middle-out compression algorithm:
- I-frames: Full ASCII grids every N seconds
- P-frames: Delta changes only (position + new character)
- LZMA compression on delta patterns
- Target: 10:1 compression ratio vs raw ASCII
"""

import lzma
import json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FrameData:
    """Single frame metadata"""
    frame_index: int
    frame_type: str  # 'I' or 'P'
    width: int
    height: int
    timestamp: float
    
@dataclass
class Delta:
    """Single character change between frames"""
    row: int
    col: int
    old_char: str
    new_char: str

class CompressedVideo:
    """Container for compressed ASCII video data"""
    
    def __init__(self, width: int, height: int, fps: float):
        self.width = width
        self.height = height
        self.fps = fps
        self.frames: List[FrameData] = []
        self.i_frames: Dict[int, List[List[str]]] = {}  # frame_index -> full ASCII grid
        self.p_frames: Dict[int, List[Delta]] = {}      # frame_index -> list of deltas
        self.metadata = {
            'version': '1.0',
            'created_by': 'OBFUSCII',
            'compression_algorithm': 'middle-out-delta-lzma'
        }

def compress_video(ascii_frames: List[List[List[str]]], fps: float = 30.0, 
                  i_frame_interval: int = 60) -> CompressedVideo:
    """
    Compress ASCII video using middle-out algorithm
    
    Args:
        ascii_frames: List of 2D ASCII character arrays
        fps: Video frame rate
        i_frame_interval: Frames between I-frames (every 2 seconds at 30fps)
        
    Returns:
        CompressedVideo object ready for .txv export
    """
    
    if not ascii_frames:
        raise ValueError("No frames to compress")
    
    # Get dimensions from first frame
    height = len(ascii_frames[0])
    width = len(ascii_frames[0][0])
    
    print(f"Compressing {len(ascii_frames)} frames ({width}x{height})")
    
    compressed = CompressedVideo(width, height, fps)
    total_deltas = 0
    
    # Process each frame
    for frame_idx, ascii_frame in enumerate(ascii_frames):
        timestamp = frame_idx / fps
        
        # Determine frame type
        is_i_frame = (frame_idx % i_frame_interval == 0) or frame_idx == 0
        frame_type = 'I' if is_i_frame else 'P'
        
        # Create frame metadata
        frame_data = FrameData(
            frame_index=frame_idx,
            frame_type=frame_type,
            width=width,
            height=height,
            timestamp=timestamp
        )
        compressed.frames.append(frame_data)
        
        if is_i_frame:
            # Store complete frame (I-frame)
            compressed.i_frames[frame_idx] = ascii_frame
            
        else:
            # Calculate delta from previous frame (P-frame)
            prev_frame = get_previous_reconstructed_frame(compressed, frame_idx)
            if prev_frame:
                deltas = calculate_deltas(prev_frame, ascii_frame)
                compressed.p_frames[frame_idx] = deltas
                total_deltas += len(deltas)
            else:
                # Fallback to I-frame if can't reconstruct previous
                compressed.i_frames[frame_idx] = ascii_frame
                compressed.frames[-1].frame_type = 'I'
    
    # Summary stats
    i_frames = len(compressed.i_frames)
    p_frames = len(compressed.p_frames)
    avg_deltas = total_deltas / p_frames if p_frames > 0 else 0
    
    print(f"I-frames: {i_frames}, P-frames: {p_frames}")
    print(f"Average deltas per P-frame: {avg_deltas:.1f}")
    
    return compressed

def calculate_deltas(prev_frame: List[List[str]], curr_frame: List[List[str]]) -> List[Delta]:
    """
    Calculate character differences between two frames
    
    Returns:
        List of Delta objects for changed characters only
    """
    deltas = []
    
    for row in range(len(curr_frame)):
        for col in range(len(curr_frame[row])):
            old_char = prev_frame[row][col]
            new_char = curr_frame[row][col]
            
            if old_char != new_char:
                deltas.append(Delta(row, col, old_char, new_char))
    
    return deltas

def get_previous_reconstructed_frame(compressed: CompressedVideo, 
                                   frame_idx: int) -> Optional[List[List[str]]]:
    """
    Reconstruct the previous frame by applying all deltas since last I-frame
    
    This is needed to calculate accurate deltas for P-frames
    """
    
    # Find the most recent I-frame
    last_i_frame_idx = None
    for i in range(frame_idx - 1, -1, -1):
        if i in compressed.i_frames:
            last_i_frame_idx = i
            break
    
    if last_i_frame_idx is None:
        return None
    
    # Start with the I-frame
    reconstructed = [row[:] for row in compressed.i_frames[last_i_frame_idx]]
    
    # Apply all P-frame deltas since the I-frame
    for p_frame_idx in range(last_i_frame_idx + 1, frame_idx):
        if p_frame_idx in compressed.p_frames:
            for delta in compressed.p_frames[p_frame_idx]:
                reconstructed[delta.row][delta.col] = delta.new_char
    
    return reconstructed

def compress_deltas_lzma(deltas: List[Delta]) -> bytes:
    """
    Compress delta list using LZMA
    
    Converts deltas to compact JSON then applies LZMA compression
    """
    
    # Convert deltas to compact representation
    delta_data = []
    for delta in deltas:
        delta_data.append([delta.row, delta.col, delta.old_char, delta.new_char])
    
    # Serialize to JSON
    json_data = json.dumps(delta_data, separators=(',', ':')).encode('utf-8')
    
    # Apply LZMA compression
    compressed_data = lzma.compress(json_data, preset=6)
    
    return compressed_data

def calculate_compression_ratio(ascii_frames: List[List[List[str]]], 
                              compressed: CompressedVideo) -> Tuple[int, int, float]:
    """
    Calculate compression statistics
    
    Returns:
        (raw_size_bytes, compressed_size_bytes, compression_ratio)
    """
    
    # Calculate raw ASCII video size
    if not ascii_frames:
        return 0, 0, 0.0
        
    frame_size = len(ascii_frames[0]) * len(ascii_frames[0][0])  # chars per frame
    raw_size = frame_size * len(ascii_frames)  # total characters
    
    # Calculate compressed size (rough estimate)
    compressed_size = 0
    
    # I-frame sizes
    for frame_idx, ascii_frame in compressed.i_frames.items():
        frame_chars = sum(len(row) for row in ascii_frame)
        compressed_size += frame_chars
    
    # P-frame sizes (deltas only)
    for frame_idx, deltas in compressed.p_frames.items():
        compressed_size += len(deltas) * 4  # rough estimate: 4 chars per delta
    
    # Add metadata overhead
    compressed_size += 1000  # rough metadata size
    
    compression_ratio = raw_size / compressed_size if compressed_size > 0 else 0
    
    return raw_size, compressed_size, compression_ratio

def test_compression(ascii_frames: List[List[List[str]]]) -> None:
    """
    Test compression algorithm and print statistics
    """
    
    print(f"\n=== COMPRESSION TEST ===")
    
    # Only test one interval to reduce output
    interval = 60  # 2 seconds at 30fps
    
    compressed = compress_video(ascii_frames, fps=30.0, i_frame_interval=interval)
    raw_size, comp_size, ratio = calculate_compression_ratio(ascii_frames, compressed)
    
    print(f"Raw size: {raw_size:,} characters")
    print(f"Compressed: {comp_size:,} characters")
    print(f"Compression ratio: {ratio:.1f}:1")
    
    if ratio >= 10.0:
        print("✅ TARGET ACHIEVED: 10:1+ compression ratio")
    elif ratio >= 5.0:
        print("⚠️  DECENT: 5:1+ compression ratio")
    elif ratio >= 2.0:
        print("📉 POOR: 2:1+ compression ratio")
    else:
        print("❌ FAILED: Less than 2:1 compression")

# Example usage for development
if __name__ == "__main__":
    # Create dummy ASCII frames for testing
    dummy_frames = []
    for i in range(60):  # 2 seconds at 30fps
        frame = []
        for row in range(40):
            frame_row = []
            for col in range(80):
                # Simulate subtle changes between frames
                char_index = (row + col + i) % 10
                chars = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
                frame_row.append(chars[char_index])
            frame.append(frame_row)
        dummy_frames.append(frame)
    
    test_compression(dummy_frames)