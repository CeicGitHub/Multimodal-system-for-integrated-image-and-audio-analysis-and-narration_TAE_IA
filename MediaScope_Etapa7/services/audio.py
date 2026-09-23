"""Análisis auditivo de MediaScope mediante Whisper y AST."""

from __future__ import annotations

from collections import defaultdict
from time import perf_counter
from typing import Any

import librosa
import numpy as np
import torch
from transformers import pipeline

from config import (
    MAX_AUDIO_SECONDS,
    SOUND_CLASSIFICATION_MODEL,
    SPEECH_RECOGNITION_MODEL,
)


_asr_pipeline: Any | None = None
_sound_pipeline: Any | None = None

LANGUAGE_OPTIONS: dict[str, str | None] = {
    "Automático": None,
    "Español": "spanish",
    "Inglés": "english",
}


def _runtime_device() -> tuple[int, str, torch.dtype]:
    """Selecciona GPU con float16 o CPU con float32."""

    if torch.cuda.is_available():
        return 0, "cuda:0", torch.float16
    return -1, "cpu", torch.float32


def _get_asr_pipeline() -> Any:
    """Carga Whisper una sola vez y conserva el modelo en memoria."""

    global _asr_pipeline
    if _asr_pipeline is None:
        device, _, dtype = _runtime_device()
        _asr_pipeline = pipeline(
            task="automatic-speech-recognition",
            model=SPEECH_RECOGNITION_MODEL,
            device=device,
            dtype=dtype,
        )
    return _asr_pipeline


def _get_sound_pipeline() -> Any:
    """Carga AST una sola vez y conserva el modelo en memoria."""

    global _sound_pipeline
    if _sound_pipeline is None:
        device, _, dtype = _runtime_device()
        _sound_pipeline = pipeline(
            task="audio-classification",
            model=SOUND_CLASSIFICATION_MODEL,
            device=device,
            dtype=dtype,
        )
    return _sound_pipeline


def _format_timestamp(seconds: float) -> str:
    """Convierte segundos a una marca de tiempo MM:SS."""

    total_seconds = max(0, int(round(seconds)))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


def _classify_sound(
    waveform: np.ndarray,
    sample_rate: int,
) -> dict[str, Any]:
    """Clasifica fragmentos consecutivos de hasta 10 segundos con AST."""

    classifier = _get_sound_pipeline()
    segment_samples = 10 * sample_rate
    sound_table: list[list[Any]] = []
    scores_by_label: dict[str, list[float]] = defaultdict(list)

    started_at = perf_counter()
    segments_analyzed = 0
    for start_sample in range(0, waveform.size, segment_samples):
        end_sample = min(start_sample + segment_samples, waveform.size)
        segment = waveform[start_sample:end_sample]
        if segment.size < sample_rate // 2:
            continue

        predictions = classifier(
            {"array": segment, "sampling_rate": sample_rate},
            top_k=3,
        )
        start_seconds = start_sample / float(sample_rate)
        end_seconds = end_sample / float(sample_rate)
        interval = (
            f"{_format_timestamp(start_seconds)}–{_format_timestamp(end_seconds)}"
        )

        for prediction in predictions:
            label = str(prediction["label"])
            score = float(prediction["score"])
            scores_by_label[label].append(score)
            sound_table.append([interval, label, round(score, 3)])

        segments_analyzed += 1

    elapsed_ms = (perf_counter() - started_at) * 1000
    ranked_labels = sorted(
        (
            (label, max(scores))
            for label, scores in scores_by_label.items()
        ),
        key=lambda item: item[1],
        reverse=True,
    )[:3]

    if ranked_labels:
        dominant_text = ", ".join(
            f"{label} ({score:.0%})" for label, score in ranked_labels
        )
        summary = f"AST identificó principalmente: {dominant_text}."
    else:
        summary = "AST no obtuvo categorías acústicas para el audio."

    return {
        "sound_table": sound_table,
        "summary": summary,
        "segments_analyzed": segments_analyzed,
        "inference_ms": round(elapsed_ms, 1),
    }


def analyze_audio(
    audio_path: str | None,
    language_option: str = "Automático",
) -> dict[str, Any]:
    """Decodifica hasta 30 segundos, transcribe y clasifica el audio."""

    _, device_label, _ = _runtime_device()
    if not audio_path:
        return {
            "provided": False,
            "transcript": "No se proporcionó un audio.",
            "summary": "No se proporcionó un audio.",
            "model": SPEECH_RECOGNITION_MODEL,
            "model_loaded": False,
            "device": device_label,
            "language_mode": language_option,
            "processed_seconds": 0.0,
            "truncated": False,
            "inference_ms": None,
            "sound_table": [],
            "sound_summary": "No se proporcionó un audio.",
            "sound_model": SOUND_CLASSIFICATION_MODEL,
            "sound_model_loaded": False,
            "sound_device": device_label,
            "sound_segments": 0,
            "sound_inference_ms": None,
        }

    # Se carga un pequeño margen adicional para saber si el audio fue truncado.
    waveform, sample_rate = librosa.load(
        audio_path,
        sr=16_000,
        mono=True,
        duration=MAX_AUDIO_SECONDS + 0.5,
    )
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.size == 0:
        raise ValueError("El archivo de audio está vacío o no pudo decodificarse.")

    maximum_samples = MAX_AUDIO_SECONDS * sample_rate
    truncated = waveform.size > maximum_samples
    waveform = waveform[:maximum_samples]
    processed_seconds = waveform.size / float(sample_rate)

    asr = _get_asr_pipeline()
    requested_language = LANGUAGE_OPTIONS.get(language_option)
    generation_options: dict[str, str] = {"task": "transcribe"}
    if requested_language:
        generation_options["language"] = requested_language

    started_at = perf_counter()
    with torch.inference_mode():
        result = asr(
            {"array": waveform, "sampling_rate": sample_rate},
            generate_kwargs=generation_options,
        )
    elapsed_ms = (perf_counter() - started_at) * 1000

    transcript = str(result.get("text", "")).strip()
    if not transcript:
        transcript = "No se reconoció habla inteligible en el audio."

    truncation_note = " El audio se limitó a 30 segundos." if truncated else ""
    summary = (
        f"Whisper procesó {processed_seconds:.1f} s de audio en modo "
        f"{language_option.lower()}.{truncation_note}"
    )
    sound_result = _classify_sound(waveform, sample_rate)

    return {
        "provided": True,
        "transcript": transcript,
        "summary": summary,
        "model": SPEECH_RECOGNITION_MODEL,
        "model_loaded": True,
        "device": device_label,
        "language_mode": language_option,
        "processed_seconds": round(processed_seconds, 2),
        "truncated": truncated,
        "inference_ms": round(elapsed_ms, 1),
        "sound_table": sound_result["sound_table"],
        "sound_summary": sound_result["summary"],
        "sound_model": SOUND_CLASSIFICATION_MODEL,
        "sound_model_loaded": True,
        "sound_device": device_label,
        "sound_segments": sound_result["segments_analyzed"],
        "sound_inference_ms": sound_result["inference_ms"],
    }
