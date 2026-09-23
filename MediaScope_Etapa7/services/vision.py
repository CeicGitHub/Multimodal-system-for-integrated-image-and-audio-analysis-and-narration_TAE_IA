"""Análisis visual de MediaScope mediante YOLO11n y BLIP."""

from __future__ import annotations

from collections import defaultdict
from time import perf_counter
from typing import Any

import numpy as np
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor
from ultralytics import YOLO

from config import VISION_CAPTION_MODEL, VISION_DETECTION_MODEL


# El modelo se conserva en memoria después de la primera inferencia para evitar
# cargarlo nuevamente cada vez que el usuario presiona el botón de análisis.
_detector: YOLO | None = None
_caption_processor: BlipProcessor | None = None
_caption_model: BlipForConditionalGeneration | None = None


def _runtime_device() -> tuple[int | str, str]:
    """Devuelve el dispositivo para Ultralytics y una etiqueta informativa."""

    if torch.cuda.is_available():
        return 0, f"cuda:0 — {torch.cuda.get_device_name(0)}"
    return "cpu", "cpu"


def _get_detector() -> YOLO:
    """Carga YOLO11n una sola vez y reutiliza la instancia."""

    global _detector
    if _detector is None:
        _detector = YOLO(VISION_DETECTION_MODEL)
    return _detector


def _get_captioner() -> tuple[BlipProcessor, BlipForConditionalGeneration]:
    """Carga BLIP una sola vez con precisión adecuada para GPU o CPU."""

    global _caption_processor, _caption_model
    if _caption_processor is None or _caption_model is None:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        _caption_processor = BlipProcessor.from_pretrained(
            VISION_CAPTION_MODEL,
            use_fast=False,
        )
        _caption_model = BlipForConditionalGeneration.from_pretrained(
            VISION_CAPTION_MODEL,
            dtype=dtype,
        )
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        _caption_model = _caption_model.to(device)
        _caption_model.eval()

    return _caption_processor, _caption_model


def _generate_caption(image: Image.Image) -> dict[str, Any]:
    """Genera una descripción no condicionada de la imagen con BLIP."""

    processor, model = _get_captioner()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    inputs = processor(images=image, return_tensors="pt")
    prepared_inputs: dict[str, torch.Tensor] = {}
    for name, tensor in inputs.items():
        if torch.is_floating_point(tensor):
            prepared_inputs[name] = tensor.to(device=device, dtype=dtype)
        else:
            prepared_inputs[name] = tensor.to(device=device)

    started_at = perf_counter()
    with torch.inference_mode():
        generated_ids = model.generate(
            **prepared_inputs,
            max_new_tokens=35,
            num_beams=3,
            repetition_penalty=1.15,
        )
    elapsed_ms = (perf_counter() - started_at) * 1000

    caption = processor.decode(generated_ids[0], skip_special_tokens=True).strip()
    if caption:
        caption = caption[0].upper() + caption[1:]
        if caption[-1] not in ".!?":
            caption += "."
    else:
        caption = "BLIP no pudo generar una descripción para esta imagen."

    return {
        "caption": caption,
        "model": VISION_CAPTION_MODEL,
        "model_loaded": True,
        "device": str(device),
        "inference_ms": round(elapsed_ms, 1),
    }


def analyze_image(image: Image.Image | None, confidence: float) -> dict[str, Any]:
    """Detecta objetos, genera la imagen anotada y resume los resultados."""

    _, device_label = _runtime_device()
    if image is None:
        return {
            "provided": False,
            "annotated_image": None,
            "object_table": [],
            "detections_total": 0,
            "object_counts": {},
            "summary": "No se proporcionó una imagen.",
            "model_loaded": False,
            "model": VISION_DETECTION_MODEL,
            "device": device_label,
            "inference_ms": None,
            "caption": "No se proporcionó una imagen.",
            "caption_model": VISION_CAPTION_MODEL,
            "caption_model_loaded": False,
            "caption_device": device_label.split(" — ", maxsplit=1)[0],
            "caption_inference_ms": None,
        }

    detector = _get_detector()
    device, device_label = _runtime_device()
    rgb_image = image.convert("RGB")

    started_at = perf_counter()
    predictions = detector.predict(
        source=rgb_image,
        conf=float(confidence),
        device=device,
        imgsz=640,
        verbose=False,
    )
    elapsed_ms = (perf_counter() - started_at) * 1000

    result = predictions[0]

    # result.plot() entrega un arreglo BGR; Gradio/PIL trabajan en RGB.
    annotated_bgr = result.plot(line_width=2, labels=True, conf=True)
    annotated_rgb = np.ascontiguousarray(annotated_bgr[:, :, ::-1])
    annotated_image = Image.fromarray(annotated_rgb)

    confidences_by_class: dict[str, list[float]] = defaultdict(list)
    if result.boxes is not None:
        class_ids = result.boxes.cls.detach().cpu().tolist()
        scores = result.boxes.conf.detach().cpu().tolist()

        for class_id, score in zip(class_ids, scores):
            class_name = str(result.names[int(class_id)])
            confidences_by_class[class_name].append(float(score))

    object_table: list[list[Any]] = []
    object_counts: dict[str, int] = {}
    for class_name in sorted(confidences_by_class):
        scores = confidences_by_class[class_name]
        count = len(scores)
        mean_confidence = sum(scores) / count
        object_counts[class_name] = count
        object_table.append([class_name, count, round(mean_confidence, 3)])

    detections_total = sum(object_counts.values())
    if detections_total:
        detected_items = ", ".join(
            f"{count} × {class_name}"
            for class_name, count in object_counts.items()
        )
        summary = f"YOLO11n detectó {detections_total} objeto(s): {detected_items}."
    else:
        summary = (
            "YOLO11n no detectó objetos por encima del umbral "
            f"de confianza de {float(confidence):.0%}."
        )

    caption_result = _generate_caption(rgb_image)

    return {
        "provided": True,
        "annotated_image": annotated_image,
        "object_table": object_table,
        "detections_total": detections_total,
        "object_counts": object_counts,
        "summary": summary,
        "model_loaded": True,
        "model": VISION_DETECTION_MODEL,
        "device": device_label,
        "inference_ms": round(elapsed_ms, 1),
        "caption": caption_result["caption"],
        "caption_model": caption_result["model"],
        "caption_model_loaded": caption_result["model_loaded"],
        "caption_device": caption_result["device"],
        "caption_inference_ms": caption_result["inference_ms"],
    }
