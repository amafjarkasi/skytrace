# Research & product gaps

SkyTrace is a **demo** of Supervision-style airborne tracking. Compared to production aviation, UAS, and airport-ops systems (and to what Supervision *can* support with more work), these gaps remain.

## Research context (2025–2026)

Recent airport / UAS literature treats **vision-only tracking as one layer**, not the system:

- **ADS-B + video fusion** for surface aircraft (e.g. attention-aware matching, contrastive vision–ADS-B pretraining) improves small/distant targets that cameras miss alone.
- **Drone detection reviews** push multimodal stacks (radar + RF + EO/IR + acoustic); CV alone struggles with birds vs drones and range.
- **Multi-scale / context modules** matter for apron scenes (huge airliners vs tiny ground objects).

SkyTrace intentionally stops at Supervision-style EO tracking + public samples. Closing the gaps above is R&D / ops engineering, not a README checkbox.

## Capability gaps


| Gap                                | Why it matters                                               | Possible next step                                                 |
| ---------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------ |
| **No ADS-B / Mode-S fusion**       | Visual tracks lack callsign, altitude, ICAO address          | Correlate track centroids with OpenSky / ADS-B feeds by time+geo   |
| **No multi-camera re-ID**          | Same aircraft across cameras gets new IDs                    | Appearance embeddings + spatial handoff                            |
| **Tiny / distant targets**         | High-altitude spotting can be a few pixels                   | SAHI / tiled inference, higher-res models, lower conf + NMS tuning |
| **Weak drone coverage in samples** | Bundled clips are mostly airliners                           | Add dedicated drone Commons / Universe drone models                |
| **View-specific models**           | Under-shot ≠ overhead ≠ satellite                            | Auto-select alias by source metadata or UI preset                  |
| **No zone analytics**              | Runway occupancy / apron counts are common Supervision demos | `PolygonZone` + line crossing counts                               |
| **No live RTSP recipe**            | Ops care about streams, not files                            | Document webcam/RTSP → `process_video` loop                        |
| **Not safety-certified**           | Cannot replace ATC / certified surveillance                  | Keep disclaimer; no “operational use” claims                       |
| **Cloud cost footgun**             | `roboflow` backend bills per frame                           | Keep `local` default; warn in UI when cloud selected               |




## Supervision features not yet showcased

- `PolygonZone` / `LineZone` for apron or runway counting  
- Heatmaps / speed estimates from tracks  
- Dataset export (`DetectionDataset`) for fine-tuning  
- SAM-based refinement (optional; currently disabled to reduce noise)



## Sample / data gaps

- Long spotting videos are large; demos often use `--max-frames`  
- Overhead path uses a **still montage**, not true continuous aerial video  
- Licenses vary (CC BY / CC BY-SA / GODL) — commercial redistribution of media needs care



## Engineering polish still useful

- Pin / upgrade `inference` to silence version warnings  
- Optional GPU acceleration notes (CUDA providers)  
- CI: lint + pytest on normalize / path helpers  
- Screenshot / GIF gallery in README (from `data/outputs/`)  
- Rename internal package `airtrack` → `skytrace` for full brand alignment



## What already works well

- Local Inference on under-shot + overhead samples with stable ByteTrack IDs  
- Cost-aware backend table and `.venv312` path  
- Public-sample fetch (no user data required)  
- Events JSON for downstream analysis

This list is intentional scope control — not a claim that airborne CV is “solved.”