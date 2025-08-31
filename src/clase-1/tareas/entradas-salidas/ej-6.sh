#!/bin/bash
# **Ejercicio 6: Redirección Combinada de Salida y Errores**
# **Objetivo:** Guardar la salida estándar y los errores en un solo archivo.

# **Instrucción:**
# Ejecuta un comando que liste un directorio válido e inválido al mismo tiempo, y redirige toda la salida (éxito y errores) a `resultado_completo.log`.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ls "$SCRIPT_DIR" /directorio/inexistente &> "$SCRIPT_DIR/resultado-completo.log"