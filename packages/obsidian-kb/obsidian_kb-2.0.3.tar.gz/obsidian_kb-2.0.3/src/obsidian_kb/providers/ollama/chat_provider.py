"""Ollama провайдер для chat completion."""

import asyncio
import logging
import time

import aiohttp
from aiohttp import ClientError, ClientTimeout, TCPConnector

from obsidian_kb.config import settings
from obsidian_kb.providers.exceptions import (
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.interfaces import IChatCompletionProvider, ProviderHealth

logger = logging.getLogger(__name__)


class OllamaChatProvider:
    """Провайдер chat completion через Ollama.
    
    Реализует IChatCompletionProvider протокол.
    """
    
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Инициализация провайдера.
        
        Args:
            base_url: Базовый URL Ollama (по умолчанию из settings)
            model: Название модели (по умолчанию из settings)
            timeout: Таймаут запросов в секундах
        """
        self._base_url = (base_url or settings.ollama_url).rstrip("/")
        self._model = model or settings.llm_model
        self._timeout = ClientTimeout(total=timeout or settings.llm_timeout)
        self._session: aiohttp.ClientSession | None = None
        
        # TCPConnector с connection pool
        self._connector = TCPConnector(
            limit=settings.ollama_connector_limit,
            limit_per_host=settings.ollama_connector_limit_per_host,
        )
        
        # Semaphore для ограничения параллелизма
        self._semaphore = asyncio.Semaphore(settings.llm_max_concurrent)
    
    @property
    def name(self) -> str:
        """Имя провайдера."""
        return "ollama"
    
    @property
    def model(self) -> str:
        """Название модели."""
        return self._model
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                connector=self._connector,
            )
        return self._session
    
    async def close(self) -> None:
        """Закрытие HTTP сессии и connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()
    
    async def health_check(self) -> ProviderHealth:
        """Проверка доступности Ollama."""
        start_time = time.time()
        try:
            timeout = ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self._base_url}/api/tags") as resp:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m["name"] for m in data.get("models", [])]
                        model_found = self._model in models
                        
                        if not model_found:
                            # Проверяем совпадение с версией
                            model_base = self._model.split(":")[0] if ":" in self._model else self._model
                            matching_models = [
                                m for m in models
                                if m.startswith(f"{model_base}:") or m == model_base
                            ]
                            if matching_models:
                                self._model = matching_models[0]
                                model_found = True
                        
                        if model_found:
                            return ProviderHealth(
                                available=True,
                                latency_ms=latency_ms,
                                model=self._model,
                            )
                        else:
                            return ProviderHealth(
                                available=False,
                                latency_ms=latency_ms,
                                error=f"Model {self._model} not found",
                                model=self._model,
                            )
                    else:
                        return ProviderHealth(
                            available=False,
                            latency_ms=latency_ms,
                            error=f"HTTP {resp.status}",
                        )
        except asyncio.TimeoutError:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error="Timeout (10s)",
            )
        except ClientError as e:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error=f"Connection error: {e}",
            )
        except Exception as e:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error=f"Unexpected error: {e}",
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
            temperature: Температура генерации (0.0-2.0)
            max_tokens: Максимальное количество токенов в ответе (для Ollama это num_predict)
            
        Returns:
            Сгенерированный текст
            
        Raises:
            ProviderError: При ошибке генерации
        """
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        async with self._semaphore:
            session = await self._get_session()
            url = f"{self._base_url}/api/chat"
            
            # Формируем payload для Ollama
            payload = {
                "model": self._model,
                "messages": messages,
                "stream": False,
            }
            
            # Ollama использует options для параметров
            options: dict[str, Any] = {
                "temperature": temperature,
            }
            if max_tokens is not None:
                options["num_predict"] = max_tokens
            
            if options:
                payload["options"] = options
            
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        message = response.get("message", {})
                        content = message.get("content", "")
                        
                        if not content:
                            raise ProviderError("Empty response from Ollama")
                        
                        return content
                    elif resp.status == 404:
                        error_text = await resp.text()
                        raise ProviderError(f"Model not found: {error_text}")
                    else:
                        error_text = await resp.text()
                        raise ProviderConnectionError(
                            f"Ollama returned status {resp.status}: {error_text}"
                        )
            except asyncio.TimeoutError:
                raise ProviderTimeoutError("Ollama request timeout")
            except ClientError as e:
                raise ProviderConnectionError(f"Ollama connection error: {e}") from e

