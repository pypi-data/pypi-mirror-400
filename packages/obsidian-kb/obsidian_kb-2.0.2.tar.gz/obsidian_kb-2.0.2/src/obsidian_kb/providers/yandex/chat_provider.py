"""Yandex Cloud провайдер для chat completion.

Использует:
- yandex-cloud-ml-sdk (gRPC) для YandexGPT моделей
- OpenAI-compatible HTTP API для open source моделей

Документация:
- SDK: https://yandex.cloud/en/docs/ai-studio/sdk/
- Модели: https://yandex.cloud/ru/docs/ai-studio/concepts/generation/models
- OpenAI API: https://yandex.cloud/ru/docs/ai-studio/concepts/openai-compatibility

Список поддерживаемых моделей см. в models.py (реестр YANDEX_CHAT_MODELS).
"""

import asyncio
import logging
import time
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout
from yandex_cloud_ml_sdk import AsyncYCloudML

from obsidian_kb.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.interfaces import ProviderHealth
from obsidian_kb.providers.provider_config import get_provider_config
from obsidian_kb.providers.rate_limiter import AdaptiveRateLimiter
from obsidian_kb.providers.yandex.models import get_yandex_model

logger = logging.getLogger(__name__)

# OpenAI-compatible API endpoint для open source моделей
YANDEX_OPENAI_API_URL = "https://llm.api.cloud.yandex.net/v1/chat/completions"


class YandexChatProvider:
    """Провайдер chat completion для Yandex Cloud AI Studio.

    Поддерживает все модели Yandex Cloud AI Studio:
    - YandexGPT модели (через SDK/gRPC): yandexgpt, yandexgpt-lite, yandexgpt/rc, aliceai-llm
    - Open source модели (через HTTP): qwen3-235b-a22b-fp8, gpt-oss-120b, gpt-oss-20b, gemma-3-27b-it
    """

    def __init__(
        self,
        folder_id: str,
        api_key: str,
        model: str = "yandexgpt/latest",
        timeout: int | None = None,
        instance_id: str | None = None,
    ) -> None:
        """Инициализация провайдера.

        Args:
            folder_id: ID папки в Yandex Cloud
            api_key: IAM токен или API ключ сервисного аккаунта
            model: Название модели (например 'yandexgpt/latest' или 'qwen3-235b-a22b-fp8')
            timeout: Таймаут запросов в секундах
            instance_id: ID dedicated instance (опционально)
        """
        if not folder_id:
            raise ValueError("folder_id is required for Yandex provider")
        if not api_key:
            raise ValueError("api_key is required for Yandex provider")

        self._folder_id = folder_id
        self._api_key = api_key
        self._model_name = model
        self._instance_id = instance_id

        config = get_provider_config("yandex")
        self._timeout = timeout or config.timeout
        self._config = config

        # SDK для YandexGPT моделей (gRPC)
        self._sdk = AsyncYCloudML(folder_id=folder_id, auth=api_key)

        # HTTP сессия для OpenAI-compatible API (создаётся лениво)
        self._http_session: aiohttp.ClientSession | None = None

        # Адаптивный rate limiter
        initial_rps = float(config.rate_limit_rps or 20)
        max_rps = config.rate_limit_max_rps or initial_rps
        self._rate_limiter = AdaptiveRateLimiter(
            initial_rps=initial_rps,
            max_rps=max_rps,
            min_rps=config.rate_limit_min_rps,
            recovery_threshold=config.rate_limit_recovery,
            enabled=config.adaptive_rate_limit,
        )

    @property
    def name(self) -> str:
        """Имя провайдера."""
        return "yandex"

    @property
    def model(self) -> str:
        """Название модели."""
        return self._model_name

    def _is_openai_compatible_model(self) -> bool:
        """Проверка, требует ли модель OpenAI-compatible HTTP API.

        Использует реестр моделей из models.py для определения типа API.
        Если модель не найдена в реестре, использует эвристику по префиксу.
        """
        # Сначала проверяем в реестре моделей
        model_info = get_yandex_model(self._model_name)
        if model_info:
            return model_info.api_type == "openai"

        # Fallback: эвристика по префиксу для неизвестных моделей
        model_lower = self._model_name.lower()
        openai_prefixes = ("gpt-oss-", "qwen", "gemma")
        return any(model_lower.startswith(prefix) for prefix in openai_prefixes)

    def _get_model_id(self) -> str:
        """Получить ID модели для SDK (gRPC).

        SDK принимает короткое имя модели и сам добавляет '/latest'.
        """
        if self._instance_id:
            return f"yandexgpt/{self._instance_id}"

        model_id = self._model_name
        if model_id.endswith("/latest"):
            model_id = model_id[:-7]

        return model_id

    def _build_model_uri(self) -> str:
        """Построение URI модели для OpenAI-compatible API."""
        model_name = self._model_name
        if model_name.endswith("/latest"):
            model_name = model_name[:-7]

        return f"gpt://{self._folder_id}/{model_name}/latest"

    async def _get_http_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии для OpenAI API."""
        if self._http_session is None or self._http_session.closed:
            self._http_session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=self._timeout),
                headers={
                    "Authorization": f"Api-Key {self._api_key}",
                    "x-folder-id": self._folder_id,
                    "Content-Type": "application/json",
                },
            )
        return self._http_session

    async def close(self) -> None:
        """Закрытие HTTP сессии."""
        if self._http_session and not self._http_session.closed:
            await self._http_session.close()

    async def health_check(self) -> ProviderHealth:
        """Проверка доступности Yandex Cloud API."""
        start_time = time.time()

        if self._is_openai_compatible_model():
            return await self._health_check_http(start_time)
        else:
            return await self._health_check_grpc(start_time)

    async def _health_check_grpc(self, start_time: float) -> ProviderHealth:
        """Health check через SDK (gRPC)."""
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
            return self._handle_health_check_error(e, start_time)

    async def _health_check_http(self, start_time: float) -> ProviderHealth:
        """Health check через OpenAI-compatible API."""
        try:
            session = await self._get_http_session()
            payload = {
                "model": self._build_model_uri(),
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10,
                "temperature": 0.1,
            }

            async with session.post(YANDEX_OPENAI_API_URL, json=payload) as resp:
                latency_ms = (time.time() - start_time) * 1000

                if resp.status == 200:
                    return ProviderHealth(
                        available=True,
                        latency_ms=latency_ms,
                        model=self._model_name,
                    )
                elif resp.status == 401:
                    return ProviderHealth(
                        available=False,
                        latency_ms=latency_ms,
                        error="Authentication failed (invalid API key)",
                    )
                elif resp.status == 403:
                    return ProviderHealth(
                        available=False,
                        latency_ms=latency_ms,
                        error="Access denied (check folder_id and permissions)",
                    )
                else:
                    error_text = await resp.text()
                    return ProviderHealth(
                        available=False,
                        latency_ms=latency_ms,
                        error=f"HTTP {resp.status}: {error_text[:100]}",
                    )

        except Exception as e:
            return self._handle_health_check_error(e, start_time)

    def _handle_health_check_error(self, e: Exception, start_time: float) -> ProviderHealth:
        """Обработка ошибок health check."""
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
        """Генерация ответа на основе сообщений.

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов в ответе

        Returns:
            Сгенерированный текст

        Raises:
            ProviderError: При ошибке генерации
        """
        if not messages:
            raise ValueError("Messages cannot be empty")

        if self._is_openai_compatible_model():
            return await self._complete_http(messages, temperature, max_tokens)
        else:
            return await self._complete_grpc(messages, temperature, max_tokens)

    async def _complete_grpc(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Генерация через SDK (gRPC) для YandexGPT моделей."""
        async with self._rate_limiter:
            try:
                model = self._sdk.models.completions(self._get_model_id())
                model = model.configure(temperature=max(0.0, min(1.0, temperature)))

                if max_tokens is not None:
                    model = model.configure(max_tokens=max_tokens)

                sdk_messages = self._convert_messages_for_grpc(messages)

                result = await asyncio.wait_for(
                    model.run(sdk_messages),
                    timeout=self._timeout,
                )

                if not result or not result.alternatives:
                    raise ProviderError("Empty response from Yandex API")

                content = result.alternatives[0].text
                if not content:
                    raise ProviderError("Empty content in Yandex API response")

                self._rate_limiter.record_success()
                return content

            except asyncio.TimeoutError:
                raise ProviderTimeoutError("Yandex API request timeout")
            except (ProviderError, ProviderTimeoutError, ProviderRateLimitError):
                raise
            except Exception as e:
                self._handle_api_error(e)

    async def _complete_http(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Генерация через OpenAI-compatible API для open source моделей."""
        async with self._rate_limiter:
            try:
                session = await self._get_http_session()

                openai_messages = self._convert_messages_for_http(messages)

                payload: dict[str, Any] = {
                    "model": self._build_model_uri(),
                    "messages": openai_messages,
                    "temperature": max(0.0, min(1.0, temperature)),
                }

                if max_tokens is not None:
                    payload["max_tokens"] = max_tokens

                async with session.post(YANDEX_OPENAI_API_URL, json=payload) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        choices = response.get("choices", [])
                        if not choices:
                            raise ProviderError("Empty response from Yandex OpenAI API")

                        message = choices[0].get("message", {})
                        content = message.get("content", "")

                        # Некоторые модели (DeepSeek) возвращают reasoning_content
                        if not content:
                            content = message.get("reasoning_content", "")

                        if not content:
                            raise ProviderError("Empty content in Yandex OpenAI API response")

                        self._rate_limiter.record_success()
                        return content
                    else:
                        error_text = await resp.text()
                        self._handle_http_error(resp.status, error_text)

            except asyncio.TimeoutError:
                raise ProviderTimeoutError("Yandex API request timeout")
            except ClientError as e:
                raise ProviderConnectionError(f"Yandex API connection error: {e}") from e
            except (ProviderError, ProviderTimeoutError, ProviderAuthenticationError, ProviderRateLimitError):
                raise
            except Exception as e:
                raise ProviderConnectionError(f"Yandex API error: {e}") from e

    def _convert_messages_for_grpc(
        self, messages: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Конвертация сообщений для SDK (gRPC). Формат: role + text."""
        sdk_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "") or msg.get("text", "")

            if role not in ("system", "user", "assistant"):
                role = "user"

            sdk_messages.append({"role": role, "text": content})

        return sdk_messages

    def _convert_messages_for_http(
        self, messages: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Конвертация сообщений для OpenAI API. Формат: role + content."""
        openai_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "") or msg.get("text", "")

            if role not in ("system", "user", "assistant"):
                role = "user"

            openai_messages.append({"role": role, "content": content})

        return openai_messages

    def _handle_api_error(self, e: Exception) -> None:
        """Обработка ошибок gRPC API."""
        error_msg = str(e)
        if "401" in error_msg:
            raise ProviderAuthenticationError(f"Yandex API authentication failed: {e}")
        elif "403" in error_msg:
            raise ProviderAuthenticationError(f"Yandex API access denied: {e}")
        elif "429" in error_msg:
            self._rate_limiter.record_rate_limit()
            raise ProviderRateLimitError(f"Yandex API rate limit exceeded: {e}")
        else:
            raise ProviderConnectionError(f"Yandex API error: {e}") from e

    def _handle_http_error(self, status: int, error_text: str) -> None:
        """Обработка HTTP ошибок."""
        if status == 401:
            raise ProviderAuthenticationError(f"Yandex API authentication failed: {error_text}")
        elif status == 403:
            raise ProviderAuthenticationError(f"Yandex API access denied: {error_text}")
        elif status == 429:
            self._rate_limiter.record_rate_limit()
            raise ProviderRateLimitError(f"Yandex API rate limit exceeded: {error_text}")
        else:
            raise ProviderConnectionError(f"Yandex API returned status {status}: {error_text}")
