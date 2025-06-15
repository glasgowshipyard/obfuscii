# OBFUSCII Video Processing Guide

**Complete workflow for processing video files with the parametrized OBFUSCII system**

---

## 🎬 Quick Start

### Basic Video Processing
```bash
# Process entire video with default settings
python3 obfuscii.py input.mp4

# Process with high compression preset
python3 obfuscii.py input.mp4 --config config_high_compression.json

# Process with custom frame range
python3 obfuscii.py input.mp4 --start-frame 100 --end-frame 200
```

### Output Formats
- **`.txv`** - Compressed ASCII video format
- **`.txt`** - Individual ASCII frames 
- **`.json`** - Metadata and configuration

---

## ⚙️ Configuration-Based Processing

Since parametrization is complete, all processing now uses the centralized configuration system:

### 1. Choose a Configuration

#### Pre-built Configurations
```python
from obfuscii.config import (
    OBFUSCIIConfig,           # Balanced default
    HIGH_QUALITY_CONFIG,      # Maximum detail preservation  
    HIGH_COMPRESSION_CONFIG   # Maximum compression ratio
)
```

#### Custom Configuration
```python
custom_config = OBFUSCIIConfig()
custom_config.smoothing.bilateral_d = 25              # Heavy smoothing
custom_config.cleanup.spatial_coherence_threshold = 0.05  # Aggressive cleanup
custom_config.compression.lzma_preset = 9             # Maximum compression
custom_config.conversion.default_width = 140          # High resolution
```

### 2. Process Video
```python
from obfuscii.vid import process_video_to_compressed

# Process with chosen configuration
compressed_video = process_video_to_compressed(
    "input.mp4", 
    config=custom_config
)

# Save compressed video
with open("output.txv", "wb") as f:
    f.write(compressed_video.compressed_data)
```

---

## 🎯 Optimization Workflow

### Step 1: Parameter Sweep Testing
```bash
# Generate 81 test configurations from a single frame
python3 test_engine.py your_video.mp4 --frame 30

# Output: obfuscii_test_YYYYMMDD_HHMMSS_results.zip
```

### Step 2: LLM-Based Analysis  
1. Upload the ZIP file to Claude, GPT-4V, or similar vision model
2. Use this proven prompt (based on GPT-4V analysis that achieved 4.02:1):
```
Analyze these ASCII outputs for optimal OBFUSCII parameters.

Evaluate each configuration using the ZQ Visual Score system:
1. Compression ratio (current benchmark: 4.02:1 from light_balanced_high_max)
2. Visual legibility and minimal speckle
3. Run-length consistency and visual coherence
4. Detail preservation vs noise reduction balance

The benchmark configuration achieved:
- ZQ Visual Score: 7.7/10
- Settings: light smoothing + balanced cleanup + high resolution + max compression
- Key strengths: "highly legible ASCII with minimal speckle, long run-lengths"

Recommend configurations that can exceed 4.02:1 while maintaining visual quality above 7.0.
Consider glyph palette reduction and posterization techniques.
```

### Step 3: Apply Recommendations
```python
# Implement the proven GPT-4V optimized configuration
zq_benchmark_config = OBFUSCIIConfig()

# ZQ-2025 benchmark settings (4.02:1 compression, 7.7 visual score)
zq_benchmark_config.smoothing.bilateral_d = 9           # Light smoothing
zq_benchmark_config.smoothing.gaussian_kernel_size = 5
zq_benchmark_config.smoothing.median_kernel_size = 3
zq_benchmark_config.cleanup.enable_isolated_replacement = True    # Balanced cleanup
zq_benchmark_config.cleanup.enable_spatial_coherence = True
zq_benchmark_config.conversion.default_width = 140               # High resolution
zq_benchmark_config.compression.lzma_preset = 9                  # Max compression

# Save the benchmark configuration
zq_benchmark_config.to_json("config_zq_benchmark.json")

# Process full video with proven settings
result = process_video_to_compressed("video.mp4", config=zq_benchmark_config)
print(f"Compression ratio: {result.compression_ratio:.2f}:1")
print(f"Target: 4.02:1+ (ZQ benchmark)")
```

---

## 📊 Performance Targets

### Current Benchmarks (GPT-4V Analysis)
- **Best Configuration**: `light_balanced_high_max` (ZQ Visual Score: 7.7)
- **Peak Compression**: 4.02:1 - *"highly legible ASCII with minimal speckle, long run-lengths, and strong visual coherence"*
- **Optimal Settings**: Light smoothing + Balanced cleanup + High resolution + Max compression

### Compression Context
| Format | Compression Ratio | Notes |
|--------|------------------|-------|
| PNG (lossless) | 1.5–2.5:1 | Lossless raster image |
| JPEG (85%) | 4–8:1 | Lossy, psychovisual optimized |
| H.264 (video) | 50–200:1 | Delta + temporal prediction |
| ASCII-RLE | 3.5–4.0:1 | Text-based, plaintext, RLE-compliant |
| **OBFUSCII** | **4.02:1** | **Plaintext frame encoding (txv format)** |

### Quality vs Compression Trade-offs

| Config Type | Compression Ratio | Visual Quality | Use Case |
|-------------|------------------|----------------|----------|
| High Quality | 2.5-3.5:1 | Excellent | Archival, detailed analysis |
| Balanced (GPT Recommended) | 3.5-4.02:1 | Good | General purpose, web use |
| High Compression | 4.5-7:1+ | Acceptable | Bandwidth-limited, storage |

### GPT-4V Validated Best Practice
**Configuration**: `light_balanced_high_max`
- **Smoothing**: Light (preserves detail while reducing noise)
- **Cleanup**: Balanced (optimal speckle reduction without over-processing)  
- **Resolution**: High (140px width for detail preservation)
- **Compression**: Max (LZMA preset 9 for best ratio)

---

## 🔧 Processing Pipeline

### 1. Frame Extraction
- Extract frames at specified intervals
- Apply resolution scaling based on `conversion.default_width`
- Maintain aspect ratio with `aspect_compensation`

### 2. Progressive Smoothing
```python
# Configurable smoothing pipeline
bilateral_filter(d=config.smoothing.bilateral_d)
gaussian_blur(kernel=config.smoothing.gaussian_kernel_size) 
median_filter(kernel=config.smoothing.median_kernel_size)
clahe_enhancement(clip_limit=config.smoothing.clahe_clip_limit)
```

### 3. ASCII Conversion
- Convert luminance to ASCII using `conversion.ascii_chars`
- Apply hysteresis filtering with `conversion.hysteresis_threshold`
- Handle temporal consistency across frames

### 4. Pattern Cleanup
- Remove isolated characters (`cleanup.enable_isolated_replacement`)
- Consolidate broken runs (`cleanup.enable_run_consolidation`)
- Apply spatial coherence filtering (`cleanup.enable_spatial_coherence`)
- Preserve important features (`cleanup.preserve_facial_features`)

### 5. Compression
- Apply RLE encoding to ASCII frames
- LZMA compression with configurable preset (`compression.lzma_preset`)
- Generate `.txv` format with metadata

---

## 📁 File Structure

### Input
```
video.mp4              # Source video file
config.json            # Optional configuration file
```

### Processing
```
temp/
├── frame_0001.jpg     # Extracted frames
├── frame_0002.jpg
└── ...
```

### Output
```
video.txv              # Compressed ASCII video
video_metadata.json    # Processing metadata
video_config.json      # Configuration used
frames/                # Individual ASCII frames (optional)
├── frame_0001.txt
├── frame_0002.txt
└── ...
```

---

## 🧨 Advanced Optimization Strategies

### GPT-4V Identified Breakthrough Techniques

Based on compression analysis, these strategies can potentially exceed 5.0:1 compression:

#### 1. Glyph Palette Quantization
```python
# Reduce ASCII character set for longer run-lengths
minimal_chars = [' ', '.', ':', '+', '#', '@']  # 6 chars vs default 10
config.conversion.ascii_chars = minimal_chars
```
**Goal**: Reduce variability → increase run lengths → better RLE compression

#### 2. Posterization
```python
# Collapse luminance into discrete bands
def apply_posterization(frame, levels=3):
    # Convert to 2-4 luminance buckets for uniform ASCII regions
    quantized = np.floor(frame / (256 / levels)) * (256 / levels)
    return quantized.astype(np.uint8)
```
**Goal**: Hard luminance bands = uniform ASCII segments = longer RLE  
**Risk**: May introduce banding artifacts

#### 3. Edge-Preserving Smoothing
```python
# Replace standard Gaussian with edge-preserving filter
config.smoothing.use_edge_preserving = True
config.smoothing.edge_preserving_flags = cv2.RECURS_FILTER
config.smoothing.edge_preserving_sigma_s = 50
config.smoothing.edge_preserving_sigma_r = 0.4
```
**Goal**: Retain contours while suppressing micro-noise

#### 4. Block Redundancy Normalization
```python
# Identify visually identical blocks with different characters
def normalize_similar_blocks(ascii_frame, similarity_threshold=0.9):
    # Post-process to unify similar patterns
    # Enhances gzip/RLE performance
    pass
```
**Goal**: Unify equivalent visual patterns for better compression

#### 5. Frame-to-Frame Delta Compression
```python
# Store only differences between frames (like MPEG I-frames + B-frames)
def encode_frame_delta(current_frame, previous_frame):
    # Store unchanged lines as references
    # Only encode actual changes
    pass
```
**Goal**: Temporal redundancy reduction for video sequences

### Implementation Priority
1. **Glyph Palette Quantization** - Easiest to implement, immediate gains
2. **Edge-Preserving Smoothing** - Already supported by OpenCV
3. **Posterization** - Simple preprocessing step
4. **Block Redundancy** - Requires pattern analysis
5. **Frame Delta** - Most complex but highest potential gain

---

## 🚀 Advanced Techniques

### Batch Processing
```python
import glob
from obfuscii.vid import process_video_to_compressed

# Process all videos in directory
for video_file in glob.glob("*.mp4"):
    print(f"Processing {video_file}...")
    
    result = process_video_to_compressed(
        video_file, 
        config=HIGH_COMPRESSION_CONFIG
    )
    
    output_file = video_file.replace(".mp4", ".txv")
    with open(output_file, "wb") as f:
        f.write(result.compressed_data)
```

### Quality Assessment
```python
# Evaluate compression performance
if result.compression_ratio >= config.compression.excellent_ratio:
    print(f"🏆 Excellent compression: {result.compression_ratio:.2f}:1")
elif result.compression_ratio >= config.compression.good_ratio:
    print(f"✅ Good compression: {result.compression_ratio:.2f}:1")
elif result.compression_ratio >= config.compression.acceptable_ratio:
    print(f"⚠️  Acceptable compression: {result.compression_ratio:.2f}:1")
else:
    print(f"❌ Poor compression: {result.compression_ratio:.2f}:1")
```

### Memory Management
```python
# For large videos, process in chunks
def process_large_video(video_path, chunk_size=100):
    total_frames = get_frame_count(video_path)
    
    for start_frame in range(0, total_frames, chunk_size):
        end_frame = min(start_frame + chunk_size, total_frames)
        
        chunk_result = process_video_to_compressed(
            video_path,
            start_frame=start_frame,
            end_frame=end_frame,
            config=HIGH_COMPRESSION_CONFIG
        )
        
        # Save chunk
        chunk_file = f"video_chunk_{start_frame:06d}.txv"
        with open(chunk_file, "wb") as f:
            f.write(chunk_result.compressed_data)
```

---

## 🎨 Use Cases

### Web Delivery
- **Config**: `HIGH_COMPRESSION_CONFIG`
- **Target**: 5:1+ compression ratio
- **Priority**: File size over visual fidelity

### Archival Storage
- **Config**: `HIGH_QUALITY_CONFIG` 
- **Target**: Maximum detail preservation
- **Priority**: Visual quality over file size

### Real-time Processing
- **Config**: Custom with fast LZMA preset
- **Target**: Processing speed
- **Priority**: Low latency over compression

### Artistic/Creative
- **Config**: Custom ASCII character sets
- **Target**: Aesthetic appeal
- **Priority**: Visual style over efficiency

---

## 🔍 Troubleshooting

### Common Issues

#### Poor Compression Ratios
- Try `HIGH_COMPRESSION_CONFIG`
- Increase smoothing parameters
- Enable aggressive cleanup options
- Use higher LZMA preset (8-9)

#### Loss of Detail
- Use `HIGH_QUALITY_CONFIG`
- Reduce smoothing intensity
- Disable aggressive cleanup
- Increase resolution (`default_width`)

#### Processing Too Slow
- Lower LZMA preset (1-3)
- Reduce resolution
- Process fewer frames
- Use frame skipping

#### Memory Issues
- Process in smaller chunks
- Reduce resolution
- Lower frame count
- Clear temporary files

---

## 📈 Next Steps (GPT-4V Roadmap)

### Immediate Actions
1. **Implement ZQ-2025 benchmark** - Use the proven 4.02:1 configuration
2. **Test glyph palette quantization** - Reduce character set from 10 → 6 chars
3. **Experiment with posterization** - 2-4 luminance buckets for uniform regions

### Research Priorities  
1. **Test posterization + bilateral smoothing** combination
2. **Benchmark different glyph ramp sizes** (5, 6, 8, 10, 12 characters)
3. **Measure downstream gzip gains** after .txv RLE encoding
4. **Prototype delta encoding** between frames for video sequences

### Long-term Goals
- **Exceed 5.0:1 compression** while maintaining 7.0+ visual score
- **Implement frame-to-frame delta compression** for temporal redundancy
- **Create specialized configs** for different content types (faces, landscapes, text)
- **Establish new benchmarks** beyond the current ZQ-2025 record

### Community Impact
*"4.02:1 on plaintext visual data is rare. This work sets a precedent for glyph-based video compression formats that are terminal-compatible, searchable, compressible, and weirdly beautiful."*

The ZQ-2025 configuration remains the benchmark until dethroned.

---

*With parametrization complete, OBFUSCII now offers systematic, reproducible video processing with LLM-optimized parameter selection for maximum compression and quality.*