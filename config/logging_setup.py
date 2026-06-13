#? Loguru для MegaShop / Colour console + file output
#! Используется / Usage: @loguru.catch decorator or from loguru import logger
import sys
from pathlib import Path
from loguru import logger


def setup_logging():
    #* Удаляем стандартный handler / Remove default handler
    logger.remove()

    #* Формат / Format: time | level | file:line | message
    fmt = (
        '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
        '<level>{level: <7}</level> | '
        '<cyan>{name}</cyan>:<cyan>{line}</cyan> | '
        '<level>{message}</level>'
    )

    #* Консоль / Colour console output
    logger.add(
        sys.stderr,
        format=fmt,
        level='DEBUG',
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    #* Файл / File rotation — daily, keep 7 days
    #* Локально / Local: /tmp/megashop_logs, Docker: /app/logs
    log_dir = Path('/app/logs') if Path('/app').exists() else Path('/tmp/megashop_logs')
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / 'megashop_{time:YYYY-MM-DD}.log',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {name}:{line} | {message}',
        level='INFO',
        rotation='1 day',
        retention='7 days',
        compression='gz',
        enqueue=True,
    )

    #* Ошибки / Errors — separate file, 30 day retention
    logger.add(
        log_dir / 'errors_{time:YYYY-MM-DD}.log',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {name}:{line} | {message}',
        level='ERROR',
        rotation='1 day',
        retention='30 days',
        compression='gz',
        enqueue=True,
    )

    return logger


# Инициализируем / Initialise on import
logger = setup_logging()
