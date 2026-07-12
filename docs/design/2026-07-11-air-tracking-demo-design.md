# SkyTrace — Design

**Goal:** Ship a runnable Supervision demo (**SkyTrace**) that detects and tracks airplanes and drones (plus helicopters/birds when present) on public under-shot, overhead, and drone sample media — no user-provided data required.

## Stack
- `supervision` — ByteTrack, annotators, `PolygonZone` / `LineZone`, video I/O
- **Roboflow Inference (local)** — preferred; Universe models after one-time weight download
- Ultralytics **YOLO-World** — offline open-vocab multi-class fallback
- COCO YOLOv8n — airplane-only smoke-test fallback
- Gradio UI + CLI (`python -m skytrace.cli`)
- Sample fetch from Wikimedia Commons (CC-licensed planes + drones)

## Pipeline
`frame → detector → sv.Detections → ByteTrack → optional zones → Box/Label/Trace → MP4 + events JSON`

## Samples
- Under-shot / sky-side: Commons takeoff & spotting videos
- Overhead-style: Commons aerial airport stills stitched into a short clip
- Drone: Commons clips *of* drones (not footage filmed by drones)

## Outputs
- Annotated MP4 under `data/outputs/`
- Event JSON (frame, track_id, class, confidence, xyxy, optional in_zone)
- Gradio: pick bundled sample or upload; optional zone counters
- Gallery GIFs under `docs/assets/` (via `scripts/build_gallery.py`)
