from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.stores.models import Store, StoreStaff, StoreProduct
from apps.catalog.models import Category, Product

User = get_user_model()


class StoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='manager', password='pass')
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Product', slug='product',
            category=self.category, price=1000, stock=10,
        )

    def test_create_store(self):
        store = Store.objects.create(
            name='MegaShop City',
            address='1 Tverskaya St',
            city='Moscow',
        )
        self.assertEqual(str(store), 'MegaShop City (Moscow)')

    def test_store_staff_assignment(self):
        store = Store.objects.create(
            name='MegaShop City', address='1 Tverskaya St', city='Moscow',
        )
        staff = StoreStaff.objects.create(
            store=store, user=self.user, role='manager',
        )
        self.assertIn(staff, store.staff.all())

    def test_store_product_stock(self):
        store = Store.objects.create(
            name='MegaShop City', address='1 Tverskaya St', city='Moscow',
        )
        sp = StoreProduct.objects.create(
            store=store, product=self.product, stock=5,
        )
        self.assertEqual(sp.stock, 5)
        self.assertEqual(
            str(sp), f'{self.product.name} — {store.name}: 5 pcs.'
        )

    def test_unique_store_product(self):
        store = Store.objects.create(
            name='MegaShop City', address='1 Tverskaya St', city='Moscow',
        )
        StoreProduct.objects.create(store=store, product=self.product)
        with self.assertRaises(Exception):
            StoreProduct.objects.create(store=store, product=self.product)
