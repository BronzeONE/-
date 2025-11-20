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
└── requirements.txt      # Python зависимости
```

## Запуск проекта

### Backend (Django)
```bash
cd mvp_backend
source ../venv/bin/activate
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
python3 -m http.server 3000 --bind 127.0.0.1
```

## Доступ
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Основной функционал

1. **Авторизация** - регистрация и вход по номеру телефона
2. **Профиль** - многошаговая форма профиля (6 шагов)
3. **Заказы** - просмотр и принятие заказов от модератора
4. **Отчеты** - форма отчета о тестировании после принятия заказа

## Цветовая схема
- Основной цвет: #0F7657 (темно-зеленый)
- Логотип: ShopTest с оранжевой галочкой

