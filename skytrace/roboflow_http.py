"""Minimal Roboflow Detect HTTP client (works on Python 3.13)."""

from __future__ import annotations

import base64
from typing import Any

import cv2
import numpy as np
import requests
import supervision as sv


def normalize_detect_path(model_id: str) -> str:
    """
    Roboflow hosted detect expects `{project}/{version}`, not `{workspace}/{project}/{version}`.
    Accept either form from config.
    """
    parts = [p for p in model_id.strip("/").split("/") if p]
    if len(parts) >= 3:
        return f"{parts[-2]}/{parts[-1]}"
    if len(parts) == 2:
        return f"{parts[0]}/{parts[1]}"
    raise ValueError(f"Invalid Roboflow model id: {model_id}")


class RoboflowHTTPModel:
    """Call serverless.roboflow.com without the inference package."""

    def __init__(
        self,
        model_id: str,
        api_key: str,
        api_url: str = "https://serverless.roboflow.com",
    ) -> None:
        self.model_id = model_id
        self.detect_path = normalize_detect_path(model_id)
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self._session = requests.Session()

    def infer(self, frame: np.ndarray, confidence: float = 0.25) -> list[dict[str, Any]]:
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            raise RuntimeError("Failed to encode frame as JPEG")

        conf_pct = int(confidence * 100) if confidence <= 1 else int(confidence)
        url = f"{self.api_url}/{self.detect_path}"
        img_b64 = base64.b64encode(buffer.tobytes()).decode("ascii")
        response = self._session.post(
            url,
            params={
                "api_key": self.api_key,
                "name": "frame.jpg",
                "overlap": 30,
                "confidence": conf_pct,
                "stroke": 1,
                "labels": "false",
                "format": "json",
            },
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=60,
        )
        if not response.ok:
            raise RuntimeError(
                f"Roboflow detect failed ({response.status_code}) for model "
                f"{self.detect_path}: {response.text[:300]}"
            )
        return [response.json()]


def detections_from_roboflow_payload(payload: dict[str, Any]) -> sv.Detections:
    predictions = payload.get("predictions") or []
    if not predictions:
        empty = sv.Detections.empty()
        empty["class_name"] = np.array([], dtype=str)
        return empty

    xyxy = []
    confidence = []
    class_id = []
    class_name = []
    for pred in predictions:
        x = float(pred["x"])
        y = float(pred["y"])
        w = float(pred["width"])
        h = float(pred["height"])
        xyxy.append([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
        confidence.append(float(pred.get("confidence", 0.0)))
        class_id.append(int(pred.get("class_id", 0)))
        class_name.append(str(pred.get("class", "object")))

    detections = sv.Detections(
        xyxy=np.array(xyxy, dtype=np.float32),
        confidence=np.array(confidence, dtype=np.float32),
        class_id=np.array(class_id, dtype=int),
    )
    detections["class_name"] = np.array(class_name)
    return detections
