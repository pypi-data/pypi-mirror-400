"""Тесты для структурированного логирования."""

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from obsidian_kb.structured_logging import (
    ContextLogger,
    JSONFormatter,
    LogContext,
    generate_operation_id,
    get_logger,
    get_structured_logger,
    setup_structured_logging,
)


def test_json_formatter_basic():
    """Тест базового форматирования JSON."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    log_data = json.loads(result)

    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "test"
    assert log_data["message"] == "Test message"
    assert "timestamp" in log_data


def test_json_formatter_with_exception():
    """Тест форматирования с исключением."""
    formatter = JSONFormatter()

    try:
        raise ValueError("Test error")
    except ValueError:
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=sys.exc_info(),
        )

    result = formatter.format(record)
    log_data = json.loads(result)

    assert log_data["level"] == "ERROR"
    assert "exception" in log_data
    assert log_data["exception"]["type"] == "ValueError"
    assert "Test error" in log_data["exception"]["message"]


def test_json_formatter_with_extra():
    """Тест форматирования с extra полями."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    record.operation = "search"
    record.vault_name = "test_vault"

    result = formatter.format(record)
    log_data = json.loads(result)

    assert "extra" in log_data
    assert log_data["extra"]["operation"] == "search"
    assert log_data["extra"]["vault_name"] == "test_vault"


def test_setup_structured_logging():
    """Тест настройки структурированного логирования."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        setup_structured_logging(
            level=logging.INFO,
            log_file=log_file,
            json_format=True,
        )

        logger = logging.getLogger("test_logger_setup")
        logger.info("Test message", extra={"key": "value"})

        # Проверяем что файл создан
        assert log_file.exists()

        # Проверяем содержимое
        with open(log_file, "r", encoding="utf-8") as f:
            line = f.readline()
            log_data = json.loads(line)
            assert log_data["message"] == "Test message"
            assert log_data["extra"]["key"] == "value"


def test_get_logger():
    """Тест получения контекстного логгера."""
    logger = get_logger("test_context")

    assert isinstance(logger, ContextLogger)
    assert logger.name == "test_context"


def test_get_structured_logger():
    """Тест получения структурированного логгера (обратная совместимость)."""
    logger = get_structured_logger("test_compat")

    assert isinstance(logger, ContextLogger)
    assert logger.name == "test_compat"


def test_context_logger_methods():
    """Тест методов ContextLogger."""
    logger = get_logger("test_methods")

    # Проверяем что методы существуют и не падают
    logger.debug("Debug message", vault_name="test")
    logger.info("Info message", vault_name="test", count=5)
    logger.warning("Warning message", operation="test_op")
    logger.error("Error message", error="test_error")
    logger.critical("Critical message", severity="high")


def test_context_logger_with_exc_info():
    """Тест логирования с exc_info."""
    logger = get_logger("test_exc")

    try:
        raise ValueError("Test error")
    except ValueError:
        logger.error("Error occurred", exc_info=True, error_type="ValueError")


def test_context_logger_exception():
    """Тест метода exception()."""
    logger = get_logger("test_exception")

    try:
        raise ValueError("Test error")
    except ValueError:
        logger.exception("Error occurred", operation="test")


def test_json_formatter_without_context():
    """Тест форматирования без контекста."""
    formatter = JSONFormatter(include_context=False)
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    record.custom_field = "should_not_appear"

    result = formatter.format(record)
    log_data = json.loads(result)

    assert "extra" not in log_data
    assert "context" not in log_data


def test_log_context_basic():
    """Тест LogContext context manager."""
    with LogContext(vault_name="my_vault", operation_id="abc123"):
        context = LogContext.get_current()
        assert context["vault_name"] == "my_vault"
        assert context["operation_id"] == "abc123"

    # После выхода контекст должен быть очищен
    context = LogContext.get_current()
    assert context == {}


def test_log_context_nested():
    """Тест вложенных LogContext."""
    with LogContext(vault_name="my_vault"):
        with LogContext(file_path="notes/readme.md"):
            context = LogContext.get_current()
            assert context["vault_name"] == "my_vault"
            assert context["file_path"] == "notes/readme.md"

        # После выхода из внутреннего контекста
        context = LogContext.get_current()
        assert context["vault_name"] == "my_vault"
        assert "file_path" not in context


def test_log_context_set_and_clear():
    """Тест статических методов set() и clear()."""
    LogContext.set(vault_name="test_vault")
    context = LogContext.get_current()
    assert context["vault_name"] == "test_vault"

    LogContext.clear()
    context = LogContext.get_current()
    assert context == {}


def test_generate_operation_id():
    """Тест генерации operation_id."""
    op_id1 = generate_operation_id()
    op_id2 = generate_operation_id()

    assert len(op_id1) == 8
    assert len(op_id2) == 8
    assert op_id1 != op_id2  # Уникальность


def test_json_formatter_with_log_context():
    """Тест JSONFormatter с LogContext."""
    # Очищаем контекст перед тестом
    LogContext.clear()

    formatter = JSONFormatter()

    with LogContext(vault_name="context_vault", operation="search"):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "context" in log_data
        assert log_data["context"]["vault_name"] == "context_vault"
        assert log_data["context"]["operation"] == "search"

    # Очищаем контекст после теста
    LogContext.clear()


def test_context_logger_is_enabled_for():
    """Тест метода isEnabledFor."""
    logger = get_logger("test_enabled")
    logger.setLevel(logging.WARNING)

    assert logger.isEnabledFor(logging.WARNING)
    assert logger.isEnabledFor(logging.ERROR)
    assert not logger.isEnabledFor(logging.DEBUG)
    assert not logger.isEnabledFor(logging.INFO)
