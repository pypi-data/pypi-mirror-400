"""Ollama провайдер для embeddings."""

import asyncio
import logging
import time
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout, TCPConnector

from obsidian_kb.config import settings
from obsidian_kb.providers.exceptions import (
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.interfaces import IEmbeddingProvider, ProviderHealth
from obsidian_kb.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider:
    """Провайдер embeddings через Ollama.
    
    Реализует IEmbeddingProvider протокол.
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
        self._model = model or settings.embedding_model
        self._timeout = ClientTimeout(total=timeout or settings.embedding_timeout)
        self._session: aiohttp.ClientSession | None = None
        
        # TCPConnector с connection pool
        self._connector = TCPConnector(
            limit=settings.ollama_connector_limit,
            limit_per_host=settings.ollama_connector_limit_per_host,
        )
        
        # Rate Limiter для Ollama (если включен)
        self._rate_limiter: RateLimiter | None = None
        if settings.ollama_rate_limit_enabled:
            self._rate_limiter = RateLimiter(
                max_requests=settings.ollama_rate_limit_max_requests,
                window_seconds=settings.ollama_rate_limit_window_seconds,
                name="OllamaRateLimiter",
            )
        
        # Semaphore для ограничения параллелизма
        self._semaphore = asyncio.Semaphore(settings.ollama_max_concurrent)
    
    @property
    def name(self) -> str:
        """Имя провайдера."""
        return "ollama"
    
    @property
    def model(self) -> str:
        """Название модели."""
        return self._model
    
    @property
    def dimensions(self) -> int:
        """Размерность векторов."""
        return settings.embedding_dimensions
    
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
                                dimensions=self.dimensions,
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
    
    async def get_embedding(self, text: str, embedding_type: str = "doc") -> list[float]:
        """Получение embedding для одного текста."""
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Обрезаем текст до безопасного лимита
        MAX_TEXT_LENGTH = 6000
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
            logger.debug(f"Text truncated to {MAX_TEXT_LENGTH} characters")
        
        async with self._semaphore:
            if self._rate_limiter:
                await self._rate_limiter.acquire()
            
            session = await self._get_session()
            url = f"{self._base_url}/api/embeddings"
            payload = {"model": self._model, "prompt": text}
            
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        embedding = response.get("embedding", [])
                        
                        if not embedding:
                            raise ProviderError("Empty embedding returned from Ollama")
                        
                        if len(embedding) != self.dimensions:
                            logger.warning(
                                f"Embedding dimension mismatch: expected {self.dimensions}, "
                                f"got {len(embedding)}"
                            )
                        
                        return embedding
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
    
    async def get_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        embedding_type: str = "doc",
    ) -> list[list[float]]:
        """Батчевая генерация embeddings.
        
        Ollama не поддерживает батчинг напрямую, поэтому делаем параллельные запросы.
        """
        if not texts:
            return []
        
        non_empty_texts = [t for t in texts if t.strip()]
        if not non_empty_texts:
            raise ValueError("All texts are empty")
        
        # Используем batch_size из settings если не указан
        effective_batch_size = batch_size or settings.batch_size
        
        all_embeddings: list[list[float]] = []
        
        for i in range(0, len(non_empty_texts), effective_batch_size):
            batch = non_empty_texts[i : i + effective_batch_size]
            logger.debug(f"Processing embedding batch {i // effective_batch_size + 1} ({len(batch)} texts)")
            
            # Параллельные запросы
            tasks = [self.get_embedding(text, embedding_type=embedding_type) for text in batch]
            batch_embeddings = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            for result in batch_embeddings:
                if isinstance(result, Exception):
                    logger.error(f"Error getting embedding: {result}")
                    # Возвращаем нулевой вектор в случае ошибки
                    all_embeddings.append([0.0] * self.dimensions)
                elif isinstance(result, list):
                    all_embeddings.append(result)
                else:
                    logger.warning(f"Unexpected result type: {type(result)}, using zero vector")
                    all_embeddings.append([0.0] * self.dimensions)
        
        # Восстанавливаем порядок с учётом пустых текстов
        result_embeddings: list[list[float]] = []
        text_idx = 0
        
        for text in texts:
            if text.strip():
                result_embeddings.append(all_embeddings[text_idx])
                text_idx += 1
            else:
                result_embeddings.append([0.0] * self.dimensions)
        
        return result_embeddings

