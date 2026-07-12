"""Detection + ByteTrack pipeline using Supervision."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Quiet noisy optional Inference plugins before heavy imports
os.environ.setdefault("CORE_MODEL_GAZE_ENABLED", "False")
os.environ.setdefault("CORE_MODEL_SAM_ENABLED", "False")
os.environ.setdefault("CORE_MODEL_SAM3_ENABLED", "False")
os.environ.setdefault("ONNXRUNTIME_EXECUTION_PROVIDERS", "[CPUExecutionProvider]")

import cv2
import numpy as np
import supervision as sv
from tqdm import tqdm

from skytrace.config import (
    COCO_AIRPLANE_ID,
    CONFIDENCE,
    DEFAULT_BACKEND,
    DEFAULT_CLASSES,
    DEFAULT_ROBOFLOW_MODEL,
    IOU,
    OUTPUTS_DIR,
    ROBOFLOW_API_KEY,
    ROBOFLOW_MODELS,
    WEIGHTS_DIR,
)


def _make_tracker(frame_rate: float = 30.0):
    """Prefer modern trackers.ByteTrackTracker; fall back to sv.ByteTrack."""
    try:
        from trackers import ByteTrackTracker

        return (
            ByteTrackTracker(
                frame_rate=frame_rate,
                track_activation_threshold=0.25,
                minimum_consecutive_frames=1,
                high_conf_det_threshold=0.3,
                minimum_iou_threshold=0.1,
                lost_track_buffer=45,
            ),
            "update",
        )
    except ImportError:
        return sv.ByteTrack(frame_rate=frame_rate), "update_with_detections"


def _track(tracker, detections: sv.Detections, method: str) -> sv.Detections:
    if method == "update":
        return tracker.update(detections)
    return tracker.update_with_detections(detections)


def _default_corridor_polygon(width: int, height: int) -> np.ndarray:
    """Central approach / airspace corridor as a relative polygon."""
    return np.array(
        [
            [int(width * 0.15), int(height * 0.20)],
            [int(width * 0.85), int(height * 0.20)],
            [int(width * 0.95), int(height * 0.90)],
            [int(width * 0.05), int(height * 0.90)],
        ],
        dtype=np.int32,
    )


def _default_count_line(width: int, height: int) -> tuple[sv.Point, sv.Point]:
    y = int(height * 0.55)
    return sv.Point(x=int(width * 0.05), y=y), sv.Point(x=int(width * 0.95), y=y)


@dataclass
class PipelineResult:
    output_video: Path
    events_json: Path
    unique_tracks: int
    class_counts: dict[str, int]
    frames_processed: int
    model_name: str
    zone_in_frames: int = 0
    line_in: int = 0
    line_out: int = 0
    zone_enabled: bool = False


class AirborneDetector:
    """Roboflow Inference, YOLO-World, or COCO airplane fallback."""

    def __init__(
        self,
        classes: list[str] | None = None,
        confidence: float = CONFIDENCE,
        backend: str | None = None,
        roboflow_model: str | None = None,
    ) -> None:
        self.classes = classes or list(DEFAULT_CLASSES)
        self.confidence = confidence
        self.backend = (backend or DEFAULT_BACKEND).lower()
        self.roboflow_model = (
            ROBOFLOW_MODELS.get(roboflow_model or "", None)
            or roboflow_model
            or DEFAULT_ROBOFLOW_MODEL
        )
        self.model_name = ""
        self._mode = self.backend
        self._model = self._load()

    def _load(self):
        if self.backend in {"local", "inference"}:
            if not ROBOFLOW_API_KEY:
                raise RuntimeError(
                    "ROBOFLOW_API_KEY missing in .env (needed once to download weights)"
                )
            try:
                from inference import get_model
            except ImportError as exc:
                raise RuntimeError(
                    "Local inference requires the `inference` package on Python "
                    "3.10–3.12. Use .venv312 (see README) or --backend world / roboflow."
                ) from exc

            from skytrace.roboflow_http import normalize_detect_path

            os.environ.setdefault("ROBOFLOW_API_KEY", ROBOFLOW_API_KEY)
            local_model_id = normalize_detect_path(self.roboflow_model)
            model = get_model(
                model_id=local_model_id,
                api_key=ROBOFLOW_API_KEY,
            )
            self.model_name = f"local:{local_model_id}"
            self._mode = "local"
            return model

        if self.backend == "roboflow":
            if not ROBOFLOW_API_KEY:
                raise RuntimeError(
                    "ROBOFLOW_API_KEY missing. Add it to .env or use --backend world"
                )
            from skytrace.roboflow_http import RoboflowHTTPModel

            model = RoboflowHTTPModel(
                model_id=self.roboflow_model,
                api_key=ROBOFLOW_API_KEY,
            )
            self.model_name = f"cloud:{self.roboflow_model}"
            self._mode = "roboflow"
            return model

        world_weights = str(WEIGHTS_DIR / "yolov8s-worldv2.pt")
        coco_weights = str(WEIGHTS_DIR / "yolov8n.pt")

        if self.backend in {"world", "yolo-world", "auto"}:
            try:
                from ultralytics import YOLOWorld

                model = YOLOWorld(world_weights)
                model.set_classes(self.classes)
                self.model_name = "yolov8s-worldv2.pt"
                self._mode = "world"
                return model
            except Exception:
                try:
                    from ultralytics import YOLO

                    model = YOLO(world_weights)
                    if hasattr(model, "set_classes"):
                        model.set_classes(self.classes)
                    self.model_name = "yolov8s-worldv2.pt"
                    self._mode = "world"
                    return model
                except Exception:
                    if self.backend != "auto":
                        raise

        from ultralytics import YOLO

        model = YOLO(coco_weights)
        self.model_name = "yolov8n.pt (COCO airplane fallback)"
        self._mode = "coco"
        return model

    def predict(self, frame: np.ndarray) -> sv.Detections:
        if self._mode == "local":
            result = self._model.infer(frame, confidence=self.confidence)[0]
            return sv.Detections.from_inference(result)

        if self._mode == "roboflow":
            from skytrace.roboflow_http import detections_from_roboflow_payload

            result = self._model.infer(frame, confidence=self.confidence)[0]
            return detections_from_roboflow_payload(result)

        results = self._model.predict(
            frame,
            conf=self.confidence,
            iou=IOU,
            verbose=False,
        )[0]
        detections = sv.Detections.from_ultralytics(results)

        if self._mode == "coco":
            if detections.class_id is None or len(detections) == 0:
                return detections
            mask = detections.class_id == COCO_AIRPLANE_ID
            detections = detections[mask]
            detections["class_name"] = np.array(["airplane"] * len(detections))
        else:
            names = results.names
            if detections.class_id is not None and len(detections):
                detections["class_name"] = np.array(
                    [str(names.get(int(i), "object")) for i in detections.class_id]
                )
            else:
                detections["class_name"] = np.array([], dtype=str)
        return detections


def _class_name(detections: sv.Detections, index: int) -> str:
    if "class_name" in detections.data:
        return str(detections.data["class_name"][index])
    if detections.class_id is not None:
        return str(detections.class_id[index])
    return "object"


def process_video(
    source: Path | str,
    output: Path | str | None = None,
    classes: list[str] | None = None,
    confidence: float = CONFIDENCE,
    max_frames: int | None = None,
    show_preview: bool = False,
    backend: str | None = None,
    roboflow_model: str | None = None,
    enable_zones: bool = False,
) -> PipelineResult:
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(source)

    if max_frames is not None and max_frames <= 0:
        max_frames = None

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output = Path(output) if output else OUTPUTS_DIR / f"{source.stem}_tracked.mp4"
    events_path = output.with_suffix(".events.json")

    detector = AirborneDetector(
        classes=classes,
        confidence=confidence,
        backend=backend,
        roboflow_model=roboflow_model,
    )
    video_info = sv.VideoInfo.from_video_path(str(source))
    tracker, track_method = _make_tracker(frame_rate=float(video_info.fps or 30))
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_thickness=1, text_scale=0.5)
    trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=40)

    polygon_zone = None
    polygon_annotator = None
    line_zone = None
    line_annotator = None
    zone_in_frames = 0
    if enable_zones:
        poly = _default_corridor_polygon(video_info.width, video_info.height)
        polygon_zone = sv.PolygonZone(polygon=poly)
        polygon_annotator = sv.PolygonZoneAnnotator(
            zone=polygon_zone,
            color=sv.Color.BLUE,
            thickness=2,
            text_thickness=1,
            text_scale=0.5,
        )
        start, end = _default_count_line(video_info.width, video_info.height)
        line_zone = sv.LineZone(start=start, end=end)
        line_annotator = sv.LineZoneAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5,
        )

    frame_generator = sv.get_video_frames_generator(str(source))

    events: list[dict[str, Any]] = []
    unique_ids: set[int] = set()
    class_counts: dict[str, int] = {}
    frames_processed = 0

    with sv.VideoSink(str(output), video_info) as sink:
        for frame_idx, frame in enumerate(
            tqdm(frame_generator, total=video_info.total_frames, desc=source.name)
        ):
            if max_frames is not None and frame_idx >= max_frames:
                break

            detections = detector.predict(frame)
            detections = _track(tracker, detections, track_method)

            in_zone_mask = None
            if polygon_zone is not None:
                in_zone_mask = polygon_zone.trigger(detections)
                zone_in_frames += int(np.sum(in_zone_mask)) if len(detections) else 0
            if line_zone is not None:
                line_zone.trigger(detections)

            labels: list[str] = []
            for i in range(len(detections)):
                name = _class_name(detections, i)
                track_id = (
                    int(detections.tracker_id[i])
                    if detections.tracker_id is not None
                    else -1
                )
                conf = (
                    float(detections.confidence[i])
                    if detections.confidence is not None
                    else 0.0
                )
                zone_tag = ""
                if in_zone_mask is not None and bool(in_zone_mask[i]):
                    zone_tag = " [zone]"
                labels.append(f"#{track_id} {name} {conf:.2f}{zone_tag}")
                if track_id >= 0:
                    unique_ids.add(track_id)
                class_counts[name] = class_counts.get(name, 0) + 1
                xyxy = detections.xyxy[i].tolist()
                events.append(
                    {
                        "frame": frame_idx,
                        "track_id": track_id,
                        "class": name,
                        "confidence": conf,
                        "xyxy": xyxy,
                        "in_zone": bool(in_zone_mask[i])
                        if in_zone_mask is not None
                        else None,
                    }
                )

            annotated = frame.copy()
            if polygon_annotator is not None:
                try:
                    annotated = polygon_annotator.annotate(scene=annotated)
                except TypeError:
                    annotated = polygon_annotator.annotate(annotated)
            if line_annotator is not None and line_zone is not None:
                try:
                    annotated = line_annotator.annotate(
                        annotated, line_counter=line_zone
                    )
                except TypeError:
                    annotated = line_annotator.annotate(annotated, line_zone)
            annotated = trace_annotator.annotate(annotated, detections)
            annotated = box_annotator.annotate(annotated, detections)
            annotated = label_annotator.annotate(annotated, detections, labels)

            line_in = int(getattr(line_zone, "in_count", 0) or 0) if line_zone else 0
            line_out = int(getattr(line_zone, "out_count", 0) or 0) if line_zone else 0
            hud = (
                f"tracks:{len(unique_ids)}  "
                f"frame_dets:{len(detections)}  "
                f"model:{detector.model_name}"
            )
            if enable_zones:
                hud += f"  zone:{zone_in_frames}  line:{line_in}/{line_out}"
            (tw, th), _ = cv2.getTextSize(hud, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(annotated, (8, 8), (16 + tw, 16 + th), (0, 0, 0), -1)
            cv2.putText(
                annotated,
                hud,
                (12, 12 + th),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            sink.write_frame(annotated)
            frames_processed += 1

            if show_preview:
                preview = cv2.resize(annotated, (960, 540))
                cv2.imshow("skytrace", preview)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    if show_preview:
        cv2.destroyAllWindows()

    line_in = int(getattr(line_zone, "in_count", 0) or 0) if line_zone else 0
    line_out = int(getattr(line_zone, "out_count", 0) or 0) if line_zone else 0

    payload = {
        "source": str(source),
        "output": str(output),
        "model": detector.model_name,
        "backend": detector._mode,
        "classes": classes or DEFAULT_CLASSES,
        "unique_tracks": len(unique_ids),
        "class_counts": class_counts,
        "frames_processed": frames_processed,
        "zones": {
            "enabled": enable_zones,
            "zone_detection_hits": zone_in_frames,
            "line_in": line_in,
            "line_out": line_out,
        },
        "events": events,
    }
    events_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return PipelineResult(
        output_video=output,
        events_json=events_path,
        unique_tracks=len(unique_ids),
        class_counts=class_counts,
        frames_processed=frames_processed,
        model_name=detector.model_name,
        zone_in_frames=zone_in_frames,
        line_in=line_in,
        line_out=line_out,
        zone_enabled=enable_zones,
    )
