#!/usr/bin/env python3

# Ejercicio 3 — FIFO + archivos
# Objetivo: Usar un FIFO como entrada para un proceso que guarda datos en un archivo.
#
# Instrucciones:
# 1. Crear un script que escuche un FIFO y guarde todo lo que llega en `output.txt`.
# 2. Otro script debe leer líneas desde el teclado y enviarlas al FIFO.
# 3. Al escribir "exit" se debe cerrar todo correctamente.

import os
import sys
import time
import signal
from datetime import datetime

# Configuración
FIFO_PATH = '/tmp/file_fifo'
OUTPUT_FILE = 'output.txt'

def limpiar_recursos():
    """Función para limpiar recursos al salir"""
    try:
        if os.path.exists(FIFO_PATH):
            os.remove(FIFO_PATH)
            print(f"FIFO {FIFO_PATH} eliminado")
    except OSError as e:
        print(f"Error al eliminar FIFO: {e}")

def signal_handler(signum, frame):
    """Manejador para señales (Ctrl+C)"""
    print("\nInterrumpido por el usuario")
    limpiar_recursos()
    sys.exit(0)

def lector_archivo():
    """
    Proceso que lee del FIFO y guarda todo en un archivo.
    
    Este ejercicio demuestra cómo los FIFOs pueden actuar como puente
    entre diferentes tipos de E/S: entrada interactiva → FIFO → archivo
    """
    print("=== LECTOR DE ARCHIVO - Ejercicio 3 ===")
    print(f"Leyendo del FIFO: {FIFO_PATH}")
    print(f"Guardando en archivo: {OUTPUT_FILE}")
    print("Esperando entrada del cliente...")
    print("-" * 50)
    
    try:
        # Crear FIFO si no existe
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
            print(f"FIFO creado: {FIFO_PATH}")
        
        # Abrir archivo de salida
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as archivo:
            archivo.write(f"=== Log iniciado: {datetime.now()} ===\n")
            print(f"✅ Archivo {OUTPUT_FILE} abierto para escritura")
            
            # Abrir FIFO para lectura (se bloquea hasta que haya escritor)
            fd = os.open(FIFO_PATH, os.O_RDONLY)
            print("✅ Cliente conectado al FIFO")
            
            linea_count = 0
            
            while True:
                # Leer línea del FIFO
                buffer = b""
                while True:
                    try:
                        char = os.read(fd, 1)
                        if not char:
                            # EOF - el escritor cerró
                            break
                        buffer += char
                        if char == b'\n':
                            break
                    except OSError:
                        break
                
                if not buffer:
                    print("📭 Cliente desconectado")
                    break
                
                linea = buffer.decode('utf-8', errors='replace').strip()
                
                # Verificar comando de salida
                if linea.lower() == 'exit':
                    print("🚪 Comando 'exit' recibido")
                    archivo.write(f"[{datetime.now()}] COMANDO EXIT RECIBIDO\n")
                    break
                
                if linea:  # Solo procesar líneas no vacías
                    linea_count += 1
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Escribir al archivo con timestamp
                    entrada_archivo = f"[{timestamp}] {linea}\n"
                    archivo.write(entrada_archivo)
                    archivo.flush()  # Forzar escritura inmediata
                    
                    print(f"📝 Línea #{linea_count} guardada: '{linea}'")
            
            # Cerrar FIFO
            os.close(fd)
            
            # Escribir estadísticas finales
            archivo.write(f"\n=== Log terminado: {datetime.now()} ===\n")
            archivo.write(f"Total de líneas procesadas: {linea_count}\n")
            
        print(f"✅ Archivo {OUTPUT_FILE} cerrado")
        print(f"📊 Total de líneas guardadas: {linea_count}")
        
        # Mostrar contenido del archivo
        print(f"\n--- Contenido de {OUTPUT_FILE} ---")
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
        
    except KeyboardInterrupt:
        print("\nLector interrumpido")
    except OSError as e:
        print(f"Error en lector: {e}")

def cliente_interactivo():
    """
    Cliente que lee líneas del teclado y las envía al FIFO.
    
    Demuestra la entrada interactiva a través de FIFOs:
    - Teclado → FIFO → Proceso receptor
    - Comando 'exit' para terminar ordenadamente
    """
    print("=== CLIENTE INTERACTIVO - Ejercicio 3 ===")
    print(f"Enviando entrada al FIFO: {FIFO_PATH}")
    print("Escribe líneas de texto (o 'exit' para salir)")
    print("-" * 50)
    
    try:
        # Verificar que el FIFO existe
        if not os.path.exists(FIFO_PATH):
            print(f"❌ Error: FIFO {FIFO_PATH} no existe")
            print("Primero ejecuta el lector de archivo")
            return
        
        # Abrir FIFO para escritura
        print("Conectando al lector...")
        fd = os.open(FIFO_PATH, os.O_WRONLY)
        print("✅ Conectado. Puedes empezar a escribir:")
        print("(Escribe 'exit' para terminar)")
        
        linea_count = 0
        
        while True:
            try:
                # Leer línea del usuario
                linea = input("> ").strip()
                
                if linea:  # Solo enviar líneas no vacías
                    linea_count += 1
                    
                    # Enviar al FIFO
                    os.write(fd, (linea + '\n').encode('utf-8'))
                    print(f"✅ Enviado: '{linea}'")
                    
                    # Verificar si es comando de salida
                    if linea.lower() == 'exit':
                        print("🚪 Cerrando cliente...")
                        break
                
            except EOFError:
                # Ctrl+D presionado
                print("\nEOF detectado, cerrando...")
                break
        
        os.close(fd)
        print(f"Cliente terminado. Total líneas enviadas: {linea_count}")
        
    except KeyboardInterrupt:
        print("\nCliente interrumpido")
    except OSError as e:
        print(f"Error en cliente: {e}")

def demo_automatica():
    """
    Demo que simula un cliente automático enviando datos al lector
    """
    print("=== DEMO AUTOMÁTICA - Ejercicio 3 ===")
    print("Simulando cliente y lector automáticamente")
    print("-" * 50)
    
    # Limpiar recursos previos
    limpiar_recursos()
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    # Crear FIFO
    os.mkfifo(FIFO_PATH)
    print(f"FIFO creado: {FIFO_PATH}")
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (lector)
        print("Proceso padre: LECTOR DE ARCHIVO")
        time.sleep(0.5)  # Dar tiempo al hijo
        
        try:
            # Abrir archivo para escritura
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as archivo:
                archivo.write(f"=== Demo Log: {datetime.now()} ===\n")
                
                # Abrir FIFO
                fd = os.open(FIFO_PATH, os.O_RDONLY)
                print("✅ FIFO abierto para lectura")
                
                linea_count = 0
                
                while True:
                    # Leer línea
                    buffer = b""
                    while True:
                        char = os.read(fd, 1)
                        if not char:
                            break
                        buffer += char
                        if char == b'\n':
                            break
                    
                    if not buffer:
                        break
                    
                    linea = buffer.decode('utf-8', errors='replace').strip()
                    
                    if linea.lower() == 'exit':
                        archivo.write(f"[{datetime.now()}] EXIT recibido\n")
                        break
                    
                    if linea:
                        linea_count += 1
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        archivo.write(f"[{timestamp}] {linea}\n")
                        archivo.flush()
                        print(f"📝 Guardado: '{linea}'")
                
                os.close(fd)
                archivo.write(f"Total líneas: {linea_count}\n")
            
            print(f"Lector terminado. {linea_count} líneas guardadas")
            
        except OSError as e:
            print(f"Error en lector: {e}")
        
        # Esperar al proceso hijo
        os.waitpid(pid, 0)
        
        # Mostrar archivo resultante
        print(f"\n--- Contenido final de {OUTPUT_FILE} ---")
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"Error: {e}")
        
        limpiar_recursos()
        
    elif pid == 0:  # Proceso hijo (cliente automático)
        print("Proceso hijo: CLIENTE AUTOMÁTICO")
        time.sleep(1)  # Dar tiempo al padre para configurarse
        
        try:
            # Abrir FIFO para escritura
            fd = os.open(FIFO_PATH, os.O_WRONLY)
            
            # Enviar algunas líneas de prueba
            mensajes = [
                "Primera línea de prueba",
                "Segunda línea con datos",
                "Línea con números: 123 456",
                "Línea con símbolos: !@#$%",
                "Texto en español: ñáéíóú",
                "Última línea antes de salir",
                "exit"
            ]
            
            for i, mensaje in enumerate(mensajes, 1):
                print(f"📤 Cliente enviando {i}: '{mensaje}'")
                os.write(fd, (mensaje + '\n').encode('utf-8'))
                time.sleep(0.5)  # Pausa entre mensajes
            
            os.close(fd)
            print("Cliente automático terminado")
            
        except OSError as e:
            print(f"Error en cliente: {e}")
        
        sys.exit(0)
    
    else:
        print("Error en fork()")
        sys.exit(1)

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 3: FIFO + archivos")
    print("Flujo: Entrada interactiva → FIFO → Archivo")
    print("Elige el modo de ejecución:")
    print("1. Lector de archivo (lee FIFO y guarda en output.txt)")
    print("2. Cliente interactivo (envía líneas del teclado al FIFO)")
    print("3. Demo automática (fork para simular ambos)")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            lector_archivo()
        elif opcion == '2':
            cliente_interactivo()
        elif opcion == '3':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_recursos()

if __name__ == "__main__":
    main()