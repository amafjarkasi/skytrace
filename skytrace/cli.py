"""CLI entrypoints for fetching samples and running tracking."""

from __future__ import annotations

import argparse
from pathlib import Path

from skytrace.config import (
    DEFAULT_BACKEND,
    DEFAULT_CLASSES,
    DEFAULT_ROBOFLOW_MODEL,
    INFERENCE_AVAILABLE,
    OUTPUTS_DIR,
    ROBOFLOW_API_KEY,
    ROBOFLOW_MODELS,
)
from skytrace.pipeline import process_video
from skytrace.samples import ensure_all_samples, list_local_sources


def cmd_fetch(args: argparse.Namespace) -> None:
    result = ensure_all_samples(force=args.force)
    print("Downloaded / built:")
    for key, paths in result.items():
        for path in paths:
            print(f"  [{key}] {path}")


def cmd_track(args: argparse.Namespace) -> None:
    source = Path(args.source) if args.source else None
    if source is None:
        local = list_local_sources()
        if not local:
            print("No local videos. Run: python -m skytrace.cli fetch")
            raise SystemExit(1)
        source = local[0]
        print(f"Using first local sample: {source}")

    classes = [c.strip() for c in args.classes.split(",") if c.strip()]
    result = process_video(
        source=source,
        output=Path(args.output) if args.output else None,
        classes=classes or None,
        confidence=args.conf,
        max_frames=args.max_frames,
        show_preview=args.preview,
        backend=args.backend,
        roboflow_model=args.roboflow_model,
        enable_zones=args.zones,
    )
    print(f"Model:   {result.model_name}")
    print(f"Frames:  {result.frames_processed}")
    print(f"Tracks:  {result.unique_tracks}")
    print(f"Classes: {result.class_counts}")
    if result.zone_enabled:
        print(
            f"Zones:   hits={result.zone_in_frames}  "
            f"line_in={result.line_in}  line_out={result.line_out}"
        )
    print(f"Video:   {result.output_video}")
    print(f"Events:  {result.events_json}")


def cmd_list(_: argparse.Namespace) -> None:
    files = list_local_sources()
    if not files:
        print("No videos in data/videos — run fetch first.")
        return
    for path in files:
        print(path)


def cmd_status(_: argparse.Namespace) -> None:
    key_set = bool(ROBOFLOW_API_KEY)
    print(f"ROBOFLOW_API_KEY:     {'set' if key_set else 'missing'}")
    print(f"inference package:    {'yes' if INFERENCE_AVAILABLE else 'no (use .venv312)'}")
    print(f"Default backend:      {DEFAULT_BACKEND}")
    print(f"Default RF model:     {DEFAULT_ROBOFLOW_MODEL}")
    print("Backends:")
    print("  local     — Roboflow Inference on-device (recommended, low cost)")
    print("  world     — YOLO-World fully offline")
    print("  roboflow  — cloud HTTP detect (uses credits per frame)")
    print("  coco      — YOLOv8n airplane only, offline")
    print("Named Roboflow models:")
    for name, model_id in ROBOFLOW_MODELS.items():
        print(f"  {name}: {model_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skytrace",
        description="SkyTrace — airborne detection & tracking (Supervision)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="Download public sample videos/images")
    fetch.add_argument("--force", action="store_true", help="Re-download assets")
    fetch.set_defaults(func=cmd_fetch)

    track = sub.add_parser("track", help="Run detect+track on a video")
    track.add_argument("--source", type=str, default=None, help="Input video path")
    track.add_argument("--output", type=str, default=None, help="Output MP4 path")
    track.add_argument(
        "--backend",
        type=str,
        default=DEFAULT_BACKEND,
        choices=["local", "roboflow", "world", "coco", "auto"],
        help="local=on-device inference (cheap), roboflow=cloud HTTP (costly), world=offline",
    )
    track.add_argument(
        "--roboflow-model",
        type=str,
        default=DEFAULT_ROBOFLOW_MODEL,
        help="Universe model id, or alias: airborne | overhead_plane | drone | tello",
    )
    track.add_argument(
        "--classes",
        type=str,
        default=",".join(DEFAULT_CLASSES),
        help="Comma-separated YOLO-World classes (world backend only)",
    )
    track.add_argument("--conf", type=float, default=0.15)
    track.add_argument("--max-frames", type=int, default=None)
    track.add_argument("--preview", action="store_true")
    track.add_argument(
        "--zones",
        action="store_true",
        help="Draw PolygonZone corridor + LineZone crossing counters",
    )
    track.set_defaults(func=cmd_track)

    listing = sub.add_parser("list", help="List local sample videos")
    listing.set_defaults(func=cmd_list)

    status = sub.add_parser("status", help="Show API key / model config")
    status.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
