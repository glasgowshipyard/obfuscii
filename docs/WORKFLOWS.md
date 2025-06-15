# OBFUSCII Workflows

## Quick Start Workflow

1. **Test with preview:** `python3 obfuscii.py video.mp4 --preview`
2. **Check results:** If quality good, run full conversion
3. **Full conversion:** `python3 obfuscii.py video.mp4`
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

## Web Integration Workflow

### Player Setup
1. **Copy files:** `index.html`, `player.js`, LZMA library
2. **Upload .txv:** Place in same directory
3. **Test locally:** Open in browser
4. **Deploy:** Upload to web server

### Responsive Design
```html
<!-- Responsive ASCII video -->
<pre class="ascii-video" style="
  font-family: monospace;
  font-size: min(1vw, 1vh);
  line-height: 1;
  white-space: pre;
">
  <!-- ASCII content here -->
</pre>
```

### Direct Embedding
```html
<!-- Copy/paste ASCII directly -->
<pre class="ascii-content">
@@@@@@@@@@@@@@
@            @
@   ASCII    @
@   VIDEO    @
@            @
@@@@@@@@@@@@@@
</pre>
```

## Batch Processing Workflow

### Multiple Files
```bash
# Process all MP4 files
for file in *.mp4; do
  python3 obfuscii.py "$file" --config light_balanced_high_max.json
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
4. **Preview mode:** Quick iteration without full processing
5. **Studio tuning:** Real-time parameter adjustment

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
3. **Optimize:** Use studio for parameter tuning if needed
4. **Process:** Full conversion with optimized settings
5. **Deploy:** Integrate into web/app with player
6. **Test:** Verify playback across devices/browsers

### Quality Assurance
- **Compression target:** Aim for 7:1+ ratio
- **File size limits:** <100KB for portraits, <1MB for short clips
- **Visual quality:** Maintain recognition at target display size
- **Cross-platform:** Test on mobile and desktop
- **Performance:** Ensure smooth playback at target FPS