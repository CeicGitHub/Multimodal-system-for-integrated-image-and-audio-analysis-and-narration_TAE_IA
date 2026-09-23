"""Entrega final de MediaScope: análisis, narración y reporte exportable."""

from __future__ import annotations

import os
import warnings
from typing import Any

# Estas advertencias pertenecen a dependencias y no afectan a la aplicación.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
warnings.filterwarnings(
    "ignore",
    message=".*HTTP_422_UNPROCESSABLE_ENTITY.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*return_token_timestamps.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*mel filter has all zero values.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*torch.jit.script.*deprecated.*",
)

import gradio as gr

from config import (
    APP_DESCRIPTION,
    APP_SUBTITLE,
    APP_TITLE,
    DEFAULT_CONFIDENCE,
    MAX_AUDIO_SECONDS,
)
from services.audio import LANGUAGE_OPTIONS, analyze_audio
from services.exporter import export_markdown_report
from services.fusion import (
    build_multimodal_report,
    translate_object_label,
    translate_sound_label,
)
from services.tts import synthesize_report
from services.vision import analyze_image
from utils.validation import inspect_audio, inspect_image


CUSTOM_CSS = """
.gradio-container {
    max-width: 1320px !important;
    margin: 0 auto !important;
}

.hero {
    padding: 1.1rem 1.3rem;
    border: 1px solid var(--border-color-primary);
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.10), rgba(14, 165, 233, 0.05));
    margin-bottom: 1rem;
}

.status-card {
    padding: 0.85rem 1rem;
    border-radius: 12px;
    border-left: 5px solid #2563eb;
    background: rgba(37, 99, 235, 0.07);
}

.footer-note {
    text-align: center;
    opacity: 0.75;
    margin-top: 1rem;
}
"""


def gradio_major_version() -> int:
    """Obtiene la versión mayor para mantener compatibilidad con Gradio 5 y 6."""

    try:
        return int(gr.__version__.split(".", maxsplit=1)[0])
    except (AttributeError, ValueError):
        return 6


def build_theme() -> gr.Theme:
    """Devuelve el tema visual utilizado por la aplicación."""

    return gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="sky",
        neutral_hue="slate",
    )


def analyze_final_pipeline(
    image: Any,
    audio_path: str | None,
    report_type: str,
    confidence: float,
    audio_language: str,
) -> tuple[Any, ...]:
    """Ejecuta el pipeline final y genera salidas visuales y descargables."""

    if image is None and not audio_path:
        raise gr.Error("Carga al menos una imagen o un audio para continuar.")

    image_info = inspect_image(image)
    audio_info = inspect_audio(audio_path, MAX_AUDIO_SECONDS)

    try:
        vision_result = analyze_image(image, confidence)
    except Exception as exc:
        raise gr.Error(
            f"No fue posible ejecutar el análisis visual (YOLO11n + BLIP): {exc}"
        ) from exc

    try:
        audio_result = analyze_audio(audio_path, audio_language)
    except Exception as exc:
        raise gr.Error(
            f"No fue posible analizar el audio con Whisper y AST: {exc}"
        ) from exc

    fusion_result = build_multimodal_report(
        vision_result,
        audio_result,
        report_type,
        confidence,
    )

    try:
        tts_result = synthesize_report(fusion_result["narration_text"])
    except Exception as exc:
        raise gr.Error(
            f"El análisis terminó, pero no fue posible generar la narración: {exc}"
        ) from exc

    missing = []
    if image is None:
        missing.append("imagen")
    if not audio_path:
        missing.append("audio")

    if missing:
        gr.Warning(
            "Análisis parcial de interfaz: falta " + " y ".join(missing) + "."
        )
        mode = "Análisis parcial"
    else:
        mode = "Análisis multimodal completo"

    vision_status = (
        "Análisis con YOLO11n y BLIP terminado: "
        f"{vision_result['detections_total']} objeto(s) y una descripción generada."
        if image is not None
        else "No se ejecutaron los modelos visuales porque no se proporcionó una imagen."
    )
    audio_status = (
        f"Audio procesado con Whisper y AST ({audio_result['processed_seconds']:.1f} s)."
        if audio_path
        else "No se proporcionó audio."
    )
    status = (
        "<div class='status-card'><strong>✅ MediaScope final listo</strong><br>"
        f"{mode}. {vision_status} {audio_status} "
        f"Reporte fusionado y narración generada ({tts_result['duration_seconds']:.1f} s)."
        "</div>"
    )

    metadata = {
        "stage": 7,
        "release": "final-r2",
        "mode": mode,
        "report_type": report_type,
        "confidence_threshold": round(float(confidence), 2),
        "image": image_info,
        "audio": audio_info,
        "vision_detection": {
            "model": vision_result["model"],
            "loaded": vision_result["model_loaded"],
            "device": vision_result["device"],
            "inference_ms": vision_result["inference_ms"],
            "detections_total": vision_result["detections_total"],
            "object_counts": vision_result["object_counts"],
        },
        "vision_captioning": {
            "model": vision_result["caption_model"],
            "loaded": vision_result["caption_model_loaded"],
            "device": vision_result["caption_device"],
            "inference_ms": vision_result["caption_inference_ms"],
            "caption": vision_result["caption"],
        },
        "speech_recognition": {
            "model": audio_result["model"],
            "loaded": audio_result["model_loaded"],
            "device": audio_result["device"],
            "language_mode": audio_result["language_mode"],
            "processed_seconds": audio_result["processed_seconds"],
            "truncated": audio_result["truncated"],
            "inference_ms": audio_result["inference_ms"],
        },
        "sound_classification": {
            "model": audio_result["sound_model"],
            "loaded": audio_result["sound_model_loaded"],
            "device": audio_result["sound_device"],
            "segments_analyzed": audio_result["sound_segments"],
            "inference_ms": audio_result["sound_inference_ms"],
            "summary": audio_result["sound_summary"],
        },
        "multimodal_fusion": {
            "report_type": report_type,
            "summary": fusion_result["summary"],
        },
        "text_to_speech": {
            "model": tts_result["model"],
            "loaded": tts_result["model_loaded"],
            "device": tts_result["device"],
            "sample_rate": tts_result["sample_rate"],
            "duration_seconds": tts_result["duration_seconds"],
            "chunks": tts_result["chunks"],
            "inference_ms": tts_result["inference_ms"],
        },
        "pending_models": [],
    }

    localized_object_table = [
        [translate_object_label(str(row[0]), int(row[1])), row[1], row[2]]
        for row in vision_result["object_table"]
    ]
    localized_sound_table = []
    for row in audio_result["sound_table"]:
        original_label = str(row[1])
        translated_label = translate_sound_label(original_label)
        display_label = (
            translated_label
            if translated_label.casefold() == original_label.casefold()
            else f"{translated_label} ({original_label})"
        )
        localized_sound_table.append([row[0], display_label, row[2]])
    report_file = export_markdown_report(
        fusion_result["markdown"],
        metadata,
    )

    return (
        status,
        vision_result["annotated_image"],
        localized_object_table,
        vision_result["caption"],
        audio_result["transcript"],
        localized_sound_table,
        fusion_result["markdown"],
        tts_result["path"],
        report_file,
        metadata,
    )


def reset_interface() -> tuple[Any, ...]:
    """Restablece entradas, controles y salidas a sus valores iniciales."""

    return (
        None,
        None,
        "Detallado",
        DEFAULT_CONFIDENCE,
        "Automático",
        "<div class='status-card'><strong>Estado:</strong> esperando archivos.</div>",
        None,
        [],
        "",
        "",
        [],
        "",
        None,
        None,
        {},
    )


def build_app() -> gr.Blocks:
    """Construye y conecta todos los componentes de Gradio."""

    blocks_options: dict[str, Any] = {"title": APP_TITLE}
    if gradio_major_version() < 6:
        blocks_options.update(theme=build_theme(), css=CUSTOM_CSS)

    with gr.Blocks(**blocks_options) as demo:
        gr.HTML(
            f"""
            <section class="hero">
                <h1>{APP_TITLE}</h1>
                <h3>{APP_SUBTITLE}</h3>
                <p>{APP_DESCRIPTION}</p>
            </section>
            """
        )

        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=360):
                gr.Markdown("## 1. Entradas")
                image_input = gr.Image(
                    label="Imagen de entrada",
                    sources=["upload", "webcam", "clipboard"],
                    type="pil",
                    height=360,
                )
                audio_input = gr.Audio(
                    label=f"Audio de entrada (recomendado: máximo {MAX_AUDIO_SECONDS} s)",
                    sources=["upload", "microphone"],
                    type="filepath",
                )

                with gr.Row():
                    report_type = gr.Dropdown(
                        choices=["Breve", "Detallado", "Accesible"],
                        value="Detallado",
                        label="Tipo de reporte",
                    )
                    confidence = gr.Slider(
                        minimum=0.10,
                        maximum=0.90,
                        value=DEFAULT_CONFIDENCE,
                        step=0.05,
                        label="Confianza mínima",
                    )

                audio_language = gr.Dropdown(
                    choices=list(LANGUAGE_OPTIONS),
                    value="Automático",
                    label="Idioma del audio",
                    info="Automático, español o inglés",
                )

                with gr.Accordion("Recomendación para la demostración", open=False):
                    gr.Markdown(
                        "Carga archivos de hasta 30 segundos, utiliza el reporte "
                        "**Detallado** y mantén el umbral en **35%**. La primera "
                        "ejecución puede tardar más mientras los modelos se cargan."
                    )

                with gr.Row():
                    analyze_button = gr.Button(
                        "Analizar y narrar",
                        variant="primary",
                        scale=2,
                    )
                    clear_button = gr.Button("Limpiar", variant="secondary")

            with gr.Column(scale=7, min_width=420):
                gr.Markdown("## 2. Resultados")
                status_output = gr.HTML(
                    "<div class='status-card'><strong>Estado:</strong> esperando archivos.</div>"
                )

                with gr.Tabs():
                    with gr.Tab("Análisis visual"):
                        annotated_image = gr.Image(
                            label="Imagen procesada",
                            interactive=False,
                            height=360,
                        )
                        object_table = gr.Dataframe(
                            headers=["Objeto", "Cantidad", "Confianza"],
                            datatype=["str", "number", "number"],
                            label="Objetos detectados",
                            interactive=False,
                        )
                        caption_output = gr.Textbox(
                            label="Descripción de la escena",
                            lines=3,
                            interactive=False,
                        )

                    with gr.Tab("Análisis auditivo"):
                        transcript_output = gr.Textbox(
                            label="Transcripción",
                            lines=5,
                            interactive=False,
                        )
                        sound_table = gr.Dataframe(
                            headers=["Intervalo", "Sonido", "Confianza"],
                            datatype=["str", "str", "number"],
                            label="Eventos acústicos detectados por AST",
                            interactive=False,
                        )

                    with gr.Tab("Reporte multimodal"):
                        report_output = gr.Markdown()
                        narration_output = gr.Audio(
                            label="Narración del reporte en español",
                            interactive=False,
                        )
                        report_file_output = gr.File(
                            label="Descargar reporte técnico (.md)",
                            interactive=False,
                        )

                    with gr.Tab("Detalles técnicos"):
                        metadata_output = gr.JSON(
                            label="Metadatos de ejecución"
                        )

                    with gr.Tab("Acerca del pipeline"):
                        gr.Markdown(
                            """
### Arquitectura multimodal mixta

Las entradas se validan y después se procesan por dos ramas. La rama visual
ejecuta detección y descripción; la rama auditiva ejecuta transcripción y
clasificación ambiental. Los resultados disponibles se fusionan y finalmente
se convierten en una narración en español.

| Modelo | Modalidad | Función |
| --- | --- | --- |
| YOLO11n | Imagen | Detección y localización de objetos |
| BLIP | Imagen | Descripción contextual de la escena |
| Whisper | Audio | Reconocimiento automático del habla |
| AST | Audio | Clasificación de eventos acústicos |
| MMS-TTS | Salida de audio | Narración del reporte integrado |

### Condiciones obligatorias cubiertas

- ✅ Dos modelos de visión con tareas distintas.
- ✅ Audio analizado y generado por modelos de IA.
- ✅ Aplicación interactiva ejecutada en vivo con Gradio.
- ✅ Flujo condicional cuando falta una modalidad.

> Las predicciones son probabilísticas y deben interpretarse como resultados
> automáticos sujetos a verificación.
"""
                        )

        gr.Markdown(
            "<div class='footer-note'>MediaScope · Entrega final · "
            "YOLO11n + BLIP + Whisper + AST + MMS-TTS</div>"
        )

        analyze_button.click(
            fn=analyze_final_pipeline,
            inputs=[image_input, audio_input, report_type, confidence, audio_language],
            outputs=[
                status_output,
                annotated_image,
                object_table,
                caption_output,
                transcript_output,
                sound_table,
                report_output,
                narration_output,
                report_file_output,
                metadata_output,
            ],
        )

        clear_button.click(
            fn=reset_interface,
            inputs=[],
            outputs=[
                image_input,
                audio_input,
                report_type,
                confidence,
                audio_language,
                status_output,
                annotated_image,
                object_table,
                caption_output,
                transcript_output,
                sound_table,
                report_output,
                narration_output,
                report_file_output,
                metadata_output,
            ],
        )

    return demo


if __name__ == "__main__":
    share_enabled = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")

    app = build_app()
    app.queue(default_concurrency_limit=1, max_size=20)
    launch_options: dict[str, Any] = {
        "server_name": server_name,
        "server_port": 7860,
        "share": share_enabled,
        "inbrowser": True,
    }
    if gradio_major_version() >= 6:
        launch_options.update(theme=build_theme(), css=CUSTOM_CSS)

    app.launch(
        **launch_options,
    )
