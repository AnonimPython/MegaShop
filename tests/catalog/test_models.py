from django.test import TestCase
from apps.catalog.models import Category, Product


class CategoryModelTests(TestCase):
    def test_create_category(self):
        cat = Category.objects.create(
            name='Laptops', slug='notebooks'
        )
        self.assertEqual(str(cat), 'Laptops')

    def test_category_children(self):
        parent = Category.objects.create(name='Electronics', slug='electronics')
        child = Category.objects.create(
            name='Laptops', slug='notebooks', parent=parent
        )
        self.assertIn(child, parent.children.all())


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Laptops', slug='notebooks'
        )

    def test_create_product(self):
        product = Product.objects.create(
            name='MacBook Pro',
            slug='macbook-pro',
            category=self.category,
            price=199900,
            stock=10,
        )
        self.assertEqual(str(product), 'MacBook Pro')
        self.assertEqual(product.discount_percent, 0)
        self.assertTrue(product.is_available)

    def test_discount_percent_calculated(self):
        product = Product.objects.create(
            name='MacBook Pro',
            slug='macbook-pro',
            category=self.category,
            price=179900,
            old_price=199900,
            stock=10,
        )
        self.assertEqual(product.discount_percent, 10)

    def test_discount_percent_no_old_price(self):
        product = Product.objects.create(
            name='MacBook Pro', slug='macbook-pro',
            category=self.category, price=179900, stock=10,
        )
        self.assertEqual(product.discount_percent, 0)

    def test_product_str(self):
        product = Product.objects.create(
            name='MacBook Pro', slug='macbook-pro',
            category=self.category, price=179900, stock=10,
        )
        self.assertEqual(str(product), 'MacBook Pro')
