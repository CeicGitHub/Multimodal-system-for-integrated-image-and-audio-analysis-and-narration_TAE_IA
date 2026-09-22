# MediaScope — Etapa 1

Interfaz base para un sistema multimodal de análisis integrado y narración de
imagen y audio.

Esta primera etapa implementa:

- carga, captura y vista previa de imágenes;
- carga o grabación de audio;
- validación básica de entradas;
- selección del tipo de reporte;
- configuración del umbral de confianza;
- pestañas preparadas para resultados visuales, auditivos y multimodales;
- cola de solicitudes de Gradio;
- estructura modular para integrar los modelos posteriores.

Todavía no realiza inferencias de inteligencia artificial.

## Requisitos

- Python 3.10, 3.11 o 3.12.
- Navegador web actualizado.

## Instalación en Windows y VS Code

Abre la carpeta del proyecto en VS Code y ejecuta en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Si PowerShell bloquea temporalmente la activación del entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

La aplicación se abrirá en:

```text
http://127.0.0.1:7860
```

## Enlace público temporal

Para habilitar un enlace público de Gradio en PowerShell:

```powershell
$env:GRADIO_SHARE="true"
python app.py
```

Para volver al modo local:

```powershell
Remove-Item Env:GRADIO_SHARE
```

## Verificación de la Etapa 1

1. Carga una imagen.
2. Carga o graba un audio.
3. Selecciona un tipo de reporte.
4. Presiona **Analizar contenido**.
5. Comprueba que aparezca el mensaje **Etapa 1 operativa**.
6. Abre todas las pestañas y verifica que no se produzcan errores.
7. Presiona **Limpiar** y confirma que la interfaz vuelva a su estado inicial.

## Próximas etapas

1. Integración de YOLO11n.
2. Integración de BLIP.
3. Integración de Whisper.
4. Integración de AST.
5. Fusión multimodal.
6. Síntesis de voz con MMS-TTS.
