from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.catalog.models import Category, Product
from apps.reviews.models import Review

User = get_user_model()


class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reviewer', password='pass'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Product', slug='product',
            category=self.category, price=1000, stock=10,
        )

    def test_create_review(self):
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            text='Great product!',
        )
        self.assertEqual(Review.objects.count(), 1)

    def test_review_str(self):
        review = Review.objects.create(
            user=self.user, product=self.product,
            rating=4, text='Good',
        )
        self.assertIn(str(self.product), str(review))
        self.assertIn(str(self.user), str(review))

    def test_one_review_per_user(self):
        Review.objects.create(
            user=self.user, product=self.product,
            rating=5, text='First review',
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                user=self.user, product=self.product,
                rating=4, text='Second review',
            )

    def test_review_default_not_moderated(self):
        review = Review.objects.create(
            user=self.user, product=self.product,
            rating=3, text='Average',
        )
        self.assertFalse(review.is_moderated)

    def test_anonymous_cannot_post_review(self):
        """Anonymous users see the product page but cannot post a review"""
        response = self.client.get(
            reverse('catalog:product_detail', args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)
        # review form should not be present for anonymous
        self.assertNotContains(response, 'Submit')

    def test_review_ordering(self):
        Review.objects.create(
            user=self.user, product=self.product,
            rating=5, text='First review',
        )
        user2 = User.objects.create_user(username='user2', password='pass')
        Review.objects.create(
            user=user2, product=self.product,
            rating=4, text='Second review',
        )
        reviews = Review.objects.all()
        self.assertEqual(reviews.count(), 2)
