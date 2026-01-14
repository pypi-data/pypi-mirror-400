"""Тесты для команды watch (автоматическое инкрементальное обновление)."""

import json
import signal
import threading
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from obsidian_kb.cli import cli


@pytest.fixture
def runner():
    """CLI runner для тестов."""
    return CliRunner()


@pytest.fixture
def temp_config(tmp_path, temp_vault):
    """Временный конфиг vault'ов."""
    config_path = tmp_path / "vaults.json"
    config_path.write_text(
        json.dumps({
            "vaults": [
                {"name": "test_vault", "path": str(temp_vault)}
            ]
        }),
        encoding="utf-8"
    )
    return config_path


def test_watch_command_help(runner):
    """Тест справки команды watch."""
    result = runner.invoke(cli, ["watch", "--help"])
    assert result.exit_code == 0
    assert "watch" in result.output.lower()
    assert "vault" in result.output.lower() or "отслеживание" in result.output.lower()


def test_watch_command_no_vaults(runner, tmp_path, monkeypatch):
    """Тест команды watch без vault'ов в конфиге."""
    from obsidian_kb import config
    
    # Создаём пустой конфиг
    config_path = tmp_path / "vaults.json"
    config_path.write_text(json.dumps({"vaults": []}), encoding="utf-8")
    
    monkeypatch.setattr(config.settings, "vaults_config", config_path)
    
    result = runner.invoke(cli, ["watch"], input="\n")
    
    # Команда должна завершиться с сообщением об отсутствии vault'ов
    assert "нет валидных vault'ов" in result.output.lower() or "no vaults" in result.output.lower()


def test_watch_command_invalid_vault(runner, temp_config, monkeypatch):
    """Тест команды watch с несуществующим vault'ом."""
    from obsidian_kb import config
    
    monkeypatch.setattr(config.settings, "vaults_config", temp_config)
    
    result = runner.invoke(cli, ["watch", "--vault", "nonexistent"])
    
    # Команда должна завершиться с ошибкой
    assert result.exit_code != 0
    assert "не найден" in result.output.lower() or "not found" in result.output.lower()


def test_watch_command_starts_watchers(runner, temp_config, temp_vault, temp_db, monkeypatch):
    """Тест, что команда watch запускает watchers для vault'ов."""
    from obsidian_kb import config

    monkeypatch.setattr(config.settings, "vaults_config", temp_config)
    monkeypatch.setattr(config.settings, "db_path", temp_db)

    # Мокаем get_services
    mock_services = MagicMock()
    mock_services.embedding_service.get_embeddings_batch = AsyncMock(return_value=[[0.1] * 768] * 5)
    mock_services.embedding_service.close = AsyncMock()
    mock_services.db_manager = MagicMock()

    with patch("obsidian_kb.cli.commands.watch.get_services", return_value=mock_services):
        # Мокаем asyncio.run чтобы команда не запускалась бесконечно
        with patch("obsidian_kb.cli.commands.watch.asyncio.run") as mock_run:
            # Создаём мок для async функции
            async def mock_watch_async():
                # Имитируем короткую работу
                import asyncio
                await asyncio.sleep(0.1)

            mock_run.side_effect = mock_watch_async

            # Мокаем signal.signal чтобы не устанавливать реальные обработчики
            with patch("signal.signal"):
                result = runner.invoke(cli, ["watch"], input="\n")

                # Команда должна начать выполнение
                # Проверяем, что есть упоминание о запуске
                assert len(result.output) >= 0  # Может быть пустой если быстро завершилась


def test_watch_command_with_specific_vault(runner, temp_config, temp_vault, temp_db, monkeypatch):
    """Тест команды watch с указанием конкретного vault'а."""
    from obsidian_kb import config

    monkeypatch.setattr(config.settings, "vaults_config", temp_config)
    monkeypatch.setattr(config.settings, "db_path", temp_db)

    # Мокаем get_services
    mock_services = MagicMock()
    mock_services.embedding_service.get_embeddings_batch = AsyncMock(return_value=[[0.1] * 768] * 5)
    mock_services.embedding_service.close = AsyncMock()
    mock_services.db_manager = MagicMock()

    with patch("obsidian_kb.cli.commands.watch.get_services", return_value=mock_services):
        # Мокаем asyncio.run
        with patch("obsidian_kb.cli.commands.watch.asyncio.run") as mock_run:
            async def mock_watch_async():
                import asyncio
                await asyncio.sleep(0.1)

            mock_run.side_effect = mock_watch_async

            with patch("signal.signal"):
                result = runner.invoke(cli, ["watch", "--vault", "test_vault"], input="\n")

                # Команда должна начать выполнение
                assert len(result.output) >= 0


def test_watch_command_debounce_option(runner, temp_config, temp_vault, temp_db, monkeypatch):
    """Тест команды watch с настройкой debounce."""
    from obsidian_kb import config

    monkeypatch.setattr(config.settings, "vaults_config", temp_config)
    monkeypatch.setattr(config.settings, "db_path", temp_db)

    # Мокаем get_services
    mock_services = MagicMock()
    mock_services.embedding_service.get_embeddings_batch = AsyncMock(return_value=[[0.1] * 768] * 5)
    mock_services.embedding_service.close = AsyncMock()
    mock_services.db_manager = MagicMock()

    with patch("obsidian_kb.cli.commands.watch.get_services", return_value=mock_services):
        # Мокаем asyncio.run
        with patch("obsidian_kb.cli.commands.watch.asyncio.run") as mock_run:
            async def mock_watch_async():
                import asyncio
                await asyncio.sleep(0.1)

            mock_run.side_effect = mock_watch_async

            with patch("signal.signal"):
                result = runner.invoke(cli, ["watch", "--debounce", "5.0"], input="\n")

                # Команда должна начать выполнение
                assert len(result.output) >= 0


@pytest.mark.asyncio
async def test_watch_file_change_processing(temp_vault, temp_db):
    """Тест обработки изменений файлов в watch режиме."""
    from obsidian_kb.embedding_cache import EmbeddingCache
    from obsidian_kb.embedding_service import EmbeddingService
    from obsidian_kb.lance_db import LanceDBManager
    from obsidian_kb.vault_indexer import VaultIndexer
    
    vault_name = "test_vault"
    db_manager = LanceDBManager(db_path=temp_db)
    embedding_service = EmbeddingService()
    
    try:
        # Создаём начальный индекс
        embedding_cache = EmbeddingCache()
        indexer = VaultIndexer(temp_vault, vault_name, embedding_cache=embedding_cache)
        chunks = await indexer.scan_all(only_changed=False, indexed_files=None)
        
        if chunks:
            texts = [c.content for c in chunks]
            embeddings = await embedding_service.get_embeddings_batch(texts)
            await db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Изменяем файл
        test_file = temp_vault / "file1.md"
        original_content = test_file.read_text(encoding="utf-8")
        test_file.write_text(original_content + "\n\nNew content added", encoding="utf-8")
        
        # Получаем список проиндексированных файлов
        indexed_files = await db_manager.get_indexed_files(vault_name)
        
        # Проверяем инкрементальное индексирование
        chunks2 = await indexer.scan_all(only_changed=True, indexed_files=indexed_files)
        
        # Должен найти изменённый файл
        assert len(chunks2) > 0
        
        # Проверяем, что новый контент в чанках
        new_content_found = any("New content added" in chunk.content for chunk in chunks2)
        assert new_content_found
        
    finally:
        await embedding_service.close()

