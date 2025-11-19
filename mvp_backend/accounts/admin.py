from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserChangeForm, UserCreationForm
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('phone_number',)
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Личная информация'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'full_name',
        'country',
        'city',
        'is_completed',
        'is_participating',
        'updated_at',
    )
    search_fields = ('user__phone_number', 'full_name', 'contact', 'city', 'country')
    list_filter = ('is_completed', 'is_participating', 'country', 'has_self_employment', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'user',
                    'full_name',
                    'country',
                    'city',
                    'age',
                    'gender',
                    'coverage_regions',
                    'contact',
                    'date_of_birth',
                    'pickup_point',
                )
            },
        ),
        (
            'Самозанятость и блог',
            {
                'fields': (
                    'has_self_employment',
                    'ready_for_self_employment',
                    'main_blog_link',
                    'social_links',
                )
            },
        ),
        (
            'Контент и платформа',
            {
                'fields': (
                    'platforms',
                    'blog_topics',
                    'blog_description',
                    'blog_experience',
                    'publication_frequency',
                )
            },
        ),
        (
            'Аудитория',
            {
                'fields': (
                    'subscribers_by_platform',
                    'average_reach',
                    'audience_gender_age',
                    'audience_region',
                    'engagement_level',
                )
            },
        ),
        (
            'Опыт и сотрудничество',
            {
                'fields': (
                    'has_collaborations',
                    'collaboration_examples',
                    'ready_to_share_results',
                    'ready_for_paid_ads',
                )
            },
        ),
        (
            'Формат сотрудничества',
            {
                'fields': (
                    'collaboration_formats',
                    'ad_pricing',
                    'ready_for_barter',
                    'barter_categories',
                )
            },
        ),
        (
            'Дополнительно',
            {
                'fields': (
                    'ready_for_brand_projects',
                    'products_wont_advertise',
                    'blog_management',
                    'has_media_kit',
                    'media_kit_link',
                    'ready_for_blogger_community',
                    'additional_info',
                )
            },
        ),
        (
            'Согласия',
            {
                'fields': (
                    'consent_privacy',
                    'consent_marketing_email',
                    'consent_marketing_calls',
                )
            },
        ),
        (
            'Статусы',
            {
                'fields': (
                    'is_completed',
                    'is_participating',
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )
