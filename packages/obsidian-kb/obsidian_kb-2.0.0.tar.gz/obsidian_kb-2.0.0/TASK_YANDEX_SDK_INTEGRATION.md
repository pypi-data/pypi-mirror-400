# Техническое задание: Интеграция Yandex Cloud ML SDK

## Контекст проблемы

**BUG-10:** Yandex Chat провайдер не работает ни с одной моделью (HTTP 400: "Failed to get model").

**Причина:** Текущая реализация использует прямые HTTP запросы к Yandex API, но:
1. Для OpenAI-совместимых моделей (Qwen, DeepSeek) отсутствует заголовок `x-folder-id` / `OpenAI-Project`
2. Формат URI модели может быть некорректным для разных типов API
3. Нет единого способа работы с разными типами моделей (YandexGPT vs Open Source)

## Решение

Использовать официальный **yandex-cloud-ml-sdk** вместо прямых HTTP запросов.

### Преимущества SDK

- Официальная поддержка от Yandex Cloud
- Автоматическая обработка авторизации (API Key, IAM Token, OAuth)
- Единый интерфейс для всех моделей (YandexGPT, Qwen, DeepSeek и др.)
- Встроенная поддержка streaming и async
- Embeddings API из коробки
- Корректное определение endpoint для каждого типа модели

---

## Фаза 1: Добавление SDK и рефакторинг провайдеров

### 1.1 Добавить зависимость

**Файл:** `pyproject.toml`

```toml
dependencies = [
    ...
    "yandex-cloud-ml-sdk>=0.17.0",
]
```

### 1.2 Создать конфигурацию провайдеров

**Новый файл:** `src/obsidian_kb/providers/provider_config.py`

```python
"""Конфигурация провайдеров с учётом их производительности."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    """Конфигурация провайдера."""
    max_concurrent: int          # Максимум параллельных запросов для embeddings
    batch_size: int              # Размер батча для embeddings
    enrichment_concurrent: int   # Максимум параллельных LLM запросов для enrichment
    rate_limit_rps: int | None   # Rate limit (requests per second), None = без лимита
    timeout: int                 # Таймаут запросов в секундах


# Пресеты для провайдеров
PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "ollama": ProviderConfig(
        max_concurrent=10,
        batch_size=32,
        enrichment_concurrent=5,
        rate_limit_rps=15,
        timeout=60,
    ),
    "yandex": ProviderConfig(
        max_concurrent=50,       # Yandex поддерживает больше параллельных запросов
        batch_size=100,          # Больший batch для embeddings
        enrichment_concurrent=20, # Больше параллельных LLM запросов
        rate_limit_rps=100,      # Высокий rate limit
        timeout=30,              # Меньший таймаут (облако быстрее)
    ),
}


def get_provider_config(provider_name: str) -> ProviderConfig:
    """Получить конфигурацию провайдера.

    Args:
        provider_name: Имя провайдера (ollama, yandex)

    Returns:
        Конфигурация провайдера (fallback на ollama если не найден)
    """
    return PROVIDER_CONFIGS.get(provider_name.lower(), PROVIDER_CONFIGS["ollama"])
```

### 1.3 Рефакторинг YandexChatProvider

**Файл:** `src/obsidian_kb/providers/yandex/chat_provider.py`

Заменить реализацию на использование SDK:

```python
"""Yandex Cloud провайдер для chat completion через ML SDK."""

import asyncio
import logging
import time
from typing import Any

from yandex_cloud_ml_sdk import AsyncYCloudML

from obsidian_kb.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.interfaces import ProviderHealth
from obsidian_kb.providers.provider_config import get_provider_config

logger = logging.getLogger(__name__)


class YandexChatProvider:
    """Провайдер chat completion через Yandex Cloud ML SDK.

    Поддерживает все модели Yandex Cloud AI Studio:
    - yandexgpt/latest, yandexgpt-lite/latest, yandexgpt-pro/latest
    - qwen3-235b-a22b-fp8/latest, qwen3-235b-a22b/latest
    - deepseek-r1/latest, gpt-oss-120b/latest
    - И другие модели из каталога AI Studio
    """

    def __init__(
        self,
        folder_id: str,
        api_key: str,
        model: str = "yandexgpt/latest",
        timeout: int | None = None,
        instance_id: str | None = None,  # Для обратной совместимости
    ) -> None:
        if not folder_id:
            raise ValueError("folder_id is required for Yandex provider")
        if not api_key:
            raise ValueError("api_key is required for Yandex provider")

        self._folder_id = folder_id
        self._api_key = api_key
        self._model_name = model
        self._instance_id = instance_id

        # Получаем конфигурацию провайдера
        config = get_provider_config("yandex")
        self._timeout = timeout or config.timeout

        # Инициализация SDK
        self._sdk = AsyncYCloudML(folder_id=folder_id, auth=api_key)

        # Semaphore для ограничения параллелизма
        self._semaphore = asyncio.Semaphore(config.enrichment_concurrent)

    @property
    def name(self) -> str:
        return "yandex"

    @property
    def model(self) -> str:
        return self._model_name

    def _get_model_id(self) -> str:
        """Получить ID модели для SDK.

        SDK принимает короткое имя модели (например, 'yandexgpt/latest')
        и сам формирует правильный URI.
        """
        if self._instance_id:
            # Dedicated instance
            return f"yandexgpt/{self._instance_id}"
        return self._model_name

    async def health_check(self) -> ProviderHealth:
        """Проверка доступности Yandex Cloud API."""
        start_time = time.time()
        try:
            model = self._sdk.models.completions(self._get_model_id())
            model = model.configure(temperature=0.1, max_tokens=10)

            result = await model.run("test")
            latency_ms = (time.time() - start_time) * 1000

            if result and result.alternatives:
                return ProviderHealth(
                    available=True,
                    latency_ms=latency_ms,
                    model=self._model_name,
                )
            else:
                return ProviderHealth(
                    available=False,
                    latency_ms=latency_ms,
                    error="Empty response from model",
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            if "401" in error_msg or "authentication" in error_msg.lower():
                return ProviderHealth(
                    available=False,
                    latency_ms=latency_ms,
                    error="Authentication failed (invalid API key)",
                )
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                return ProviderHealth(
                    available=False,
                    latency_ms=latency_ms,
                    error="Access denied (check folder_id and permissions)",
                )
            else:
                return ProviderHealth(
                    available=False,
                    latency_ms=latency_ms,
                    error=f"Error: {error_msg[:100]}",
                )

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Генерация ответа на основе сообщений."""
        if not messages:
            raise ValueError("Messages cannot be empty")

        async with self._semaphore:
            try:
                # Получаем модель и конфигурируем
                model = self._sdk.models.completions(self._get_model_id())
                model = model.configure(temperature=max(0.0, min(1.0, temperature)))

                if max_tokens is not None:
                    model = model.configure(max_tokens=max_tokens)

                # Конвертируем сообщения в формат SDK
                sdk_messages = self._convert_messages(messages)

                # Вызываем модель
                result = await asyncio.wait_for(
                    model.run(sdk_messages),
                    timeout=self._timeout,
                )

                if not result or not result.alternatives:
                    raise ProviderError("Empty response from Yandex API")

                # Извлекаем текст из первой альтернативы
                content = result.alternatives[0].text
                if not content:
                    raise ProviderError("Empty content in Yandex API response")

                return content

            except asyncio.TimeoutError:
                raise ProviderTimeoutError("Yandex API request timeout")
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg:
                    raise ProviderAuthenticationError(f"Yandex API authentication failed: {e}")
                elif "403" in error_msg:
                    raise ProviderAuthenticationError(f"Yandex API access denied: {e}")
                elif "429" in error_msg:
                    raise ProviderError(f"Yandex API rate limit exceeded: {e}")
                else:
                    raise ProviderConnectionError(f"Yandex API error: {e}") from e

    def _convert_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """Конвертация сообщений в формат SDK.

        SDK принимает список dict с ключами 'role' и 'text'.
        """
        sdk_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "") or msg.get("text", "")

            if role not in ("system", "user", "assistant"):
                role = "user"

            sdk_messages.append({"role": role, "text": content})

        return sdk_messages
```

### 1.4 Обновить config.py (настройки провайдеров)

**Файл:** `src/obsidian_kb/config.py`

Добавить новые настройки:

```python
class Settings(BaseSettings):
    # ... существующие настройки ...

    # === Provider-specific Performance Settings ===

    # Ollama (локальный, умеренная скорость)
    ollama_max_concurrent: int = 10
    ollama_batch_size: int = 32
    ollama_enrichment_concurrent: int = 5

    # Yandex Cloud (облако, высокая скорость)
    yandex_max_concurrent: int = 50
    yandex_batch_size: int = 100
    yandex_enrichment_concurrent: int = 20
    yandex_timeout: int = 30
```

### 1.5 Обновить __init__.py

**Файл:** `src/obsidian_kb/providers/__init__.py`

Добавить экспорт:

```python
from obsidian_kb.providers.provider_config import (
    ProviderConfig,
    PROVIDER_CONFIGS,
    get_provider_config,
)
```

---

## Фаза 2: Интеграция с enrichment (следующий этап)

После успешного завершения Фазы 1:
- Обновить `LLMEnrichmentService` для использования провайдера
- Обновить `FullEnrichmentStrategy` для использования `IChatCompletionProvider`
- Добавить автоматический выбор параллелизма на основе провайдера

---

## Фаза 3: Рефакторинг embeddings (опционально)

- Рефакторинг `YandexEmbeddingProvider` на SDK
- Использование `sdk.models.text_embeddings()`

---

## Тестирование

### Unit тесты

```python
# tests/unit/providers/yandex/test_chat_provider_sdk.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from obsidian_kb.providers.yandex.chat_provider import YandexChatProvider


@pytest.fixture
def mock_sdk():
    with patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML") as mock:
        yield mock


@pytest.mark.asyncio
async def test_complete_with_qwen_model(mock_sdk):
    """Тест chat completion с моделью Qwen."""
    # Arrange
    mock_result = MagicMock()
    mock_result.alternatives = [MagicMock(text="Test response")]

    mock_model = AsyncMock()
    mock_model.configure.return_value = mock_model
    mock_model.run.return_value = mock_result

    mock_sdk.return_value.models.completions.return_value = mock_model

    provider = YandexChatProvider(
        folder_id="test_folder",
        api_key="test_key",
        model="qwen3-235b-a22b-fp8/latest",
    )

    # Act
    result = await provider.complete([{"role": "user", "content": "Hello"}])

    # Assert
    assert result == "Test response"
    mock_sdk.return_value.models.completions.assert_called_once_with("qwen3-235b-a22b-fp8/latest")


@pytest.mark.asyncio
async def test_health_check_success(mock_sdk):
    """Тест успешного health check."""
    mock_result = MagicMock()
    mock_result.alternatives = [MagicMock(text="ok")]

    mock_model = AsyncMock()
    mock_model.configure.return_value = mock_model
    mock_model.run.return_value = mock_result

    mock_sdk.return_value.models.completions.return_value = mock_model

    provider = YandexChatProvider(
        folder_id="test_folder",
        api_key="test_key",
        model="yandexgpt/latest",
    )

    health = await provider.health_check()

    assert health.available is True
    assert health.model == "yandexgpt/latest"
```

### Интеграционные тесты

```python
# tests/integration/providers/test_yandex_integration.py

import pytest
import os

from obsidian_kb.providers.yandex.chat_provider import YandexChatProvider


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("OBSIDIAN_KB_YANDEX_API_KEY"),
    reason="Yandex credentials not configured"
)
async def test_real_yandex_chat():
    """Интеграционный тест с реальным Yandex API."""
    provider = YandexChatProvider(
        folder_id=os.environ["OBSIDIAN_KB_YANDEX_FOLDER_ID"],
        api_key=os.environ["OBSIDIAN_KB_YANDEX_API_KEY"],
        model="qwen3-235b-a22b-fp8/latest",
    )

    result = await provider.complete([
        {"role": "user", "content": "Скажи 'тест' одним словом"}
    ])

    assert "тест" in result.lower()
```

---

## Чеклист Фазы 1

- [ ] Добавить `yandex-cloud-ml-sdk>=0.17.0` в `pyproject.toml`
- [ ] Создать `src/obsidian_kb/providers/provider_config.py`
- [ ] Рефакторинг `src/obsidian_kb/providers/yandex/chat_provider.py`
- [ ] Обновить `src/obsidian_kb/providers/__init__.py`
- [ ] Добавить настройки в `src/obsidian_kb/config.py`
- [ ] Написать unit тесты для нового провайдера
- [ ] Запустить все 745 тестов: `.venv/bin/pytest tests/ -v`
- [ ] Проверить вручную через MCP: `test_provider("yandex")`

---

## Ссылки

- [yandex-cloud-ml-sdk на PyPI](https://pypi.org/project/yandex-cloud-ml-sdk/)
- [GitHub yandex-cloud-ml-sdk](https://github.com/yandex-cloud/yandex-cloud-ml-sdk)
- [Yandex AI Studio Models](https://yandex.cloud/en/docs/ai-studio/concepts/generation/)
- [SDK Documentation](https://yandex.cloud/en/docs/ai-studio/sdk/)
