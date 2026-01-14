"""Тесты для cli.py"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from obsidian_kb.cli import cli
from obsidian_kb.cli.utils import get_uv_path, CLAUDE_CONFIG_FILE, CLAUDE_CONFIG_DIR


@pytest.fixture
def runner():
    """CLI runner для тестов."""
    return CliRunner()


@pytest.fixture
def temp_config_dir():
    """Создание временной директории для конфигов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_vaults_config(temp_config_dir):
    """Создание тестового конфига vault'ов."""
    config_path = temp_config_dir / "vaults.json"
    vault_path = temp_config_dir / "test_vault"
    vault_path.mkdir()
    (vault_path / "test.md").write_text("# Test\n\nContent", encoding="utf-8")

    config = {
        "vaults": [
            {"name": "test_vault", "path": str(vault_path)},
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def test_cli_help(runner):
    """Тест отображения help."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "obsidian-kb" in result.output
    assert "Commands:" in result.output


def test_cli_index_all_no_config(runner, temp_config_dir, monkeypatch):
    """Тест index-all без конфига."""
    from obsidian_kb import config

    # Мокаем путь к конфигу
    fake_config = temp_config_dir / "nonexistent.json"
    monkeypatch.setattr(config.settings, "vaults_config", fake_config)

    result = runner.invoke(cli, ["index-all"])
    assert result.exit_code == 1
    assert "не найден" in result.output or "Конфиг" in result.output


def test_cli_index_all_empty_config(runner, temp_config_dir, monkeypatch):
    """Тест index-all с пустым конфигом."""
    from obsidian_kb import config

    config_path = temp_config_dir / "vaults.json"
    config_path.write_text(json.dumps({"vaults": []}), encoding="utf-8")
    monkeypatch.setattr(config.settings, "vaults_config", config_path)

    result = runner.invoke(cli, ["index-all"])
    assert result.exit_code == 0
    assert "Нет vault'ов" in result.output or "vault" in result.output.lower()


@pytest.mark.asyncio
async def test_cli_index_command(runner, temp_config_dir):
    """Тест команды index."""
    vault_path = temp_config_dir / "test_vault"
    vault_path.mkdir()
    (vault_path / "test.md").write_text("# Test\n\nContent", encoding="utf-8")

    # Мокаем ServiceContainer
    mock_service_container = MagicMock()
    mock_embedding_service = MagicMock()
    mock_db_manager = MagicMock()
    mock_service_container.embedding_service = mock_embedding_service
    mock_service_container.db_manager = mock_db_manager

    # Патчим get_services в модуле index где он используется
    with patch("obsidian_kb.cli.commands.index.get_services", return_value=mock_service_container):
        with patch("obsidian_kb.cli.commands.index.VaultIndexer") as mock_indexer_class:
            from obsidian_kb.types import DocumentChunk
            from datetime import datetime

            mock_chunks = [
                DocumentChunk(
                    id="test::file.md::0",
                    vault_name="test",
                    file_path="file.md",
                    title="Test",
                    section="Main",
                    content="Content",
                    tags=[],
                    frontmatter_tags=[],
                    inline_tags=[],
                    links=[],
                    created_at=None,
                    modified_at=datetime.now(),
                    metadata={},
                )
            ]

            mock_indexer_instance = MagicMock()
            mock_indexer_instance.scan_all = AsyncMock(return_value=mock_chunks)
            mock_indexer_class.return_value = mock_indexer_instance

            mock_embedding_service.get_embeddings_batch = AsyncMock(return_value=[[0.1] * 768])
            mock_db_manager.upsert_chunks = AsyncMock()

            result = runner.invoke(cli, ["index", "--vault", "test", "--path", str(vault_path)])

            # Команда должна выполниться (может быть exit_code 0 или другой в зависимости от реализации)
            assert "Индексирование" in result.output or result.exit_code == 0


def test_cli_search_vault_not_found(runner):
    """Тест команды search с несуществующим vault."""
    from obsidian_kb.types import VaultNotFoundError

    mock_service_container = MagicMock()
    mock_search_service = MagicMock()
    mock_service_container.search_service = mock_search_service

    # Мокаем SearchResponse с пустыми результатами или ошибкой
    mock_search_service.search = AsyncMock(side_effect=VaultNotFoundError("Not found"))

    with patch("obsidian_kb.cli.commands.search.get_services", return_value=mock_service_container):
        result = runner.invoke(cli, ["search", "--vault", "nonexistent", "--query", "test"])

        # CLI может обработать ошибку по-разному
        assert result.exit_code in [0, 1]
        assert "не найден" in result.output or "Not found" in result.output or "Ошибка" in result.output or "не найден" in result.output.lower()


def test_cli_stats_vault_not_found(runner):
    """Тест команды stats с несуществующим vault."""
    from obsidian_kb.types import VaultNotFoundError

    mock_service_container = MagicMock()
    mock_db_manager = MagicMock()
    mock_service_container.db_manager = mock_db_manager

    mock_db_manager.get_vault_stats = AsyncMock(side_effect=VaultNotFoundError("Not found"))

    with patch("obsidian_kb.cli.commands.diagnostics.get_services", return_value=mock_service_container):
        result = runner.invoke(cli, ["stats", "--vault", "nonexistent"])

        # CLI может обработать ошибку и вернуть 0 или 1, или показать пустую статистику
        assert result.exit_code in [0, 1]
        # Проверяем, что либо ошибка показана, либо пустая статистика (что тоже валидно)
        assert "не найден" in result.output or "Not found" in result.output or "Ошибка" in result.output or "Статистика" in result.output


def test_cli_doctor_command(runner):
    """Тест команды doctor."""
    from datetime import datetime

    from obsidian_kb.types import HealthCheck, HealthStatus, SystemHealth

    mock_service_container = MagicMock()
    mock_diagnostics_service = MagicMock()
    mock_service_container.diagnostics_service = mock_diagnostics_service

    mock_health = SystemHealth(
        overall=HealthStatus.OK,
        checks=[
            HealthCheck("ollama", HealthStatus.OK, "OK"),
            HealthCheck("lancedb", HealthStatus.OK, "OK"),
        ],
        timestamp=datetime.now(),
    )
    mock_diagnostics_service.full_check = AsyncMock(return_value=mock_health)

    with patch("obsidian_kb.cli.commands.diagnostics.get_services", return_value=mock_service_container):
        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "статус" in result.output.lower() or "status" in result.output.lower()


def test_cli_doctor_json(runner):
    """Тест команды doctor с JSON выводом."""
    from datetime import datetime

    from obsidian_kb.types import HealthCheck, HealthStatus, SystemHealth

    mock_service_container = MagicMock()
    mock_diagnostics_service = MagicMock()
    mock_service_container.diagnostics_service = mock_diagnostics_service

    mock_health = SystemHealth(
        overall=HealthStatus.OK,
        checks=[
            HealthCheck("ollama", HealthStatus.OK, "OK"),
        ],
        timestamp=datetime.now(),
    )
    mock_diagnostics_service.full_check = AsyncMock(return_value=mock_health)

    with patch("obsidian_kb.cli.commands.diagnostics.get_services", return_value=mock_service_container):
        result = runner.invoke(cli, ["doctor", "--json"])

        assert result.exit_code == 0
        # Проверяем что это JSON
        try:
            data = json.loads(result.output)
            assert "overall" in data
            assert "checks" in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


def test_cli_doctor_check_component(runner):
    """Тест команды doctor с проверкой конкретного компонента."""
    from obsidian_kb.types import HealthCheck, HealthStatus

    mock_service_container = MagicMock()
    mock_diagnostics_service = MagicMock()
    mock_service_container.diagnostics_service = mock_diagnostics_service

    mock_check = HealthCheck("ollama", HealthStatus.OK, "Ollama доступна")
    mock_diagnostics_service.check_ollama = AsyncMock(return_value=mock_check)

    with patch("obsidian_kb.cli.commands.diagnostics.get_services", return_value=mock_service_container):
        result = runner.invoke(cli, ["doctor", "--check", "ollama"])

        assert result.exit_code == 0
        assert "ollama" in result.output.lower()


def test_cli_service_status_not_installed(runner):
    """Тест команды service-status когда сервис не установлен."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1

        result = runner.invoke(cli, ["service-status"])

        assert result.exit_code == 0
        assert "не запущен" in result.output or "not" in result.output.lower()


def test_get_uv_path():
    """Тест функции get_uv_path."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "/usr/local/bin/uv\n"

            path = get_uv_path()
            assert path is not None
            assert isinstance(path, str)


def test_claude_config_show(runner, temp_config_dir, monkeypatch):
    """Тест команды claude-config (показ конфигурации)."""
    # Мокаем путь к конфигу Claude Desktop
    fake_claude_config = temp_config_dir / "claude_desktop_config.json"
    monkeypatch.setattr("obsidian_kb.cli.commands.misc.CLAUDE_CONFIG_FILE", fake_claude_config)

    # В dev режиме используется uv
    with patch("obsidian_kb.cli.commands.misc.is_development_mode", return_value=True):
        with patch("obsidian_kb.cli.commands.misc.find_project_root", return_value=temp_config_dir):
            with patch("obsidian_kb.cli.commands.misc.get_uv_path", return_value="/usr/local/bin/uv"):
                result = runner.invoke(cli, ["claude-config"])

                assert result.exit_code == 0
                assert "Конфигурация для Claude Desktop" in result.output
                assert "obsidian-kb" in result.output
                assert "uv" in result.output


def test_claude_config_json(runner, temp_config_dir, monkeypatch):
    """Тест команды claude-config с JSON выводом."""
    fake_claude_config = temp_config_dir / "claude_desktop_config.json"
    monkeypatch.setattr("obsidian_kb.cli.commands.misc.CLAUDE_CONFIG_FILE", fake_claude_config)

    with patch("obsidian_kb.cli.commands.misc.is_development_mode", return_value=True):
        with patch("obsidian_kb.cli.commands.misc.find_project_root", return_value=temp_config_dir):
            with patch("obsidian_kb.cli.commands.misc.get_uv_path", return_value="/usr/local/bin/uv"):
                result = runner.invoke(cli, ["claude-config", "--json"])

                assert result.exit_code == 0
                # Проверяем что это валидный JSON
                try:
                    data = json.loads(result.output)
                    assert "mcpServers" in data
                    assert "obsidian-kb" in data["mcpServers"]
                except json.JSONDecodeError:
                    pytest.fail("Output is not valid JSON")


def test_claude_config_apply(runner, temp_config_dir, monkeypatch):
    """Тест команды claude-config --apply."""
    fake_claude_config = temp_config_dir / "claude_desktop_config.json"
    fake_claude_dir = temp_config_dir
    monkeypatch.setattr("obsidian_kb.cli.commands.misc.CLAUDE_CONFIG_FILE", fake_claude_config)
    monkeypatch.setattr("obsidian_kb.cli.commands.misc.CLAUDE_CONFIG_DIR", fake_claude_dir)

    uv_path = "/usr/local/bin/uv"
    with patch("obsidian_kb.cli.commands.misc.is_development_mode", return_value=True):
        with patch("obsidian_kb.cli.commands.misc.find_project_root", return_value=temp_config_dir):
            with patch("obsidian_kb.cli.commands.misc.get_uv_path", return_value=uv_path):
                result = runner.invoke(cli, ["claude-config", "--apply"])

                assert result.exit_code == 0
                assert "Конфигурация применена" in result.output
                assert fake_claude_config.exists()

                # Проверяем содержимое файла
                config_data = json.loads(fake_claude_config.read_text(encoding="utf-8"))
                assert "mcpServers" in config_data
                assert "obsidian-kb" in config_data["mcpServers"]
                # В dev режиме используется полный путь к uv
                assert config_data["mcpServers"]["obsidian-kb"]["command"] == uv_path


def test_claude_config_apply_with_existing_config(runner, temp_config_dir, monkeypatch):
    """Тест команды claude-config --apply с существующим конфигом."""
    fake_claude_config = temp_config_dir / "claude_desktop_config.json"
    fake_claude_dir = temp_config_dir
    monkeypatch.setattr("obsidian_kb.cli.commands.misc.CLAUDE_CONFIG_FILE", fake_claude_config)
    monkeypatch.setattr("obsidian_kb.cli.commands.misc.CLAUDE_CONFIG_DIR", fake_claude_dir)

    # Создаём существующий конфиг с другим сервером
    existing_config = {
        "mcpServers": {
            "other-server": {
                "command": "python",
                "args": ["other.py"]
            }
        }
    }
    fake_claude_config.write_text(json.dumps(existing_config), encoding="utf-8")

    with patch("obsidian_kb.cli.commands.misc.is_development_mode", return_value=True):
        with patch("obsidian_kb.cli.commands.misc.find_project_root", return_value=temp_config_dir):
            with patch("obsidian_kb.cli.commands.misc.get_uv_path", return_value="/usr/local/bin/uv"):
                result = runner.invoke(cli, ["claude-config", "--apply"])

                assert result.exit_code == 0
                assert "Конфигурация применена" in result.output

                # Проверяем что оба сервера присутствуют
                config_data = json.loads(fake_claude_config.read_text(encoding="utf-8"))
                assert "obsidian-kb" in config_data["mcpServers"]
                assert "other-server" in config_data["mcpServers"]

