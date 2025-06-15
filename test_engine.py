#!/usr/bin/env python3
"""
OBFUSCII Test Engine

Automated parameter sweep for optimization via LLM visual evaluation.
Extracts frame, applies parameter combinations, generates ASCII outputs with compression metrics.
"""

import cv2
import json
import zipfile
import itertools
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import argparse

from obfuscii.vid import load_video, process_video_to_compressed
from obfuscii.config import OBFUSCIIConfig, SmoothingConfig, ConversionConfig, CleanupConfig, CompressionConfig


class ParameterTestEngine:
    """
    Test engine for OBFUSCII parameter optimization
    
    Generates strategic parameter sweep with visual ASCII outputs
    and compression metrics for LLM-based evaluation.
    
    Uses SMART GRID DESIGN to keep combinations manageable (~50-100 total)
    """
    
    def __init__(self, output_dir: str = "parameter_tests", clean: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Clean existing results if requested
        if clean:
            self.clean_existing_results()
        
        # STRATEGIC PARAMETER GRID - carefully chosen for max impact with min combinations
        # Focus on parameters that most affect compression ratio and visual quality
        self.parameter_variants = {
            # SMOOTHING IMPACT: These dramatically affect compression by reducing noise
            'smoothing_level': [
                ('light', {'bilateral_d': 9, 'gaussian_kernel_size': 5, 'median_kernel_size': 3, 'clahe_clip_limit': 1.0}),
                ('medium', {'bilateral_d': 15, 'gaussian_kernel_size': 9, 'median_kernel_size': 5, 'clahe_clip_limit': 1.5}),
                ('heavy', {'bilateral_d': 21, 'gaussian_kernel_size': 13, 'median_kernel_size': 7, 'clahe_clip_limit': 2.0})
            ],
            
            # CLEANUP IMPACT: These are critical for compression ratio
            'cleanup_aggressiveness': [
                ('conservative', {'enable_isolated_replacement': False, 'enable_run_consolidation': True, 'enable_spatial_coherence': False}),
                ('balanced', {'enable_isolated_replacement': True, 'enable_run_consolidation': True, 'enable_spatial_coherence': True}), 
                ('aggressive', {'enable_isolated_replacement': True, 'enable_run_consolidation': True, 'enable_spatial_coherence': True, 
                               'spatial_coherence_threshold': 0.05, 'spatial_uniformity_threshold': 0.9})
            ],
            
            # RESOLUTION IMPACT: Affects both quality and compression
            'resolution': [
                ('low', 100),
                ('medium', 120),
                ('high', 140)
            ],
            
            # COMPRESSION IMPACT: Different LZMA settings
            'compression_level': [
                ('fast', 1),
                ('balanced', 6), 
                ('max', 9)
            ]
        }
        
        self.results = []
        
    def generate_test_configurations(self) -> List[Tuple[str, OBFUSCIIConfig]]:
        """Generate strategic test configurations with manageable combinations"""
        
        configs = []
        
        # Generate all combinations from the strategic grid
        smoothing_variants = self.parameter_variants['smoothing_level']
        cleanup_variants = self.parameter_variants['cleanup_aggressiveness'] 
        resolution_variants = self.parameter_variants['resolution']
        compression_variants = self.parameter_variants['compression_level']
        
        for smooth_name, smooth_params in smoothing_variants:
            for cleanup_name, cleanup_params in cleanup_variants:
                for res_name, res_width in resolution_variants:
                    for comp_name, comp_preset in compression_variants:
                        
                        # Create configuration name
                        config_name = f"{smooth_name}_{cleanup_name}_{res_name}_{comp_name}"
                        
                        # Build configuration object
                        config = OBFUSCIIConfig()
                        
                        # Apply smoothing parameters
                        for param, value in smooth_params.items():
                            setattr(config.smoothing, param, value)
                        
                        # Apply cleanup parameters
                        for param, value in cleanup_params.items():
                            setattr(config.cleanup, param, value)
                        
                        # Apply resolution
                        config.conversion.default_width = res_width
                        
                        # Apply compression level
                        config.compression.lzma_preset = comp_preset
                        
                        configs.append((config_name, config))
        
        print(f"🔬 Generated {len(configs)} strategic configurations")
        print(f"📊 Grid: {len(smoothing_variants)} smoothing × {len(cleanup_variants)} cleanup × {len(resolution_variants)} resolution × {len(compression_variants)} compression")
        
        return configs
    
    def extract_test_frame(self, video_path: str, frame_number: int = 30) -> Tuple[Any, float]:
        """Extract single frame for testing"""
        print(f"📹 Extracting frame {frame_number} from {video_path}")
        
        cap, fps, frame_count = load_video(video_path)
        
        # Seek to specific frame  
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(frame_number, frame_count - 1))
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError(f"Could not extract frame {frame_number}")
            
        return frame, fps
    
    def process_single_frame(self, frame: Any, config: OBFUSCIIConfig, fps: float, test_name: str) -> Tuple[str, Dict[str, Any]]:
        """Process single frame with specific configuration"""
        
        # Create temporary video with just this frame
        temp_frames = []
        
        # Process frame using refactored pipeline
        from obfuscii.vid import frame_to_ascii_with_hysteresis, cleanup_ascii_patterns
        from obfuscii.moc import compress_video_rle
        
        # Step 1: Convert frame to ASCII
        ascii_frame = frame_to_ascii_with_hysteresis(frame, config=config)
        temp_frames = [ascii_frame]
        
        # Step 2: Apply cleanup pipeline
        cleaned_frames = cleanup_ascii_patterns(temp_frames, verbose=False, config=config)
        
        # Step 3: Compress for metrics
        compressed_result = compress_video_rle(cleaned_frames, fps=fps, verbose=False, config=config.compression)
        
        # Step 4: Generate ASCII string
        ascii_string = '\n'.join(''.join(row) for row in cleaned_frames[0])
        
        # Extract metrics
        stats = compressed_result.stats
        metrics = {
            'compression_ratio': f"{stats.overall_ratio:.2f}:1",
            'file_size_kb': f"{stats.compressed_size_kb:.2f}",
            'raw_size_chars': stats.total_raw_size,
            'compressed_size_bytes': stats.total_compressed_size,
            'width': compressed_result.width,
            'height': compressed_result.height,
            'config_summary': {
                'smoothing_level': f"b{config.smoothing.bilateral_d}_g{config.smoothing.gaussian_kernel_size}_m{config.smoothing.median_kernel_size}",
                'cleanup_flags': f"I{config.cleanup.enable_isolated_replacement}_R{config.cleanup.enable_run_consolidation}_S{config.cleanup.enable_spatial_coherence}",
                'resolution': config.conversion.default_width,
                'compression_preset': config.compression.lzma_preset
            }
        }
        
        return ascii_string, metrics
    
    def save_test_result(self, test_name: str, ascii_string: str, metrics: Dict[str, Any], 
                        config: OBFUSCIIConfig, test_id: str) -> None:
        """Save test result with comprehensive metadata"""
        
        filename = f"{test_id}_{test_name}.txt"
        filepath = self.output_dir / filename
        
        # Create detailed metadata
        metadata = {
            "test_info": {
                "test_id": test_id,
                "config_name": test_name,
                "generated": datetime.now().isoformat()
            },
            "metrics": metrics,
            "configuration": {
                "smoothing": {
                    "bilateral_d": config.smoothing.bilateral_d,
                    "gaussian_kernel": config.smoothing.gaussian_kernel_size,
                    "median_kernel": config.smoothing.median_kernel_size,
                    "clahe_clip_limit": config.smoothing.clahe_clip_limit
                },
                "cleanup": {
                    "isolated_replacement": config.cleanup.enable_isolated_replacement,
                    "run_consolidation": config.cleanup.enable_run_consolidation,
                    "spatial_coherence": config.cleanup.enable_spatial_coherence,
                    "spatial_threshold": config.cleanup.spatial_coherence_threshold
                },
                "conversion": {
                    "width": config.conversion.default_width,
                    "hysteresis_threshold": config.conversion.hysteresis_threshold
                },
                "compression": {
                    "lzma_preset": config.compression.lzma_preset,
                    "target_ratio": config.compression.target_ratio
                }
            }
        }
        
        # Write file with metadata header
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# OBFUSCII Parameter Test Result\n")
            f.write("# " + "="*60 + "\n")
            f.write(f"# Configuration: {test_name}\n")
            f.write(f"# Compression: {metrics['compression_ratio']}\n")
            f.write(f"# File Size: {metrics['file_size_kb']} KB\n")
            f.write(f"# Resolution: {metrics['width']}x{metrics['height']}\n")
            f.write("# " + "="*60 + "\n")
            f.write(f"# Full metadata: {json.dumps(metadata, indent=2)}\n")
            f.write("# " + "="*60 + "\n\n")
            f.write(ascii_string)
        
        # Store for summary
        self.results.append({
            'test_name': test_name,
            'filename': filename,
            'compression_ratio': float(metrics['compression_ratio'].split(':')[0]),
            'file_size_kb': float(metrics['file_size_kb']),
            'resolution': metrics['width'],
            'config': metadata['configuration']
        })
        
        print(f"💾 {test_name}: {metrics['compression_ratio']} ({metrics['file_size_kb']} KB)")
    
    def run_parameter_sweep(self, video_path: str, frame_number: int = 30) -> str:
        """Run complete parameter sweep with strategic configurations"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_id = f"obfuscii_test_{timestamp}"
        
        print(f"🚀 Starting OBFUSCII parameter sweep: {test_id}")
        print(f"📁 Output directory: {self.output_dir}")
        
        # Extract test frame
        frame, fps = self.extract_test_frame(video_path, frame_number)
        
        # Generate strategic test configurations
        configs = self.generate_test_configurations()
        
        print(f"\n⚙️  Processing {len(configs)} configurations...")
        
        # Process each configuration
        for i, (config_name, config) in enumerate(configs):
            try:
                print(f"🔧 [{i+1:2d}/{len(configs)}] {config_name}")
                
                # Process frame with this configuration
                ascii_string, metrics = self.process_single_frame(frame, config, fps, config_name)
                
                # Save result
                self.save_test_result(config_name, ascii_string, metrics, config, test_id)
                
            except Exception as e:
                print(f"❌ Error processing {config_name}: {e}")
                continue
        
        # Create results package
        zip_path = self.create_results_package(test_id, video_path, frame_number)
        
        print(f"\n✅ Parameter sweep complete!")
        print(f"📦 Results package: {zip_path}")
        print(f"📊 Generated {len(self.results)} test files")
        
        # Show quick summary
        self.print_quick_summary()
        
        return str(zip_path)
    
    def print_quick_summary(self) -> None:
        """Print quick analysis of results"""
        if not self.results:
            return
            
        # Find best configurations
        best_compression = max(self.results, key=lambda x: x['compression_ratio'])
        best_quality = min(self.results, key=lambda x: x['file_size_kb'])  # Smaller file = better compression
        
        print(f"\n📈 QUICK ANALYSIS:")
        print(f"🏆 Best compression: {best_compression['test_name']} ({best_compression['compression_ratio']:.1f}:1)")
        print(f"🎯 Smallest file: {best_quality['test_name']} ({best_quality['file_size_kb']:.1f} KB)")
        
        # Compression range
        ratios = [r['compression_ratio'] for r in self.results]
        print(f"📊 Compression range: {min(ratios):.1f}:1 to {max(ratios):.1f}:1")
    
    def create_results_package(self, test_id: str, video_path: str, frame_number: int) -> Path:
        """Create comprehensive results package for LLM evaluation"""
        
        zip_path = self.output_dir / f"{test_id}_results.zip"
        
        # Create comprehensive summary
        summary = {
            "test_info": {
                "test_id": test_id,
                "source_video": str(video_path),
                "frame_number": frame_number,
                "generated": datetime.now().isoformat(),
                "total_configurations": len(self.results),
                "strategy": "Strategic parameter grid for optimal compression vs quality balance"
            },
            "parameter_strategy": {
                "smoothing_levels": ["light (preserve detail)", "medium (balanced)", "heavy (max compression)"],
                "cleanup_levels": ["conservative (preserve detail)", "balanced (moderate cleanup)", "aggressive (max compression)"],
                "resolutions": ["low (100px)", "medium (120px)", "high (140px)"],
                "compression_levels": ["fast (preset 1)", "balanced (preset 6)", "max (preset 9)"]
            },
            "results": self.results,
            "analysis": {
                "best_compression": max(self.results, key=lambda x: x['compression_ratio']) if self.results else None,
                "smallest_file": min(self.results, key=lambda x: x['file_size_kb']) if self.results else None,
                "compression_stats": {
                    "min": min(r['compression_ratio'] for r in self.results) if self.results else 0,
                    "max": max(r['compression_ratio'] for r in self.results) if self.results else 0,
                    "avg": sum(r['compression_ratio'] for r in self.results) / len(self.results) if self.results else 0
                }
            }
        }
        
        # Save comprehensive summary
        summary_path = self.output_dir / f"{test_id}_analysis.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Create LLM evaluation guide
        guide_path = self.output_dir / f"{test_id}_LLM_EVALUATION_GUIDE.txt"
        with open(guide_path, 'w') as f:
            f.write("OBFUSCII PARAMETER OPTIMIZATION - LLM EVALUATION GUIDE\n")
            f.write("="*65 + "\n\n")
            f.write("🎯 TASK: Analyze ASCII outputs to recommend optimal parameters\n\n")
            
            f.write("📊 EVALUATION CRITERIA (in order of importance):\n")
            f.write("1. COMPRESSION RATIO: Higher is better (target 7:1+, excellent 10:1+)\n")
            f.write("2. VISUAL QUALITY: Recognizable features, clean edges, minimal noise\n")
            f.write("3. DETAIL PRESERVATION: Important facial features, text, edges visible\n")
            f.write("4. ARTIFACT REDUCTION: Minimal salt-and-pepper noise, smooth gradients\n\n")
            
            f.write("🔧 PARAMETER GUIDE:\n")
            f.write("• SMOOTHING: light=detail, medium=balanced, heavy=compression\n")
            f.write("• CLEANUP: conservative=detail, balanced=moderate, aggressive=compression\n")
            f.write("• RESOLUTION: low=speed, medium=balanced, high=quality\n")
            f.write("• COMPRESSION: fast=speed, balanced=moderate, max=size\n\n")
            
            f.write("🎨 VISUAL ASSESSMENT TIPS:\n")
            f.write("• Look for recognizable shapes and features\n")
            f.write("• Check for excessive noise (random scattered characters)\n")
            f.write("• Evaluate edge smoothness and gradient quality\n")
            f.write("• Consider if main subject is clearly distinguishable\n\n")
            
            f.write(f"📈 TEST RESULTS SUMMARY:\n")
            f.write(f"Total configurations tested: {len(self.results)}\n")
            if self.results:
                ratios = [r['compression_ratio'] for r in self.results]
                f.write(f"Compression range: {min(ratios):.1f}:1 to {max(ratios):.1f}:1\n")
                f.write(f"Best performing config: {summary['analysis']['best_compression']['test_name']}\n")
            
            f.write(f"\n🤖 RECOMMENDATION FORMAT:\n")
            f.write("Please provide:\n")
            f.write("1. Top 3 recommended configurations (with rationale)\n")
            f.write("2. Trade-offs analysis (compression vs quality)\n")
            f.write("3. Optimal settings for different use cases:\n")
            f.write("   - Maximum compression (web delivery)\n")
            f.write("   - Balanced quality (general use)\n")
            f.write("   - Maximum detail (high quality)\n")
        
        # Create zip package
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all test result files
            for txt_file in self.output_dir.glob(f"{test_id}_*.txt"):
                zipf.write(txt_file, txt_file.name)
            
            # Add analysis and guide
            zipf.write(summary_path, summary_path.name)
            zipf.write(guide_path, guide_path.name)
        
        # Cleanup individual files
        for txt_file in self.output_dir.glob(f"{test_id}_*.txt"):
            txt_file.unlink()
        summary_path.unlink()
        guide_path.unlink()
        
        return zip_path
    
    def clean_existing_results(self) -> None:
        """Clean existing test results from output directory"""
        cleaned_count = 0
        
        # Remove .txt files (test results)
        for txt_file in self.output_dir.glob("obfuscii_test_*.txt"):
            txt_file.unlink()
            cleaned_count += 1
        
        # Remove .zip files (result packages)
        for zip_file in self.output_dir.glob("obfuscii_test_*.zip"):
            zip_file.unlink()
            cleaned_count += 1
            
        # Remove .json files (analysis results)
        for json_file in self.output_dir.glob("obfuscii_test_*.json"):
            json_file.unlink()
            cleaned_count += 1
        
        if cleaned_count > 0:
            print(f"🧹 Cleaned {cleaned_count} existing test files")


def main():
    parser = argparse.ArgumentParser(
        description='OBFUSCII Parameter Test Engine - Strategic parameter sweep for LLM evaluation',
        epilog='Generates ~80 strategic test configurations covering key parameter combinations'
    )
    parser.add_argument('video', help='Input video file')
    parser.add_argument('--frame', type=int, default=30, help='Frame number to extract (default: 30)')
    parser.add_argument('--output', default='parameter_tests', help='Output directory (default: parameter_tests)')
    parser.add_argument('--clean', action='store_true', help='Clean existing test results before running')
    
    args = parser.parse_args()
    
    # Create test engine
    engine = ParameterTestEngine(args.output, clean=args.clean)
    
    # Run parameter sweep
    try:
        zip_path = engine.run_parameter_sweep(args.video, args.frame)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Upload {zip_path} to an LLM with vision capabilities (Claude, GPT-4V)")
        print(f"2. Ask: 'Analyze these ASCII outputs and recommend optimal OBFUSCII parameters'")
        print(f"3. Request specific recommendations for compression vs quality trade-offs")
        print(f"4. Use recommended settings to update your OBFUSCII configuration")
        
    except Exception as e:
        print(f"❌ Test engine failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())