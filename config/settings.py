import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-megashop-dev-key-change-in-production-2024')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*').split(',')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.forms',

    'apps.accounts',
    'apps.catalog',
    'apps.cart',
    'apps.orders',
    'apps.reviews',
    'apps.stores',
    'apps.analytics',
    'apps.admin_panel',
    'apps.geo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.geo.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart',
                'apps.stores.context_processors.stores',
                'apps.catalog.context_processors.exchange_rates',
                'apps.geo.context_processors.geo_location',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='megashop'),
        'USER': config('DB_USER', default='megashop_user'),
        'PASSWORD': config('DB_PASSWORD', default='megashop_pass'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'catalog:product_list'
LOGOUT_REDIRECT_URL = 'catalog:product_list'

# Защита от межсайтовой подделки запросов / CSRF trusted origins
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
).split(',')

# Безопасность / Security: HTTPS-only cookies in production
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LANGUAGE_CODE = 'en-GB'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SITE_ID = 1

#! Храним CSRF-токен в сессии / Store CSRF token in session (more reliable with Redis cache)
CSRF_USE_SESSIONS = True

# OTP (Google Authenticator) настройки / Settings
OTP_TOTP_ISSUER = 'MegaShop'

# Время жизни сессии / Session lifetime — "remember me" 30 days
SESSION_COOKIE_AGE_REMEMBER = 60 * 60 * 24 * 30  # 30 days
SESSION_COOKIE_AGE_DEFAULT = 60 * 60 * 24 * 7    # 7 days

# Session expiry on browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

#? Loguru: перехватывает стандартное логирование Django / Replaces Django's default logging
#! Удаляем стандартные Django-логгеры / Remove default Django loggers to avoid duplicates
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'intercept': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['intercept'],
        'level': 'DEBUG',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CART_SESSION_ID = 'cart'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='amqp://megashop:megashop_pass@localhost:5672//')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

CLICKHOUSE_HOST = config('CLICKHOUSE_HOST', default='localhost')
CLICKHOUSE_PORT = config('CLICKHOUSE_PORT', default='9000')
CLICKHOUSE_DB = config('CLICKHOUSE_DB', default='megashop')
CLICKHOUSE_USER = config('CLICKHOUSE_USER', default='megashop')
CLICKHOUSE_PASSWORD = config('CLICKHOUSE_PASSWORD', default='megashop_pass')

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.mail.ru')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@megashop.ru')
