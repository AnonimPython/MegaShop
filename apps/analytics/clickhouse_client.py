#! ClickHouse client for MegaShop analytics / ClickHouse клиент для аналитики MegaShop
#? Used for aggregating views, orders, and user actions / Используется для агрегации просмотров, заказов и действий пользователей
from django.conf import settings
from clickhouse_driver import Client as CHClient


def get_client():
    return CHClient(
        host=settings.CLICKHOUSE_HOST,
        port=int(settings.CLICKHOUSE_PORT),
        user=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DB,
    )


def init_tables():
    #* Create analytics tables if they don't exist / Создаём таблицы для аналитики, если их нет
    client = get_client()
    client.execute('''
        CREATE TABLE IF NOT EXISTS product_views (
            event_date Date,
            product_id UInt32,
            product_name String,
            user_id Nullable(UInt32),
            store_id Nullable(UInt32),
            viewed_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (event_date, product_id)
    ''')
    client.execute('''
        CREATE TABLE IF NOT EXISTS order_events (
            event_date Date,
            order_id UInt32,
            product_id UInt32,
            store_id Nullable(UInt32),
            quantity UInt16,
            price Float64,
            status String,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (event_date, order_id)
    ''')
