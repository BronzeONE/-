from django.contrib import admin

from .models import CreatingOrder, Purchase, TestReport


@admin.register(CreatingOrder)
class CreatingOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'user', 'status', 'pickup_point', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at', 'responded_at')
    search_fields = ('article', 'user__phone_number', 'user__first_name', 'user__last_name')
    autocomplete_fields = ('user', 'assigned_by')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'tester', 'status', 'pickup_point', 'has_report', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('article', 'tester__phone_number', 'external_id')
    autocomplete_fields = ('tester', 'creating_order')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_report(self, obj):
        return hasattr(obj, 'test_report')
    has_report.boolean = True
    has_report.short_description = 'Есть отчёт'


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase', 'item_name', 'category', 'full_name', 'completed_at', 'created_at')
    list_filter = ('category', 'report_type', 'issues_occured', 'ready_for_next', 'created_at')
    search_fields = ('item_name', 'full_name', 'contact', 'purchase__article')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            'Заказ',
            {
                'fields': ('purchase',)
            },
        ),
        (
            'Идентификация задания',
            {
                'fields': (
                    'full_name',
                    'contact',
                    'item_name',
                    'category',
                    'received_at',
                    'completed_at',
                )
            },
        ),
        (
            'Подтверждение выполнения',
            {
                'fields': (
                    'report_type',
                    'proof_links',
                    'proof_files',
                )
            },
        ),
        (
            'Количественные оценки',
            {
                'fields': (
                    'score_overall',
                    'score_expectation_fit',
                    'score_quality_effect',
                    'score_usability',
                    'score_value_for_money',
                    'score_recommend',
                )
            },
        ),
        (
            'Качественная обратная связь',
            {
                'fields': (
                    'likes',
                    'improvements',
                    'review_text',
                    'emotions_3_words',
                )
            },
        ),
        (
            'Условия и итоги',
            {
                'fields': (
                    'issues_occured',
                    'issues_note',
                    'would_buy',
                    'ready_for_next',
                )
            },
        ),
        (
            'Согласия',
            {
                'fields': (
                    'consent_truthful',
                    'consent_use_materials',
                )
            },
        ),
        (
            'Даты',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )
