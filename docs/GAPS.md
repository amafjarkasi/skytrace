# Research & product gaps

SkyTrace is a **demo** of Supervision-style airborne tracking. Compared to production aviation, UAS, and airport-ops systems, these gaps remain.

## Mission (product framing)

SkyTrace exists to stress **multi-object aerial MOT**: dense apron traffic, drone activity, and hard-to-track jets — not a single close-up airliner screenshot.

## Research context (2025–2026)

Recent airport / UAS literature treats **vision-only tracking as one layer**, not the system:

- **ADS-B + video fusion** for surface aircraft improves small/distant targets that cameras miss alone.
- **Drone detection reviews** push multimodal stacks (radar + RF + EO/IR + acoustic); CV alone struggles with birds vs drones and range.
- **Multi-scale / context modules** matter for apron scenes (huge airliners vs tiny ground objects).

SkyTrace intentionally stops at Supervision-style EO tracking + public samples.

## Capability gaps

| Gap | Why it matters | Possible next step |
| --- | --- | --- |
| **No ADS-B / Mode-S fusion** | Visual tracks lack callsign, altitude, ICAO address | Correlate tracks with OpenSky / ADS-B by time+geo |
| **No multi-camera re-ID** | Same aircraft across cameras gets new IDs | Appearance embeddings + spatial handoff |
| **Tiny / distant targets** | High-altitude spotting can be a few pixels | SAHI / tiled inference, higher-res models |
| **View-specific models** | Under-shot ≠ overhead ≠ satellite | Auto-select alias by source metadata |
| **Not safety-certified** | Cannot replace ATC / certified surveillance | Keep disclaimer; no operational-use claims |
| **Cloud cost footgun** | `roboflow` backend bills per frame | Keep `local` default; warn in UI when cloud selected |

## Closed in this repo (demo scope)

- Drone Commons samples + Universe aliases (`drone`, `drone_v2`, `tello`, …)
- `PolygonZone` + `LineZone` via `--zones`
- Package `skytrace`, CI, README gallery under `docs/assets/`
- Root hygiene: `weights/`, `docs/design/`, expanded `.gitignore`

## Still optional

- Heatmaps / speed estimates from tracks
- Dataset export for fine-tuning
- Live RTSP / webcam recipe
- Pin / upgrade `inference`; CUDA provider notes

## Sample / data notes

- Long spotting videos are large; demos often use `--max-frames`
- Overhead path uses a **still montage**, not continuous aerial video
- Media licenses vary — see `NOTICE.md`

## What already works

- Local Inference on under-shot, overhead, and drone samples with ByteTrack
- Cost-aware backends and `.venv312` path
- Public-sample fetch (no user data required)
- Events JSON + optional zone counters
