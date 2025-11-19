from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Custom manager for the application's user model."""

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Users must have a phone number')

        email = extra_fields.get('email')
        if email:
            extra_fields['email'] = self.normalize_email(email)

        if password is None:
            raise ValueError('Users must set a password')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Authentication user identified by phone number."""

    phone_number = PhoneNumberField(unique=True, region='RU')
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.phone_number)


class UserProfile(models.Model):
    """Extended profile information for bloggers/influencers."""

    # Шаг 1: Базовая информация
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО или псевдоним блогера')
    has_self_employment = models.BooleanField(null=True, blank=True, verbose_name='Есть ли у вас самозанятость?')
    ready_for_self_employment = models.CharField(
        max_length=50,
        blank=True,
        choices=[('yes', 'Да'), ('no', 'Нет'), ('maybe', 'Возможно')],
        verbose_name='Готовы ли вы оформить самозанятость?'
    )
    main_blog_link = models.URLField(blank=True, verbose_name='Ссылка на основной блог')
    social_links = models.JSONField(default=list, blank=True, verbose_name='Ссылки на все активные соцсети')
    country = models.CharField(max_length=100, blank=True, verbose_name='Страна')
    city = models.CharField(max_length=255, blank=True, verbose_name='Город проживания')
    age = models.IntegerField(null=True, blank=True, verbose_name='Возраст')
    gender = models.CharField(
        max_length=1,
        blank=True,
        choices=[('M', 'М'), ('F', 'Ж')],
        verbose_name='Пол'
    )
    coverage_regions = models.CharField(max_length=500, blank=True, verbose_name='Город(а)/регионы охвата')

    # Шаг 2: Контент и платформа
    platforms = models.JSONField(default=list, blank=True, verbose_name='Платформы, на которых ведёшь блог')
    blog_topics = models.JSONField(default=list, blank=True, verbose_name='Тематика блога')
    blog_description = models.TextField(blank=True, verbose_name='Краткое описание блога')
    blog_experience = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('<6months', 'До 6 месяцев'),
            ('6months-1year', '6 мес - 1 год'),
            ('1-2years', '1-2 года'),
            ('>2years', 'Более 2 лет')
        ],
        verbose_name='Как давно ведёшь блог?'
    )
    publication_frequency = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('daily', 'Ежедневно'),
            ('few_times_week', 'Несколько раз в неделю'),
            ('once_week', 'Раз в неделю'),
            ('less_often', 'Реже')
        ],
        verbose_name='Частота публикаций'
    )

    # Шаг 3: Аудитория
    subscribers_by_platform = models.JSONField(default=list, blank=True, verbose_name='Количество подписчиков по платформам')
    average_reach = models.JSONField(default=list, blank=True, verbose_name='Средний охват постов/сторис/видео')
    audience_gender_age = models.TextField(blank=True, verbose_name='Пол и возраст аудитории')
    audience_region = models.CharField(max_length=255, blank=True, verbose_name='Основной регион/страна аудитории')
    engagement_level = models.CharField(max_length=255, blank=True, verbose_name='Уровень вовлечённости')

    # Шаг 4: Опыт и сотрудничество
    has_collaborations = models.BooleanField(default=False, verbose_name='Были ли у тебя уже рекламные коллаборации?')
    collaboration_examples = models.JSONField(default=list, blank=True, verbose_name='Примеры успешных коллабораций')
    ready_to_share_results = models.CharField(
        max_length=50,
        blank=True,
        choices=[('yes', 'Да'), ('no', 'Нет'), ('by_agreement', 'По договорённости')],
        verbose_name='Готов(а) делиться результатами'
    )
    ready_for_paid_ads = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('yes_no_problem', 'Да, без проблем'),
            ('depends_on_conditions', 'Зависит от условий'),
            ('no', 'Нет')
        ],
        verbose_name='Готов(а) делать рекламу по договору/купленным сделкам?'
    )

    # Шаг 5: Формат сотрудничества
    collaboration_formats = models.JSONField(default=list, blank=True, verbose_name='Какие форматы сотрудничества тебе интересны?')
    ad_pricing = models.JSONField(default=list, blank=True, verbose_name='Стоимость рекламы')
    ready_for_barter = models.CharField(
        max_length=50,
        blank=True,
        choices=[('yes', 'Да'), ('no', 'Нет'), ('depends_on_product', 'Зависит от товара/условий')],
        verbose_name='Готов(а) на бартерное сотрудничество?'
    )
    barter_categories = models.JSONField(default=list, blank=True, verbose_name='Какие категории товаров тебе интересны для бартерных')

    # Шаг 6: Дополнительно
    ready_for_brand_projects = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('yes', 'Да'),
            ('maybe_depends', 'Возможно, смотря на условия'),
            ('no', 'Нет')
        ],
        verbose_name='Готов(а) участвовать в проектах/промо-акциях/челленджах от брендов?'
    )
    products_wont_advertise = models.TextField(blank=True, verbose_name='Какой товар не будешь рекламировать точно?')
    blog_management = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('myself', 'Сам(а)'),
            ('assistant_manager', 'Есть помощник/менеджер'),
            ('agency', 'Агентство')
        ],
        verbose_name='Ты сам(а) ведёшь блог или есть команда/менеджер?'
    )
    has_media_kit = models.BooleanField(null=True, blank=True, verbose_name='Есть ли у тебя медиа-кит?')
    media_kit_link = models.URLField(blank=True, verbose_name='Ссылка на медиа-кит')
    ready_for_blogger_community = models.CharField(
        max_length=50,
        blank=True,
        choices=[('yes', 'Да'), ('maybe', 'Возможно'), ('no', 'Нет')],
        verbose_name='Согласен(на) ли ты участвовать в закрытом сообществе блогеров?'
    )
    additional_info = models.TextField(blank=True, verbose_name='Дополнительная информация, пожелания, ссылки')
    consent_privacy = models.BooleanField(default=False, verbose_name='Согласие на обработку персональных данных')
    consent_marketing_email = models.BooleanField(default=False, verbose_name='Согласие на получение рекламных материалов на email')
    consent_marketing_calls = models.BooleanField(default=False, verbose_name='Согласие на получение информационных и рекламных звонков')

    # Старые поля (для обратной совместимости)
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name='Контакт (телефон или Telegram)')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    pickup_point = models.CharField(max_length=255, blank=True, null=True, verbose_name='ПВЗ')

    # Статусы
    is_completed = models.BooleanField(default=False, verbose_name='Профиль заполнен')
    is_participating = models.BooleanField(default=False, verbose_name='Участвует в заказах')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль({self.user_id})'
