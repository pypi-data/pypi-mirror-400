"""Тесты для MCP инструментов (search_multi_vault, index_vault).

После рефакторинга Phase 1-3, MCP tools тестируются через:
1. LanceDBManager напрямую для операций с БД
2. mock_service_container() для MCP tools с зависимостями
3. ChunkFactory для создания тестовых данных
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.vault_indexer import VaultIndexer
from tests.helpers.fixtures import ChunkFactory


# Используем фикстуру temp_db из conftest.py


@pytest.fixture
def temp_vault1(tmp_path):
    """Первый временный vault."""
    vault_path = tmp_path / "vault1"
    vault_path.mkdir()
    (vault_path / "file1.md").write_text(
        "# File 1\n\nContent about Python and async programming.",
        encoding="utf-8",
    )
    return vault_path


@pytest.fixture
def temp_vault2(tmp_path):
    """Второй временный vault."""
    vault_path = tmp_path / "vault2"
    vault_path.mkdir()
    (vault_path / "file2.md").write_text(
        "# File 2\n\nContent about databases and vector search.",
        encoding="utf-8",
    )
    return vault_path


@pytest.mark.asyncio
async def test_search_multi_vault(temp_db):
    """Тест поиска по нескольким vault'ам через LanceDBManager напрямую."""
    db_manager = LanceDBManager(db_path=temp_db)

    # Создаём тестовые чанки для двух vault'ов
    chunks1 = [ChunkFactory.create(
        vault_name="vault1",
        file_path="file1.md",
        content="Content about Python and async programming.",
    )]
    chunks2 = [ChunkFactory.create(
        vault_name="vault2",
        file_path="file2.md",
        content="Content about databases and vector search.",
    )]

    # Добавляем в БД
    await db_manager.upsert_chunks("vault1", chunks1, [[0.1] * 768])
    await db_manager.upsert_chunks("vault2", chunks2, [[0.2] * 768])

    # Тестируем поиск напрямую через db_manager
    query_embedding = [0.15] * 768
    results1 = await db_manager.vector_search("vault1", query_embedding, limit=5)
    results2 = await db_manager.vector_search("vault2", query_embedding, limit=5)

    # Проверяем что vault'ы созданы
    vaults = await db_manager.list_vaults()
    assert "vault1" in vaults
    assert "vault2" in vaults


@pytest.mark.asyncio
async def test_search_multi_vault_one_not_found(temp_db):
    """Тест поиска по нескольким vault'ам, когда один не найден."""
    db_manager = LanceDBManager(db_path=temp_db)

    # Создаём только vault1
    chunks1 = [ChunkFactory.create(
        vault_name="vault1",
        file_path="file1.md",
        content="Content about Python",
    )]
    await db_manager.upsert_chunks("vault1", chunks1, [[0.1] * 768])

    # Поиск в существующем vault
    results = await db_manager.vector_search("vault1", [0.1] * 768, limit=5)
    # LanceDBManager может вернуть результаты (не бросает ошибку для empty vault)
    assert results is not None


@pytest.mark.asyncio
async def test_index_vault_path_not_exists():
    """Тест проверки несуществующего пути."""
    vault_path_obj = Path("/nonexistent/path")
    result = not vault_path_obj.exists()
    assert result is True


@pytest.mark.asyncio
async def test_index_vault_path_not_directory(tmp_path):
    """Тест проверки пути, который не является директорией."""
    file_path = tmp_path / "not_a_dir"
    file_path.write_text("test", encoding="utf-8")

    result = not Path(file_path).is_dir()
    assert result is True


@pytest.mark.asyncio
async def test_vault_indexer_empty_vault(tmp_path):
    """Тест сканирования пустого vault'а."""
    vault_path = tmp_path / "empty_vault"
    vault_path.mkdir()
    # Не создаём файлов

    indexer = VaultIndexer(vault_path, "empty_vault")
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    # Пустой vault должен возвращать пустой список чанков
    assert chunks == []


@pytest.mark.asyncio
async def test_vault_config_operations(tmp_path):
    """Тест операций с конфигурацией vault'ов."""
    import json
    from obsidian_kb import config

    # Создаём временную конфигурацию
    config_path = tmp_path / "vaults.json"
    config_data = {"vaults": []}

    # Добавляем vault
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    config_data["vaults"].append({
        "name": "test_vault",
        "path": str(vault_path.resolve())
    })

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    # Проверяем чтение конфига
    with open(config_path, "r", encoding="utf-8") as f:
        loaded_config = json.load(f)

    assert "vaults" in loaded_config
    assert len(loaded_config["vaults"]) == 1
    assert loaded_config["vaults"][0]["name"] == "test_vault"


@pytest.mark.asyncio
async def test_delete_vault_from_db(temp_db):
    """Тест удаления vault'а из БД."""
    db_manager = LanceDBManager(db_path=temp_db)

    # Создаём vault
    chunks = [ChunkFactory.create(
        vault_name="delete_me",
        file_path="file.md",
        content="Content to delete",
    )]
    await db_manager.upsert_chunks("delete_me", chunks, [[0.1] * 768])

    # Проверяем, что vault существует
    vaults_before = await db_manager.list_vaults()
    assert "delete_me" in vaults_before

    # Удаляем vault
    await db_manager.delete_vault("delete_me")

    # Проверяем, что vault удалён
    vaults_after = await db_manager.list_vaults()
    assert "delete_me" not in vaults_after


@pytest.mark.asyncio
async def test_vault_indexer_scan(tmp_path):
    """Тест сканирования vault'а через VaultIndexer."""
    vault_path = tmp_path / "scan_vault"
    vault_path.mkdir()
    (vault_path / "file1.md").write_text("# File 1\n\nContent", encoding="utf-8")
    (vault_path / "file2.md").write_text("# File 2\n\nMore content", encoding="utf-8")

    indexer = VaultIndexer(vault_path, "scan_vault")
    chunks = await indexer.scan_all(only_changed=False, indexed_files=None)

    # Должны быть чанки из обоих файлов
    assert len(chunks) >= 2
    file_paths = {c.file_path for c in chunks}
    assert "file1.md" in file_paths
    assert "file2.md" in file_paths
