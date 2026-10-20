# ARMAND_IA

Kiosco de bienvenida con inteligencia artificial para el Instituto Tecnológico Superior de Acayucan (ITSA). Interactúa con las personas por voz y muestra un avatar animado en pantalla.

> Proyecto de tesis en desarrollo.

## ¿Qué hace?

- Escucha y reconoce voz en español (Vosk).
- Responde con voz sintetizada (pyttsx3).
- Muestra un avatar animado en el navegador.
- Usa la cámara para Detectar personas, saludarlas y ayudarles con temas del instituto.
- Genera respuestas con IA Ollama.

## Estructura

| Archivo | Función |
|---|---|
| `servidor.py` | Servidor principal: voz, respuestas y comunicación con el avatar |
| `avatar.html` | Interfaz del avatar |
| `mascota.png` | Imagen de la mascota |
| `prueba_*.py` | Scripts de prueba de cámara, IA y voz |

## Requisitos

- Python 3.x
- Windows (la voz usa los motores de Microsoft Speech)
- Dependencias: `[pip install ...]`

## Modelo de voz (Vosk)

El modelo no está incluido en el repositorio por su tamaño. Para usarlo:

1. Descarga `vosk-model-small-es-0.42` desde https://alphacephei.com/vosk/models
2. Descomprímelo en la carpeta del proyecto.

## Cómo ejecutarlo

```
python servidor.py
```

Luego abre `avatar.html` en el navegador.

## Estado

En desarrollo.

## Autor

Ricardo Javier Rodríguez Hernández, estudiante del ITSA.