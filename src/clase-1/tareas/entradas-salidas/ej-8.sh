#!/bin/bash
# **Ejercicio 8: Creación de Alias con Descriptores de Archivo**
# **Objetivo:** Manipular descriptores de archivo manualmente.

# **Instrucción:**
# Ejecuta un comando que cree un descriptor de archivo adicional para `stdout`, lo use para escribir en `salida_custom.log` y luego lo cierre.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Crear descriptor de archivo 3 que apunta al archivo salida-custom.log
# exec 3> significa: "abre el descriptor 3 para escritura hacia el archivo"
exec 3> "$SCRIPT_DIR/salida-custom.log"

# Escribir al descriptor 3 usando >&3
# >&3 significa: "redirige la salida hacia el descriptor 3"
echo "Mensaje escrito usando descriptor personalizado" >&3

# Cerrar el descriptor 3
# exec 3>&- significa: "cierra el descriptor 3"
exec 3>&-