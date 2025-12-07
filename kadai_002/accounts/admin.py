from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # 一覧画面の表示設定
    list_display = ('email', 'name', 'is_owner_member', 'is_paid_member', 'is_staff', 'is_active') # is_activeを追加して状態を見える化
    ordering = ('email',)
    search_fields = ('email', 'name')
    list_filter = (
        'is_owner_member',
        'is_paid_member',
        'is_active',
        'is_staff',
    )

    # 【修正】編集画面の構成
    # デフォルトの削除ボタンは画面左下に自動で表示されるけん、ここで設定する必要はないで
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("プロフィール情報", {"fields": ("name", "tel", "zipcode", "address")}), # 住所なども見れた方がええかも
        ("権限・状態", {"fields": ("is_active", "is_staff", "is_superuser", "is_owner_member", "is_paid_member")}), # 【重要】ここを追加
        ("ログイン情報", {"fields": ("last_login", "date_joined")}),
    )

    # 新規作成時の設定（そのままでOK）
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
                "is_active", # 新規作成時にも有効/無効を選べると便利
            ),
        }),
    )

    # 【追加】アクションの追加
    actions = ['delete_selected_users', 'deactivate_users']

    # デフォルトの削除アクション（物理削除）の挙動を明示的に書く場合（通常は不要だがカスタム用に）
    def delete_selected_users(self, request, queryset):
        # ここで削除前のチェックなどを入れることも可能
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} 件のユーザーを完全に削除しました。")
    delete_selected_users.short_description = "選択されたユーザーを完全に削除する"

    # 【推奨】論理削除用のアクション（データを残してログインできなくする）
    def deactivate_users(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"{rows_updated} 件のユーザーを無効化（凍結）しました。")
    deactivate_users.short_description = "選択されたユーザーを無効化する（論理削除）"