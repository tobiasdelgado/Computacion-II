#!/bin/bash

# Script para configurar el entorno del TP2 - Sistema de Scraping Distribuido

echo "=========================================="
echo "  TP2 - Setup del Sistema de Scraping"
echo "=========================================="
echo ""

echo "[1/5] Creando entorno virtual..."
python3 -m venv venv

echo "[2/5] Activando entorno virtual..."
source venv/bin/activate

echo "[3/5] Actualizando pip..."
pip install --upgrade pip

echo "[4/5] Instalando dependencias Python..."
pip install -r requirements.txt

echo "[5/5] Instalando navegadores para Playwright..."
playwright install chromium

echo ""
echo "=========================================="
echo "  ¡Configuración completada!"
echo "=========================================="
echo ""
echo "Para iniciar el sistema, ejecuta:"
echo "  ./start.sh"
echo ""
echo "O manualmente:"
echo "  Terminal 1: python server_b.py -i 127.0.0.1 -p 9000"
echo "  Terminal 2: python server_a.py -i 127.0.0.1 -p 8000"
echo ""
