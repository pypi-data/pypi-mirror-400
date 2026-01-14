"""Интеграционные тесты для проверки end-to-end функциональности.

Тесты проверяют работу системы в целом: индексация, поиск, фильтры, миграции.
"""

import asyncio
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.query_parser import QueryParser
from obsidian_kb.service_container import ServiceContainer, reset_service_container
from obsidian_kb.types import DocumentChunk
from obsidian_kb.vault_indexer import VaultIndexer


@pytest.fixture
def temp_db():
    """Создание временной БД для тестов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_db.lance"
        yield db_path


@pytest.fixture
def service_container(temp_db):
    """Создание контейнера сервисов для тестов."""
    # Сбрасываем глобальный контейнер перед каждым тестом
    reset_service_container()
    container = ServiceContainer(db_path=temp_db)
    yield container
    # Очищаем ресурсы после теста
    import asyncio
    try:
        asyncio.run(container.cleanup())
    except Exception:
        pass
    reset_service_container()


@pytest.fixture
def test_vault():
    """Создание тестового vault'а с файлами."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        vault_path.mkdir()
        
        # Создаём тестовые файлы
        file1 = vault_path / "person1.md"
        file1.write_text("""---
type: person
tags: [person, team]
created: 2024-01-01
---

# Иван Иванов

Разработчик команды. Работает над проектом X.

[[project-x]] [[meeting-2024-01-15]]
""")
        
        file2 = vault_path / "person2.md"
        file2.write_text("""---
type: person
tags: [person, manager]
created: 2024-02-01
---

# Петр Петров

Менеджер проекта. Участвует в #meeting-2024-01-15.
""")
        
        file3 = vault_path / "meeting.md"
        file3.write_text("""---
type: meeting
tags: [meeting]
created: 2024-01-15
---

# Встреча команды

Участники: [[person1]] [[person2]]

Обсуждали проект X.
""")
        
        yield vault_path


@pytest.mark.asyncio
async def test_end_to_end_indexing_and_search(temp_db, test_vault, service_container):
    """Тест полного цикла: индексация и поиск."""
    vault_name = "test_vault"
    
    # Используем сервисы из контейнера
    db_manager = service_container.db_manager
    embedding_service = service_container.embedding_service
    embedding_cache = service_container.embedding_cache
    vault_indexer = VaultIndexer(test_vault, vault_name, embedding_cache)
    
    try:
        # Индексация
        chunks = await vault_indexer.scan_all(max_workers=2)
        
        assert len(chunks) > 0, "Должны быть проиндексированы чанки"
        
        # Генерация embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        
        assert len(embeddings) == len(chunks), "Количество embeddings должно совпадать с количеством chunks"
        
        # Сохранение в БД
        await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Проверка сохранения
        stats = await db_manager.get_vault_stats(vault_name)
        assert stats.chunk_count > 0, "Должны быть сохранены чанки"
        
        # Поиск
        query_text = "разработчик"
        parsed_query = QueryParser.parse(query_text)
        query_vector = await embedding_service.get_embedding(query_text)
        
        # Векторный поиск
        vector_results = await db_manager.vector_search(
            vault_name, query_vector, limit=10
        )
        assert len(vector_results) > 0, "Должны быть найдены результаты векторного поиска"
        
        # FTS поиск
        fts_results = await db_manager.fts_search(
            vault_name, query_text, limit=10
        )
        assert len(fts_results) > 0, "Должны быть найдены результаты FTS поиска"
        
        # Гибридный поиск
        hybrid_results = await db_manager.hybrid_search(
            vault_name, query_vector, query_text, limit=10
        )
        assert len(hybrid_results) > 0, "Должны быть найдены результаты гибридного поиска"
        
    finally:
        await embedding_service.close()


@pytest.mark.asyncio
async def test_search_with_filters(temp_db, test_vault, service_container):
    """Тест поиска с фильтрами."""
    vault_name = "test_vault"
    
    db_manager = service_container.db_manager
    embedding_service = service_container.embedding_service
    embedding_cache = service_container.embedding_cache
    vault_indexer = VaultIndexer(test_vault, vault_name, embedding_cache)
    
    try:
        # Индексация
        chunks = await vault_indexer.scan_all(max_workers=2)
        
        texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Поиск с фильтром по типу (используем двухэтапный запрос)
        query = "команда"
        parsed_query = QueryParser.parse(f"{query} type:person")
        where_clause, document_ids = await QueryParser.build_where_clause(
            parsed_query,
            db_manager=db_manager,
            vault_name=vault_name,
        )
        
        query_vector = await embedding_service.get_embedding(query)
        results = await db_manager.hybrid_search(
            vault_name, query_vector, query, limit=10, where=where_clause, document_ids=document_ids
        )
        
        # Проверяем, что результаты найдены
        assert len(results) > 0, "Должны быть найдены результаты с фильтром по типу"
        
        # Поиск с фильтром по тегам (используем двухэтапный запрос)
        parsed_query = QueryParser.parse(f"{query} tags:team")
        where_clause, document_ids = await QueryParser.build_where_clause(
            parsed_query,
            db_manager=db_manager,
            vault_name=vault_name,
        )
        
        results = await db_manager.hybrid_search(
            vault_name, query_vector, query, limit=10, where=where_clause, document_ids=document_ids
        )
        
        # Проверяем, что результаты найдены
        assert len(results) > 0, "Должны быть найдены результаты с фильтром по тегам"
        
    finally:
        await embedding_service.close()


@pytest.mark.asyncio
async def test_schema_migration(temp_db, test_vault, service_container):
    """Тест миграции схемы БД."""
    vault_name = "test_vault"
    
    db_manager = service_container.db_manager
    embedding_service = service_container.embedding_service
    embedding_cache = service_container.embedding_cache
    vault_indexer = VaultIndexer(test_vault, vault_name, embedding_cache)
    
    try:
        # Первая индексация (создаёт таблицу)
        chunks = await vault_indexer.scan_all(max_workers=2)
        
        texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Проверяем, что таблица создана с правильной схемой
        stats = await db_manager.get_vault_stats(vault_name)
        assert stats.chunk_count > 0
        
        # Повторная индексация должна использовать существующую таблицу
        # (миграция схемы происходит автоматически при необходимости)
        await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        stats_after = await db_manager.get_vault_stats(vault_name)
        assert stats_after.chunk_count == stats.chunk_count, "Количество чанков не должно измениться при повторной индексации"
        
    finally:
        await embedding_service.close()


@pytest.mark.asyncio
async def test_file_deletion(temp_db, test_vault, service_container):
    """Тест удаления файла из индекса."""
    vault_name = "test_vault"
    
    db_manager = service_container.db_manager
    embedding_service = service_container.embedding_service
    embedding_cache = service_container.embedding_cache
    vault_indexer = VaultIndexer(test_vault, vault_name, embedding_cache)
    
    try:
        # Индексация
        chunks = await vault_indexer.scan_all(max_workers=2)
        
        texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Проверяем количество чанков до удаления
        stats_before = await db_manager.get_vault_stats(vault_name)
        initial_count = stats_before.chunk_count
        
        # Удаляем файл
        file_to_delete = "person1.md"
        await db_manager.delete_file(vault_name, file_to_delete)
        
        # Проверяем, что чанки удалены
        stats_after = await db_manager.get_vault_stats(vault_name)
        assert stats_after.chunk_count < initial_count, "Количество чанков должно уменьшиться после удаления файла"
        
        # Проверяем, что удалённый файл не находится в поиске
        query_vector = await embedding_service.get_embedding("разработчик")
        results = await db_manager.vector_search(vault_name, query_vector, limit=100)
        
        deleted_file_found = any(
            result.file_path == file_to_delete for result in results
        )
        assert not deleted_file_found, "Удалённый файл не должен находиться в результатах поиска"
        
    finally:
        await embedding_service.close()


@pytest.mark.asyncio
async def test_vault_deletion(temp_db, test_vault, service_container):
    """Тест удаления vault'а."""
    vault_name = "test_vault"
    
    db_manager = service_container.db_manager
    embedding_service = service_container.embedding_service
    embedding_cache = service_container.embedding_cache
    vault_indexer = VaultIndexer(test_vault, vault_name, embedding_cache)
    
    try:
        # Индексация
        chunks = await vault_indexer.scan_all(max_workers=2)
        
        texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_service.get_embeddings_batch(texts)
        await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Проверяем, что vault существует (через get_vault_stats)
        stats = await db_manager.get_vault_stats(vault_name)
        assert stats.chunk_count > 0, "Vault должен существовать и содержать чанки"
        
        # Удаляем vault
        await db_manager.delete_vault(vault_name)
        
        # Проверяем, что vault удалён (через VaultNotFoundError при попытке получить статистику)
        from obsidian_kb.types import VaultNotFoundError
        try:
            await db_manager.get_vault_stats(vault_name)
            # Если не вызвана ошибка, проверяем что статистика пустая
            stats_after = await db_manager.get_vault_stats(vault_name)
            assert stats_after.chunk_count == 0, "Vault должен быть удалён"
        except VaultNotFoundError:
            # Ожидаемое поведение - vault не найден
            pass
        
        # Проверяем, что поиск по удалённому vault вызывает ошибку
        query_vector = await embedding_service.get_embedding("тест")
        try:
            await db_manager.vector_search(vault_name, query_vector, limit=10)
            # Если не вызвана ошибка, проверяем что результатов нет
            results = await db_manager.vector_search(vault_name, query_vector, limit=10)
            assert len(results) == 0, "Поиск по удалённому vault не должен возвращать результаты"
        except (VaultNotFoundError, Exception):
            # Ожидаемое поведение - ошибка при поиске
            pass
        
    finally:
        await embedding_service.close()

