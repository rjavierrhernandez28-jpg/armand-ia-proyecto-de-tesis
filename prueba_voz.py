import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.say("Hola, bienvenido a la escuela. ¿En qué puedo ayudarte?")
engine.runAndWait()