"""Модуль для улучшенной обработки ошибок."""

import inspect
import logging
import traceback
from functools import wraps
from typing import Any, Callable, TypeVar

from obsidian_kb.types import ObsidianKBError

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Type alias для контекста логирования
LogContextValue = str | int | float | bool | None


def handle_errors(
    fallback_value: Any = None,
    fallback_func: Callable[[Exception], Any] | None = None,
    log_level: int = logging.ERROR,
) -> Callable[[F], F]:
    """Декоратор для обработки ошибок с fallback.

    Args:
        fallback_value: Значение для возврата при ошибке
        fallback_func: Функция для вызова при ошибке (получает exception)
        log_level: Уровень логирования ошибок

    Returns:
        Декорированная функция
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except ObsidianKBError as e:
                logger.log(log_level, f"ObsidianKB error in {func.__name__}: {e}")
                if fallback_func:
                    return fallback_func(e)
                return fallback_value
            except Exception as e:
                logger.log(
                    log_level,
                    f"Unexpected error in {func.__name__}: {e}\n{traceback.format_exc()}",
                )
                if fallback_func:
                    return fallback_func(e)
                return fallback_value

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ObsidianKBError as e:
                logger.log(log_level, f"ObsidianKB error in {func.__name__}: {e}")
                if fallback_func:
                    return fallback_func(e)
                return fallback_value
            except Exception as e:
                logger.log(
                    log_level,
                    f"Unexpected error in {func.__name__}: {e}\n{traceback.format_exc()}",
                )
                if fallback_func:
                    return fallback_func(e)
                return fallback_value

        # Определяем, async или sync функция
        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def log_error_with_context(
    error: Exception,
    context: dict[str, LogContextValue],
    level: int = logging.ERROR,
) -> None:
    """Логирование ошибки с контекстом.

    Args:
        error: Исключение
        context: Контекстные данные
        level: Уровень логирования
    """
    context_str = ", ".join(f"{k}={v}" for k, v in context.items())
    logger.log(
        level,
        f"Error: {type(error).__name__}: {error} | Context: {context_str}\n{traceback.format_exc()}",
    )


def safe_execute(
    func: Callable[..., Any],
    *args: Any,
    default: Any = None,
    error_message: str | None = None,
    **kwargs: Any,
) -> Any:
    """Безопасное выполнение функции с обработкой ошибок.

    Args:
        func: Функция для выполнения
        *args: Позиционные аргументы
        default: Значение по умолчанию при ошибке
        error_message: Сообщение для логирования
        **kwargs: Именованные аргументы

    Returns:
        Результат функции или default при ошибке
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = error_message or f"Error executing {func.__name__}"
        logger.error(f"{msg}: {e}")
        return default

