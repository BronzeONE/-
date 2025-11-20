# MVP для тестирования продуктов

## Структура проекта

```
.
├── frontend/              # Frontend (HTML, CSS, JavaScript)
│   ├── index.html        # Главная страница
│   ├── app.js            # JavaScript логика
│   ├── styles.css        # Стили
│   └── logo.svg          # Логотип ShopTest
│
├── mvp_backend/          # Django Backend
│   ├── accounts/         # Приложение для пользователей
│   │   ├── models.py     # User, UserProfile
│   │   ├── views.py      # API endpoints для авторизации и профиля
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── orders/           # Приложение для заказов
│   │   ├── models.py     # CreatingOrder, Purchase, TestReport
│   │   ├── views.py      # API endpoints для заказов и отчетов
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   └── mvp_backend/      # Настройки Django
│       ├── settings.py
│       └── urls.py
│
├── .env                  # Переменные окружения (не в git)
├── .env.example          # Пример переменных окружения
├── requirements.txt      # Python зависимости
└── README.md            # Этот файл
```

## Быстрый старт

### 1. Установка зависимостей

```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать виртуальное окружение
# На macOS/Linux:
source venv/bin/activate
# На Windows:
# venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Скопировать пример файла окружения
cp .env.example .env

# Отредактировать .env и установить SECRET_KEY
# Для генерации нового SECRET_KEY:
cd mvp_backend
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Настройка базы данных

```bash
cd mvp_backend
source ../venv/bin/activate

# Применить миграции
python manage.py migrate

# Создать суперпользователя для доступа к админке
python manage.py createsuperuser
```

### 4. Запуск проекта

**Backend (Django):**
```bash
cd mvp_backend
source ../venv/bin/activate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
python3 -m http.server 3000 --bind 127.0.0.1
```

## Доступ

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

## Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=

# Security Settings (для production)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=31536000
```

### Для production:

1. Установите `DEBUG=False`
2. Установите безопасный `SECRET_KEY` (минимум 50 символов)
3. Укажите реальные хосты в `ALLOWED_HOSTS`
4. Настройте `CORS_ALLOWED_ORIGINS` вместо `CORS_ALLOW_ALL_ORIGINS=True`
5. Включите `SECURE_SSL_REDIRECT=True` (если используете HTTPS)

## Основной функционал

1. **Авторизация** - регистрация и вход по номеру телефона
2. **Профиль** - многошаговая форма профиля (6 шагов)
3. **Заказы** - просмотр и принятие заказов от модератора
4. **Отчеты** - форма отчета о тестировании после принятия заказа

## Безопасность

Проект настроен с учетом лучших практик безопасности:

- ✅ Переменные окружения для секретных данных
- ✅ Настройки безопасности для production (HSTS, CSRF, XSS защита)
- ✅ CORS настроен правильно
- ✅ Валидация паролей
- ✅ Защита от SQL-инъекций (ORM Django)

## Цветовая схема

- Основной цвет: #0F7657 (темно-зеленый)
- Логотип: ShopTest с оранжевой галочкой

## Деплой

### Подготовка к деплою:

1. Установите переменные окружения на сервере
2. Установите `DEBUG=False`
3. Соберите статические файлы: `python manage.py collectstatic`
4. Настройте веб-сервер (Nginx/Apache) для статических файлов
5. Настройте WSGI сервер (Gunicorn/uWSGI)

### Пример с Gunicorn:

```bash
pip install gunicorn
gunicorn mvp_backend.wsgi:application --bind 0.0.0.0:8000
```

## Миграции

Все миграции применены. Для проверки:

```bash
python manage.py showmigrations
python manage.py migrate
```

## Troubleshooting

**Ошибка "ModuleNotFoundError: No module named 'dotenv'":**
```bash
pip install python-dotenv
```

**Ошибка миграций:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Ошибка CORS:**
Проверьте настройки `CORS_ALLOWED_ORIGINS` в `.env`
