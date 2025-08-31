#!/bin/bash
# **Ejercicio 9: Redirección Avanzada con `exec`**
# **Objetivo:** Usar `exec` para establecer una redirección persistente.

# **Instrucción:**
# Utiliza `exec` para redirigir toda la salida de comandos ejecutados en la sesión actual a un archivo llamado `sesion.log`.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# exec > redirige TODA la salida estándar (stdout) del script hacia el archivo
# A partir de esta línea, todo lo que normalmente aparecería en pantalla va al archivo
exec > "$SCRIPT_DIR/sesion.log"

# Estos comandos ya no aparecen en pantalla, van directo al archivo sesion.log
echo "Esta salida va al archivo"
ls "$SCRIPT_DIR"