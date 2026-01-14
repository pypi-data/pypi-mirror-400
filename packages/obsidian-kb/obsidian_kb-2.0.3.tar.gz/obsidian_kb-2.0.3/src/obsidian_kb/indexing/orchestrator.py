"""Оркестратор гибридного pipeline индексации."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol


class CancellationTokenProtocol(Protocol):
    """Протокол для токена отмены (избегаем циклических импортов)."""

    def is_cancelled(self) -> bool: ...
    def raise_if_cancelled(self) -> None: ...

from obsidian_kb.config.manager import ConfigManager
from obsidian_kb.config.schema import EnrichmentStrategy as ConfigEnrichmentStrategy
from obsidian_kb.enrichment.contextual_retrieval import (
    ContextualRetrievalService,
    EnrichedChunk,
    EnrichmentStats,
)
from obsidian_kb.enrichment.summarization import DocumentSummary, SummarizationService
from obsidian_kb.file_parsers import extract_text_from_file
from obsidian_kb.frontmatter_parser import FrontmatterParser
from obsidian_kb.storage.change_detector import ChangeDetector, ChangeSet
from obsidian_kb.indexing.chunking import ChunkInfo, ChunkingService
from obsidian_kb.types import DocumentChunk

if TYPE_CHECKING:
    from obsidian_kb.providers.interfaces import (
        IChatCompletionProvider,
        IEmbeddingProvider,
    )
    from obsidian_kb.storage.chunk_repository import ChunkRepository
    from obsidian_kb.storage.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class EnrichmentStrategy(Enum):
    """Стратегия обогащения документов."""
    
    NONE = "none"
    CONTEXTUAL = "contextual"
    FULL = "full"


@dataclass
class ProcessedDocument:
    """Обработанный документ после chunking."""

    file_path: Path  # Полный путь к файлу
    relative_path: Path  # Относительный путь внутри vault'а (для хранения в БД)
    content: str
    metadata: dict[str, Any]
    chunks: list[ChunkInfo]
    title: str
    frontmatter_data: Any  # FrontmatterData


@dataclass
class EnrichedDocument:
    """Обогащённый документ."""
    
    processed: ProcessedDocument
    enriched_chunks: list[EnrichedChunk]
    summary: DocumentSummary | None = None


@dataclass
class VectorizedDocument:
    """Векторизованный документ готовый к сохранению."""
    
    enriched: EnrichedDocument
    chunk_embeddings: list[list[float]]
    summary_embedding: list[float] | None = None


@dataclass
class IndexingJob:
    """Задача индексации."""

    id: str
    vault_name: str
    vault_path: Path  # Path к vault'у для построения полных путей к файлам
    paths: list[Path]  # Относительные пути файлов внутри vault'а
    enrichment: EnrichmentStrategy
    status: str  # pending | running | completed | failed
    progress: float  # 0.0 - 1.0
    documents_total: int
    documents_processed: int
    errors: list[str] = field(default_factory=list)
    cost_estimate: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class IndexingResult:
    """Результат индексации."""

    job_id: str
    documents_processed: int
    documents_total: int
    chunks_created: int
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    # Дополнительные поля для совместимости с job_queue
    vault_name: str | None = None
    chunks_updated: int = 0
    chunks_deleted: int = 0
    warnings: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    # Phase 2: Прозрачность статуса Enrichment
    enrichment_stats: EnrichmentStats | None = None


class IndexingOrchestrator:
    """Оркестратор процесса индексации.
    
    Координирует весь pipeline:
    1. Change detection
    2. Document processing (chunking)
    3. Enrichment (context prefix, summaries)
    4. Vectorization
    5. Storage
    """
    
    def __init__(
        self,
        embedding_provider: "IEmbeddingProvider",
        chat_provider: "IChatCompletionProvider | None",
        chunk_repository: "ChunkRepository",
        document_repository: "DocumentRepository",
        config_manager: ConfigManager,
    ) -> None:
        """Инициализация оркестратора.
        
        Args:
            embedding_provider: Провайдер для генерации embeddings
            chat_provider: Провайдер для обогащения (может быть None)
            chunk_repository: Репозиторий чанков
            document_repository: Репозиторий документов
            config_manager: Менеджер конфигурации
        """
        self._embedding = embedding_provider
        self._chat = chat_provider
        self._chunks = chunk_repository
        self._documents = document_repository
        self._config_manager = config_manager
        
        # Инициализируем сервисы
        self._chunking_service = ChunkingService(
            chat_provider=chat_provider,
        )
        self._change_detector = ChangeDetector(
            document_repository=document_repository,
        )
        
        # Сервисы обогащения (только если есть chat_provider)
        self._contextual_retrieval: ContextualRetrievalService | None = None
        self._summarization: SummarizationService | None = None
        
        if chat_provider:
            config = config_manager.get_config()
            self._contextual_retrieval = ContextualRetrievalService(
                chat_provider=chat_provider,
                config=config.enrichment,
            )
            self._summarization = SummarizationService(
                chat_provider=chat_provider,
                config=config.enrichment,
            )
        
        # Активные задачи
        self._jobs: dict[str, IndexingJob] = {}
    
    async def create_job(
        self,
        vault_name: str,
        vault_path: Path,
        paths: list[Path] | None = None,
        force: bool = False,
        enrichment: EnrichmentStrategy = EnrichmentStrategy.CONTEXTUAL,
    ) -> IndexingJob:
        """Создание задачи индексации.
        
        Args:
            vault_name: Имя vault'а
            vault_path: Путь к vault'у
            paths: Список путей для индексации (None = все изменённые)
            force: Принудительная переиндексация даже без изменений
            enrichment: Стратегия обогащения
            
        Returns:
            IndexingJob с информацией о задаче
        """
        job_id = str(uuid.uuid4())
        
        # Определяем файлы для индексации
        if paths is None or force:
            change_set = await self._change_detector.detect_changes(
                vault_path=vault_path,
                vault_name=vault_name,
            )
            
            if paths is None:
                # Используем все изменённые файлы
                paths = change_set.new_files + change_set.modified_files
            # Если force=True и paths указаны, используем указанные paths
        
        if not paths:
            logger.info(f"No files to index for vault '{vault_name}'")
            paths = []
        
        job = IndexingJob(
            id=job_id,
            vault_name=vault_name,
            vault_path=vault_path,
            paths=paths,
            enrichment=enrichment,
            status="pending",
            progress=0.0,
            documents_total=len(paths),
            documents_processed=0,
        )
        
        self._jobs[job_id] = job
        logger.info(
            f"Created indexing job {job_id} for vault '{vault_name}': "
            f"{len(paths)} documents, enrichment={enrichment.value}"
        )
        
        return job
    
    async def run_job(
        self,
        job_id: str,
        cancellation_token: CancellationTokenProtocol | None = None,
    ) -> IndexingResult:
        """Выполнение задачи индексации.

        Args:
            job_id: ID задачи
            cancellation_token: Токен отмены для graceful shutdown

        Returns:
            IndexingResult с результатами индексации

        Raises:
            CancellationError: Если задача была отменена
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = "running"
        job.started_at = datetime.now()

        start_time = datetime.now()
        chunks_created = 0
        errors = []
        warnings = []

        # Агрегированная статистика enrichment по всем документам
        total_enrichment_stats = EnrichmentStats(
            total_chunks=0,
            enriched_ok=0,
            enriched_fallback=0,
            errors=[],
        )

        try:
            # Получаем конфигурацию vault'а
            config = self._config_manager.get_config(job.vault_name)

            # Обновляем конфигурацию сервисов
            self._chunking_service._config = config.indexing
            if self._contextual_retrieval:
                self._contextual_retrieval._config = config.enrichment
            if self._summarization:
                self._summarization._config = config.enrichment

            # Обрабатываем каждый документ
            for i, rel_path in enumerate(job.paths):
                # Строим полный путь к файлу из vault_path и относительного пути
                file_path = job.vault_path / rel_path

                # Проверяем отмену перед каждым документом
                if cancellation_token and cancellation_token.is_cancelled():
                    job.status = "cancelled"
                    job.completed_at = datetime.now()
                    logger.info(
                        f"Job {job_id} cancelled at document {i}/{len(job.paths)}"
                    )
                    # Поднимаем исключение для корректной обработки
                    cancellation_token.raise_if_cancelled()

                try:
                    # Обработка документа
                    processed = await self._process_document(
                        vault_name=job.vault_name,
                        file_path=file_path,
                        relative_path=rel_path,
                    )

                    # Обогащение (возвращает кортеж)
                    enriched, doc_stats = await self._enrich_document(
                        processed=processed,
                        strategy=job.enrichment,
                    )

                    # Агрегируем статистику enrichment
                    total_enrichment_stats.total_chunks += doc_stats.total_chunks
                    total_enrichment_stats.enriched_ok += doc_stats.enriched_ok
                    total_enrichment_stats.enriched_fallback += doc_stats.enriched_fallback
                    # Ограничиваем количество ошибок чтобы не раздувать память
                    if len(total_enrichment_stats.errors) < 100:
                        total_enrichment_stats.errors.extend(doc_stats.errors[:10])

                    # Векторизация
                    vectorized = await self._vectorize(enriched)

                    # Сохранение
                    await self._store(
                        vault_name=job.vault_name,
                        document=vectorized,
                    )

                    chunks_created += len(vectorized.enriched.enriched_chunks)
                    job.documents_processed += 1
                    job.progress = job.documents_processed / job.documents_total

                    logger.debug(
                        f"Processed document {i+1}/{len(job.paths)}: {rel_path}"
                    )
                except Exception as e:
                    error_msg = f"Failed to process {rel_path}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    job.errors.append(error_msg)
                    continue

            job.status = "completed"
            job.completed_at = datetime.now()

            duration = (datetime.now() - start_time).total_seconds()

            # Добавляем warning если были fallback обогащения
            if total_enrichment_stats.enriched_fallback > 0:
                fallback_pct = (
                    total_enrichment_stats.enriched_fallback
                    / total_enrichment_stats.total_chunks
                    * 100
                ) if total_enrichment_stats.total_chunks > 0 else 0
                warnings.append(
                    f"Enrichment fallback: {total_enrichment_stats.enriched_fallback}/"
                    f"{total_enrichment_stats.total_chunks} chunks ({fallback_pct:.1f}%)"
                )

            return IndexingResult(
                job_id=job_id,
                documents_processed=job.documents_processed,
                documents_total=job.documents_total,
                chunks_created=chunks_created,
                errors=errors,
                duration_seconds=duration,
                warnings=warnings,
                enrichment_stats=total_enrichment_stats,
            )
        except Exception as e:
            # Не перехватываем CancellationError - пробрасываем выше
            if cancellation_token and cancellation_token.is_cancelled():
                raise

            job.status = "failed"
            job.completed_at = datetime.now()
            error_msg = f"Job failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            duration = (datetime.now() - start_time).total_seconds()

            return IndexingResult(
                job_id=job_id,
                documents_processed=job.documents_processed,
                documents_total=job.documents_total,
                chunks_created=chunks_created,
                errors=errors,
                duration_seconds=duration,
                warnings=warnings,
                enrichment_stats=total_enrichment_stats if total_enrichment_stats.total_chunks > 0 else None,
            )
    
    async def _process_document(
        self,
        vault_name: str,
        file_path: Path,
        relative_path: Path,
    ) -> ProcessedDocument:
        """Phase 2: Обработка документа.

        Args:
            vault_name: Имя vault'а
            file_path: Полный путь к файлу
            relative_path: Относительный путь внутри vault'а (для хранения в БД)

        Returns:
            ProcessedDocument с распарсенным содержимым
        """
        # Читаем файл
        content = extract_text_from_file(file_path)
        if not content:
            raise ValueError(f"Failed to read file: {file_path}")

        # Парсим frontmatter
        frontmatter_data, body = FrontmatterParser.parse(content, str(file_path))
        metadata = frontmatter_data.to_dict()

        # Извлекаем заголовок
        title = metadata.get("title", "") or frontmatter_data.title or file_path.stem

        # Разбиваем на чанки
        from obsidian_kb.indexing.chunking import ChunkingStrategy
        chunks = await self._chunking_service.chunk_document(
            content=body,
            strategy=ChunkingStrategy.AUTO,
        )

        return ProcessedDocument(
            file_path=file_path,
            relative_path=relative_path,
            content=content,
            metadata=metadata,
            chunks=chunks,
            title=title,
            frontmatter_data=frontmatter_data,
        )
    
    async def _enrich_document(
        self,
        processed: ProcessedDocument,
        strategy: EnrichmentStrategy,
    ) -> tuple[EnrichedDocument, EnrichmentStats]:
        """Phase 3: Обогащение чанков с трекингом статистики.

        - Context prefix generation
        - Document summary (если strategy == FULL)
        - Сбор статистики обогащения

        Returns:
            Кортеж (EnrichedDocument, EnrichmentStats) с результатом и статистикой.
        """
        enriched_chunks = []
        summary = None

        # Инициализируем статистику
        stats = EnrichmentStats(
            total_chunks=len(processed.chunks),
            enriched_ok=0,
            enriched_fallback=0,
            errors=[],
        )

        if strategy == EnrichmentStrategy.NONE:
            # Без обогащения, создаём EnrichedChunk без context_prefix
            for chunk_info in processed.chunks:
                enriched_chunks.append(EnrichedChunk(
                    chunk_info=chunk_info,
                    context_prefix="",
                    provider_info=None,
                    enrichment_status="skipped",
                ))
            # Все чанки skipped - считаем как успех (по замыслу)
            stats.enriched_ok = len(processed.chunks)
        elif strategy == EnrichmentStrategy.CONTEXTUAL:
            # Только context prefix
            if self._contextual_retrieval:
                enriched_chunks = await self._contextual_retrieval.enrich_chunks(
                    chunks=processed.chunks,
                    document_context=processed.title,
                )
                # Подсчитываем статистику
                stats = self._compute_enrichment_stats(enriched_chunks)
            else:
                # Fallback: без обогащения (нет провайдера)
                for chunk_info in processed.chunks:
                    enriched_chunks.append(EnrichedChunk(
                        chunk_info=chunk_info,
                        context_prefix="",
                        provider_info=None,
                        enrichment_status="fallback",
                        error_message="No chat provider configured",
                    ))
                stats.enriched_fallback = len(processed.chunks)
                stats.errors.append("No chat provider configured for enrichment")
        elif strategy == EnrichmentStrategy.FULL:
            # Context prefix + summary
            if self._contextual_retrieval:
                enriched_chunks = await self._contextual_retrieval.enrich_chunks(
                    chunks=processed.chunks,
                    document_context=processed.title,
                )
                # Подсчитываем статистику
                stats = self._compute_enrichment_stats(enriched_chunks)
            else:
                # Fallback: без context prefix
                for chunk_info in processed.chunks:
                    enriched_chunks.append(EnrichedChunk(
                        chunk_info=chunk_info,
                        context_prefix="",
                        provider_info=None,
                        enrichment_status="fallback",
                        error_message="No chat provider configured",
                    ))
                stats.enriched_fallback = len(processed.chunks)
                stats.errors.append("No chat provider configured for enrichment")

            # Генерируем summary
            if self._summarization:
                summary = await self._summarization.summarize_document(
                    content=processed.content,
                    metadata=processed.metadata,
                )

        enriched_doc = EnrichedDocument(
            processed=processed,
            enriched_chunks=enriched_chunks,
            summary=summary,
        )

        return enriched_doc, stats

    def _compute_enrichment_stats(
        self,
        enriched_chunks: list[EnrichedChunk],
    ) -> EnrichmentStats:
        """Вычисление статистики обогащения из списка чанков.

        Args:
            enriched_chunks: Список обогащённых чанков

        Returns:
            EnrichmentStats с подсчитанной статистикой
        """
        stats = EnrichmentStats(
            total_chunks=len(enriched_chunks),
            enriched_ok=0,
            enriched_fallback=0,
            errors=[],
        )

        for chunk in enriched_chunks:
            if chunk.enrichment_status == "success":
                stats.enriched_ok += 1
            elif chunk.enrichment_status == "fallback":
                stats.enriched_fallback += 1
                if chunk.error_message:
                    stats.errors.append(chunk.error_message)
            elif chunk.enrichment_status == "skipped":
                # Skipped считаем как успех (enrichment отключен)
                stats.enriched_ok += 1

        return stats
    
    async def _vectorize(
        self,
        document: EnrichedDocument,
    ) -> VectorizedDocument:
        """Phase 4: Векторизация."""
        # Генерируем embeddings для чанков
        chunk_texts = []
        for enriched_chunk in document.enriched_chunks:
            # Объединяем context_prefix и текст чанка для embedding
            if enriched_chunk.context_prefix:
                chunk_text = f"{enriched_chunk.context_prefix}\n\n{enriched_chunk.chunk_info.text}"
            else:
                chunk_text = enriched_chunk.chunk_info.text
            chunk_texts.append(chunk_text)
        
        # Батчевая генерация embeddings (используем doc модель для индексации)
        chunk_embeddings = await self._embedding.get_embeddings_batch(
            chunk_texts, embedding_type="doc"
        )
        
        # Генерируем embedding для summary (если есть)
        summary_embedding = None
        if document.summary and document.summary.summary_text:
            summary_embedding = await self._embedding.get_embedding(
                document.summary.summary_text, embedding_type="doc"
            )
        
        return VectorizedDocument(
            enriched=document,
            chunk_embeddings=chunk_embeddings,
            summary_embedding=summary_embedding,
        )
    
    async def _store(
        self,
        vault_name: str,
        document: VectorizedDocument,
    ) -> None:
        """Phase 5: Сохранение в LanceDB."""
        # Конвертируем в DocumentChunk для сохранения
        document_chunks = []
        
        for i, (enriched_chunk, embedding) in enumerate(
            zip(document.enriched.enriched_chunks, document.chunk_embeddings)
        ):
            chunk_info = enriched_chunk.chunk_info
            processed = document.enriched.processed

            # Используем относительный путь для хранения в БД
            # (относительный путь внутри vault'а, без пробелов на краях)
            relative_path_str = str(processed.relative_path)

            # Создаём DocumentChunk
            chunk_id = f"{vault_name}::{relative_path_str}::{i}"

            # Извлекаем теги и ссылки из контента
            inline_tags = self._extract_inline_tags(chunk_info.text)
            links = self._extract_wikilinks(chunk_info.text)

            document_chunk = DocumentChunk(
                id=chunk_id,
                vault_name=vault_name,
                file_path=relative_path_str,
                title=processed.title,
                section=chunk_info.headers[-1] if chunk_info.headers else "",
                content=chunk_info.text,
                tags=processed.frontmatter_data.tags or [],
                frontmatter_tags=processed.frontmatter_data.tags or [],
                inline_tags=inline_tags,
                links=links,
                created_at=processed.frontmatter_data.created_at,
                modified_at=processed.frontmatter_data.modified_at or datetime.now(),
                metadata=processed.metadata,
            )
            
            document_chunks.append(document_chunk)
        
        # Сохраняем чанки через репозиторий
        # Нужно конвертировать DocumentChunk в Chunk для репозитория
        from obsidian_kb.types import Chunk
        
        chunks = []
        for doc_chunk, embedding in zip(document_chunks, document.chunk_embeddings):
            chunk = Chunk(
                chunk_id=doc_chunk.id,
                document_id=f"{vault_name}::{doc_chunk.file_path}",
                vault_name=vault_name,
                chunk_index=document_chunks.index(doc_chunk),
                section=doc_chunk.section,
                content=doc_chunk.content,
                vector=embedding,
                inline_tags=doc_chunk.inline_tags,
                links=doc_chunk.links,
            )
            chunks.append(chunk)
        
        await self._chunks.upsert(vault_name, chunks)
        
        logger.debug(
            f"Stored {len(chunks)} chunks for document {document.enriched.processed.relative_path}"
        )
    
    def _extract_inline_tags(self, text: str) -> list[str]:
        """Извлечение inline тегов из текста."""
        import re
        pattern = r"#([\w-]+)"
        return re.findall(pattern, text)
    
    def _extract_wikilinks(self, text: str) -> list[str]:
        """Извлечение wikilinks из текста."""
        import re
        pattern = r"\[\[([^\]]+)\]\]"
        matches = re.findall(pattern, text)
        return [m.split("|")[0].strip() for m in matches]
    
    def get_job(self, job_id: str) -> IndexingJob | None:
        """Получение задачи по ID."""
        return self._jobs.get(job_id)

