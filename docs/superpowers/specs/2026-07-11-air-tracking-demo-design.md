# SkyTrace — Design

**Goal:** Ship a runnable Supervision demo (**SkyTrace**) that detects and tracks airplanes and drones (plus helicopters/birds when present) on public under-shot, overhead, and drone sample media — no user-provided data required.

## Stack
- `supervision` — ByteTrack, annotators, video I/O
- Ultralytics **YOLO-World** — open-vocab multi-class (`airplane`, `drone`, `helicopter`, `bird`) without a custom trained weight
- Fallback: COCO YOLO (`airplane` only) if YOLO-World unavailable
- Gradio UI + CLI
- Sample fetch from Wikimedia Commons (CC-licensed)

## Pipeline
`frame → YOLO-World → sv.Detections → ByteTrack → Box/Label/Trace annotators → video + JSON events`

## Samples
- Under-shot / sky-side: Commons takeoff & spotting videos
- Overhead-style: Commons aerial airport stills stitched into a short clip (+ optional spotting video)

## Outputs
- Annotated MP4 under `data/outputs/`
- Event JSON (frame, track_id, class, confidence, xyxy)
- Gradio: pick bundled sample or upload
