# Status

_Last reviewed 2026-10-06. This page replaces the old checklist, issues, SRS and compression notes._

## What works

Checked by running it:

- **Video → `.txv`** (`python3 obfuscii.py video.mp4`), from any directory. About 7 frames/s at the default 140-character width.
- **Audio extraction** (`--with-audio`), writing `<name>_audio.mp3` next to the `.txv`.
- **MP4 export** (`--export reels` etc.) with audio. About 7 s for 60 frames at 1080×1920 on 4 cores.
- **`--info`, `--validate`, terminal playback**.
- **Web player** (`index.html` + `player.js`), **live webcam mode** (`live.html`) and **demo** (`demo.html`),
  deployed at https://obfuscii.pages.dev (live mode at `/live`).
- **Tests**: `python -m pytest tests` (round trip, validate, hysteresis, CLI conversion, export).

## Known issues

**Output**
- **Theme polarity is inverted.** The pipeline maps black pixels to a space and white to `@`
  (`obfuscii/vid.py`, `char_index = pixel * len // 256`). On a light page `@` is the darkest glyph,
  so the default light theme renders a negative; `--dark` reverses the set and is also a negative on
  a dark page. Live mode maps the other way round, so it and the CLI disagree.

**Compression**
- Every frame is run-length encoded, turned into JSON and LZMA-compressed on its own, so nothing
  is shared between frames. Re-compressing the same frames as plain text:

  | File | Now | LZMA, 30-frame chunks | gzip, 30-frame chunks | Brotli, 30-frame chunks |
  |---|---|---|---|---|
  | `test_light.txv` (198 frames) | 6.1:1 | 17.7:1 | 10.5:1 | 18.3:1 |
  | `green.txv` (2,415 frames) | 10.5:1 | 70.2:1 | 37.7:1 | 84.1:1 |

**Web player** (`player.js`)
- Pause then play restarts the audio from the beginning.
- Video frames drive the audio clock instead of following it; drift is corrected only when it passes 0.5 s.
- Audio is requested relative to the page, so it never plays for a file opened with the file picker.
- Logs to the console for every frame while loading; a frame that fails to decode is silently
  replaced with a sine-wave pattern.

**Studio** (`studio.html`)
- "Process Full Video" is a stub that shows an alert.
- The compression ratio it shows is an estimate (`jsonSize * 0.3`), not a measurement.
- Exported settings use key names the CLI doesn't read, so loading them gives the defaults.
- It has the hysteresis bug the Python side had (`studio.html`, `boundaryPixel`), and its bilateral slider does nothing.

**Live mode**
- `--live` serves the whole repo folder on port 8000 to the local network.
- Phones need the HTTPS site; browsers block the camera on `http://<LAN IP>`.
- It uses its own simple mapping (no smoothing, hysteresis or cleanup), so it doesn't preview what the codec produces.

**CLI**
- Conversion is per-pixel Python loops, hence about 7 frames/s.
- After converting, it asks "Play result now?" and exits with an error if there is no terminal input.
- Export's worker pool prints a `fork()` DeprecationWarning on Python 3.12+; output is fine.

**Repo**
- No `requirements.txt` (`pip install opencv-python numpy Pillow`; ffmpeg for audio and export) and no LICENSE.
- `test_static_moc.py` needs a file that isn't in the repo, so run `pytest tests`, not bare `pytest`.
- Root clutter: six config JSONs (`test_config.json` duplicates `config_default.json`), `parameter_tests/`
  (83 files plus a zip of the same files), and `green.txv` / `test_dark.txv`, which no page uses.
- Version numbers disagree: binary format `1`, metadata `"3.0"`, README "v2.0", configs `"1.0"`.

## Tools in the repo

- `test_engine.py`: parameter sweep from one frame of a video, written to `parameter_tests/` for visual
  comparison. The June 2025 run picked `light_balanced_high_max.json`, the current default.
- `test_image.py`: compares character sets on a still image.
- `test_example.py`: prints the built-in config presets.

## What's next

Everything people see already runs in the browser (player, live mode, demo, Studio), and the CLI's
jobs all have browser equivalents. The plan is to make the browser the product:

1. **Format v2.** Store plain-text frames in 30-frame LZMA chunks (3–7× smaller, and the player
   already loads LZMA-JS). Record the theme and character set in the metadata. Embed the audio so a
   `.txv` is one self-contained file. Readers keep accepting v1.
2. **Studio becomes the converter.** Drop in a video, tune with a live preview, convert every frame,
   download the `.txv`. Port the real pipeline (resize, hysteresis, temporal smoothing, cleanup) and
   settle the theme polarity there.
3. **MP4 export in the browser** with WebCodecs plus an MP4 muxer, replacing Pillow and ffmpeg.
4. **Embeddable player**: one script tag or web component for putting a `.txv` on a site, with the
   theme following `prefers-color-scheme`.
5. **Retire the Python CLI** once the browser version matches its output, or keep a thin batch mode
   if long videos need it.
