# OBFUSCII v2.0

ASCII video codec for social media content creation.

Convert video to compressed ASCII animation with synchronized audio, export to platform-optimized formats, and demo with live webcam filter.

---

## Features

### Core Codec
- **Video→ASCII conversion** with progressive smoothing
- **RLE+LZMA compression** (5-10:1 ratios)
- **Binary .txv format** with metadata
- **Web playback** with LZMA decompression

### v2.0 Features
- **Audio integration** - Synchronized audio playback
- **Social media export** - Platform-optimized MP4 (Reels, YouTube, Instagram)
- **Live mode** - Real-time webcam ASCII filter

---

## Installation

### 1. Install Python Dependencies

```bash
pip install opencv-python numpy Pillow
```

### 2. Install System Dependencies

**ffmpeg** (required for audio and export):

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

### 3. Verify Installation

```bash
python3 obfuscii.py --help
ffmpeg -version
```

---

## Quick Start

### Convert Video with Audio

```bash
python3 obfuscii.py video.mp4 --with-audio
```

Creates:
- `video.txv` - Compressed ASCII video
- `video_audio.mp3` - Audio track

### Export for Social Media

```bash
# Reels/TikTok/Shorts (vertical 9:16)
python3 obfuscii.py video.txv --export reels

# YouTube (horizontal 16:9)
python3 obfuscii.py video.txv --export youtube

# Instagram Square (1:1)
python3 obfuscii.py video.txv --export instagram_square
```

### Live Webcam Demo

```bash
python3 obfuscii.py --live
```

Opens browser with real-time ASCII filter.

---

## Usage Guide

### Video Conversion

**Basic conversion:**
```bash
python3 obfuscii.py video.mp4
```

**With audio:**
```bash
python3 obfuscii.py video.mp4 --with-audio
```

**Dark theme:**
```bash
python3 obfuscii.py video.mp4 --dark
```

**Custom resolution:**
```bash
python3 obfuscii.py video.mp4 --resolution 160x90
```

**Custom config:**
```bash
python3 obfuscii.py video.mp4 --config config_high_quality.json
```

**Preview (first 30 frames):**
```bash
python3 obfuscii.py video.mp4 --preview
```

### Audio Options

**Extract audio (MP3, AAC, OGG):**
```bash
python3 obfuscii.py video.mp4 --with-audio --audio-format aac --audio-bitrate 256k
```

**Strip audio:**
```bash
python3 obfuscii.py video.mp4 --no-audio
```

### Social Media Export

**List available profiles:**
```bash
python3 obfuscii.py --list-profiles
```

**Export profiles:**
- `reels` - Instagram/Facebook Reels (1080x1920, 9:16)
- `tiktok` - TikTok (1080x1920, 9:16)
- `youtube_shorts` - YouTube Shorts (1080x1920, 9:16)
- `youtube` - YouTube (1920x1080, 16:9)
- `youtube_4k` - YouTube 4K (3840x2160, 16:9)
- `instagram_square` - Instagram Feed (1080x1080, 1:1)
- `twitter` - Twitter/X (1280x720, 16:9)

**Export examples:**
```bash
# Reels (vertical)
python3 obfuscii.py video.txv --export reels

# YouTube with dark theme
python3 obfuscii.py video.txv --export youtube --export-theme dark

# Custom output path
python3 obfuscii.py video.txv --export reels --export-output branded.mp4

# Custom font
python3 obfuscii.py video.txv --export reels --export-font /path/to/font.ttf

# Verbose output
python3 obfuscii.py video.txv --export reels --verbose
```

### Live Mode

**Launch webcam filter:**
```bash
python3 obfuscii.py --live
```

Features:
- Real-time webcam→ASCII conversion (10-20 FPS)
- Resolution selector (60, 80, 120, 160 chars)
- Performance stats display
- Screenshot capture (saves as .txt)
- Auto-performance adjustment

Access on mobile: `http://YOUR_IP:8000/live.html`

### Playback

**Play .txv file:**
```bash
python3 obfuscii.py video.txv
```

Or open `index.html` in browser and load the file.

**File info:**
```bash
python3 obfuscii.py video.txv --info
```

**Validate:**
```bash
python3 obfuscii.py video.txv --validate
```

---

## Complete Workflow Example

```bash
# 1. Convert video with audio
python3 obfuscii.py myvideo.mp4 --with-audio
# → Creates: myvideo.txv + myvideo_audio.mp3

# 2. Preview in browser
python3 obfuscii.py myvideo.txv
# → Opens index.html, loads .txv, plays with audio

# 3. Export for Reels (vertical)
python3 obfuscii.py myvideo.txv --export reels
# → Creates: myvideo_reels.mp4 (1080x1920 with audio)

# 4. Export for YouTube (horizontal)
python3 obfuscii.py myvideo.txv --export youtube
# → Creates: myvideo_youtube.mp4 (1920x1080 with audio)

# 5. Demo with live mode
python3 obfuscii.py --live
# → Opens browser with real-time webcam ASCII

# 6. Upload to platforms
# - myvideo_reels.mp4 → Instagram Reels, TikTok, YouTube Shorts
# - myvideo_youtube.mp4 → YouTube, Twitter
```

---

## Architecture

### .TXV File Format (v2.0)

Binary format:
```
[8 bytes]  Magic: b'OBFUSCII'
[4 bytes]  Version: uint32
[4 bytes]  Metadata length: uint32
[N bytes]  Metadata: JSON (UTF-8)
[4 bytes]  Frame count: uint32
[Frames]   Compressed frame data
```

**Metadata fields (v2.0):**
- Video: width, height, fps, duration, compression ratio
- Audio: has_audio, audio_file, format, codec, sample_rate, bitrate, channels
- Sync: audio_sync_offset_ms (manual adjustment)

**Backward compatible:** v1.0 files still work (no audio)

### Processing Pipeline

**Video→ASCII:**
1. Load video with OpenCV
2. Progressive smoothing (bilateral → gaussian → median → CLAHE)
3. Frame-to-ASCII with hysteresis (anti-flicker)
4. Pattern cleanup (4-stage modular)
5. RLE+LZMA compression
6. Export to .txv

**Audio extraction:**
1. Detect audio stream with ffprobe
2. Extract audio with ffmpeg (MP3/AAC/OGG)
3. Store metadata in .txv
4. Player loads audio automatically

**Export pipeline:**
1. Load .txv and decompress frames
2. Render ASCII to PNG with PIL (parallel)
3. Encode to MP4 with ffmpeg (H.264 + AAC)
4. Platform-specific bitrates and resolutions

**Live mode:**
1. WebRTC captures webcam at 1280x720
2. Canvas extracts frame as ImageData
3. JavaScript converts to grayscale and resizes
4. Map brightness to ASCII characters
5. Display in `<pre>` element

---

## File Structure

```
obfuscii/
├── obfuscii.py              # CLI entry point
├── obfuscii/
│   ├── vid.py               # Video→ASCII processing
│   ├── moc.py               # RLE+LZMA compression
│   ├── txv.py               # .txv file format I/O
│   ├── config.py            # Configuration system
│   ├── audio.py             # Audio extraction (v2.0)
│   └── export.py            # MP4 export (v2.0)
├── player.js                # Web player with audio sync
├── index.html               # Web player UI
├── live.html                # Live mode web app (v2.0)
├── studio.html              # Parameter optimizer
└── docs/                    # Technical documentation
```

---

## Configuration

### Presets

**Default:** `light_balanced_high_max.json` (optimal balance)

**Other presets:**
- `config_high_quality.json` - Maximum visual fidelity
- `config_high_compression.json` - Smallest file size
- `config_default.json` - Basic settings

### Custom Configuration

Create JSON config with:
- **Smoothing:** bilateral, gaussian, median filter parameters
- **Conversion:** ASCII character set, width, hysteresis threshold
- **Cleanup:** isolated char, run consolidation, temporal smoothing, spatial coherence
- **Compression:** LZMA preset (0-9)
- **Audio:** format, bitrate, sample rate (v2.0)
- **Export:** theme, profiles (v2.0)

Example:
```json
{
  "version": "2.0",
  "smoothing": {
    "bilateral_d": 15,
    "gaussian_kernel": 9,
    "median_kernel": 5
  },
  "conversion": {
    "ascii_chars": [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"],
    "default_width": 140
  }
}
```

---

## Performance

### Compression Ratios
- Excellent: 10:1+
- Very Good: 7:1+
- Good: 5:1+

Typical: 5-10:1 for most videos

### Export Speed
- 30s video (900 frames): ~30-60 seconds
- Parallel rendering: 4-8 cores used
- Depends on resolution and CPU

### Live Mode FPS
- Desktop: 10-20 FPS (60-120 char widths)
- Mobile: 8-15 FPS (60-80 char widths)
- Auto-adjusts resolution if FPS < 10

---

## Troubleshooting

### "ffmpeg not found"

Install ffmpeg:
```bash
brew install ffmpeg       # macOS
sudo apt install ffmpeg   # Ubuntu
choco install ffmpeg      # Windows
```

### Audio doesn't load in browser

**Check:**
1. Audio file exists in same directory as .txv
2. Browser console for errors (F12)
3. Audio file format supported (MP3/AAC/OGG)

**Solution:** Re-extract audio with different format:
```bash
python3 obfuscii.py video.mp4 --with-audio --audio-format aac
```

### Audio out of sync

**Solution:** Adjust sync offset in .txv metadata:
```json
"audio_sync_offset_ms": -100  // Negative = audio earlier
```

Or re-extract audio:
```bash
python3 obfuscii.py video.mp4 --with-audio --verbose
```

### Export is slow

**Expected:** 30-60s for 30s video

**Speed up:**
- Uses all CPU cores automatically
- Reduce resolution: `--resolution 100x60`
- Use lower quality preset: `--config config_high_compression.json`

### Live mode: Camera access denied

**Solution:**
1. Check browser permissions (Settings → Camera)
2. Try Chrome (best compatibility)
3. Ensure no other app is using camera
4. Try incognito mode

### Live mode: Low FPS

**Solution:**
- Reduce resolution (60 or 80 chars)
- Close other browser tabs
- Auto-adjustment should activate if FPS < 10

### Export rejected by platform

**Check:**
1. Resolution matches platform requirements
2. Audio codec is AAC (should be automatic)
3. Video codec is H.264 (should be automatic)
4. File size not too large

**Platform requirements:**
- Instagram Reels: 1080x1920 (9:16), max 90s
- TikTok: 1080x1920 (9:16), max 60s
- YouTube: 1920x1080 (16:9), any length
- Instagram Feed: 1080x1080 (1:1), max 60s

---

## Platform-Specific Tips

### Instagram Reels
- Use `--export reels`
- Keep under 90 seconds
- Light theme recommended
- Audio is critical

### TikTok
- Use `--export tiktok` (same as Reels)
- Keep under 60 seconds for feed
- Vertical format essential

### YouTube
- Use `--export youtube` for main videos (16:9)
- Use `--export youtube_shorts` for Shorts (9:16)
- Longer videos acceptable
- 4K option available: `--export youtube_4k`

### Instagram Feed
- Use `--export instagram_square` (1:1)
- Keep under 60 seconds
- Square format for feed posts

### Twitter/X
- Use `--export twitter` (16:9)
- Keep under 2:20
- 720p acceptable

---

## Technical Specs

### Video Encoding
- **Codec:** H.264 (libx264)
- **Quality:** CRF 18 (high quality)
- **Pixel format:** yuv420p (platform compatibility)
- **Preset:** medium (speed/quality balance)
- **Flags:** +faststart (streaming)

### Audio Encoding
- **Codec:** AAC
- **Bitrate:** 192k (standard), 256k (4K)
- **Sample rate:** 44100 Hz or 48000 Hz
- **Channels:** Mono or stereo

### ASCII Character Set
Default: `[' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']`
- Space = darkest
- @ = brightest
- 10 density levels

Dark theme: Inverted character set

---

## API Reference

### CLI Commands

**Video conversion:**
```bash
obfuscii.py <input> [options]
```

**Options:**
- `-o, --output` - Output file path
- `--resolution WxH` - ASCII resolution
- `--config FILE` - Configuration preset
- `--preview` - Convert first 30 frames only
- `--verbose` - Detailed output
- `--force` - Overwrite without prompt

**Theme:**
- `--light` - Light background (default)
- `--dark` - Dark background
- `--both` - Generate both versions

**Audio:**
- `--with-audio` - Extract audio
- `--audio-format FORMAT` - Audio format (mp3/aac/ogg)
- `--audio-bitrate RATE` - Audio bitrate (128k/192k/256k/320k)
- `--no-audio` - Strip audio

**Export:**
- `--export PROFILE` - Export to MP4
- `--export-output FILE` - Output path
- `--export-theme THEME` - Rendering theme (light/dark)
- `--export-font PATH` - Custom font
- `--list-profiles` - List export profiles

**Live mode:**
- `--live` - Launch webcam filter

**File operations:**
- `--info` - Show file metadata
- `--validate` - Validate file integrity

---

## Development

### Module Structure

**obfuscii/vid.py** - Video processing
- `load_video()` - Extract metadata
- `progressive_smoothing()` - Image filtering
- `frame_to_ascii_with_hysteresis()` - Conversion with anti-flicker
- `cleanup_ascii_patterns()` - 4-stage cleanup
- `process_video_to_compressed()` - Main pipeline

**obfuscii/moc.py** - Compression
- `encode_frame_rle()` - Run-length encoding
- `compress_video_rle()` - Full video compression
- `decompress_video_rle()` - Decompression

**obfuscii/txv.py** - File format
- `write_txv_file()` - Write .txv with metadata
- `read_txv_file()` - Read .txv and decompress
- `validate_txv_file()` - Integrity check

**obfuscii/audio.py** (v2.0) - Audio
- `extract_audio_from_video()` - ffmpeg extraction
- `get_audio_info()` - ffprobe metadata
- `validate_audio_sync()` - Duration check

**obfuscii/export.py** (v2.0) - Export
- `render_ascii_frame_to_image()` - PIL rendering
- `render_frames_to_directory()` - Batch rendering (parallel)
- `encode_frames_to_video()` - ffmpeg encoding
- `export_video_from_txv()` - Full export pipeline

### Testing

```bash
# Test conversion
python3 obfuscii.py test.mp4 --preview

# Test audio
python3 obfuscii.py test.mp4 --with-audio --verbose

# Test export
python3 obfuscii.py test.txv --export reels --verbose

# Test live mode
python3 obfuscii.py --live
```

---

## Changelog

### v2.0 (Current)
- ✅ Audio integration (synchronized playback)
- ✅ Social media export (7 platform profiles)
- ✅ Live mode (WebRTC webcam filter)
- ✅ .txv format v2.0 with audio metadata
- ✅ Web player audio sync with drift correction
- ✅ Parallel frame rendering for export

### v1.0
- ✅ Video→ASCII conversion
- ✅ RLE+LZMA compression
- ✅ .txv binary format
- ✅ Web player
- ✅ Progressive smoothing
- ✅ Hysteresis anti-flicker
- ✅ Pattern cleanup

---

## License

See LICENSE file.

---

## Credits

Built for temporal logos and ASCII-based social media content.

**Dependencies:**
- OpenCV (video I/O)
- Pillow (image rendering)
- ffmpeg (audio/video encoding)
- LZMA.js (browser decompression)
