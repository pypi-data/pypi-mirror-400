"""Тесты для модуля кэширования embeddings."""

import asyncio
from pathlib import Path

import pytest

from obsidian_kb.embedding_cache import EmbeddingCache


@pytest.mark.asyncio
async def test_cache_embeddings(temp_db, tmp_path):
    """Тест сохранения embeddings в кэш."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test\nContent", encoding="utf-8")
    
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    chunk_indices = [0, 1]
    
    await cache.cache_embeddings("test_vault", test_file, chunk_indices, embeddings)
    
    # Проверяем, что embeddings сохранены
    cached = await cache.get_cached_embeddings("test_vault", test_file, 2)
    assert cached is not None
    assert len(cached) == 2
    assert cached[0] == [0.1, 0.2, 0.3]
    assert cached[1] == [0.4, 0.5, 0.6]


@pytest.mark.asyncio
async def test_get_cached_embeddings_missing(temp_db, tmp_path):
    """Тест получения кэша для несуществующего файла."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file = tmp_path / "nonexistent.md"
    
    cached = await cache.get_cached_embeddings("test_vault", test_file, 2)
    assert cached is None


@pytest.mark.asyncio
async def test_get_cached_embeddings_wrong_hash(temp_db, tmp_path):
    """Тест получения кэша для изменённого файла."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test\nContent", encoding="utf-8")
    
    # Кэшируем embeddings
    embeddings = [[0.1, 0.2, 0.3]]
    await cache.cache_embeddings("test_vault", test_file, [0], embeddings)
    
    # Изменяем файл
    test_file.write_text("# Test\nModified Content", encoding="utf-8")
    
    # Кэш должен быть недействителен
    cached = await cache.get_cached_embeddings("test_vault", test_file, 1)
    assert cached is None


@pytest.mark.asyncio
async def test_invalidate_file(temp_db, tmp_path):
    """Тест инвалидации кэша для файла."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test\nContent", encoding="utf-8")
    
    # Кэшируем embeddings
    embeddings = [[0.1, 0.2, 0.3]]
    await cache.cache_embeddings("test_vault", test_file, [0], embeddings)
    
    # Проверяем, что кэш есть
    cached = await cache.get_cached_embeddings("test_vault", test_file, 1)
    assert cached is not None
    
    # Инвалидируем кэш
    await cache.invalidate_file("test_vault", test_file)
    
    # Проверяем, что кэш удалён
    cached = await cache.get_cached_embeddings("test_vault", test_file, 1)
    assert cached is None


@pytest.mark.asyncio
async def test_clear_vault_cache(temp_db, tmp_path):
    """Тест очистки всего кэша для vault'а."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file1 = tmp_path / "test1.md"
    test_file1.write_text("# Test 1", encoding="utf-8")
    test_file2 = tmp_path / "test2.md"
    test_file2.write_text("# Test 2", encoding="utf-8")
    
    # Кэшируем embeddings для обоих файлов
    await cache.cache_embeddings("test_vault", test_file1, [0], [[0.1, 0.2, 0.3]])
    await cache.cache_embeddings("test_vault", test_file2, [0], [[0.4, 0.5, 0.6]])
    
    # Очищаем кэш
    await cache.clear_vault_cache("test_vault")
    
    # Проверяем, что кэш очищен
    cached1 = await cache.get_cached_embeddings("test_vault", test_file1, 1)
    cached2 = await cache.get_cached_embeddings("test_vault", test_file2, 1)
    assert cached1 is None
    assert cached2 is None


@pytest.mark.asyncio
async def test_get_cache_stats(temp_db, tmp_path):
    """Тест получения статистики кэша."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file1 = tmp_path / "test1.md"
    test_file1.write_text("# Test 1", encoding="utf-8")
    test_file2 = tmp_path / "test2.md"
    test_file2.write_text("# Test 2", encoding="utf-8")
    
    # Кэшируем embeddings
    await cache.cache_embeddings("test_vault", test_file1, [0, 1], [[0.1], [0.2]])
    await cache.cache_embeddings("test_vault", test_file2, [0], [[0.3]])
    
    stats = await cache.get_cache_stats("test_vault")
    assert stats["cached_files"] == 2
    assert stats["total_embeddings"] == 3


@pytest.mark.asyncio
async def test_cache_multiple_chunks(temp_db, tmp_path):
    """Тест кэширования нескольких чанков одного файла."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test\n" + "Content " * 100, encoding="utf-8")
    
    embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    chunk_indices = [0, 1, 2]
    
    await cache.cache_embeddings("test_vault", test_file, chunk_indices, embeddings)
    
    # Получаем кэш
    cached = await cache.get_cached_embeddings("test_vault", test_file, 3)
    assert cached is not None
    assert len(cached) == 3
    assert cached == embeddings


@pytest.mark.asyncio
async def test_cache_partial_match(temp_db, tmp_path):
    """Тест, что кэш не используется если количество чанков не совпадает."""
    cache = EmbeddingCache(db_path=temp_db.parent / "embedding_cache.lance")
    
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test\nContent", encoding="utf-8")
    
    # Кэшируем 2 чанка
    await cache.cache_embeddings("test_vault", test_file, [0, 1], [[0.1], [0.2]])
    
    # Запрашиваем 1 чанк - кэш не должен использоваться
    cached = await cache.get_cached_embeddings("test_vault", test_file, 1)
    assert cached is None

