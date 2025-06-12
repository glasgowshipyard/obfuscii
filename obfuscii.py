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
        epilog='OBFUSCII: Temporal logos that exist as behavioral systems'
    )
    
    parser.add_argument('input', help='Input video file (mp4, mov, avi, etc.) or .txv file')
    parser.add_argument('-o', '--output', help='Output .txv file (default: input name + .txv)')
    parser.add_argument('--resolution', help='Output resolution (WIDTHxHEIGHT, e.g. 140x80)')
    parser.add_argument('--config', help='Configuration file (.json) - Available presets: light_balanced_high_max.json (default), config_high_quality.json, config_high_compression.json')
    parser.add_argument('--background', choices=['dark', 'light', 'both'], help='Target background mode for ASCII output')
    
    # Behavior flags
    parser.add_argument('--info', action='store_true', help='Show .txv file information')
    parser.add_argument('--validate', action='store_true', help='Validate .txv file integrity')
    parser.add_argument('--preview', action='store_true', help='Convert and play short clip (first 30 frames)')
    parser.add_argument('--verbose', action='store_true', help='Show compression performance and detailed stats')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files without asking')
    
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
    
    # Determine background rendering mode
    bg_choice = args.background
    if not bg_choice:
        resp = input("Render for dark, light, or both backgrounds? [d/l/b] (default: both): ").strip().lower()
        if resp in ("d", "dark"):
            bg_choice = "dark"
        elif resp in ("l", "light"):
            bg_choice = "light"
        else:
            bg_choice = "both"

    backgrounds = [bg_choice] if bg_choice in ("dark", "light") else ["dark", "light"]

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
    
    for bg in backgrounds:
        cfg = config.copy()
        if bg == "light":
            cfg.conversion.ascii_chars = cfg.conversion.light_ascii_chars
        else:
            cfg.conversion.ascii_chars = cfg.conversion.dark_ascii_chars

        # Process video
        compressed_result = process_video_to_compressed(
            input_file=args.input,
            target_width=target_width,
            target_height=target_height,
            max_frames=max_frames,
            verbose=args.verbose,
            config=cfg
        )

        # Export to .txv
        print(f"\nExporting to .txv format...")
        original_filename = Path(args.input).name
        output_file = args.output
        if len(backgrounds) > 1:
            stem = Path(args.output).stem
            suffix = Path(args.output).suffix
            output_file = f"{stem}_{bg}{suffix}"

        write_txv_file(compressed_result, output_file, original_filename)

        # Show results
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

        # Play result
        if args.preview:
            print(f"\nPreview complete. Use 'python obfuscii.py {output_file}' to play full .txv file")
        else:
            print(f"\nPlaying result for {bg} background...")
            from obfuscii.txv import read_txv_file, decompress_txv_frame

            try:
                compressed_video = read_txv_file(output_file)
                ascii_frames = []

                print("Decompressing for playback...")
                for frame_idx in range(len(compressed_video.frames)):
                    ascii_frame = decompress_txv_frame(compressed_video, frame_idx)
                    ascii_frames.append(ascii_frame)

                    if frame_idx % 30 == 0:
                        print(f"Decompressed frame {frame_idx}/{len(compressed_video.frames)}")

                play_ascii_video(ascii_frames, compressed_video.fps)
            except KeyboardInterrupt:
                print("\nPlayback cancelled")

if __name__ == '__main__':
    main()