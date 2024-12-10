import requests

import sys

import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import pygame
import numpy as np
import threading
import os
import time
import random
import requests
from datetime import datetime



# Configuración del servidor
SERVER_URL = "http://192.168.114.179/CasaInteligente/php/insercion.php"
# Configuración del asistente (voz)
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad de la voz
engine.setProperty('voice', 'spanish')  # Ajusta la voz al español

# Interfaz visual
class AsistenteVisual:
    def _init_(self):
        self.root = tk.Tk()
        self.root.title("Asistente Digital")
        self.root.geometry("900x700")
        self.root.configure(bg="#1E1E1E")  # Fondo negro moderno

        # Fondo animado (partículas)
        self.canvas = tk.Canvas(self.root, width=900, height=700, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.particles = self.crear_particulas(50)
        self.animar_particulas()

        # Título
        self.label_title = tk.Label(
            self.root,
            text="Asistente Digital",
            font=("Segoe UI", 36, "bold"),
            bg="#1E1E1E",
            fg="#00BFFF"
        )
        self.label_title.place(relx=0.5, rely=0.1, anchor="center")

        # Indicador de estado
        self.label_status = tk.Label(
            self.root,
            text="Esperando comandos...",
            font=("Segoe UI", 20),
            bg="#1E1E1E",
            fg="#FFD700"
        )
        self.label_status.place(relx=0.5, rely=0.2, anchor="center")

        # Espectro de audio
        self.spectrum_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.spectrum_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.bars = [tk.Frame(self.spectrum_frame, bg="#00BFFF", width=15, height=100) for _ in range(30)]
        for bar in self.bars:
            bar.pack(side="left", padx=3)

        # Reloj
        self.label_clock = tk.Label(
            self.root,
            text="00:00:00",
            font=("Segoe UI", 24, "bold"),
            bg="#1E1E1E",
            fg="#00FF7F"
        )
        self.label_clock.place(relx=0.5, rely=0.85, anchor="center")
        self.actualizar_reloj()

    def crear_particulas(self, cantidad):
        """Crea partículas animadas en el fondo."""
        particles = []
        for _ in range(cantidad):
            x = random.randint(0, 900)
            y = random.randint(0, 700)
            size = random.randint(2, 6)
            speed = random.uniform(0.5, 2)
            particle = self.canvas.create_oval(x, y, x + size, y + size, fill="#00BFFF", outline="")
            particles.append({"id": particle, "x": x, "y": y, "size": size, "speed": speed})
        return particles

    def animar_particulas(self):
        """Anima las partículas del fondo."""
        for particle in self.particles:
            self.canvas.move(particle["id"], 0, particle["speed"])
            coords = self.canvas.coords(particle["id"])
            if coords[1] > 700:  # Si sale de la pantalla, vuelve a aparecer arriba
                self.canvas.coords(particle["id"], coords[0], -particle["size"], coords[2], 0)
        self.root.after(30, self.animar_particulas)

    def actualizar_reloj(self):
        """Actualiza el reloj en tiempo real."""
        hora_actual = datetime.now().strftime("%H:%M:%S")
        self.label_clock.config(text=hora_actual)
        self.root.after(1000, self.actualizar_reloj)

    def actualizar_espectro(self, activar):
        if activar:
            for bar in self.bars:
                bar.config(height=np.random.randint(50, 200), bg=random.choice(["#00BFFF", "#FFD700", "#FF4500"]))
        else:
            for bar in self.bars:
                bar.config(height=100, bg="#00BFFF")

    def actualizar_estado(self, texto):
        self.label_status.config(text=texto)

    def animar_estado(self, color):
        self.label_status.config(fg=color)
        self.root.after(200, lambda: self.label_status.config(fg="#FFD700"))

    def iniciar(self):
        self.root.mainloop()

# Instancia de la interfaz visual
ui = AsistenteVisual()

# Funciones del asistente
def escuchar():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        ui.actualizar_estado("Escuchando...")
        ui.animar_estado("#00BFFF")
        try:
            audio = recognizer.listen(source)
            comando = recognizer.recognize_google(audio, language="es-ES")
            ui.actualizar_estado(f"Comando reconocido: {comando}")
            return comando.lower()
        except sr.UnknownValueError:
            ui.actualizar_estado("No entendí el comando.")
            return None
        except Exception as e:
            ui.actualizar_estado(f"Error: {e}")
            return None

def buscar_en_internet(pregunta):
    """Busca la respuesta en Wikipedia."""
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{pregunta.replace(' ', '_')}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "No encontré información relevante.")
        else:
            return "No encontré resultados en Wikipedia."
    except Exception as e:
        return f"Error al buscar en internet: {e}"
    
def respuestas_personalidad(comando):
    """Respuestas personalizadas con personalidad."""
    personalidades = {
        "cómo estás": "Estoy genial, ¡gracias por preguntar!",
        "quién eres": "Soy tu asistente digital, siempre listo para ayudarte.",
        "cuéntame un chiste": "¿Por qué el libro de matemáticas estaba triste? ¡Porque tenía demasiados problemas!",
        "te gusta algo": "Me encanta ayudarte, ¡es mi misión principal!",
        "dónde estás": "Estoy aquí, en tu dispositivo, listo para responder.",
        "qué puedes hacer": "Puedo responder preguntas, encender luces y mucho más.",
        "tienes sueños": "Sueño con un mundo donde todos tengan un asistente digital.",
        "adiós": "¡Hasta luego! No olvides volver si me necesitas."
    }
    for clave, respuesta in personalidades.items():
        if clave in comando:
            return respuesta
    return "No estoy seguro de cómo responder a eso, pero puedo aprender."

def hablar(texto):
    ui.actualizar_estado("Hablando...")
    ui.animar_estado("#00FF7F")
    ui.actualizar_espectro(True)  # Activa el espectro
    tts = gTTS(text=texto, lang="es")
    tts.save("respuesta.mp3")
    #os.system("start respuesta.mp3")
    
    # Reproducir el audio directamente con pygame
    pygame.mixer.init()
    pygame.mixer.music.load("respuesta.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():  # Espera a que termine la reproducción
        time.sleep(0.1)
        
    pygame.mixer.quit()
    
    time.sleep(0.5)  # Pausa para evitar
    
    
    ui.actualizar_espectro(False)  # Detiene el espectro
    ui.actualizar_estado("Esperando comandos...")
    
    os.remove("respuesta.mp3")
    
#     try:
#        os.remove("respuesta.mp3")  # Elimina el archivo
#    except PermissionError as e:
#        print(f"No se pudo eliminar el archivo: {e}")
    

    
def procesar_comando(comando):
    if "enciende la luz" in comando:
        try:
            response = requests.post(SERVER_URL, data={'enc': 'encender_luz'})
            if response.status_code == 200:
                hablar("Luz encendida.")
            else:
                hablar("Hubo un problema al encender la luz.")
        except requests.RequestException as e:
            hablar(f"No se pudo conectar al servidor. Error: {e}")
        
    elif "apaga la luz" in comando:
        try:
            response = requests.post(SERVER_URL, data={'enc': 'apagar_luz'})
            if response.status_code == 200:
                hablar("Luz apagada.")
            else:
                hablar("Hubo un problema al apagar la luz.")
        except requests.RequestException as e:
            hablar(f"No se pudo conectar al servidor. Error: {e}")
            
    elif "temperatura" in comando:
    
    try:
            response = requests.get(SERVER_URL, params={'temp': 'temperatura'})
            if response.status_code == 200:
                temperatura = response.json().get("temperatura", "No disponible")
                hablar(f"La temperatura actual es {temperatura} grados.")
            else:
                hablar("Hubo un problema al obtener la temperatura.")
        except requests.RequestException as e:
            hablar(f"No se pudo conectar al servidor. Error: {e}")
        
    elif "qué es" in comando or "quién es" in comando:
        pregunta = comando.replace("qué es", "").replace("quién es", "").strip()
        respuesta = buscar_en_internet(pregunta)
        hablar(respuesta)
    else:
        respuesta = respuestas_personalidad(comando)
        hablar(respuesta)
    

# Loop principal del asistente
def asistente_loop():
    while True:
        comando = escuchar()
        if comando:
            procesar_comando(comando)

# Ejecutar la interfaz en el hilo principal
asistente_thread = threading.Thread(target=asistente_loop)
asistente_thread.daemon = True
asistente_thread.start()

ui.iniciar()