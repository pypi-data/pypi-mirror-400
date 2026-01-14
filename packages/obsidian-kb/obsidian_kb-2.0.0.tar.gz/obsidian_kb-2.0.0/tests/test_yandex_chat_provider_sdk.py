"""Тесты для YandexChatProvider с использованием yandex-cloud-ml-sdk."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.interfaces import ProviderHealth
from obsidian_kb.providers.provider_config import (
    PROVIDER_CONFIGS,
    ProviderConfig,
    get_provider_config,
)
from obsidian_kb.providers.yandex.chat_provider import YandexChatProvider


class TestProviderConfig:
    """Тесты для конфигурации провайдеров."""

    def test_get_provider_config_ollama(self):
        """Тест получения конфигурации ollama."""
        config = get_provider_config("ollama")
        assert config.max_concurrent == 10
        assert config.batch_size == 32
        assert config.enrichment_concurrent == 5
        assert config.timeout == 60

    def test_get_provider_config_yandex(self):
        """Тест получения конфигурации yandex."""
        config = get_provider_config("yandex")
        assert config.max_concurrent == 50
        assert config.batch_size == 100
        assert config.enrichment_concurrent == 10  # Уменьшено для стабильности
        assert config.timeout == 30
        # Параметры адаптивного rate limiting
        assert config.adaptive_rate_limit is True
        assert config.rate_limit_rps == 20  # Начальный RPS
        assert config.rate_limit_min_rps == 2.0
        assert config.rate_limit_max_rps == 100.0
        assert config.rate_limit_recovery == 30

    def test_get_provider_config_case_insensitive(self):
        """Тест регистронезависимости имени провайдера."""
        config1 = get_provider_config("YANDEX")
        config2 = get_provider_config("Yandex")
        config3 = get_provider_config("yandex")
        assert config1 == config2 == config3

    def test_get_provider_config_fallback(self):
        """Тест fallback на ollama для неизвестного провайдера."""
        config = get_provider_config("unknown_provider")
        assert config == PROVIDER_CONFIGS["ollama"]

    def test_provider_config_frozen(self):
        """Тест что конфигурация immutable."""
        config = get_provider_config("yandex")
        with pytest.raises(Exception):  # FrozenInstanceError
            config.timeout = 100


class TestYandexChatProviderInit:
    """Тесты инициализации YandexChatProvider."""

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_init_success(self, mock_sdk):
        """Тест успешной инициализации."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            model="qwen3-235b-a22b-fp8/latest",
        )

        assert provider.name == "yandex"
        assert provider.model == "qwen3-235b-a22b-fp8/latest"
        mock_sdk.assert_called_once_with(folder_id="test_folder", auth="test_key")

    def test_init_missing_folder_id(self):
        """Тест ошибки при отсутствии folder_id."""
        with pytest.raises(ValueError, match="folder_id is required"):
            YandexChatProvider(folder_id="", api_key="test_key")

    def test_init_missing_api_key(self):
        """Тест ошибки при отсутствии api_key."""
        with pytest.raises(ValueError, match="api_key is required"):
            YandexChatProvider(folder_id="test_folder", api_key="")

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_init_with_custom_timeout(self, mock_sdk):
        """Тест инициализации с пользовательским таймаутом."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            timeout=120,
        )
        assert provider._timeout == 120

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_init_with_instance_id(self, mock_sdk):
        """Тест инициализации с instance_id для dedicated instances."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            instance_id="my_instance",
        )
        assert provider._get_model_id() == "yandexgpt/my_instance"

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_get_model_id_strips_latest_suffix(self, mock_sdk):
        """Тест что _get_model_id() убирает суффикс /latest."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            model="yandexgpt/latest",
        )
        assert provider._get_model_id() == "yandexgpt"

        provider2 = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            model="yandexgpt-lite",
        )
        assert provider2._get_model_id() == "yandexgpt-lite"


class TestYandexChatProviderComplete:
    """Тесты метода complete()."""

    @pytest.fixture
    def mock_sdk(self):
        """Фикстура для мока SDK."""
        with patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_complete_success_grpc(self, mock_sdk):
        """Тест успешного chat completion через gRPC (YandexGPT)."""
        # Arrange
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(text="Test response")]

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            model="yandexgpt-lite",  # YandexGPT модели используют gRPC
        )

        # Act
        result = await provider.complete([{"role": "user", "content": "Hello"}])

        # Assert
        assert result == "Test response"
        mock_sdk.return_value.models.completions.assert_called_once_with(
            "yandexgpt-lite"
        )

    @pytest.mark.asyncio
    async def test_complete_with_yandexgpt_model(self, mock_sdk):
        """Тест chat completion с моделью YandexGPT."""
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(text="Привет!")]

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            model="yandexgpt/latest",
        )

        result = await provider.complete([{"role": "user", "content": "Привет"}])

        assert result == "Привет!"
        # SDK получает модель без /latest, так как сам добавляет этот суффикс
        mock_sdk.return_value.models.completions.assert_called_once_with(
            "yandexgpt"
        )

    @pytest.mark.asyncio
    async def test_complete_success_http(self, mock_sdk):
        """Тест успешного chat completion через HTTP (Qwen)."""
        # Qwen модели используют HTTP API, не gRPC
        with patch("obsidian_kb.providers.yandex.chat_provider.aiohttp.ClientSession") as mock_session_class:
            # Настраиваем mock для HTTP сессии
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "choices": [{"message": {"content": "OK from Qwen"}}]
            })

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response)))
            mock_session.closed = False
            mock_session_class.return_value = mock_session

            provider = YandexChatProvider(
                folder_id="test_folder",
                api_key="test_key",
                model="qwen3-235b-a22b-fp8",  # Qwen модели используют HTTP
            )
            # Подменяем сессию
            provider._http_session = mock_session

            result = await provider.complete([{"role": "user", "content": "Hello"}])

            assert result == "OK from Qwen"

    @pytest.mark.asyncio
    async def test_complete_with_temperature(self, mock_sdk):
        """Тест chat completion с заданной температурой."""
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(text="Response")]

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        await provider.complete(
            [{"role": "user", "content": "Test"}],
            temperature=0.3,
        )

        # Проверяем, что configure был вызван с нужной температурой
        mock_model.configure.assert_any_call(temperature=0.3)

    @pytest.mark.asyncio
    async def test_complete_with_max_tokens(self, mock_sdk):
        """Тест chat completion с max_tokens."""
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(text="Response")]

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        await provider.complete(
            [{"role": "user", "content": "Test"}],
            max_tokens=100,
        )

        # Проверяем, что configure был вызван с max_tokens
        mock_model.configure.assert_any_call(max_tokens=100)

    @pytest.mark.asyncio
    async def test_complete_empty_messages(self, mock_sdk):
        """Тест ошибки при пустом списке сообщений."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        with pytest.raises(ValueError, match="Messages cannot be empty"):
            await provider.complete([])

    @pytest.mark.asyncio
    async def test_complete_empty_response(self, mock_sdk):
        """Тест ошибки при пустом ответе от API."""
        mock_result = MagicMock()
        mock_result.alternatives = []

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        with pytest.raises(ProviderError, match="Empty response"):
            await provider.complete([{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_empty_content(self, mock_sdk):
        """Тест ошибки при пустом контенте в ответе."""
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(text="")]

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        with pytest.raises(ProviderError, match="Empty content"):
            await provider.complete([{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_timeout(self, mock_sdk):
        """Тест таймаута при запросе."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=asyncio.TimeoutError())

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            timeout=1,
        )

        with pytest.raises(ProviderTimeoutError, match="timeout"):
            await provider.complete([{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_authentication_error(self, mock_sdk):
        """Тест ошибки аутентификации."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=Exception("401 Unauthorized"))

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="invalid_key",
        )

        with pytest.raises(ProviderAuthenticationError, match="authentication"):
            await provider.complete([{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_access_denied(self, mock_sdk):
        """Тест ошибки доступа (403)."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=Exception("403 Forbidden"))

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="wrong_folder",
            api_key="test_key",
        )

        with pytest.raises(ProviderAuthenticationError, match="access denied"):
            await provider.complete([{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_rate_limit(self, mock_sdk):
        """Тест ошибки rate limit (429)."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=Exception("429 Too Many Requests"))

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        with pytest.raises(ProviderError, match="rate limit"):
            await provider.complete([{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_generic_error(self, mock_sdk):
        """Тест обработки общей ошибки."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=Exception("Some network error"))

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        with pytest.raises(ProviderConnectionError, match="Yandex API error"):
            await provider.complete([{"role": "user", "content": "Test"}])


class TestYandexChatProviderHealthCheck:
    """Тесты метода health_check()."""

    @pytest.fixture
    def mock_sdk(self):
        """Фикстура для мока SDK."""
        with patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_sdk):
        """Тест успешного health check."""
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(text="ok")]

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
            model="yandexgpt/latest",
        )

        health = await provider.health_check()

        assert health.available is True
        assert health.model == "yandexgpt/latest"
        assert health.latency_ms is not None
        assert health.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_health_check_empty_response(self, mock_sdk):
        """Тест health check с пустым ответом."""
        mock_result = MagicMock()
        mock_result.alternatives = []

        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(return_value=mock_result)

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        health = await provider.health_check()

        assert health.available is False
        assert "Empty response" in health.error

    @pytest.mark.asyncio
    async def test_health_check_auth_error(self, mock_sdk):
        """Тест health check с ошибкой аутентификации."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=Exception("401 Authentication failed"))

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="invalid_key",
        )

        health = await provider.health_check()

        assert health.available is False
        assert "Authentication" in health.error

    @pytest.mark.asyncio
    async def test_health_check_forbidden_error(self, mock_sdk):
        """Тест health check с ошибкой доступа."""
        mock_model = MagicMock()
        mock_model.configure.return_value = mock_model
        mock_model.run = AsyncMock(side_effect=Exception("403 Forbidden"))

        mock_sdk.return_value.models.completions.return_value = mock_model

        provider = YandexChatProvider(
            folder_id="wrong_folder",
            api_key="test_key",
        )

        health = await provider.health_check()

        assert health.available is False
        assert "Access denied" in health.error


class TestYandexChatProviderMessageConversion:
    """Тесты конвертации сообщений."""

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_convert_messages_for_grpc_basic(self, mock_sdk):
        """Тест базовой конвертации сообщений для gRPC (YandexGPT)."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

        result = provider._convert_messages_for_grpc(messages)

        assert len(result) == 3
        assert result[0] == {"role": "system", "text": "You are helpful."}
        assert result[1] == {"role": "user", "text": "Hello"}
        assert result[2] == {"role": "assistant", "text": "Hi!"}

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_convert_messages_for_http_basic(self, mock_sdk):
        """Тест базовой конвертации сообщений для HTTP (OpenAI API)."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

        result = provider._convert_messages_for_http(messages)

        assert len(result) == 3
        assert result[0] == {"role": "system", "content": "You are helpful."}
        assert result[1] == {"role": "user", "content": "Hello"}
        assert result[2] == {"role": "assistant", "content": "Hi!"}

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_convert_messages_with_text_key(self, mock_sdk):
        """Тест конвертации сообщений с ключом 'text' вместо 'content'."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        messages = [
            {"role": "user", "text": "Hello from text key"},
        ]

        # gRPC формат
        result_grpc = provider._convert_messages_for_grpc(messages)
        assert result_grpc[0] == {"role": "user", "text": "Hello from text key"}

        # HTTP формат
        result_http = provider._convert_messages_for_http(messages)
        assert result_http[0] == {"role": "user", "content": "Hello from text key"}

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_convert_messages_invalid_role(self, mock_sdk):
        """Тест конвертации сообщений с неправильной ролью."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        messages = [
            {"role": "invalid_role", "content": "Test"},
        ]

        result = provider._convert_messages_for_grpc(messages)

        # Неизвестные роли должны конвертироваться в 'user'
        assert result[0] == {"role": "user", "text": "Test"}

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_convert_messages_missing_role(self, mock_sdk):
        """Тест конвертации сообщений без роли."""
        provider = YandexChatProvider(
            folder_id="test_folder",
            api_key="test_key",
        )

        messages = [
            {"content": "Test without role"},
        ]

        result = provider._convert_messages_for_grpc(messages)

        assert result[0] == {"role": "user", "text": "Test without role"}
