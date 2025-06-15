
# OBFUSCII COMPRESSION BENCHMARK — JUNE 2025

---

## 📊 CURRENT BEST CONFIG

**File**: `light_balanced_high_max.txt`  
**ZQ Visual Score**: 7.7  
**Compression Ratio**: 4.02:1  
**Settings**:
- **Smoothing**: light
- **Cleanup**: balanced
- **Resolution**: high
- **Compression Profile**: max

This config produces highly legible ASCII with minimal speckle, long run-lengths, and strong visual coherence. It is the current benchmark for compression and clarity balance.

---

## ⚖️ COMPRESSION CONTEXT

| Format         | Typical Compression | Notes                                  |
|----------------|---------------------|----------------------------------------|
| PNG (lossless) | 1.5–2.5:1           | Lossless raster image                  |
| JPEG (85%)     | 4–8:1               | Lossy, psychovisual optimised          |
| H.264 (video)  | 50–200:1            | Delta + temporal prediction            |
| ASCII-RLE      | 3.5–4.0:1           | Text-based, plaintext, RLE-compliant   |
| **OBFUSCII**   | **4.02:1**          | Plaintext frame encoding (txv format)  |

---

## 🧨 STRATEGIES TO EXCEED 5.0:1

### 1. Glyph Palette Quantisation
- Reduce active glyphs from 16 → 5–6 (`@`, `#`, `+`, `-`, `.`)
- Goal: Reduce variability → increase run lengths

### 2. Posterisation
- Collapse luminance into 2–4 buckets
- Hard bands = uniform ASCII segments = longer RLE
- Risk: May introduce banding artifacts

### 3. Edge-Preserving Blur
- Replace Gaussian with bilateral or `cv2.edgePreservingFilter`
- Retains contour while suppressing micro-noise

### 4. Block Redundancy Normalisation
- Identify visually identical blocks with differing glyphs
- Post-process to unify → enhance gzip/RLE performance

### 5. Frame-to-Frame Delta Compression
- Store only diffs or identical lines across time
- Like inter-frame compression (e.g., MPEG I-frames + B-frames)

---

## 🔍 NEXT STEPS

- Test posterisation + bilateral smoothing
- Benchmark different glyph ramp sizes
- Measure downstream gzip gains after `.txv` RLE
- Prototype delta encoding between frames

---

## 🧠 AUTHOR’S NOTE

4.02:1 on plaintext visual data is rare. This work sets a precedent for glyph-based video compression formats that are:
- Terminal-compatible
- Searchable
- Compressible
- Weirdly beautiful

`ZQ-2025` config remains the benchmark until dethroned.

