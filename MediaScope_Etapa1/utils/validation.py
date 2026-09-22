"""Validaciones ligeras para las entradas de la interfaz."""

from __future__ import annotations

import os
import wave
from typing import Any


def inspect_image(image: Any) -> dict[str, Any]:
    """Devuelve metadatos básicos de una imagen PIL sin ejecutar IA."""

    if image is None:
        return {
            "provided": False,
            "summary": "no proporcionada",
        }

    width, height = image.size
    mode = getattr(image, "mode", "desconocido")
    return {
        "provided": True,
        "width": int(width),
        "height": int(height),
        "color_mode": str(mode),
        "summary": f"{width} × {height} píxeles, modo {mode}",
    }


def _wav_duration_seconds(path: str) -> float | None:
    """Obtiene la duración de un WAV mediante la biblioteca estándar."""

    if not path.lower().endswith(".wav"):
        return None

    try:
        with wave.open(path, "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate) if rate else None
    except (wave.Error, OSError):
        return None


def inspect_audio(path: str | None, recommended_max_seconds: int) -> dict[str, Any]:
    """Devuelve metadatos disponibles sin decodificadores externos."""

    if not path:
        return {
            "provided": False,
            "summary": "no proporcionado",
        }

    file_name = os.path.basename(path)
    size_bytes = os.path.getsize(path) if os.path.exists(path) else 0
    extension = os.path.splitext(file_name)[1].lower() or "sin extensión"
    duration = _wav_duration_seconds(path)

    if duration is None:
        duration_text = "duración pendiente de decodificación"
    else:
        duration_text = f"{duration:.1f} s"

    exceeds_recommendation = (
        duration is not None and duration > recommended_max_seconds
    )

    return {
        "provided": True,
        "file_name": file_name,
        "extension": extension,
        "size_bytes": int(size_bytes),
        "duration_seconds": round(duration, 2) if duration is not None else None,
        "exceeds_recommended_duration": exceeds_recommendation,
        "summary": f"{extension}, {duration_text}, {size_bytes / 1024:.1f} KiB",
    }
