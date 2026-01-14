"""Тесты для иерархии исключений MCP инструментов."""

import pytest

from obsidian_kb.types import (
    MCPToolError,
    MCPValidationError,
    MCPVaultError,
    MCPSearchError,
    MCPTimeoutError,
    MCPRateLimitError,
    MCPServiceUnavailableError,
)


class TestMCPToolError:
    """Тесты базового класса MCPToolError."""

    def test_basic_creation(self):
        """Тест создания базовой ошибки."""
        error = MCPToolError(
            message="Test error",
            tool_name="search_vault",
        )

        assert error.message == "Test error"
        assert error.tool_name == "search_vault"
        assert error.user_message == "Test error"
        assert error.context["tool_name"] == "search_vault"

    def test_with_user_message(self):
        """Тест с отдельным сообщением для пользователя."""
        error = MCPToolError(
            message="Technical error details",
            tool_name="search_vault",
            user_message="Search failed, please try again",
        )

        assert error.message == "Technical error details"
        assert error.user_message == "Search failed, please try again"

    def test_with_context(self):
        """Тест с дополнительным контекстом."""
        error = MCPToolError(
            message="Test error",
            tool_name="search_vault",
            context={"vault_name": "my_vault", "query": "test"},
        )

        assert error.context["tool_name"] == "search_vault"
        assert error.context["vault_name"] == "my_vault"
        assert error.context["query"] == "test"

    def test_to_user_response(self):
        """Тест форматирования ответа для пользователя."""
        error = MCPToolError(
            message="Technical details",
            tool_name="search_vault",
            user_message="Search failed",
        )

        assert error.to_user_response() == "Error in search_vault: Search failed"

    def test_str_representation(self):
        """Тест строкового представления."""
        error = MCPToolError(
            message="Test error",
            tool_name="search_vault",
            context={"extra": "info"},
        )

        str_repr = str(error)
        assert "Test error" in str_repr
        assert "tool_name=search_vault" in str_repr


class TestMCPValidationError:
    """Тесты MCPValidationError."""

    def test_basic_validation_error(self):
        """Тест базовой ошибки валидации."""
        error = MCPValidationError(
            message="must be positive",
            tool_name="search_vault",
            param_name="limit",
            param_value=-1,
        )

        assert error.param_name == "limit"
        assert error.param_value == -1
        assert "Invalid parameter 'limit'" in error.user_message
        assert error.context["param_name"] == "limit"
        assert error.context["param_value"] == -1

    def test_without_param_value(self):
        """Тест без значения параметра (для чувствительных данных)."""
        error = MCPValidationError(
            message="invalid format",
            tool_name="search_vault",
            param_name="query",
        )

        assert error.param_value is None
        assert "param_value" not in error.context


class TestMCPVaultError:
    """Тесты MCPVaultError."""

    def test_vault_not_found(self):
        """Тест ошибки vault не найден."""
        error = MCPVaultError(
            message="not indexed",
            tool_name="search_vault",
            vault_name="my_vault",
        )

        assert error.vault_name == "my_vault"
        assert "Vault 'my_vault'" in error.user_message
        assert error.context["vault_name"] == "my_vault"

    def test_with_extra_context(self):
        """Тест с дополнительным контекстом."""
        error = MCPVaultError(
            message="not indexed",
            tool_name="search_vault",
            vault_name="my_vault",
            context={"suggestion": "run index_vault first"},
        )

        assert error.context["suggestion"] == "run index_vault first"


class TestMCPSearchError:
    """Тесты MCPSearchError."""

    def test_basic_search_error(self):
        """Тест базовой ошибки поиска."""
        error = MCPSearchError(
            message="Vector search failed",
            tool_name="search_vault",
            query="test query",
            search_type="vector",
        )

        assert error.query == "test query"
        assert error.search_type == "vector"
        assert error.context["query"] == "test query"
        assert error.context["search_type"] == "vector"

    def test_without_query(self):
        """Тест без запроса (для приватности)."""
        error = MCPSearchError(
            message="Search failed",
            tool_name="search_vault",
            search_type="hybrid",
        )

        assert error.query is None
        assert "query" not in error.context


class TestMCPTimeoutError:
    """Тесты MCPTimeoutError."""

    def test_timeout_error(self):
        """Тест ошибки таймаута."""
        error = MCPTimeoutError(
            message="Index operation took too long",
            tool_name="index_vault",
            timeout_seconds=30.0,
        )

        assert error.timeout_seconds == 30.0
        assert "30.0s" in error.user_message
        assert error.context["timeout_seconds"] == 30.0


class TestMCPRateLimitError:
    """Тесты MCPRateLimitError."""

    def test_rate_limit_with_retry(self):
        """Тест rate limit с указанием retry после."""
        error = MCPRateLimitError(
            tool_name="search_vault",
            retry_after_seconds=5.0,
        )

        assert error.retry_after_seconds == 5.0
        assert "5.0s" in error.user_message
        assert error.context["retry_after_seconds"] == 5.0

    def test_rate_limit_without_retry(self):
        """Тест rate limit без retry."""
        error = MCPRateLimitError(tool_name="search_vault")

        assert error.retry_after_seconds is None
        assert "try again later" in error.user_message


class TestMCPServiceUnavailableError:
    """Тесты MCPServiceUnavailableError."""

    def test_service_unavailable(self):
        """Тест недоступности сервиса."""
        error = MCPServiceUnavailableError(
            message="Connection refused",
            tool_name="search_vault",
            service_name="Ollama",
        )

        assert error.service_name == "Ollama"
        assert "Service 'Ollama'" in error.user_message
        assert error.context["service_name"] == "Ollama"


class TestExceptionHierarchy:
    """Тесты иерархии исключений."""

    def test_all_inherit_from_mcp_tool_error(self):
        """Тест что все исключения наследуют от MCPToolError."""
        exceptions = [
            MCPValidationError("msg", "tool", "param"),
            MCPVaultError("msg", "tool", "vault"),
            MCPSearchError("msg", "tool"),
            MCPTimeoutError("msg", "tool", 10.0),
            MCPRateLimitError("tool"),
            MCPServiceUnavailableError("msg", "tool", "service"),
        ]

        for exc in exceptions:
            assert isinstance(exc, MCPToolError)

    def test_can_catch_by_base_class(self):
        """Тест что можно перехватить по базовому классу."""
        try:
            raise MCPValidationError("test", "tool", "param")
        except MCPToolError as e:
            assert e.tool_name == "tool"
        else:
            pytest.fail("Should have caught MCPToolError")

    def test_specific_catch_before_base(self):
        """Тест что специфичный catch работает раньше базового."""
        try:
            raise MCPValidationError("test", "tool", "param")
        except MCPValidationError as e:
            assert e.param_name == "param"
        except MCPToolError:
            pytest.fail("Should have caught MCPValidationError first")
