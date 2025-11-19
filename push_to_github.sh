#!/bin/bash

# Инициализация git репозитория
git init

# Добавление remote
git remote add origin https://github.com/solutionvasya/-.git

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: MVP для тестирования продуктов с многошаговой формой профиля"

# Переименование ветки в main (если нужно)
git branch -M main

# Push в репозиторий
git push -u origin main

echo "✅ Код успешно запушен в репозиторий!"
