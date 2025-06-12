# OBFUSCII Parameter Optimization System

**From Hardcoded to AI-Optimized: A Complete Refactoring for LLM-Based Parameter Tuning**

---

## 🎯 Overview

This document describes the complete refactoring of OBFUSCII from hardcoded parameters to a fully configurable system with an intelligent test engine for LLM-based parameter optimization.

### The Problem
OBFUSCII had **12+ critical hardcoded parameters** scattered throughout the codebase that directly impact compression ratio and visual quality. Manual optimization was time-consuming and suboptimal.

### The Solution
1. **Centralized Configuration System** - All parameters in structured, validated configs
2. **Refactored Core Functions** - Accept configuration objects instead of hardcoded values
3. **Smart Test Engine** - Generate strategic parameter combinations for LLM evaluation
4. **LLM-Optimized Workflow** - Upload test results to vision-capable LLMs for analysis

---

## 🏗️ Architecture

### Configuration Hierarchy
```
OBFUSCIIConfig
├── SmoothingConfig      # Progressive smoothing pipeline
├── ConversionConfig     # ASCII character conversion  
├── CleanupConfig        # Pattern cleanup pipeline
└── CompressionConfig    # LZMA compression settings
```

### File Structure
```
obfuscii/
├── config.py           # Configuration system
├── vid.py              # Refactored video processing
├── moc.py              # Refactored compression
test_engine.py          # Parameter sweep engine
test_example.py         # Usage examples
PARAMETER_OPTIMIZATION.md  # This document
```

---

## ⚙️ Configuration System

### Core Configuration Classes

#### `SmoothingConfig`
Progressive smoothing pipeline parameters for noise reduction and compression optimization.

```python
@dataclass
class SmoothingConfig:
    bilateral_d: int = 15                    # Bilateral filter diameter
    bilateral_sigma_color: int = 80          # Color sigma
    bilateral_sigma_space: int = 80          # Space sigma
    gaussian_kernel_size: int = 9            # Gaussian blur kernel (odd)
    median_kernel_size: int = 5              # Median filter kernel (odd)
    clahe_clip_limit: float = 1.5            # Contrast enhancement
    clahe_tile_grid_size: Tuple[int, int] = (8, 8)  # CLAHE tile size
```

#### `ConversionConfig`
ASCII character conversion and resolution parameters.

```python
@dataclass
class ConversionConfig:
    ascii_chars: List[str] = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
    hysteresis_threshold: int = 8            # Anti-flicker threshold
    default_width: int = 120                 # Default ASCII width
    aspect_compensation: float = 0.55        # Terminal aspect ratio
```

#### `CleanupConfig`
Pattern cleanup pipeline for compression optimization.

```python
@dataclass
class CleanupConfig:
    enable_isolated_replacement: bool = True      # Remove lone characters
    enable_run_consolidation: bool = True         # Fix A-A-B-A-A patterns
    enable_temporal_smoothing: bool = True        # Reduce frame flicker
    enable_spatial_coherence: bool = True         # Context-aware cleanup
    spatial_coherence_threshold: float = 0.15     # Character frequency
    spatial_uniformity_threshold: float = 0.7     # Neighborhood uniformity
    preserve_facial_features: bool = True         # Preserve important chars
```

#### `CompressionConfig`
LZMA compression and performance targets.

```python
@dataclass
class CompressionConfig:
    lzma_preset: int = 6                    # 0 (fast) to 9 (best compression)
    lzma_format: str = "alone"              # "alone" or "xz"
    target_ratio: float = 10.0              # Target compression ratio
    acceptable_ratio: float = 5.0           # Minimum acceptable ratio
    excellent_ratio: float = 10.0           # Excellence threshold
    good_ratio: float = 7.0                 # Good performance threshold
```

### Pre-built Configurations

#### Default Configuration
Balanced settings for general use.
```python
DEFAULT_CONFIG = OBFUSCIIConfig()
```

#### High Quality Configuration
Preserves maximum detail with minimal cleanup.
```python
HIGH_QUALITY_CONFIG = OBFUSCIIConfig(
    smoothing=SmoothingConfig(
        bilateral_d=9,           # Less aggressive smoothing
        gaussian_kernel_size=5,   # Smaller blur
        median_kernel_size=3,     # Minimal noise reduction
        clahe_clip_limit=1.0      # Less contrast enhancement
    ),
    cleanup=CleanupConfig(
        enable_isolated_replacement=False,  # Preserve detail
        spatial_coherence_threshold=0.1,    # More permissive
        spatial_uniformity_threshold=0.8    # Higher uniformity required
    )
)
```

#### High Compression Configuration
Maximum compression ratio with aggressive cleanup.
```python
HIGH_COMPRESSION_CONFIG = OBFUSCIIConfig(
    smoothing=SmoothingConfig(
        bilateral_d=21,           # Aggressive smoothing
        gaussian_kernel_size=13,  # Large blur
        median_kernel_size=7,     # Strong noise reduction
        clahe_clip_limit=2.0      # Strong contrast enhancement
    ),
    cleanup=CleanupConfig(
        spatial_coherence_threshold=0.2,    # More aggressive cleanup
        spatial_uniformity_threshold=0.6    # Lower uniformity threshold
    ),
    compression=CompressionConfig(
        lzma_preset=9,            # Maximum compression
        target_ratio=15.0         # Higher target
    )
)
```

---

## 🔄 Refactored Core Functions

### Progressive Smoothing
```python
def progressive_smoothing(frame: np.ndarray, config: Optional[SmoothingConfig] = None) -> np.ndarray:
    """Apply configurable smoothing pipeline"""
    if config is None:
        config = SmoothingConfig()
    
    # Use config parameters instead of hardcoded values
    smooth1 = cv2.bilateralFilter(frame, config.bilateral_d, 
                                 config.bilateral_sigma_color, 
                                 config.bilateral_sigma_space)
    # ... rest of pipeline
```

### ASCII Conversion
```python
def frame_to_ascii_with_hysteresis(frame: np.ndarray, 
                                  config: Optional[OBFUSCIIConfig] = None) -> List[List[str]]:
    """Convert frame using configurable parameters"""
    if config is None:
        config = OBFUSCIIConfig()
    
    # Use configured character set and thresholds
    ascii_chars = config.conversion.ascii_chars
    hysteresis_threshold = config.conversion.hysteresis_threshold
    # ... conversion logic
```

### Cleanup Pipeline
```python
def cleanup_ascii_patterns(ascii_frames: List[List[List[str]]], 
                         config: Optional[OBFUSCIIConfig] = None) -> List[List[List[str]]]:
    """Apply configurable cleanup pipeline"""
    if config is None:
        config = OBFUSCIIConfig()
    
    # Use config flags and thresholds
    if config.cleanup.enable_isolated_replacement:
        # Apply cleanup with configured thresholds
        threshold = config.cleanup.spatial_coherence_threshold
    # ... cleanup stages
```

### Compression
```python
def compress_video_rle(ascii_frames: List[List[List[str]]], 
                      config: Optional[CompressionConfig] = None) -> CompressedVideo:
    """Compress using configurable LZMA settings"""
    if config is None:
        config = CompressionConfig()
    
    # Use configured compression settings
    lzma_format = lzma.FORMAT_ALONE if config.lzma_format == "alone" else lzma.FORMAT_XZ
    compressed_data = lzma.compress(json_data, format=lzma_format, preset=config.lzma_preset)
    # ... compression logic
```

---

## 🧪 Smart Test Engine

### Strategic Parameter Grid
The test engine uses a **4-dimensional strategic grid** to generate manageable combinations:

```
3 Smoothing Levels × 3 Cleanup Levels × 3 Resolutions × 3 Compression Levels = 81 Tests
```

#### Parameter Dimensions

**Smoothing Levels:**
- `light`: Preserve detail (bilateral_d=9, gaussian=5, median=3, clahe=1.0)
- `medium`: Balanced (bilateral_d=15, gaussian=9, median=5, clahe=1.5)  
- `heavy`: Max compression (bilateral_d=21, gaussian=13, median=7, clahe=2.0)

**Cleanup Aggressiveness:**
- `conservative`: Preserve detail (isolated=False, spatial=False)
- `balanced`: Moderate cleanup (isolated=True, spatial=True, default thresholds)
- `aggressive`: Max compression (spatial_threshold=0.05, uniformity=0.9)

**Resolution:**
- `low`: 100px width (fast processing)
- `medium`: 120px width (balanced)
- `high`: 140px width (detail preservation)

**Compression Level:**
- `fast`: LZMA preset 1 (speed)
- `balanced`: LZMA preset 6 (balance)
- `max`: LZMA preset 9 (maximum compression)

### Test Engine Output

Each test generates:
1. **ASCII art file** with comprehensive metadata header
2. **Compression metrics** (ratio, file size, resolution)
3. **Configuration summary** for easy identification

Final package includes:
- **81 .txt files** with ASCII art + metadata
- **analysis.json** with statistics and rankings
- **LLM_EVALUATION_GUIDE.txt** with evaluation instructions

---

## 🤖 LLM Optimization Workflow

### Step 1: Generate Test Data
```bash
# Extract frame and generate parameter sweep
python3 test_engine.py your_video.mp4 --frame 30

# Output: obfuscii_test_YYYYMMDD_HHMMSS_results.zip
```

### Step 2: LLM Analysis
Upload the ZIP file to a vision-capable LLM (Claude, GPT-4V) with this prompt:

```
Analyze these ASCII outputs and recommend optimal OBFUSCII parameters.

Evaluate each configuration for:
1. Compression ratio (higher is better, target 7:1+)
2. Visual quality (recognizable features, clean edges)
3. Detail preservation (important features visible)
4. Artifact reduction (minimal noise)

Provide:
1. Top 3 recommended configurations with rationale
2. Trade-offs analysis (compression vs quality)
3. Optimal settings for different use cases:
   - Maximum compression (web delivery)
   - Balanced quality (general use)  
   - Maximum detail (high quality)
```

### Step 3: Apply Recommendations
Create configuration based on LLM recommendations:

```python
# Example: LLM recommends medium smoothing + aggressive cleanup + high compression
optimized_config = OBFUSCIIConfig()
optimized_config.smoothing.bilateral_d = 15
optimized_config.smoothing.gaussian_kernel_size = 9
optimized_config.cleanup.enable_isolated_replacement = True
optimized_config.cleanup.spatial_coherence_threshold = 0.05
optimized_config.compression.lzma_preset = 9

# Save for reuse
optimized_config.to_json("config_llm_optimized.json")
```

---

## 📊 Usage Examples

### Basic Configuration Usage
```python
from obfuscii.config import OBFUSCIIConfig, HIGH_COMPRESSION_CONFIG
from obfuscii.vid import process_video_to_compressed

# Use pre-built configuration
compressed_video = process_video_to_compressed(
    "input.mp4", 
    config=HIGH_COMPRESSION_CONFIG
)

# Custom configuration
custom_config = OBFUSCIIConfig()
custom_config.compression.lzma_preset = 9
custom_config.smoothing.bilateral_d = 25

compressed_video = process_video_to_compressed(
    "input.mp4", 
    config=custom_config
)
```

### Parameter Sweep Testing
```bash
# Basic test on default frame (30)
python3 test_engine.py video.mp4

# Custom frame and output directory
python3 test_engine.py video.mp4 --frame 60 --output my_tests

# Results in ZIP file ready for LLM upload
```

### Configuration Management
```python
# Load configuration from JSON
config = OBFUSCIIConfig.from_json("optimized_config.json")

# Modify and save
config.compression.target_ratio = 12.0
config.to_json("updated_config.json")

# Validate configuration
from obfuscii.config import validate_config
issues = validate_config(config)
if issues:
    print("Configuration issues:", issues)
```

---

## 🎯 Benefits

### Before Refactoring
- ❌ **12+ hardcoded parameters** scattered across files
- ❌ **Manual optimization** required code changes
- ❌ **No systematic testing** approach
- ❌ **Difficult to reproduce** optimal settings

### After Refactoring
- ✅ **Centralized configuration** system with validation
- ✅ **JSON-based parameter** management
- ✅ **Strategic test engine** generates optimal combinations
- ✅ **LLM-optimized workflow** for intelligent parameter selection
- ✅ **Reproducible configurations** for different use cases
- ✅ **Easy parameter sharing** and version control

---

## 🚀 Next Steps

1. **Run parameter sweeps** on your target content
2. **Upload results to LLMs** for analysis and recommendations
3. **Create optimized configurations** for different use cases
4. **Share configurations** with the community
5. **Iterate and refine** based on real-world results

---

## 📁 File Reference

### Core Files
- `obfuscii/config.py` - Configuration system and pre-built configs
- `obfuscii/vid.py` - Refactored video processing with config support
- `obfuscii/moc.py` - Refactored compression with config support

### Tools
- `test_engine.py` - Parameter sweep test engine
- `test_example.py` - Configuration usage examples

### Output Examples
- `config_*.json` - Various configuration presets
- `obfuscii_test_*_results.zip` - Test engine output packages

---

*This refactoring transforms OBFUSCII from a hardcoded system into an AI-optimizable parameter space, enabling systematic optimization through LLM-based visual analysis.*