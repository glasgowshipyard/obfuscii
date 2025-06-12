#!/usr/bin/env python3
"""
Example usage of the refactored OBFUSCII system with configurable parameters
"""

from obfuscii.config import OBFUSCIIConfig, HIGH_COMPRESSION_CONFIG, HIGH_QUALITY_CONFIG

def demonstrate_configurations():
    """Show how to use different configurations"""
    
    print("🔧 OBFUSCII Configuration Examples")
    print("="*50)
    
    # Example 1: Default configuration
    default_config = OBFUSCIIConfig()
    print(f"📄 Default Config:")
    print(f"   Smoothing: bilateral_d={default_config.smoothing.bilateral_d}, gaussian={default_config.smoothing.gaussian_kernel_size}")
    print(f"   Resolution: {default_config.conversion.default_width}px wide")
    print(f"   Compression: LZMA preset {default_config.compression.lzma_preset}")
    print(f"   Target ratio: {default_config.compression.target_ratio}:1")
    
    print()
    
    # Example 2: High compression configuration
    print(f"🗜️  High Compression Config:")
    print(f"   Smoothing: bilateral_d={HIGH_COMPRESSION_CONFIG.smoothing.bilateral_d}, gaussian={HIGH_COMPRESSION_CONFIG.smoothing.gaussian_kernel_size}")
    print(f"   Cleanup: isolated={HIGH_COMPRESSION_CONFIG.cleanup.enable_isolated_replacement}, spatial={HIGH_COMPRESSION_CONFIG.cleanup.enable_spatial_coherence}")
    print(f"   Compression: LZMA preset {HIGH_COMPRESSION_CONFIG.compression.lzma_preset}")
    print(f"   Target ratio: {HIGH_COMPRESSION_CONFIG.compression.target_ratio}:1")
    
    print()
    
    # Example 3: High quality configuration
    print(f"🎨 High Quality Config:")
    print(f"   Smoothing: bilateral_d={HIGH_QUALITY_CONFIG.smoothing.bilateral_d}, gaussian={HIGH_QUALITY_CONFIG.smoothing.gaussian_kernel_size}")
    print(f"   Cleanup: isolated={HIGH_QUALITY_CONFIG.cleanup.enable_isolated_replacement}, spatial={HIGH_QUALITY_CONFIG.cleanup.enable_spatial_coherence}")
    print(f"   Thresholds: coherence={HIGH_QUALITY_CONFIG.cleanup.spatial_coherence_threshold}")
    
    print()
    
    # Example 4: Custom configuration
    print(f"⚙️  Custom Config Example:")
    custom_config = OBFUSCIIConfig()
    
    # Customize for very aggressive compression
    custom_config.smoothing.bilateral_d = 25
    custom_config.smoothing.gaussian_kernel_size = 15
    custom_config.cleanup.spatial_coherence_threshold = 0.05  # Very aggressive
    custom_config.cleanup.spatial_uniformity_threshold = 0.9
    custom_config.compression.lzma_preset = 9
    custom_config.compression.target_ratio = 15.0
    
    print(f"   Ultra-aggressive smoothing and cleanup for maximum compression")
    print(f"   Expected ratio: {custom_config.compression.target_ratio}:1")
    
    # Save examples
    default_config.to_json("config_default.json")
    HIGH_COMPRESSION_CONFIG.to_json("config_high_compression.json") 
    HIGH_QUALITY_CONFIG.to_json("config_high_quality.json")
    custom_config.to_json("config_custom_ultra.json")
    
    print()
    print("✅ Example configurations saved:")
    print("   • config_default.json")
    print("   • config_high_compression.json")
    print("   • config_high_quality.json") 
    print("   • config_custom_ultra.json")

def show_test_engine_usage():
    """Show how to use the test engine"""
    
    print()
    print("🧪 Test Engine Usage")
    print("="*30)
    print()
    print("# Run parameter sweep on a video:")
    print("python3 test_engine.py your_video.mp4")
    print()
    print("# Use specific frame and output directory:")
    print("python3 test_engine.py your_video.mp4 --frame 60 --output my_tests")
    print()
    print("# The engine will generate ~81 configurations:")
    print("# 3 smoothing levels × 3 cleanup levels × 3 resolutions × 3 compression levels")
    print()
    print("📦 Output: ZIP file with:")
    print("   • 81 .txt files with ASCII art + metadata")
    print("   • analysis.json with compression statistics")
    print("   • LLM_EVALUATION_GUIDE.txt with instructions")
    print()
    print("🤖 Upload the ZIP to an LLM and ask:")
    print('   "Analyze these ASCII outputs and recommend optimal OBFUSCII parameters"')

if __name__ == "__main__":
    demonstrate_configurations()
    show_test_engine_usage()