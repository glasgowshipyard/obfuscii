"""
OBFUSCII Video Export Module

Render ASCII video to platform-optimized MP4 files for social media.
Supports multiple aspect ratios and export profiles (Reels, TikTok, YouTube, etc.)

Key Functions:
    export_video_from_txv() - Main export pipeline
    render_ascii_frame_to_image() - Render single ASCII frame to PIL Image
    render_frames_to_directory() - Batch render all frames
    encode_frames_to_video() - FFmpeg encoding to MP4

Dependencies:
    - Pillow (PIL) for image rendering
    - ffmpeg (system binary) for video encoding

Usage:
    from obfuscii.export import export_video_from_txv

    export_video_from_txv(
        "video.txv",
        "video_reels.mp4",
        profile="reels",
        theme="light"
    )
"""

import subprocess
import tempfile
import shutil
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("\n❌ Error: Pillow is required for export functionality", file=sys.stderr)
    print("Install with: pip install Pillow\n", file=sys.stderr)
    sys.exit(1)


@dataclass
class ExportProfile:
    """Social media platform export profile"""
    name: str
    width: int
    height: int
    fps: int
    video_bitrate: str
    audio_bitrate: str
    description: str


# Platform export profiles (Reels first!)
EXPORT_PROFILES = {
    # TIER 1: Vertical Formats (9:16) - PRIMARY
    "reels": ExportProfile(
        name="Instagram/Facebook Reels (9:16)",
        width=1080,
        height=1920,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        description="Vertical format for Reels, TikTok, Shorts - PRIMARY"
    ),
    "tiktok": ExportProfile(
        name="TikTok (9:16)",
        width=1080,
        height=1920,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        description="Same as Reels - optimized for TikTok"
    ),
    "youtube_shorts": ExportProfile(
        name="YouTube Shorts (9:16)",
        width=1080,
        height=1920,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        description="Same as Reels - optimized for YouTube Shorts"
    ),

    # TIER 2: Traditional Formats
    "youtube": ExportProfile(
        name="YouTube (16:9)",
        width=1920,
        height=1080,
        fps=30,
        video_bitrate="8M",
        audio_bitrate="192k",
        description="Full HD 1080p horizontal for YouTube, Twitter"
    ),
    "youtube_4k": ExportProfile(
        name="YouTube 4K (16:9)",
        width=3840,
        height=2160,
        fps=30,
        video_bitrate="20M",
        audio_bitrate="256k",
        description="4K Ultra HD for premium YouTube content"
    ),
    "instagram_square": ExportProfile(
        name="Instagram Feed Square (1:1)",
        width=1080,
        height=1080,
        fps=30,
        video_bitrate="5M",
        audio_bitrate="192k",
        description="Square format for Instagram feed posts"
    ),
    "twitter": ExportProfile(
        name="Twitter/X (16:9)",
        width=1280,
        height=720,
        fps=30,
        video_bitrate="5M",
        audio_bitrate="192k",
        description="720p HD for Twitter/X timeline"
    ),
}


def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def require_ffmpeg():
    """Ensure ffmpeg is installed, exit with error if not"""
    if not check_ffmpeg_available():
        print("\n❌ Error: ffmpeg is required for video export", file=sys.stderr)
        print("\nInstall ffmpeg:", file=sys.stderr)
        print("  macOS:   brew install ffmpeg", file=sys.stderr)
        print("  Ubuntu:  sudo apt install ffmpeg", file=sys.stderr)
        print("  Windows: choco install ffmpeg", file=sys.stderr)
        print("\nOr download from: https://ffmpeg.org/download.html\n", file=sys.stderr)
        sys.exit(1)


def get_system_font(prefer_mono: bool = True) -> Optional[str]:
    """
    Get path to system monospace font

    Returns:
        Path to font file, or None if not found
    """
    # Common monospace fonts by platform
    font_paths = [
        # macOS
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Courier.dfont",
        "/Library/Fonts/SF-Mono-Regular.otf",
        # Ubuntu/Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path

    return None


def render_ascii_frame_to_image(
    ascii_frame: str,
    profile: ExportProfile,
    theme: str = "light",
    font_path: Optional[str] = None,
    font_size: Optional[int] = None
) -> Image.Image:
    """
    Render single ASCII frame to PIL Image

    Args:
        ascii_frame: ASCII frame as string (with newlines)
        profile: Export profile with dimensions
        theme: "light" or "dark"
        font_path: Path to monospace font (auto-detected if None)
        font_size: Font size in pixels (auto-calculated if None)

    Returns:
        PIL Image object
    """
    # Parse ASCII frame into lines
    lines = ascii_frame.strip().split('\n')
    ascii_height = len(lines)
    ascii_width = max(len(line) for line in lines) if lines else 0

    if ascii_width == 0 or ascii_height == 0:
        raise ValueError("Empty ASCII frame")

    # Theme colors
    if theme == "light":
        bg_color = (255, 255, 255)  # White background
        fg_color = (0, 0, 0)        # Black text
    else:  # dark
        bg_color = (0, 0, 0)        # Black background
        fg_color = (255, 255, 255)  # White text

    # Create image with background
    img = Image.new('RGB', (profile.width, profile.height), bg_color)
    draw = ImageDraw.Draw(img)

    # Get font
    if font_path is None:
        font_path = get_system_font()

    # Calculate optimal font size if not provided
    if font_size is None:
        # Calculate font size to fit ASCII grid in canvas
        # Monospace char width ≈ 0.6 * font_size
        # Monospace char height ≈ font_size
        font_size_by_height = profile.height // ascii_height
        font_size_by_width = int((profile.width / ascii_width) / 0.6)
        font_size = min(font_size_by_height, font_size_by_width)
        # Ensure minimum readable size
        font_size = max(8, font_size)

    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Fallback to default font
            font = ImageFont.load_default()
    except Exception as e:
        print(f"⚠️  Font loading failed: {e}, using default", file=sys.stderr)
        font = ImageFont.load_default()

    # Calculate character dimensions
    # Use a sample character to measure
    try:
        bbox = draw.textbbox((0, 0), 'M', font=font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
    except:
        # Fallback if textbbox not available
        char_width = font_size * 0.6
        char_height = font_size

    # Calculate grid dimensions and centering offset
    grid_width = ascii_width * char_width
    grid_height = ascii_height * char_height
    offset_x = (profile.width - grid_width) / 2
    offset_y = (profile.height - grid_height) / 2

    # Render each character
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            px = offset_x + x * char_width
            py = offset_y + y * char_height
            draw.text((px, py), char, fill=fg_color, font=font)

    return img


def render_frame_wrapper(args):
    """
    Wrapper function for multiprocessing

    Args:
        args: Tuple of (frame_index, ascii_frame, profile, theme, font_path, output_dir)
    """
    frame_index, ascii_frame, profile, theme, font_path, output_dir = args

    try:
        # Render frame to image
        img = render_ascii_frame_to_image(ascii_frame, profile, theme, font_path)

        # Save to PNG
        output_path = os.path.join(output_dir, f"frame_{frame_index:04d}.png")
        img.save(output_path, 'PNG')

        return (frame_index, output_path, True, None)

    except Exception as e:
        return (frame_index, None, False, str(e))


def render_frames_to_directory(
    ascii_frames: List[str],
    output_dir: str,
    profile: ExportProfile,
    theme: str = "light",
    font_path: Optional[str] = None,
    verbose: bool = False,
    workers: int = 4
) -> List[str]:
    """
    Render all ASCII frames to PNG files in directory

    Args:
        ascii_frames: List of ASCII frames as strings
        output_dir: Directory to save PNG files
        profile: Export profile
        theme: "light" or "dark"
        font_path: Path to monospace font
        verbose: Print progress
        workers: Number of parallel workers

    Returns:
        List of rendered PNG file paths (in order)
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    if verbose:
        print(f"🎨 Rendering {len(ascii_frames)} frames to {output_dir}...")
        print(f"   Using {workers} parallel workers")

    # Prepare arguments for parallel processing
    args_list = [
        (i, frame, profile, theme, font_path, output_dir)
        for i, frame in enumerate(ascii_frames)
    ]

    # Render frames in parallel
    rendered_paths = []
    failed_frames = []

    with Pool(workers) as pool:
        results = pool.map(render_frame_wrapper, args_list)

        for frame_index, output_path, success, error in results:
            if success:
                rendered_paths.append(output_path)
                if verbose and frame_index % 10 == 0:
                    progress = (frame_index + 1) / len(ascii_frames) * 100
                    print(f"   Progress: {progress:.0f}% ({frame_index + 1}/{len(ascii_frames)} frames)")
            else:
                failed_frames.append((frame_index, error))

    if failed_frames:
        print(f"\n⚠️  {len(failed_frames)} frames failed to render:", file=sys.stderr)
        for frame_index, error in failed_frames[:5]:  # Show first 5 errors
            print(f"   Frame {frame_index}: {error}", file=sys.stderr)

    if verbose:
        print(f"✅ Rendered {len(rendered_paths)}/{len(ascii_frames)} frames")

    return rendered_paths


def encode_frames_to_video(
    frame_paths: List[str],
    output_path: str,
    profile: ExportProfile,
    audio_path: Optional[str] = None,
    fps: float = 30.0,
    verbose: bool = False
) -> None:
    """
    Encode PNG sequence to MP4 using ffmpeg

    Args:
        frame_paths: List of PNG file paths (in order)
        output_path: Output MP4 file path
        profile: Export profile with bitrate settings
        audio_path: Optional audio file to include
        fps: Frames per second
        verbose: Print ffmpeg output

    Raises:
        RuntimeError: If ffmpeg encoding fails
    """
    require_ffmpeg()

    if not frame_paths:
        raise ValueError("No frames to encode")

    # Get directory containing frames
    frame_dir = Path(frame_paths[0]).parent

    # Build ffmpeg command
    # Input: PNG sequence
    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', str(frame_dir / 'frame_%04d.png'),
    ]

    # Add audio if provided
    if audio_path and os.path.exists(audio_path):
        cmd.extend(['-i', audio_path])

    # Video encoding settings
    cmd.extend([
        '-c:v', 'libx264',          # H.264 codec
        '-preset', 'medium',         # Encoding speed/quality balance
        '-crf', '18',                # Quality (18 = high quality, lower = better)
        '-pix_fmt', 'yuv420p',       # Pixel format (required for compatibility)
    ])

    # Set video bitrate
    cmd.extend(['-b:v', profile.video_bitrate])

    # Audio encoding settings (if audio present)
    if audio_path and os.path.exists(audio_path):
        cmd.extend([
            '-c:a', 'aac',           # AAC audio codec
            '-b:a', profile.audio_bitrate,  # Audio bitrate
        ])

    # Output settings
    cmd.extend([
        '-movflags', '+faststart',   # Enable streaming (moov atom at start)
        '-y',                        # Overwrite output file
        output_path
    ])

    if verbose:
        print(f"\n🎬 Encoding video with ffmpeg...")
        print(f"   Command: {' '.join(cmd)}\n")

    try:
        if verbose:
            result = subprocess.run(cmd, check=True)
        else:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True
            )

        if verbose:
            print(f"✅ Video encoded successfully: {output_path}")

    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg encoding failed: {e}"
        if e.stderr:
            error_msg += f"\n{e.stderr.decode('utf-8', errors='ignore')}"
        raise RuntimeError(error_msg)


def export_video_from_txv(
    txv_path: str,
    output_path: str,
    profile: str = "reels",
    theme: str = "light",
    custom_font: Optional[str] = None,
    verbose: bool = False
) -> None:
    """
    Export .txv file to platform-optimized MP4

    Args:
        txv_path: Path to .txv file
        output_path: Output MP4 file path
        profile: Export profile name (e.g., "reels", "youtube", "instagram_square")
        theme: "light" or "dark" rendering
        custom_font: Path to custom monospace font
        verbose: Print progress and stats

    Process:
        1. Load .txv file and decompress frames
        2. Check for companion audio file
        3. Render each ASCII frame to PNG in temp directory
        4. Use ffmpeg to encode PNG sequence + audio to MP4
        5. Clean up temp files
    """
    from obfuscii.txv import read_txv_file
    from obfuscii.moc import decompress_video_rle

    # Validate inputs
    if not os.path.exists(txv_path):
        raise FileNotFoundError(f"TXV file not found: {txv_path}")

    if profile not in EXPORT_PROFILES:
        raise ValueError(f"Unknown profile: {profile}. Available: {', '.join(EXPORT_PROFILES.keys())}")

    export_profile = EXPORT_PROFILES[profile]

    if verbose:
        print(f"\n🎬 OBFUSCII Export")
        print(f"   Input:   {txv_path}")
        print(f"   Output:  {output_path}")
        print(f"   Profile: {export_profile.name}")
        print(f"   Theme:   {theme}")
        print(f"   Resolution: {export_profile.width}x{export_profile.height}")

    # Load .txv file
    if verbose:
        print(f"\n📂 Loading .txv file...")

    compressed_video = read_txv_file(txv_path)

    if verbose:
        print(f"✅ Loaded {len(compressed_video.frames)} frames")
        print(f"   FPS: {compressed_video.fps}")
        print(f"   ASCII size: {compressed_video.width}x{compressed_video.height} characters")

    # Check for companion audio file
    audio_path = None
    if compressed_video.metadata.get('has_audio'):
        audio_filename = compressed_video.metadata.get('audio_file')
        if audio_filename:
            # Look for audio in same directory as .txv
            audio_path = str(Path(txv_path).parent / audio_filename)
            if os.path.exists(audio_path):
                if verbose:
                    print(f"✅ Found audio file: {audio_filename}")
            else:
                print(f"⚠️  Audio file not found: {audio_path}")
                audio_path = None

    # Decompress all frames
    if verbose:
        print(f"\n🗜️  Decompressing frames...")

    ascii_frames = []
    for i, frame_result in enumerate(compressed_video.frames):
        ascii_frame = decompress_video_rle(
            [frame_result],
            compressed_video.width,
            compressed_video.height
        )[0]
        ascii_frames.append(ascii_frame)

        if verbose and i % 30 == 0:
            progress = (i + 1) / len(compressed_video.frames) * 100
            print(f"   Progress: {progress:.0f}%")

    if verbose:
        print(f"✅ Decompressed {len(ascii_frames)} frames")

    # Create temporary directory for frames
    temp_dir = tempfile.mkdtemp(prefix="obfuscii_export_")

    try:
        # Render frames to PNG
        if verbose:
            print(f"\n🎨 Rendering frames to PNG...")

        workers = min(cpu_count(), 8)  # Use up to 8 cores
        frame_paths = render_frames_to_directory(
            ascii_frames,
            temp_dir,
            export_profile,
            theme=theme,
            font_path=custom_font,
            verbose=verbose,
            workers=workers
        )

        # Encode to video
        encode_frames_to_video(
            frame_paths,
            output_path,
            export_profile,
            audio_path=audio_path,
            fps=compressed_video.fps,
            verbose=verbose
        )

        # Get output file size
        output_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB

        if verbose:
            print(f"\n✅ Export complete!")
            print(f"   Output: {output_path}")
            print(f"   Size: {output_size:.1f} MB")
            print(f"   Duration: {len(ascii_frames) / compressed_video.fps:.1f}s")

    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            if verbose:
                print(f"🗑️  Cleaned up temp files")
