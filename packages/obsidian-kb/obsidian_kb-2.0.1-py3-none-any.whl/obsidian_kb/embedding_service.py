"""Сервис для получения embeddings через Ollama."""

import asyncio
import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout, TCPConnector

from obsidian_kb.config import settings
from obsidian_kb.providers.exceptions import ProviderConnectionError
from obsidian_kb.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Сервис для получения векторных embeddings через Ollama."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        enable_query_cache: bool = True,
        query_cache_size: int = 100,
    ) -> None:
        """Инициализация сервиса embeddings.

        Args:
            base_url: Базовый URL Ollama (по умолчанию из settings)
            model: Название модели (по умолчанию из settings)
            timeout: Таймаут запросов в секундах (по умолчанию из settings.embedding_timeout)
            enable_query_cache: Включить кэширование embeddings для запросов
            query_cache_size: Размер кэша запросов
        """
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.embedding_model
        self.timeout = ClientTimeout(total=timeout or settings.embedding_timeout)
        self._session: aiohttp.ClientSession | None = None
        self.enable_query_cache = enable_query_cache
        # ОПТИМИЗАЦИЯ: Используем OrderedDict для LRU кэша
        self.query_cache: OrderedDict[str, list[float]] = OrderedDict()
        self.query_cache_size = query_cache_size
        
        # Semaphore для ограничения параллелизма запросов к Ollama
        self._semaphore = asyncio.Semaphore(settings.ollama_max_concurrent)
        
        # Rate Limiter для Ollama (если включен)
        self._rate_limiter: RateLimiter | None = None
        if settings.ollama_rate_limit_enabled:
            self._rate_limiter = RateLimiter(
                max_requests=settings.ollama_rate_limit_max_requests,
                window_seconds=settings.ollama_rate_limit_window_seconds,
                name="OllamaRateLimiter",
            )
        
        # TCPConnector с connection pool
        self._connector = TCPConnector(
            limit=settings.ollama_connector_limit,
            limit_per_host=settings.ollama_connector_limit_per_host,
        )

    async def _get_session(self, force_recreate: bool = False) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии.
        
        Args:
            force_recreate: Принудительно пересоздать сессию
        """
        if force_recreate and self._session and not self._session.closed:
            try:
                await self._session.close()
            except Exception as e:
                logger.debug(f"Error closing session during recreation: {e}")
            self._session = None
        
        if self._session is None or self._session.closed:
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

    async def health_check(self) -> bool:
        """Проверка доступности Ollama.

        Returns:
            True если Ollama доступна, False иначе
        """
        try:
            # Используем новую сессию для health check, чтобы избежать проблем с закрытой сессией
            timeout = ClientTimeout(total=10)  # Увеличиваем таймаут до 10 секунд
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m["name"] for m in data.get("models", [])]
                        # Проверяем точное совпадение
                        model_found = self.model in models
                        # Если не найдено, проверяем совпадение с версией (например, mxbai-embed-large:latest для mxbai-embed-large)
                        if not model_found:
                            model_base = self.model.split(":")[0] if ":" in self.model else self.model
                            # Ищем модель, которая начинается с базового имени (например, mxbai-embed-large:latest)
                            matching_models = [m for m in models if m.startswith(f"{model_base}:") or m == model_base]
                            if matching_models:
                                # Используем найденную модель с версией
                                self.model = matching_models[0]
                                model_found = True
                                logger.info(f"Using model {self.model} (matched {model_base})")
                        
                        if model_found:
                            logger.debug(f"Ollama health check OK, model {self.model} available")
                            return True
                        logger.warning(
                            f"Model {self.model} not found in Ollama. "
                            f"Available models: {models[:5]}{'...' if len(models) > 5 else ''}"
                        )
                        return False
                    logger.warning(f"Ollama health check failed: status {resp.status}")
                    return False
        except asyncio.TimeoutError:
            logger.warning("Ollama health check timeout (10s) - возможно Ollama не запущена")
            return False
        except ClientError as e:
            logger.warning(f"Ollama health check failed (connection error): {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error in health check: {e}", exc_info=True)
            return False

    async def _request_with_retry(
        self,
        url: str,
        payload: dict[str, Any],
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Выполнение HTTP запроса с retry и exponential backoff.

        Args:
            url: URL для запроса
            payload: Тело запроса
            max_retries: Максимальное количество попыток

        Returns:
            JSON ответ от сервера

        Raises:
            ProviderConnectionError: Если все попытки неудачны
        """
        for attempt in range(max_retries):
            # Применяем rate limiting перед запросом (если включен)
            if self._rate_limiter:
                await self._rate_limiter.acquire()
            
            # Получаем сессию перед каждой попыткой, чтобы убедиться, что она не закрыта
            session = await self._get_session()
            
            # Проверяем, что сессия не закрыта
            if session.closed:
                logger.warning("Session is closed, recreating...")
                session = await self._get_session(force_recreate=True)
            
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 404:
                        error_text = await resp.text()
                        raise ProviderConnectionError(f"Model not found: {error_text}")
                    elif resp.status == 500:
                        error_text = await resp.text()
                        # Специальная обработка ошибки превышения контекста
                        if "context length" in error_text.lower() or "input length exceeds" in error_text.lower():
                            # Если это ошибка превышения контекста, не повторяем запрос
                            # (обрезка уже была применена, значит текст все равно слишком длинный)
                            # Создаем специальное исключение, которое не будет повторяться
                            error = ProviderConnectionError(
                                f"Text too long for model (even after truncation to 6000 chars): {error_text}"
                            )
                            # Помечаем, что это ошибка превышения контекста (не повторяем)
                            error._skip_retry = True  # type: ignore
                            raise error
                        raise ProviderConnectionError(f"Ollama returned status {resp.status}: {error_text}")
                    else:
                        error_text = await resp.text()
                        raise ProviderConnectionError(f"Ollama returned status {resp.status}: {error_text}")

            except asyncio.TimeoutError:
                # Пересоздаём сессию при таймауте
                if attempt == 0:
                    logger.warning("Request timeout, recreating session")
                    await self._get_session(force_recreate=True)
                
                wait_time = 2**attempt  # Exponential backoff
                if attempt < max_retries - 1:
                    logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise ProviderConnectionError("Ollama request timeout after all retries")

            except (ClientError, RuntimeError) as e:
                # Пересоздаём сессию при ошибке подключения или "Session is closed"
                error_msg = str(e).lower()
                is_session_error = "session is closed" in error_msg or "session closed" in error_msg

                if is_session_error or attempt == 0:
                    logger.warning(f"Connection error (session issue: {is_session_error}), recreating session: {e}")
                    await self._get_session(force_recreate=True)

                wait_time = 2**attempt
                if attempt < max_retries - 1:
                    logger.warning(f"Request error: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise ProviderConnectionError(f"Ollama connection error: {e}") from e

            except ProviderConnectionError as e:
                # Проверяем, нужно ли пропустить retry (для ошибок превышения контекста)
                if hasattr(e, '_skip_retry') and e._skip_retry:
                    # Не повторяем запрос для ошибок превышения контекста
                    logger.error(f"Context length exceeded, skipping retry: {e}")
                    raise
                # Для других ошибок ProviderConnectionError тоже не повторяем
                raise

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(f"Unexpected error: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise ProviderConnectionError(f"Unexpected error in embedding request: {e}") from e

        raise ProviderConnectionError("Failed to get embeddings after all retries")

    def _get_cache_key(self, text: str) -> str:
        """Генерация ключа кэша для текста.
        
        Args:
            text: Текст для кэширования
            
        Returns:
            Хеш-ключ
        """
        normalized = text.strip().lower()
        return hashlib.md5(f"{self.model}::{normalized}".encode()).hexdigest()

    async def get_embedding(self, text: str, embedding_type: str = "doc") -> list[float]:
        """Получение embedding для одного текста с кэшированием.

        Args:
            text: Текст для получения embedding
            embedding_type: Тип embedding ("doc" для документов, "query" для запросов).
                           Поддерживается не всеми провайдерами (по умолчанию "doc").

        Returns:
            Вектор embedding (список float) размерности settings.embedding_dimensions

        Raises:
            ProviderConnectionError: Если не удалось получить embedding
            ValueError: Если text пустой

        Preconditions:
            - text не пустой (после strip)
            - Ollama доступна (проверяется через health_check)

        Postconditions:
            - len(result) == settings.embedding_dimensions
            - Все элементы result имеют тип float
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Используем semaphore для ограничения параллелизма
        async with self._semaphore:
            start_time = time.time()
            try:
                return await self._get_embedding_internal(text, embedding_type=embedding_type)
            finally:
                elapsed = time.time() - start_time
                if elapsed > 5.0:  # Логируем медленные запросы (>5 сек)
                    logger.warning(f"Slow embedding request: {elapsed:.2f}s for text: {text[:50]}...")
    
    async def _get_embedding_internal(self, text: str, embedding_type: str = "doc") -> list[float]:
        """Внутренний метод получения embedding (без semaphore)."""

        # Обрезаем текст до максимальной длины для модели
        # nomic-embed-text имеет лимит ~8000 токенов
        # Для русского текста 1 токен ≈ 2-3 символа, для английского ≈ 4 символа
        # Безопасный лимит: 6000 символов (гарантированно поместится ~2000-3000 токенов)
        MAX_TEXT_LENGTH = 6000
        if len(text) > MAX_TEXT_LENGTH:
            original_length = len(text)
            text = text[:MAX_TEXT_LENGTH]
            # Логируем как DEBUG, так как это нормальное поведение, а не ошибка
            # Обрезка предотвращает ошибки "context length exceeded"
            logger.debug(
                f"Text truncated from {original_length} to {MAX_TEXT_LENGTH} characters "
                f"for embedding (model limit: ~8000 tokens)"
            )

        # Проверяем кэш (LRU)
        if self.enable_query_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self.query_cache:
                # Перемещаем в конец (самый недавно использованный)
                embedding = self.query_cache.pop(cache_key)
                self.query_cache[cache_key] = embedding
                logger.debug(f"Cache hit for embedding query: {text[:50]}...")
                return embedding

        # Дополнительная проверка длины перед отправкой
        # Убеждаемся, что текст не превышает лимит даже после всех преобразований
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
            logger.warning(f"Text still too long after initial truncation, re-truncated to {MAX_TEXT_LENGTH}")
        
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model, "prompt": text}
        
        # Логируем длину текста для отладки (только если текст длинный)
        if len(text) > 600:
            logger.debug(f"Sending text of length {len(text)} to Ollama (limit: {MAX_TEXT_LENGTH})")

        # Используем ServiceContainer для получения recovery_service (ленивый импорт для избежания циклического импорта)
        from obsidian_kb.service_container import get_service_container
        services = get_service_container()
        recovery_service = services.recovery_service

        try:
            response = await self._request_with_retry(url, payload)
            embedding = response.get("embedding", [])

            if not embedding:
                raise ProviderConnectionError("Empty embedding returned from Ollama")

            if len(embedding) != settings.embedding_dimensions:
                logger.warning(
                    f"Embedding dimension mismatch: expected {settings.embedding_dimensions}, "
                    f"got {len(embedding)}"
                )

            # Сохраняем в кэш (LRU)
            if self.enable_query_cache:
                cache_key = self._get_cache_key(text)
                # Если ключ уже есть, удаляем его (будет добавлен в конец)
                if cache_key in self.query_cache:
                    del self.query_cache[cache_key]
                # Если кэш переполнен, удаляем самый старый (первый элемент)
                elif len(self.query_cache) >= self.query_cache_size:
                    self.query_cache.popitem(last=False)  # Удаляем первый (самый старый)
                # Добавляем в конец (самый недавно использованный)
                self.query_cache[cache_key] = embedding
                logger.debug(f"Cached embedding for query: {text[:50]}...")

            return embedding

        except ProviderConnectionError:
            # Пересоздаём сессию при ошибке подключения
            logger.warning("Provider connection error, recreating session")
            await self._get_session(force_recreate=True)

            # Пытаемся восстановить подключение перед повторной ошибкой
            try:
                await recovery_service.recover_ollama_connection(self)
            except Exception as e:
                logger.debug(f"Recovery attempt failed after ProviderConnectionError: {e}")
            raise
        except RuntimeError as e:
            # Обрабатываем ошибку "Session is closed"
            error_msg = str(e).lower()
            if "session is closed" in error_msg or "session closed" in error_msg:
                logger.warning("Session is closed, recreating session and retrying")
                await self._get_session(force_recreate=True)
                # Повторяем попытку один раз
                try:
                    response = await self._request_with_retry(url, payload, max_retries=1)
                    embedding = response.get("embedding", [])
                    if not embedding:
                        raise ProviderConnectionError("Empty embedding returned from Ollama")
                    if len(embedding) != settings.embedding_dimensions:
                        logger.warning(
                            f"Embedding dimension mismatch: expected {settings.embedding_dimensions}, "
                            f"got {len(embedding)}"
                        )
                    # Сохраняем в кэш (LRU)
                    if self.enable_query_cache:
                        cache_key = self._get_cache_key(text)
                        # Если ключ уже есть, удаляем его (будет добавлен в конец)
                        if cache_key in self.query_cache:
                            del self.query_cache[cache_key]
                        # Если кэш переполнен, удаляем самый старый (первый элемент)
                        elif len(self.query_cache) >= self.query_cache_size:
                            self.query_cache.popitem(last=False)  # Удаляем первый (самый старый)
                        # Добавляем в конец (самый недавно использованный)
                        self.query_cache[cache_key] = embedding
                    return embedding
                except Exception as retry_error:
                    logger.error(f"Retry after session recreation failed: {retry_error}")
                    raise ProviderConnectionError(f"Failed to get embedding after session recreation: {retry_error}") from retry_error
            else:
                raise ProviderConnectionError(f"Runtime error getting embedding: {e}") from e
        except Exception as e:
            # Пересоздаём сессию при неожиданной ошибке
            logger.warning(f"Unexpected error getting embedding, recreating session: {e}")
            await self._get_session(force_recreate=True)

            # Пытаемся восстановить подключение
            try:
                await recovery_service.recover_ollama_connection(self)
            except Exception as recovery_error:
                logger.debug(f"Recovery attempt failed after unexpected error: {recovery_error}")
            raise ProviderConnectionError(f"Failed to get embedding: {e}") from e

    async def get_embeddings_batch(
        self, texts: list[str], embedding_type: str = "doc"
    ) -> list[list[float]]:
        """Получение embeddings для батча текстов.

        Args:
            texts: Список текстов для получения embeddings
            embedding_type: Тип embedding ("doc" для документов, "query" для запросов).
                           Поддерживается не всеми провайдерами (по умолчанию "doc").

        Returns:
            Список векторов embeddings (один вектор на каждый текст из texts)

        Raises:
            ProviderConnectionError: Если не удалось получить embeddings
            ValueError: Если все тексты пустые

        Preconditions:
            - len(texts) > 0
            - Хотя бы один текст не пустой (после strip)

        Postconditions:
            - len(result) == len(texts)
            - Для каждого непустого текста: len(result[i]) == settings.embedding_dimensions
            - Для пустых текстов: result[i] == [0.0] * settings.embedding_dimensions
        """
        if not texts:
            return []

        # Фильтруем пустые тексты
        non_empty_texts = [t for t in texts if t.strip()]
        if not non_empty_texts:
            raise ValueError("All texts are empty")

        # Разбиваем на батчи по batch_size
        batch_size = settings.batch_size
        all_embeddings: list[list[float]] = []

        for i in range(0, len(non_empty_texts), batch_size):
            batch = non_empty_texts[i : i + batch_size]
            logger.debug(f"Processing embedding batch {i // batch_size + 1} ({len(batch)} texts)")

            # Ollama API не поддерживает батчинг напрямую, делаем параллельные запросы
            tasks = [self.get_embedding(text, embedding_type=embedding_type) for text in batch]
            batch_embeddings = await asyncio.gather(*tasks, return_exceptions=True)

            # Обрабатываем результаты
            for idx, result in enumerate(batch_embeddings):
                if isinstance(result, Exception):
                    error_msg = str(result).lower()
                    # Если это ошибка закрытой сессии, пересоздаём сессию и повторяем для этого текста
                    if "session is closed" in error_msg or "session closed" in error_msg:
                        logger.warning(f"Session closed error for text {i + idx}, recreating session and retrying")
                        await self._get_session(force_recreate=True)
                        try:
                            # Повторяем запрос для этого текста
                            result = await self.get_embedding(batch[idx])
                            if isinstance(result, list) and len(result) == settings.embedding_dimensions:
                                all_embeddings.append(result)
                                continue
                        except Exception as retry_error:
                            logger.error(f"Retry failed for text {i + idx}: {retry_error}")
                    
                    logger.error(f"Error getting embedding for text {i + idx}: {result}")
                    # Возвращаем нулевой вектор в случае ошибки
                    all_embeddings.append([0.0] * settings.embedding_dimensions)
                elif isinstance(result, list) and len(result) == settings.embedding_dimensions:
                    all_embeddings.append(result)
                else:
                    logger.warning(f"Unexpected result type for text {i + idx}: {type(result)}, using zero vector")
                    all_embeddings.append([0.0] * settings.embedding_dimensions)

        # Восстанавливаем порядок с учётом пустых текстов
        result_embeddings: list[list[float]] = []
        text_idx = 0

        for text in texts:
            if text.strip():
                result_embeddings.append(all_embeddings[text_idx])
                text_idx += 1
            else:
                # Пустой текст -> нулевой вектор
                result_embeddings.append([0.0] * settings.embedding_dimensions)

        return result_embeddings

