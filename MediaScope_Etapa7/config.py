"""Configuración central de MediaScope."""

APP_TITLE = "MediaScope"
APP_SUBTITLE = "Análisis integrado y narración de imagen y audio"
APP_DESCRIPTION = (
    "Carga una imagen y una grabación. YOLO11n detecta los objetos presentes "
    "y BLIP genera una descripción contextual de la escena. Whisper transcribe "
    "el habla, AST identifica los sonidos ambientales y MMS-TTS narra en español "
    "el reporte multimodal integrado, que también puede descargarse con su "
    "trazabilidad técnica."
)

DEFAULT_CONFIDENCE = 0.35
MAX_AUDIO_SECONDS = 30

# Modelos que forman el pipeline multimodal completo.
VISION_DETECTION_MODEL = "yolo11n.pt"
VISION_CAPTION_MODEL = "Salesforce/blip-image-captioning-base"
SPEECH_RECOGNITION_MODEL = "openai/whisper-base"
SOUND_CLASSIFICATION_MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"
TEXT_TO_SPEECH_MODEL = "facebook/mms-tts-spa"
