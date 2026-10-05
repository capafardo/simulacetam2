#!/usr/bin/env bash
# Simulacetam Launcher Script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "$DIR/simulado.py" "$@"
else
    echo "Erro: Python 3 não foi encontrado no sistema."
    exit 1
fi
