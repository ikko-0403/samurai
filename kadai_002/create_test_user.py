#!/usr/bin/env python
"""一般ユーザー（無料会員）のテストアカウントを作成"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from accounts.models import User

# 既存のテストユーザーを確認
test_email = "user@test.com"
existing_user = User.objects.filter(email=test_email).first()

if existing_user:
    print(f"✓ 一般ユーザーが既に存在します:")
    print(f"  メールアドレス: {existing_user.email}")
    print(f"  名前: {existing_user.name}")
    print(f"  有料会員: {'はい' if existing_user.is_paid_member else 'いいえ'}")
    print(f"  オーナー: {'はい' if existing_user.is_owner_member else 'いいえ'}")
    
    # パスワードをリセット
    existing_user.set_password('password123')
    existing_user.save()
    print(f"\n  パスワードを 'password123' にリセットしました")
else:
    # 新しい一般ユーザーを作成
    user = User.objects.create_user(
        email=test_email,
        password='password123',
        name='テストユーザー',
        name_kana='テストユーザー',
        zipcode='123-4567',
        address='東京都渋谷区',
        tel='09012345678',
        is_paid_member=False,
        is_owner_member=False
    )
    print(f"✓ 新しい一般ユーザーを作成しました:")
    print(f"  メールアドレス: {user.email}")
    print(f"  名前: {user.name}")
    print(f"  パスワード: password123")

print("\n" + "="*70)
print("ログイン情報")
print("="*70)
print(f"メールアドレス: {test_email}")
print(f"パスワード: password123")
print("="*70)
