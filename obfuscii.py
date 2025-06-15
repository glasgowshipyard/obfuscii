#!/usr/bin/env python3
"""
OBFUSCII - ASCII video codec for temporal portraits and responsive branding
"""

import argparse
import sys
from pathlib import Path
import json

def main():
    parser = argparse.ArgumentParser(
        prog='obfuscii',
        description='Convert video to compressed ASCII animation (.txv format)',
        epilog='''Examples:
  python3 obfuscii.py video.mp4                    # Basic conversion
  python3 obfuscii.py video.mp4 --preview          # Quick 30-frame preview
  python3 obfuscii.py video.mp4 --resolution 80x40 # Smaller output
  python3 obfuscii.py video.mp4 --config config_high_quality.json
  python3 obfuscii.py output.txv --info            # Show file details
  python3 obfuscii.py output.txv                   # Play .txv file

Available configs:
  light_balanced_high_max.json (default) - Optimal balance
  config_high_quality.json               - Maximum visual fidelity  
  config_high_compression.json           - Smallest file size
  config_default.json                    - Basic settings

OBFUSCII: Temporal logos that exist as behavioral systems''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input', help='Input video file (mp4, mov, avi, etc.) or .txv file')
    parser.add_argument('-o', '--output', help='Output .txv file (default: input name + .txv)')
    parser.add_argument('--resolution', help='Output resolution (WIDTHxHEIGHT, e.g. 140x80, default: 140x~80)')
    parser.add_argument('--config', help='Configuration preset (.json file, see Available configs below)')
    
    # Behavior flags
    parser.add_argument('--info', action='store_true', help='Show .txv file metadata (frames, size, compression ratio)')
    parser.add_argument('--validate', action='store_true', help='Validate .txv file integrity and structure')
    parser.add_argument('--preview', action='store_true', help='Convert and play first 30 frames only (fast preview)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed compression stats and processing info')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files without confirmation prompt')
    
    args = parser.parse_args()
    
    # Handle .txv file operations
    if args.input.endswith('.txv'):
        handle_txv_file(args)
        return
    
    # Handle video conversion
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Default output filename
    if not args.output:
        input_base = Path(args.input).stem
        args.output = f"{input_base}.txv"
    
    # Check for existing output file
    if Path(args.output).exists() and not args.force:
        response = input(f"'{args.output}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Aborted")
            sys.exit(0)
    
    try:
        convert_video_to_txv(args)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_txv_file(args):
    """Handle .txv file operations (info, validate, play)"""
    from obfuscii.txv import txv_info_command, validate_txv_file, play_txv_file
    
    if args.info:
        txv_info_command(args.input)
    elif args.validate:
        is_valid = validate_txv_file(args.input, verbose=True)
        sys.exit(0 if is_valid else 1)
    else:
        # Default behavior for .txv files is to play them
        try:
            play_txv_file(args.input)
        except KeyboardInterrupt:
            print("\nPlayback stopped")
        except Exception as e:
            print(f"Error playing .txv file: {e}", file=sys.stderr)
            sys.exit(1)

def convert_video_to_txv(args):
    """Convert video file to .txv format"""
    from obfuscii.vid import process_video_to_compressed, parse_resolution, play_ascii_video
    from obfuscii.txv import write_txv_file
    from obfuscii.config import OBFUSCIIConfig
    
    # Load configuration
    config_file = args.config or 'light_balanced_high_max.json'
    if not Path(config_file).exists():
        print(f"Error: Configuration file '{config_file}' not found", file=sys.stderr)
        print("Available configurations:", file=sys.stderr)
        print("  light_balanced_high_max.json (default, optimal)", file=sys.stderr)
        print("  config_high_quality.json", file=sys.stderr)
        print("  config_high_compression.json", file=sys.stderr)
        print("  config_default.json", file=sys.stderr)
        sys.exit(1)
    
    config = OBFUSCIIConfig.from_json(config_file)
    
    if args.verbose:
        print(f"Converting: {args.input} → {args.output}")
        print(f"Using configuration: {config_file} ({config.description})")
    
    # Parse resolution (override config default if specified)
    target_width, target_height = parse_resolution(args.resolution)
    if not args.resolution:
        target_width = config.conversion.default_width
    
    if args.verbose and args.resolution:
        print(f"Target resolution: {target_width}x{target_height}")
    
    # Determine frame limit for preview
    max_frames = 30 if args.preview else None
    
    if args.preview:
        print(f"Preview mode: processing first 30 frames")
    
    # Process video
    compressed_result = process_video_to_compressed(
        input_file=args.input,
        target_width=target_width,
        target_height=target_height,
        max_frames=max_frames,
        verbose=args.verbose,
        config=config
    )
    
    # Export to .txv
    print(f"\nExporting to .txv format...")
    original_filename = Path(args.input).name
    write_txv_file(compressed_result, args.output, original_filename)
    
    # Show results
    if compressed_result.stats:
        ratio = compressed_result.stats.overall_ratio
        size_kb = compressed_result.stats.compressed_size_kb
        print(f"\n✅ SUCCESS: {args.output}")
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
    
    # Play result
    if args.preview:
        print(f"\nPreview complete. Use 'python obfuscii.py {args.output}' to play full .txv file")
    else:
        # Ask user if they want to play
        response = input(f"\nPlay result now? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("Playing result...")
            # Get decompressed frames for playback
            from obfuscii.txv import read_txv_file, decompress_txv_frame
            
            # Load and decompress for playback
            compressed_video = read_txv_file(args.output)
            ascii_frames = []
            
            print("Decompressing for playback...")
            for frame_idx in range(len(compressed_video.frames)):
                ascii_frame = decompress_txv_frame(compressed_video, frame_idx)
                ascii_frames.append(ascii_frame)
                
                if frame_idx % 30 == 0:
                    print(f"Decompressed frame {frame_idx}/{len(compressed_video.frames)}")
            
            play_ascii_video(ascii_frames, compressed_video.fps)
        else:
            print(f"Conversion complete. Use 'python obfuscii.py {args.output}' to play later.")

if __name__ == '__main__':
    main()