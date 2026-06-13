from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product


class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Product',
            slug='tovar',
            category=self.category,
            price=1000,
            stock=10,
        )

    def test_add_to_cart(self):
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 2, 'update': False},
        )
        self.assertEqual(response.status_code, 302)

    def test_cart_detail(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)

    def test_remove_from_cart(self):
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'update': False},
        )
        response = self.client.post(
            reverse('cart:cart_remove', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_cart_context_processor(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertIn('cart', response.context)
