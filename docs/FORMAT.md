# .txv format

The binary container written by `obfuscii/txv.py` and read by `player.js` and `demo.html`.
All integers are little-endian.

## Layout

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | Magic: ASCII `OBFUSCII` |
| 8 | 4 | Format version, `uint32`. Always `1`; readers reject anything else |
| 12 | 4 | Metadata length in bytes, `uint32` |
| 16 | N | Metadata, UTF-8 JSON (see below) |
| 16 + N | 4 | Frame count, `uint32` |
| 20 + N | ... | Frames, back to back |

Each frame is a 24-byte header followed by its compressed data:

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | Frame index, `uint32` (0-based) |
| 4 | 1 | Frame type, ASCII. Always `I`: every frame is independent; no delta frames are written |
| 5 | 3 | Padding (zero) |
| 8 | 8 | Timestamp in seconds, `float64` |
| 16 | 4 | Raw size, `uint32`: `width * height` characters |
| 20 | 4 | Compressed size, `uint32` |
| 24 | M | Compressed data, `M` = compressed size |

## Frame data

Compressed data is LZMA in the legacy "alone" (`.lzma`) container (`lzma_format: "alone"` in the
config). The Python writer also accepts `"xz"`, but the browser players have only ever been used
with "alone".

Decompressed, a frame is a JSON array of `[character, run_length]` pairs covering the frame in
row-major order:

```json
[[" ", 45], [".", 12], [":", 8]]
```

The encoder restarts runs at the start of each row, but decoders just fill `width * height`
characters in order and break rows every `width` characters.

The character set is not stored separately; it is whatever characters appear in the runs. Which
theme a file was made for (`--light` / `--dark`) is not recorded either.

## Metadata

Written by `write_txv_file`. Files made before audio support (June 2025) lack the `audio_*` fields;
readers treat a missing `has_audio` as `false`.

| Key | Type | Notes |
|---|---|---|
| `version` | string | Informational only. Currently `"3.0"`: the compressor's metadata overwrites the writer's `"2.0"`. Readers check the binary version, not this |
| `width`, `height` | int | Frame size in characters |
| `fps` | float | Playback rate |
| `total_frames` | int | Should equal the frame count field; `--validate` checks this |
| `duration_seconds` | float | `total_frames / fps` |
| `compression_algorithm` | string | `"rle-lzma"` |
| `algorithm` | string | `"spatial-rle-lzma"` (duplicate of the above, from the compressor) |
| `created_by` | string | `"OBFUSCII"` |
| `creation_timestamp` | string | ISO 8601, local time |
| `original_file` | string | Source video file name |
| `compression_ratio` | float | Raw characters / compressed bytes |
| `has_audio` | bool | |
| `audio_file` | string | Companion audio file name, e.g. `clip_audio.mp3` |
| `audio_format`, `audio_codec` | string | e.g. `"mp3"` |
| `audio_sample_rate`, `audio_bitrate`, `audio_channels` | int | From ffprobe |
| `audio_duration_seconds` | float | |
| `audio_sync_offset_ms` | int | Added to the audio position on playback. Always written as `0` |

## Audio

Audio is not inside the `.txv`; it is a separate file named by `audio_file`. The CLI export looks
for it next to the `.txv`. The web player requests it relative to the page URL, so in the browser
it only plays when the audio file is served from the same folder as `index.html`.
