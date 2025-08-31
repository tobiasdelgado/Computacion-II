#!/usr/bin/env python3

# Ejercicio 1: Eco Simple
# Crea un programa en Python que establezca comunicación entre un proceso padre y un hijo 
# mediante un pipe. El padre debe enviar un mensaje al hijo, y el hijo debe recibir ese 
# mensaje y devolverlo al padre (eco).

import os
import sys

def main():
    # Crear pipe - devuelve dos descriptores: uno para leer [0] y otro para escribir [1]
    pipe_padre_hijo = os.pipe()  # Para enviar mensaje del padre al hijo
    pipe_hijo_padre = os.pipe()  # Para recibir eco del hijo al padre
    
    # Crear proceso hijo con fork()
    pid = os.fork()
    
    if pid > 0:  # Proceso padre
        # Cerrar extremos que no va a usar
        os.close(pipe_padre_hijo[0])  # No va a leer del primer pipe
        os.close(pipe_hijo_padre[1])  # No va a escribir en el segundo pipe
        
        # Enviar mensaje al hijo
        mensaje = "Hola desde el proceso padre!"
        os.write(pipe_padre_hijo[1], mensaje.encode())
        print(f"Padre: Enviando mensaje -> '{mensaje}'")
        
        # Cerrar extremo de escritura para que el hijo reciba EOF
        os.close(pipe_padre_hijo[1])
        
        # Leer respuesta del hijo
        respuesta = os.read(pipe_hijo_padre[0], 1024).decode()
        print(f"Padre: Recibió eco -> '{respuesta}'")
        
        # Cerrar pipe y esperar al hijo
        os.close(pipe_hijo_padre[0])
        os.waitpid(pid, 0)
        
    elif pid == 0:  # Proceso hijo
        # Cerrar extremos que no va a usar
        os.close(pipe_padre_hijo[1])  # No va a escribir en el primer pipe
        os.close(pipe_hijo_padre[0])  # No va a leer del segundo pipe
        
        # Leer mensaje del padre
        mensaje_recibido = os.read(pipe_padre_hijo[0], 1024).decode()
        print(f"Hijo: Recibió mensaje -> '{mensaje_recibido}'")
        
        # Enviar eco de vuelta al padre
        eco = f"ECO: {mensaje_recibido}"
        os.write(pipe_hijo_padre[1], eco.encode())
        print(f"Hijo: Enviando eco -> '{eco}'")
        
        # Cerrar pipes
        os.close(pipe_padre_hijo[0])
        os.close(pipe_hijo_padre[1])
        
        sys.exit(0)
    
    else:  # Error en fork
        print("Error al crear proceso hijo")
        sys.exit(1)

if __name__ == "__main__":
    main()