#? Настройки для тестов — SQLite вместо PostgreSQL
#? Test settings — SQLite instead of PostgreSQL
from config.settings import *  # noqa

#! Переключаем БД на SQLite в памяти (не нужен PostgreSQL)
#! Switch to in-memory SQLite (no PostgreSQL needed)
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

#* Отключаем Redis/ClickHouse для тестов
#* Disable Redis/ClickHouse for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CLICKHOUSE_HOST = None
CLICKHOUSE_DB = None

#* Celery — выполняем задачи синхронно
#* Celery tasks run synchronously
CELERY_TASK_ALWAYS_EAGER = True
