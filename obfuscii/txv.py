"""
OBFUSCII .txv File Format Implementation

Binary format optimized for compressed ASCII video:
- Magic header for format identification
- JSON metadata for video properties  
- LZMA-compressed frame data
- Frame index for seeking

Format structure:
[8 bytes] Magic: b'OBFUSCII'
[4 bytes] Version: uint32 (little endian)
[4 bytes] Metadata length: uint32 (little endian)  
[N bytes] Metadata: JSON (UTF-8)
[4 bytes] Frame count: uint32 (little endian)
[Frame data] Compressed frames with headers
"""

import struct
import json
import lzma
from typing import List, Dict, Any, BinaryIO, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from .moc import CompressedVideo, FrameResult

# File format constants
TXV_MAGIC = b'OBFUSCII'
TXV_VERSION = 1
FRAME_HEADER_SIZE = 24  # frame_index(4) + frame_type(1) + padding(3) + timestamp(8) + raw_size(4) + compressed_size(4)

@dataclass
class TxvMetadata:
    """Metadata structure for .txv files"""
    version: str = "1.0"
    width: int = 0
    height: int = 0
    fps: float = 30.0
    total_frames: int = 0
    duration_seconds: float = 0.0
    compression_algorithm: str = "rle-lzma"
    created_by: str = "OBFUSCII"
    creation_timestamp: Optional[str] = None
    original_file: Optional[str] = None
    compression_ratio: Optional[float] = None

def write_txv_file(compressed_video: CompressedVideo, output_path: str, 
                   original_filename: Optional[str] = None) -> None:
    """
    Write CompressedVideo to .txv file format
    
    Args:
        compressed_video: Compressed video data from moc.py
        output_path: Output .txv file path
        original_filename: Original video filename for metadata
    """
    
    from datetime import datetime
    
    # Create metadata
    duration = len(compressed_video.frames) / compressed_video.fps
    compression_ratio = compressed_video.stats.overall_ratio if compressed_video.stats else None
    
    metadata = TxvMetadata(
        width=compressed_video.width,
        height=compressed_video.height,
        fps=compressed_video.fps,
        total_frames=len(compressed_video.frames),
        duration_seconds=duration,
        creation_timestamp=datetime.now().isoformat(),
        original_file=original_filename,
        compression_ratio=compression_ratio
    )
    
    # Serialize metadata to JSON
    metadata_dict = asdict(metadata)
    metadata_dict.update(compressed_video.metadata)  # Include any additional metadata
    metadata_json = json.dumps(metadata_dict, separators=(',', ':')).encode('utf-8')
    
    print(f"Writing .txv file: {output_path}")
    print(f"Frames: {len(compressed_video.frames)}, Size: {len(metadata_json)} bytes metadata")
    
    with open(output_path, 'wb') as f:
        # Write file header
        f.write(TXV_MAGIC)  # Magic: 8 bytes
        f.write(struct.pack('<I', TXV_VERSION))  # Version: 4 bytes  
        f.write(struct.pack('<I', len(metadata_json)))  # Metadata length: 4 bytes
        f.write(metadata_json)  # Metadata: variable length
        f.write(struct.pack('<I', len(compressed_video.frames)))  # Frame count: 4 bytes
        
        # Write frame data
        for frame_result in compressed_video.frames:
            write_frame_header(f, frame_result)
            f.write(frame_result.compressed_data)
    
    # Calculate final file size
    file_size = Path(output_path).stat().st_size
    print(f"✅ .txv file created: {file_size:,} bytes ({file_size/1024:.1f} KB)")

def write_frame_header(file: BinaryIO, frame: FrameResult) -> None:
    """Write frame header before compressed frame data"""
    
    # Pack frame header (24 bytes total)
    header = struct.pack('<I', frame.frame_index)  # 4 bytes: frame index
    header += frame.frame_type.encode('ascii')  # 1 byte: frame type ('I' or 'P') 
    header += b'\x00' * 3  # 3 bytes: padding for alignment
    header += struct.pack('<d', frame.timestamp)  # 8 bytes: timestamp (double)
    header += struct.pack('<I', frame.raw_size)  # 4 bytes: raw frame size
    header += struct.pack('<I', frame.compressed_size)  # 4 bytes: compressed frame size
    
    file.write(header)

def read_txv_file(input_path: str) -> CompressedVideo:
    """
    Read .txv file and return CompressedVideo object
    
    Args:
        input_path: Path to .txv file
        
    Returns:
        CompressedVideo object ready for playback
    """
    
    print(f"Reading .txv file: {input_path}")
    
    with open(input_path, 'rb') as f:
        # Read and validate header
        magic = f.read(8)
        if magic != TXV_MAGIC:
            raise ValueError(f"Invalid .txv file: bad magic {magic}")
        
        version = struct.unpack('<I', f.read(4))[0]
        if version != TXV_VERSION:
            raise ValueError(f"Unsupported .txv version: {version}")
        
        # Read metadata
        metadata_length = struct.unpack('<I', f.read(4))[0]
        metadata_json = f.read(metadata_length).decode('utf-8')
        metadata = json.loads(metadata_json)
        
        # Read frame count
        frame_count = struct.unpack('<I', f.read(4))[0]
        
        print(f"Loading: {frame_count} frames, {metadata['width']}x{metadata['height']}")
        
        # Create CompressedVideo object
        compressed_video = CompressedVideo(
            width=metadata['width'],
            height=metadata['height'],
            fps=metadata['fps']
        )
        compressed_video.metadata = metadata
        
        # Read frames
        for frame_idx in range(frame_count):
            frame_result = read_frame_data(f)
            compressed_video.frames.append(frame_result)
    
    print(f"✅ .txv file loaded: {len(compressed_video.frames)} frames")
    return compressed_video

def read_frame_data(file: BinaryIO) -> FrameResult:
    """Read frame header and compressed data"""
    
    # Read frame header (24 bytes)
    header = file.read(FRAME_HEADER_SIZE)
    if len(header) != FRAME_HEADER_SIZE:
        raise ValueError("Unexpected end of file reading frame header")
    
    # Unpack header
    frame_index = struct.unpack('<I', header[0:4])[0]
    frame_type = header[4:5].decode('ascii')
    # Skip 3 bytes padding  
    timestamp = struct.unpack('<d', header[8:16])[0]
    raw_size = struct.unpack('<I', header[16:20])[0]
    compressed_size = struct.unpack('<I', header[20:24])[0]
    
    # Read compressed frame data
    compressed_data = file.read(compressed_size)
    if len(compressed_data) != compressed_size:
        raise ValueError(f"Frame {frame_index}: expected {compressed_size} bytes, got {len(compressed_data)}")
    
    # Create FrameResult
    compression_ratio = raw_size / compressed_size if compressed_size > 0 else 0
    
    return FrameResult(
        frame_index=frame_index,
        frame_type=frame_type,
        timestamp=timestamp,
        raw_size=raw_size,
        compressed_size=compressed_size,
        compression_ratio=compression_ratio,
        compressed_data=compressed_data
    )

def get_txv_info(input_path: str) -> Dict[str, Any]:
    """
    Get .txv file information without loading frame data
    
    Args:
        input_path: Path to .txv file
        
    Returns:
        Dictionary with file metadata and statistics
    """
    
    with open(input_path, 'rb') as f:
        # Read header
        magic = f.read(8)
        if magic != TXV_MAGIC:
            raise ValueError(f"Invalid .txv file: {magic}")
        
        version = struct.unpack('<I', f.read(4))[0]
        metadata_length = struct.unpack('<I', f.read(4))[0]
        metadata_json = f.read(metadata_length).decode('utf-8')
        metadata = json.loads(metadata_json)
        frame_count = struct.unpack('<I', f.read(4))[0]
    
    # Calculate file statistics
    file_size = Path(input_path).stat().st_size
    header_size = 8 + 4 + 4 + metadata_length + 4  # Magic + version + metadata_len + metadata + frame_count
    frame_data_size = file_size - header_size
    
    # Add calculated fields
    info = metadata.copy()
    info.update({
        'file_size_bytes': file_size,
        'file_size_kb': file_size / 1024,
        'header_size_bytes': header_size,
        'frame_data_size_bytes': frame_data_size,
        'frame_count_actual': frame_count,
        'avg_frame_size_bytes': frame_data_size / frame_count if frame_count > 0 else 0
    })
    
    return info

def validate_txv_file(input_path: str, verbose: bool = True) -> bool:
    """
    Validate .txv file integrity
    
    Args:
        input_path: Path to .txv file
        verbose: Print validation details
        
    Returns:
        True if file is valid, False otherwise
    """
    
    try:
        if verbose:
            print(f"Validating .txv file: {input_path}")
        
        # Load file info
        info = get_txv_info(input_path)
        
        # Basic validation
        required_fields = ['width', 'height', 'fps', 'total_frames']
        for field in required_fields:
            if field not in info:
                if verbose:
                    print(f"❌ Missing required field: {field}")
                return False
        
        # Check frame count consistency
        if info['frame_count_actual'] != info['total_frames']:
            if verbose:
                print(f"❌ Frame count mismatch: header={info['total_frames']}, actual={info['frame_count_actual']}")
            return False
        
        # Try to read first few frames to validate structure
        with open(input_path, 'rb') as f:
            # Skip to frame data
            f.seek(8 + 4 + 4)  # Magic + version + metadata_length
            metadata_length = struct.unpack('<I', f.read(4))[0]
            f.seek(8 + 4 + 4 + metadata_length + 4)  # Skip to frame data
            
            # Validate first 3 frames (or all if fewer)
            frames_to_check = min(3, info['frame_count_actual'])
            
            for i in range(frames_to_check):
                try:
                    frame = read_frame_data(f)
                    if frame.frame_index != i:
                        if verbose:
                            print(f"❌ Frame index mismatch: expected {i}, got {frame.frame_index}")
                        return False
                except Exception as e:
                    if verbose:
                        print(f"❌ Error reading frame {i}: {e}")
                    return False
        
        if verbose:
            duration = info['total_frames'] / info['fps']
            compression_ratio = info.get('compression_ratio', 'unknown')
            print(f"✅ Valid .txv file:")
            print(f"   Resolution: {info['width']}x{info['height']}")
            print(f"   Duration: {duration:.1f}s ({info['total_frames']} frames at {info['fps']:.1f} FPS)")
            print(f"   File size: {info['file_size_kb']:.1f} KB")
            print(f"   Compression: {compression_ratio}:1" if compression_ratio != 'unknown' else "   Compression: unknown")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"❌ Validation failed: {e}")
        return False

def decompress_txv_frame(compressed_video: CompressedVideo, frame_index: int) -> List[List[str]]:
    """
    Decompress specific frame from .txv data back to ASCII
    
    Args:
        compressed_video: Loaded .txv data
        frame_index: Frame to decompress (0-based)
        
    Returns:
        2D ASCII character array
    """
    
    if frame_index >= len(compressed_video.frames):
        raise IndexError(f"Frame {frame_index} not found (total: {len(compressed_video.frames)})")
    
    frame = compressed_video.frames[frame_index]
    
    # Use moc.py decompression function
    from .moc import decompress_frame_rle
    
    ascii_frame = decompress_frame_rle(
        frame.compressed_data,
        compressed_video.width,
        compressed_video.height
    )
    
    return ascii_frame

def play_txv_file(input_path: str) -> None:
    """
    Load and play .txv file using video player
    
    Args:
        input_path: Path to .txv file
    """
    
    # Load .txv file
    compressed_video = read_txv_file(input_path)
    
    # Decompress all frames
    print("Decompressing frames for playback...")
    ascii_frames = []
    
    for frame_idx in range(len(compressed_video.frames)):
        ascii_frame = decompress_txv_frame(compressed_video, frame_idx)
        ascii_frames.append(ascii_frame)
        
        if frame_idx % 30 == 0:  # Progress every ~1 second
            print(f"Decompressed frame {frame_idx}/{len(compressed_video.frames)}")
    
    # Play using vid.py player
    from .vid import play_ascii_video
    play_ascii_video(ascii_frames, compressed_video.fps)

# CLI utilities for development and testing
def txv_info_command(input_path: str) -> None:
    """Command line utility to show .txv file information"""
    
    try:
        info = get_txv_info(input_path)
        
        print(f"\n=== .TXV FILE INFORMATION ===")
        print(f"File: {input_path}")
        print(f"Size: {info['file_size_kb']:.1f} KB ({info['file_size_bytes']:,} bytes)")
        print(f"Resolution: {info['width']}x{info['height']}")
        print(f"Frames: {info['total_frames']}")
        print(f"FPS: {info['fps']:.1f}")
        print(f"Duration: {info['total_frames'] / info['fps']:.1f} seconds")
        
        if 'compression_ratio' in info and info['compression_ratio']:
            print(f"Compression: {info['compression_ratio']:.1f}:1")
        
        if 'creation_timestamp' in info:
            print(f"Created: {info['creation_timestamp']}")
        
        if 'original_file' in info:
            print(f"Source: {info['original_file']}")
        
        print(f"\nFrame data: {info['frame_data_size_bytes']:,} bytes")
        print(f"Avg frame: {info['avg_frame_size_bytes']:.1f} bytes")
        
    except Exception as e:
        print(f"Error reading .txv file: {e}")

def txv_validate_command(input_path: str) -> None:
    """Command line utility to validate .txv file"""
    
    is_valid = validate_txv_file(input_path, verbose=True)
    exit(0 if is_valid else 1)

def txv_play_command(input_path: str) -> None:
    """Command line utility to play .txv file"""
    
    try:
        play_txv_file(input_path)
    except KeyboardInterrupt:
        print("\nPlayback stopped")
    except Exception as e:
        print(f"Error playing .txv file: {e}")

# Development testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python txv.py <command> <file.txv>")
        print("Commands: info, validate, play")
        sys.exit(1)
    
    command = sys.argv[1]
    file_path = sys.argv[2]
    
    if command == "info":
        txv_info_command(file_path)
    elif command == "validate":
        txv_validate_command(file_path)
    elif command == "play":
        txv_play_command(file_path)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)