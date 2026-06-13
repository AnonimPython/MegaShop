from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass'
        )
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.email_confirmed)
        self.assertEqual(str(user), 'testuser')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='pass'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_get_totp_secret_generates(self):
        user = User.objects.create_user(username='testuser', password='pass')
        secret = user.get_totp_secret()
        self.assertTrue(len(secret) > 10)

    def test_get_totp_secret_persists(self):
        user = User.objects.create_user(username='testuser', password='pass')
        first = user.get_totp_secret()
        second = user.get_totp_secret()
        self.assertEqual(first, second)

    def test_str_uses_username_when_no_full_name(self):
        user = User.objects.create_user(username='testuser', password='pass')
        # get_full_name returns '' by default (Django AbstractUser)
        # __str__ falls back to username
        self.assertEqual(str(user), 'testuser')

    def test_is_expansion_manager_default(self):
        user = User.objects.create_user(username='testuser', password='pass')
        self.assertFalse(user.is_expansion_manager)

    def test_is_admin_property(self):
        admin = User.objects.create_superuser(username='admin', password='pass')
        user = User.objects.create_user(username='user', password='pass')
        self.assertTrue(admin.is_admin)
        self.assertFalse(user.is_admin)
