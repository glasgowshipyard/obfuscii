# OBFUSCII

ASCII video codec for temporal portraits and responsive branding.

## WTF is OBFUSCII?

OBFUSCII converts video into compressed ASCII animations that scale infinitely, load instantly, and adapt to any visual context. Responsive logos that move, breathe, and exist as pure text.

**Key Innovation:** Temporal portraits as ASCII loops—faces scanning left to right, subtle movements, living branding that works from mobile headers to desktop displays through CSS scaling.

## Core Features

- **Delta Compression:** Custom algo aiming to achieve 10:1 compression ratios vs raw ASCII video
- **Infinite Scaling:** CSS responsive from tiny mobile headers to full desktop displays
- **Context Adaptation:** "Transparent" backgrounds through character substitution
- **Copy/Paste Distribution:** Text-based format enables viral sharing
- **Web Native:** No special software required, works in any browser
- **Audio Sync:** Frame-perfect synchronisation for full cinematic experiences

## File Format

`.txv` (Text Video) files contain:
- I-frames: Full ASCII grids every 2-5 seconds
- P-frames: Delta changes for efficient motion encoding
- LZMA compression on delta patterns
- Optional audio synchronisation data

## Use Cases

### Personal Branding
```
Portrait scanning: looking left → centre → right → centre
140x80 character resolution, 3-4 frame loop
Website headers, business cards, social media
```

### ASCII Cinema
Convert full-length films to text-based video with audio synchronisation. Export to social media or embed as web experiences.

### Temporal Logos
Moving company branding that exists as behaviour rather than static imagery. Copying becomes viral distribution since personalised content is worthless to steal.

## Resolution Targets

- **Portraits/Logos:** 120x70, 140x80 (facial detail recognition)
- **Terminal:** 80x24, 120x30, 132x43 (classic sizes)  
- **Web Cinema:** 160x45, 200x60 (film display)
- **Social Media:** Platform-specific aspect ratios

## Technical Foundation

Built on [joelibaceta/video-to-ascii](https://github.com/joelibaceta/video-to-ascii) with:
- Resolution override capabilities (bypass terminal size limits)
- Custom delta compression pipeline
- Web player with responsive CSS scaling
- Social media export functionality

## Development Status

🚧 **Phase 1 (Current):** Core compression algorithm and .txv format
🔜 **Phase 2:** Web player and responsive scaling
🔜 **Phase 3:** Social media export and distribution tools

## Philosophy

Traditional media is fixed and static, requiring multiple versions for different contexts. OBFUSCII media is temporal, scalable, and context-adaptive. Copying becomes promotion when content is personalised but format is universal.

ASCII video works best through stylisation rather than photorealistic conversion. We target specific resolution sweet spots that preserve recognition while maintaining practical file sizes.

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/obfuscii.git
cd obfuscii

# Install dependencies
npm install

# Convert video to .txv
./obfuscii input.mp4 --resolution 140x80 --output portrait.txv

# Play .txv file
./obfuscii --play portrait.txv
```

## Contributing

Early development phase. Core compression algorithm takes priority, followed by web player implementation.

## License

MIT

---

*"Temporal logos that exist as behavioral systems rather than static symbols."*
CHARS_LIGHT 	= [' ', ' ', '.', ':', '!', '+', '*', 'e', '$', '@', '8']
CHARS_COLOR 	= ['.', '*', 'e', 's', '@']
CHARS_FILLED    = ['░', '▒', '▓', '█']
```

The reduced range of colors supported by the terminal is a problem we need to account for. Modern terminals support up to 256 colors, so we need to find the closest 8 bit color that matches the original pixel in 16 or 24 bit color, we call this set of 256 colors [ANSI colors](https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences).

![The Mapping of RGB and ANSI Colors](./images/imgPixelSection.png)

![8 Bits Color Table](./images/8-bit_color_table.png)

Finally, when putting it all together, we will have an appropriate character for each pixel and a new color.

![Frame Image by Characters](./images/imgPixelImage.png)

## Contributors

### Code Contributors

This project exists thanks to all the people who contribute. [[Contribute](./CONTRIBUTING.md)].

<a href="https://github.com/joelibaceta/video-to-ascii/graphs/contributors"><img src="https://opencollective.com/video-to-ascii/contributors.svg?width=890&button=false" /></a>

### Financial Contributors

Become a financial contributor and help us sustain our community. [[Contribute](https://opencollective.com/video-to-ascii/contribute/)].

Or maybe just [buy me a coffee](https://ko-fi.com/joelibaceta).

#### Individuals

<a href="https://opencollective.com/video-to-ascii#backers" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/individuals.svg?width=890"></a>

#### Organizations

Support this project with your organization. Your logo will show up here with a link to your website. [[Contribute](https://opencollective.com/video-to-ascii/contribute)]

<a href="https://opencollective.com/video-to-ascii/organization/0/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/0/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/1/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/1/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/2/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/2/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/3/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/3/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/4/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/4/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/5/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/5/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/6/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/6/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/7/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/7/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/8/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/8/avatar.svg"></a>
<a href="https://opencollective.com/video-to-ascii/organization/9/website" target="_blank" rel="noopener"><img src="https://opencollective.com/video-to-ascii/organization/9/avatar.svg"></a>

## As Seen On
<a href="https://www.producthunt.com/posts/video-to-ascii" target="_blank" rel="noopener"><img src="https://user-images.githubusercontent.com/864790/124545434-a2e7fe80-ddee-11eb-9d80-f24049524fd9.png" width="100px"></a>
