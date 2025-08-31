#!/bin/bash
# **Ejercicio 10: Uso Complejo de Pipes y Redirección**
# **Objetivo:** Procesar múltiples flujos de datos encadenados.

# **Instrucción:**
# Construye un pipeline que:
# 1. Liste todos los archivos en `/var/log`.
# 2. Filtre los que contengan "syslog" en su nombre.
# 3. Cuente cuántos hay.
# 4. Redirija tanto la salida estándar como la de error a `conteo_syslog.log`.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pipeline completo con redirección de salida y errores
# ls /var/log: lista archivos del directorio
# | grep syslog: filtra solo los que contienen "syslog"
# | wc -l: cuenta las líneas (archivos encontrados)
# &> redirige tanto stdout como stderr al archivo
ls /var/log | grep syslog | wc -l &> "$SCRIPT_DIR/conteo-syslog.log"