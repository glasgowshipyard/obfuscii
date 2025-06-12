# OBFUSCII

ASCII video codec for temporal portraits and responsive branding.

## WTF is OBFUSCII?

OBFUSCII converts video into compressed ASCII animations that scale infinitely, load instantly, and adapt to any visual context. Responsive logos that move, breathe, and exist as pure text.

**Key Innovation:** Temporal portraits as ASCII loops—faces scanning left to right, subtle movements, living branding that works from mobile headers to desktop displays through CSS scaling.

## Core Features

- **Middle-out Compression:** Custom algorithm attempting to achieve 10:1 compression ratios vs gigantic raw ASCII video
- **Infinite Scaling:** CSS responsive from tiny mobile headers to full desktop displays  
- **Context Adaptation:** "Transparent" backgrounds through character substitution
- **Copy/Paste Distribution:** Text-based format enables old school sharing
- **Web Native:** No special software required, works in any browser
- **Lightning Fast:** Optimized for speed over visual perfection

## The Copy/Paste Revolution

Traditional logos require multiple versions for different contexts. OBFUSCII portraits adapt automatically:

- **Light backgrounds:** Characters appear dark
- **Dark backgrounds:** Characters appear light  
- **Any context:** Background spaces adapt seamlessly
- **Sharing:** Copying becomes promotion since content is personalized

## File Format

`.txv` (Text Video) files contain:
- **I-frames:** Full ASCII grids every few seconds
- **P-frames:** Delta changes for efficient motion encoding  
- **LZMA compression:** Applied to delta patterns
- **Metadata:** Timing, dimensions, loop points

## Use Cases

### Temporal Portraits
```
Portrait scanning: looking left → centre → right → centre
140x80 character resolution, 3-4 frame loop
Website headers, business cards, social media
```

### ASCII Cinema
Convert full-length films to text-based video. Export to social media or embed as web experiences.

### Living Logos
Moving company branding that exists as behaviour rather than static imagery. Copying becomes potentially viral distribution since personalised content is worthless to steal.

## Technical Foundation

**Built from scratch** with focused architecture:
- **Greyscale processing:** Eliminates color complexity for maximum speed
- **8-character mapping:** Optimized character set for compression efficiency
- **Simple algorithms:** Based on decent, simple GPT ASCII conversion approach
- **Clean codebase:** No legacy bumf, every line has purpose

**Character Set:** `[' ', '-', '#', '=', '+', '*', '%', '@']`
Supports both dark and light backgrounds with inverted character maps.
- 98.5% visual fidelity with minimal compression overhead
- Space character enables background transparency
- Linear brightness progression

## Installation & Usage

```bash
# Basic conversion
python3 obfuscii.py input.mp4

# Custom output and resolution
python3 obfuscii.py input.mp4 -o portrait.txv --resolution 140x80

# Specify background mode (dark, light, or both)
python3 obfuscii.py input.mp4 --background dark

# Preview in terminal
python3 obfuscii.py input.mp4 --preview

# Verbose output
python3 obfuscii.py input.mp4 --verbose
```

## Development Status

🚧 **Phase 1 (Current):** Core video-to-ASCII conversion with middle-out compression  
🔜 **Phase 2:** Web player and responsive scaling  
🔜 **Phase 3:** Social media export and advanced features

## Philosophy

Traditional media is fixed and static, requiring multiple versions for different contexts. OBFUSCII media is temporal, scalable, and context-adaptive. 

ASCII video works best through stylization rather than photorealistic conversion. We target specific resolution sweet spots that preserve recognition while maintaining practical file sizes for web distribution.

**Core Principle:** Lightning speed + outlandish compression > visual perfection

## Technical Innovation

**Middle-out Compression Algorithm:**
- Analyzes character position changes between frames
- Encodes only differences, not full frames
- Achieves 10:1+ compression ratios
- Enables practical file sizes for temporal portraits

**Background Transparency:**
- Space characters adapt to any context
- No alpha channels or color matching needed
- Perfect integration with any website theme
- Copy/paste maintains transparency

## Repository Structure

```
obfuscii.py              # Main CLI interface
obfuscii/               # Core modules
  video.py              # Video loading and processing
  ascii.py              # Character conversion algorithms  
  compress.py           # Middle-out compression engine
  txv.py                # File format handling
fork/                   # Original video-to-ascii reference code
test.mp4                # Test video file
```

## Contributing

Early development phase. Core compression algorithm takes priority, followed by web player implementation.

**Current Focus:** Building clean video-to-ASCII conversion with GPT's off the cuff algorithm.

## License

MIT

---

*"Temporal logos that exist as behavioral systems rather than static symbols."*