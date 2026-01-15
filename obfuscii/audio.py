"""
OBFUSCII Audio Processing Module

Handles audio extraction from video files and synchronization with ASCII video.
Uses ffmpeg/ffprobe for robust audio handling via subprocess.

Key Functions:
    extract_audio_from_video() - Extract audio track using ffmpeg
    get_audio_info() - Get audio metadata using ffprobe
    validate_audio_sync() - Check audio/video duration match
    trim_audio_to_duration() - Trim audio to exact duration

Dependencies:
    - ffmpeg (system binary, install with: brew install ffmpeg)
    - ffprobe (included with ffmpeg)

Usage:
    from obfuscii.audio import extract_audio_from_video

    audio_track = extract_audio_from_video(
        "input.mp4",
        "output.mp3",
        format="mp3",
        bitrate="192k"
    )

    print(f"Extracted: {audio_track.duration_seconds}s audio")
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class AudioTrack:
    """Audio track metadata and file reference"""
    file_path: str
    format: str  # "mp3", "aac", "ogg"
    codec: str
    sample_rate: int
    duration_seconds: float
    bitrate: int
    channels: int


def check_ffmpeg_installed() -> bool:
    """
    Check if ffmpeg is installed and accessible

    Returns:
        True if ffmpeg is available, False otherwise
    """
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


def check_ffprobe_installed() -> bool:
    """
    Check if ffprobe is installed and accessible

    Returns:
        True if ffprobe is available, False otherwise
    """
    try:
        subprocess.run(
            ['ffprobe', '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def require_ffmpeg():
    """
    Ensure ffmpeg is installed, exit with error message if not
    """
    if not check_ffmpeg_installed():
        print("\n❌ Error: ffmpeg is required for audio processing", file=sys.stderr)
        print("\nInstall ffmpeg:", file=sys.stderr)
        print("  macOS:   brew install ffmpeg", file=sys.stderr)
        print("  Ubuntu:  sudo apt install ffmpeg", file=sys.stderr)
        print("  Windows: choco install ffmpeg", file=sys.stderr)
        print("\nOr download from: https://ffmpeg.org/download.html\n", file=sys.stderr)
        sys.exit(1)


def extract_audio_from_video(
    video_path: str,
    output_path: Optional[str] = None,
    format: str = "mp3",
    bitrate: str = "192k",
    verbose: bool = False
) -> AudioTrack:
    """
    Extract audio track from video file using ffmpeg

    Args:
        video_path: Path to source video file
        output_path: Output audio file path (auto-generated if None)
        format: Audio format ("mp3", "aac", "ogg")
        bitrate: Audio bitrate (e.g., "128k", "192k", "256k", "320k")
        verbose: Print ffmpeg output

    Returns:
        AudioTrack object with metadata

    Raises:
        FileNotFoundError: If video file doesn't exist
        RuntimeError: If ffmpeg extraction fails
    """
    require_ffmpeg()

    # Validate input file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Generate output path if not provided
    if output_path is None:
        video_stem = Path(video_path).stem
        output_path = f"{video_stem}_audio.{format}"

    # Determine audio codec based on format
    codec_map = {
        "mp3": "libmp3lame",
        "aac": "aac",
        "ogg": "libvorbis"
    }

    if format not in codec_map:
        raise ValueError(f"Unsupported audio format: {format}. Use: mp3, aac, or ogg")

    audio_codec = codec_map[format]

    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_path,        # Input video
        '-vn',                   # No video
        '-acodec', audio_codec,  # Audio codec
        '-ab', bitrate,          # Audio bitrate
        '-y',                    # Overwrite output file
        output_path              # Output audio file
    ]

    try:
        if verbose:
            print(f"\n🎵 Extracting audio from {video_path}...")
            print(f"   Command: {' '.join(cmd)}\n")
            result = subprocess.run(cmd, check=True)
        else:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

        # Get audio metadata
        audio_info = get_audio_info(output_path)

        # Create AudioTrack object
        audio_track = AudioTrack(
            file_path=output_path,
            format=format,
            codec=audio_info.get('codec', audio_codec),
            sample_rate=audio_info.get('sample_rate', 44100),
            duration_seconds=audio_info.get('duration', 0.0),
            bitrate=audio_info.get('bitrate', int(bitrate.replace('k', '')) * 1000),
            channels=audio_info.get('channels', 2)
        )

        if verbose:
            print(f"✅ Audio extracted successfully:")
            print(f"   Output: {output_path}")
            print(f"   Duration: {audio_track.duration_seconds:.2f}s")
            print(f"   Format: {audio_track.format} ({audio_track.codec})")
            print(f"   Sample rate: {audio_track.sample_rate} Hz")
            print(f"   Bitrate: {audio_track.bitrate} bps")
            print(f"   Channels: {audio_track.channels}\n")

        return audio_track

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg audio extraction failed: {e}")


def get_audio_info(audio_path: str) -> Dict[str, Any]:
    """
    Get audio file metadata using ffprobe

    Args:
        audio_path: Path to audio file

    Returns:
        Dictionary with audio metadata:
            - duration: Duration in seconds (float)
            - codec: Audio codec name (str)
            - sample_rate: Sample rate in Hz (int)
            - bitrate: Bitrate in bps (int)
            - channels: Number of audio channels (int)

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If ffprobe fails
    """
    if not check_ffprobe_installed():
        # Fallback: return default values if ffprobe not available
        return {
            'duration': 0.0,
            'codec': 'unknown',
            'sample_rate': 44100,
            'bitrate': 192000,
            'channels': 2
        }

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Build ffprobe command to get JSON output
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        audio_path
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )

        data = json.loads(result.stdout)

        # Extract audio stream info
        audio_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break

        if audio_stream is None:
            raise RuntimeError(f"No audio stream found in {audio_path}")

        # Extract metadata
        format_info = data.get('format', {})

        return {
            'duration': float(format_info.get('duration', 0.0)),
            'codec': audio_stream.get('codec_name', 'unknown'),
            'sample_rate': int(audio_stream.get('sample_rate', 44100)),
            'bitrate': int(format_info.get('bit_rate', 192000)),
            'channels': int(audio_stream.get('channels', 2))
        }

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFprobe failed: {e}")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise RuntimeError(f"Failed to parse audio metadata: {e}")


def validate_audio_sync(
    audio_path: str,
    video_duration: float,
    tolerance_ms: float = 100.0
) -> Tuple[bool, float]:
    """
    Validate audio duration matches video duration within tolerance

    Args:
        audio_path: Path to audio file
        video_duration: Video duration in seconds
        tolerance_ms: Acceptable drift in milliseconds (default: 100ms)

    Returns:
        Tuple of (is_synced, drift_ms)
            - is_synced: True if within tolerance, False otherwise
            - drift_ms: Actual drift in milliseconds
    """
    audio_info = get_audio_info(audio_path)
    audio_duration = audio_info['duration']

    # Calculate drift in milliseconds
    drift_ms = abs(audio_duration - video_duration) * 1000

    # Check if within tolerance
    is_synced = drift_ms <= tolerance_ms

    return (is_synced, drift_ms)


def trim_audio_to_duration(
    audio_path: str,
    target_duration: float,
    output_path: str,
    verbose: bool = False
) -> None:
    """
    Trim audio file to exact duration for video synchronization

    Args:
        audio_path: Path to source audio file
        target_duration: Target duration in seconds
        output_path: Output audio file path
        verbose: Print ffmpeg output

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If ffmpeg trimming fails
    """
    require_ffmpeg()

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Build ffmpeg command to trim audio
    cmd = [
        'ffmpeg',
        '-i', audio_path,
        '-t', str(target_duration),  # Trim to target duration
        '-acodec', 'copy',            # Copy codec (fast, no re-encoding)
        '-y',                         # Overwrite output file
        output_path
    ]

    try:
        if verbose:
            print(f"\n✂️  Trimming audio to {target_duration:.2f}s...")
            result = subprocess.run(cmd, check=True)
        else:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

        if verbose:
            print(f"✅ Audio trimmed successfully: {output_path}\n")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg audio trimming failed: {e}")


def has_audio_stream(video_path: str) -> bool:
    """
    Check if video file contains an audio stream

    Args:
        video_path: Path to video file

    Returns:
        True if video has audio stream, False otherwise
    """
    if not check_ffprobe_installed():
        # Assume video has audio if we can't check
        return True

    if not os.path.exists(video_path):
        return False

    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        video_path
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )

        data = json.loads(result.stdout)

        # Check for audio stream
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                return True

        return False

    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # If we can't determine, assume audio exists
        return True
