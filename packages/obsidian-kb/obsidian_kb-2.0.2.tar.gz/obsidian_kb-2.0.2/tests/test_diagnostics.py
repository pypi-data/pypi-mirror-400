"""Тесты для diagnostics.py"""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.diagnostics import DiagnosticsService, send_notification
from obsidian_kb.types import HealthStatus


@pytest.fixture
def temp_config_dir():
    """Создание временной директории для конфигов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def diagnostics_service(temp_config_dir, monkeypatch):
    """Создание сервиса диагностики с временными путями."""
    # Мокаем пути в settings
    with patch("obsidian_kb.diagnostics.settings") as mock_settings:
        mock_settings.ollama_url = "http://localhost:11434"
        mock_settings.embedding_model = "nomic-embed-text"
        mock_settings.db_path = temp_config_dir / "lancedb"
        mock_settings.vaults_config = temp_config_dir / "vaults.json"
        
        service = DiagnosticsService()
        service.ollama_url = mock_settings.ollama_url
        service.embedding_model = mock_settings.embedding_model
        service.db_path = mock_settings.db_path
        service.vaults_config = mock_settings.vaults_config
        yield service


@pytest.fixture
def sample_vaults_config(temp_config_dir):
    """Создание тестового конфига vault'ов."""
    config_path = temp_config_dir / "vaults.json"
    config = {
        "vaults": [
            {"name": "test_vault", "path": str(temp_config_dir / "test_vault")},
            {"name": "another_vault", "path": str(temp_config_dir / "another_vault")},
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


@pytest.mark.asyncio
async def test_check_ollama_success(diagnostics_service):
    """Тест успешной проверки Ollama."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "models": [
                {"name": "nomic-embed-text"},
                {"name": "llama2"},
            ]
        }
    )

    # Правильный мок для async context manager
    mock_get = AsyncMock()
    mock_get.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_get)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        check = await diagnostics_service.check_ollama()

        assert check.component == "ollama"
        assert check.status == HealthStatus.OK
        assert "Ollama доступна" in check.message
        assert check.details is not None
        assert "models" in check.details


@pytest.mark.asyncio
async def test_check_ollama_model_not_found(diagnostics_service):
    """Тест проверки Ollama с отсутствующей моделью."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"models": [{"name": "llama2"}]})

    # Правильный мок для async context manager
    mock_get = AsyncMock()
    mock_get.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_get)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        check = await diagnostics_service.check_ollama()

        assert check.component == "ollama"
        assert check.status == HealthStatus.WARNING
        assert "не найдена" in check.message


@pytest.mark.asyncio
async def test_check_ollama_timeout(diagnostics_service):
    """Тест проверки Ollama с таймаутом."""
    mock_session = AsyncMock()
    mock_session.get = MagicMock(side_effect=asyncio.TimeoutError())
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        check = await diagnostics_service.check_ollama()

        assert check.component == "ollama"
        assert check.status == HealthStatus.ERROR
        assert "timeout" in check.message.lower() or "не отвечает" in check.message


@pytest.mark.asyncio
async def test_check_lancedb_success(diagnostics_service, temp_config_dir):
    """Тест успешной проверки LanceDB."""
    # Создаём тестовую БД
    import lancedb

    db_path = temp_config_dir / "lancedb"
    db = lancedb.connect(str(db_path))
    # Создаём пустую таблицу для теста
    import pyarrow as pa

    schema = pa.schema([pa.field("id", pa.string())])
    empty_table = pa.Table.from_arrays([[]], schema=schema)
    db.create_table("test_table", empty_table, mode="overwrite")

    diagnostics_service.db_path = db_path

    check = await diagnostics_service.check_lancedb()

    assert check.component == "lancedb"
    assert check.status == HealthStatus.OK
    assert "LanceDB OK" in check.message


@pytest.mark.asyncio
async def test_check_vaults_success(diagnostics_service, sample_vaults_config, temp_config_dir):
    """Тест успешной проверки vault'ов."""
    # Создаём директории vault'ов с файлами
    vault1 = temp_config_dir / "test_vault"
    vault1.mkdir()
    (vault1 / "test.md").write_text("# Test", encoding="utf-8")

    vault2 = temp_config_dir / "another_vault"
    vault2.mkdir()
    (vault2 / "note.md").write_text("# Note", encoding="utf-8")

    check = await diagnostics_service.check_vaults()

    assert check.component == "vaults"
    assert check.status == HealthStatus.OK
    assert "доступны" in check.message
    assert check.details is not None
    assert check.details.get("vault_count") == 2


@pytest.mark.asyncio
async def test_check_vaults_missing_path(diagnostics_service, sample_vaults_config):
    """Тест проверки vault'ов с отсутствующим путём."""
    # Не создаём директории - они должны отсутствовать

    check = await diagnostics_service.check_vaults()

    assert check.component == "vaults"
    assert check.status == HealthStatus.WARNING
    assert "Проблемы" in check.message or "не существует" in check.message
    assert check.details is not None
    assert "issues" in check.details


@pytest.mark.asyncio
async def test_check_vaults_no_config(diagnostics_service):
    """Тест проверки vault'ов без конфига."""
    # Убеждаемся, что конфига нет
    diagnostics_service.vaults_config = Path("/nonexistent/config.json")

    check = await diagnostics_service.check_vaults()

    assert check.component == "vaults"
    assert check.status == HealthStatus.WARNING
    assert "не найдена" in check.message


@pytest.mark.asyncio
async def test_check_disk_space(diagnostics_service, temp_config_dir):
    """Тест проверки свободного места на диске."""
    diagnostics_service.db_path = temp_config_dir / "lancedb"

    check = await diagnostics_service.check_disk_space()

    assert check.component == "disk"
    assert check.status in (HealthStatus.OK, HealthStatus.WARNING, HealthStatus.ERROR)
    assert "GB" in check.message
    assert check.details is not None
    assert "free_gb" in check.details


@pytest.mark.asyncio
async def test_full_check(diagnostics_service, sample_vaults_config, temp_config_dir):
    """Тест полной диагностики системы."""
    # Настраиваем окружение для успешных проверок
    vault1 = temp_config_dir / "test_vault"
    vault1.mkdir()
    (vault1 / "test.md").write_text("# Test", encoding="utf-8")

    # Мокаем Ollama для успешного ответа
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={"models": [{"name": "mxbai-embed-large"}]}
    )

    # Правильный мок для async context manager
    mock_get = AsyncMock()
    mock_get.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_get)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        health = await diagnostics_service.full_check()

        assert isinstance(health.overall, HealthStatus)
        # Теперь должно быть 7 проверок: ollama, lancedb, vaults, disk, memory, cpu, performance
        assert len(health.checks) == 7
        assert isinstance(health.timestamp, datetime)
        expected_components = {"ollama", "lancedb", "vaults", "disk", "memory", "cpu", "performance"}
        actual_components = {check.component for check in health.checks}
        assert actual_components == expected_components


def test_send_notification():
    """Тест отправки уведомления macOS."""
    with patch("subprocess.run") as mock_run:
        send_notification("Test Title", "Test Message", sound=True)

        assert mock_run.called
        args = mock_run.call_args[0][0]
        assert args[0] == "osascript"
        assert "-e" in args
        assert "Test Title" in " ".join(args)
        assert "Test Message" in " ".join(args)


def test_send_notification_no_sound():
    """Тест отправки уведомления без звука."""
    with patch("subprocess.run") as mock_run:
        send_notification("Test Title", "Test Message", sound=False)

        assert mock_run.called
        args = " ".join(mock_run.call_args[0][0])
        assert "sound" not in args


@pytest.mark.asyncio
async def test_check_memory_with_psutil(diagnostics_service):
    """Тест проверки памяти с psutil."""
    try:
        import psutil
    except ImportError:
        pytest.skip("psutil не установлен")

    check = await diagnostics_service.check_memory()

    assert check.component == "memory"
    assert check.status in (HealthStatus.OK, HealthStatus.WARNING, HealthStatus.ERROR)
    assert check.details is not None
    assert "total_gb" in check.details or "percent_used" in check.details


@pytest.mark.asyncio
async def test_check_memory_without_psutil(diagnostics_service):
    """Тест проверки памяти без psutil."""
    with patch("obsidian_kb.diagnostics.platform.system", return_value="Linux"), \
         patch("builtins.__import__", side_effect=ImportError("No module named psutil")):
        check = await diagnostics_service.check_memory()

        assert check.component == "memory"
        assert check.status == HealthStatus.WARNING
        assert "psutil" in check.message.lower()


@pytest.mark.asyncio
async def test_check_cpu_with_psutil(diagnostics_service):
    """Тест проверки CPU с psutil."""
    try:
        import psutil
    except ImportError:
        pytest.skip("psutil не установлен")

    check = await diagnostics_service.check_cpu()

    assert check.component == "cpu"
    assert check.status in (HealthStatus.OK, HealthStatus.WARNING)
    assert check.details is not None
    assert "cpu_percent" in check.details or "cpu_count" in check.details


@pytest.mark.asyncio
async def test_check_cpu_without_psutil(diagnostics_service):
    """Тест проверки CPU без psutil."""
    with patch("builtins.__import__", side_effect=ImportError("No module named psutil")):
        check = await diagnostics_service.check_cpu()

        assert check.component == "cpu"
        assert check.status == HealthStatus.WARNING
        assert "psutil" in check.message.lower()


@pytest.mark.asyncio
async def test_check_performance(diagnostics_service, temp_config_dir):
    """Тест проверки производительности."""
    import lancedb
    import pyarrow as pa

    # Создаём тестовую БД
    db_path = temp_config_dir / "lancedb"
    db = lancedb.connect(str(db_path))
    schema = pa.schema([pa.field("id", pa.string())])
    empty_table = pa.Table.from_arrays([[]], schema=schema)
    db.create_table("test_table", empty_table, mode="overwrite")

    diagnostics_service.db_path = db_path

    check = await diagnostics_service.check_performance()

    assert check.component == "performance"
    assert check.status in (HealthStatus.OK, HealthStatus.WARNING, HealthStatus.ERROR)
    assert check.details is not None
    assert "response_time_ms" in check.details


@pytest.mark.asyncio
async def test_full_check_with_notifications(diagnostics_service, sample_vaults_config, temp_config_dir):
    """Тест полной диагностики с уведомлениями."""
    # Настраиваем окружение
    vault1 = temp_config_dir / "test_vault"
    vault1.mkdir()
    (vault1 / "test.md").write_text("# Test", encoding="utf-8")

    # Мокаем Ollama для успешного ответа
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={"models": [{"name": "mxbai-embed-large"}]}
    )

    mock_get = AsyncMock()
    mock_get.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_get)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session), \
         patch("obsidian_kb.diagnostics.send_notification") as mock_notify:
        health = await diagnostics_service.full_check(send_notifications=True)

        # Если есть ошибки, должно быть отправлено уведомление
        if health.overall == HealthStatus.ERROR:
            assert mock_notify.called
        # Если только предупреждения, уведомление может быть или не быть
        # Проверяем, что метод был вызван корректно
        assert isinstance(health.overall, HealthStatus)

