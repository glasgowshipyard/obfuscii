#!/usr/bin/env python3
"""
OBFUSCII - ASCII video codec for temporal portraits and responsive branding
"""

import argparse
import sys
from obfuscii.video import process_video

def main():
    parser = argparse.ArgumentParser(
        prog='obfuscii',
        description='Convert video to compressed ASCII animation (.txv format)',
        epilog='OBFUSCII: Temporal logos that exist as behavioral systems'
    )
    
    parser.add_argument('input', help='Input video file (mp4, mov, avi, etc.)')
    parser.add_argument('-o', '--output', help='Output .txv file (default: input name + .txv)')
    parser.add_argument('--resolution', help='Output resolution (WIDTHxHEIGHT, e.g. 140x80)')
    parser.add_argument('--preview', action='store_true', help='Preview ASCII output in terminal')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Default output filename
    if not args.output:
        input_base = args.input.rsplit('.', 1)[0]
        args.output = f"{input_base}.txv"
    
    try:
        print(f"OBFUSCII: Converting {args.input} to {args.output}")
        if args.verbose:
            print(f"Resolution: {args.resolution or 'auto'}")
            print(f"Preview: {'enabled' if args.preview else 'disabled'}")
        
        process_video(args.input, args.output, args.resolution, args.preview, args.verbose)
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()