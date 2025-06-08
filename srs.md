# OBFUSCII Software Requirements Specification

**Version:** 2.0  
**Date:** June 2025  
**Status:** Phase 1 Complete, Production Deployment Ready

## Project Overview

OBFUSCII is an ASCII video codec for creating temporal portraits and responsive branding. The system converts video into compressed ASCII animations that scale infinitely, load instantly, and adapt to any visual context.

**Core Innovation:** Moving ASCII portraits that work as responsive web logos, distributed through copy/paste text mechanics while maintaining professional compression ratios.

## System Architecture

### Two-Component System

**OBFUSCII Player** - Media application for content creation, testing, and file management  
**OBFUSCII Embed** - Component library for website/email integration

**File Format:** `.txv` (Text Video) - Binary container with LZMA-compressed RLE ASCII frames plus metadata

## Functional Requirements

### FR1: Content Creation Pipeline

**Input Processing:**
- Video file support: `.mp4`, `.mov`, `.avi`, `.mkv`
- Resolution targeting: 140x80 (portrait), 80x24 (terminal), 160x45 (web cinema)
- Frame rate preservation: 30fps baseline, 60fps target capability
- Progressive smoothing cascade for compression optimization

**ASCII Conversion:**
- Character set: `[' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']`
- Character boundary hysteresis to prevent flicker artifacts
- Aspect ratio compensation for display differences
- Quality preservation targeting facial feature recognition

**Compression Engine:**
- Algorithm: Spatial RLE + LZMA compression
- Target ratio: 5:1 minimum, 7:1+ production goal
- 4-stage cleanup pipeline:
  - Isolated character replacement
  - Run consolidation for RLE optimization  
  - Temporal smoothing across frames
  - Spatial coherence filtering

### FR2: Media Player Application

**Core Playback:**
- `.txv` file loading with format validation
- 60fps playback capability
- Frame timing precision <16.67ms
- Dynamic resizing with real-time adaptation

**Media Controls:**
- Playback interface: play/pause/stop/loop controls
- Frame scrubbing and timing control
- Size scaling: manual + responsive viewport adaptation
- Performance monitoring: compression ratios, frame rates, statistics

**File Operations:**
- `.txv` metadata inspection and validation
- Export pipeline for distribution formats
- Batch processing for multiple video conversion

### FR3: Embeddable Component System

**Integration Features:**
- Minimal UI - no visible player boundaries
- Auto-play infinite looping for logo applications
- CSS-responsive scaling across viewport sizes
- Self-contained HTML snippets

**Distribution Formats:**
- Inline ASCII data with CSS animation
- JavaScript component library
- Email-compatible HTML rendering
- Copy/paste ASCII text preservation

**Performance Specifications:**
- <100ms load time for embedded components
- <500KB typical file sizes
- Cross-browser compatibility: Chrome, Firefox, Safari, Edge

### FR4: Social Media Export Pipeline

**Video Export Capabilities:**
- `.txv` → `.mp4` conversion with frame-perfect rendering
- Canvas-based ASCII-to-video pipeline
- Multiple aspect ratios: 9:16 (vertical), 1:1 (square), 16:9 (landscape)
- Background options: transparent, solid colors, branded overlays
- Platform-optimized compression for Instagram/TikTok/LinkedIn

**Export Specifications:**
- Monospace font optimization for video rendering
- File size optimization leveraging ASCII compression
- Quality preservation across format conversions

## Security Requirements

### SR1: Input Validation

**File Format Security:**
- `.txv` binary validation before processing
- Magic header verification and version checking
- Metadata sanitization
- File size limits and processing timeouts

**Decompression Security:**
- LZMA decompression limits with memory bounds
- Maximum frame count and resolution limits
- Timeout protection for operations
- Content sanitization to prevent injection attacks

**Web Security:**
- Content Security Policy headers
- CORS validation for external files
- Input sanitization for user content
- Error boundary isolation

## Performance Requirements

### PR1: Playback Performance

**Frame Rate Targets:**
- 30fps baseline performance across supported browsers
- 60fps stretch goal with hardware acceleration
- Smooth playback under resource constraints
- Frame timing precision for video quality

**Memory Management:**
- Efficient frame buffering for large files
- Progressive loading for web playback
- Memory optimization for embedded components
- Garbage collection efficiency

### PR2: Compression Performance

**Ratio Targets:**
- 5:1 minimum compression ratio
- 7:1+ target ratio for web distribution
- Quality preservation across compression levels

**Processing Speed:**
- Real-time preview during conversion
- Batch processing capabilities
- Progressive encoding with user feedback
- Export optimization for different formats

## Technical Specifications

### File Format Structure
```
[8 bytes] Magic: b'OBFUSCII'
[4 bytes] Version: uint32
[4 bytes] Metadata length: uint32  
[N bytes] Metadata: JSON (UTF-8)
[4 bytes] Frame count: uint32
[Frame data] Compressed frames with headers
```

### Frame Header Structure
```
[4 bytes] Frame index
[1 byte]  Frame type ('I' or 'P')
[3 bytes] Padding
[8 bytes] Timestamp (double)
[4 bytes] Raw size
[4 bytes] Compressed size
[N bytes] Compressed data
```

### Character Mapping
Optimized 8-character progression for maximum compression efficiency:
- Space character enables background transparency
- Linear brightness progression
- 98.5% visual fidelity with minimal overhead

## Development Phases

### Phase 1: Foundation ✅ Complete
- Core video → ASCII → compression → .txv pipeline
- 5:1+ compression ratios achieved
- Binary file format implemented
- Terminal playback functional

### Phase 2: Production Deployment (Next)
- Web player deployment to Cloudflare Pages
- Modern UI design
- Browser LZMA decompression
- Social media export pipeline
- Embeddable component library

### Phase 3: Growth & Adoption (1-3 months)
- Portrait logo proof-of-concept
- Developer documentation
- Performance optimization
- Security hardening

### Phase 4: Advanced Features (Long-term)
- Audio synchronization
- Background removal tools
- Advanced export options
- Format evolution

## Success Metrics

### Technical Performance
- 60fps playback capability
- <100ms embed load times
- 7:1+ compression ratio consistently
- Zero security vulnerabilities

### Adoption Metrics
- Portrait logo deployments
- Copy/paste distribution events
- Developer community adoption
- Integration case studies

## Implementation Notes

### Browser Compatibility
- Modern browsers with ES6+ support
- WebAssembly for performance-critical operations
- Graceful degradation for older browsers
- Mobile optimization for responsive scaling

### Deployment Requirements
- Static hosting with custom MIME type support
- CORS headers for cross-origin .txv loading
- CDN optimization for global distribution
- Custom domain support for branding

---

**Current Status:** Phase 1 complete, ready for production deployment. Core pipeline validated, compression targets achieved, file format stable.