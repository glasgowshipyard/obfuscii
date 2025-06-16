# OBFUSCII

ASCII video codec for temporal portraits and responsive branding.

## Overview

OBFUSCII converts video into compressed ASCII animations that scale infinitely, load instantly, and adapt to any visual context. Perfect for temporal portraits, living logos, and ASCII cinema.

**Key Innovation:** Character-based video that exists as pure text—copy/paste friendly, infinitely scalable, context-adaptive.

## Quick Start

```bash
# Install dependencies
pip install opencv-python numpy

# Basic conversion (light theme - default)
python3 obfuscii.py video.mp4

# Dark theme (inverted characters for dark backgrounds)
python3 obfuscii.py video.mp4 --dark

# Both light and dark versions
python3 obfuscii.py video.mp4 --both

# Quick preview
python3 obfuscii.py video.mp4 --preview

# Custom resolution
python3 obfuscii.py video.mp4 --resolution 80x40

# Play existing .txv file
python3 obfuscii.py output.txv
```

## Core Features

- **10:1+ Compression:** Middle-out algorithm with LZMA
- **Infinite Scaling:** CSS responsive from mobile to desktop  
- **Light/Dark Themes:** Automatic character inversion for any background
- **Context Adaptation:** Spaces create "transparent" backgrounds
- **Copy/Paste Distribution:** Text-based sharing
- **Web Native:** Works in any browser, no plugins
- **Progressive Smoothing:** Bilateral → Gaussian → Median filtering

## File Format (.txv)

- **I-frames:** Full ASCII grids at keypoints
- **P-frames:** Delta compression for motion
- **LZMA:** Final compression layer
- **Metadata:** FPS, dimensions, loop info

## Character Set & Themes

**Light Theme (default):** `[' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']`  
**Dark Theme:** `['@', '%', '#', '*', '+', '=', '-', ':', '.', ' ']` (inverted)

Linear brightness progression with space character creating transparency on any background.

## Configuration Presets

- **`light_balanced_high_max.json`** (default) - Optimal balance of quality and compression
- **`config_high_quality.json`** - Maximum visual fidelity, larger files
- **`config_high_compression.json`** - Smallest file size, acceptable quality  
- **`config_default.json`** - Basic settings

## Web Player

Open `index.html` to play `.txv` files in browser with scaling controls.

## Optimization Studio

Open `studio.html` for real-time parameter tuning and compression optimization.

## Use Cases

**Temporal Portraits:** 140x80 character resolution, 3-4 frame loops for website headers  
**ASCII Cinema:** Full-length films as text-based video  
**Living Logos:** Behavioral branding that exists as copy/paste text

## Technical Details

**Progressive Smoothing Pipeline:**
1. Bilateral filter (edge preservation)
2. Gaussian blur (texture removal)  
3. Median filter (noise cleanup)
4. CLAHE contrast enhancement

**Compression Algorithm:**
- RLE encoding of character runs
- Temporal delta compression  
- LZMA final compression
- Target: 10:1+ compression ratios

## Documentation

- `docs/` - Technical guides and advanced usage
- Use `--help` for complete CLI reference

## Development Status

✅ **Core conversion** - Video to ASCII with compression  
✅ **Web player** - Browser-based .txv playback  
✅ **Optimization tools** - Real-time parameter tuning  
🔜 **Export tools** - Social media integration

## Philosophy

*"Temporal logos that exist as behavioral systems rather than static symbols."*

Lightning speed + compression > visual perfection. Text-based media that adapts to any context.

## License

MIT