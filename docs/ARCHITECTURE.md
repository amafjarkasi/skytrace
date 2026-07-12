# SkyTrace architecture

## Goals

- Demonstrate Supervision (detect → track → annotate → export) on **airborne** imagery.
- Prefer **local** Roboflow Inference after a one-time weight download.
- Ship **zero user samples**: fetch CC Wikimedia under-shot, overhead, and **drone** clips.

## Module map

| Module | Responsibility |
| --- | --- |
| `skytrace/config.py` | Paths (`data/`, `weights/`), `.env`, model aliases, Inference availability |
| `skytrace/pipeline.py` | `AirborneDetector`, ByteTrack, zones, annotators, `process_video` |
| `skytrace/roboflow_http.py` | Cloud detect HTTP + `normalize_detect_path` |
| `skytrace/samples.py` | Catalog, download (User-Agent), apron montage |
| `skytrace/cli.py` | `fetch` / `track` / `list` / `status` |
| `app.py` | Gradio: fetch samples, pick backend, zones, run, preview |
| `scripts/build_gallery.py` | README GIFs/stills from tracked MP4s |

## Data flow

```
source video
    → AirborneDetector.predict(frame) → sv.Detections
    → ByteTrackTracker.update(...)     → track_id on detections
    → optional PolygonZone + LineZone
    → BoxAnnotator / LabelAnnotator / TraceAnnotator
    → VideoSink → data/outputs/*_tracked.mp4
    → events list → data/outputs/*.events.json
```

## Zones (optional `--zones`)

- **PolygonZone** — relative central “corridor” polygon; detections inside are tagged `[zone]`.
- **LineZone** — horizontal mid-frame line; accumulates `in_count` / `out_count`.

## Config & env

| Variable / path | Role |
| --- | --- |
| `ROBOFLOW_API_KEY` | Universe weight download (local) or cloud detect |
| `DEFAULT_BACKEND` | Often `local` when Inference is importable |
| `weights/` | Ultralytics YOLO / YOLO-World checkpoints (gitignored) |
| Model aliases | `airborne`, `overhead_plane`, `drone`, `drone_v2`, `drone_large`, `tello` |

Model IDs for Inference/HTTP are normalized to `project/version` (workspace prefix stripped).

## Tracker policy

1. Try `trackers.ByteTrackTracker` with lower activation / IOU thresholds (sparse aerial dets).
2. Else `sv.ByteTrack.update_with_detections`.

## Backend selection

```
local / inference → inference.get_model(model_id, api_key)
world             → ultralytics YOLO-World + class prompts
coco              → YOLOv8n COCO airplane class
roboflow          → POST base64 frame to serverless.roboflow.com/{project}/{version}
```

## Outputs schema (events JSON)

```json
{
  "source": "...",
  "model": "local:project/version",
  "frames_processed": 120,
  "unique_tracks": 1,
  "class_counts": {"airplane": 95},
  "zones": {
    "enabled": true,
    "zone_detection_hits": 40,
    "line_in": 1,
    "line_out": 0
  },
  "events": [
    {
      "frame": 0,
      "track_id": 1,
      "class": "airplane",
      "confidence": 0.87,
      "xyxy": [x1, y1, x2, y2],
      "in_zone": true
    }
  ]
}
```

## Design constraints

- **Cost:** never default long videos to cloud HTTP.
- **Python:** local Inference needs 3.10–3.12 (`.venv312`).
- **Licenses:** sample media attribution in `NOTICE.md`; code is MIT.
