# Research & product gaps

SkyTrace is a **demo** of Supervision-style airborne tracking. Compared to production aviation, UAS, and airport-ops systems (and to what Supervision *can* support with more work), these gaps remain.

## Research context (2025–2026)

Recent airport / UAS literature treats **vision-only tracking as one layer**, not the system:

- **ADS-B + video fusion** for surface aircraft (e.g. attention-aware matching, contrastive vision–ADS-B pretraining) improves small/distant targets that cameras miss alone.
- **Drone detection reviews** push multimodal stacks (radar + RF + EO/IR + acoustic); CV alone struggles with birds vs drones and range.
- **Multi-scale / context modules** matter for apron scenes (huge airliners vs tiny ground objects).

SkyTrace intentionally stops at Supervision-style EO tracking + public samples. Closing the gaps above is R&D / ops engineering, not a README checkbox.

## Capability gaps

| Gap | Why it matters | Possible next step |
| --- | --- | --- |
| **No ADS-B / Mode-S fusion** | Visual tracks lack callsign, altitude, ICAO address | Correlate track centroids with OpenSky / ADS-B feeds by time+geo |
| **No multi-camera re-ID** | Same aircraft across cameras gets new IDs | Appearance embeddings + spatial handoff |
| **Tiny / distant targets** | High-altitude spotting can be a few pixels | SAHI / tiled inference, higher-res models, lower conf + NMS tuning |
| **View-specific models** | Under-shot ≠ overhead ≠ satellite | Auto-select alias by source metadata or UI preset |
| **Not safety-certified** | Cannot replace ATC / certified surveillance | Keep disclaimer; no “operational use” claims |
| **Cloud cost footgun** | `roboflow` backend bills per frame | Keep `local` default; warn in UI when cloud selected |

## Recently closed (demo scope)

- Drone-focused Commons samples + Universe model aliases (`drone`, `drone_yolo11`, `tello`, …)
- `PolygonZone` + `LineZone` showcase (`--zones`)
- Package rename to `skytrace`
- CI (pytest) + README gallery assets

## Supervision features still optional

- Heatmaps / speed estimates from tracks  
- Dataset export (`DetectionDataset`) for fine-tuning  
- SAM-based refinement (optional; currently disabled to reduce noise)  
- Live RTSP / webcam recipe polish  

## Sample / data notes

- Long spotting videos are large; demos often use `--max-frames`  
- Overhead path uses a **still montage**, not true continuous aerial video  
- Licenses vary (CC BY / CC BY-SA / GODL) — commercial redistribution of media needs care  

## What already works well

- Local Inference on under-shot + overhead + drone samples with ByteTrack IDs  
- Cost-aware backend table and `.venv312` path  
- Public-sample fetch (no user data required)  
- Events JSON + zone counters for downstream analysis  

This list is intentional scope control — not a claim that airborne CV is “solved.”
