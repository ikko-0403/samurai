from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('email', 'name', 'is_owner_member', 'is_paid_member', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'name')
    list_filter = (
        'is_owner_member',
        'is_paid_member',
        'is_active',
        'is_staff',
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("プロフィール情報", {"fields": ("name",)}),
        ("ログイン情報", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "password1",
                "password2",
                "is_owner_member",
                "is_paid_member",
                "is_staff",
                "is_superuser",
            ),
        }),
    )
