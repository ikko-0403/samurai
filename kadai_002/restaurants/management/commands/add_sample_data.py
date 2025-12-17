from django.core.management.base import BaseCommand
from accounts.models import User
from restaurants.models import Company, Restaurant, Category


class Command(BaseCommand):
    help = 'オーナーアカウントに店舗を追加し、カテゴリーを追加する'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("データ投入開始")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # カテゴリー作成
        categories = self.create_categories()
        
        # 店舗作成
        self.create_restaurants_for_owners(categories)
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS('✅ 完了'))
        self.stdout.write("=" * 70)

    def create_categories(self):
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
        
        self.stdout.write("=" * 70)
        self.stdout.write("カテゴリー追加")
        self.stdout.write("=" * 70)
        
        # 各会社用のカテゴリーを作成
        companies = Company.objects.all()
        if not companies.exists():
            self.stdout.write(self.style.WARNING("⚠️  会社が見つかりません"))
            return []
        
        created_categories = []
        for company in companies:
            for category_name in categories_data:
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    company=company
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ カテゴリー作成: {category_name} ({company.name})"))
                    created_categories.append(category)
                else:
                    if category not in created_categories:
                        created_categories.append(category)
        
        self.stdout.write("")
        return created_categories

    def create_restaurants_for_owners(self, categories):
        """各オーナーアカウントに店舗を追加"""
        self.stdout.write("=" * 70)
        self.stdout.write("店舗追加")
        self.stdout.write("=" * 70)
        
        owners = User.objects.filter(is_owner_member=True).select_related('company')
        
        if not owners.exists():
            self.stdout.write(self.style.WARNING("⚠️  オーナーユーザーが見つかりません"))
            return
        
        self.stdout.write(f"オーナー数: {owners.count()}")
        self.stdout.write("")
        
        # 各オーナー用の店舗データ
        restaurant_templates = [
            {
                'name': '名古屋めし 本店',
                'description': '伝統的な名古屋料理を提供する老舗レストラン。味噌カツ、ひつまぶし、手羽先など、名古屋の名物料理を楽しめます。',
                'zipcode': '460-0008',
                'address': '愛知県名古屋市中区栄3-1-1',
                'tel': '052-111-2222',
                'category_name': '和食',
                'price_min': 2000,
                'price_max': 4000,
            },
            {
                'name': 'トラットリア ナゴヤ',
                'description': '本格的なイタリア料理をカジュアルに楽しめるレストラン。新鮮なパスタと窯焼きピッツァが自慢です。',
                'zipcode': '460-0003',
                'address': '愛知県名古屋市中区錦3-2-15',
                'tel': '052-222-3333',
                'category_name': 'イタリアン',
                'price_min': 1500,
                'price_max': 3500,
            },
            {
                'name': 'ビストロ サクラ',
                'description': 'フランスの伝統料理と地元の食材が出会う、モダンなビストロ。季節のコース料理をご堪能ください。',
                'zipcode': '460-0011',
                'address': '愛知県名古屋市中区大須3-5-8',
                'tel': '052-333-4444',
                'category_name': 'フレンチ',
                'price_min': 4000,
                'price_max': 8000,
            },
            {
                'name': '中華楼 龍',
                'description': '本場の四川料理と広東料理が味わえる中華料理店。辛さと旨味が絶妙なバランスです。',
                'zipcode': '453-0015',
                'address': '愛知県名古屋市中村区椿町1-16',
                'tel': '052-444-5555',
                'category_name': '中華',
                'price_min': 2500,
                'price_max': 5000,
            },
            {
                'name': '焼肉 侍',
                'description': '最高級A5ランクの和牛を使用した焼肉専門店。落ち着いた個室で極上の焼肉体験を。',
                'zipcode': '460-0002',
                'address': '愛知県名古屋市中区丸の内2-10-5',
                'tel': '052-555-6666',
                'category_name': '焼肉',
                'price_min': 5000,
                'price_max': 10000,
            },
        ]
        
        for idx, owner in enumerate(owners):
            # 店舗データをローテーション
            template = restaurant_templates[idx % len(restaurant_templates)]
            
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
            restaurant_name = f"{template['name']} ({owner.company.name if owner.company else owner.name}店)"
            
            # 既存店舗をチェック
            existing = Restaurant.objects.filter(
                company=owner.company,
                name=restaurant_name
            ).exists()
            
            if existing:
                self.stdout.write(f"ℹ️  既存店舗: {restaurant_name} (オーナー: {owner.name})")
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
                open_time='11:00',
                close_time='22:00',
                holiday='月曜日',
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ 店舗作成: {restaurant_name}"))
            self.stdout.write(f"   オーナー: {owner.name} ({owner.email})")
            self.stdout.write(f"   会社: {owner.company.name if owner.company else '未設定'}")
            self.stdout.write(f"   カテゴリー: {category.name}")
            self.stdout.write("")

