from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.catalog.models import Category, Product
from apps.orders.models import Order

User = get_user_model()


class OrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer', email='buyer@test.com', password='pass'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Product', slug='product',
            category=self.category, price=1000, stock=10,
        )

    def _add_to_cart(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1, 'price': '1000.00'}}
        session.save()

    def test_order_create_get_with_cart(self):
        self.client.login(username='buyer', password='pass')
        self._add_to_cart()
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 200)

    def test_order_create_redirects_without_cart(self):
        self.client.login(username='buyer', password='pass')
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 302)

    def test_order_list_requires_login(self):
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 302)

    def test_order_list_shows_user_orders(self):
        self.client.login(username='buyer', password='pass')
        Order.objects.create(
            user=self.user,
            first_name='John', last_name='Smith',
            email='buyer@test.com', phone='+71234567890',
            address='1 Main St', city='London',
            total_cost=1000, payment_method='card',
        )
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1,000.00')

    def test_order_detail_view(self):
        self.client.login(username='buyer', password='pass')
        order = Order.objects.create(
            user=self.user,
            first_name='John', last_name='Smith',
            email='buyer@test.com', phone='+71234567890',
            address='1 Main St', city='London',
            total_cost=1000, payment_method='card',
        )
        response = self.client.get(reverse('orders:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1,000.00')
