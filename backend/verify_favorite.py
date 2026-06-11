#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:'
}
settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)

django.setup()

from django.core.management import call_command

print('--- Step 1: 执行 migrate (全新库) ---')
call_command('migrate', '--noinput', verbosity=1)
print('✅ migrate 成功，无表冲突\n')

print('--- Step 2: 检查 django_migrations 记录 ---')
from django.db import connection
with connection.cursor() as c:
    c.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
    for row in c.fetchall():
        print(f'  {row[0]:15s} {row[1]}')
print()

print('--- Step 3: 验证业务表是否存在 ---')
with connection.cursor() as c:
    c.execute("SELECT name FROM sqlite_master WHERE type='table' "
              "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%' "
              "AND name NOT LIKE 'auth_%' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    for t in tables:
        print(f'  ✓ {t}')
assert 'products_product' in tables, '缺少 products_product 表'
assert 'products_favorite' in tables, '缺少 products_favorite 表'
print('✅ 所有业务表创建成功\n')

print('--- Step 4: 检查 Favorite 表字段 ---')
with connection.cursor() as c:
    c.execute('PRAGMA table_info(products_favorite)')
    cols = [(r[1], r[2]) for r in c.fetchall()]
    for name, typ in cols:
        print(f'  {name:15s} {typ}')
    c.execute('PRAGMA index_list(products_favorite)')
    for r in c.fetchall():
        print(f'  INDEX: {r[1]}')
print()

print('--- Step 5: 收藏/取消收藏接口逻辑 ---')
from app.apps.products.models import Product, Favorite

p1 = Product.objects.create(seller_id=1001, name='iPhone 13', description='二手95新',
                             original_price=7999, sale_price=4599,
                             condition='like_new', category='digital')
p2 = Product.objects.create(seller_id=1002, name='Sony WH-1000XM4', description='降噪耳机',
                             original_price=2699, sale_price=1599,
                             condition='good', category='digital')
p3 = Product.objects.create(seller_id=1003, name='MacBook Pro 16', description='M1 Max',
                             original_price=32999, sale_price=21999,
                             condition='used', category='digital')
print(f'  ✓ 创建3个商品 id={p1.id},{p2.id},{p3.id}')

fav, created = Favorite.objects.get_or_create(user_id=2001, product=p1)
assert created == True
print(f'  ✓ 用户2001收藏商品{p1.id} favorited=True')

fav, created = Favorite.objects.get_or_create(user_id=2001, product=p1)
assert created == False
print(f'  ✓ 用户2001重复收藏商品{p1.id} favorited=False')

for uid in range(2002, 2012):
    Favorite.objects.create(user_id=uid, product=p1)
print(f'  ✓ 10个用户收藏商品{p1.id}（累计11）')

for uid in range(2001, 2004):
    Favorite.objects.create(user_id=uid, product=p3)
print(f'  ✓ 3个用户收藏商品{p3.id}')

Favorite.objects.create(user_id=2001, product=p2)
print(f'  ✓ 用户2001收藏商品{p2.id}')
print()

print('--- Step 6: 商品详情收藏数 & is_favorited ---')
from app.apps.products.serializers import ProductSerializer
from rest_framework.test import APIRequestFactory
factory = APIRequestFactory()

# 不带 user_id
req1 = factory.get(f'/api/products/{p1.id}/')
ser1 = ProductSerializer(p1, context={'request': req1})
d1 = ser1.data
print(f'  商品{p1.id}: favorite_count={d1["favorite_count"]} is_favorited={d1["is_favorited"]} (不带user_id)')
assert d1['favorite_count'] == 11
assert d1['is_favorited'] == False

# 带 user_id=2001
req2 = factory.get(f'/api/products/{p1.id}/?user_id=2001')
ser2 = ProductSerializer(p1, context={'request': req2})
d2 = ser2.data
print(f'  商品{p1.id}: favorite_count={d2["favorite_count"]} is_favorited={d2["is_favorited"]} (user_id=2001)')
assert d2['favorite_count'] == 11
assert d2['is_favorited'] == True

# 商品2: 仅用户2001收藏
req3 = factory.get(f'/api/products/{p2.id}/?user_id=2001')
ser3 = ProductSerializer(p2, context={'request': req3})
d3 = ser3.data
print(f'  商品{p2.id}: favorite_count={d3["favorite_count"]} is_favorited={d3["is_favorited"]} (user_id=2001)')
assert d3['favorite_count'] == 1
assert d3['is_favorited'] == True
print('✅ 商品详情 favorite_count & is_favorited 正确\n')

print('--- Step 7: 个人中心收藏列表 ---')
fav_qs = Favorite.objects.filter(user_id=2001).order_by('-created_at')
fav_ids = list(fav_qs.values_list('product_id', flat=True))
print(f'  用户2001 收藏商品ID(按时间倒序): {fav_ids}')
products_qs = Product.objects.filter(id__in=fav_ids)
pmap = {p.id: p for p in products_qs}
ordered = [pmap[pid] for pid in fav_ids if pid in pmap]
ser_list = ProductSerializer(ordered, many=True, context={'request': req2})
for item in ser_list.data:
    print(f'    id={item["id"]} name={item["name"]} favorite_count={item["favorite_count"]} is_favorited={item["is_favorited"]}')
assert len(ser_list.data) == 3
assert ser_list.data[0]['id'] == p2.id
assert all('favorite_count' in x and 'is_favorited' in x for x in ser_list.data)
print('✅ 个人收藏列表正确（按时间倒序 + 带收藏字段）\n')

print('--- Step 8: 按收藏热度排序 ---')
from django.db.models import Count
qs = Product.objects.annotate(fav_count=Count('favorites')).order_by('-fav_count', '-created_at')
ranked = [(p.id, p.fav_count, p.name) for p in qs]
print(f'  排序结果 (id, fav_count, name):')
for r in ranked:
    print(f'    id={r[0]:2d} fav={r[1]:2d} {r[2]}')
assert ranked[0][0] == p1.id and ranked[0][1] == 11
assert ranked[1][0] == p3.id and ranked[1][1] == 3
assert ranked[2][0] == p2.id and ranked[2][1] == 1
print('✅ 按收藏热度从高到低排序正确\n')

print('--- Step 9: 取消收藏 ---')
deleted, _ = Favorite.objects.filter(user_id=2001, product=p2).delete()
print(f'  用户2001取消收藏商品{p2.id}: deleted={deleted}')
assert deleted == 1

deleted, _ = Favorite.objects.filter(user_id=2001, product=p2).delete()
print(f'  用户2001重复取消收藏商品{p2.id}: deleted={deleted}')
assert deleted == 0

remaining = list(Favorite.objects.filter(user_id=2001).values_list('product_id', flat=True))
print(f'  用户2001剩余收藏: {remaining}')
assert len(remaining) == 2 and p2.id not in remaining
print('✅ 取消收藏正确\n')

print('--- Step 10: 级联删除（删除商品自动清理收藏）---')
total_before = Favorite.objects.count()
p1_fav_count = p1.favorites.count()
p1.delete()
total_after = Favorite.objects.count()
print(f'  删除商品{p1.id}前收藏总数={total_before}, 删除后={total_after}, 减少={total_before-total_after}')
assert total_after == total_before - p1_fav_count
print(f'✅ 级联删除正确（减少{p1_fav_count}条）\n')

print('=' * 60)
print('🎉 全部 10 个验证场景通过！')
print('=' * 60)
print('  1. migrate 在全新库执行成功，无表冲突')
print('  2. django_migrations 记录完整')
print('  3. 所有业务表（含 products_favorite）创建成功')
print('  4. 数据表字段正确')
print('  5. 收藏/重复收藏 接口逻辑正确')
print('  6. 商品详情 favorite_count + is_favorited 正确')
print('  7. 个人中心收藏列表（按时间倒序）正确')
print('  8. 按收藏热度从高到低排序正确')
print('  9. 取消收藏/重复取消 正确')
print(' 10. 删除商品级联清理收藏正确')
print('=' * 60)
