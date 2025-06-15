# OBFUSCII Technical Guide

## Video Processing Pipeline

### Stage 1: Progressive Smoothing
1. **Bilateral Filter** - Preserves edges while removing noise
2. **Gaussian Blur** - Eliminates texture patterns that fragment compression
3. **Median Filter** - Removes salt-and-pepper artifacts
4. **CLAHE Enhancement** - Improves contrast for better character mapping

### Stage 2: ASCII Conversion
- Greyscale mapping to 10-character set
- Hysteresis prevents character flicker between frames
- Aspect ratio compensation for terminal display
- Character boundary sensitivity tuning

### Stage 3: Cleanup Pipeline
- **Isolated Replacement** - Removes lone characters that break RLE runs
- **Run Consolidation** - Fixes A-A-B-A-A patterns
- **Spatial Coherence** - Context-aware noise removal
- **Multiple Passes** - Iterative improvement

### Stage 4: Compression
- Run-Length Encoding of character sequences
- JSON serialization of RLE data
- LZMA compression for final size reduction
- Temporal delta encoding between frames

## Configuration Parameters

### Smoothing Config
```json
{
  "bilateral_d": 9,                    // Filter diameter
  "bilateral_sigma_color": 80,         // Color similarity
  "bilateral_sigma_space": 80,         // Spatial similarity
  "gaussian_kernel_size": 5,           // Blur kernel size
  "median_kernel_size": 3,             // Noise filter size
  "clahe_clip_limit": 1.0,            // Contrast enhancement
  "clahe_tile_grid_size": [8, 8]      // CLAHE grid size
}
```

### Conversion Config
```json
{
  "ascii_chars": [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"],
  "hysteresis_threshold": 8,           // Anti-flicker threshold
  "default_width": 140,                // Target character width
  "aspect_compensation": 0.55          // Terminal aspect adjustment
}
```

### Cleanup Config
```json
{
  "enable_isolated_replacement": true,
  "enable_run_consolidation": true,
  "enable_temporal_smoothing": true,
  "enable_spatial_coherence": true,
  "spatial_coherence_threshold": 0.15,
  "spatial_uniformity_threshold": 0.7,
  "preserve_facial_features": true,
  "facial_feature_chars": ["#", "*", "%", "@"]
}
```

## Compression Analysis

### Target Metrics
- **Excellent:** 10:1+ compression ratio
- **Very Good:** 7:1+ compression ratio  
- **Good:** 5:1+ compression ratio
- **Acceptable:** <5:1 compression ratio

### Factors Affecting Compression
1. **RLE Run Length** - Longer character runs = better compression
2. **Character Variety** - Fewer unique characters = better compression
3. **Temporal Coherence** - Similar frames = better delta compression
4. **Noise Level** - Clean images compress better

### Optimization Strategy
1. Use `studio.html` for real-time parameter tuning
2. Target smooth gradients over fine detail
3. Aggressive cleanup for maximum compression
4. Preview mode for quick iteration

## File Format Specification

### .txv File Structure
```
HEADER:
  Magic: "OBFUSCII" (8 bytes)
  Version: uint32 (4 bytes)
  Metadata Length: uint32 (4 bytes)
  Metadata: JSON string (variable)
  Frame Count: uint32 (4 bytes)

FRAMES:
  For each frame:
    Frame Index: uint32 (4 bytes)
    Frame Type: char (1 byte) ['I' = keyframe, 'P' = delta]
    Padding: 3 bytes
    Timestamp: float64 (8 bytes)
    Raw Size: uint32 (4 bytes)
    Compressed Size: uint32 (4 bytes)
    Compressed Data: LZMA compressed JSON (variable)
```

### Frame Data Format
```json
[
  ["char", runLength],
  [" ", 45],
  [".", 12],
  [":", 8]
]
```

## Performance Optimization

### Memory Usage
- Process frames in chunks for large videos
- Stream compression to avoid memory spikes
- Use generator patterns for frame processing

### Speed Optimization
- OpenCV optimized operations
- Vectorized numpy operations where possible
- Parallel processing for frame-independent operations
- Preview mode for quick validation

### Quality vs Size Tradeoffs
- Higher smoothing = better compression, less detail
- More cleanup passes = better compression, longer processing
- Lower resolution = smaller files, less recognition

## Advanced Usage

### Custom Character Sets
Modify `ascii_chars` in config for different visual styles:
- Minimal: `[" ", ".", "#"]`
- Detailed: `[" ", ".", ":", "-", "=", "+", "*", "#", "%", "@", "█"]`

### Resolution Guidelines
- **Portraits:** 140x80 (optimal for faces)
- **Icons:** 40x40 (minimal recognition)
- **Cinema:** 200x120 (maximum practical detail)

### Temporal Optimization
- Use I-frames every 30-60 frames
- Optimize for loop points in portrait videos
- Consider frame rate reduction for better compression

## Troubleshooting

### Poor Compression
1. Increase smoothing parameters
2. Enable all cleanup options
3. Reduce resolution
4. Check for noisy source material

### Character Flicker
1. Increase hysteresis threshold
2. Add temporal smoothing
3. More aggressive bilateral filtering

### Lost Detail
1. Reduce smoothing intensity
2. Increase resolution
3. Use high-quality config preset
4. Disable aggressive cleanup

### Playback Issues
1. Validate file integrity with `--validate`
2. Check browser LZMA support
3. Verify file corruption