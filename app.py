"""Gradio UI for SkyTrace."""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from skytrace.config import (
    DEFAULT_BACKEND,
    DEFAULT_CLASSES,
    DEFAULT_ROBOFLOW_MODEL,
    OUTPUTS_DIR,
    ROBOFLOW_API_KEY,
    ROBOFLOW_MODELS,
)
from skytrace.pipeline import process_video
from skytrace.samples import ensure_all_samples, list_local_sources


def _sample_choices() -> list[str]:
    return [str(p) for p in list_local_sources()]


def prepare_samples():
    result = ensure_all_samples()
    lines = ["Samples ready:"]
    for key, paths in result.items():
        for path in paths:
            lines.append(f"- {key}: {path.name}")
    choices = _sample_choices()
    return (
        "\n".join(lines),
        gr.update(choices=choices, value=choices[0] if choices else None),
    )


def run_demo(
    sample_path: str | None,
    upload_path: str | None,
    backend: str,
    rf_model: str,
    classes_text: str,
    confidence: float,
    max_frames: float,
    enable_zones: bool,
):
    source = upload_path or sample_path
    if not source:
        return None, "Pick a bundled sample or upload a video first."

    source_path = Path(source)
    if not source_path.exists():
        return None, f"File not found: {source_path}"

    classes = [c.strip() for c in classes_text.split(",") if c.strip()]
    max_frames_i = int(max_frames) if max_frames and float(max_frames) > 0 else None

    try:
        result = process_video(
            source=source_path,
            classes=classes or None,
            confidence=float(confidence),
            max_frames=max_frames_i,
            backend=backend,
            roboflow_model=rf_model,
            enable_zones=bool(enable_zones),
        )
    except Exception as exc:  # noqa: BLE001
        return None, f"Error: {exc}"

    summary = (
        f"Model: {result.model_name}\n"
        f"Frames: {result.frames_processed}\n"
        f"Unique tracks: {result.unique_tracks}\n"
        f"Class hits: {result.class_counts}\n"
        f"Zones: enabled={result.zone_enabled} "
        f"hits={result.zone_in_frames} "
        f"line={result.line_in}/{result.line_out}\n"
        f"Events JSON: {result.events_json}"
    )
    return str(result.output_video), summary


def build_ui() -> gr.Blocks:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    choices = _sample_choices()
    key_note = "set" if ROBOFLOW_API_KEY else "missing — using YOLO-World"
    model_choices = list(ROBOFLOW_MODELS.keys()) + [DEFAULT_ROBOFLOW_MODEL]

    with gr.Blocks(title="SkyTrace") as demo:
        gr.Markdown(
            f"""
            # SkyTrace
            Airborne detection & tracking with
            [Supervision](https://supervision.roboflow.com/) + Roboflow Inference / YOLO-World.

            Roboflow API key: **{key_note}**. Default backend: `{DEFAULT_BACKEND}`
            (`local` = on-device Inference after weight download;
            `roboflow` = cloud HTTP per frame; `world` = offline YOLO-World).

            Model aliases: `airborne`, `overhead_plane`, `drone`, `drone_yolo11`, `tello`.
            """
        )

        fetch_btn = gr.Button("Fetch public samples", variant="secondary")
        fetch_status = gr.Textbox(label="Fetch status", lines=6)

        sample = gr.Dropdown(
            label="Bundled sample",
            choices=choices,
            value=choices[0] if choices else None,
        )
        upload = gr.Video(label="Or upload your own video")

        with gr.Row():
            backend = gr.Dropdown(
                label="Backend",
                choices=["local", "world", "roboflow", "coco"],
                value=DEFAULT_BACKEND,
            )
            rf_model = gr.Dropdown(
                label="Roboflow model (alias or full id)",
                choices=model_choices,
                value="airborne",
                allow_custom_value=True,
            )

        classes = gr.Textbox(
            label="Classes (YOLO-World backend only)",
            value=", ".join(DEFAULT_CLASSES),
        )
        with gr.Row():
            conf = gr.Slider(0.05, 0.8, value=0.25, step=0.05, label="Confidence")
            max_frames = gr.Number(
                value=90,
                label="Max frames (0 = full video)",
                precision=0,
            )
            zones = gr.Checkbox(
                label="PolygonZone + LineZone counters",
                value=False,
            )

        run_btn = gr.Button("Run tracking", variant="primary")
        out_video = gr.Video(label="Annotated output")
        summary = gr.Textbox(label="Summary", lines=8)

        fetch_btn.click(fn=prepare_samples, outputs=[fetch_status, sample])
        run_btn.click(
            fn=run_demo,
            inputs=[
                sample,
                upload,
                backend,
                rf_model,
                classes,
                conf,
                max_frames,
                zones,
            ],
            outputs=[out_video, summary],
        )

    return demo


def main() -> None:
    demo = build_ui()
    demo.launch()


if __name__ == "__main__":
    main()
