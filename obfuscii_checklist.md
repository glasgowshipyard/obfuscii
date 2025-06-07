# OBFUSCII Development Checklist

## Phase 1: Core Compression Engine 🚧

### Critical Path (Week 1-4)
- [ ] **Frame extraction to ASCII arrays** - Store each frame as 2D character array instead of terminal output
- [ ] **Frame comparison logic** - Detect character position changes between consecutive frames
- [ ] **Delta compression algorithm** - Generate I-frames (full) + P-frames (changes only)
- [ ] **.txv format specification** - Define file structure for compressed ASCII video
- [ ] **LZMA compression layer** - Apply compression to delta patterns
- [ ] **Basic .txv file export** - Generate compressed files instead of terminal output

### Validation (Week 4-5)
- [ ] **Compression ratio testing** - Verify 10:1 compression claims with real iPhone video
- [ ] **Quality assessment** - Ensure ASCII fidelity maintained through compression/decompression
- [ ] **File size benchmarks** - Test with 3-4 second portrait loops (target <100KB)

## Phase 2: Web Player & Distribution 🔜

### Player Development (Week 6-7)
- [ ] **HTML/CSS/JS web player** - Play .txv files in browser
- [ ] **Frame timing precision** - Maintain correct playback speed
- [ ] **CSS responsive scaling** - Scale from mobile headers to desktop displays
- [ ] **Character substitution** - Background transparency through character swapping

### Integration (Week 8-9)
- [ ] **Loop controls** - Seamless portrait scanning loops
- [ ] **Embedding code generation** - Easy website integration
- [ ] **Cross-browser testing** - Ensure compatibility
- [ ] **Performance optimization** - Smooth playback across devices

## Phase 3: Advanced Features 🔮

### Audio & Export
- [ ] **Audio synchronization** - Frame-perfect audio alignment in .txv
- [ ] **Social media export** - Generate .mp4 from .txv for platforms
- [ ] **Batch processing** - Convert multiple videos efficiently

### Quality & Usability
- [ ] **Resolution override** - Custom output dimensions (bypass terminal size)
- [ ] **Multiple character sets** - Different ASCII density options
- [ ] **Rotation handling** - Auto-detect and correct video orientation
- [ ] **CLI improvements** - Better progress indicators, error handling

## Success Metrics

### Phase 1 Complete When:
- ✅ 3-second iPhone video converts to <100KB .txv file
- ✅ 10:1+ compression ratio achieved vs raw ASCII
- ✅ Facial features recognizable in decompressed output
- ✅ Processing time <30 seconds for test video

### Phase 2 Complete When:
- ✅ .txv plays smoothly in browser
- ✅ Portrait scales from mobile to desktop
- ✅ Copy/paste functionality works
- ✅ Background transparency functional

## Current Status: Frame Extraction
**Next Immediate Task:** Modify ASCII output to store frames as arrays instead of printing to terminal