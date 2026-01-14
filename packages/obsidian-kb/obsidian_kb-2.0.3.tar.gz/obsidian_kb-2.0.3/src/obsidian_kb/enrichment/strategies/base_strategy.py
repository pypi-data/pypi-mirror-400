"""Базовый класс для стратегий обогащения чанков.

DEPRECATED: Этот класс устарел и будет удалён в v1.0.0.
Используйте FullEnrichmentStrategy или FastEnrichmentStrategy с IChatCompletionProvider.

Причина: класс жёстко привязан к Ollama HTTP API.
Новые стратегии используют IChatCompletionProvider для поддержки любых провайдеров.
"""

import asyncio
import hashlib
import json
import logging
import re
import warnings
from abc import ABC, abstractmethod
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout, TCPConnector

from obsidian_kb.config import settings
from obsidian_kb.providers.exceptions import ProviderConnectionError
from obsidian_kb.types import ChunkEnrichment, DocumentChunk

logger = logging.getLogger(__name__)


class BaseEnrichmentStrategy(ABC):
    """Базовый класс для стратегий обогащения чанков через LLM.

    DEPRECATED: Этот класс устарел. Используйте FullEnrichmentStrategy или
    FastEnrichmentStrategy с IChatCompletionProvider вместо наследования от этого класса.

    Предоставляет общую функциональность:
    - Управление HTTP сессиями с retry logic
    - Вычисление content hash
    - Парсинг JSON ответов LLM с fallback-стратегиями
    - Очистка ответов от markdown и других артефактов

    Наследники должны реализовать:
    - enrich(chunk) -> ChunkEnrichment
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        connector_limit: int | None = None,
        connector_limit_per_host: int | None = None,
    ) -> None:
        """Инициализация базовой стратегии.

        Args:
            base_url: Базовый URL Ollama (по умолчанию из settings)
            model: Название модели (по умолчанию из settings.llm_model)
            timeout: Таймаут запросов в секундах (по умолчанию из settings.llm_timeout)
            connector_limit: Лимит соединений для TCPConnector
            connector_limit_per_host: Лимит соединений на хост
        """
        warnings.warn(
            "BaseEnrichmentStrategy is deprecated. Use FullEnrichmentStrategy or "
            "FastEnrichmentStrategy with IChatCompletionProvider instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.llm_model
        self.timeout = ClientTimeout(total=timeout or settings.llm_timeout)
        self._session: aiohttp.ClientSession | None = None

        # TCPConnector с connection pool
        self._connector = TCPConnector(
            limit=connector_limit or settings.ollama_connector_limit,
            limit_per_host=connector_limit_per_host
            or settings.ollama_connector_limit_per_host,
        )

    async def _get_session(self, force_recreate: bool = False) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии.

        Args:
            force_recreate: Принудительно пересоздать сессию

        Returns:
            aiohttp.ClientSession
        """
        # Закрываем старую сессию если нужно пересоздать
        if force_recreate and self._session:
            try:
                if not self._session.closed:
                    await self._session.close()
            except Exception as e:
                logger.debug(f"Error closing session: {e}")
            finally:
                self._session = None

        # Проверяем и пересоздаем сессию если нужно
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=self._connector,
            )
        elif self._session.closed:
            # Сессия закрыта, пересоздаем
            logger.debug("Session is closed, recreating...")
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=self._connector,
            )

        return self._session

    async def close(self) -> None:
        """Закрытие HTTP сессии и connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Вычисление SHA256 hash контента.

        Args:
            content: Контент для хеширования

        Returns:
            SHA256 hash в hex формате
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def _extract_json_from_response(self, response_text: str) -> dict[str, Any] | None:
        """Извлечение JSON из ответа LLM с несколькими стратегиями.

        Args:
            response_text: Текст ответа от LLM

        Returns:
            Распарсенный JSON или None если не удалось
        """
        raw_response = response_text.strip()

        # Стратегия 1: Прямой парсинг (если ответ чистый JSON)
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            pass

        # Стратегия 2: Извлечение из markdown code block
        code_block_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", raw_response, re.DOTALL
        )
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # Стратегия 3: Поиск JSON-объекта в тексте (greedy)
        json_match = re.search(
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw_response, re.DOTALL
        )
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Стратегия 4: Очистка и исправление common issues
        cleaned = raw_response

        # Удаление trailing commas: ,] → ] и ,} → }
        cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)

        # Замена одинарных кавычек на двойные (осторожно!)
        if cleaned.startswith("{") or cleaned.startswith("["):
            cleaned = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', cleaned)
            cleaned = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    def _extract_text_from_response(self, response_text: str) -> str:
        """Извлечение чистого текста из ответа LLM (удаление markdown обёрток).

        Args:
            response_text: Текст ответа от LLM

        Returns:
            Очищенный текст
        """
        fallback_text = response_text.strip()

        if "```" in fallback_text:
            lines = fallback_text.split("\n")
            start_idx = 0
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    if start_idx == 0:
                        start_idx = i + 1
                    else:
                        end_idx = i
                        break
            if start_idx < end_idx:
                fallback_text = "\n".join(lines[start_idx:end_idx]).strip()

        return fallback_text.strip()

    async def _call_ollama_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        num_predict: int = 512,
        json_format: bool = True,
    ) -> str:
        """Вызов Ollama /api/chat endpoint с retry logic.

        Args:
            messages: Список сообщений для чата
            temperature: Температура генерации
            num_predict: Максимальное количество токенов в ответе
            json_format: Использовать JSON режим

        Returns:
            Текст ответа от LLM

        Raises:
            ProviderConnectionError: При ошибке подключения к LLM
        """
        url = f"{self.base_url}/api/chat"

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
        }

        if json_format:
            payload["format"] = "json"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                session = await self._get_session(force_recreate=(attempt > 0))

                # Дополнительная проверка перед использованием
                if session.closed:
                    logger.warning(
                        f"Session closed before request (attempt {attempt + 1}), "
                        "recreating..."
                    )
                    session = await self._get_session(force_recreate=True)

                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        # Извлекаем ответ из структуры Ollama
                        message = data.get("message", {})
                        response_text = message.get("content", "")

                        if not response_text:
                            raise ProviderConnectionError("Empty response from LLM")

                        return response_text

                    elif resp.status == 404:
                        error_text = await resp.text()
                        raise ProviderConnectionError(f"Model not found: {error_text}")
                    else:
                        error_text = await resp.text()
                        raise ProviderConnectionError(
                            f"Ollama returned status {resp.status}: {error_text}"
                        )

            except (ClientError, RuntimeError, asyncio.TimeoutError) as e:
                # Обрабатываем ошибки соединения и таймауты
                error_msg = str(e).lower()
                is_session_error = (
                    "session is closed" in error_msg
                    or "session closed" in error_msg
                    or isinstance(e, asyncio.TimeoutError)
                )

                if is_session_error and attempt < max_retries - 1:
                    logger.warning(
                        f"Session/connection error (attempt {attempt + 1}/{max_retries}): "
                        f"{e}. Recreating session and retrying..."
                    )
                    await self._get_session(force_recreate=True)
                    # Небольшая задержка перед повтором
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    # Последняя попытка или не session error
                    await self._get_session(force_recreate=True)
                    if isinstance(e, asyncio.TimeoutError):
                        raise ProviderConnectionError("LLM request timeout") from None
                    raise ProviderConnectionError(f"LLM connection error: {e}") from e
            except Exception as e:
                # Другие ошибки - не retry
                if isinstance(e, ProviderConnectionError):
                    raise
                await self._get_session(force_recreate=True)
                raise ProviderConnectionError(f"Unexpected error calling LLM: {e}") from e

        # Если дошли сюда, значит все попытки исчерпаны
        raise ProviderConnectionError("Failed to call LLM after multiple retries")

    @abstractmethod
    async def enrich(self, chunk: DocumentChunk) -> ChunkEnrichment:
        """Обогащение чанка через LLM.

        Args:
            chunk: Чанк для обогащения

        Returns:
            Обогащенные данные чанка

        Raises:
            ProviderConnectionError: При ошибке подключения к LLM
        """
        ...

    async def __aenter__(self) -> "BaseEnrichmentStrategy":
        """Вход в async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Выход из async context manager с закрытием ресурсов."""
        await self.close()
