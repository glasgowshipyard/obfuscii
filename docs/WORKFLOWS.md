# OBFUSCII Workflows

## Quick Start Workflow

1. **Test with preview:** `python3 obfuscii.py video.mp4 --preview`
2. **Check results:** If quality good, run full conversion
3. **Choose theme:** 
   - Light backgrounds: `python3 obfuscii.py video.mp4` (default)
   - Dark backgrounds: `python3 obfuscii.py video.mp4 --dark`
   - Both versions: `python3 obfuscii.py video.mp4 --both`
4. **Play result:** Answer 'y' to play prompt or `python3 obfuscii.py output.txv`

## Portrait Creation Workflow

### Source Video Requirements
- **Duration:** 3-5 seconds for natural loops
- **Resolution:** 720p+ for best quality
- **Content:** Face centered, minimal background
- **Motion:** Subtle - looking left/right, blinking
- **Lighting:** Even, avoid harsh shadows

### Optimal Settings
```bash
python3 obfuscii.py portrait.mp4 \
  --resolution 140x80 \
  --config light_balanced_high_max.json \
  --verbose
```

### Quality Check
1. **Preview first:** Use `--preview` for quick validation
2. **Check compression:** Target 7:1+ ratio in verbose output
3. **Visual quality:** Ensure face recognition in ASCII output
4. **File size:** Aim for <100KB for web use

## Logo Animation Workflow

### Source Preparation
- **Clean background:** Solid color or remove background
- **High contrast:** Logo should be clearly defined
- **Simple motion:** Rotation, scaling, or breathing effect
- **Loop-friendly:** Start and end frames should match

### Processing
```bash
python3 obfuscii.py logo.mp4 \
  --resolution 80x40 \
  --config config_high_compression.json
```

### Integration
1. Export to web with `index.html`
2. Copy ASCII text for direct embedding
3. Use CSS scaling for responsive design

## Cinema Conversion Workflow

### Large File Handling
```bash
# Process in segments for memory efficiency
python3 obfuscii.py movie.mp4 \
  --resolution 120x60 \
  --config config_high_compression.json \
  --verbose
```

### Quality vs Size Balance
- **Compression priority:** Use high compression config
- **Resolution:** 120x60 balances recognition and size
- **Preview sections:** Test critical scenes first

## Optimization Workflow

### Using Studio for Parameter Tuning
1. **Open:** `studio.html` in browser
2. **Load:** Sample frame from your video
3. **Adjust:** Real-time parameter tuning
4. **Export:** Save optimized config JSON
5. **Apply:** Use custom config for full conversion

### Manual Parameter Tuning
1. **Start conservative:** Use default config
2. **Increase smoothing:** If compression poor
3. **Adjust cleanup:** For noise issues
4. **Test resolution:** Find sweet spot for content

### Compression Optimization
```bash
# Test different configs quickly
python3 obfuscii.py video.mp4 --preview --config config_high_quality.json
python3 obfuscii.py video.mp4 --preview --config light_balanced_high_max.json  
python3 obfuscii.py video.mp4 --preview --config config_high_compression.json
```

## Theme Selection Workflow

### Choosing the Right Theme

**Light Theme (default):**
- Best for: Light backgrounds, white/cream websites, documentation
- Characters: Space (transparent) → @ (darkest)
- Usage: `python3 obfuscii.py video.mp4` or `python3 obfuscii.py video.mp4 --light`

**Dark Theme:**
- Best for: Dark backgrounds, dark mode websites, terminals
- Characters: @ (darkest) → Space (transparent) 
- Usage: `python3 obfuscii.py video.mp4 --dark`

**Both Themes:**
- Best for: Responsive websites supporting light/dark modes
- Generates: `video_light.txv` and `video_dark.txv`
- Usage: `python3 obfuscii.py video.mp4 --both`

### Theme Testing
```bash
# Test both themes quickly
python3 obfuscii.py video.mp4 --both --preview
python3 obfuscii.py video_light.txv  # Test light version
python3 obfuscii.py video_dark.txv   # Test dark version
```

## Web Integration Workflow

### Player Setup
1. **Copy files:** `index.html`, `player.js`, LZMA library
2. **Upload .txv:** Place in same directory (choose appropriate theme)
3. **Test locally:** Open in browser
4. **Deploy:** Upload to web server

### Theme-Aware Responsive Design
```html
<!-- Light theme ASCII video -->
<pre class="ascii-video light-theme" style="
  font-family: monospace;
  font-size: min(1vw, 1vh);
  line-height: 1;
  white-space: pre;
  color: #000;
  background: #fff;
">
  <!-- Light theme ASCII content -->
</pre>

<!-- Dark theme ASCII video -->
<pre class="ascii-video dark-theme" style="
  font-family: monospace;
  font-size: min(1vw, 1vh);
  line-height: 1;
  white-space: pre;
  color: #fff;
  background: #000;
">
  <!-- Dark theme ASCII content -->
</pre>
```

### Direct Embedding with Theme Support
```html
<!-- Responsive theme switching -->
<style>
  @media (prefers-color-scheme: light) {
    .ascii-content { color: #000; background: #fff; }
  }
  @media (prefers-color-scheme: dark) {
    .ascii-content { color: #fff; background: #000; }
  }
</style>

<pre class="ascii-content">
<!-- Use appropriate theme .txv content here -->
</pre>
```

## Batch Processing Workflow

### Multiple Files
```bash
# Process all MP4 files with both themes
for file in *.mp4; do
  python3 obfuscii.py "$file" --both --config light_balanced_high_max.json
done
```

### Quality Control
```bash
# Validate all outputs
for file in *.txv; do
  echo "Checking $file:"
  python3 obfuscii.py "$file" --validate
  python3 obfuscii.py "$file" --info
done
```

## Troubleshooting Workflow

### Poor Results Checklist
1. **Source quality:** Check input video resolution and clarity
2. **Config choice:** Try different presets
3. **Resolution:** Test higher/lower resolutions
4. **Theme selection:** Try opposite theme for better contrast
5. **Preview mode:** Quick iteration without full processing
6. **Studio tuning:** Real-time parameter adjustment

### Theme Issues
```bash
# If ASCII appears too dark/light
python3 obfuscii.py video.mp4 --dark   # Try opposite theme
python3 obfuscii.py video.mp4 --both   # Generate both for comparison

# Test in different contexts
python3 obfuscii.py light_version.txv  # Test on terminal (usually dark)
python3 obfuscii.py dark_version.txv   # Test on white background
```

### File Issues
```bash
# Diagnose problems
python3 obfuscii.py problem.txv --info      # Check metadata
python3 obfuscii.py problem.txv --validate  # Check integrity
python3 obfuscii.py source.mp4 --verbose    # Debug processing
```

### Performance Issues
1. **Memory:** Reduce resolution for large videos
2. **Speed:** Use preview mode for testing
3. **Quality:** Balance smoothing vs processing time

## Production Workflow

### Content Creation Pipeline
1. **Shoot/Edit:** Create source video with optimization in mind
2. **Preview:** Quick quality check with OBFUSCII
3. **Choose theme:** Select appropriate theme for target context
4. **Optimize:** Use studio for parameter tuning if needed
5. **Process:** Full conversion with optimized settings
6. **Deploy:** Integrate into web/app with appropriate theme
7. **Test:** Verify playback across devices/browsers and color schemes

### Quality Assurance
- **Compression target:** Aim for 7:1+ ratio
- **File size limits:** <100KB for portraits, <1MB for short clips
- **Visual quality:** Maintain recognition at target display size
- **Theme compatibility:** Test on both light and dark backgrounds
- **Cross-platform:** Test on mobile and desktop
- **Performance:** Ensure smooth playback at target FPS