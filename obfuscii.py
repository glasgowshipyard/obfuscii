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
  python3 obfuscii.py video.mp4                    # Basic conversion (light theme)
  python3 obfuscii.py video.mp4 --dark             # Dark theme (inverted chars)
  python3 obfuscii.py video.mp4 --both             # Both light and dark versions
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
    
    parser.add_argument('input', nargs='?', help='Input video file (mp4, mov, avi, etc.) or .txv file')
    parser.add_argument('-o', '--output', help='Output .txv file (default: input name + .txv)')
    parser.add_argument('--resolution', help='Output resolution (WIDTHxHEIGHT, e.g. 140x80, default: 140x~80)')
    parser.add_argument('--config', help='Configuration preset (.json file, see Available configs below)')
    
    # Behavior flags
    parser.add_argument('--info', action='store_true', help='Show .txv file metadata (frames, size, compression ratio)')
    parser.add_argument('--validate', action='store_true', help='Validate .txv file integrity and structure')
    parser.add_argument('--preview', action='store_true', help='Convert and play first 30 frames only (fast preview)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed compression stats and processing info')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files without confirmation prompt')
    
    # Theme options
    theme_group = parser.add_mutually_exclusive_group()
    theme_group.add_argument('--light', action='store_true', help='Optimize for light backgrounds (default)')
    theme_group.add_argument('--dark', action='store_true', help='Optimize for dark backgrounds (inverted characters)')
    theme_group.add_argument('--both', action='store_true', help='Generate both light and dark versions')

    # Audio options (v2.0)
    audio_group = parser.add_argument_group('audio', 'Audio extraction and synchronization (v2.0)')
    audio_group.add_argument('--with-audio', action='store_true',
                             help='Extract and include audio track from video (creates companion audio file)')
    audio_group.add_argument('--audio-format', default='mp3', choices=['mp3', 'aac', 'ogg'],
                             help='Audio format for extraction (default: mp3)')
    audio_group.add_argument('--audio-bitrate', default='192k',
                             help='Audio bitrate (default: 192k, options: 128k, 192k, 256k, 320k)')
    audio_group.add_argument('--no-audio', action='store_true',
                             help='Strip audio from video (even if present in source)')

    # Export options (v2.0)
    export_group = parser.add_argument_group('export', 'Video export for social media (v2.0)')
    export_group.add_argument('--export', metavar='PROFILE',
                              choices=['reels', 'tiktok', 'youtube_shorts', 'youtube', 'youtube_4k',
                                      'instagram_square', 'twitter'],
                              help='Export .txv to platform-optimized MP4 (reels, youtube, instagram_square, etc.)')
    export_group.add_argument('--export-output', metavar='FILE',
                              help='Output MP4 file path (default: input_name_PROFILE.mp4)')
    export_group.add_argument('--export-theme', choices=['light', 'dark'], default='light',
                              help='Rendering theme for export (default: light)')
    export_group.add_argument('--export-font', metavar='PATH',
                              help='Path to custom monospace font (.ttf)')
    export_group.add_argument('--list-profiles', action='store_true',
                              help='List available export profiles and exit')

    # Live mode options (v2.0)
    parser.add_argument('--live', action='store_true',
                       help='Launch live webcam ASCII filter in browser')

    args = parser.parse_args()

    # Handle --live mode (v2.0)
    if args.live:
        launch_live_mode()
        return

    # Handle --list-profiles (v2.0)
    if args.list_profiles:
        list_export_profiles()
        return

    # Check for input file (required for all other operations)
    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Handle .txv file operations (includes --export)
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
        if args.both:
            # Will generate both _light.txv and _dark.txv
            args.output = input_base  # Base name without extension
        else:
            args.output = f"{input_base}.txv"
    
    # Check for existing output file
    if Path(args.output).exists() and not args.force:
        response = input(f"'{args.output}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Aborted")
            sys.exit(0)
    
    try:
        if args.both:
            convert_both_themes(args)
        else:
            convert_video_to_txv(args)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_txv_file(args):
    """Handle .txv file operations (info, validate, play, export)"""
    from obfuscii.txv import txv_info_command, validate_txv_file, play_txv_file

    # Handle export (v2.0)
    if args.export:
        export_txv_to_video(args)
        return

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

def invert_ascii_chars(chars):
    """Invert ASCII character set for dark backgrounds"""
    return list(reversed(chars))

def convert_both_themes(args):
    """Convert video to both light and dark versions"""
    # Generate light version
    light_output = f"{args.output}_light.txv"
    dark_output = f"{args.output}_dark.txv"
    
    print(f"Converting both themes: {light_output} and {dark_output}")
    
    # Create light version (default)
    light_args = args.__dict__.copy()
    light_args = type('Args', (), light_args)()
    light_args.output = light_output
    light_args.light = True
    light_args.dark = False
    light_args.both = False
    
    print("\n🌞 Creating light theme version...")
    convert_video_to_txv(light_args)
    
    # Create dark version (inverted)
    dark_args = args.__dict__.copy()
    dark_args = type('Args', (), dark_args)()
    dark_args.output = dark_output
    dark_args.light = False
    dark_args.dark = True
    dark_args.both = False
    
    print("\n🌙 Creating dark theme version...")
    convert_video_to_txv(dark_args)
    
    print(f"\n✅ Both versions created:")
    print(f"   Light: {light_output}")
    print(f"   Dark:  {dark_output}")

def convert_video_to_txv(args):
    """Convert video file to .txv format"""
    from obfuscii.vid import process_video_to_compressed, parse_resolution, play_ascii_video
    from obfuscii.txv import write_txv_file
    from obfuscii.config import OBFUSCIIConfig
    from obfuscii.audio import extract_audio_from_video, has_audio_stream  # NEW: v2.0

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

    # Apply theme modifications
    if args.dark:
        config.conversion.ascii_chars = invert_ascii_chars(config.conversion.ascii_chars)
        theme_name = "dark theme"
    else:
        theme_name = "light theme"  # Default

    if args.verbose:
        print(f"Converting: {args.input} → {args.output}")
        print(f"Using configuration: {config_file} ({config.description})")
        print(f"Theme: {theme_name}")

    # NEW: Extract audio if requested (v2.0)
    audio_track = None
    if args.with_audio and not args.no_audio:
        if has_audio_stream(args.input):
            try:
                print(f"\n🎵 Extracting audio from video...")
                audio_output = f"{Path(args.output).stem}_audio.{args.audio_format}"
                audio_track = extract_audio_from_video(
                    args.input,
                    audio_output,
                    format=args.audio_format,
                    bitrate=args.audio_bitrate,
                    verbose=args.verbose
                )
                print(f"✅ Audio extracted: {audio_output} ({audio_track.duration_seconds:.1f}s)")
            except Exception as e:
                print(f"⚠️  Audio extraction failed: {e}")
                print("Continuing without audio...")
                audio_track = None
        else:
            print(f"⚠️  No audio stream detected in {args.input}")
            print("Continuing without audio...")
    
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
    
    # Export to .txv (with audio metadata if audio was extracted)
    print(f"\nExporting to .txv format...")
    original_filename = Path(args.input).name
    write_txv_file(compressed_result, args.output, original_filename, audio_track=audio_track)
    
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
        # Don't prompt for playback if we're in --both mode (too many files)
        if hasattr(args, 'both') and args.both:
            print(f"Conversion complete. Use 'python obfuscii.py filename.txv' to play either version.")
            return
            
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


def list_export_profiles():
    """List available export profiles (v2.0)"""
    from obfuscii.export import EXPORT_PROFILES

    print("\n=== AVAILABLE EXPORT PROFILES ===\n")

    # Group by tier
    print("TIER 1: Vertical Formats (9:16)")
    print("-" * 60)
    for key in ['reels', 'tiktok', 'youtube_shorts']:
        profile = EXPORT_PROFILES[key]
        print(f"  {key:20s} {profile.width}x{profile.height} @ {profile.fps}fps")
        print(f"  {' '*20} {profile.description}")
        print()

    print("\nTIER 2: Traditional Formats")
    print("-" * 60)
    for key in ['youtube', 'youtube_4k', 'instagram_square', 'twitter']:
        profile = EXPORT_PROFILES[key]
        print(f"  {key:20s} {profile.width}x{profile.height} @ {profile.fps}fps")
        print(f"  {' '*20} {profile.description}")
        print()

    print("\nUsage:")
    print("  python3 obfuscii.py video.txv --export reels")
    print("  python3 obfuscii.py video.txv --export youtube --export-theme dark")
    print()


def export_txv_to_video(args):
    """Export .txv file to social media video (v2.0)"""
    from obfuscii.export import export_video_from_txv

    if not args.export:
        print("Error: --export requires a profile name", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if not args.export_output:
        input_stem = Path(args.input).stem
        args.export_output = f"{input_stem}_{args.export}.mp4"

    # Check for overwrite
    if Path(args.export_output).exists() and not args.force:
        response = input(f"'{args.export_output}' exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Aborted")
            return

    try:
        export_video_from_txv(
            txv_path=args.input,
            output_path=args.export_output,
            profile=args.export,
            theme=args.export_theme,
            custom_font=args.export_font,
            verbose=args.verbose
        )

        # Show success message
        file_size = Path(args.export_output).stat().st_size / (1024 * 1024)
        print(f"\n✅ Export complete: {args.export_output} ({file_size:.1f} MB)")

    except Exception as e:
        print(f"❌ Export failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def launch_live_mode():
    """Launch live webcam ASCII filter in browser (v2.0)"""
    import webbrowser
    import http.server
    import socketserver
    import threading
    import time

    # Determine path to live.html
    script_dir = Path(__file__).parent
    live_html = script_dir / "live.html"

    if not live_html.exists():
        print("Error: live.html not found", file=sys.stderr)
        print(f"Expected at: {live_html}", file=sys.stderr)
        sys.exit(1)

    # Start local web server
    PORT = 8000

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(script_dir), **kwargs)

        def log_message(self, format, *args):
            # Suppress server logs
            pass

    def start_server():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give server time to start
    time.sleep(0.5)

    # Open browser
    url = f"http://localhost:{PORT}/live.html"
    print(f"\n🎥 OBFUSCII Live Mode")
    print(f"   Server running at {url}")
    print(f"   Opening browser...")
    print(f"   Press Ctrl+C to stop\n")

    webbrowser.open(url)

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping live mode...")
        sys.exit(0)


if __name__ == '__main__':
    main()