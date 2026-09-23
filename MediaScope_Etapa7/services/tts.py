"""Síntesis local de la narración en español mediante MMS-TTS."""

from __future__ import annotations

import re
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

import numpy as np
import torch
from scipy.io import wavfile
from transformers import AutoTokenizer, VitsModel

from config import TEXT_TO_SPEECH_MODEL


_tokenizer: Any | None = None
_model: VitsModel | None = None


def _runtime_device() -> torch.device:
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def _get_tts() -> tuple[Any, VitsModel]:
    """Carga MMS-TTS una sola vez y conserva sus componentes en memoria."""

    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(TEXT_TO_SPEECH_MODEL)
        _model = VitsModel.from_pretrained(TEXT_TO_SPEECH_MODEL)
        _model = _model.to(_runtime_device())
        _model.eval()
    return _tokenizer, _model


def _clean_text(text: str) -> str:
    clean = re.sub(r"[#*_`>|]", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:900]


def _split_text(text: str, maximum_chars: int = 230) -> list[str]:
    """Divide el reporte para evitar secuencias demasiado largas en VITS."""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        words = sentence.split()
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > maximum_chars and current:
                chunks.append(current)
                current = word
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks


def synthesize_report(text: str) -> dict[str, Any]:
    """Genera un WAV reproducible desde el reporte fusionado."""

    clean_text = _clean_text(text)
    if not clean_text:
        raise ValueError("El reporte no contiene texto que pueda narrarse.")

    tokenizer, model = _get_tts()
    device = _runtime_device()
    sample_rate = int(model.config.sampling_rate)
    silence = np.zeros(int(sample_rate * 0.18), dtype=np.float32)
    waveforms: list[np.ndarray] = []
    chunks = _split_text(clean_text)

    started_at = perf_counter()
    for index, chunk in enumerate(chunks):
        inputs = tokenizer(chunk, return_tensors="pt")
        inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
        torch.manual_seed(42 + index)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(42 + index)

        with torch.inference_mode():
            waveform = model(**inputs).waveform[0]
        audio = waveform.detach().float().cpu().numpy()
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 1.0:
            audio = audio / peak
        waveforms.append(audio.astype(np.float32))
        if index < len(chunks) - 1:
            waveforms.append(silence)

    combined = np.concatenate(waveforms)
    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"narracion_{uuid4().hex}.wav"
    wavfile.write(output_path, sample_rate, combined)
    elapsed_ms = (perf_counter() - started_at) * 1000

    return {
        "path": str(output_path),
        "model": TEXT_TO_SPEECH_MODEL,
        "model_loaded": True,
        "device": str(device),
        "sample_rate": sample_rate,
        "duration_seconds": round(combined.size / sample_rate, 2),
        "chunks": len(chunks),
        "inference_ms": round(elapsed_ms, 1),
    }
