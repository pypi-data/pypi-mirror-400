"""Тесты для модуля обработки ошибок."""

import pytest

from obsidian_kb.error_handler import handle_errors, log_error_with_context, safe_execute
from obsidian_kb.providers.exceptions import ProviderConnectionError
from obsidian_kb.types import ObsidianKBError


def test_safe_execute_success():
    """Тест успешного выполнения функции."""
    def func(x: int, y: int) -> int:
        return x + y

    result = safe_execute(func, 2, 3, default=0)
    assert result == 5


def test_safe_execute_error():
    """Тест обработки ошибки в safe_execute."""
    def func() -> None:
        raise ValueError("Test error")

    result = safe_execute(func, default="default_value")
    assert result == "default_value"


def test_safe_execute_custom_error_message(caplog):
    """Тест safe_execute с кастомным сообщением об ошибке."""
    def func() -> None:
        raise ValueError("Test error")

    safe_execute(func, default=None, error_message="Custom error")
    assert "Custom error" in caplog.text


@pytest.mark.asyncio
async def test_handle_errors_async_success():
    """Тест успешного выполнения async функции с декоратором."""
    @handle_errors(fallback_value=None)
    async def async_func(x: int) -> int:
        return x * 2

    result = await async_func(5)
    assert result == 10


@pytest.mark.asyncio
async def test_handle_errors_async_fallback():
    """Тест fallback при ошибке в async функции."""
    @handle_errors(fallback_value="fallback")
    async def async_func() -> str:
        raise ValueError("Error")

    result = await async_func()
    assert result == "fallback"


@pytest.mark.asyncio
async def test_handle_errors_async_fallback_func():
    """Тест fallback функции при ошибке."""
    def fallback_func(error: Exception) -> str:
        return f"Error: {type(error).__name__}"

    @handle_errors(fallback_func=fallback_func)
    async def async_func() -> str:
        raise ProviderConnectionError("Connection failed")

    result = await async_func()
    assert "ProviderConnectionError" in result


def test_handle_errors_sync_success():
    """Тест успешного выполнения sync функции с декоратором."""
    @handle_errors(fallback_value=None)
    def sync_func(x: int) -> int:
        return x * 2

    result = sync_func(5)
    assert result == 10


def test_handle_errors_sync_fallback():
    """Тест fallback при ошибке в sync функции."""
    @handle_errors(fallback_value="fallback")
    def sync_func() -> str:
        raise ValueError("Error")

    result = sync_func()
    assert result == "fallback"


def test_log_error_with_context(caplog):
    """Тест логирования ошибки с контекстом."""
    import logging
    caplog.set_level(logging.INFO)
    
    error = ValueError("Test error")
    context = {"vault": "test_vault", "operation": "indexing"}

    log_error_with_context(error, context, level=logging.INFO)

    assert "Test error" in caplog.text
    assert "vault=test_vault" in caplog.text
    assert "operation=indexing" in caplog.text


def test_handle_errors_obsidian_kb_error(caplog):
    """Тест обработки ProviderConnectionError."""
    import logging
    caplog.set_level(logging.WARNING)

    @handle_errors(fallback_value=None, log_level=logging.WARNING)
    def func() -> None:
        raise ProviderConnectionError("Provider unavailable")

    result = func()
    assert result is None
    assert "Provider unavailable" in caplog.text

