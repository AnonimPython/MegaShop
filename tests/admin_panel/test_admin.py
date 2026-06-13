from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.catalog.models import Category, Product
from apps.orders.models import Order
from apps.stores.models import Store

User = get_user_model()


class AdminAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='admin123'
        )
        self.admin.totp_secret = 'test'  # 2FA considered configured
        self.admin.save()

        self.user = User.objects.create_user(
            username='user', password='pass'
        )

    def test_dashboard_redirects_anonymous_to_login(self):
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_allows_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_blocks_regular_user(self):
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_product_list_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_panel:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_works_without_email_confirmed(self):
        #* Email is not checked for staff, only 2FA
        #* Email is not checked for staff, only 2FA
        admin2 = User.objects.create_superuser(
            username='admin2', email='admin2@test.com', password='admin123'
        )
        admin2.totp_secret = 'test'
        admin2.email_confirmed = False
        admin2.save()
        self.client.login(username='admin2', password='admin123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)


class AdminCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='admin123'
        )
        self.admin.totp_secret = 'test'
        self.admin.save()
        self.client.login(username='admin', password='admin123')

    def test_create_category(self):
        response = self.client.post(
            reverse('admin_panel:category_create'),
            {'name': 'Laptops', 'slug': 'notebooks'},
        )
        self.assertIn(response.status_code, [200, 302])

    def test_analytics_dashboard(self):
        response = self.client.get(reverse('admin_panel:analytics_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_store_list(self):
        response = self.client.get(reverse('admin_panel:store_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_create_form(self):
        response = self.client.get(reverse('admin_panel:product_create'))
        self.assertEqual(response.status_code, 200)

    def test_csv_export(self):
        response = self.client.get(reverse('admin_panel:product_export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
