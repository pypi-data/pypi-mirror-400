"""Базовый интерфейс стратегии обогащения."""

from typing import Protocol

from obsidian_kb.types import ChunkEnrichment, DocumentChunk


class EnrichmentStrategy(Protocol):
    """Базовый интерфейс стратегии обогащения чанков."""

    async def enrich(
        self,
        chunk: DocumentChunk,
    ) -> ChunkEnrichment:
        """Обогащение чанка через LLM.

        Args:
            chunk: Чанк для обогащения

        Returns:
            Обогащенные данные чанка

        Raises:
            ProviderError: При ошибке провайдера
        """
        ...

