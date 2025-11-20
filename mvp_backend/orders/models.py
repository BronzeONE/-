from django.conf import settings
from django.db import models


class CreatingOrder(models.Model):
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = (
        (STATUS_PROCESSING, 'В обработке'),
        (STATUS_APPROVED, 'Одобрено'),
        (STATUS_REJECTED, 'Отклонено'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_requests',
    )
    article = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    pickup_point = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PROCESSING)
    payload = models.JSONField(default=dict, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_order_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Запрос на заказ'
        verbose_name_plural = 'Запросы на заказы'

    def __str__(self):
        return f'{self.article} ({self.get_status_display()})'


class Purchase(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_COMPLETED, 'Завершено'),
        (STATUS_CANCELLED, 'Отменено'),
    )

    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases',
    )
    creating_order = models.OneToOneField(
        CreatingOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase',
    )
    external_id = models.CharField(max_length=255, blank=True)
    article = models.CharField(max_length=255)
    pickup_point = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        managed = False
        db_table = 'purchases'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ #{self.id or "new"} - {self.article}'


class TestReport(models.Model):
    """Универсальная форма отчёта о тестировании."""
    
    CATEGORY_CHOICES = (
        ('cosmetics', 'Косметика'),
        ('clothing', 'Одежда'),
        ('tech', 'Техника'),
        ('home', 'Дом'),
        ('other', 'Другое'),
    )
    
    REPORT_TYPE_CHOICES = (
        ('publication', 'Публикация'),
        ('marketplace_review', 'Отзыв на МП'),
        ('photo_report', 'Фото-отчёт'),
        ('video_report', 'Видео-отчёт'),
        ('other', 'Другое'),
    )
    
    WOULD_BUY_CHOICES = (
        ('yes', 'Да'),
        ('no', 'Нет'),
        ('depends_on_price', 'Зависит от цены'),
    )
    
    purchase = models.OneToOneField(
        Purchase,
        on_delete=models.CASCADE,
        related_name='test_report',
        verbose_name='Заказ'
    )
    
    # 1) Идентификация задания
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    contact = models.CharField(max_length=255, verbose_name='Телефон/Telegram')
    item_name = models.CharField(max_length=255, verbose_name='Название товара/кейса')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    received_at = models.DateField(verbose_name='Дата получения')
    completed_at = models.DateField(verbose_name='Дата завершения')
    
    # 2) Подтверждение выполнения
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        blank=True,
        verbose_name='Тип отчёта'
    )
    proof_links = models.JSONField(default=list, blank=True, verbose_name='Ссылки на материалы')
    proof_files = models.JSONField(default=list, blank=True, verbose_name='Загруженные файлы (пути)')
    
    # 3) Количественные оценки
    score_overall = models.IntegerField(null=True, blank=True, verbose_name='Общее впечатление (1-5)')
    score_expectation_fit = models.IntegerField(null=True, blank=True, verbose_name='Соответствие ожиданиям (1-5)')
    score_quality_effect = models.IntegerField(null=True, blank=True, verbose_name='Качество/эффективность (1-5)')
    score_usability = models.IntegerField(null=True, blank=True, verbose_name='Удобство использования (1-5)')
    score_value_for_money = models.IntegerField(null=True, blank=True, verbose_name='Соотношение цена/качество (1-5)')
    score_recommend = models.IntegerField(null=True, blank=True, verbose_name='Готовность рекомендовать (0-10)')
    
    # 4) Качественная обратная связь
    likes = models.TextField(blank=True, verbose_name='Что понравилось?')
    improvements = models.TextField(blank=True, verbose_name='Что улучшить?')
    review_text = models.TextField(max_length=1000, blank=True, verbose_name='Комментарий/отзыв')
    emotions_3_words = models.CharField(max_length=255, blank=True, verbose_name='3 слова-эмоции о товаре')
    
    # 5) Условия и итоги
    issues_occured = models.BooleanField(default=False, verbose_name='Опыт проблем/дефектов')
    issues_note = models.TextField(blank=True, verbose_name='Описание проблем')
    would_buy = models.CharField(
        max_length=50,
        choices=WOULD_BUY_CHOICES,
        blank=True,
        verbose_name='Купили бы сами?'
    )
    ready_for_next = models.BooleanField(default=False, verbose_name='Готовность к повторному тесту')
    
    # Согласия
    consent_truthful = models.BooleanField(default=False, verbose_name='Подтверждаю достоверность данных')
    consent_use_materials = models.BooleanField(default=False, verbose_name='Разрешаю использовать материалы')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Отчёт о тестировании'
        verbose_name_plural = 'Отчёты о тестировании'
    
    def __str__(self):
        return f'Отчёт по заказу #{self.purchase_id} - {self.item_name}'
