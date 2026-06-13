from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.orders.models import Order, OrderItem
from apps.catalog.models import Category, Product

User = get_user_model()


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer', password='pass'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Product', slug='product',
            category=self.category, price=1000, stock=10,
        )

    def test_create_order(self):
        order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Smith',
            email='john@example.com',
            phone='+71234567890',
            address='1 Main St',
            city='London',
            total_cost=2000,
            payment_method='card',
        )
        self.assertEqual(str(order), f'Order #{order.id}')
        self.assertEqual(order.status, 'new')

    def test_order_item_get_cost(self):
        order = Order.objects.create(
            user=self.user,
            first_name='John', last_name='Smith',
            email='john@example.com', phone='+71234567890',
            address='1 Main St', city='London',
            total_cost=1000, payment_method='card',
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            product_price=self.product.price,
            quantity=2,
        )
        self.assertEqual(item.get_cost(), self.product.price * 2)

    def test_order_auto_created_at(self):
        order = Order.objects.create(
            first_name='John', last_name='Smith',
            email='john@example.com', phone='+71234567890',
            address='1 Main St', city='London',
            total_cost=1000, payment_method='cash',
        )
        self.assertIsNotNone(order.created)

    def test_order_status_choices(self):
        order = Order.objects.create(
            first_name='Anna', last_name='Johnson',
            email='anna@example.com', phone='+71111111111',
            address='10 Park Lane', city='Manchester',
            total_cost=5000, payment_method='card_on_delivery',
        )
        self.assertIn(order.status, ['new', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'])
