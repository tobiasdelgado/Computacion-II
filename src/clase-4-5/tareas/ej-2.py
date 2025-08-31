#!/usr/bin/env python3

# Ejercicio 2: Contador de Palabras
# Implementa un sistema donde el proceso padre lee un archivo de texto y envía su contenido 
# línea por línea a un proceso hijo a través de un pipe. El hijo debe contar las palabras 
# en cada línea y devolver el resultado al padre.

import os
import sys
import tempfile

def crear_archivo_prueba():
    """Crear un archivo de prueba si no existe"""
    archivo_prueba = "/tmp/texto_prueba.txt"
    if not os.path.exists(archivo_prueba):
        with open(archivo_prueba, 'w') as f:
            f.write("Esta es la primera línea con cinco palabras\n")
            f.write("Segunda línea más corta\n") 
            f.write("La tercera línea tiene exactamente seis palabras aquí\n")
            f.write("Última línea final\n")
    return archivo_prueba

def main():
    # Crear archivo de prueba
    archivo = crear_archivo_prueba()
    print(f"Usando archivo: {archivo}")
    
    # Crear pipes para comunicación bidireccional
    pipe_padre_hijo = os.pipe()  # Para enviar líneas del padre al hijo
    pipe_hijo_padre = os.pipe()  # Para recibir conteos del hijo al padre
    
    # Crear proceso hijo
    pid = os.fork()
    
    if pid > 0:  # Proceso padre
        # Cerrar extremos no utilizados
        os.close(pipe_padre_hijo[0])  # No lee del primer pipe
        os.close(pipe_hijo_padre[1])  # No escribe en el segundo pipe
        
        # Leer archivo línea por línea y enviarlo al hijo
        try:
            with open(archivo, 'r') as f:
                for numero_linea, linea in enumerate(f, 1):
                    linea = linea.strip()
                    print(f"Padre: Enviando línea {numero_linea}: '{linea}'")
                    
                    # Enviar línea al hijo (con número de línea)
                    mensaje = f"{numero_linea}:{linea}"
                    os.write(pipe_padre_hijo[1], mensaje.encode())
                    
                    # Leer respuesta del hijo
                    respuesta = os.read(pipe_hijo_padre[0], 1024).decode()
                    print(f"Padre: {respuesta}")
            
            # Enviar señal de fin al hijo
            os.write(pipe_padre_hijo[1], b"FIN")
            
        except FileNotFoundError:
            print(f"Error: No se pudo abrir el archivo {archivo}")
        
        # Cerrar pipes y esperar al hijo
        os.close(pipe_padre_hijo[1])
        os.close(pipe_hijo_padre[0])
        os.waitpid(pid, 0)
        
    elif pid == 0:  # Proceso hijo
        # Cerrar extremos no utilizados
        os.close(pipe_padre_hijo[1])  # No escribe en el primer pipe
        os.close(pipe_hijo_padre[0])  # No lee del segundo pipe
        
        print("Hijo: Iniciado, esperando líneas...")
        
        while True:
            # Leer línea del padre
            datos = os.read(pipe_padre_hijo[0], 1024).decode()
            
            # Verificar si es señal de fin
            if datos == "FIN":
                print("Hijo: Recibida señal de fin, terminando")
                break
            
            # Separar número de línea y contenido
            if ":" in datos:
                numero_linea, linea = datos.split(":", 1)
                
                # Contar palabras (dividir por espacios y filtrar vacías)
                palabras = [palabra for palabra in linea.split() if palabra]
                cantidad_palabras = len(palabras)
                
                # Enviar resultado al padre
                resultado = f"Línea {numero_linea}: {cantidad_palabras} palabras"
                os.write(pipe_hijo_padre[1], resultado.encode())
                print(f"Hijo: Procesada {resultado.lower()}")
        
        # Cerrar pipes
        os.close(pipe_padre_hijo[0])
        os.close(pipe_hijo_padre[1])
        sys.exit(0)
        
    else:  # Error en fork
        print("Error al crear proceso hijo")
        sys.exit(1)

if __name__ == "__main__":
    main()