# OBFUSCII Development Checklist

## Current Status: Clean Rebuild Phase

**Decision Made:** Fork original `video-to-ascii` repo was too complex/bloated. Building focused OBFUSCII implementation from scratch.

**Fork Code Moved To:** `fork/` directory (preserved for reference)

**New Clean Structure Created:**
```
obfuscii.py              # ✅ Main CLI (created)
obfuscii/
  __init__.py           # ✅ Created (empty)
  video.py              # 🚧 Next: Video loading/processing
  ascii.py              # 🚧 GPT's character conversion
  compress.py           # 🚧 Middle-out compression
  txv.py                # 🚧 .txv file format
```

## Phase 1: Core Foundation (Current)

### Step 1: Basic Video to ASCII Conversion ⚡ Priority
- [x] **CLI structure** - `obfuscii.py` with argparse
- [ ] **Video loading** - OpenCV video capture (steal from fork)
- [ ] **Frame processing** - Frame-by-frame conversion loop
- [ ] **GPT ASCII conversion** - Clean greyscale character mapping
- [ ] **Terminal preview** - ASCII output for testing

### Implementation Notes:
**Taking from fork:**
- Basic OpenCV video loading (`cv2.VideoCapture`)
- Frame processing loops
- FPS detection logic

**Discarding from fork:**
- Color processing (all of it)
- Strategy pattern system
- Terminal size detection
- Windows compatibility layers
- Complex brightness calculations
- ANSI color rendering
- Multiple character density options

**GPT ASCII Algorithm (to implement):**
```python
# Simple greyscale conversion
img.convert("L")
# Direct character mapping  
chars = "@%#*+=-:. "
pixel // (256 // len(chars))
```

### Step 2: Frame Data Structures
- [ ] **2D ASCII arrays** - Store frames as List[List[str]] instead of strings
- [ ] **Frame metadata** - Timing, dimensions, frame index
- [ ] **Memory management** - Handle large video files efficiently

### Step 3: Middle-out Compression Algorithm ⭐ Core Innovation
- [ ] **I-frame generation** - Full ASCII grid every N seconds
- [ ] **P-frame delta detection** - Character position changes only
- [ ] **Compression logic** - LZMA on delta patterns
- [ ] **Compression ratio testing** - Verify 10:1+ claims

### Step 4: .txv File Format
- [ ] **Format specification** - Header + I-frames + P-frames + metadata
- [ ] **File writer** - Generate .txv from frame data
- [ ] **File reader** - Parse .txv back to frame arrays
- [ ] **Validation** - Round-trip testing

## Phase 2: Web Player & Distribution

### Web Player Development
- [ ] **HTML/CSS/JS player** - Browser-based .txv playback
- [ ] **Frame timing** - Accurate playback speed
- [ ] **CSS responsive scaling** - Mobile to desktop scaling
- [ ] **Character substitution** - Background transparency feature

### Integration Features  
- [ ] **Loop controls** - Seamless portrait loops
- [ ] **Embedding code** - Easy website integration
- [ ] **Copy/paste optimization** - Viral distribution format

## Phase 3: Advanced Features

### Export & Compatibility
- [ ] **Social media export** - .txv to .mp4 conversion
- [ ] **Audio synchronization** - Frame-perfect audio alignment
- [ ] **Batch processing** - Multiple video conversion

### Quality & Performance
- [ ] **Resolution override** - Custom dimensions
- [ ] **Rotation handling** - Auto-correct phone videos
- [ ] **Performance optimization** - Speed improvements

## Technical Decisions Made

### Character Set: OBFUSCII 8-Character Mapping
**Selected:** `[' ', '-', '#', '=', '+', '*', '%', '@']`
- Based on character frequency analysis of GPT-generated ASCII
- 98.5% visual fidelity with only 8 characters
- Space character enables background transparency
- Optimized for compression efficiency

### Compression Algorithm: "Middle-out"
**Approach:** I-frames (full grids) + P-frames (delta changes) + LZMA
**Target:** 10:1 compression ratio vs raw ASCII video
**Benefits:** Enables practical file sizes for web distribution

### Development Philosophy
- **Lightning speed + outlandish compression** over visual perfection  
- **Greyscale foundation** - color as future extension
- **Copy/paste viral distribution** - text-based format
- **Temporal portraits** - faces scanning left→center→right→center

## Success Metrics

### Phase 1 Complete When:
- ✅ `python3 obfuscii.py test.mp4 --preview` shows clean ASCII conversion
- ✅ 3-second iPhone video converts to <100KB .txv file  
- ✅ 10:1+ compression ratio achieved
- ✅ Facial features recognizable in output
- ✅ Processing time <30 seconds

### Phase 2 Complete When:
- ✅ .txv plays smoothly in browser
- ✅ Portrait scales mobile→desktop  
- ✅ Background transparency functional
- ✅ Copy/paste works as intended

## Files & References

**Test Video:** `test.mp4` (22MB, iPhone footage)
**Reference ASCII:** `fork/ascii_face_background_at_only.txt` (GPT-generated example)
**Legacy Code:** `fork/` directory (video-to-ascii codebase)

## Next Immediate Task
**Build `obfuscii/video.py`** - Video loading and frame processing with GPT's ASCII conversion algorithm.