#! ClickHouse initialization: creating analytics tables / Инициализация ClickHouse: создание таблиц для аналитики
from django.core.management.base import BaseCommand
from apps.analytics.clickhouse_client import init_tables


class Command(BaseCommand):
    help = 'Create ClickHouse tables for analytics'

    def handle(self, *args, **options):
        init_tables()
        self.stdout.write(self.style.SUCCESS('ClickHouse tables created'))
