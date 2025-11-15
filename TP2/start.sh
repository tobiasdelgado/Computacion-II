#!/bin/bash

# Script para iniciar ambos servidores del TP2

echo "=========================================="
echo "  TP2 - Sistema de Scraping Distribuido"
echo "=========================================="
echo ""

if lsof -Pi :9000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Puerto 9000 ya está en uso"
    echo "Ejecuta: ./kill_servers.sh"
    exit 1
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Puerto 8000 ya está en uso"
    echo "Ejecuta: ./kill_servers.sh"
    exit 1
fi

source venv/bin/activate

echo "Iniciando Servidor B (Procesamiento) en puerto 9000..."
python server_b.py -i 127.0.0.1 -p 9000 &
SERVER_B_PID=$!

sleep 2

echo "Iniciando Servidor A (Scraping) en puerto 8000..."
python server_a.py -i 127.0.0.1 -p 8000 &
SERVER_A_PID=$!

echo ""
echo "=========================================="
echo "  Servidores en ejecución"
echo "=========================================="
echo ""
echo "Servidor B (Procesamiento): PID $SERVER_B_PID"
echo "Servidor A (HTTP):          PID $SERVER_A_PID"
echo ""
echo "Prueba el sistema con:"
echo "  python client.py https://example.com"
echo ""
echo "O con curl:"
echo "  curl 'http://127.0.0.1:8000/scrape?url=https://example.com'"
echo ""
echo "Para detener los servidores: Ctrl+C"
echo ""

trap "echo ''; echo 'Deteniendo servidores...'; kill -TERM $SERVER_B_PID $SERVER_A_PID 2>/dev/null; sleep 2; kill -9 $SERVER_B_PID $SERVER_A_PID 2>/dev/null; exit" INT TERM

wait
