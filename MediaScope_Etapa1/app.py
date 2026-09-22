"""Interfaz base de MediaScope.

Etapa 1: adquisición, validación y presentación de entradas.
Los modelos de IA se incorporarán de forma incremental en las etapas siguientes.
"""

from __future__ import annotations

import os
from typing import Any

import gradio as gr

from config import (
    APP_DESCRIPTION,
    APP_SUBTITLE,
    APP_TITLE,
    DEFAULT_CONFIDENCE,
    MAX_AUDIO_SECONDS,
)
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


def analyze_stage_one(
    image: Any,
    audio_path: str | None,
    report_type: str,
    confidence: float,
) -> tuple[Any, ...]:
    """Valida las entradas y confirma que la interfaz está lista.

    Esta función no ejecuta modelos todavía. Devuelve resultados de demostración
    claramente identificados como pendientes para evitar confundirlos con
    inferencias reales.
    """

    if image is None and not audio_path:
        raise gr.Error("Carga al menos una imagen o un audio para continuar.")

    image_info = inspect_image(image)
    audio_info = inspect_audio(audio_path, MAX_AUDIO_SECONDS)

    missing = []
    if image is None:
        missing.append("imagen")
    if not audio_path:
        missing.append("audio")

    if missing:
        gr.Warning(
            "Análisis parcial de interfaz: falta " + " y ".join(missing) + "."
        )
        mode = "Validación parcial"
    else:
        mode = "Validación multimodal completa"

    status = (
        "<div class='status-card'><strong>✅ Etapa 1 operativa</strong><br>"
        f"{mode}. Las entradas fueron recibidas correctamente. "
        "Los resultados de IA se habilitarán en las siguientes etapas.</div>"
    )

    placeholder_caption = (
        "Pendiente — BLIP se integrará en la etapa de descripción visual."
        if image is not None
        else "No se proporcionó una imagen."
    )
    placeholder_transcript = (
        "Pendiente — Whisper se integrará en la etapa de reconocimiento del habla."
        if audio_path
        else "No se proporcionó un audio."
    )

    report = f"""
### Comprobación de la interfaz

- **Modo:** {mode}
- **Tipo de reporte seleccionado:** {report_type}
- **Umbral de confianza configurado:** {confidence:.0%}
- **Imagen:** {image_info['summary']}
- **Audio:** {audio_info['summary']}

> Esta salida únicamente valida el flujo de la interfaz. Todavía no representa
> una predicción de los modelos de inteligencia artificial.
"""

    metadata = {
        "stage": 1,
        "mode": mode,
        "report_type": report_type,
        "confidence_threshold": round(float(confidence), 2),
        "image": image_info,
        "audio": audio_info,
        "models_loaded": False,
    }

    # La imagen de entrada se devuelve sin anotaciones únicamente como vista previa.
    return (
        status,
        image,
        [],
        placeholder_caption,
        placeholder_transcript,
        [],
        report,
        None,
        metadata,
    )


def reset_interface() -> tuple[Any, ...]:
    """Restablece entradas, controles y salidas a sus valores iniciales."""

    return (
        None,
        None,
        "Detallado",
        DEFAULT_CONFIDENCE,
        "<div class='status-card'><strong>Estado:</strong> esperando archivos.</div>",
        None,
        [],
        "",
        "",
        [],
        "",
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

                with gr.Row():
                    analyze_button = gr.Button(
                        "Analizar contenido",
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
                            label="Eventos acústicos",
                            interactive=False,
                        )

                    with gr.Tab("Reporte multimodal"):
                        report_output = gr.Markdown()
                        narration_output = gr.Audio(
                            label="Narración generada",
                            interactive=False,
                        )

                    with gr.Tab("Detalles técnicos"):
                        metadata_output = gr.JSON(
                            label="Metadatos de ejecución"
                        )

        gr.Markdown(
            "<div class='footer-note'>MediaScope · Etapa 1 · Interfaz y validación de entradas</div>"
        )

        analyze_button.click(
            fn=analyze_stage_one,
            inputs=[image_input, audio_input, report_type, confidence],
            outputs=[
                status_output,
                annotated_image,
                object_table,
                caption_output,
                transcript_output,
                sound_table,
                report_output,
                narration_output,
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
                status_output,
                annotated_image,
                object_table,
                caption_output,
                transcript_output,
                sound_table,
                report_output,
                narration_output,
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
