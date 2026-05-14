#!/usr/bin/env python3
"""Concatenate videos using ffmpeg concat demuxer."""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def _build_concat_file(paths):
    lines = []
    for path in paths:
        # Escape single quotes for ffmpeg concat file syntax.
        safe_path = str(path).replace("'", "'\\''")
        lines.append(f"file '{safe_path}'")
    return "\n".join(lines) + "\n"


def concat_videos(inputs, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    concat_text = _build_concat_file(inputs)
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as fp:
        fp.write(concat_text)
        concat_path = fp.name

    try:
        command = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_path,
            "-c",
            "copy",
            str(output),
        ]
        subprocess.run(command, check=True)
    finally:
        try:
            os.remove(concat_path)
        except OSError:
            pass


def _resolve_path(value, base_dir, prefer_base=False):
    path = Path(value)
    if path.is_absolute():
        return path

    candidate = base_dir / path
    if prefer_base or candidate.exists():
        return candidate

    return path


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate multiple videos into one using ffmpeg."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input video files in the order to concatenate",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output video file path",
    )

    args = parser.parse_args()
    base_dir = (Path(__file__).resolve().parents[1] / "uploads" / "videos")

    input_paths = [
        _resolve_path(p, base_dir).resolve()
        for p in args.inputs
    ]
    output_path = _resolve_path(args.output, base_dir, prefer_base=True).resolve()

    missing = [str(p) for p in input_paths if not p.exists()]
    if missing:
        raise SystemExit(f"Missing input files: {', '.join(missing)}")

    concat_videos(input_paths, output_path)


if __name__ == "__main__":
    main()
