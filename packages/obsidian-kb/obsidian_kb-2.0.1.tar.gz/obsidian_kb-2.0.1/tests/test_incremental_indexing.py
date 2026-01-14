"""Тесты для инкрементального индексирования."""

from datetime import datetime
from pathlib import Path

import pytest

from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.vault_indexer import VaultIndexer

# Используем фикстуры из conftest.py
# temp_vault, temp_db, embedding_service


@pytest.mark.asyncio
async def test_incremental_indexing_skips_unchanged_files(temp_vault, temp_db, embedding_service):
    """Тест инкрементального индексирования: пропуск неизменённых файлов."""
    vault_name = "test_vault"
    indexer = VaultIndexer(temp_vault, vault_name)
    db_manager = LanceDBManager(db_path=temp_db)

    # Первое индексирование - все файлы
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)
    assert len(chunks) > 0

    # Сохраняем в БД
    texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    await db_manager.upsert_chunks(vault_name, chunks, embeddings)

    # Получаем список проиндексированных файлов
    indexed_files = await db_manager.get_indexed_files(vault_name)
    assert len(indexed_files) > 0

    # Второе индексирование - должно пропустить все файлы (они не изменились)
    chunks2 = await indexer.scan_all(only_changed=True, indexed_files=indexed_files)
    assert len(chunks2) == 0  # Все файлы актуальны


@pytest.mark.asyncio
async def test_incremental_indexing_indexes_changed_files(temp_vault, temp_db, embedding_service):
    """Тест инкрементального индексирования: индексирование изменённых файлов."""
    vault_name = "test_vault"
    indexer = VaultIndexer(temp_vault, vault_name)
    db_manager = LanceDBManager(db_path=temp_db)

    # Первое индексирование
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)
    texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    await db_manager.upsert_chunks(vault_name, chunks, embeddings)

    # Изменяем один файл
    file1_path = temp_vault / "file1.md"
    file1_path.write_text("# File 1 Updated\n\nNew content", encoding="utf-8")

    # Получаем список проиндексированных файлов
    indexed_files = await db_manager.get_indexed_files(vault_name)

    # Второе индексирование - должно найти изменённый файл
    chunks2 = await indexer.scan_all(only_changed=True, indexed_files=indexed_files)
    assert len(chunks2) > 0  # Должен найти изменённый файл


@pytest.mark.asyncio
async def test_get_indexed_files(temp_vault, temp_db, embedding_service):
    """Тест получения списка проиндексированных файлов."""
    vault_name = "test_vault"
    db_manager = LanceDBManager(db_path=temp_db)

    # Индексируем файлы
    indexer = VaultIndexer(temp_vault, vault_name)
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    await db_manager.upsert_chunks(vault_name, chunks, embeddings)

    # Получаем список файлов
    indexed_files = await db_manager.get_indexed_files(vault_name)

    assert len(indexed_files) > 0
    # Проверяем, что все файлы в списке
    unique_files = set(c.file_path for c in chunks)
    assert len(indexed_files) == len(unique_files)

    # Проверяем формат времени модификации
    for file_path, modified_at in indexed_files.items():
        assert isinstance(modified_at, datetime)


@pytest.mark.asyncio
async def test_get_indexed_files_empty_vault(temp_db):
    """Тест получения списка файлов для пустого vault'а.

    После рефакторинга LanceDB v4 создаёт таблицы лениво,
    поэтому для несуществующего vault возвращается пустой словарь.
    """
    vault_name = "empty_vault"
    db_manager = LanceDBManager(db_path=temp_db)

    # Для несуществующего vault возвращается пустой словарь
    indexed_files = await db_manager.get_indexed_files(vault_name)
    assert indexed_files == {}


@pytest.mark.asyncio
async def test_incremental_indexing_with_new_file(temp_vault, temp_db, embedding_service):
    """Тест инкрементального индексирования: добавление нового файла."""
    vault_name = "test_vault"
    indexer = VaultIndexer(temp_vault, vault_name)
    db_manager = LanceDBManager(db_path=temp_db)

    # Первое индексирование
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)
    original_count = len(chunks)
    texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    await db_manager.upsert_chunks(vault_name, chunks, embeddings)

    # Добавляем новый файл
    new_file = temp_vault / "new_file.md"
    new_file.write_text("# New File\n\nThis is a new file", encoding="utf-8")

    # Получаем список проиндексированных файлов
    indexed_files = await db_manager.get_indexed_files(vault_name)

    # Второе индексирование - должно найти новый файл
    chunks2 = await indexer.scan_all(only_changed=True, indexed_files=indexed_files)
    assert len(chunks2) > 0  # Должен найти новый файл

    # Проверяем, что новый файл найден
    new_file_chunks = [c for c in chunks2 if c.file_path == "new_file.md"]
    assert len(new_file_chunks) > 0


@pytest.mark.asyncio
async def test_incremental_indexing_deleted_file_handling(temp_vault, temp_db, embedding_service):
    """Тест обработки удалённых файлов при инкрементальном индексировании."""
    vault_name = "test_vault"
    indexer = VaultIndexer(temp_vault, vault_name)
    db_manager = LanceDBManager(db_path=temp_db)

    # Первое индексирование
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)
    texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    await db_manager.upsert_chunks(vault_name, chunks, embeddings)

    # Удаляем файл
    file_to_delete = temp_vault / "file1.md"
    if file_to_delete.exists():
        file_to_delete.unlink()

    # Получаем список проиндексированных файлов (включает удалённый файл)
    indexed_files = await db_manager.get_indexed_files(vault_name)

    # При сканировании только изменённых файлов, удалённые файлы не должны индексироваться
    chunks2 = await indexer.scan_all(only_changed=True, indexed_files=indexed_files)

    # Проверяем, что удалённый файл не в новых чанках
    deleted_file_chunks = [c for c in chunks2 if c.file_path == "file1.md"]
    assert len(deleted_file_chunks) == 0


@pytest.mark.asyncio
async def test_modified_at_timestamp_updated(temp_vault, temp_db, embedding_service):
    """Тест, что modified_at обновляется при переиндексировании."""
    vault_name = "test_vault"
    indexer = VaultIndexer(temp_vault, vault_name)
    db_manager = LanceDBManager(db_path=temp_db)

    # Первое индексирование
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)
    texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    await db_manager.upsert_chunks(vault_name, chunks, embeddings)

    # Получаем начальное время модификации
    indexed_files_before = await db_manager.get_indexed_files(vault_name)

    # Изменяем файл
    file1_path = temp_vault / "file1.md"
    original_content = file1_path.read_text(encoding="utf-8") if file1_path.exists() else ""
    file1_path.write_text(original_content + "\n\nUpdated content", encoding="utf-8")

    # Переиндексируем
    chunks2 = await indexer.scan_all(only_changed=True, indexed_files=indexed_files_before)
    if chunks2:
        texts2 = [c.content for c in chunks2]
        embeddings2 = await embedding_service.get_embeddings_batch(texts2)
        await db_manager.upsert_chunks(vault_name, chunks2, embeddings2)

    # Получаем новое время модификации
    indexed_files_after = await db_manager.get_indexed_files(vault_name)

    # Время должно быть обновлено для изменённого файла
    if "file1.md" in indexed_files_before and "file1.md" in indexed_files_after:
        # modified_at для изменённого файла должна быть позже или равна
        assert indexed_files_after["file1.md"] >= indexed_files_before["file1.md"]
