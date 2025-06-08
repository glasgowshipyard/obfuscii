#!/usr/bin/env python3
"""
OBFUSCII - ASCII video codec for temporal portraits and responsive branding
"""

import argparse
import sys
from pathlib import Path
from obfuscii.vid import process_video
from obfuscii.txv import read_txv_file, play_txv_file, txv_info_command, validate_txv_file

def main():
parser = argparse.ArgumentParser(
prog=‘obfuscii’,
description=‘Convert video to compressed ASCII animation (.txv format)’,
epilog=‘OBFUSCII: Temporal logos that exist as behavioral systems’
)

```
parser.add_argument('input', help='Input video file (mp4, mov, avi, etc.) or .txv file')
parser.add_argument('-o', '--output', help='Output .txv file (default: input name + .txv)')
parser.add_argument('--resolution', help='Output resolution (WIDTHxHEIGHT, e.g. 140x80)')

# Behavior flags - clean and logical
parser.add_argument('--play', action='store_true', help='Play existing .txv file without conversion')
parser.add_argument('--info', action='store_true', help='Show .txv file information')
parser.add_argument('--validate', action='store_true', help='Validate .txv file integrity')
parser.add_argument('--preview', action='store_true', help='Convert and play short clip (first 30 frames)')
parser.add_argument('--verbose', action='store_true', help='Show compression performance and detailed stats')

args = parser.parse_args()

# Handle .txv file operations
if args.input.endswith('.txv'):
    if args.info:
        txv_info_command(args.input)
        return
    elif args.validate:
        is_valid = validate_txv_file(args.input, verbose=True)
        sys.exit(0 if is_valid else 1)
    elif args.play or not any([args.info, args.validate]):
        # Default behavior for .txv files is to play them
        try:
            play_txv_file(args.input)
        except KeyboardInterrupt:
            print("\nPlayback stopped")
        except Exception as e:
            print(f"Error playing .txv file: {e}", file=sys.stderr)
            sys.exit(1)
        return

# Handle video conversion
if not Path(args.input).exists():
    print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
    sys.exit(1)

# Default output filename
if not args.output:
    input_base = Path(args.input).stem
    args.output = f"{input_base}.txv"

try:
    # Convert video and export to .txv
    process_video_with_export(
        input_file=args.input,
        output_file=args.output,
        resolution=args.resolution,
        preview_mode=args.preview,
        verbose=args.verbose
    )
    
except FileNotFoundError:
    print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

def process_video_with_export(input_file: str, output_file: str, resolution: str = None,
preview_mode: bool = False, verbose: bool = False) -> None:
"""
Process video to ASCII and export .txv file

```
Enhanced version of vid.process_video that actually exports the .txv file
"""
from obfuscii.vid import (load_video, parse_resolution, frame_to_ascii_with_hysteresis,
                          cleanup_ascii_patterns, play_ascii_video)
from obfuscii.moc import compress_video_rle, analyze_compression_performance
from obfuscii.txv import write_txv_file

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
    prev_ascii_frame = ascii_frame
    
    # Progress reporting
    if verbose and frame_index % 30 == 0:
        print(f"Processed frame {frame_index}/{max_frames}")
    elif not verbose and frame_index % 60 == 0:
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
    enable_spatial_coherence=False  # Disabled until fixed
)

# Compress video
print("\nCompressing ASCII video...")
if verbose:
    compressed_result = compress_video_rle(ascii_frames, fps=fps, verbose=True)
    analyze_compression_performance(ascii_frames, compressed_result)
else:
    compressed_result = compress_video_rle(ascii_frames, fps=fps, verbose=False)

# Export to .txv file
print(f"\nExporting to .txv format...")
original_filename = Path(input_file).name
write_txv_file(compressed_result, output_file, original_filename)

# Show final results
if compressed_result.stats:
    ratio = compressed_result.stats.overall_ratio
    size_kb = compressed_result.stats.compressed_size_kb
    print(f"\n✅ SUCCESS: {output_file}")
    print(f"   Compression: {ratio:.1f}:1 ratio")
    print(f"   File size: {size_kb:.1f} KB")
    
    if ratio >= 10.0:
        print("🎯 EXCELLENT: Target 10:1+ compression achieved!")
    elif ratio >= 7.0:
        print("🔥 VERY GOOD: 7:1+ compression achieved")
    elif ratio >= 5.0:
        print("✅ GOOD: 5:1+ compression achieved")
    else:
        print("⚠️  ACCEPTABLE: Compression below 5:1")

# Play result if not in preview mode
if not preview_mode:
    print(f"\nPlaying final result...")
    play_ascii_video(ascii_frames, fps)
else:
    print(f"\nPreview complete. Use 'obfuscii {output_file} --play' to play full .txv file")
```

if **name** == ‘**main**’:
main()