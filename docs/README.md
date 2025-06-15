# OBFUSCII Documentation

## Core Documentation

- **[Technical Guide](TECHNICAL_GUIDE.md)** - Detailed technical implementation, configuration parameters, file format specs
- **[Workflows](WORKFLOWS.md)** - Step-by-step guides for common use cases and optimization

## Development Documentation

- **[Parameter Optimization](PARAMETER_OPTIMIZATION.md)** - Algorithm tuning and compression optimization
- **[Video Processing Guide](VIDEO_PROCESSING_GUIDE.md)** - Low-level processing pipeline details
- **[Compression Notes](obfuscii_compression_notes.md)** - Research notes on compression techniques

## Project Management

- **[Issues](issues.md)** - Known issues and TODO items
- **[Checklist](checklist.md)** - Development milestones and testing checklist  
- **[SRS](srs.md)** - Software requirements specification

## Quick Reference

### CLI Usage
```bash
python3 obfuscii.py --help          # Complete command reference
python3 obfuscii.py video.mp4       # Basic conversion
python3 obfuscii.py video.mp4 --preview  # Quick test
```

### Web Tools
- `index.html` - .txv file player
- `studio.html` - Real-time parameter optimization
- `demo.html` - Animated landing page

### Configuration Files
- `light_balanced_high_max.json` (default) - Optimal balance
- `config_high_quality.json` - Maximum fidelity
- `config_high_compression.json` - Smallest files
- `config_default.json` - Basic settings

## Getting Help

1. **CLI Help:** `python3 obfuscii.py --help`
2. **Technical Issues:** Check [issues.md](issues.md)
3. **Optimization:** Use [studio.html](../studio.html) for real-time tuning
4. **Workflows:** Follow guides in [WORKFLOWS.md](WORKFLOWS.md)