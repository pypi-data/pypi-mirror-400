"""Модуль для структурированного логирования в JSON формате.

Этот модуль предоставляет:
- JSONFormatter для форматирования логов в JSON
- ContextLogger для логирования с контекстом
- LogContext для передачи контекста между функциями
- setup_structured_logging() для настройки логирования

Пример использования:
    from obsidian_kb.structured_logging import get_logger, LogContext

    logger = get_logger(__name__)

    # Простое логирование с контекстом
    logger.info("Operation started", vault_name="my_vault", file_count=10)

    # Использование LogContext для передачи контекста
    with LogContext(vault_name="my_vault", operation_id="abc123"):
        logger.info("Processing file", file_path="notes/readme.md")
        # Лог будет содержать vault_name и operation_id автоматически
"""

import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any


# Context variable для хранения текущего контекста логирования
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})


class LogContext:
    """Context manager для добавления контекста к логам.

    Позволяет автоматически добавлять контекстные данные ко всем логам
    внутри блока with. Контексты можно вкладывать друг в друга.

    Пример:
        with LogContext(vault_name="my_vault"):
            logger.info("Started")  # vault_name будет добавлен автоматически
            with LogContext(file_path="notes/readme.md"):
                logger.info("Processing")  # vault_name и file_path будут добавлены
    """

    def __init__(self, **kwargs: Any) -> None:
        """Инициализация контекста.

        Args:
            **kwargs: Контекстные данные для добавления к логам
        """
        self._context = kwargs
        self._token: Any = None
        self._previous: dict[str, Any] = {}

    def __enter__(self) -> "LogContext":
        """Вход в контекст."""
        self._previous = _log_context.get().copy()
        new_context = {**self._previous, **self._context}
        self._token = _log_context.set(new_context)
        return self

    def __exit__(self, *args: Any) -> None:
        """Выход из контекста."""
        _log_context.set(self._previous)

    @staticmethod
    def get_current() -> dict[str, Any]:
        """Получить текущий контекст логирования.

        Returns:
            Словарь с текущими контекстными данными
        """
        return _log_context.get().copy()

    @staticmethod
    def set(**kwargs: Any) -> None:
        """Установить контекст без использования context manager.

        Args:
            **kwargs: Контекстные данные для добавления
        """
        current = _log_context.get().copy()
        current.update(kwargs)
        _log_context.set(current)

    @staticmethod
    def clear() -> None:
        """Очистить текущий контекст."""
        _log_context.set({})


def generate_operation_id() -> str:
    """Генерация уникального идентификатора операции.

    Returns:
        Короткий уникальный идентификатор (8 символов)
    """
    return uuid.uuid4().hex[:8]



class JSONFormatter(logging.Formatter):
    """Форматтер для структурированного логирования в JSON формате.

    Автоматически включает:
    - Timestamp в ISO формате
    - Уровень логирования
    - Имя логгера
    - Сообщение
    - Контекст из LogContext (если есть)
    - Extra поля из записи лога
    - Информацию об исключении (если есть)
    """

    # Стандартные поля LogRecord которые не нужно включать в контекст
    _STANDARD_FIELDS = {
        "name", "msg", "args", "created", "filename", "funcName",
        "levelname", "levelno", "lineno", "module", "msecs",
        "message", "pathname", "process", "processName", "relativeCreated",
        "thread", "threadName", "exc_info", "exc_text", "stack_info",
        "taskName",  # Python 3.12+
    }

    def __init__(self, include_context: bool = True) -> None:
        """Инициализация JSON форматтера.

        Args:
            include_context: Включать ли контекст (extra поля) в JSON
        """
        super().__init__()
        self.include_context = include_context

    def format(self, record: logging.LogRecord) -> str:
        """Форматирование записи лога в JSON.

        Args:
            record: Запись лога

        Returns:
            JSON строка с данными лога
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Добавляем информацию об исключении если есть
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }

        # Добавляем контекст из LogContext (contextvars)
        if self.include_context:
            context = LogContext.get_current()
            if context:
                log_data["context"] = context

        # Добавляем extra поля из записи лога
        if self.include_context:
            extra_data: dict[str, Any] = {}
            for key, value in record.__dict__.items():
                if key not in self._STANDARD_FIELDS:
                    # Сериализуем только простые типы
                    try:
                        json.dumps(value)  # Проверяем сериализуемость
                        extra_data[key] = value
                    except (TypeError, ValueError):
                        extra_data[key] = str(value)

            if extra_data:
                log_data["extra"] = extra_data

        return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_structured_logging(
    level: int | None = None,
    log_file: Path | None = None,
    json_format: bool | None = None,
) -> None:
    """Настройка структурированного логирования.

    Параметры могут быть переопределены через переменные окружения:
    - OBSIDIAN_KB_LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - OBSIDIAN_KB_LOG_FILE: путь к файлу логов
    - OBSIDIAN_KB_LOG_JSON: true/false (JSON или text формат)

    Args:
        level: Уровень логирования (по умолчанию INFO)
        log_file: Путь к файлу для записи логов (опционально)
        json_format: Использовать ли JSON формат (по умолчанию False для CLI)

    Пример:
        # Базовая настройка
        setup_structured_logging()

        # JSON логирование для production
        setup_structured_logging(json_format=True)

        # Подробное логирование в файл
        setup_structured_logging(
            level=logging.DEBUG,
            log_file=Path("/var/log/obsidian-kb.log"),
            json_format=True,
        )
    """
    # Читаем настройки из переменных окружения
    env_level = os.environ.get("OBSIDIAN_KB_LOG_LEVEL", "").upper()
    env_file = os.environ.get("OBSIDIAN_KB_LOG_FILE")
    env_json = os.environ.get("OBSIDIAN_KB_LOG_JSON", "").lower()

    # Определяем уровень логирования
    if level is None:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        level = level_map.get(env_level, logging.INFO)

    # Определяем файл логов
    if log_file is None and env_file:
        log_file = Path(env_file)

    # Определяем формат (по умолчанию text для CLI, т.к. JSON не читабелен)
    if json_format is None:
        json_format = env_json in ("true", "1", "yes")

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Форматтер
    if json_format:
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Консольный обработчик (stderr для лучшей совместимости с pipe)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Файловый обработчик (если указан)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


class ContextLogger:
    """Логгер с поддержкой контекстных аргументов.

    Обёртка над стандартным logging.Logger, позволяющая передавать
    контекстные данные как keyword arguments.

    Пример:
        logger = get_logger(__name__)
        logger.info("File processed", file_path="notes/readme.md", chunks=5)
        logger.error("Failed to index", vault_name="my_vault", error_type="timeout")
    """

    def __init__(self, name: str) -> None:
        """Инициализация контекстного логгера.

        Args:
            name: Имя логгера (обычно __name__)
        """
        self._logger = logging.getLogger(name)
        self.name = name

    def _log(
        self,
        level: int,
        msg: str,
        *args: Any,
        exc_info: Any = None,
        stack_info: bool = False,
        **kwargs: Any,
    ) -> None:
        """Внутренний метод для логирования.

        Args:
            level: Уровень логирования
            msg: Сообщение
            *args: Позиционные аргументы для форматирования
            exc_info: Информация об исключении
            stack_info: Включить ли stack trace
            **kwargs: Контекстные данные для добавления в extra
        """
        if self._logger.isEnabledFor(level):
            self._logger.log(
                level,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                extra=kwargs if kwargs else None,
            )

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Логирование на уровне DEBUG."""
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Логирование на уровне INFO."""
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Логирование на уровне WARNING."""
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        """Логирование на уровне ERROR."""
        self._log(logging.ERROR, msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args: Any, exc_info: Any = None, **kwargs: Any) -> None:
        """Логирование на уровне CRITICAL."""
        self._log(logging.CRITICAL, msg, *args, exc_info=exc_info, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Логирование исключения с трейсбеком."""
        self._log(logging.ERROR, msg, *args, exc_info=True, **kwargs)

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Логирование на произвольном уровне."""
        self._log(level, msg, *args, **kwargs)

    def isEnabledFor(self, level: int) -> bool:
        """Проверка, включён ли уровень логирования."""
        return self._logger.isEnabledFor(level)

    def setLevel(self, level: int) -> None:
        """Установка уровня логирования."""
        self._logger.setLevel(level)

    @property
    def level(self) -> int:
        """Текущий уровень логирования."""
        return self._logger.level


# Кэш для логгеров
_loggers: dict[str, ContextLogger] = {}


def get_logger(name: str) -> ContextLogger:
    """Получение контекстного логгера.

    Args:
        name: Имя логгера (обычно __name__)

    Returns:
        ContextLogger с поддержкой контекстных аргументов

    Пример:
        logger = get_logger(__name__)
        logger.info("Started indexing", vault_name="my_vault")
    """
    if name not in _loggers:
        _loggers[name] = ContextLogger(name)
    return _loggers[name]


def get_structured_logger(name: str) -> ContextLogger:
    """Получение логгера с поддержкой структурированного логирования.

    Args:
        name: Имя логгера

    Returns:
        Настроенный логгер

    Note:
        Эта функция сохранена для обратной совместимости.
        Рекомендуется использовать get_logger() напрямую.
    """
    return get_logger(name)

