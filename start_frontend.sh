#!/bin/bash
# Скрипт для запуска frontend

cd "$(dirname "$0")/frontend"

echo "Запуск frontend на http://localhost:3000"
python3 -m http.server 3000 --bind 127.0.0.1

