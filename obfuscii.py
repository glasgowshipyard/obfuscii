#!/usr/bin/env python3
"""
OBFUSCII - ASCII video codec for temporal portraits and responsive branding
"""

import argparse
import sys
from obfuscii.vid import process_video

def main():
    parser = argparse.ArgumentParser(
        prog='obfuscii',
        description='Convert video to compressed ASCII animation (.txv format)',
        epilog='OBFUSCII: Temporal logos that exist as behavioral systems'
    )
    
    parser.add_argument('input', help='Input video file (mp4, mov, avi, etc.)')
    parser.add_argument('-o', '--output', help='Output .txv file (default: input name + .txv)')
    parser.add_argument('--resolution', help='Output resolution (WIDTHxHEIGHT, e.g. 140x80)')
    
    # Behavior flags - clean and logical
    parser.add_argument('--raw', action='store_true', help='Play existing ASCII video without conversion')
    parser.add_argument('--preview', action='store_true', help='Convert and play short clip (first 30 frames)')
    parser.add_argument('--verbose', action='store_true', help='Show compression performance and detailed stats')
    
    args = parser.parse_args()
    
    # Default output filename
    if not args.output:
        input_base = args.input.rsplit('.', 1)[0]
        args.output = f"{input_base}.txv"
    
    try:
        if args.raw:
            # TODO: Implement raw playback from existing .txv file
            print("Raw playback not yet implemented")
            sys.exit(1)
        else:
            # Convert video and play result
            process_video(
                input_file=args.input,
                output_file=args.output,
                resolution=args.resolution,
                preview_mode=args.preview,  # True = short clip, False = full video
                verbose=args.verbose
            )
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()