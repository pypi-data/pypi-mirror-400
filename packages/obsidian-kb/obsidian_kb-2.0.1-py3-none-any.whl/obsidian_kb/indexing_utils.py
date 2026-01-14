"""Утилиты для индексирования с поддержкой кэширования embeddings."""

import asyncio
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.types import DocumentChunk
from obsidian_kb.vault_indexer import VaultIndexer

logger = logging.getLogger(__name__)


async def index_with_cache(
    vault_name: str,
    indexer: VaultIndexer,
    embedding_service: EmbeddingService,
    db_manager: LanceDBManager,
    embedding_cache: EmbeddingCache | None = None,
    only_changed: bool = False,
    indexed_files: dict[str, Any] | None = None,
    max_workers: int | None = None,
    enable_enrichment: bool = True,
    only_new_chunks: bool = False,
    enable_clustering: bool = True,
) -> tuple[list[DocumentChunk], list[list[float]], dict[str, Any]]:
    """Индексирование vault'а с использованием кэша embeddings.

    Args:
        vault_name: Имя vault'а
        indexer: Индексатор vault'а
        embedding_service: Сервис для генерации embeddings
        db_manager: Менеджер базы данных
        embedding_cache: Кэш embeddings (опционально)
        only_changed: Индексировать только изменённые файлы
        indexed_files: Словарь проиндексированных файлов для сравнения
        max_workers: Максимальное количество параллельных файлов (по умолчанию из settings)
        enable_enrichment: Включить LLM-обогащение чанков
        only_new_chunks: Обогащать только новые чанки (игнорировать кэш обогащений)
        enable_clustering: Включить кластеризацию документов

    Returns:
        Кортеж (chunks, embeddings, stats) где stats содержит информацию о кэше и обогащении
    """
    # Сканируем файлы
    chunks = await indexer.scan_all(only_changed=only_changed, indexed_files=indexed_files, max_workers=max_workers)

    if not chunks:
        return [], [], {"cached": 0, "computed": 0, "total_files": 0, "enrichment": {"enriched": 0, "skipped": 0, "errors": 0}}

    # Группируем чанки по файлам
    # Используем абсолютные пути для корректной работы с кэшем
    chunks_by_file: dict[str, list[DocumentChunk]] = defaultdict(list)
    vault_path = indexer.vault_path
    
    for chunk in chunks:
        # Строим абсолютный путь к файлу
        chunk_file_path = (vault_path / chunk.file_path).resolve()
        chunks_by_file[str(chunk_file_path)].append(chunk)

    # Сортируем чанки в каждом файле по порядку
    for file_path in chunks_by_file:
        chunks_by_file[file_path].sort(key=lambda c: c.content)

    stats = {"cached": 0, "computed": 0, "total_files": len(chunks_by_file)}

    all_embeddings: list[list[float]] = []
    chunks_to_index: list[DocumentChunk] = []
    files_to_cache: dict[str, tuple[list[DocumentChunk], list[int]]] = {}

    # Проверяем кэш для каждого файла
    if embedding_cache:
        for file_path, file_chunks in chunks_by_file.items():
            file_path_obj = Path(file_path)
            chunk_count = len(file_chunks)

            # Пытаемся получить кэшированные embeddings
            cached_embeddings = await embedding_cache.get_cached_embeddings(
                vault_name, file_path_obj, chunk_count
            )

            if cached_embeddings and len(cached_embeddings) == chunk_count:
                # Кэш найден, используем его
                all_embeddings.extend(cached_embeddings)
                chunks_to_index.extend(file_chunks)
                stats["cached"] += chunk_count
                logger.debug(f"Using cached embeddings for {file_path} ({chunk_count} chunks)")
            else:
                # Кэш не найден или неполный, нужно вычислить
                chunk_indices = list(range(len(file_chunks)))
                files_to_cache[file_path] = (file_chunks, chunk_indices)
                stats["computed"] += chunk_count
    else:
        # Кэш не используется, вычисляем все embeddings
        for file_path, file_chunks in chunks_by_file.items():
            files_to_cache[file_path] = (file_chunks, list(range(len(file_chunks))))
            stats["computed"] += len(file_chunks)

    # Вычисляем embeddings для файлов без кэша
    if files_to_cache:
        texts_to_compute: list[str] = []
        chunk_mapping: list[tuple[str, int]] = []  # (file_path, chunk_index_in_file)

        for file_path, (file_chunks, chunk_indices) in files_to_cache.items():
            for chunk_idx, chunk in enumerate(file_chunks):
                texts_to_compute.append(chunk.content)
                chunk_mapping.append((file_path, chunk_idx))

        # Вычисляем embeddings батчами (параллельно)
        from obsidian_kb.config import settings
        batch_size = settings.batch_size
        computed_embeddings: list[list[float]] = []

        if len(texts_to_compute) > batch_size:
            # Обрабатываем батчи параллельно для ускорения
            batch_tasks = []
            for i in range(0, len(texts_to_compute), batch_size):
                batch_texts = texts_to_compute[i:i + batch_size]
                batch_tasks.append(embedding_service.get_embeddings_batch(batch_texts))
            
            # Выполняем все батчи параллельно
            batch_results = await asyncio.gather(*batch_tasks)
            for batch_result in batch_results:
                computed_embeddings.extend(batch_result)
            
            logger.debug(f"Computed {len(computed_embeddings)} embeddings in {len(batch_tasks)} parallel batches")
        else:
            computed_embeddings = await embedding_service.get_embeddings_batch(texts_to_compute)

        # Распределяем embeddings по файлам и сохраняем в кэш
        embedding_idx = 0
        for file_path, (file_chunks, chunk_indices) in files_to_cache.items():
            file_embeddings: list[list[float]] = []
            file_chunk_indices: list[int] = []

            for chunk_idx in range(len(file_chunks)):
                file_embeddings.append(computed_embeddings[embedding_idx])
                file_chunk_indices.append(chunk_idx)
                embedding_idx += 1

            # Сохраняем в кэш
            if embedding_cache:
                file_path_obj = Path(file_path)
                await embedding_cache.cache_embeddings(
                    vault_name, file_path_obj, file_chunk_indices, file_embeddings
                )

            # Добавляем embeddings и чанки
            all_embeddings.extend(file_embeddings)
            chunks_to_index.extend(file_chunks)

    # Убеждаемся, что порядок чанков и embeddings совпадает
    assert len(chunks_to_index) == len(all_embeddings), "Mismatch between chunks and embeddings"

    # LLM-обогащение чанков (если включено)
    enrichment_stats = {"enriched": 0, "skipped": 0, "errors": 0}
    if enable_enrichment and chunks_to_index:
        try:
            from obsidian_kb.config import settings
            from obsidian_kb.service_container import get_service_container
            
            # Проверяем, включено ли обогащение в настройках
            if settings.enable_llm_enrichment:
                services = get_service_container()
                llm_service = services.llm_enrichment_service
                
                # Проверяем доступность LLM
                if await llm_service.health_check():
                    # Определяем, какие чанки нужно обогащать
                    chunks_to_enrich = chunks_to_index
                    if only_new_chunks:
                        # Фильтруем только новые чанки (те, которые не были в кэше embeddings)
                        # Это упрощенная логика - в реальности нужно проверять кэш обогащений
                        # Но для Этапа 4 используем только новые чанки из computed
                        chunks_to_enrich = chunks_to_index
                    
                    if chunks_to_enrich:
                        logger.info(f"Enriching {len(chunks_to_enrich)} chunks with LLM...")
                        try:
                            enrichments = await llm_service.enrich_chunks_batch(chunks_to_enrich)
                            enrichment_stats["enriched"] = len(enrichments)
                            logger.info(f"Successfully enriched {len(enrichments)} chunks")
                        except Exception as e:
                            logger.error(f"Error during enrichment: {e}", exc_info=True)
                            enrichment_stats["errors"] = len(chunks_to_enrich)
                            # Graceful degradation: продолжаем индексацию без обогащения
                else:
                    logger.warning("LLM not available, skipping enrichment")
                    enrichment_stats["skipped"] = len(chunks_to_index)
            else:
                logger.debug("LLM enrichment disabled in settings")
                enrichment_stats["skipped"] = len(chunks_to_index)
        except Exception as e:
            logger.error(f"Failed to initialize enrichment service: {e}", exc_info=True)
            enrichment_stats["errors"] = len(chunks_to_index)
            # Graceful degradation: продолжаем индексацию без обогащения
    
    # Добавляем статистику обогащения в stats
    stats["enrichment"] = enrichment_stats
    
    # Кластеризация документов (если включено)
    clustering_stats = {"clustered": 0, "skipped": 0, "errors": 0}
    if enable_clustering and chunks_to_index:
        try:
            from obsidian_kb.config import settings
            from obsidian_kb.service_container import get_service_container
            
            # Проверяем, включена ли кластеризация в настройках
            if settings.enable_knowledge_clusters:
                services = get_service_container()
                cluster_service = services.knowledge_cluster_service
                
                logger.info("Clustering documents...")
                try:
                    clusters = await cluster_service.cluster_documents(vault_name)
                    
                    # Сохранение через репозиторий
                    cluster_repo = services.knowledge_cluster_repository
                    await cluster_repo.upsert(vault_name, clusters)
                    
                    clustering_stats["clustered"] = len(clusters)
                    logger.info(f"Created {len(clusters)} knowledge clusters")
                except Exception as e:
                    logger.error(f"Clustering failed: {e}", exc_info=True)
                    clustering_stats["errors"] = 1
                    # Graceful degradation: продолжаем без кластеризации
            else:
                logger.debug("Knowledge clustering disabled in settings")
                clustering_stats["skipped"] = 1
        except Exception as e:
            logger.error(f"Failed to initialize clustering service: {e}", exc_info=True)
            clustering_stats["errors"] = 1
            # Graceful degradation: продолжаем без кластеризации
    
    # Добавляем статистику кластеризации в stats
    stats["clustering"] = clustering_stats

    return chunks_to_index, all_embeddings, stats

