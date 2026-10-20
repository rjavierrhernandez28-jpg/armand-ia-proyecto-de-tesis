import requests
import pyttsx3

# Configurar la voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Contexto de tu escuela (aquí le dices quién es el avatar)
sistema = "Eres un asistente de bienvenida de una escuela. Respondes de forma amable y breve en español. Solo respondes preguntas relacionadas con la escuela."

# Pregunta de prueba
pregunta = "¿Cuál es tu función aquí?"

# Llamar a Ollama
respuesta = requests.post("http://localhost:11434/api/chat", json={
    "model": "llama3.2:1b",
    "messages": [
        {"role": "system", "content": sistema},
        {"role": "user", "content": pregunta}
    ],
    "stream": False
})

# Extraer el texto de la respuesta
texto = respuesta.json()["message"]["content"]
print("IA dice:", texto)

# Decirlo en voz alta
engine.say(texto)
engine.runAndWait()