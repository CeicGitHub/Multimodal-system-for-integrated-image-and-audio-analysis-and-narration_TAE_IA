# MediaScope — Entrega final, revisión 2

Aplicación multimodal en Gradio que analiza una imagen y un audio, fusiona los
hallazgos, genera un reporte escrito, produce una narración en español y permite
descargar la trazabilidad técnica de la ejecución.

## Funcionalidades

- Imagen desde archivo, cámara o portapapeles.
- Audio desde archivo o micrófono.
- Detección de objetos con YOLO11n.
- Descripción contextual con BLIP.
- Transcripción del habla con Whisper.
- Clasificación ambiental con AST en intervalos de hasta 10 segundos.
- Consolidación de etiquetas acústicas equivalentes en el resumen.
- Aviso de confiabilidad cuando la música domina la transcripción.
- Reportes Breve, Detallado y Accesible.
- Funcionamiento condicional con una o ambas modalidades.
- Narración en español con MMS-TTS.
- Reporte Markdown descargable con modelos, dispositivos y tiempos.
- Pestaña interna con arquitectura y cumplimiento de requisitos.
- Metadatos técnicos visibles para demostrar trazabilidad.

## Pipeline

1. Gradio recibe y valida las entradas.
2. YOLO11n y BLIP procesan la imagen.
3. Whisper y AST procesan el audio.
4. El módulo de fusión combina los resultados disponibles.
5. MMS-TTS genera la narración.
6. La interfaz presenta y exporta los resultados.

Consulta [ARQUITECTURA.md](ARQUITECTURA.md) para la descripción lista para el
reporte técnico y [DEMO_DAY.md](DEMO_DAY.md) para el guion de exposición.

## Condiciones cubiertas

| Condición | Evidencia en MediaScope |
| --- | --- |
| Dos modelos de visión diferentes | YOLO11n detecta; BLIP describe. |
| Audio procesado mediante IA | Whisper transcribe, AST clasifica y MMS-TTS narra. |
| Aplicación Gradio en vivo | Entradas, controles y resultados interactivos. |

## Modelos

- `yolo11n.pt`
- `Salesforce/blip-image-captioning-base`
- `openai/whisper-base`
- `MIT/ast-finetuned-audioset-10-10-0.4593`
- `facebook/mms-tts-spa`

## Ejecución en Windows

Descomprime el proyecto en `C:\project_final_m6_ia` y ejecuta cada instrucción
por separado en PowerShell:

```powershell
cd C:\project_final_m6_ia\MediaScope_Etapa7
& "..\MediaScope_Etapa1\.venv\Scripts\Activate.ps1"
Copy-Item "..\MediaScope_Etapa6\yolo11n.pt" ".\yolo11n.pt"
python -m pip install -r requirements.txt
python app.py
```

Si el archivo `yolo11n.pt` ya está presente, puede omitirse `Copy-Item`.

Abrir:

```text
http://127.0.0.1:7860
```

## Enlace público temporal

```powershell
$env:GRADIO_SHARE="true"
python app.py
```

Al terminar:

```powershell
Remove-Item Env:GRADIO_SHARE -ErrorAction SilentlyContinue
```

## Validación final

1. Ejecutar imagen y audio juntos con el reporte Detallado.
2. Confirmar el estado **MediaScope final listo**.
3. Revisar las pestañas visual, auditiva y multimodal.
4. Reproducir la narración.
5. Descargar y abrir el reporte `.md`.
6. Verificar que los metadatos indiquen etapa 7, `release: final-r2` y
   `pending_models: []`.
7. Probar solo imagen, solo audio y el botón Limpiar.
8. Si se usará `share=True`, probar el enlace desde otro dispositivo.

## Licencia y uso responsable

Las salidas son predicciones automáticas y requieren verificación. El checkpoint
`facebook/mms-tts-spa` utiliza licencia CC BY-NC 4.0 y se incorpora para una
demostración académica no comercial.
