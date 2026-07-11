"""Catalog of public sample media and download helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import requests
from tqdm import tqdm

from skytrace.config import IMAGES_DIR, VIDEOS_DIR

# Wikimedia requires a descriptive User-Agent:
# https://meta.wikimedia.org/wiki/User-Agent_policy
USER_AGENT = (
    "SkyTrace/0.1 (https://github.com/local/skytrace; research/demo; python-requests)"
)
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


@dataclass(frozen=True)
class SampleAsset:
    id: str
    kind: str  # undershot | overhead | spotting | drone
    filename: str
    url: str
    license: str
    attribution: str
    notes: str


# Direct Wikimedia Commons file URLs (resolved via Commons API).
SAMPLES: list[SampleAsset] = [
    SampleAsset(
        id="undershot_a380_yyz",
        kind="undershot",
        filename="undershot_a380_yyz.webm",
        url="https://upload.wikimedia.org/wikipedia/commons/e/e2/A380_Taking_off_from_YYZ.webm",
        license="CC BY 4.0",
        attribution="LeoTor / Wikimedia Commons — File:A380 Taking off from YYZ.webm",
        notes="Under-shot / side sky view of A380 takeoff (~34s, ~8MB)",
    ),
    SampleAsset(
        id="undershot_flight_delhi",
        kind="undershot",
        filename="undershot_flight_delhi.webm",
        url="https://upload.wikimedia.org/wikipedia/commons/d/d1/Flight_taking_off.webm",
        license="CC BY-SA 3.0",
        attribution="Subhashish Panigrahi / Wikimedia Commons — File:Flight taking off.webm",
        notes="Ground-looking takeoff, Air India Airbus (~94s, ~19MB)",
    ),
    SampleAsset(
        id="spotting_747_rctp",
        kind="spotting",
        filename="spotting_747_rctp.webm",
        url=(
            "https://upload.wikimedia.org/wikipedia/commons/2/20/"
            "Plane_Spotting_Atlas_Air_Cargo_Boeing_747_Runway_at_RCTP_with_ATC_"
            "%E6%A1%83%E5%9C%92%E6%A9%9F%E5%A0%B4%E8%B5%B7%E9%99%8D.webm"
        ),
        license="See Commons file page",
        attribution="Wikimedia Commons — Atlas Air 747 runway spotting at RCTP",
        notes="Longer spotting clip with runway activity (~3min, ~30MB)",
    ),
    SampleAsset(
        id="undershot_tejas",
        kind="undershot",
        filename="undershot_tejas.webm",
        url="https://upload.wikimedia.org/wikipedia/commons/1/16/Tejas_takeoff_from_INS_Vikrant.webm",
        license="GODL-India",
        attribution="Government of India / Wikimedia Commons — Tejas takeoff from INS Vikrant",
        notes="Short carrier takeoff clip (~8s, ~2MB) — good smoke test",
    ),
    # Videos of drones (not footage filmed by drones)
    SampleAsset(
        id="drone_quadcopter_hover",
        kind="drone",
        filename="drone_quadcopter_hover.webm",
        url="https://upload.wikimedia.org/wikipedia/commons/a/ac/Quadcopter_20200202.webm",
        license="CC BY-SA 4.0",
        attribution="Project Kei / Wikimedia Commons — File:Quadcopter 20200202.webm",
        notes="Quadcopter hovering against sky (~10s, ~10MB)",
    ),
    SampleAsset(
        id="drone_matrice_fire",
        kind="drone",
        filename="drone_matrice_fire.webm",
        url=(
            "https://upload.wikimedia.org/wikipedia/commons/5/52/"
            "DJI_Matrice_300RTK_Feuerwehr_Drohne_LFV_Stmk_BFVFF.webm"
        ),
        license="CC BY-SA 4.0",
        attribution="Iswoar / Wikimedia Commons — DJI Matrice 300RTK Feuerwehr Drohne",
        notes="Fire-service DJI Matrice 300RTK (~12s, ~4MB)",
    ),
    SampleAsset(
        id="drone_cobalt_vtol",
        kind="drone",
        filename="drone_cobalt_vtol.webm",
        url="https://upload.wikimedia.org/wikipedia/commons/3/36/Armed_Cobalt_110_G-VTOL_Drone.webm",
        license="See Commons file page",
        attribution="Wikimedia Commons — Armed Cobalt 110 G-VTOL Drone.webm",
        notes="VTOL drone demo clip (~18s, ~5MB)",
    ),
    SampleAsset(
        id="drone_peliscu",
        kind="drone",
        filename="drone_peliscu.webm",
        url=(
            "https://upload.wikimedia.org/wikipedia/commons/0/02/"
            "Dron_na_Peli%C5%A1cu_134429.webm"
        ),
        license="See Commons file page",
        attribution="Wikimedia Commons — Dron na Pelišcu 134429.webm",
        notes="Small outdoor drone clip (~12s, ~2MB)",
    ),
]

OVERHEAD_IMAGES: list[SampleAsset] = [
    SampleAsset(
        id="overhead_farnborough",
        kind="overhead",
        filename="overhead_farnborough.jpg",
        url=(
            "https://upload.wikimedia.org/wikipedia/commons/e/ea/"
            "Farnborough_Airport_Control_Tower_and_parked_aircraft%2C_aerial_2016_"
            "-_geograph.org.uk_-_4993873.jpg"
        ),
        license="CC BY-SA 2.0",
        attribution="geograph.org.uk / Wikimedia Commons — Farnborough aerial 2016",
        notes="True overhead apron with parked aircraft",
    ),
    SampleAsset(
        id="overhead_tansonnhat",
        kind="overhead",
        filename="overhead_tansonnhat.jpg",
        url="https://upload.wikimedia.org/wikipedia/commons/5/5a/Tansonnhat9.jpg",
        license="See Commons file page",
        attribution="Wikimedia Commons — Tan Son Nhat airport view",
        notes="Elevated / near-overhead airport with multiple aircraft",
    ),
    SampleAsset(
        id="overhead_lappeenranta",
        kind="overhead",
        filename="overhead_lappeenranta.jpg",
        url="https://upload.wikimedia.org/wikipedia/commons/8/81/Lappeenranta_Airport_apron_1986-07.jpg",
        license="See Commons file page",
        attribution="Wikimedia Commons — Lappeenranta Airport apron",
        notes="Apron overview with aircraft on the ground",
    ),
]

OVERHEAD_VIDEO_NAME = "overhead_apron_montage.mp4"


def _download(url: str, dest: Path, timeout: int = 120) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest

    with SESSION.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        with open(dest, "wb") as handle, tqdm(
            total=total or None,
            unit="B",
            unit_scale=True,
            desc=dest.name,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                handle.write(chunk)
                bar.update(len(chunk))
    return dest


def download_videos(force: bool = False) -> list[Path]:
    paths: list[Path] = []
    for sample in SAMPLES:
        dest = VIDEOS_DIR / sample.filename
        if force and dest.exists():
            dest.unlink()
        paths.append(_download(sample.url, dest))
    return paths


def download_overhead_images(force: bool = False) -> list[Path]:
    paths: list[Path] = []
    for sample in OVERHEAD_IMAGES:
        dest = IMAGES_DIR / sample.filename
        if force and dest.exists():
            dest.unlink()
        paths.append(_download(sample.url, dest))
    return paths


def build_overhead_montage(
    image_paths: list[Path] | None = None,
    out_path: Path | None = None,
    seconds_per_image: float = 3.0,
    fps: int = 10,
) -> Path:
    """Stitch overhead stills into a short video the tracker can process."""
    out_path = out_path or (VIDEOS_DIR / OVERHEAD_VIDEO_NAME)
    image_paths = image_paths or [
        IMAGES_DIR / sample.filename for sample in OVERHEAD_IMAGES
    ]
    frames_per = max(1, int(seconds_per_image * fps))
    writer = None
    size = None

    for image_path in image_paths:
        if not image_path.exists():
            continue
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        if size is None:
            h, w = image.shape[:2]
            scale = min(1.0, 1280 / max(w, 1))
            size = (int(w * scale), int(h * scale))
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps, size)
        resized = cv2.resize(image, size)
        assert writer is not None
        for _ in range(frames_per):
            writer.write(resized)

    if writer is None:
        raise RuntimeError("No overhead images available to build montage")
    writer.release()
    return out_path


def write_manifest(path: Path | None = None) -> Path:
    path = path or (VIDEOS_DIR / "manifest.json")
    payload = {
        "videos": [asdict(s) for s in SAMPLES],
        "overhead_images": [asdict(s) for s in OVERHEAD_IMAGES],
        "overhead_video": OVERHEAD_VIDEO_NAME,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def ensure_all_samples(force: bool = False) -> dict[str, list[Path]]:
    videos = download_videos(force=force)
    images = download_overhead_images(force=force)
    overhead = build_overhead_montage(images)
    write_manifest()
    return {"videos": videos, "images": images, "overhead_video": [overhead]}


def list_local_sources() -> list[Path]:
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    patterns = ("*.mp4", "*.webm", "*.avi", "*.mov", "*.mkv")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(VIDEOS_DIR.glob(pattern)))
    return files
