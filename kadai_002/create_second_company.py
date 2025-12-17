#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新しい会社とオーナーユーザーを作成するスクリプト
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
    print("=" * 60)
    print("新しい会社とオーナーユーザーの作成")
    print("=" * 60)
    print()
    
    # 既存の会社数を確認
    existing_count = Company.objects.count()
    print(f"現在の会社数: {existing_count}")
    
    # 新しい会社を作成
    company2 = Company.objects.create(
        name='サムライレストラン株式会社',
        representative='佐藤一郎',
        zipcode='530-0001',
        address='大阪府大阪市北区梅田1-1-1',
        business='飲食店経営'
    )
    print(f"✅ 会社を作成しました: {company2.name}")
    
    # 新しいオーナーユーザーを作成
    owner2 = User.objects.create_user(
        email='sato@samurai-restaurant.com',
        password='password123',
        name='佐藤一郎',
        name_kana='サトウイチロウ',
        zipcode='530-0001',
        address='大阪府大阪市北区梅田1-1-1',
        tel='09087654321',
        is_owner_member=True,
        company=company2
    )
    print(f"✅ オーナーを作成しました: {owner2.email}")
    
    # 会社のオーナーにも設定
    company2.owner = owner2
    company2.save()
    print(f"✅ 会社とオーナーを紐付けました")
    print()
    
    # 作成結果を表示
    print("=" * 60)
    print("【作成された情報】")
    print("=" * 60)
    print(f"会社名: {company2.name}")
    print(f"代表者: {company2.representative}")
    print(f"住所: {company2.address}")
    print()
    print(f"オーナー名: {owner2.name} ({owner2.name_kana})")
    print(f"メールアドレス: {owner2.email}")
    print(f"所属会社: {owner2.company.name}")
    print(f"オーナー権限: {'はい' if owner2.is_owner_member else 'いいえ'}")
    print()
    print("【ログイン情報】")
    print(f"メールアドレス: {owner2.email}")
    print(f"パスワード: password123")
    print("=" * 60)
    print()
    
    # 全体の確認
    all_companies = Company.objects.all()
    all_owners = User.objects.filter(is_owner_member=True)
    
    print("【現在の全会社一覧】")
    for c in all_companies:
        owner_name = c.owner.email if c.owner else "未設定"
        print(f"  - {c.name} (オーナー: {owner_name})")
    
    print()
    print("【現在の全オーナー一覧】")
    for u in all_owners:
        company_name = u.company.name if u.company else "未設定"
        print(f"  - {u.email} ({u.name}) - 所属: {company_name}")
    
    print()
    print("✅ 完了しました！")

if __name__ == '__main__':
    main()
