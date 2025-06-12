"""
OBFUSCII Configuration System

Centralized parameter management for video processing and compression.
Replaces hardcoded values with configurable parameters.
"""

from dataclasses import dataclass, asdict
from typing import Tuple, List, Optional
import json
from pathlib import Path


@dataclass
class SmoothingConfig:
    """Progressive smoothing pipeline parameters"""
    # Bilateral filter parameters
    bilateral_d: int = 15
    bilateral_sigma_color: int = 80
    bilateral_sigma_space: int = 80
    
    # Gaussian blur parameters
    gaussian_kernel_size: int = 9  # Must be odd
    
    # Median filter parameters  
    median_kernel_size: int = 5   # Must be odd
    
    # CLAHE enhancement parameters
    clahe_clip_limit: float = 1.5
    clahe_tile_grid_size: Tuple[int, int] = (8, 8)


@dataclass
class ConversionConfig:
    """ASCII character conversion parameters"""
    # Character sets for ASCII conversion
    ascii_chars: List[str] = None
    dark_ascii_chars: Optional[List[str]] = None
    light_ascii_chars: Optional[List[str]] = None
    
    # Hysteresis threshold for anti-flicker
    hysteresis_threshold: int = 8
    
    # Default resolution parameters
    default_width: int = 120
    aspect_compensation: float = 0.55  # Terminal character aspect ratio compensation
    
    def __post_init__(self):
        if self.ascii_chars is None:
            self.ascii_chars = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
        if self.dark_ascii_chars is None:
            self.dark_ascii_chars = self.ascii_chars
        if self.light_ascii_chars is None:
            self.light_ascii_chars = list(reversed(self.dark_ascii_chars))


@dataclass  
class CleanupConfig:
    """Pattern cleanup pipeline parameters"""
    # Stage enable/disable flags
    enable_isolated_replacement: bool = True
    enable_run_consolidation: bool = True
    enable_temporal_smoothing: bool = True
    enable_spatial_coherence: bool = True
    
    # Cleanup thresholds and parameters
    spatial_coherence_threshold: float = 0.15  # Character frequency threshold
    spatial_uniformity_threshold: float = 0.7   # Neighborhood uniformity threshold
    
    # Facial feature preservation
    preserve_facial_features: bool = True
    facial_feature_chars: List[str] = None
    
    def __post_init__(self):
        if self.facial_feature_chars is None:
            self.facial_feature_chars = ['#', '*', '%', '@']


@dataclass
class CompressionConfig:
    """Compression algorithm parameters"""
    # LZMA compression settings
    lzma_preset: int = 6           # 0 (fast) to 9 (best compression)
    lzma_format: str = "alone"     # "alone" or "xz"
    
    # Compression targets and thresholds
    target_ratio: float = 10.0     # Target compression ratio
    acceptable_ratio: float = 5.0  # Minimum acceptable ratio
    excellent_ratio: float = 10.0  # Excellent performance threshold
    good_ratio: float = 7.0        # Good performance threshold


@dataclass
class OBFUSCIIConfig:
    """Master configuration for OBFUSCII processing"""
    smoothing: SmoothingConfig = None
    conversion: ConversionConfig = None
    cleanup: CleanupConfig = None
    compression: CompressionConfig = None
    
    # Processing metadata
    version: str = "1.0"
    description: str = "OBFUSCII processing configuration"
    
    def __post_init__(self):
        if self.smoothing is None:
            self.smoothing = SmoothingConfig()
        if self.conversion is None:
            self.conversion = ConversionConfig()
        if self.cleanup is None:
            self.cleanup = CleanupConfig()
        if self.compression is None:
            self.compression = CompressionConfig()
    
    @classmethod
    def from_json(cls, json_path: str) -> 'OBFUSCIIConfig':
        """Load configuration from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Create config objects from nested dictionaries
        config = cls()
        
        if 'smoothing' in data:
            config.smoothing = SmoothingConfig(**data['smoothing'])
        if 'conversion' in data:
            config.conversion = ConversionConfig(**data['conversion'])
        if 'cleanup' in data:
            config.cleanup = CleanupConfig(**data['cleanup'])
        if 'compression' in data:
            config.compression = CompressionConfig(**data['compression'])
            
        # Set metadata
        config.version = data.get('version', '1.0')
        config.description = data.get('description', 'OBFUSCII processing configuration')
        
        return config
    
    def to_json(self, json_path: str) -> None:
        """Save configuration to JSON file"""
        data = {
            'version': self.version,
            'description': self.description,
            'smoothing': asdict(self.smoothing),
            'conversion': asdict(self.conversion),
            'cleanup': asdict(self.cleanup),
            'compression': asdict(self.compression)
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def copy(self) -> 'OBFUSCIIConfig':
        """Create deep copy of configuration"""
        return OBFUSCIIConfig(
            smoothing=SmoothingConfig(**asdict(self.smoothing)),
            conversion=ConversionConfig(**asdict(self.conversion)),
            cleanup=CleanupConfig(**asdict(self.cleanup)),
            compression=CompressionConfig(**asdict(self.compression)),
            version=self.version,
            description=self.description
        )


# Default configurations for different use cases
DEFAULT_CONFIG = OBFUSCIIConfig()

# High quality configuration (more detail preservation)
HIGH_QUALITY_CONFIG = OBFUSCIIConfig(
    smoothing=SmoothingConfig(
        bilateral_d=9,           # Less aggressive smoothing
        gaussian_kernel_size=5,   # Smaller blur
        median_kernel_size=3,     # Minimal noise reduction
        clahe_clip_limit=1.0      # Less contrast enhancement
    ),
    cleanup=CleanupConfig(
        enable_isolated_replacement=False,  # Preserve more detail
        spatial_coherence_threshold=0.1,    # More permissive
        spatial_uniformity_threshold=0.8    # Higher uniformity required
    )
)

# High compression configuration (maximum compression ratio)
HIGH_COMPRESSION_CONFIG = OBFUSCIIConfig(
    smoothing=SmoothingConfig(
        bilateral_d=21,           # Aggressive smoothing
        gaussian_kernel_size=13,  # Large blur
        median_kernel_size=7,     # Strong noise reduction
        clahe_clip_limit=2.0      # Strong contrast enhancement
    ),
    cleanup=CleanupConfig(
        enable_isolated_replacement=True,   # Aggressive cleanup
        enable_run_consolidation=True,      # Fix broken runs
        spatial_coherence_threshold=0.2,    # More aggressive
        spatial_uniformity_threshold=0.6    # Lower uniformity threshold
    ),
    compression=CompressionConfig(
        lzma_preset=9,            # Maximum compression
        target_ratio=15.0         # Higher target
    )
)

# Fast processing configuration (speed over quality)
FAST_CONFIG = OBFUSCIIConfig(
    smoothing=SmoothingConfig(
        bilateral_d=9,            # Smaller filter
        gaussian_kernel_size=5,   # Smaller kernel
        median_kernel_size=3,     # Smaller kernel
        clahe_clip_limit=1.5      # Default contrast
    ),
    cleanup=CleanupConfig(
        enable_temporal_smoothing=False,    # Skip expensive temporal processing
        enable_spatial_coherence=False      # Skip expensive spatial processing
    ),
    compression=CompressionConfig(
        lzma_preset=1,            # Fast compression
        target_ratio=5.0          # Lower target for speed
    )
)


def create_default_config_file(output_path: str = "obfuscii_config.json") -> None:
    """Create default configuration file"""
    DEFAULT_CONFIG.to_json(output_path)
    print(f"✅ Created default configuration: {output_path}")


def validate_config(config: OBFUSCIIConfig) -> List[str]:
    """Validate configuration parameters and return list of issues"""
    issues = []
    
    # Validate smoothing parameters
    if config.smoothing.bilateral_d % 2 == 0:
        issues.append("bilateral_d must be odd")
    if config.smoothing.gaussian_kernel_size % 2 == 0:
        issues.append("gaussian_kernel_size must be odd")
    if config.smoothing.median_kernel_size % 2 == 0:
        issues.append("median_kernel_size must be odd")
    if config.smoothing.clahe_clip_limit <= 0:
        issues.append("clahe_clip_limit must be positive")
    
    # Validate conversion parameters
    if config.conversion.hysteresis_threshold < 0:
        issues.append("hysteresis_threshold must be non-negative")
    if config.conversion.default_width < 10:
        issues.append("default_width too small")
    if config.conversion.aspect_compensation <= 0:
        issues.append("aspect_compensation must be positive")
    if not config.conversion.ascii_chars:
        issues.append("ascii_chars cannot be empty")
    if not config.conversion.dark_ascii_chars:
        issues.append("dark_ascii_chars cannot be empty")
    if not config.conversion.light_ascii_chars:
        issues.append("light_ascii_chars cannot be empty")
    if (config.conversion.dark_ascii_chars and config.conversion.light_ascii_chars and
            len(config.conversion.dark_ascii_chars) != len(config.conversion.light_ascii_chars)):
        issues.append("dark_ascii_chars and light_ascii_chars must be same length")
    
    # Validate cleanup parameters
    if not (0 <= config.cleanup.spatial_coherence_threshold <= 1):
        issues.append("spatial_coherence_threshold must be between 0 and 1")
    if not (0 <= config.cleanup.spatial_uniformity_threshold <= 1):
        issues.append("spatial_uniformity_threshold must be between 0 and 1")
    
    # Validate compression parameters
    if not (0 <= config.compression.lzma_preset <= 9):
        issues.append("lzma_preset must be between 0 and 9")
    if config.compression.target_ratio < 1:
        issues.append("target_ratio must be >= 1")
    
    return issues


if __name__ == "__main__":
    # Create example configurations
    configs = {
        "default": DEFAULT_CONFIG,
        "high_quality": HIGH_QUALITY_CONFIG,
        "high_compression": HIGH_COMPRESSION_CONFIG,
        "fast": FAST_CONFIG
    }
    
    for name, config in configs.items():
        config.description = f"OBFUSCII {name.replace('_', ' ')} configuration"
        config.to_json(f"config_{name}.json")
        print(f"Created {name} configuration: config_{name}.json")
    
    # Validate all configurations
    for name, config in configs.items():
        issues = validate_config(config)
        if issues:
            print(f"⚠️  {name} config issues: {issues}")
        else:
            print(f"✅ {name} config validated successfully")