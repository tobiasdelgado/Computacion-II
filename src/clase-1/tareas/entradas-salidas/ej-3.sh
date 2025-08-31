#!/bin/bash
# **Ejercicio 3: Redirección de Errores**
# **Objetivo:** Capturar errores generados por comandos inválidos.

# **Instrucción:**
# Ejecuta un comando que intente listar un directorio inexistente y redirige el mensaje de error a un archivo llamado `errores.log`.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ls /directorio/inexistente 2> "$SCRIPT_DIR/errores.log"