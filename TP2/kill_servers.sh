#!/bin/bash

echo "Buscando y matando servidores en puertos 8000 y 9000..."

if lsof -ti:9000 >/dev/null 2>&1; then
    lsof -ti:9000 | xargs kill -9 2>/dev/null
    echo "✓ Puerto 9000 liberado"
else
    echo "  Puerto 9000 ya estaba libre"
fi

if lsof -ti:8000 >/dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "✓ Puerto 8000 liberado"
else
    echo "  Puerto 8000 ya estaba libre"
fi

echo ""
echo "Puertos liberados. Ahora puedes ejecutar ./start.sh"
