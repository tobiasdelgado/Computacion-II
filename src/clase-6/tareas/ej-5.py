#!/usr/bin/env python3

# Ejercicio 5 — FIFO con apertura condicional
# Objetivo: Usar os.open() y manejar errores.
#
# Instrucciones:
# 1. Usar os.open() con flags como O_NONBLOCK.
# 2. Crear un lector que intente abrir el FIFO sin bloquear.
# 3. Si el FIFO no tiene escritores, debe imprimir un mensaje y salir correctamente.
#
# Desafío adicional: Hacer que el lector reintente 5 veces con espera entre intentos antes de salir.

import os
import sys
import time
import signal
import errno
from datetime import datetime

# Configuración
FIFO_PATH = '/tmp/conditional_fifo'

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

def lector_no_bloqueante():
    """
    Lector que usa O_NONBLOCK para evitar bloqueo.
    
    O_NONBLOCK cambia el comportamiento de apertura y operaciones:
    - open() falla inmediatamente si no hay escritor (ENXIO)
    - read() retorna inmediatamente si no hay datos (EAGAIN/EWOULDBLOCK)
    - Permite operaciones no bloqueantes para mayor control
    """
    print("=== LECTOR NO BLOQUEANTE - Ejercicio 5 ===")
    print(f"Intentando leer del FIFO: {FIFO_PATH}")
    print("Usando O_NONBLOCK para evitar bloqueo")
    print("-" * 50)
    
    try:
        # Crear FIFO si no existe
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
            print(f"FIFO creado: {FIFO_PATH}")
        
        print("Intentando abrir FIFO sin bloquear...")
        
        try:
            # Intentar abrir con O_NONBLOCK
            # Si no hay escritor, fallará inmediatamente con ENXIO
            fd = os.open(FIFO_PATH, os.O_RDONLY | os.O_NONBLOCK)
            print("✅ FIFO abierto exitosamente")
            
        except OSError as e:
            if e.errno == errno.ENXIO:
                print("❌ No hay escritores disponibles en el FIFO")
                print("El FIFO existe pero ningún proceso lo tiene abierto para escritura")
                return False
            else:
                print(f"❌ Error abriendo FIFO: {e}")
                return False
        
        print("📖 Iniciando lectura no bloqueante...")
        
        # Leer datos del FIFO
        buffer_completo = b""
        intentos_sin_datos = 0
        max_intentos_sin_datos = 10
        
        while intentos_sin_datos < max_intentos_sin_datos:
            try:
                # Leer sin bloquear
                data = os.read(fd, 1024)
                
                if data:
                    # Hay datos disponibles
                    buffer_completo += data
                    intentos_sin_datos = 0
                    
                    # Procesar líneas completas
                    while b'\n' in buffer_completo:
                        linea, buffer_completo = buffer_completo.split(b'\n', 1)
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        mensaje = linea.decode('utf-8', errors='replace')
                        
                        if mensaje.strip() == "exit":
                            print("🚪 Comando 'exit' recibido")
                            break
                        
                        print(f"📨 [{timestamp}] {mensaje}")
                else:
                    # EOF - el escritor cerró
                    print("📭 Escritor ha cerrado la conexión")
                    break
                    
            except OSError as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    # No hay datos disponibles ahora
                    intentos_sin_datos += 1
                    print(f"⏳ Sin datos disponibles (intento {intentos_sin_datos}/{max_intentos_sin_datos})")
                    time.sleep(0.5)
                else:
                    print(f"❌ Error leyendo: {e}")
                    break
        
        if intentos_sin_datos >= max_intentos_sin_datos:
            print("⏰ Timeout: No se recibieron datos por mucho tiempo")
        
        os.close(fd)
        print("✅ Lector terminado")
        return True
        
    except KeyboardInterrupt:
        print("\nLector interrumpido")
        return False
    except OSError as e:
        print(f"Error en lector: {e}")
        return False

def lector_con_reintentos(max_reintentos=5, delay_reintento=2.0):
    """
    Lector que reintenta conectar múltiples veces.
    
    Patrón útil para servicios que deben esperar a que aparezca un escritor:
    - Reintentos con backoff exponencial opcional
    - Logging de intentos
    - Salida limpia después de max_reintentos
    """
    print("=== LECTOR CON REINTENTOS - Ejercicio 5 ===")
    print(f"FIFO: {FIFO_PATH}")
    print(f"Máximo {max_reintentos} reintentos con delay de {delay_reintento}s")
    print("-" * 50)
    
    # Crear FIFO si no existe
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)
        print(f"FIFO creado: {FIFO_PATH}")
    
    for intento in range(1, max_reintentos + 1):
        print(f"\n🔄 Intento {intento}/{max_reintentos}")
        
        try:
            # Intentar abrir sin bloquear
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Intentando conectar...")
            
            fd = os.open(FIFO_PATH, os.O_RDONLY | os.O_NONBLOCK)
            
            print("✅ ¡Conexión exitosa!")
            
            # Leer datos
            print("📖 Leyendo datos...")
            while True:
                try:
                    data = os.read(fd, 1024)
                    if not data:
                        print("📭 Escritor desconectado")
                        break
                    
                    mensaje = data.decode('utf-8', errors='replace').strip()
                    if mensaje:
                        if mensaje == "exit":
                            print("🚪 Comando exit recibido")
                            break
                        print(f"📨 Recibido: {mensaje}")
                        
                except OSError as e:
                    if e.errno == errno.EAGAIN:
                        time.sleep(0.1)  # Esperar un poco más de datos
                    else:
                        print(f"Error leyendo: {e}")
                        break
            
            os.close(fd)
            print("✅ Lectura completada exitosamente")
            return True
            
        except OSError as e:
            if e.errno == errno.ENXIO:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"❌ [{timestamp}] Sin escritores disponibles")
                
                if intento < max_reintentos:
                    print(f"⏰ Esperando {delay_reintento}s antes del siguiente intento...")
                    time.sleep(delay_reintento)
                else:
                    print("💀 Se agotaron los reintentos")
                    return False
            else:
                print(f"❌ Error: {e}")
                return False
    
    return False

def escritor_demo():
    """
    Escritor simple para probar los lectores no bloqueantes
    """
    print("=== ESCRITOR DEMO - Ejercicio 5 ===")
    print(f"Escribiendo al FIFO: {FIFO_PATH}")
    print("Escribe mensajes (o 'exit' para salir)")
    print("-" * 50)
    
    try:
        # Verificar que el FIFO existe
        if not os.path.exists(FIFO_PATH):
            print(f"❌ FIFO {FIFO_PATH} no existe")
            print("Primero ejecuta el lector")
            return
        
        # Abrir FIFO para escritura (puede bloquear hasta que haya lector)
        print("Conectando al lector...")
        fd = os.open(FIFO_PATH, os.O_WRONLY)
        print("✅ Conectado")
        
        # Enviar algunos mensajes automáticos primero
        mensajes_auto = [
            "Mensaje automático 1",
            "Mensaje automático 2", 
            "Datos de prueba",
            "Último mensaje automático"
        ]
        
        print("📤 Enviando mensajes automáticos...")
        for msg in mensajes_auto:
            timestamp = datetime.now().strftime("%H:%M:%S")
            mensaje_completo = f"[{timestamp}] {msg}\n"
            os.write(fd, mensaje_completo.encode())
            print(f"Enviado: {msg}")
            time.sleep(1)
        
        # Modo interactivo
        print("\n💬 Modo interactivo activado:")
        while True:
            try:
                mensaje = input("> ").strip()
                if mensaje:
                    if mensaje.lower() == 'exit':
                        os.write(fd, b"exit\n")
                        break
                    else:
                        os.write(fd, (mensaje + "\n").encode())
                        print(f"✅ Enviado: {mensaje}")
            except EOFError:
                break
        
        os.close(fd)
        print("Escritor terminado")
        
    except KeyboardInterrupt:
        print("\nEscritor interrumpido")
    except OSError as e:
        print(f"Error en escritor: {e}")

def demo_automatica():
    """
    Demo que muestra el comportamiento no bloqueante
    """
    print("=== DEMO AUTOMÁTICA - Ejercicio 5 ===")
    print("Demostrando apertura no bloqueante de FIFOs")
    print("-" * 50)
    
    # Limpiar recursos previos
    limpiar_fifo()
    
    # Crear FIFO
    os.mkfifo(FIFO_PATH)
    print(f"FIFO creado: {FIFO_PATH}")
    
    # Probar lector sin escritor (debe fallar inmediatamente)
    print("\n1️⃣ Probando lector sin escritor...")
    try:
        fd = os.open(FIFO_PATH, os.O_RDONLY | os.O_NONBLOCK)
        print("❌ ¡Esto no debería pasar!")
        os.close(fd)
    except OSError as e:
        if e.errno == errno.ENXIO:
            print("✅ Correcto: ENXIO - No hay escritores")
        else:
            print(f"❌ Error inesperado: {e}")
    
    # Crear escritor y lector
    print("\n2️⃣ Creando escritor y lector...")
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (lector)
        time.sleep(1)  # Dar tiempo al escritor
        
        try:
            print("Padre: Intentando leer con O_NONBLOCK...")
            fd = os.open(FIFO_PATH, os.O_RDONLY | os.O_NONBLOCK)
            print("✅ Padre: FIFO abierto exitosamente")
            
            # Leer algunos mensajes
            for i in range(3):
                try:
                    data = os.read(fd, 1024)
                    if data:
                        print(f"📨 Padre recibió: {data.decode().strip()}")
                    else:
                        print("📭 EOF recibido")
                        break
                except OSError as e:
                    if e.errno == errno.EAGAIN:
                        print("⏳ Sin datos, esperando...")
                        time.sleep(0.5)
                    else:
                        print(f"Error: {e}")
                        break
            
            os.close(fd)
            
        except OSError as e:
            print(f"Error en padre: {e}")
        
        # Esperar al hijo
        os.waitpid(pid, 0)
        
    elif pid == 0:  # Proceso hijo (escritor)
        print("Hijo: Actuando como escritor")
        time.sleep(0.5)
        
        try:
            fd = os.open(FIFO_PATH, os.O_WRONLY)
            print("✅ Hijo: FIFO abierto para escritura")
            
            # Enviar algunos mensajes
            for i in range(3):
                msg = f"Mensaje {i+1} del escritor\n"
                os.write(fd, msg.encode())
                print(f"📤 Hijo envió: Mensaje {i+1}")
                time.sleep(0.5)
            
            os.close(fd)
            print("Hijo terminado")
            
        except OSError as e:
            print(f"Error en hijo: {e}")
        
        sys.exit(0)
    
    limpiar_fifo()

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 5: FIFO con apertura condicional")
    print("Demuestra el uso de O_NONBLOCK en FIFOs")
    print("Elige el modo de ejecución:")
    print("1. Lector no bloqueante (falla si no hay escritor)")
    print("2. Lector con reintentos (intenta 5 veces)")
    print("3. Escritor demo (para probar con los lectores)")
    print("4. Demo automática (muestra comportamiento no bloqueante)")
    
    try:
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == '1':
            exito = lector_no_bloqueante()
            if not exito:
                print("\n💡 Ejecuta el escritor demo en otro terminal")
        elif opcion == '2':
            reintentos = input("Máximo reintentos (default 5): ").strip()
            reintentos = int(reintentos) if reintentos.isdigit() else 5
            
            delay = input("Delay entre reintentos en segundos (default 2.0): ").strip()
            delay = float(delay) if delay else 2.0
            
            lector_con_reintentos(reintentos, delay)
        elif opcion == '3':
            escritor_demo()
        elif opcion == '4':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_fifo()

if __name__ == "__main__":
    main()