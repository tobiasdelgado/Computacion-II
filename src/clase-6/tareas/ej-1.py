#!/usr/bin/env python3

# Ejercicio 1 — Lectura diferida
# Objetivo: Comprender el bloqueo de lectura en un FIFO.
#
# Instrucciones:
# 1. Crear un FIFO llamado `/tmp/test_fifo`.
# 2. Ejecutar un script Python que intente leer desde el FIFO antes de que exista un escritor.
# 3. En otro terminal, ejecutar un script que escriba un mensaje en el FIFO.
#
# Preguntas:
# - ¿Qué se observa en el lector mientras espera?
# - ¿Qué ocurre si se escriben múltiples líneas desde el escritor?

import os
import sys
import signal
import time

# Nombre del FIFO
FIFO_PATH = '/tmp/test_fifo'

def limpiar_fifo():
    """Función para limpiar el FIFO al salir"""
    try:
        if os.path.exists(FIFO_PATH):
            os.remove(FIFO_PATH)
            print(f"FIFO {FIFO_PATH} eliminado")
    except OSError as e:
        print(f"Error al eliminar FIFO: {e}")

def signal_handler(signum, frame):
    """Manejador para señales (Ctrl+C)"""
    print("\nInterrumpido por el usuario")
    limpiar_fifo()
    sys.exit(0)

def lector():
    """
    Proceso lector que intenta leer del FIFO antes de que haya escritor.
    
    Los FIFOs (named pipes) se comportan diferente a los pipes anónimos:
    - Son archivos especiales en el sistema de archivos
    - Pueden ser accedidos por procesos no relacionados
    - Bloquean hasta que hay un escritor/lector en el otro extremo
    """
    print("=== LECTOR DE FIFO - Ejercicio 1 ===")
    print(f"Intentando leer del FIFO: {FIFO_PATH}")
    print("NOTA: Este proceso se bloqueará hasta que haya un escritor")
    print("Ejecuta el escritor en otro terminal para desbloquear")
    print("-" * 50)
    
    try:
        # Crear el FIFO si no existe
        # os.mkfifo crea un archivo especial tipo FIFO en el sistema de archivos
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
            print(f"FIFO creado: {FIFO_PATH}")
        else:
            print(f"FIFO ya existe: {FIFO_PATH}")
        
        print("Abriendo FIFO para lectura...")
        print("⏳ BLOQUEADO esperando escritor...")
        
        # Abrir el FIFO en modo solo lectura
        # Esta operación BLOQUEA hasta que haya un proceso que abra el FIFO para escritura
        fd = os.open(FIFO_PATH, os.O_RDONLY)
        
        print("✅ ¡Escritor conectado! Comenzando a leer...")
        
        mensaje_count = 0
        while True:
            # Leer datos del FIFO
            data = os.read(fd, 1024)
            
            if not data:
                # Si no hay datos, significa que el escritor cerró su extremo
                print("📭 El escritor ha cerrado la conexión (EOF recibido)")
                break
            
            mensaje_count += 1
            mensaje = data.decode().strip()
            timestamp = time.strftime("%H:%M:%S")
            
            print(f"📨 Mensaje #{mensaje_count} [{timestamp}]: '{mensaje}'")
        
        os.close(fd)
        print(f"Lectura completada. Total de mensajes recibidos: {mensaje_count}")
        
    except KeyboardInterrupt:
        print("\nLectura interrumpida por el usuario")
    except OSError as e:
        print(f"Error: {e}")
    finally:
        limpiar_fifo()

def escritor():
    """
    Proceso escritor que envía mensajes al FIFO.
    Debe ejecutarse en un terminal separado después de iniciar el lector.
    """
    print("=== ESCRITOR DE FIFO - Ejercicio 1 ===")
    print(f"Escribiendo al FIFO: {FIFO_PATH}")
    print("Escribe mensajes (o 'exit' para salir)")
    print("-" * 50)
    
    try:
        # Verificar que el FIFO existe
        if not os.path.exists(FIFO_PATH):
            print(f"Error: El FIFO {FIFO_PATH} no existe")
            print("Primero ejecuta el lector para crear el FIFO")
            return
        
        print("Abriendo FIFO para escritura...")
        
        # Abrir el FIFO en modo solo escritura
        # Esta operación también puede bloquear si no hay lector
        fd = os.open(FIFO_PATH, os.O_WRONLY)
        
        print("✅ Conectado al lector!")
        print("Ahora puedes escribir mensajes:")
        
        while True:
            try:
                mensaje = input("> ")
                
                if mensaje.lower() == 'exit':
                    print("Cerrando escritor...")
                    break
                
                if mensaje.strip():  # Solo enviar si no está vacío
                    # Escribir mensaje al FIFO
                    os.write(fd, (mensaje + '\n').encode())
                    print(f"✅ Mensaje enviado: '{mensaje}'")
                
            except EOFError:
                # Ctrl+D presionado
                break
        
        os.close(fd)
        print("Escritor terminado")
        
    except KeyboardInterrupt:
        print("\nEscritor interrumpido")
    except OSError as e:
        print(f"Error: {e}")

def modo_demo():
    """
    Modo demostración que usa fork() para crear lector y escritor automáticamente
    """
    print("=== MODO DEMO - Ejercicio 1 ===")
    print("Demostrando el bloqueo de lectura en FIFOs")
    print("-" * 50)
    
    # Crear el FIFO
    if os.path.exists(FIFO_PATH):
        os.remove(FIFO_PATH)
    
    os.mkfifo(FIFO_PATH)
    print(f"FIFO creado: {FIFO_PATH}")
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (lector)
        print("Proceso padre: actuando como LECTOR")
        time.sleep(1)  # Pequeña pausa para mostrar el bloqueo
        
        try:
            print("⏳ Intentando abrir FIFO para lectura...")
            fd = os.open(FIFO_PATH, os.O_RDONLY)
            print("✅ FIFO abierto para lectura")
            
            # Leer mensajes del proceso hijo
            for i in range(3):
                data = os.read(fd, 1024)
                if data:
                    print(f"📨 Recibido: '{data.decode().strip()}'")
            
            os.close(fd)
            
        except OSError as e:
            print(f"Error en lector: {e}")
        
        # Esperar al proceso hijo
        os.waitpid(pid, 0)
        limpiar_fifo()
        
    elif pid == 0:  # Proceso hijo (escritor)
        print("Proceso hijo: actuando como ESCRITOR")
        time.sleep(2)  # Dar tiempo al padre para bloquearse
        
        try:
            print("📝 Abriendo FIFO para escritura...")
            fd = os.open(FIFO_PATH, os.O_WRONLY)
            print("✅ FIFO abierto para escritura")
            
            # Enviar algunos mensajes
            mensajes = ["Primer mensaje", "Segundo mensaje", "Tercer mensaje"]
            for i, msg in enumerate(mensajes, 1):
                print(f"📤 Enviando mensaje {i}: '{msg}'")
                os.write(fd, (msg + '\n').encode())
                time.sleep(1)
            
            os.close(fd)
            print("Escritor terminado")
            
        except OSError as e:
            print(f"Error en escritor: {e}")
        
        sys.exit(0)

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 1: Lectura diferida en FIFOs")
    print("Elige el modo de ejecución:")
    print("1. Lector (se bloqueará hasta que haya un escritor)")
    print("2. Escritor (para usar con el lector en otro terminal)")
    print("3. Demo automática (fork para crear ambos procesos)")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            lector()
        elif opcion == '2':
            escritor()
        elif opcion == '3':
            modo_demo()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_fifo()

if __name__ == "__main__":
    main()