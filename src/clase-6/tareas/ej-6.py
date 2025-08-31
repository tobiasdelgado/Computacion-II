#!/usr/bin/env python3

# Ejercicio 6 — Chat asincrónico con doble FIFO
# Objetivo: Crear una estructura de comunicación bidireccional entre dos usuarios.
#
# Instrucciones:
# 1. Crear dos FIFOs: `/tmp/chat_a` y `/tmp/chat_b`.
# 2. Usuario A escribe en `chat_a` y lee de `chat_b`, y viceversa.
# 3. Implementar dos scripts simétricos, uno para cada usuario.
#
# Extras:
# - Permitir comandos como `/exit` para salir.
# - Mostrar los mensajes con nombre de emisor y timestamp.

import os
import sys
import time
import signal
import select
import threading
from datetime import datetime

# Configuración de FIFOs
FIFO_A = '/tmp/chat_a'  # Usuario A escribe, Usuario B lee
FIFO_B = '/tmp/chat_b'  # Usuario B escribe, Usuario A lee

def limpiar_fifos():
    """Función para limpiar los FIFOs al salir"""
    for fifo in [FIFO_A, FIFO_B]:
        try:
            if os.path.exists(fifo):
                os.remove(fifo)
                print(f"FIFO {fifo} eliminado")
        except OSError as e:
            print(f"Error al eliminar {fifo}: {e}")

def signal_handler(signum, frame):
    """Manejador para señales (Ctrl+C)"""
    print("\nChat interrumpido por el usuario")
    limpiar_fifos()
    sys.exit(0)

def crear_fifos():
    """Crear ambos FIFOs si no existen"""
    for fifo in [FIFO_A, FIFO_B]:
        if not os.path.exists(fifo):
            os.mkfifo(fifo)
            print(f"FIFO creado: {fifo}")

def usuario_a():
    """
    Usuario A del chat bidireccional.
    
    Comunicación bidireccional con FIFOs:
    - Usa dos FIFOs separados (uno para cada dirección)
    - Usuario A: escribe en FIFO_A, lee de FIFO_B
    - Usuario B: escribe en FIFO_B, lee de FIFO_A
    - Esto evita deadlocks y confusión de datos
    """
    print("=== USUARIO A - Chat Bidireccional ===")
    print(f"Escribes en: {FIFO_A}")
    print(f"Lees de: {FIFO_B}")
    print("Comandos: /exit (salir), /help (ayuda)")
    print("-" * 50)
    
    crear_fifos()
    
    try:
        # Abrir FIFOs
        print("Conectando al chat...")
        fd_escribir = os.open(FIFO_A, os.O_WRONLY)  # Escribir en chat_a
        print("✅ Canal de escritura conectado")
        
        # Intentar abrir canal de lectura (puede bloquear si Usuario B no está)
        try:
            fd_leer = os.open(FIFO_B, os.O_RDONLY | os.O_NONBLOCK)
            print("✅ Canal de lectura conectado")
        except OSError:
            print("⏳ Esperando al Usuario B...")
            fd_leer = os.open(FIFO_B, os.O_RDONLY)  # Bloquear hasta que B conecte
            print("✅ Usuario B conectado!")
        
        print("🎯 Chat iniciado! Puedes escribir mensajes:")
        
        # Hilo para leer mensajes entrantes
        def leer_mensajes():
            while True:
                try:
                    # Leer línea completa
                    buffer = b""
                    while True:
                        try:
                            char = os.read(fd_leer, 1)
                            if not char:
                                print("\n💔 Usuario B desconectado")
                                return
                            buffer += char
                            if char == b'\n':
                                break
                        except OSError as e:
                            if e.errno != 11:  # EAGAIN
                                print(f"\n❌ Error leyendo: {e}")
                                return
                            time.sleep(0.1)
                    
                    mensaje = buffer.decode('utf-8', errors='replace').strip()
                    
                    if mensaje.startswith('/exit'):
                        print("\n👋 Usuario B ha salido del chat")
                        return
                    elif mensaje:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"\n[{timestamp}] Usuario B: {mensaje}")
                        print("Usuario A> ", end="", flush=True)
                        
                except OSError:
                    break
        
        # Iniciar hilo lector
        hilo_lector = threading.Thread(target=leer_mensajes, daemon=True)
        hilo_lector.start()
        
        # Bucle principal de escritura
        while True:
            try:
                mensaje = input("Usuario A> ").strip()
                
                if not mensaje:
                    continue
                
                if mensaje.startswith('/exit'):
                    # Notificar salida al otro usuario
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    salida = f"/exit Usuario A salió del chat [{timestamp}]\n"
                    os.write(fd_escribir, salida.encode())
                    print("👋 Saliendo del chat...")
                    break
                elif mensaje.startswith('/help'):
                    print("📖 Comandos disponibles:")
                    print("  /exit  - Salir del chat")
                    print("  /help  - Mostrar esta ayuda")
                    continue
                else:
                    # Enviar mensaje normal
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    mensaje_completo = f"[{timestamp}] {mensaje}\n"
                    os.write(fd_escribir, mensaje_completo.encode())
                    
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Saliendo del chat...")
                break
        
        # Cerrar conexiones
        os.close(fd_escribir)
        os.close(fd_leer)
        
    except OSError as e:
        print(f"❌ Error en Usuario A: {e}")

def usuario_b():
    """
    Usuario B del chat bidireccional.
    Simétrico al Usuario A pero con FIFOs intercambiados.
    """
    print("=== USUARIO B - Chat Bidireccional ===")
    print(f"Escribes en: {FIFO_B}")
    print(f"Lees de: {FIFO_A}")
    print("Comandos: /exit (salir), /help (ayuda)")
    print("-" * 50)
    
    crear_fifos()
    
    try:
        # Abrir FIFOs (orden intercambiado respecto a A)
        print("Conectando al chat...")
        fd_escribir = os.open(FIFO_B, os.O_WRONLY)  # Escribir en chat_b
        print("✅ Canal de escritura conectado")
        
        try:
            fd_leer = os.open(FIFO_A, os.O_RDONLY | os.O_NONBLOCK)
            print("✅ Canal de lectura conectado")
        except OSError:
            print("⏳ Esperando al Usuario A...")
            fd_leer = os.open(FIFO_A, os.O_RDONLY)
            print("✅ Usuario A conectado!")
        
        print("🎯 Chat iniciado! Puedes escribir mensajes:")
        
        # Hilo para leer mensajes entrantes
        def leer_mensajes():
            while True:
                try:
                    buffer = b""
                    while True:
                        try:
                            char = os.read(fd_leer, 1)
                            if not char:
                                print("\n💔 Usuario A desconectado")
                                return
                            buffer += char
                            if char == b'\n':
                                break
                        except OSError as e:
                            if e.errno != 11:  # EAGAIN
                                print(f"\n❌ Error leyendo: {e}")
                                return
                            time.sleep(0.1)
                    
                    mensaje = buffer.decode('utf-8', errors='replace').strip()
                    
                    if mensaje.startswith('/exit'):
                        print("\n👋 Usuario A ha salido del chat")
                        return
                    elif mensaje.startswith('[') and ']' in mensaje:
                        # Mensaje con timestamp
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        contenido = mensaje.split('] ', 1)[1] if '] ' in mensaje else mensaje
                        print(f"\n[{timestamp}] Usuario A: {contenido}")
                        print("Usuario B> ", end="", flush=True)
                        
                except OSError:
                    break
        
        # Iniciar hilo lector
        hilo_lector = threading.Thread(target=leer_mensajes, daemon=True)
        hilo_lector.start()
        
        # Bucle principal de escritura
        while True:
            try:
                mensaje = input("Usuario B> ").strip()
                
                if not mensaje:
                    continue
                
                if mensaje.startswith('/exit'):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    salida = f"/exit Usuario B salió del chat [{timestamp}]\n"
                    os.write(fd_escribir, salida.encode())
                    print("👋 Saliendo del chat...")
                    break
                elif mensaje.startswith('/help'):
                    print("📖 Comandos disponibles:")
                    print("  /exit  - Salir del chat")
                    print("  /help  - Mostrar esta ayuda")
                    continue
                else:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    mensaje_completo = f"[{timestamp}] {mensaje}\n"
                    os.write(fd_escribir, mensaje_completo.encode())
                    
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Saliendo del chat...")
                break
        
        os.close(fd_escribir)
        os.close(fd_leer)
        
    except OSError as e:
        print(f"❌ Error en Usuario B: {e}")

def demo_automatica():
    """
    Demo que simula una conversación automática entre dos usuarios
    """
    print("=== DEMO AUTOMÁTICA - Chat Bidireccional ===")
    print("Simulando conversación entre Usuario A y Usuario B")
    print("-" * 50)
    
    # Limpiar FIFOs previos
    limpiar_fifos()
    crear_fifos()
    
    # Crear dos procesos para simular usuarios
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (Usuario A simulado)
        print("Proceso padre: simulando Usuario A")
        time.sleep(0.5)
        
        try:
            # Abrir canales como Usuario A
            fd_escribir = os.open(FIFO_A, os.O_WRONLY)
            fd_leer = os.open(FIFO_B, os.O_RDONLY)
            
            # Conversación predefinida de A
            mensajes_a = [
                "¡Hola! ¿Cómo estás?",
                "Estoy probando este chat con FIFOs",
                "¿Qué opinas de la comunicación bidireccional?",
                "Los FIFOs son muy útiles para IPC",
                "Bueno, me tengo que ir. ¡Hasta luego!"
            ]
            
            for i, msg in enumerate(mensajes_a):
                # Enviar mensaje
                timestamp = datetime.now().strftime("%H:%M:%S")
                mensaje_completo = f"[{timestamp}] {msg}\n"
                os.write(fd_escribir, mensaje_completo.encode())
                print(f"👤 A envió: {msg}")
                
                # Esperar respuesta (excepto en el último mensaje)
                if i < len(mensajes_a) - 1:
                    try:
                        # Leer respuesta de B
                        buffer = b""
                        while True:
                            char = os.read(fd_leer, 1)
                            if not char:
                                break
                            buffer += char
                            if char == b'\n':
                                break
                        
                        if buffer:
                            respuesta = buffer.decode('utf-8', errors='replace').strip()
                            if respuesta.startswith('[') and '] ' in respuesta:
                                contenido = respuesta.split('] ', 1)[1]
                                print(f"👥 B respondió: {contenido}")
                            
                    except OSError as e:
                        print(f"Error leyendo respuesta: {e}")
                
                time.sleep(2)  # Pausa entre mensajes
            
            # Enviar salida
            salida = f"/exit Usuario A salió del chat [{datetime.now().strftime('%H:%M:%S')}]\n"
            os.write(fd_escribir, salida.encode())
            
            os.close(fd_escribir)
            os.close(fd_leer)
            
        except OSError as e:
            print(f"Error en Usuario A: {e}")
        
        # Esperar al proceso hijo
        os.waitpid(pid, 0)
        print("Demo completada")
        
    elif pid == 0:  # Proceso hijo (Usuario B simulado)
        print("Proceso hijo: simulando Usuario B")
        time.sleep(1)  # Dar tiempo a A para configurarse
        
        try:
            # Abrir canales como Usuario B
            fd_escribir = os.open(FIFO_B, os.O_WRONLY)
            fd_leer = os.open(FIFO_A, os.O_RDONLY)
            
            # Respuestas predefinidas de B
            respuestas_b = [
                "¡Hola! Muy bien, ¿y tú?",
                "¡Qué interesante! Me gusta esta implementación",
                "Es genial, permite comunicación asíncrona",
                "Totalmente de acuerdo, son muy versátiles",
                "¡Hasta luego! Fue un placer chatear"
            ]
            
            respuesta_idx = 0
            
            while respuesta_idx < len(respuestas_b):
                try:
                    # Leer mensaje de A
                    buffer = b""
                    while True:
                        char = os.read(fd_leer, 1)
                        if not char:
                            break
                        buffer += char
                        if char == b'\n':
                            break
                    
                    if buffer:
                        mensaje = buffer.decode('utf-8', errors='replace').strip()
                        
                        if mensaje.startswith('/exit'):
                            print("👋 Usuario A se fue")
                            break
                        elif mensaje.startswith('[') and '] ' in mensaje:
                            contenido = mensaje.split('] ', 1)[1]
                            print(f"👤 A dice: {contenido}")
                            
                            # Enviar respuesta
                            if respuesta_idx < len(respuestas_b):
                                time.sleep(1)  # Simular tiempo de escritura
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                respuesta = f"[{timestamp}] {respuestas_b[respuesta_idx]}\n"
                                os.write(fd_escribir, respuesta.encode())
                                print(f"👥 B respondió: {respuestas_b[respuesta_idx]}")
                                respuesta_idx += 1
                        
                except OSError as e:
                    print(f"Error en B: {e}")
                    break
            
            os.close(fd_escribir)
            os.close(fd_leer)
            
        except OSError as e:
            print(f"Error en Usuario B: {e}")
        
        sys.exit(0)
    
    limpiar_fifos()

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 6: Chat asincrónico con doble FIFO")
    print("Comunicación bidireccional usando dos FIFOs separados")
    print("Elige tu rol:")
    print("1. Usuario A (escribe en chat_a, lee de chat_b)")
    print("2. Usuario B (escribe en chat_b, lee de chat_a)")
    print("3. Demo automática (simula conversación entre A y B)")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            usuario_a()
        elif opcion == '2':
            usuario_b()
        elif opcion == '3':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_fifos()

if __name__ == "__main__":
    main()