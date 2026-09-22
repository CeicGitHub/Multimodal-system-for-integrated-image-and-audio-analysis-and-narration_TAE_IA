"""Configuración central de MediaScope."""

APP_TITLE = "MediaScope"
APP_SUBTITLE = "Análisis integrado y narración de imagen y audio"
APP_DESCRIPTION = (
    "Carga una imagen y una grabación. En las siguientes etapas, el sistema "
    "detectará objetos, describirá la escena, transcribirá el habla, reconocerá "
    "sonidos ambientales y generará un reporte narrado."
)

DEFAULT_CONFIDENCE = 0.35
MAX_AUDIO_SECONDS = 30

# Identificadores previstos para las etapas posteriores.
VISION_DETECTION_MODEL = "yolo11n.pt"
VISION_CAPTION_MODEL = "Salesforce/blip-image-captioning-base"
SPEECH_RECOGNITION_MODEL = "openai/whisper-base"
SOUND_CLASSIFICATION_MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"
TEXT_TO_SPEECH_MODEL = "facebook/mms-tts-spa"
