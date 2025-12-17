from django.core.management.base import BaseCommand
from accounts.models import User
from restaurants.models import Company, Restaurant, Category


class Command(BaseCommand):
    help = '各オーナーアカウントにさらに店舗を追加する'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("追加の店舗データ投入")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # 店舗作成
        self.create_more_restaurants()
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS('✅ 完了'))
        self.stdout.write("=" * 70)

    def create_more_restaurants(self):
        """各オーナーアカウントにさらに店舗を追加"""
        self.stdout.write("=" * 70)
        self.stdout.write("店舗追加")
        self.stdout.write("=" * 70)
        
        owners = User.objects.filter(is_owner_member=True).select_related('company')
        
        if not owners.exists():
            self.stdout.write(self.style.WARNING("⚠️  オーナーユーザーが見つかりません"))
            return
        
        self.stdout.write(f"オーナー数: {owners.count()}")
        self.stdout.write("")
        
        # さらに多くの店舗データテンプレート
        all_restaurant_templates = [
            {
                'name': '回転寿司 海鮮丸',
                'description': '新鮮なネタを回転寿司スタイルで気軽に楽しめる寿司店。家族連れに人気です。',
                'zipcode': '460-0001',
                'address': '愛知県名古屋市中区三の丸1-5-3',
                'tel': '052-777-8888',
                'category_name': '寿司',
                'price_min': 1500,
                'price_max': 3000,
            },
            {
                'name': 'カフェレストラン ル・ソレイユ',
                'description': '落ち着いた雰囲気のカフェレストラン。こだわりのコーヒーと洋食メニューが楽しめます。',
                'zipcode': '464-0850',
                'address': '愛知県名古屋市千種区今池1-6-2',
                'tel': '052-888-9999',
                'category_name': '洋食',
                'price_min': 1200,
                'price_max': 2500,
            },
            {
                'name': '焼鳥居酒屋 鶏心',
                'description': '備長炭で丁寧に焼き上げる絶品焼鳥が自慢の居酒屋。地酒との相性も抜群です。',
                'zipcode': '460-0008',
                'address': '愛知県名古屋市中区栄4-2-8',
                'tel': '052-999-0000',
                'category_name': '和食',
                'price_min': 2000,
                'price_max': 4000,
            },
            {
                'name': '四川飯店 龍華',
                'description': '本格的な四川料理専門店。麻婆豆腐と担々麺が絶品です。',
                'zipcode': '450-0002',
                'address': '愛知県名古屋市中村区名駅3-15-1',
                'tel': '052-100-1111',
                'category_name': '中華',
                'price_min': 1800,
                'price_max': 3500,
            },
            {
                'name': 'パスタ工房 マンマミーア',
                'description': '自家製生パスタが自慢のイタリアンレストラン。',
                'zipcode': '460-0011',
                'address': '愛知県名古屋市中区大須2-8-15',
                'tel': '052-200-2222',
                'category_name': 'イタリアン',
                'price_min': 1500,
                'price_max': 3000,
            },
            {
                'name': '炭火焼肉 牛太郎',
                'description': '良質な和牛をリーズナブルに楽しめる焼肉店。',
                'zipcode': '460-0003',
                'address': '愛知県名古屋市中区錦2-12-5',
                'tel': '052-300-3333',
                'category_name': '焼肉',
                'price_min': 3000,
                'price_max': 6000,
            },
            {
                'name': 'フレンチダイニング エトワール',
                'description': 'カジュアルなフレンチレストラン。コースメニューが充実。',
                'zipcode': '464-0075',
                'address': '愛知県名古屋市千種区内山3-18-6',
                'tel': '052-400-4444',
                'category_name': 'フレンチ',
                'price_min': 3500,
                'price_max': 7000,
            },
            {
                'name': 'お寿司処 鮨勘',
                'description': '職人が握る本格寿司。カウンター席で目の前で握られる寿司は格別です。',
                'zipcode': '460-0008',
                'address': '愛知県名古屋市中区栄5-3-12',
                'tel': '052-500-5555',
                'category_name': '寿司',
                'price_min': 5000,
                'price_max': 12000,
            },
            {
                'name': '洋食屋 グリル名古屋',
                'description': '昔懐かしい洋食が味わえるレストラン。ハンバーグとオムライスが人気。',
                'zipcode': '453-0015',
                'address': '愛知県名古屋市中村区椿町6-9',
                'tel': '052-600-6666',
                'category_name': '洋食',
                'price_min': 1000,
                'price_max': 2000,
            },
            {
                'name': '割烹 日本橋',
                'description': '季節の食材を使った会席料理が楽しめる高級和食店。',
                'zipcode': '460-0002',
                'address': '愛知県名古屋市中区丸の内3-7-22',
                'tel': '052-700-7777',
                'category_name': '和食',
                'price_min': 8000,
                'price_max': 15000,
            },
        ]
        
        # 各オーナーに複数店舗を割り当て
        template_idx = 0
        for owner in owners:
            # 各オーナーに3-4店舗追加
            num_restaurants = 3 if template_idx % 2 == 0 else 4
            
            for i in range(num_restaurants):
                if template_idx >= len(all_restaurant_templates):
                    break
                    
                template = all_restaurant_templates[template_idx]
                template_idx += 1
                
                # オーナーの会社に対応するカテゴリーを取得
                category = Category.objects.filter(
                    company=owner.company,
                    name=template['category_name']
                ).first()
                
                if not category:
                    # カテゴリーがない場合は最初のカテゴリーを使用
                    category = Category.objects.filter(company=owner.company).first()
                
                if not category:
                    self.stdout.write(self.style.WARNING(f"⚠️  {owner.company.name}のカテゴリーが見つかりません"))
                    continue
                
                # オーナー固有の店舗名にする
                restaurant_name = f"{template['name']} ({owner.company.name}店)"
                
                # 既存店舗をチェック
                existing = Restaurant.objects.filter(
                    company=owner.company,
                    name=restaurant_name
                ).exists()
                
                if existing:
                    self.stdout.write(f"ℹ️  既存店舗: {restaurant_name}")
                    continue
                
                # 店舗を作成
                restaurant = Restaurant.objects.create(
                    company=owner.company,
                    owner=owner,
                    name=restaurant_name,
                    description=template['description'],
                    zipcode=template['zipcode'],
                    address=template['address'],
                    tel=template['tel'],
                    category=category,
                    price_min=template['price_min'],
                    price_max=template['price_max'],
                    open_time='11:30',
                    close_time='21:30',
                    holiday='水曜日',
                )
                
                self.stdout.write(self.style.SUCCESS(f"✅ 店舗作成: {restaurant_name}"))
                self.stdout.write(f"   オーナー: {owner.name} ({owner.email})")
                self.stdout.write(f"   カテゴリー: {category.name}")
                self.stdout.write("")
