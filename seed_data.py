
#/ Seed demo data: admin, categories, products, stores, exchange rates, spec fields."""
#/ этот скрипт позволяет запустить миграцию данных в базу данных и создать администратора по умолчанию + создаем заранее нужные категории и товары к ним
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.catalog.models import Category, Product, ExchangeRate, CategorySpecField
from apps.stores.models import Store, StoreStaff, StoreProduct

User = get_user_model()

# ── Admin/ Администратор ──
#* создаем админа/ create admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@megashop.local', 'admin123', email_confirmed=True)
    print('✓ Admin: admin / admin123')
else:
    print('✓ Admin already exists')

# ── Categories/ Категории для первого запуска ──
cats = {
    'laptops':     {'name': 'Laptops',     'icon': 'bi-laptop'},
    'smartphones': {'name': 'Smartphones', 'icon': 'bi-phone'},
    'gaming':      {'name': 'Gaming',      'icon': 'bi-controller'},
    'audio':       {'name': 'Audio',       'icon': 'bi-headphones'},
    'accessories': {'name': 'Accessories', 'icon': 'bi-mouse'},
    'tablets':     {'name': 'Tablets',     'icon': 'bi-tablet'},
    'consoles':    {'name': 'Consoles',    'icon': 'bi-controller'},
}

created_cats = {}
for slug, data in cats.items():
    cat, created = Category.objects.get_or_create(slug=slug, defaults={
        'name': data['name'], 'is_active': True,
    })
    created_cats[slug] = cat
    if created:
        print(f'  ✓ Category: {data["name"]}')

# ── Products/ Продукты для первого запуска ──
products = [
    {
        'name': 'MacBook Pro 16" M4 Max',    
        'slug': 'macbook-pro-16-m4',          
        'cat': 'laptops',     
        'price': 4499, 
        'stock': 15, 
        'specs': {
            "Screen size": '16.2"', 
            "Processor": 'M4 Max', 
            "RAM": '48 GB', 
            "Storage": '1 TB SSD', 
            "GPU": '40-core', 
            "Battery life": '22h', 
            "Weight": '2.14 kg'
        }
    },
    {
        'name': 'ThinkPad X1 Carbon Gen 12', 
        'slug': 'thinkpad-x1-carbon-gen-12',  
        'cat': 'laptops',     
        'price': 3299, 
        'stock': 10, 
        'specs': {
            "Screen size": '14"', 
            "Processor": 'Intel Ultra 7', 
            "RAM": '32 GB',
            "Storage": '512 GB SSD', 
            "GPU": 'Intel Arc', 
            "Battery life": '15h', 
            "Weight": '1.08 kg'
        }
    },
    {
        'name': 'iPhone 16 Pro Max',          
        'slug': 'iphone-16-pro-max',          
        'cat': 'smartphones', 
        'price': 1199, 
        'stock': 50, 
        'specs': {
            "Screen size": '6.9"', 
            "Processor": 'A18 Pro', 
            "RAM": '8 GB', 
            "Storage": '256 GB', 
            "Camera": '48 MP main', 
            "Battery": '4685 mAh'
        }
    },
    {
        'name': 'Samsung Galaxy S25 Ultra',   
        'slug': 'samsung-galaxy-s25-ultra',   
        'cat': 'smartphones', 
        'price': 1299, 
        'stock': 40, 
        'specs': {
            "Screen size": '6.9"', 
            "Processor": 'Snapdragon 8 Elite', "RAM": '12 GB', 
            "Storage": '256 GB', 
            "Camera": '200 MP main', 
            "Battery": '5000 mAh'
        }
    },
    {
        'name': 'Google Pixel 9 Pro XL',      
        'slug': 'google-pixel-9-pro-xl',      
        'cat': 'smartphones', 
        'price': 1099, 
        'stock': 25, 
        'specs': {
            "Screen size": '6.8"', 
            "Processor": 'Tensor G4', 
            "RAM": '16 GB', 
            "Storage": '128 GB', 
            "Camera": '50 MP main', 
            "Battery": '5060 mAh'
        }
    },
    {
        'name': 'PlayStation 5 Pro',          
        'slug': 'ps5-pro',                    
        'cat': 'consoles',    
        'price': 699,  
        'stock': 20, 
        'specs': {
            "GPU": '16.7 TFLOPS RDNA 4', 
            "Storage": '2 TB SSD', 
            "RAM": '16 GB GDDR6', 
            "Ray tracing": True, 
            "Upscaling": 'PSSR AI-driven'
        }
    },
    {
        'name': 'Xbox Series X',              
        'slug': 'xbox-series-x',              
        'cat': 'consoles',    
        'price': 479,  
        'stock': 18, 
        'specs': {
            "GPU": '12 TFLOPS RDNA 2', 
            "Storage": '1 TB SSD', 
            "RAM": '16 GB GDDR6', 
            "Quick Resume": True
        }
    },
    {
        'name': 'Nintendo Switch 2',          
        'slug': 'nintendo-switch-2',          
        'cat': 'gaming',      
        'price': 449,  
        'stock': 30, 
        'specs': {
            "Screen": '8" LCD', 
            "Storage": '256 GB', 
            "Joy-Con": 'Magnetic', 
            "Backward compatible": True
        }
    },
    {
        'name': 'Sony WH-1000XM6',            
        'slug': 'sony-wh-1000xm6',            
        'cat': 'audio',       
        'price': 349,  
        'stock': 35, 
        'specs': {
            "Driver": '30 mm', 
            "Noise cancelling": 'Auto NC Optimizer', 
            "Battery": '40h', 
            "Codec": 'LDAC'
        }
    },
    {
        'name': 'AirPods Pro 3',              
        'slug': 'airpods-pro-3',              
        'cat': 'audio',       
        'price': 249,  
        'stock': 45, 
        'specs': {
            "Driver": 'Custom Apple', 
            "Noise cancelling": 'Adaptive ANC', 
            "Battery": '6h', 
            "Chip": 'H3'
        }
    },
    {
        'name': 'Logitech MX Master 3S',      
        'slug': 'logitech-mx-master-3s',      
        'cat': 'accessories', 
        'price': 99,   
        'stock': 60, 
        'specs': {
            "Sensor": '8000 DPI', 
            "Buttons": '7', 
            "Battery": '70 days',
            "Connection": 'Bluetooth + USB-C'
        }
    },
    {
        'name': 'Samsung Galaxy Tab S10 Ultra',
        'slug': 'samsung-galaxy-tab-s10-ultra',
        'cat': 'tablets',    
        'price': 1199, 
        'stock': 12, 
        'specs': {
            "Screen": '14.6" Dynamic AMOLED', 
            "Processor": 'MediaTek Dimensity 9300+', 
            "RAM": '12 GB', "Storage": '256 GB'
        }
    },
]

for p in products:
    cat = created_cats[p['cat']]
    _, created = Product.objects.get_or_create(
        slug=p['slug'],
        defaults={
            'name': p['name'],
            'category': cat,
            'price': p['price'],
            'stock': p['stock'],
            'specifications': p['specs'],
            'is_available': True,
        },
    )
    if created:
        print(f'  ✓ Product: {p["name"]}')

# ── Spec fields per category/ Поля характеристик категорий ──
spec_defs = {
    'laptops':[
        ('Screen size', 'text'), 
        ('Refresh rate', 'text'), 
        ('Processor', 'text'), 
        ('RAM', 'text'), 
        ('Storage', 'text'), 
        ('GPU', 'text'), 
        ('Battery life', 'text'), 
        ('Weight', 'text'),
    ],
    'smartphones':[
        ('Screen size', 'text'), 
        ('Processor', 'text'), 
        ('RAM', 'text'), 
        ('Storage', 'text'), 
        ('Camera', 'text'), 
        ('Battery', 'text'),
    ],
    'gaming':[
        ('Console type', 'text'), 
        ('GPU', 'text'), 
        ('Storage', 'text'), 
        ('RAM', 'text'), 
        ('Backward compatible', 'boolean'),
    ],
    'audio':[
        ('Driver', 'text'), 
        ('Noise cancelling', 'text'), 
        ('Battery', 'text'), 
        ('Connection', 'text'),
    ],
    'accessories':[
        ('Compatibility', 'text'), 
        ('Connection', 'text'), 
        ('Weight', 'text'),
    ],
    'tablets':[
        ('Screen', 'text'), 
        ('Processor', 'text'), 
        ('RAM', 'text'), 
        ('Storage', 'text'),
    ],
    'consoles':[
        ('GPU', 'text'), 
        ('Storage', 'text'), 
        ('RAM', 'text'),
        ('Ray tracing', 'boolean'), 
        ('Upscaling', 'text'),
    ],
}

for slug, fields in spec_defs.items():
    cat = created_cats.get(slug)
    if not cat:
        continue
    for idx, (name, ftype) in enumerate(fields):
        _, created = CategorySpecField.objects.get_or_create(
            category=cat, field_name=name,
            defaults={'field_type': ftype, 'sort_order': idx},
        )
        if created:
            print(f'  ✓ Spec field: {cat.name} → {name}')

# ── Exchange rates/ Курсы валют ──
for code, rate, symbol in [('EUR', 0.92, '€'), ('GBP', 0.79, '£')]:
    _, created = ExchangeRate.objects.get_or_create(
        currency=code,
        defaults={'rate': rate, 'symbol': symbol, 'is_active': True},
    )
    if created:
        print(f'  [+]Exchange rate: {code} = {rate}')
        print(f'  [+]Валюта: {code} = {rate}')

# ── Stores/ Магазины ──
stores = [
    {
        'name': 'MegaShop London Oxford St',
        'slug': 'london-oxford',
        'city': 'London',
        'address': '200 Oxford Street, London W1D 1NU',
        'phone': '+44 20 7946 0958'
    },
    {
        'name': 'MegaShop Manchester',       
        'slug': 'manchester',    
        'city': 'Manchester', 
        'address': '20 Market Street, Manchester M1 1WR', 
        'phone': '+44 161 234 5678'
    },
    {
        'name': 'MegaShop Birmingham',       
        'slug': 'birmingham',    
        'city': 'Birmingham', 
        'address': '150 High Street, Birmingham B4 7TA', 
        'phone': '+44 121 345 6789'
    },
]

for s in stores:
    store, created = Store.objects.get_or_create(
        slug=s['slug'],
        defaults={
            'name': s['name'],
            'city': s['city'],
            'address': s['address'],
            'phone': s['phone'],
            'is_active': True,
        },
    )
    if created:
        print(f'[+]Store: {store.name}')

print('\n Seed complete. Admin: admin / admin123')
print('   Login at http://localhost:8000/accounts/login/')
print('\n Первые данные созданы. Администратор: admin / admin123')
print('   Перейдите по http://localhost:8000/accounts/login/')
