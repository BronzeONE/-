from django.contrib import admin

from .models import CreatingOrder, Purchase


@admin.register(CreatingOrder)
class CreatingOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'user', 'status', 'pickup_point', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at', 'responded_at')
    search_fields = ('article', 'user__phone_number', 'user__first_name', 'user__last_name')
    autocomplete_fields = ('user', 'assigned_by')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'tester', 'status', 'pickup_point', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('article', 'tester__phone_number', 'external_id')
    autocomplete_fields = ('tester', 'creating_order')
    readonly_fields = ('created_at', 'updated_at')
