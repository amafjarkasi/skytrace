"""Unit tests that don't need models or network."""

from skytrace.roboflow_http import normalize_detect_path
from skytrace.config import ROBOFLOW_MODELS


def test_normalize_strips_workspace():
    assert (
        normalize_detect_path(
            "airborne-object-detection/airborne-object-detection-4-aod4/6"
        )
        == "airborne-object-detection-4-aod4/6"
    )


def test_normalize_already_short():
    assert normalize_detect_path("overhead-plane-detector/3") == "overhead-plane-detector/3"


def test_normalize_rejects_bad():
    try:
        normalize_detect_path("only-one-part")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_drone_model_aliases_present():
    assert "drone" in ROBOFLOW_MODELS
    assert "drone_yolo11" in ROBOFLOW_MODELS
    assert "drone_v2" in ROBOFLOW_MODELS
    assert ROBOFLOW_MODELS["drone"] == ROBOFLOW_MODELS["drone_yolo11"]
    assert ROBOFLOW_MODELS["drone"].endswith("/2")


def test_normalize_drone_model():
    assert (
        normalize_detect_path(ROBOFLOW_MODELS["drone"])
        == "drone-detection-dvhol/2"
    )
