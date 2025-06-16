# OBFUSCII Theme System

## Overview

OBFUSCII supports automatic light/dark theme generation through character inversion. This allows ASCII videos to work perfectly on any background without manual adjustment.

## How Themes Work

### Character Mapping

**Light Theme (default):**
```
Brightness:  Light ────────────────► Dark
Characters: [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
Use case:   Light backgrounds, white websites, documentation
```

**Dark Theme (--dark):**
```
Brightness:  Dark ─────────────────► Light  
Characters: ['@', '%', '#', '*', '+', '=', '-', ':', '.', ' ']
Use case:   Dark backgrounds, dark mode, terminals
```

### Transparency Effect

The space character `' '` creates transparency by becoming invisible on any background:
- **Light theme:** Spaces are transparent, `@` is darkest
- **Dark theme:** `@` becomes spaces (transparent), spaces become `@` (darkest)

## Usage

### Single Theme
```bash
# Light theme (default)
python3 obfuscii.py portrait.mp4
python3 obfuscii.py portrait.mp4 --light

# Dark theme
python3 obfuscii.py portrait.mp4 --dark
```

### Dual Theme Generation
```bash
# Generate both themes
python3 obfuscii.py portrait.mp4 --both

# Creates:
# portrait_light.txv  - For light backgrounds
# portrait_dark.txv   - For dark backgrounds
```

## Web Integration

### Static Theme Selection
```html
<!-- Light theme version -->
<div class="light-bg">
  <pre class="ascii-video">
    <!-- Load portrait_light.txv content -->
  </pre>
</div>

<!-- Dark theme version -->
<div class="dark-bg">
  <pre class="ascii-video">
    <!-- Load portrait_dark.txv content -->
  </pre>
</div>
```

### Responsive Theme Switching
```html
<style>
  .ascii-container {
    font-family: monospace;
    line-height: 1;
    white-space: pre;
  }
  
  /* Light mode */
  @media (prefers-color-scheme: light) {
    .ascii-container {
      color: #000;
      background: #fff;
    }
  }
  
  /* Dark mode */
  @media (prefers-color-scheme: dark) {
    .ascii-container {
      color: #fff;
      background: #000;
    }
  }
</style>

<div class="ascii-container">
  <!-- Use appropriate theme .txv based on user preference -->
</div>
```

### JavaScript Theme Loading
```javascript
// Detect user theme preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const themeFile = prefersDark ? 'portrait_dark.txv' : 'portrait_light.txv';

// Load appropriate theme
loadTxvFile(themeFile);
```

## Best Practices

### Theme Selection Guidelines

**Use Light Theme When:**
- Target website has light/white backgrounds
- Content will be embedded in documentation
- Printing or PDF export is important
- Traditional web design aesthetic

**Use Dark Theme When:**
- Target website has dark backgrounds
- Terminal/console integration
- Modern dark mode interfaces
- High contrast requirements

**Use Both Themes When:**
- Building responsive websites
- Supporting user theme preferences
- Maximum compatibility needed
- Professional web applications

### Optimization Tips

1. **Test Both Themes:** Always preview both versions to ensure quality
2. **Consider Context:** Different themes may require different compression settings
3. **File Naming:** Use clear suffixes (`_light`, `_dark`) for organization
4. **Performance:** Both themes have identical compression ratios
5. **Accessibility:** Both themes maintain the same visual recognition

## Technical Implementation

### Character Inversion Algorithm
```python
def invert_ascii_chars(chars):
    """Invert ASCII character set for dark backgrounds"""
    return list(reversed(chars))

# Example:
light_chars = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
dark_chars = invert_ascii_chars(light_chars)
# Result: ['@', '%', '#', '*', '+', '=', '-', ':', '.', ' ']
```

### Configuration Integration
```json
{
  "conversion": {
    "ascii_chars": [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"],
    "theme": "light"
  }
}
```

The theme system modifies the `ascii_chars` array at runtime without changing the core configuration files.

## Troubleshooting

### Common Issues

**Characters appear inverted:**
- Check theme selection matches your background
- Verify CSS color settings don't conflict

**Poor contrast:**
- Try opposite theme
- Adjust background/foreground colors in CSS
- Consider custom character set in config

**Inconsistent appearance:**
- Ensure consistent font family (monospace)
- Verify line-height: 1 in CSS
- Check white-space: pre setting

### Quality Comparison
Both themes maintain identical:
- Compression ratios
- Visual recognition quality
- Frame rates and playback
- File structure and metadata

Only the character mapping changes, ensuring consistent quality across themes.