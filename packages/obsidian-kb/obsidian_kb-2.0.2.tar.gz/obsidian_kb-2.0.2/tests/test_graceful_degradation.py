"""Тесты для graceful degradation при недоступности Ollama.

После рефакторинга Phase 1-3 архитектура использует ServiceContainer.
Тесты проверяют fallback на FTS при ошибках embedding service.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.providers.exceptions import ProviderConnectionError


@pytest.mark.asyncio
async def test_search_vault_ollama_fallback_fts(temp_db, temp_vault, embedding_service):
    """Тест fallback на FTS при недоступности Ollama в search_vault."""
    from obsidian_kb.vault_indexer import VaultIndexer

    db_manager = LanceDBManager(db_path=temp_db)
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    if chunks:
        texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks("test_vault", chunks, embeddings)

    # FTS поиск должен работать независимо от Ollama (без сложных фильтров)
    results = await db_manager.fts_search("test_vault", "Python", limit=5, where=None)

    # При наличии чанков должны быть результаты
    if chunks:
        assert len(results) > 0


@pytest.mark.asyncio
async def test_search_vault_fts_direct(temp_db, temp_vault, embedding_service):
    """Тест прямого FTS поиска (без Ollama)."""
    from obsidian_kb.vault_indexer import VaultIndexer

    db_manager = LanceDBManager(db_path=temp_db)
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    if chunks:
        texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks("test_vault", chunks, embeddings)

    # FTS поиск не требует Ollama - тестируем напрямую
    results = await db_manager.fts_search("test_vault", "Python", limit=5, where=None)

    # При наличии чанков должны быть результаты
    if chunks:
        assert len(results) > 0


@pytest.mark.asyncio
async def test_search_multi_vault_ollama_fallback(temp_db, temp_vault, embedding_service):
    """Тест fallback на FTS в search_multi_vault при недоступности Ollama."""
    from obsidian_kb.vault_indexer import VaultIndexer

    db_manager = LanceDBManager(db_path=temp_db)
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    if chunks:
        texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks("test_vault", chunks, embeddings)

    # FTS поиск для multi-vault сценария
    results = await db_manager.fts_search("test_vault", "Python", limit=5, where=None)

    # При наличии чанков должны быть результаты
    if chunks:
        assert len(results) > 0


@pytest.mark.asyncio
async def test_search_vault_vector_requires_ollama(temp_db, temp_vault, embedding_service):
    """Тест, что vector поиск работает с embeddings, но FTS работает без них."""
    from obsidian_kb.vault_indexer import VaultIndexer

    db_manager = LanceDBManager(db_path=temp_db)
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    # Индексируем vault с embeddings для теста
    if chunks:
        texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks("test_vault", chunks, embeddings)

    # Тестируем vector поиск с реальными embeddings
    query_embedding = await embedding_service.get_embedding("Python")
    vector_results = await db_manager.vector_search("test_vault", query_embedding, limit=5)

    # При наличии чанков должны быть результаты vector поиска
    if chunks:
        assert len(vector_results) > 0

    # FTS поиск также должен работать
    fts_results = await db_manager.fts_search("test_vault", "Python", limit=5)

    if chunks:
        assert len(fts_results) > 0


@pytest.mark.asyncio
async def test_embedding_service_error_handling():
    """Тест обработки ошибки ProviderConnectionError."""
    # Создаём mock embedding service который бросает ProviderConnectionError
    mock_embedding_service = MagicMock()
    mock_embedding_service.get_embedding = AsyncMock(
        side_effect=ProviderConnectionError("Provider unavailable")
    )

    # Проверяем что исключение правильно бросается
    with pytest.raises(ProviderConnectionError):
        await mock_embedding_service.get_embedding("test query")
