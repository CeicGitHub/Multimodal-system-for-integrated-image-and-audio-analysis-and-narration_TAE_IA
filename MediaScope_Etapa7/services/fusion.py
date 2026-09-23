"""Fusión determinista de los resultados visuales y auditivos de MediaScope."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


OBJECT_NAMES_ES: dict[str, tuple[str, str]] = {
    "person": ("persona", "personas"),
    "bicycle": ("bicicleta", "bicicletas"),
    "car": ("automóvil", "automóviles"),
    "motorcycle": ("motocicleta", "motocicletas"),
    "airplane": ("avión", "aviones"),
    "bus": ("autobús", "autobuses"),
    "train": ("tren", "trenes"),
    "truck": ("camión", "camiones"),
    "boat": ("barco", "barcos"),
    "traffic light": ("semáforo", "semáforos"),
    "fire hydrant": ("hidrante", "hidrantes"),
    "stop sign": ("señal de alto", "señales de alto"),
    "parking meter": ("parquímetro", "parquímetros"),
    "bench": ("banco", "bancos"),
    "bird": ("ave", "aves"),
    "cat": ("gato", "gatos"),
    "dog": ("perro", "perros"),
    "horse": ("caballo", "caballos"),
    "sheep": ("oveja", "ovejas"),
    "cow": ("vaca", "vacas"),
    "elephant": ("elefante", "elefantes"),
    "bear": ("oso", "osos"),
    "zebra": ("cebra", "cebras"),
    "giraffe": ("jirafa", "jirafas"),
    "backpack": ("mochila", "mochilas"),
    "umbrella": ("paraguas", "paraguas"),
    "handbag": ("bolso", "bolsos"),
    "tie": ("corbata", "corbatas"),
    "suitcase": ("maleta", "maletas"),
    "frisbee": ("disco volador", "discos voladores"),
    "skis": ("esquís", "esquís"),
    "snowboard": ("tabla de nieve", "tablas de nieve"),
    "sports ball": ("pelota", "pelotas"),
    "kite": ("cometa", "cometas"),
    "baseball bat": ("bate de béisbol", "bates de béisbol"),
    "baseball glove": ("guante de béisbol", "guantes de béisbol"),
    "skateboard": ("patineta", "patinetas"),
    "surfboard": ("tabla de surf", "tablas de surf"),
    "tennis racket": ("raqueta de tenis", "raquetas de tenis"),
    "bottle": ("botella", "botellas"),
    "wine glass": ("copa", "copas"),
    "cup": ("taza", "tazas"),
    "fork": ("tenedor", "tenedores"),
    "knife": ("cuchillo", "cuchillos"),
    "spoon": ("cuchara", "cucharas"),
    "bowl": ("tazón", "tazones"),
    "banana": ("plátano", "plátanos"),
    "apple": ("manzana", "manzanas"),
    "sandwich": ("sándwich", "sándwiches"),
    "orange": ("naranja", "naranjas"),
    "broccoli": ("brócoli", "brócolis"),
    "carrot": ("zanahoria", "zanahorias"),
    "hot dog": ("perrito caliente", "perritos calientes"),
    "pizza": ("pizza", "pizzas"),
    "donut": ("dona", "donas"),
    "cake": ("pastel", "pasteles"),
    "chair": ("silla", "sillas"),
    "couch": ("sofá", "sofás"),
    "potted plant": ("planta en maceta", "plantas en maceta"),
    "bed": ("cama", "camas"),
    "dining table": ("mesa", "mesas"),
    "toilet": ("inodoro", "inodoros"),
    "tv": ("televisor", "televisores"),
    "laptop": ("computadora portátil", "computadoras portátiles"),
    "mouse": ("ratón", "ratones"),
    "remote": ("control remoto", "controles remotos"),
    "keyboard": ("teclado", "teclados"),
    "cell phone": ("teléfono celular", "teléfonos celulares"),
    "microwave": ("microondas", "microondas"),
    "oven": ("horno", "hornos"),
    "toaster": ("tostadora", "tostadoras"),
    "sink": ("fregadero", "fregaderos"),
    "refrigerator": ("refrigerador", "refrigeradores"),
    "book": ("libro", "libros"),
    "clock": ("reloj", "relojes"),
    "vase": ("florero", "floreros"),
    "scissors": ("tijeras", "tijeras"),
    "teddy bear": ("oso de peluche", "osos de peluche"),
    "hair drier": ("secadora de cabello", "secadoras de cabello"),
    "toothbrush": ("cepillo de dientes", "cepillos de dientes"),
}


SOUND_TERMS_ES: tuple[tuple[str, str], ...] = (
    ("female speech", "voz femenina"),
    ("male speech", "voz masculina"),
    ("child speech", "voz infantil"),
    ("speech", "habla"),
    ("conversation", "conversación"),
    ("narration", "narración"),
    ("monologue", "monólogo"),
    ("singing", "canto"),
    ("rhythm and blues", "R&B"),
    ("music", "música"),
    ("laughter", "risa"),
    ("giggle", "risita"),
    ("applause", "aplausos"),
    ("clapping", "palmadas"),
    ("dog", "perro"),
    ("bark", "ladrido"),
    ("cat", "gato"),
    ("meow", "maullido"),
    ("bird", "ave"),
    ("siren", "sirena"),
    ("alarm", "alarma"),
    ("engine", "motor"),
    ("train", "tren"),
    ("rail", "tren"),
    ("vehicle", "vehículo"),
    ("traffic", "tráfico"),
    ("rain", "lluvia"),
    ("thunder", "trueno"),
    ("wind", "viento"),
    ("footstep", "pasos"),
    ("typing", "escritura con teclado"),
    ("keyboard", "teclado"),
    ("door", "puerta"),
    ("silence", "silencio"),
    ("noise", "ruido"),
)


def _natural_join(items: list[str]) -> str:
    if not items:
        return "ningún elemento identificable"
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " y " + items[-1]


def _object_name(class_name: str, count: int) -> str:
    singular, plural = OBJECT_NAMES_ES.get(
        class_name.lower(),
        (class_name, class_name),
    )
    return singular if count == 1 else plural


def _objects_text(object_counts: dict[str, int]) -> str:
    items = [
        f"{count} {_object_name(class_name, count)}"
        for class_name, count in object_counts.items()
    ]
    return _natural_join(items)


def _sound_name(label: str) -> str:
    lowered = label.lower()
    for term, translation in SOUND_TERMS_ES:
        if term in lowered:
            return translation
    return label


def translate_object_label(class_name: str, count: int = 1) -> str:
    """Traduce una clase COCO para mostrarla en la interfaz."""

    return _object_name(class_name, count)


def translate_sound_label(label: str) -> str:
    """Traduce las categorías acústicas más comunes de AudioSet."""

    return _sound_name(label)


def _dominant_sounds(sound_table: list[list[Any]]) -> list[tuple[str, float]]:
    scores: dict[str, list[float]] = defaultdict(list)
    for row in sound_table:
        if len(row) >= 3:
            scores[str(row[1])].append(float(row[2]))

    return sorted(
        ((label, max(values)) for label, values in scores.items()),
        key=lambda item: item[1],
        reverse=True,
    )


def _sounds_text(sound_table: list[list[Any]], include_scores: bool) -> str:
    ranked = _dominant_sounds(sound_table)
    if not ranked:
        return "ningún evento acústico concluyente"

    # Varias etiquetas de AudioSet pueden traducirse al mismo concepto, por
    # ejemplo "Music" y "Musical instrument". Se conserva la confianza mayor
    # de cada concepto traducido para evitar duplicados en el resumen.
    scores_by_translation: dict[str, float] = {}
    for label, score in ranked:
        translated = _sound_name(label)
        scores_by_translation[translated] = max(
            score,
            scores_by_translation.get(translated, 0.0),
        )

    unique_ranked = sorted(
        scores_by_translation.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]

    items = []
    for translated, score in unique_ranked:
        if include_scores:
            items.append(f"{translated} ({score:.0%})")
        else:
            items.append(translated)
    return _natural_join(items)


def _music_is_dominant(sound_table: list[list[Any]]) -> bool:
    """Indica si AST detectó música con una confianza significativa."""

    music_terms = ("music", "singing", "song", "rhythm and blues")
    return any(
        any(term in label.lower() for term in music_terms) and score >= 0.45
        for label, score in _dominant_sounds(sound_table)
    )


def _clip_text(text: str, limit: int) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    shortened = clean[:limit].rsplit(" ", maxsplit=1)[0]
    return shortened.rstrip(".,;:") + "…"


def build_multimodal_report(
    vision_result: dict[str, Any],
    audio_result: dict[str, Any],
    report_type: str,
    confidence: float,
) -> dict[str, str]:
    """Combina resultados de los cuatro modelos y produce texto narrable."""

    has_image = bool(vision_result["provided"])
    has_audio = bool(audio_result["provided"])
    objects = _objects_text(vision_result["object_counts"])
    sounds = _sounds_text(
        audio_result["sound_table"],
        include_scores=report_type == "Detallado",
    )
    music_dominant = _music_is_dominant(audio_result["sound_table"])
    caption = _clip_text(str(vision_result["caption"]), 320)
    transcript = _clip_text(str(audio_result["transcript"]), 500)

    integrated_parts: list[str] = []
    narration_parts = ["Reporte de MediaScope."]

    if has_image:
        if vision_result["detections_total"]:
            visual_sentence = f"En la imagen se detectaron {objects}."
        else:
            visual_sentence = (
                "En la imagen no se detectaron objetos por encima del umbral "
                "de confianza configurado."
            )
        integrated_parts.append(visual_sentence)
        narration_parts.append(visual_sentence)
        narration_parts.append(
            "La descripción contextual generada por BLIP fue: " + caption
        )

    if has_audio:
        sound_sentence = f"En el audio se identificaron principalmente {sounds}."
        integrated_parts.append(sound_sentence)
        narration_parts.append(sound_sentence)
        if transcript and not transcript.startswith("No se reconoció"):
            if music_dominant:
                narration_parts.append(
                    "Debido a la presencia dominante de música, la transcripción "
                    "de Whisper es orientativa y puede contener errores. Extracto: "
                    + _clip_text(transcript, 160)
                )
            else:
                spoken_limit = 160 if report_type == "Breve" else 320
                narration_parts.append(
                    "La transcripción obtenida fue: "
                    + _clip_text(transcript, spoken_limit)
                )
        else:
            narration_parts.append(
                "Whisper no reconoció habla inteligible en la grabación."
            )

    integrated_summary = " ".join(integrated_parts)
    if has_image and has_audio:
        mode_text = "La salida integra evidencia visual y auditiva."
    elif has_image:
        mode_text = "La salida se generó únicamente con evidencia visual."
    else:
        mode_text = "La salida se generó únicamente con evidencia auditiva."

    transcription_note = (
        " La presencia dominante de música puede reducir la precisión de Whisper."
        if has_audio and music_dominant
        else ""
    )

    if report_type == "Breve":
        markdown = f"""
### Reporte multimodal breve

{integrated_summary}

- **Descripción de BLIP:** {caption if has_image else "No aplica."}
- **Transcripción de Whisper:** {transcript if has_audio else "No aplica."}{transcription_note}

> {mode_text}
"""
    elif report_type == "Accesible":
        accessible_parts = []
        if has_image:
            accessible_parts.append(
                f"**Lo que aparece en la imagen:** {objects.capitalize()}."
                if vision_result["detections_total"]
                else "**Lo que aparece en la imagen:** no se identificaron objetos con suficiente seguridad."
            )
            accessible_parts.append(f"**Descripción adicional:** {caption}")
        if has_audio:
            accessible_parts.append(f"**Lo que se escucha:** {sounds.capitalize()}.")
            accessible_parts.append(f"**Palabras reconocidas:** {transcript}")
            if music_dominant:
                accessible_parts.append(
                    "**Aviso:** la música domina la grabación, por lo que las "
                    "palabras reconocidas pueden contener errores."
                )
        markdown = """
### Reporte accesible

""" + "\n\n".join(accessible_parts) + f"""

> El texto usa frases directas para facilitar su lectura. {mode_text}
"""
    else:
        visual_section = (
            f"""
### Evidencia visual

- **YOLO11n:** {vision_result['summary']}
- **BLIP:** {caption}
- **Umbral de detección:** {confidence:.0%}
- **Tiempo YOLO:** {vision_result['inference_ms']} ms
- **Tiempo BLIP:** {vision_result['caption_inference_ms']} ms
"""
            if has_image
            else "\n### Evidencia visual\n\nNo se proporcionó una imagen.\n"
        )
        audio_section = (
            f"""
### Evidencia auditiva

- **Whisper:** {transcript}{transcription_note}
- **AST:** eventos dominantes: {sounds}.
- **Duración procesada:** {audio_result['processed_seconds']:.1f} s
- **Tiempo Whisper:** {audio_result['inference_ms']} ms
- **Tiempo AST:** {audio_result['sound_inference_ms']} ms
"""
            if has_audio
            else "\n### Evidencia auditiva\n\nNo se proporcionó un audio.\n"
        )
        markdown = f"""
## Reporte multimodal integrado

### Resumen

{integrated_summary} {mode_text}

{visual_section}
{audio_section}
### Interpretación responsable

Los resultados son estimaciones automáticas. Las detecciones, la descripción,
la transcripción y los eventos acústicos deben verificarse antes de utilizarlos
en decisiones importantes.
"""

    narration_text = " ".join(narration_parts)
    return {
        "markdown": markdown.strip(),
        "narration_text": narration_text,
        "summary": f"{integrated_summary} {mode_text}".strip(),
    }
