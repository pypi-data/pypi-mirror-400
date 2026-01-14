"""Сервис для генерации context prefix через LLM (Contextual Retrieval)."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from obsidian_kb.config.schema import EnrichmentConfig

if TYPE_CHECKING:
    from obsidian_kb.indexing.chunking import ChunkInfo
    from obsidian_kb.providers.interfaces import IChatCompletionProvider

logger = logging.getLogger(__name__)

# Количество параллельных запросов (можно вынести в конфиг)
DEFAULT_MAX_CONCURRENT_ENRICHMENT = 10

# Тип статуса обогащения
EnrichmentStatus = Literal["success", "fallback", "skipped"]


@dataclass
class EnrichmentStats:
    """Статистика обогащения чанков.

    Используется для прозрачного отображения результатов enrichment
    в job status и IndexingResult.
    """

    total_chunks: int
    enriched_ok: int  # Успешно обогащены
    enriched_fallback: int  # Использован fallback (пустой context)
    errors: list[str]  # Список сообщений об ошибках

    @property
    def success_rate(self) -> float:
        """Процент успешных обогащений."""
        if self.total_chunks == 0:
            return 0.0
        return (self.enriched_ok / self.total_chunks) * 100

    def to_dict(self) -> dict:
        """Сериализация для MCP и логирования."""
        return {
            "total": self.total_chunks,
            "success": self.enriched_ok,
            "fallback": self.enriched_fallback,
            "errors_count": len(self.errors),
            "success_rate_percent": round(self.success_rate, 1),
        }


@dataclass
class EnrichedChunk:
    """Обогащённый чанк с context prefix.

    Attributes:
        chunk_info: Информация о чанке
        context_prefix: Краткое описание контекста чанка (80-100 токенов)
        provider_info: Информация о провайдере (name, model)
        enrichment_status: Статус обогащения:
            - "success": обогащение выполнено успешно
            - "fallback": использован fallback (пустой context или ошибка)
            - "skipped": обогащение пропущено (например, отключено в конфиге)
        error_message: Сообщение об ошибке (только если status != "success")
    """

    chunk_info: "ChunkInfo"
    context_prefix: str  # Краткое описание контекста чанка (80-100 токенов)
    provider_info: dict[str, str] | None = None  # Информация о провайдере
    enrichment_status: EnrichmentStatus = "success"
    error_message: str | None = None


class ContextualRetrievalService:
    """Сервис для генерации context prefix для чанков через LLM.
    
    Context prefix содержит краткое описание контекста чанка, что улучшает
    качество retrieval при поиске.
    """
    
    def __init__(
        self,
        chat_provider: "IChatCompletionProvider",
        config: EnrichmentConfig | None = None,
        max_concurrent: int | None = None,
    ) -> None:
        """Инициализация сервиса.

        Args:
            chat_provider: Провайдер для генерации context prefix
            config: Конфигурация обогащения
            max_concurrent: Максимальное количество параллельных запросов к LLM
                           (если не указано, берётся из config или DEFAULT_MAX_CONCURRENT_ENRICHMENT)
        """
        self._chat = chat_provider
        self._config = config or EnrichmentConfig()
        # Приоритет: явный параметр > конфиг > дефолт
        self._max_concurrent = (
            max_concurrent
            or getattr(self._config, "max_concurrent", None)
            or DEFAULT_MAX_CONCURRENT_ENRICHMENT
        )
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
    
    async def enrich_chunks(
        self,
        chunks: list["ChunkInfo"],
        document_context: str,
    ) -> list[EnrichedChunk]:
        """Генерирует context prefix для чанков.
        
        Args:
            chunks: Список чанков для обогащения
            document_context: Контекст документа (заголовки, метаданные)
            
        Returns:
            Список обогащённых чанков с context prefix
        """
        if not chunks:
            return []
        
        # Батчинг для эффективности
        batch_size = self._config.batch_size
        enriched_chunks = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            try:
                batch_enriched = await self._enrich_batch(batch, document_context)
                enriched_chunks.extend(batch_enriched)
            except Exception as e:
                error_msg = f"Batch enrichment failed: {e}"
                logger.error(f"Failed to enrich batch {i}-{i+len(batch)}: {e}")
                # Graceful degradation: добавляем чанки без context prefix
                for chunk in batch:
                    enriched_chunks.append(EnrichedChunk(
                        chunk_info=chunk,
                        context_prefix="",
                        provider_info=None,
                        enrichment_status="fallback",
                        error_message=error_msg,
                    ))

        return enriched_chunks
    
    async def _enrich_batch(
        self,
        chunks: list["ChunkInfo"],
        document_context: str,
    ) -> list[EnrichedChunk]:
        """Обогащение батча чанков параллельно.

        Использует asyncio.gather для параллельной обработки чанков
        с ограничением через семафор для предотвращения перегрузки API.

        Args:
            chunks: Батч чанков
            document_context: Контекст документа

        Returns:
            Список обогащённых чанков (в том же порядке, что и входные)
        """

        async def enrich_one(chunk: "ChunkInfo") -> EnrichedChunk:
            """Обогащение одного чанка с семафором."""
            async with self._semaphore:
                try:
                    context_prefix = await self._generate_context_prefix(
                        chunk,
                        document_context,
                    )
                    return EnrichedChunk(
                        chunk_info=chunk,
                        context_prefix=context_prefix,
                        provider_info={
                            "provider": self._chat.name,
                            "model": self._chat.model,
                        },
                        enrichment_status="success",
                        error_message=None,
                    )
                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"Failed to generate context prefix for chunk: {e}")
                    # Graceful degradation: возвращаем чанк без context prefix
                    return EnrichedChunk(
                        chunk_info=chunk,
                        context_prefix="",
                        provider_info={
                            "provider": self._chat.name,
                            "model": self._chat.model,
                        },
                        enrichment_status="fallback",
                        error_message=error_msg,
                    )

        # Запускаем все обогащения параллельно
        tasks = [enrich_one(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        enriched = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = f"Unexpected error: {result}"
                logger.error(f"Unexpected error enriching chunk {i}: {result}")
                # Graceful degradation
                enriched.append(EnrichedChunk(
                    chunk_info=chunks[i],
                    context_prefix="",
                    provider_info={
                        "provider": self._chat.name,
                        "model": self._chat.model,
                    },
                    enrichment_status="fallback",
                    error_message=error_msg,
                ))
            else:
                enriched.append(result)

        return enriched
    
    async def _generate_context_prefix(
        self,
        chunk: "ChunkInfo",
        document_context: str,
    ) -> str:
        """Генерация context prefix для чанка.
        
        Args:
            chunk: Чанк для обогащения
            document_context: Контекст документа
            
        Returns:
            Context prefix (80-100 токенов)
        """
        # Формируем промпт для генерации context prefix
        prompt = self._build_prompt(chunk, document_context)
        
        # Генерируем через LLM
        messages = [
            {
                "role": "system",
                "content": "Ты помощник для генерации кратких описаний контекста текстовых фрагментов. "
                           "Твоя задача - создать краткое описание (80-100 токенов), которое поможет "
                           "понять контекст фрагмента при поиске.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        try:
            max_tokens = self._config.context_prefix_tokens + 20  # Небольшой запас
            response = await self._chat.complete(
                messages=messages,
                temperature=0.3,  # Низкая температура для более детерминированных результатов
                max_tokens=max_tokens,
            )
            
            # Обрезаем до нужной длины (примерно)
            context_prefix = response.strip()
            
            # Проверяем длину и обрезаем если нужно
            estimated_tokens = len(context_prefix) // 3  # Примерная оценка токенов
            if estimated_tokens > self._config.context_prefix_tokens:
                # Обрезаем до нужной длины
                max_chars = self._config.context_prefix_tokens * 3
                context_prefix = context_prefix[:max_chars].rsplit(".", 1)[0] + "."
            
            return context_prefix
        except Exception as e:
            logger.error(f"Failed to generate context prefix: {e}")
            raise
    
    def _build_prompt(self, chunk: "ChunkInfo", document_context: str) -> str:
        """Построение промпта для генерации context prefix.
        
        Args:
            chunk: Чанк для обогащения
            document_context: Контекст документа
            
        Returns:
            Промпт для LLM
        """
        # Формируем контекст из заголовков
        headers_context = " > ".join(chunk.headers) if chunk.headers else "Документ"
        
        prompt = f"""Создай краткое описание контекста следующего текстового фрагмента.

Контекст документа:
{document_context[:500]}

Иерархия заголовков: {headers_context}

Тип фрагмента: {chunk.chunk_type}

Текст фрагмента:
{chunk.text[:1000]}

Создай краткое описание (80-100 токенов), которое поможет понять контекст этого фрагмента при поиске.
Описание должно быть информативным и содержать ключевые понятия из фрагмента.

Описание:"""
        
        return prompt

