import vosk
import sounddevice as sd
import json

modelo = vosk.Model(r"C:\Users\ricar\OneDrive\Documentos\ARMAND_IA\vosk-model-small-es-0.42\vosk-model-small-es-0.42")
reconocedor = vosk.KaldiRecognizer(modelo, 16000)

print("Habla algo en español... (Ctrl+C para salir)")

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                        channels=1) as stream:
    while True:
        data, _ = stream.read(8000)
        if reconocedor.AcceptWaveform(bytes(data)):
            resultado = json.loads(reconocedor.Result())
            texto = resultado.get("text", "")
            if texto:
                print("Escuché:", texto)