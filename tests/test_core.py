"""Regression tests for the core OBFUSCII pipeline

Run from the repo root with: python -m pytest tests
"""

import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from obfuscii import moc, vid
from obfuscii.config import OBFUSCIIConfig
from obfuscii.txv import write_txv_file, read_txv_file, decompress_txv_frame, validate_txv_file

CHARS = OBFUSCIIConfig().conversion.ascii_chars


def make_frames(count=5, width=24, height=10):
    """Deterministic ASCII frames with runs and per-frame variation"""
    return [[[CHARS[(x // 3 + y + i) % len(CHARS)] for x in range(width)] for y in range(height)]
            for i in range(count)]


@pytest.fixture
def txv_path(tmp_path):
    frames = make_frames()
    compressed = moc.compress_video_rle(frames, fps=10.0)
    path = tmp_path / "sample.txv"
    write_txv_file(compressed, str(path), "sample.mp4")
    return path, frames


def test_round_trip(txv_path):
    path, frames = txv_path
    loaded = read_txv_file(str(path))
    assert [decompress_txv_frame(loaded, i) for i in range(len(frames))] == frames


def test_validate_accepts_fresh_and_committed_files(txv_path):
    path, _ = txv_path
    assert validate_txv_file(str(path), verbose=False)
    assert validate_txv_file(str(REPO_ROOT / "test_light.txv"), verbose=False)


def test_hysteresis_holds_previous_char_near_boundary():
    config = OBFUSCIIConfig()
    threshold = config.conversion.hysteresis_threshold
    n = len(CHARS)

    # Find a grey level whose smoothed value lands just above a character boundary
    for grey in range(256):
        frame = np.full((48, 64, 3), grey, np.uint8)
        value = int(vid.progressive_smoothing(frame, config.smoothing)[0, 0])
        index = value * n // 256
        if index > 0 and value - index * 256 / n < threshold:
            break
    else:
        pytest.skip("no grey level lands near a boundary after smoothing")

    fresh = vid.frame_to_ascii_with_hysteresis(frame, 16, 8, None, config)
    assert {c for row in fresh for c in row} == {CHARS[index]}

    prev = [[CHARS[index - 1]] * 16 for _ in range(8)]
    held = vid.frame_to_ascii_with_hysteresis(frame, 16, 8, prev, config)
    assert {c for row in held for c in row} == {CHARS[index - 1]}


def test_terminal_sample_indices_fit_and_keep_aspect():
    rows, cols = vid.terminal_sample_indices(136, 140, 160, 59)
    assert len(rows) <= 59 and len(cols) <= 160
    assert max(rows) < 136 and max(cols) < 140
    assert abs(len(cols) / len(rows) - 140 / 136) < 0.05


def test_cli_converts_with_default_config_outside_repo(tmp_path):
    video = tmp_path / "clip.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10, (64, 48))
    for i in range(6):
        frame = np.zeros((48, 64, 3), np.uint8)
        frame[:, : 10 * (i + 1)] = 255
        writer.write(frame)
    writer.release()

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "obfuscii.py"), "clip.avi",
         "--preview", "--force", "--resolution", "32x12"],
        cwd=tmp_path, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert validate_txv_file(str(tmp_path / "clip.txv"), verbose=False)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_export_produces_mp4(txv_path, tmp_path):
    from obfuscii.export import export_video_from_txv

    path, frames = txv_path
    output = tmp_path / "sample.mp4"
    export_video_from_txv(str(path), str(output), profile="twitter")

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=width,height,nb_read_frames", "-of", "csv=p=0", str(output)],
        capture_output=True, text=True, check=True,
    )
    assert probe.stdout.strip() == f"1280,720,{len(frames)}"
