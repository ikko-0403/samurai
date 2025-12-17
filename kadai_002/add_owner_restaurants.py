#!/usr/bin/env python
import os
import sys
import django

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()


from accounts.models import User
from restaurants.models import Company, Restaurant, Category
from django.utils import timezone

def create_categories():
    """カテゴリーを7個追加"""
    categories_data = [
        '和食',
        '洋食',
        'イタリアン',
        'フレンチ',
        '中華',
        '焼肉',
        '寿司',
    ]
    
    print("=" * 70)
    print("カテゴリー追加")
    print("=" * 70)
    
    created_categories = []
    for category_name in categories_data:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'{category_name}のレストラン'}
        )
        if created:
            print(f"✅ カテゴリー作成: {category_name}")
        else:
            print(f"ℹ️  既存カテゴリー: {category_name}")
        created_categories.append(category)
    
    print()
    return created_categories


def create_restaurants_for_owners(categories):
    """各オーナーアカウントに店舗を追加"""
    print("=" * 70)
    print("店舗追加")
    print("=" * 70)
    
    owners = User.objects.filter(is_owner_member=True).select_related('company')
    
    if not owners.exists():
        print("⚠️  オーナーユーザーが見つかりません")
        return
    
    print(f"オーナー数: {owners.count()}\n")
    
    # 各オーナー用の店舗データ
    restaurant_templates = [
        {
            'name': '名古屋めし 本店',
            'description': '伝統的な名古屋料理を提供する老舗レストラン。味噌カツ、ひつまぶし、手羽先など、名古屋の名物料理を楽しめます。',
            'postal_code': '460-0008',
            'address': '愛知県名古屋市中区栄3-1-1',
            'phone_number': '052-111-2222',
            'category_index': 0,  # 和食
            'price_range': 3000,
        },
        {
            'name': 'トラットリア ナゴヤ',
            'description': '本格的なイタリア料理をカジュアルに楽しめるレストラン。新鮮なパスタと窯焼きピッツァが自慢です。',
            'postal_code': '460-0003',
            'address': '愛知県名古屋市中区錦3-2-15',
            'phone_number': '052-222-3333',
            'category_index': 2,  # イタリアン
            'price_range': 2500,
        },
        {
            'name': 'ビストロ サクラ',
            'description': 'フランスの伝統料理と地元の食材が出会う、モダンなビストロ。季節のコース料理をご堪能ください。',
            'postal_code': '460-0011',
            'address': '愛知県名古屋市中区大須3-5-8',
            'phone_number': '052-333-4444',
            'category_index': 3,  # フレンチ
            'price_range': 5000,
        },
        {
            'name': '中華楼 龍',
            'description': '本場の四川料理と広東料理が味わえる中華料理店。辛さと旨味が絶妙なバランスです。',
            'postal_code': '453-0015',
            'address': '愛知県名古屋市中村区椿町1-16',
            'phone_number': '052-444-5555',
            'category_index': 4,  # 中華
            'price_range': 3500,
        },
        {
            'name': '焼肉 侍',
            'description': '最高級A5ランクの和牛を使用した焼肉専門店。落ち着いた個室で極上の焼肉体験を。',
            'postal_code': '460-0002',
            'address': '愛知県名古屋市中区丸の内2-10-5',
            'phone_number': '052-555-6666',
            'category_index': 5,  # 焼肉
            'price_range': 6000,
        },
    ]
    
    for idx, owner in enumerate(owners):
        # 店舗データをローテーション
        template = restaurant_templates[idx % len(restaurant_templates)]
        category = categories[template['category_index'] % len(categories)]
        
        # オーナー固有の店舗名にする
        restaurant_name = f"{template['name']} ({owner.company.name if owner.company else owner.name}店)"
        
        # 既存店舗をチェック
        existing = Restaurant.objects.filter(
            company=owner.company,
            name=restaurant_name
        ).exists()
        
        if existing:
            print(f"ℹ️  既存店舗: {restaurant_name} (オーナー: {owner.name})")
            continue
        
        # 店舗を作成
        restaurant = Restaurant.objects.create(
            company=owner.company,
            name=restaurant_name,
            description=template['description'],
            postal_code=template['postal_code'],
            address=template['address'],
            phone_number=template['phone_number'],
            category=category,
            price_range=template['price_range'],
            opening_time='11:00',
            closing_time='22:00',
            capacity=50,
        )
        
        print(f"✅ 店舗作成: {restaurant_name}")
        print(f"   オーナー: {owner.name} ({owner.email})")
        print(f"   会社: {owner.company.name if owner.company else '未設定'}")
        print(f"   カテゴリー: {category.name}")
        print()


def main():
    print("\n")
    print("=" * 70)
    print("データ投入スクリプト")
    print("=" * 70)
    print()
    
    # カテゴリー作成
    categories = create_categories()
    
    # 店舗作成
    create_restaurants_for_owners(categories)
    
    print("=" * 70)
    print("✅ 完了")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
