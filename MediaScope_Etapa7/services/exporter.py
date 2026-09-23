"""Exportación de resultados de MediaScope a un reporte Markdown."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def _format_time(value: Any) -> str:
    if value is None:
        return "No ejecutado"
    return f"{float(value):.1f} ms"


def export_markdown_report(
    report_markdown: str,
    metadata: dict[str, Any],
    output_dir: Path | None = None,
) -> str:
    """Crea un archivo descargable con resultados y trazabilidad técnica."""

    generated_at = datetime.now().astimezone()
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"reporte_mediascope_{generated_at:%Y%m%d_%H%M%S}_"
        f"{uuid4().hex[:8]}.md"
    )
    output_path = output_dir / filename

    detection = metadata["vision_detection"]
    captioning = metadata["vision_captioning"]
    speech = metadata["speech_recognition"]
    sound = metadata["sound_classification"]
    tts = metadata["text_to_speech"]

    content = f"""# Reporte exportado de MediaScope

**Fecha de generación:** {generated_at:%Y-%m-%d %H:%M:%S %Z}  
**Modo de ejecución:** {metadata['mode']}  
**Tipo de reporte:** {metadata['report_type']}  
**Umbral de confianza:** {metadata['confidence_threshold']:.0%}

---

{report_markdown.strip()}

---

## Trazabilidad del pipeline

| Modelo | Función | Ejecutado | Dispositivo | Inferencia |
| --- | --- | --- | --- | --- |
| `{detection['model']}` | Detección visual | {detection['loaded']} | {detection['device']} | {_format_time(detection['inference_ms'])} |
| `{captioning['model']}` | Descripción visual | {captioning['loaded']} | {captioning['device']} | {_format_time(captioning['inference_ms'])} |
| `{speech['model']}` | Transcripción | {speech['loaded']} | {speech['device']} | {_format_time(speech['inference_ms'])} |
| `{sound['model']}` | Clasificación acústica | {sound['loaded']} | {sound['device']} | {_format_time(sound['inference_ms'])} |
| `{tts['model']}` | Narración en español | {tts['loaded']} | {tts['device']} | {_format_time(tts['inference_ms'])} |

## Resumen de entradas

- **Imagen:** {metadata['image']['summary']}
- **Audio:** {metadata['audio']['summary']}
- **Audio procesado:** {speech['processed_seconds']:.1f} segundos
- **Segmentos acústicos:** {sound['segments_analyzed']}
- **Duración de la narración:** {tts['duration_seconds']:.1f} segundos

## Nota de uso responsable

Este documento contiene estimaciones producidas por modelos de inteligencia
artificial. Los resultados deben verificarse antes de utilizarlos en decisiones
importantes.
"""

    output_path.write_text(content, encoding="utf-8")
    return str(output_path)
