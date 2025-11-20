#!/bin/bash
# Скрипт для запуска Django backend

cd "$(dirname "$0")/mvp_backend"
source ../venv/bin/activate

echo "Запуск Django backend..."
python manage.py runserver

