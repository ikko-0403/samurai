import random
from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, Table


class Command(BaseCommand):
    help = '既存の全てのRestaurantに対してランダムにTableデータを生成します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='既存のテーブルデータを削除してから生成する',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = Table.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'既存のテーブルデータを{deleted_count}件削除しました。')
            )

        restaurants = Restaurant.objects.all()
        
        if not restaurants.exists():
            self.stdout.write(
                self.style.ERROR('店舗データが見つかりません。先に店舗データを作成してください。')
            )
            return

        total_tables_created = 0
        
        for restaurant in restaurants:
            # 既存の席データがある場合はスキップ
            if restaurant.tables.exists() and not options['clear']:
                self.stdout.write(
                    self.style.WARNING(
                        f'スキップ: {restaurant.name} には既にテーブルデータが存在します。'
                    )
                )
                continue
            
            # ランダムに座席を生成
            # 2人席: 2-5個
            # 4人席: 2-4個
            # 8人席: 0-2個
            
            num_2_seat = random.randint(2, 5)
            num_4_seat = random.randint(2, 4)
            num_8_seat = random.randint(0, 2)
            
            tables_to_create = []
            
            # 2人席
            for _ in range(num_2_seat):
                tables_to_create.append(
                    Table(restaurant=restaurant, capacity=2)
                )
            
            # 4人席
            for _ in range(num_4_seat):
                tables_to_create.append(
                    Table(restaurant=restaurant, capacity=4)
                )
            
            # 8人席
            for _ in range(num_8_seat):
                tables_to_create.append(
                    Table(restaurant=restaurant, capacity=8)
                )
            
            # 一括作成
            Table.objects.bulk_create(tables_to_create)
            
            total_created = len(tables_to_create)
            total_tables_created += total_created
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {restaurant.name}: {num_2_seat}x2名席, {num_4_seat}x4名席, {num_8_seat}x8名席 '
                    f'(合計{total_created}席) を作成しました。'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完了: 合計{total_tables_created}個のテーブルを{restaurants.count()}店舗に作成しました。'
            )
        )
