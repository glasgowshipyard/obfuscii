# OBFUSCII Software Requirements Specification

**Version:** 3.0  
**Date:** June 2025  
**Status:** Algorithm Development Phase

## Project Overview

OBFUSCII is an ASCII video codec for creating temporal portraits and responsive branding. The system converts video into compressed ASCII animations that scale infinitely, load instantly, and adapt to any visual context.

**Current Problem:** Compression ratios are 3.7:1-5:1, below the 7:1+ target needed for practical web deployment. The core issue is errant noise characters fragmenting RLE runs.

**Solution Approach:** Build a studio interface for real-time algorithm optimization rather than blind parameter tweaking in code.

## System Architecture

### Three-Component System

**OBFUSCII Studio** - Web-based algorithm development and optimization environment  
**OBFUSCII Player** - Media application for content creation, testing, and file management  
**OBFUSCII Embed** - Component library for website/email integration

**File Format:** `.txv` (Text Video) - Binary container with LZMA-compressed RLE ASCII frames plus metadata

## Current Status

### Working Components ✅
- Video → ASCII conversion pipeline
- RLE + LZMA compression (achieving 3.7:1-5:1 ratios)
- .txv binary file format with validation
- Web player with LZMA decompression
- Terminal playback functionality
- Cross-platform deployment

### Critical Issues ❌
- Compression ratios below 7:1+ target
- Errant noise characters fragmenting RLE runs
- Cleanup pipeline parameters require systematic optimization
- No efficient method for algorithm tuning

## Priority Requirements: OBFUSCII Studio

### SR1: Algorithm Development Environment

**Core Function:** Real-time parameter optimization interface for compression algorithm development.

**Input Processing:**
- Video file upload (.mp4, .mov, .avi, .mkv)
- Single image upload (.jpg, .png) for testing
- Frame isolation from video timeline
- Drag-and-drop file handling

**Real-time ASCII Preview:**
- Live ASCII conversion as parameters change
- Side-by-side before/after comparison
- Monospace font display using `<pre>` elements
- Responsive viewport scaling

**Parameter Control Interface:**
- **Progressive Smoothing Controls:**
  - Bilateral filter strength (0-100)
  - Gaussian blur radius (1-15)
  - Median filter kernel size (3-11)
  - CLAHE contrast enhancement (0.5-3.0)

- **Character Conversion Controls:**
  - Hysteresis threshold (4-24 pixels)
  - Character boundary sensitivity (0.1-2.0)
  - Brightness mapping curve adjustment

- **Cleanup Pipeline Controls:**
  - Isolated character replacement aggressiveness (0-100%)
  - Run consolidation strength (0-100%)
  - Spatial coherence threshold (0.15-0.7)
  - Multiple cleanup passes (1-5 iterations)

**Real-time Metrics Display:**
- RLE compression ratio calculation
- Run length distribution analysis
- Character frequency histogram
- Visual quality preservation metrics

### SR2: Full Video Processing Workflow

**Apply Optimized Settings:**
- Process entire video with studio-optimized parameters
- Progress indication for long videos
- Memory-efficient frame processing
- Error handling and recovery

**Preview and Validation:**
- ASCII video playback with optimized settings
- Frame-by-frame scrubbing capability
- Compression ratio validation across full video
- Visual quality assessment tools

**Settings Management:**
- Save/load parameter presets
- Export optimized settings for production pipeline
- Content-type specific parameter sets (faces, landscapes, motion)
- Parameter validation and bounds checking

### SR3: Export Pipeline

**ASCII Video Export:**
- .txv format with optimized compression
- Metadata embedding (settings used, compression achieved)
- File size optimization
- Validation and integrity checking

**Social Media Export:**
- Canvas-based ASCII-to-video rendering
- Multiple aspect ratios (1:1, 9:16, 16:9)
- .mp4 export using MediaRecorder API or equivalent
- Frame rate and quality controls
- Background options (transparent, solid, branded)

**Settings Export:**
- JSON parameter export for production pipeline integration
- Documentation generation for settings
- Batch processing configuration files

## Technical Implementation Requirements

### TI1: Studio Architecture

**Frontend Framework:**
- Pure HTML/CSS/JavaScript (no framework dependencies)
- Real-time parameter updates using input event handlers
- Canvas API for image processing and preview
- File API for drag-and-drop functionality

**Algorithm Implementation:**
- Port critical functions from `vid.py` and `moc.py` to JavaScript
- Real-time ASCII conversion without server round-trips
- RLE compression calculation in browser
- Efficient frame processing for responsive UI

**Required Functions from Python Codebase:**
```javascript
// From vid.py
progressiveSmoothing(imageData, parameters)
frameToASCII(imageData, parameters)
cleanupASCIIPatterns(asciiFrame, parameters)

// From moc.py  
encodeFrameRLE(asciiFrame)
calculateCompressionRatio(rleSegments, originalSize)
```

### TI2: Parameter System

**Parameter Structure:**
```javascript
const optimizationParameters = {
  smoothing: {
    bilateralStrength: 80,
    gaussianRadius: 9,
    medianKernel: 5,
    claheClip: 1.5
  },
  conversion: {
    hysteresisThreshold: 8,
    boundarySensitivity: 1.0,
    contrastCurve: 'linear' // 'linear', 'sigmoid', 'exponential'
  },
  cleanup: {
    isolatedReplacement: 75,
    runConsolidation: 85,
    spatialCoherence: 0.4,
    cleanupPasses: 2
  }
}
```

**Parameter Validation:**
- Real-time bounds checking
- Parameter interdependency validation  
- Performance impact warnings for expensive settings
- Automatic parameter suggestions based on content analysis

### TI3: Performance Requirements

**Real-time Responsiveness:**
- Parameter changes reflected in ASCII preview within 100ms
- Smooth slider interactions without lag
- Efficient canvas operations for large images
- Progressive processing for high-resolution inputs

**Memory Management:**
- Efficient image buffer handling
- Garbage collection optimization
- Memory usage monitoring and limits
- Progressive loading for large video files

**Browser Compatibility:**
- Modern browsers with Canvas API support
- File API and drag-and-drop functionality
- MediaRecorder API for video export
- Fallback options for unsupported features

## Integration with Existing System

### Studio → Production Pipeline

**Parameter Export:**
- JSON configuration files consumable by `obfuscii.py`
- Direct parameter injection into Python pipeline
- Batch processing configuration generation
- Settings validation and compatibility checking

**Workflow Integration:**
1. Optimize parameters in Studio using representative content
2. Export validated parameter sets 
3. Apply settings to production `obfuscii.py` pipeline
4. Batch process content with proven parameters
5. Eliminate iterative parameter guessing

### Backward Compatibility

**Existing .txv Files:**
- Studio can load and analyze existing .txv files
- Parameter reverse-engineering from compressed content
- Quality assessment of historical conversions
- Migration path for improved compression

**Player Integration:**
- Studio-generated .txv files compatible with existing player
- Metadata preservation for settings tracking
- Version compatibility across studio and player components

## Development Phases

### Phase 1: Core Studio Development (Immediate Priority)
- Single frame parameter optimization interface
- Real-time ASCII preview with sliders
- RLE compression ratio calculation
- Parameter export functionality

### Phase 2: Full Video Processing
- Video upload and frame isolation
- Full video processing with optimized parameters
- ASCII video preview and validation
- Social media export pipeline

### Phase 3: Production Integration
- Parameter injection into Python pipeline
- Batch processing workflows
- Content-type specific parameter sets
- Advanced analytics and optimization

### Phase 4: Advanced Features (Future)
- Audio synchronization support
- AI-powered parameter optimization
- Content analysis and automatic parameter selection
- Cloud processing for large videos

## Success Criteria

### Algorithm Optimization
- Consistent 7:1+ compression ratios on real-world content
- Visual quality preservation for facial recognition
- Elimination of errant noise characters fragmenting RLE runs
- Reproducible parameter sets for different content types

### Development Efficiency
- Real-time parameter tuning replacing code iteration cycles
- Settings validation and export for production use
- Systematic algorithm development rather than trial-and-error
- Clear path from optimization to deployment

### System Integration
- Seamless workflow from studio optimization to production
- Backward compatibility with existing components
- Parameter portability across development and production environments
- Reliable batch processing with proven settings

## Technical Debt and Constraints

### Current Limitations
- ASCII conversion quality vs compression trade-off not optimized
- Manual parameter tuning is inefficient and unreliable
- No systematic approach to algorithm development
- Limited visibility into compression bottlenecks

### Studio Constraints
- Browser-based processing limits for very large videos
- Canvas API performance constraints for real-time processing
- JavaScript implementation complexity for advanced image processing
- Memory limitations for high-resolution content

### Integration Challenges
- Parameter synchronization between JavaScript and Python implementations
- Algorithm consistency across studio and production environments
- Performance differences between browser and native implementations
- Version compatibility and parameter migration

## Implementation Notes

### File Structure
```
studio/
  index.html              # Main studio interface
  studio.js               # Core studio logic
  algorithms/
    smoothing.js          # Progressive smoothing implementation
    ascii.js              # ASCII conversion logic
    cleanup.js            # Pattern cleanup algorithms
    compression.js        # RLE compression calculation
  ui/
    sliders.js           # Parameter control interface
    preview.js           # ASCII preview management
    export.js            # Settings and video export
  assets/
    styles.css           # Studio styling
    test-frames/         # Sample frames for testing
```

### Development Priority
The studio is not a nice-to-have feature - it's the critical tool needed to solve the compression optimization problem. Manual parameter tweaking has proven ineffective. The studio approach provides the systematic optimization capability required to achieve production-ready compression ratios.

---

**Current Status:** Core algorithm functional but below compression targets. Studio development is immediate priority to enable systematic optimization rather than continued trial-and-error parameter adjustment.