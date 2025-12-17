#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
オーナーユーザーのログイン情報を表示するスクリプト
"""
import os
import sys
import django

# Djangoの設定を読み込み
sys.path.insert(0, '/Users/ikkoikko/Desktop/samurai-1/kadai_002')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from accounts.models import User
from restaurants.models import Company

def main():
    print("=" * 70)
    print("オーナーユーザー ログイン情報")
    print("=" * 70)
    print()
    
    owners = User.objects.filter(is_owner_member=True).select_related('company')
    
    if not owners.exists():
        print("⚠️  オーナーユーザーが見つかりません")
        return
    
    print(f"登録されているオーナー数: {owners.count()}\n")
    
    # 既知のログイン情報（スクリプトから判明したもの）
    known_passwords = {
        'sato@samurai-restaurant.com': 'password123',
        # 他のユーザーは不明
    }
    
    for idx, owner in enumerate(owners, 1):
        print(f"【オーナー {idx}】")
        print(f"  名前: {owner.name}")
        print(f"  メールアドレス: {owner.email}")
        print(f"  所属会社: {owner.company.name if owner.company else '未設定'}")
        
        # パスワードが既知の場合のみ表示
        if owner.email in known_passwords:
            print(f"  パスワード: {known_passwords[owner.email]}")
        else:
            print(f"  パスワード: （不明 - データベースで暗号化されています）")
        
        print()
    
    print("=" * 70)
    print("💡 ヒント:")
    print("  - 未知のパスワードは、Djangoの管理画面やパスワードリセット機能で")
    print("    変更できます")
    print("  - または、新しいテストユーザーを作成することもできます")
    print("=" * 70)

if __name__ == '__main__':
    main()
