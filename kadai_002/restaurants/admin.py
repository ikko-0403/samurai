# restaurants/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Company, Category, Restaurant, Favorite, Table

User = get_user_model()

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'representative', 'zipcode', 'created_at')
    search_fields = ('name', 'representative')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("id",)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'company',
        'category',
        'owner',
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
    list_select_related = ('company', 'category', 'owner')

    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'company', 'category', 'image', 'description')
        }),
        ('営業情報', {
            'fields': ('price_min', 'price_max', 'open_time', 'close_time', 'holiday')
        }),
        ('住所', {
            'fields': ('zipcode', 'address', 'tel')
        }),
        ('その他', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            # ★ オーナーメンバーだけを候補に
            kwargs["queryset"] = User.objects.filter(is_owner_member=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "created_at")
    list_filter = ("restaurant",)
    search_fields = ("user__email", "restaurant__name")


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'capacity', 'created_at')
    list_filter = ('capacity', 'restaurant')
    search_fields = ('restaurant__name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('restaurant', 'capacity')