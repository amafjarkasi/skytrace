from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
VIDEOS_DIR = DATA_DIR / "videos"
IMAGES_DIR = DATA_DIR / "images"
OUTPUTS_DIR = DATA_DIR / "outputs"
WEIGHTS_DIR = ROOT / "weights"
DOCS_ASSETS_DIR = ROOT / "docs" / "assets"

WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "").strip()

# Open-vocab classes for YOLO-World (multi-type airborne tracking)
DEFAULT_CLASSES = [
    "airplane",
    "aircraft",
    "jet",
    "drone",
    "UAV",
    "helicopter",
    "bird",
]


def _inference_available() -> bool:
    try:
        import inference  # noqa: F401

        return True
    except ImportError:
        return False


INFERENCE_AVAILABLE = _inference_available()

# Prefer local inference (free after model download) over cloud HTTP.
if INFERENCE_AVAILABLE and ROBOFLOW_API_KEY:
    DEFAULT_BACKEND = "local"
elif ROBOFLOW_API_KEY:
    DEFAULT_BACKEND = "roboflow"  # cloud HTTP — costs credits
else:
    DEFAULT_BACKEND = "world"

# Public Universe models with a trained hosted model (verified via API)
ROBOFLOW_MODELS = {
    "airborne": "airborne-object-detection/airborne-object-detection-4-aod4/6",
    "overhead_plane": "skybot-cam/overhead-plane-detector/3",
    # Drone / UAV (verified trained models on Roboflow Universe)
    # Prefer drone_yolo11 weights (verified non-zero tracks on hover clip)
    "drone": "godworkspace/drone-detection-dvhol/2",
    "drone_yolo11": "godworkspace/drone-detection-dvhol/2",
    "drone_v2": "yolodrone/drone-object-detection-v2/1",
    "drone_large": "drone-detection-snemv/drone-detection-wpccn/1",
    "tello": "alexander437-gzzhf/tello_detect/1",
}
DEFAULT_ROBOFLOW_MODEL = ROBOFLOW_MODELS["airborne"]

# COCO class id for airplane when using standard YOLO fallback
COCO_AIRPLANE_ID = 4

CONFIDENCE = 0.15
IOU = 0.5
