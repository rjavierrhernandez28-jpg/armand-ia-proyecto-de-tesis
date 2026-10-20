from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pyttsx3
import vosk
import sounddevice as sd
import json
import threading
import cv2

app = Flask(__name__)
CORS(app)

SISTEMA = """
Eres Armandillo, el asistente virtual de bienvenida del Instituto Tecnológico Superior de Acayucan (ITSA), 
perteneciente al Tecnológico Nacional de México (TecNM).
Respondes de forma amable, clara y breve en español.
Solo respondes preguntas relacionadas con el ITSA.
Si no sabes algo con certeza, dices amablemente que no tienes esa información y sugieres contactar a la escuela.

=== INFORMACIÓN GENERAL ===
- Nombre completo: Instituto Tecnológico Superior de Acayucan (ITSA)
- Pertenece al: Tecnológico Nacional de México (TecNM)
- Dirección: Carretera Costera del Golfo Km. 216.4, Col. Agrícola Michapan, C.P. 96100, Acayucan, Veracruz
- Teléfono: 924 247 4473
- WhatsApp admisiones: 924 143 49 69
- Correo: web_dacayucan@tecnm.mx
- Sitio web: www.itsacayucan.edu.mx
- Redes sociales: Facebook e Instagram como @TecnmAcayucan, TikTok como @tecnm_acayucan
- Horario de atención: Lunes a viernes de 9:00 am a 4:00 pm
- Mascota: El Armadillo (¡ese soy yo!)

=== OFERTA EDUCATIVA (9 ingenierías) ===
1. Ingeniería Bioquímica - industria alimentaria, farmacéutica, biotecnología
2. Ingeniería en Sistemas Computacionales - desarrollo de software, apps, ciberseguridad
3. Ingeniería en Informática - redes, soporte técnico, sistemas empresariales
4. Ingeniería Civil - construcción de edificios, puentes, carreteras
5. Ingeniería en Gestión Empresarial - negocios, emprendimiento, consultoría
6. Ingeniería Química - industria petroquímica, manufactura, control de calidad
7. Ingeniería Electromecánica - mantenimiento industrial, automatización
8. Ingeniería Mecatrónica - robótica, automatización industrial, máquinas inteligentes
9. Ingeniería Industrial - logística, optimización de procesos, gestión de proyectos

=== ADMISIÓN 2026 ===
- Cierre de convocatoria: 12 de junio de 2026
- Examen: 22 de junio de 2026, 12:00-15:00 horas, modalidad en línea
- Costo de ficha: $660 pesos
- Registro en línea o en ventanilla (Control Escolar, Ventanilla 6)
- WhatsApp informes: 924 143 49 69

=== ORIENTACIÓN VOCACIONAL ===
Si alguien no sabe qué carrera elegir, pregúntale:
- ¿Te gustan más las matemáticas y física, o la administración y negocios?
- ¿Prefieres trabajar con computadoras, máquinas, personas o en laboratorio?
- ¿Tienes alguna industria favorita?
Con esas respuestas sugiere la carrera más adecuada y explica brevemente por qué.
"""

modelo_voz = vosk.Model(r"C:\Users\ricar\OneDrive\Documentos\ARMAND_IA\vosk-model-small-es-0.42\vosk-model-small-es-0.42")
detector_caras = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

escuchando = False
cara_detectada = False
en_conversacion = False
lock = threading.Lock()

def hablar(texto):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0')
    engine.setProperty('rate', 150)
    engine.say(texto)
    engine.runAndWait()
    engine.stop()

def preguntar_ia(pregunta):
    respuesta = requests.post("http://localhost:11434/api/chat", json={
        "model": "llama3.2:1b",
        "messages": [
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": pregunta}
        ],
        "stream": False
    })
    return respuesta.json()["message"]["content"]

def escuchar_microfono():
    global escuchando, en_conversacion
    reconocedor = vosk.KaldiRecognizer(modelo_voz, 16000)
    print("Micrófono activo...")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1) as stream:
        while escuchando:
            data, _ = stream.read(8000)
            if reconocedor.AcceptWaveform(bytes(data)):
                resultado = json.loads(reconocedor.Result())
                texto = resultado.get("text", "").strip()
                if texto:
                    print("Escuché:", texto)
                    respuesta = preguntar_ia(texto)
                    print("Armandillo:", respuesta)
                    hablar(respuesta)

def vigilar_camara():
    global cara_detectada, escuchando, en_conversacion
    camara = cv2.VideoCapture(0)
    frames_sin_cara = 0
    frames_con_cara = 0
    UMBRAL_ACTIVAR = 5
    UMBRAL_DESACTIVAR = 300

    print("Cámara activa, esperando personas...")

    while True:
        ret, frame = camara.read()
        if not ret:
            continue

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = detector_caras.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=3, minSize=(80, 80))

        if len(caras) > 0:
            frames_con_cara += 1
            frames_sin_cara = 0

            if frames_con_cara >= UMBRAL_ACTIVAR and not en_conversacion:
                with lock:
                    en_conversacion = True
                    escuchando = True
                print("¡Persona detectada! Activando Armandillo...")
                hilo_saludo = threading.Thread(target=saludar)
                hilo_saludo.start()
                hilo_mic = threading.Thread(target=escuchar_microfono, daemon=True)
                hilo_mic.start()
        else:
            frames_sin_cara += 1
            frames_con_cara = 0

            if frames_sin_cara >= UMBRAL_DESACTIVAR and en_conversacion:
                with lock:
                    en_conversacion = False
                    escuchando = False
                print("Persona se fue. Armandillo en espera.")

    camara.release()

def saludar():
    saludo = preguntar_ia("Saluda brevemente a alguien que acaba de llegar al ITSA y pregúntale en qué puedes ayudarle.")
    print("Saludo:", saludo)
    hablar(saludo)

@app.route("/preguntar", methods=["POST"])
def preguntar():
    datos = request.json
    pregunta = datos.get("pregunta", "")
    texto = preguntar_ia(pregunta)
    hablar(texto)
    return jsonify({"respuesta": texto})

@app.route("/estado", methods=["GET"])
def estado():
    return jsonify({"en_conversacion": en_conversacion, "escuchando": escuchando})

if __name__ == "__main__":
    hilo_camara = threading.Thread(target=vigilar_camara, daemon=True)
    hilo_camara.start()
    app.run(port=5000)