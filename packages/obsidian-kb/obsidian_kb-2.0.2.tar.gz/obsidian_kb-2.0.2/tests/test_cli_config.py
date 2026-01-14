"""Тесты для config подкоманд."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from obsidian_kb.cli import cli
from obsidian_kb.config import settings


@pytest.fixture
def runner():
    """CLI runner для тестов."""
    return CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Временная директория для конфига."""
    fake_config = tmp_path / "vaults.json"
    monkeypatch.setattr(settings, "vaults_config", fake_config)
    return tmp_path


@pytest.fixture
def sample_vaults_config(temp_config_dir):
    """Создание примера конфига vault'ов."""
    config_path = settings.vaults_config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    config = {
        "vaults": [
            {"name": "vault1", "path": "/path/to/vault1"},
            {"name": "vault2", "path": "/path/to/vault2"},
        ]
    }
    
    config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    return config_path


def test_config_show(runner, sample_vaults_config):
    """Тест команды config show."""
    result = runner.invoke(cli, ["config", "show"])
    
    assert result.exit_code == 0
    assert "vault1" in result.output or "vault2" in result.output
    assert "Путь" in result.output or "Path" in result.output


def test_config_show_empty(runner, temp_config_dir):
    """Тест команды config show с пустым конфигом."""
    # Создаём пустой конфиг
    config_path = settings.vaults_config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({"vaults": []}, ensure_ascii=False), encoding="utf-8")
    
    result = runner.invoke(cli, ["config", "show"])
    
    assert result.exit_code == 0
    # Должен показать, что vault'ов нет


def test_config_add_vault_new(runner, temp_config_dir, tmp_path):
    """Тест команды config add-vault для нового vault'а.

    Используем --no-index чтобы избежать сложного мокирования сервисов.
    """
    # Создаём временный vault
    vault_path = tmp_path / "new_vault"
    vault_path.mkdir()
    (vault_path / "test.md").write_text("# Test", encoding="utf-8")

    # Используем --no-index чтобы не запускать индексацию
    result = runner.invoke(
        cli,
        [
            "config",
            "add-vault",
            "--name",
            "new_vault",
            "--path",
            str(vault_path),
            "--no-index",
        ],
    )

    assert result.exit_code == 0
    assert "добавлен" in result.output.lower() or "added" in result.output.lower()

    # Проверяем, что vault добавлен в конфиг
    config_data = json.loads(settings.vaults_config.read_text(encoding="utf-8"))
    vault_names = [v.get("name") for v in config_data.get("vaults", [])]
    assert "new_vault" in vault_names


def test_config_add_vault_existing(runner, sample_vaults_config, tmp_path):
    """Тест команды config add-vault для существующего vault'а."""
    vault_path = tmp_path / "vault1"
    vault_path.mkdir()
    
    result = runner.invoke(
        cli,
        [
            "config",
            "add-vault",
            "--name",
            "vault1",
            "--path",
            str(vault_path),
        ],
    )
    
    # Должна быть ошибка или предупреждение о существующем vault'е
    assert result.exit_code != 0 or "уже существует" in result.output.lower() or "already exists" in result.output.lower()


def test_config_add_vault_no_index(runner, temp_config_dir, tmp_path):
    """Тест команды config add-vault с флагом --no-index."""
    vault_path = tmp_path / "new_vault"
    vault_path.mkdir()
    (vault_path / "test.md").write_text("# Test", encoding="utf-8")
    
    result = runner.invoke(
        cli,
        [
            "config",
            "add-vault",
            "--name",
            "new_vault",
            "--path",
            str(vault_path),
            "--no-index",
        ],
    )
    
    assert result.exit_code == 0
    assert "добавлен" in result.output.lower() or "added" in result.output.lower()
    
    # Проверяем, что vault добавлен в конфиг
    config_data = json.loads(settings.vaults_config.read_text(encoding="utf-8"))
    vault_names = [v.get("name") for v in config_data.get("vaults", [])]
    assert "new_vault" in vault_names


def test_config_remove_vault(runner, sample_vaults_config):
    """Тест команды config remove-vault."""
    result = runner.invoke(
        cli,
        [
            "config",
            "remove-vault",
            "--name",
            "vault1",
        ],
    )
    
    assert result.exit_code == 0
    assert "удалён" in result.output.lower() or "removed" in result.output.lower()
    
    # Проверяем, что vault удалён из конфига
    config_data = json.loads(settings.vaults_config.read_text(encoding="utf-8"))
    vault_names = [v.get("name") for v in config_data.get("vaults", [])]
    assert "vault1" not in vault_names
    assert "vault2" in vault_names  # Другой vault должен остаться


def test_config_remove_vault_not_found(runner, sample_vaults_config):
    """Тест команды config remove-vault для несуществующего vault'а."""
    result = runner.invoke(
        cli,
        [
            "config",
            "remove-vault",
            "--name",
            "nonexistent",
        ],
    )
    
    # Команда может вернуть 0, но должна показать сообщение об ошибке
    assert "не найден" in result.output.lower() or "not found" in result.output.lower() or "не существует" in result.output.lower()

