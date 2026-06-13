from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product


class CatalogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Laptops', slug='notebooks')
        self.product = Product.objects.create(
            name='MacBook Pro',
            slug='macbook-pro',
            category=self.category,
            price=179900,
            stock=10,
        )

    def test_product_list_status(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_shows_products(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, 'MacBook Pro')

    def test_product_detail_status(self):
        response = self.client.get(
            reverse('catalog:product_detail', args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_product_detail_404(self):
        response = self.client.get(
            reverse('catalog:product_detail', args=['non-existent'])
        )
        self.assertEqual(response.status_code, 404)

    def test_category_filter(self):
        response = self.client.get(
            reverse('catalog:product_list'),
            {'category': self.category.slug},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MacBook Pro')

    def test_search(self):
        response = self.client.get(
            reverse('catalog:product_list'),
            {'q': 'MacBook'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MacBook Pro')

    def test_search_no_results(self):
        response = self.client.get(
            reverse('catalog:product_list'),
            {'q': 'zzzzzznothing'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'MacBook Pro')
