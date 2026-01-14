"""Утилиты для индексации в тестах."""

from pathlib import Path
from typing import Any

from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.service_container import ServiceContainer
from obsidian_kb.vault_indexer import VaultIndexer


async def index_vault_for_tests(
    services: ServiceContainer,
    vault_path: Path,
    vault_name: str,
    only_changed: bool = False,
) -> dict[str, Any]:
    """Индексация vault'а для тестов.
    
    Args:
        services: Контейнер сервисов
        vault_path: Путь к vault'у
        vault_name: Имя vault'а
        only_changed: Индексировать только изменённые файлы
        
    Returns:
        Результаты индексации с ключами:
        - success: bool - успешность индексации
        - vault_name: str - имя vault'а
        - vault_path: Path - путь к vault'у
        - files_indexed: int - количество проиндексированных файлов
        - chunks_indexed: int - количество проиндексированных чанков
        - tags_found: int - количество найденных тегов
    """
    indexer = VaultIndexer(vault_path, vault_name)
    embedding_cache = EmbeddingCache()
    
    chunks, embeddings, stats = await index_with_cache(
        vault_name=vault_name,
        indexer=indexer,
        embedding_service=services.embedding_service,
        db_manager=services.db_manager,
        embedding_cache=embedding_cache,
        only_changed=only_changed,
    )
    
    await services.db_manager.upsert_chunks(vault_name, chunks, embeddings)
    
    vault_stats = await services.db_manager.get_vault_stats(vault_name)
    
    return {
        "success": True,
        "vault_name": vault_name,
        "vault_path": vault_path,
        "files_indexed": vault_stats.file_count,
        "chunks_indexed": vault_stats.chunk_count,
        "tags_found": len(vault_stats.tags),
    }

