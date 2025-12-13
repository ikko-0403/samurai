import os
import sys
import django

sys.path.insert(0, '/Users/ikkoikko/Desktop/samurai-1/kadai_002')
os.environ['DJANGO_SETTINGS_MODULE'] = 'base.settings'
django.setup()

from accounts.models import User
from restaurants.models import Company

print('=' * 60)
print('データベース確認')
print('=' * 60)

companies = Company.objects.all()
owners = User.objects.filter(is_owner_member=True)

print(f'\n会社数: {companies.count()}')
print(f'オーナー数: {owners.count()}\n')

print('【会社一覧】')
for c in companies:
    owner_email = c.owner.email if c.owner else '未設定'
    print(f'  {c.id}. {c.name} - オーナー: {owner_email}')

print('\n【オーナー一覧】')
for u in owners:
    company_name = u.company.name if u.company else '未設定'
    print(f'  {u.id}. {u.email} ({u.name}) - 所属: {company_name}')

print('\n' + '=' * 60)
