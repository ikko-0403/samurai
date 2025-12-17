from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'price', 'started_at', 'next_billing_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'stripe_customer_id', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('ユーザー情報', {
            'fields': ('user',)
        }),
        ('Stripe情報', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id')
        }),
        ('サブスクリプション情報', {
            'fields': ('status', 'price')
        }),
        ('日付情報', {
            'fields': ('started_at', 'next_billing_date', 'canceled_at', 'created_at', 'updated_at')
        }),
    )
