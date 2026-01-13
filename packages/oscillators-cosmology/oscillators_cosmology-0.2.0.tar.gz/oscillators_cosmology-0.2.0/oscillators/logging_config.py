"""
Конфигурация логирования для библиотеки oscillators.

Использование:
    from oscillators.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("Симуляция запущена")
"""

import logging
import sys
from typing import Optional


# Формат логов
DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
SIMPLE_FORMAT = "%(levelname)s: %(message)s"
DETAILED_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

# Уровень по умолчанию
DEFAULT_LEVEL = logging.INFO


def get_logger(
    name: str,
    level: int = DEFAULT_LEVEL,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Получить настроенный логгер.
    
    Args:
        name: имя логгера (обычно __name__)
        level: уровень логирования
        format_string: строка форматирования
        
    Returns:
        настроенный логгер
    """
    logger = logging.getLogger(name)
    
    # Если уже настроен, возвращаем
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Создаём обработчик для stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Форматирование
    fmt = format_string or DEFAULT_FORMAT
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Предотвращаем дублирование логов
    logger.propagate = False
    
    return logger


def setup_logging(
    level: int = DEFAULT_LEVEL,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
):
    """
    Глобальная настройка логирования.
    
    Args:
        level: уровень логирования
        format_string: строка форматирования
        log_file: файл для логов (опционально)
    """
    fmt = format_string or DEFAULT_FORMAT
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )


def set_level(level: int):
    """
    Установить уровень логирования для всей библиотеки.
    
    Args:
        level: уровень логирования (logging.DEBUG, logging.INFO, и т.д.)
    """
    logging.getLogger('oscillators').setLevel(level)


def enable_debug():
    """Включить отладочный режим."""
    set_level(logging.DEBUG)


def enable_quiet():
    """Включить тихий режим (только ошибки)."""
    set_level(logging.ERROR)


# Создаём корневой логгер для библиотеки
root_logger = get_logger('oscillators')

