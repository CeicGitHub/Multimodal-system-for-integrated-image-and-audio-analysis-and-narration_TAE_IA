# Guía de demostración de MediaScope

## Preparación previa

### Un día antes

- Ejecutar la aplicación y confirmar que los cinco modelos estén descargados.
- Probar una imagen clara y un audio de entre 10 y 25 segundos.
- Guardar ambos archivos en una carpeta fácil de localizar.
- Confirmar que el audio de la computadora y el navegador funcionen.
- Conservar la etapa 6 como respaldo.

### Treinta minutos antes

```powershell
cd C:\project_final_m6_ia\MediaScope_Etapa7
& "..\MediaScope_Etapa1\.venv\Scripts\Activate.ps1"
$env:GRADIO_SHARE="true"
python app.py
```

- Abrir la URL local y el enlace público.
- Probar el enlace público desde un teléfono u otra computadora.
- Ejecutar una inferencia de calentamiento para cargar todos los modelos.
- Limpiar la interfaz antes de iniciar la presentación.

## Guion sugerido de cinco minutos

### 0:00–0:40 — Problema y objetivo

“MediaScope es una aplicación multimodal que interpreta conjuntamente una
imagen y una grabación. Integra visión artificial, reconocimiento del habla,
clasificación acústica y síntesis de voz en una interfaz Gradio.”

### 0:40–1:20 — Entradas y configuración

Mostrar la imagen, el audio, el tipo de reporte, el idioma y el umbral de
confianza. Indicar que puede usarse una entrada o ambas.

### 1:20–2:10 — Ejecución

Presionar **Analizar y narrar**. Mientras se procesa, explicar las dos ramas:

- YOLO11n detecta objetos y BLIP describe la escena.
- Whisper transcribe y AST identifica sonidos por intervalos.

### 2:10–3:35 — Resultados

1. Mostrar la imagen anotada y la tabla de objetos.
2. Mostrar el caption de BLIP.
3. Mostrar la transcripción y los eventos acústicos.
4. Abrir el reporte integrado y reproducir la narración.
5. Descargar el reporte Markdown.

### 3:35–4:30 — Requisitos

Abrir **Acerca del pipeline** y señalar:

- dos modelos de visión diferentes;
- audio analizado y generado mediante IA;
- aplicación Gradio ejecutada en vivo;
- funcionamiento condicional si falta una modalidad.

### 4:30–5:00 — Cierre

“El sistema entrega evidencia visual, auditiva, textual y narrada, además de
metadatos para conocer qué modelo produjo cada resultado. Las predicciones se
presentan como estimaciones automáticas sujetas a verificación.”

## Matriz de prueba final

| Caso | Imagen | Audio | Resultado esperado |
| --- | --- | --- | --- |
| Principal | Sí | Sí | Estado “Análisis multimodal completo”, cinco modelos y narración |
| Solo visión | Sí | No | Reporte parcial con YOLO, BLIP y TTS |
| Solo audio | No | Sí | Reporte parcial con Whisper, AST y TTS |
| Sin entradas | No | No | Mensaje solicitando al menos una entrada |
| Limpiar | Cualquiera | Cualquiera | Todos los campos vuelven a su valor inicial |
| Exportación | Sí | Sí | Archivo `.md` descargable con reporte y trazabilidad |

## Contingencias

- **El enlace público no abre:** usar la URL local y explicar que el enlace de
  Gradio es temporal.
- **WinError 10054:** recargar el navegador; normalmente es una desconexión del
  cliente y no un fallo de los modelos.
- **La primera inferencia tarda:** esperar; los modelos se están cargando. Las
  siguientes ejecuciones reutilizan la memoria.
- **No se escucha la narración:** verificar volumen y descargar el WAV desde el
  reproductor.
- **Falta Internet:** utilizar la URL local. Los modelos ya almacenados en caché
  pueden seguir funcionando, pero no se podrá crear un enlace público.
- **Memoria insuficiente:** cerrar otras aplicaciones, reiniciar MediaScope y
  ejecutar una sola solicitud.

## Cierre de la aplicación

Presionar `Ctrl + C` en la terminal y eliminar la variable temporal:

```powershell
Remove-Item Env:GRADIO_SHARE -ErrorAction SilentlyContinue
```
