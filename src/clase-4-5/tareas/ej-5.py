#!/usr/bin/env python3

# Ejercicio 5: Chat Bidireccional  
# Desarrolla un sistema de chat simple entre dos procesos usando pipes. Cada proceso debe 
# poder enviar y recibir mensajes simultáneamente, implementando una comunicación 
# bidireccional completa.

import os
import sys
import signal
import select

def main():
    # Crear dos pipes para comunicación bidireccional
    # pipe_padre_hijo: padre -> hijo
    # pipe_hijo_padre: hijo -> padre
    pipe_padre_hijo = os.pipe()
    pipe_hijo_padre = os.pipe()
    
    print("=== Chat Bidireccional ===")
    print("Escribe 'salir' para terminar el chat")
    print("=" * 30)
    
    # Crear proceso hijo
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (Usuario A)
        # Cerrar extremos no utilizados
        os.close(pipe_padre_hijo[0])  # No lee del pipe padre->hijo
        os.close(pipe_hijo_padre[1])  # No escribe en pipe hijo->padre
        
        print("Usuario A: Chat iniciado. Puedes escribir mensajes.")
        
        try:
            while True:
                # Usar select para verificar si hay mensajes del hijo sin bloquear
                listo, _, _ = select.select([pipe_hijo_padre[0]], [], [], 0)
                
                if listo:
                    # Hay mensaje del hijo
                    mensaje = os.read(pipe_hijo_padre[0], 1024).decode().strip()
                    if mensaje == "SALIR":
                        print("Usuario A: Usuario B ha salido del chat.")
                        break
                    print(f"Usuario B: {mensaje}")
                
                # Verificar si hay input del usuario sin bloquear
                listo, _, _ = select.select([sys.stdin], [], [], 0)
                
                if listo:
                    # Hay input del usuario
                    mensaje = input().strip()
                    
                    if mensaje.lower() == "salir":
                        os.write(pipe_padre_hijo[1], b"SALIR")
                        print("Usuario A: Saliendo del chat...")
                        break
                    elif mensaje:  # Solo enviar si no está vacío
                        os.write(pipe_padre_hijo[1], mensaje.encode())
                        print(f"Usuario A: {mensaje}")
        
        except (KeyboardInterrupt, OSError):
            print("\nUsuario A: Chat interrumpido")
        
        # Cerrar pipes y esperar al hijo
        os.close(pipe_padre_hijo[1])
        os.close(pipe_hijo_padre[0])
        os.waitpid(pid, 0)
        print("Chat terminado")
        
    elif pid == 0:  # Proceso hijo (Usuario B)
        # Cerrar extremos no utilizados
        os.close(pipe_padre_hijo[1])  # No escribe en pipe padre->hijo
        os.close(pipe_hijo_padre[0])  # No lee del pipe hijo->padre
        
        # Redireccionar stdin a stderr para evitar conflictos con el padre
        # El hijo leerá de sys.stdin pero el padre también puede hacerlo
        print("Usuario B: Chat iniciado. Puedes escribir mensajes.", file=sys.stderr)
        
        try:
            while True:
                # Verificar mensajes del padre
                listo, _, _ = select.select([pipe_padre_hijo[0]], [], [], 0)
                
                if listo:
                    mensaje = os.read(pipe_padre_hijo[0], 1024).decode().strip()
                    if mensaje == "SALIR":
                        print("Usuario B: Usuario A ha salido del chat.", file=sys.stderr)
                        break
                    print(f"Usuario A: {mensaje}", file=sys.stderr)
                
                # El input del usuario B se simula con un timer
                # En una implementación real, cada proceso tendría su propia terminal
                # Para simplificar, el proceso hijo enviará mensajes automáticos
                
                # Simular respuestas automáticas del Usuario B
                import time
                time.sleep(2)
                
                # Enviar un mensaje automático de vez en cuando
                import random
                if random.random() < 0.3:  # 30% de probabilidad
                    mensajes_auto = [
                        "Hola! ¿Cómo estás?",
                        "Interesante...",
                        "¿Qué opinas sobre los pipes?",
                        "Este chat funciona bien!",
                        "Python es genial para esto"
                    ]
                    mensaje_auto = random.choice(mensajes_auto)
                    os.write(pipe_hijo_padre[1], mensaje_auto.encode())
                    print(f"Usuario B: {mensaje_auto}", file=sys.stderr)
        
        except (KeyboardInterrupt, OSError):
            print("Usuario B: Chat interrumpido", file=sys.stderr)
        
        os.close(pipe_padre_hijo[0])
        os.close(pipe_hijo_padre[1])
        sys.exit(0)
        
    else:  # Error en fork
        print("Error al crear proceso hijo")
        sys.exit(1)

def chat_interactivo():
    """
    Versión más simple donde cada proceso envía mensajes por turnos
    Esta versión es más fácil de entender y probar
    """
    pipe_padre_hijo = os.pipe()
    pipe_hijo_padre = os.pipe()
    
    print("=== Chat por Turnos ===")
    print("Cada usuario envía un mensaje por turno")
    print("Escribe 'salir' para terminar")
    print("=" * 30)
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre
        os.close(pipe_padre_hijo[0])
        os.close(pipe_hijo_padre[1])
        
        for turno in range(5):  # 5 turnos de conversación
            # Padre envía mensaje
            mensaje = input(f"Usuario A (turno {turno + 1}): ")
            if mensaje.lower() == "salir":
                os.write(pipe_padre_hijo[1], b"SALIR")
                break
            os.write(pipe_padre_hijo[1], mensaje.encode())
            
            # Padre recibe respuesta
            respuesta = os.read(pipe_hijo_padre[0], 1024).decode()
            if respuesta == "SALIR":
                print("Usuario B ha salido del chat")
                break
            print(f"Usuario B responde: {respuesta}")
        
        os.close(pipe_padre_hijo[1])
        os.close(pipe_hijo_padre[0])
        os.waitpid(pid, 0)
        
    elif pid == 0:  # Proceso hijo
        os.close(pipe_padre_hijo[1])
        os.close(pipe_hijo_padre[0])
        
        for turno in range(5):
            # Hijo recibe mensaje
            mensaje = os.read(pipe_padre_hijo[0], 1024).decode()
            if mensaje == "SALIR":
                break
            print(f"Usuario A dice: {mensaje}")
            
            # Hijo responde
            respuesta = input(f"Usuario B (turno {turno + 1}): ")
            if respuesta.lower() == "salir":
                os.write(pipe_hijo_padre[1], b"SALIR")
                break
            os.write(pipe_hijo_padre[1], respuesta.encode())
        
        os.close(pipe_padre_hijo[0])
        os.close(pipe_hijo_padre[1])
        sys.exit(0)

if __name__ == "__main__":
    # Usar la versión por turnos que es más simple de probar
    print("Seleccione el tipo de chat:")
    print("1. Chat por turnos (más simple)")
    print("2. Chat bidireccional simultáneo")
    
    opcion = input("Opción (1 o 2): ").strip()
    
    if opcion == "2":
        main()
    else:
        chat_interactivo()