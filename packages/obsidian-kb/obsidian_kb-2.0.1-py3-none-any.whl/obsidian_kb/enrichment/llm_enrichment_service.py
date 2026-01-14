"""Сервис LLM-обогащения чанков."""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from obsidian_kb.config import settings
from obsidian_kb.enrichment.strategies.enrichment_strategy import EnrichmentStrategy
from obsidian_kb.enrichment.strategies.fast_enrichment_strategy import FastEnrichmentStrategy
from obsidian_kb.enrichment.strategies.full_enrichment_strategy import FullEnrichmentStrategy
from obsidian_kb.providers.exceptions import ProviderError
from obsidian_kb.types import ChunkEnrichment, DocumentChunk

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IChunkEnrichmentRepository, IRecoveryService
    from obsidian_kb.providers.interfaces import IChatCompletionProvider

logger = logging.getLogger(__name__)


class LLMEnrichmentService:
    """Сервис для обогащения чанков через LLM.

    Реализует ILLMEnrichmentService и обеспечивает:
    - Кэширование результатов по content_hash
    - Rate limiting через semaphore
    - Retry логику через RecoveryService
    - Graceful degradation при ошибках
    - Параллельную обработку с ограничением
    """

    def __init__(
        self,
        repository: "IChunkEnrichmentRepository",
        recovery_service: "IRecoveryService",
        chat_provider: "IChatCompletionProvider",
        strategy: EnrichmentStrategy | None = None,
    ) -> None:
        """Инициализация сервиса обогащения.

        Args:
            repository: Репозиторий для кэширования обогащений
            recovery_service: Сервис для retry логики
            chat_provider: Провайдер chat completion (Ollama, Yandex, etc.)
            strategy: Стратегия обогащения (по умолчанию выбирается по settings.llm_enrichment_strategy)
        """
        self._chat_provider = chat_provider
        self.repository = repository
        self.recovery_service = recovery_service

        # Выбор стратегии
        if strategy is None:
            strategy_name = settings.llm_enrichment_strategy.lower()
            if strategy_name == "fast":
                strategy = FastEnrichmentStrategy(chat_provider=chat_provider)
            else:  # По умолчанию "full"
                strategy = FullEnrichmentStrategy(chat_provider=chat_provider)

        self._strategy = strategy

        # Semaphore для ограничения параллелизма
        self._semaphore = asyncio.Semaphore(settings.llm_max_concurrent)

    @property
    def provider_name(self) -> str:
        """Имя используемого провайдера."""
        return self._chat_provider.name

    @property
    def model(self) -> str:
        """Название используемой модели."""
        return self._chat_provider.model

    def _compute_content_hash(self, chunk: DocumentChunk) -> str:
        """Вычисление SHA256 hash контента чанка.

        Args:
            chunk: Чанк для вычисления hash

        Returns:
            SHA256 hash в hex формате
        """
        content = chunk.content
        return hashlib.sha256(content.encode()).hexdigest()

    def _create_empty_enrichment(self, chunk: DocumentChunk) -> ChunkEnrichment:
        """Создание пустого обогащения (fallback при ошибках).

        Args:
            chunk: Чанк для создания обогащения

        Returns:
            Пустое обогащение
        """
        content_hash = self._compute_content_hash(chunk)
        return ChunkEnrichment(
            chunk_id=chunk.id,
            vault_name=chunk.vault_name,
            summary="",
            key_concepts=[],
            semantic_tags=[],
            enriched_at=datetime.now(),
            content_hash=content_hash,
        )

    async def enrich_chunk(self, chunk: DocumentChunk) -> ChunkEnrichment:
        """Обогащение одного чанка через LLM.

        Args:
            chunk: Чанк для обогащения

        Returns:
            Обогащенные данные чанка

        Raises:
            ProviderError: При ошибке провайдера (только если не удалось выполнить fallback)
        """
        # Вычисляем content_hash для проверки кэша
        content_hash = self._compute_content_hash(chunk)

        # Проверяем кэш
        try:
            cached = await self.repository.get(
                vault_name=chunk.vault_name,
                chunk_id=chunk.id,
            )

            if cached and cached.content_hash == content_hash:
                logger.debug(f"Cache hit for chunk {chunk.id}")
                return cached
        except Exception as e:
            logger.warning(f"Failed to check cache for chunk {chunk.id}: {e}")
            # Продолжаем выполнение, если кэш недоступен

        # Используем semaphore для ограничения параллелизма
        async with self._semaphore:
            try:
                # Вызываем стратегию обогащения с retry логикой
                enrichment = await self.recovery_service.retry_with_backoff(
                    self._strategy.enrich,
                    chunk,
                    max_retries=3,
                    initial_delay=1.0,
                    max_delay=60.0,
                    exponential_base=2.0,
                    operation_name="llm_enrichment",
                )

                # Сохраняем результат в кэш
                try:
                    await self.repository.upsert(
                        vault_name=chunk.vault_name,
                        enrichments=[enrichment],
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache enrichment for chunk {chunk.id}: {e}")
                    # Продолжаем выполнение, даже если кэширование не удалось

                return enrichment

            except ProviderError as e:
                logger.warning(f"LLM enrichment failed for chunk {chunk.id}: {e}")
                # Graceful degradation: возвращаем пустое обогащение
                empty_enrichment = self._create_empty_enrichment(chunk)

                # Пытаемся сохранить пустое обогащение (чтобы не повторять запросы)
                try:
                    await self.repository.upsert(
                        vault_name=chunk.vault_name,
                        enrichments=[empty_enrichment],
                    )
                except Exception as cache_error:
                    logger.debug(f"Failed to cache empty enrichment: {cache_error}")

                return empty_enrichment

            except Exception as e:
                logger.error(f"Unexpected error enriching chunk {chunk.id}: {e}", exc_info=True)
                # Graceful degradation: возвращаем пустое обогащение
                return self._create_empty_enrichment(chunk)

    async def enrich_chunks_batch(self, chunks: list[DocumentChunk]) -> list[ChunkEnrichment]:
        """Батчевое обогащение чанков через LLM с параллельным выполнением.

        Использует asyncio.gather для параллельной обработки чанков,
        при этом семафор ограничивает количество одновременных запросов к LLM.

        Args:
            chunks: Список чанков для обогащения

        Returns:
            Список обогащенных данных (один на каждый чанк, в том же порядке)

        Raises:
            ProviderError: При ошибке провайдера (только если не удалось выполнить fallback)
        """
        if not chunks:
            return []

        logger.debug(f"Starting parallel batch enrichment for {len(chunks)} chunks")

        # Проверяем Circuit Breaker перед началом обработки
        circuit_breaker = self.recovery_service.get_circuit_breaker("llm_enrichment")
        if not circuit_breaker.can_proceed():
            logger.warning("Circuit breaker is open, returning empty enrichments for batch")
            return [self._create_empty_enrichment(chunk) for chunk in chunks]

        async def enrich_with_fallback(chunk: DocumentChunk) -> ChunkEnrichment:
            """Обогащение одного чанка с graceful degradation."""
            # Проверяем Circuit Breaker
            if not circuit_breaker.can_proceed():
                return self._create_empty_enrichment(chunk)

            try:
                return await self.enrich_chunk(chunk)
            except Exception as e:
                logger.warning(f"Error enriching chunk {chunk.id}: {e}")
                return self._create_empty_enrichment(chunk)

        # Запускаем все обогащения параллельно
        # Семафор уже есть в enrich_chunk, он ограничит параллелизм
        tasks = [enrich_with_fallback(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        enrichments: list[ChunkEnrichment] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Unexpected error in gather for chunk {chunks[i].id}: {result}")
                enrichments.append(self._create_empty_enrichment(chunks[i]))
            else:
                enrichments.append(result)

        logger.debug(f"Completed parallel batch enrichment: {len(enrichments)} enrichments")
        return enrichments

    async def health_check(self) -> bool:
        """Проверка доступности LLM провайдера.

        Returns:
            True если провайдер доступен, False иначе
        """
        try:
            health = await self._chat_provider.health_check()
            if health.available:
                logger.debug(f"LLM health check OK, provider {self.provider_name}, model {self.model}")
                return True
            else:
                logger.warning(f"LLM health check failed: {health.error}")
                return False
        except Exception as e:
            logger.warning(f"LLM health check failed: {e}")
            return False
