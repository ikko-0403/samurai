# restaurants/admin.py
from django.contrib import admin
from .models import Company, Category, Restaurant


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'representative', 'zipcode', 'created_at')
    search_fields = ('name', 'representative')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'company',
        'category',
        'price_min',
        'price_max',
        'open_time',
        'close_time',
        'holiday',
        'created_at',
    )
    list_filter = ('company', 'category', 'holiday')
    search_fields = ('name', 'address')
    ordering = ('name',)
    list_select_related = ('company', 'category')

    fieldsets = (
        (None, {
            'fields': ('name', 'company', 'category', 'image', 'description')
        }),
        ('営業情報', {
            'fields': ('price_min', 'price_max', 'open_time', 'close_time', 'holiday')
        }),
        ('所在地', {
            'fields': ('zipcode', 'address', 'tel')
        }),
        ('その他', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
