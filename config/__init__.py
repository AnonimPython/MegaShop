from .celery import app as celery_app
from .logging_setup import logger

__all__ = ('celery_app', 'logger')
