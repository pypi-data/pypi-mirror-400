"""Yandex Cloud провайдер для embeddings.

Использует Yandex Cloud Foundation Models API для генерации embeddings.
API документация: https://cloud.yandex.ru/docs/foundation-models/concepts/embeddings
"""

import asyncio
import logging
import time
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout

from obsidian_kb.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.interfaces import IEmbeddingProvider, ProviderHealth
from obsidian_kb.providers.provider_config import get_provider_config
from obsidian_kb.providers.rate_limiter import AdaptiveRateLimiter

logger = logging.getLogger(__name__)

# Yandex Cloud Foundation Models API endpoint
YANDEX_API_BASE_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1"


class YandexEmbeddingProvider:
    """Провайдер embeddings через Yandex Cloud Foundation Models API.
    
    Поддерживает модели embeddings из Yandex Cloud AI Studio:
    - text-search-doc/latest (256 dimensions) - для документов
    - text-search-query/latest (256 dimensions) - для поисковых запросов
    
    Документация:
    - Embeddings: https://yandex.cloud/ru/docs/ai-studio/concepts/embeddings
    - Pricing: https://yandex.cloud/ru/docs/ai-studio/pricing
    """
    
    def __init__(
        self,
        folder_id: str,
        api_key: str,
        model: str | None = None,
        doc_model: str | None = None,
        query_model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Инициализация провайдера.
        
        Args:
            folder_id: ID папки в Yandex Cloud
            api_key: IAM токен или API ключ сервисного аккаунта
            model: Название модели (deprecated, используйте doc_model и query_model)
            doc_model: Модель для индексации документов (по умолчанию text-search-doc/latest)
            query_model: Модель для поисковых запросов (по умолчанию text-search-query/latest)
            timeout: Таймаут запросов в секундах
        """
        if not folder_id:
            raise ValueError("folder_id is required for Yandex provider")
        if not api_key:
            raise ValueError("api_key is required for Yandex provider")
        
        self._folder_id = folder_id
        self._api_key = api_key
        
        # Поддержка asymmetric embeddings
        # Если указан старый параметр model, используем его как doc_model для обратной совместимости
        if model and not doc_model:
            doc_model = model
        
        # Импортируем settings для получения значений по умолчанию
        from obsidian_kb.config import settings
        
        self._doc_model = doc_model or getattr(settings, "yandex_embedding_doc_model", "text-search-doc/latest")
        self._query_model = query_model or getattr(settings, "yandex_embedding_query_model", "text-search-query/latest")
        
        # Для обратной совместимости: _model указывает на doc_model
        self._model = self._doc_model
        
        config = get_provider_config("yandex")
        self._timeout = ClientTimeout(total=timeout or config.timeout)
        self._session: aiohttp.ClientSession | None = None
        self._config = config

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
        return self._model
    
    @property
    def dimensions(self) -> int:
        """Размерность векторов (256 для Yandex text-search моделей)."""
        return 256
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers={
                    "Authorization": f"Api-Key {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._session
    
    async def close(self) -> None:
        """Закрытие HTTP сессии."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _build_model_uri(self, model: str | None = None) -> str:
        """Построение URI модели для Yandex Embeddings API.
        
        Args:
            model: Название модели (по умолчанию self._doc_model)
        
        Returns:
            URI модели в формате emb://{folder_id}/{model}
        """
        model_name = model or self._doc_model
        return f"emb://{self._folder_id}/{model_name}"
    
    async def health_check(self) -> ProviderHealth:
        """Проверка доступности Yandex Cloud API."""
        start_time = time.time()
        try:
            # Делаем простой запрос для проверки доступности
            session = await self._get_session()
            url = f"{YANDEX_API_BASE_URL}/textEmbedding"
            
            # Минимальный тестовый запрос с правильным форматом
            payload = {
                "modelUri": self._build_model_uri(),
                "text": "test",
            }
            
            async with session.post(url, json=payload) as resp:
                latency_ms = (time.time() - start_time) * 1000
                
                if resp.status == 200:
                    # Показываем информацию о моделях (doc и query, если они разные)
                    model_info = self._model
                    if self._doc_model != self._query_model:
                        model_info = f"{self._doc_model} (doc) / {self._query_model} (query)"
                    
                    return ProviderHealth(
                        available=True,
                        latency_ms=latency_ms,
                        model=model_info,
                        dimensions=self.dimensions,
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
        except asyncio.TimeoutError:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error="Timeout",
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
        """Получение embedding для одного текста.
        
        Args:
            text: Текст для генерации embedding
            embedding_type: "doc" для документов, "query" для поисковых запросов
            
        Returns:
            Векторное представление текста (256 dimensions)
            
        Raises:
            ProviderError: При ошибке получения embedding
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Yandex API имеет лимит на длину текста (около 2000 токенов)
        # Обрезаем до безопасного лимита
        MAX_TEXT_LENGTH = 8000  # Примерно 2000 токенов для русского текста
        if len(text) > MAX_TEXT_LENGTH:
            original_length = len(text)
            text = text[:MAX_TEXT_LENGTH]
            logger.debug(f"Text truncated from {original_length} to {MAX_TEXT_LENGTH} characters")
        
        # Выбираем модель в зависимости от типа
        model = self._doc_model if embedding_type == "doc" else self._query_model

        async with self._rate_limiter:
            session = await self._get_session()
            url = f"{YANDEX_API_BASE_URL}/textEmbedding"

            payload = {
                "modelUri": self._build_model_uri(model),
                "text": text,
            }

            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        embedding = response.get("embedding", [])

                        if not embedding:
                            raise ProviderError("Empty embedding returned from Yandex API")

                        if len(embedding) != self.dimensions:
                            logger.warning(
                                f"Embedding dimension mismatch: expected {self.dimensions}, "
                                f"got {len(embedding)}"
                            )

                        self._rate_limiter.record_success()
                        return embedding
                    elif resp.status == 401:
                        error_text = await resp.text()
                        raise ProviderAuthenticationError(
                            f"Yandex API authentication failed: {error_text}"
                        )
                    elif resp.status == 403:
                        error_text = await resp.text()
                        raise ProviderAuthenticationError(
                            f"Yandex API access denied: {error_text}"
                        )
                    elif resp.status == 429:
                        error_text = await resp.text()
                        self._rate_limiter.record_rate_limit()
                        raise ProviderRateLimitError(f"Yandex API rate limit exceeded: {error_text}")
                    else:
                        error_text = await resp.text()
                        raise ProviderConnectionError(
                            f"Yandex API returned status {resp.status}: {error_text}"
                        )
            except asyncio.TimeoutError:
                raise ProviderTimeoutError("Yandex API request timeout")
            except ClientError as e:
                raise ProviderConnectionError(f"Yandex API connection error: {e}") from e
    
    async def get_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        embedding_type: str = "doc",
    ) -> list[list[float]]:
        """Батчевая генерация embeddings.
        
        Yandex API поддерживает батчинг через массив текстов в одном запросе.
        Максимальный размер батча: 100 текстов.
        
        Args:
            texts: Список текстов для генерации embeddings
            batch_size: Размер батча (по умолчанию 50, максимум 100)
            embedding_type: "doc" для документов, "query" для поисковых запросов
            
        Returns:
            Список векторных представлений
        """
        if not texts:
            return []
        
        non_empty_texts = [t for t in texts if t.strip()]
        if not non_empty_texts:
            raise ValueError("All texts are empty")
        
        # Yandex API поддерживает батчи до 100 текстов
        effective_batch_size = min(batch_size or 50, 100)
        
        all_embeddings: list[list[float]] = []
        
        for i in range(0, len(non_empty_texts), effective_batch_size):
            batch = non_empty_texts[i : i + effective_batch_size]
            logger.debug(f"Processing Yandex embedding batch {i // effective_batch_size + 1} ({len(batch)} texts)")
            
            # Выбираем модель в зависимости от типа
            model = self._doc_model if embedding_type == "doc" else self._query_model

            async with self._rate_limiter:
                session = await self._get_session()
                url = f"{YANDEX_API_BASE_URL}/textEmbedding"

                # Yandex API поддерживает массив текстов в одном запросе
                payload = {
                    "modelUri": self._build_model_uri(model),
                    "texts": batch,
                }

                try:
                    async with session.post(url, json=payload) as resp:
                        if resp.status == 200:
                            response = await resp.json()
                            embeddings = response.get("embeddings", [])

                            if len(embeddings) != len(batch):
                                logger.warning(
                                    f"Expected {len(batch)} embeddings, got {len(embeddings)}"
                                )

                            # Проверяем размерность каждого embedding
                            for idx, emb in enumerate(embeddings):
                                if len(emb) != self.dimensions:
                                    logger.warning(
                                        f"Embedding {idx} dimension mismatch: "
                                        f"expected {self.dimensions}, got {len(emb)}"
                                    )

                            self._rate_limiter.record_success()
                            all_embeddings.extend(embeddings)
                        elif resp.status == 401:
                            error_text = await resp.text()
                            raise ProviderAuthenticationError(
                                f"Yandex API authentication failed: {error_text}"
                            )
                        elif resp.status == 403:
                            error_text = await resp.text()
                            raise ProviderAuthenticationError(
                                f"Yandex API access denied: {error_text}"
                            )
                        elif resp.status == 429:
                            error_text = await resp.text()
                            self._rate_limiter.record_rate_limit()
                            raise ProviderRateLimitError(f"Yandex API rate limit exceeded: {error_text}")
                        else:
                            error_text = await resp.text()
                            raise ProviderConnectionError(
                                f"Yandex API returned status {resp.status}: {error_text}"
                            )
                except asyncio.TimeoutError:
                    # При таймауте возвращаем нулевые векторы для этого батча
                    logger.error(f"Yandex API timeout for batch {i // effective_batch_size + 1}")
                    all_embeddings.extend([[0.0] * self.dimensions] * len(batch))
                except ClientError as e:
                    logger.error(f"Yandex API connection error for batch: {e}")
                    all_embeddings.extend([[0.0] * self.dimensions] * len(batch))
                except (ProviderRateLimitError, ProviderAuthenticationError, ProviderConnectionError):
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error getting Yandex embeddings batch: {e}")
                    all_embeddings.extend([[0.0] * self.dimensions] * len(batch))
        
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
