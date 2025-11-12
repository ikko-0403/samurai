from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'name', 'is_paid_member', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'name')
    list_filter = (
        'is_paid_member',
        'is_active',
        'is_staff',
    )
