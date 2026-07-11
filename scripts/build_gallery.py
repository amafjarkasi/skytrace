"""Build README gallery GIFs / stills from tracked MP4 outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from skytrace.config import DOCS_ASSETS_DIR, OUTPUTS_DIR


def video_to_gif(
    source: Path,
    dest: Path,
    max_frames: int = 48,
    stride: int = 2,
    width: int = 640,
) -> Path | None:
    if not source.exists() or source.stat().st_size < 1000:
        return None

    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        return None

    frames: list = []
    idx = 0
    while len(frames) < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % stride == 0:
            h, w = frame.shape[:2]
            scale = width / max(w, 1)
            resized = cv2.resize(frame, (width, max(1, int(h * scale))))
            frames.append(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        idx += 1
    cap.release()

    if not frames:
        return None

    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import imageio.v2 as imageio

        imageio.mimsave(dest, frames, duration=0.12, loop=0)
    except Exception:
        # Fallback: write a representative PNG still
        still = dest.with_suffix(".png")
        bgr = cv2.cvtColor(frames[len(frames) // 2], cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(still), bgr)
        return still
    return dest


def write_still(source: Path, dest: Path, frame_index: int = 10) -> Path | None:
    if not source.exists() or source.stat().st_size < 1000:
        return None
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        return None
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    h, w = frame.shape[:2]
    scale = 960 / max(w, 1)
    frame = cv2.resize(frame, (960, max(1, int(h * scale))))
    cv2.imwrite(str(dest), frame)
    return dest


GALLERY = [
    ("demo_undershot_a380_local.mp4", "undershot_a380.gif", "undershot_a380.png"),
    ("demo_overhead_local.mp4", "overhead_apron.gif", "overhead_apron.png"),
    ("undershot_tejas_tracked.mp4", "undershot_tejas.gif", "undershot_tejas.png"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build docs/assets gallery")
    parser.add_argument("--outputs", type=Path, default=OUTPUTS_DIR)
    parser.add_argument("--dest", type=Path, default=DOCS_ASSETS_DIR)
    args = parser.parse_args()

    args.dest.mkdir(parents=True, exist_ok=True)
    for video_name, gif_name, png_name in GALLERY:
        src = args.outputs / video_name
        gif = video_to_gif(src, args.dest / gif_name)
        still = write_still(src, args.dest / png_name)
        print(f"{video_name}: gif={gif} still={still}")


if __name__ == "__main__":
    main()
