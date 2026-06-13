from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_register_success(self):
        response = self.client.post(reverse('accounts:register'), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_with_username(self):
        User.objects.create_user(username='testuser', password='12345')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_email(self):
        User.objects.create_user(
            username='testuser', email='test@example.com', password='12345'
        )
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_fail_wrong_password(self):
        User.objects.create_user(username='testuser', password='12345')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email/login or password.')

    def test_logout_requires_post(self):
        # default LogoutView only accepts POST
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 405)

    def test_logout_success(self):
        User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
