"""Тесты для индексирования с использованием кэша."""

import asyncio
from pathlib import Path

import pytest

from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.vault_indexer import VaultIndexer


@pytest.mark.asyncio
async def test_index_with_cache_hit(temp_db, temp_vault, embedding_service):
    """Тест индексирования с попаданием в кэш."""
    # Создаём тестовый файл
    test_file = temp_vault / "test.md"
    test_file.write_text("# Test\nContent here", encoding="utf-8")
    
    db_manager = LanceDBManager(db_path=temp_db)
    embedding_cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    indexer = VaultIndexer(temp_vault, "test_vault", embedding_cache=embedding_cache)
    
    # Первое индексирование (без кэша)
    chunks1, embeddings1, stats1 = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=embedding_cache,
        only_changed=False,
        indexed_files=None,
    )
    
    assert len(chunks1) > 0
    assert len(embeddings1) == len(chunks1)
    assert stats1["computed"] > 0
    assert stats1["cached"] == 0
    
    # Второе индексирование (с кэшем)
    chunks2, embeddings2, stats2 = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=embedding_cache,
        only_changed=False,
        indexed_files=None,
    )
    
    assert len(chunks2) == len(chunks1)
    assert len(embeddings2) == len(embeddings1)
    # Должны использоваться кэшированные embeddings
    assert stats2["cached"] > 0
    assert stats2["computed"] == 0
    
    # Embeddings должны совпадать
    assert embeddings2 == embeddings1


@pytest.mark.asyncio
async def test_index_with_cache_miss(temp_db, temp_vault, embedding_service):
    """Тест индексирования с промахом кэша (файл изменён)."""
    # Создаём тестовый файл
    test_file = temp_vault / "test.md"
    test_file.write_text("# Test\nContent", encoding="utf-8")
    
    db_manager = LanceDBManager(db_path=temp_db)
    embedding_cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    indexer = VaultIndexer(temp_vault, "test_vault", embedding_cache=embedding_cache)
    
    # Первое индексирование
    chunks1, embeddings1, stats1 = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=embedding_cache,
        only_changed=False,
        indexed_files=None,
    )
    
    # Изменяем файл
    test_file.write_text("# Test\nModified Content", encoding="utf-8")
    
    # Второе индексирование (файл изменён, кэш недействителен)
    chunks2, embeddings2, stats2 = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=embedding_cache,
        only_changed=False,
        indexed_files=None,
    )
    
    # Должны быть вычислены новые embeddings (файл изменён, хеш не совпадает)
    assert stats2["computed"] > 0
    # Примечание: в temp_vault могут быть другие файлы из conftest.py, для которых кэш используется
    # Поэтому проверяем, что хотя бы для изменённого файла embeddings были вычислены заново
    # (кэш не должен использоваться для изменённого файла из-за изменения хеша)
    assert len(chunks2) > 0


@pytest.mark.asyncio
async def test_index_without_cache(temp_db, temp_vault, embedding_service):
    """Тест индексирования без кэша."""
    test_file = temp_vault / "test.md"
    test_file.write_text("# Test\nContent", encoding="utf-8")
    
    db_manager = LanceDBManager(db_path=temp_db)
    indexer = VaultIndexer(temp_vault, "test_vault")
    
    # Индексирование без кэша
    chunks, embeddings, stats = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=None,  # Без кэша
        only_changed=False,
        indexed_files=None,
    )
    
    assert len(chunks) > 0
    assert len(embeddings) == len(chunks)
    assert stats["computed"] > 0
    assert stats["cached"] == 0


@pytest.mark.asyncio
async def test_index_with_cache_max_workers(temp_db, temp_vault, embedding_service):
    """Тест индексирования с max_workers параметром."""
    # Создаём несколько файлов для параллельной обработки
    for i in range(10):
        test_file = temp_vault / f"test_{i}.md"
        test_file.write_text(f"# Test {i}\nContent {i}", encoding="utf-8")
    
    db_manager = LanceDBManager(db_path=temp_db)
    embedding_cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    indexer = VaultIndexer(temp_vault, "test_vault", embedding_cache=embedding_cache)
    
    # Индексирование с разными значениями max_workers
    chunks1, embeddings1, stats1 = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=embedding_cache,
        only_changed=False,
        indexed_files=None,
        max_workers=3,
    )
    
    chunks2, embeddings2, stats2 = await index_with_cache(
        vault_name="test_vault",
        indexer=indexer,
        embedding_service=embedding_service,
        db_manager=db_manager,
        embedding_cache=embedding_cache,
        only_changed=False,
        indexed_files=None,
        max_workers=15,
    )
    
    # Результаты должны быть одинаковыми независимо от max_workers
    assert len(chunks1) == len(chunks2)
    assert len(embeddings1) == len(embeddings2)
    assert stats1["total_files"] == stats2["total_files"]

