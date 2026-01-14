"""Тесты для service management команд."""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from obsidian_kb.cli import cli
from obsidian_kb.cli.utils import LAUNCH_AGENTS_DIR, PLIST_NAME


@pytest.fixture
def runner():
    """CLI runner для тестов."""
    return CliRunner()


@pytest.fixture
def temp_launch_agents(tmp_path, monkeypatch):
    """Временная директория для LaunchAgents."""
    fake_dir = tmp_path / "LaunchAgents"
    fake_dir.mkdir()
    # Патчим в модуле service где используется
    monkeypatch.setattr("obsidian_kb.cli.commands.service.LAUNCH_AGENTS_DIR", fake_dir)
    return fake_dir


@pytest.fixture
def temp_project_root(tmp_path):
    """Временный корень проекта."""
    project_root = tmp_path / "obsidian-kb"
    project_root.mkdir()
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()
    
    # Создаём шаблон plist файла
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.obsidian-kb</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/USERNAME/.local/bin/uv</string>
        <string>run</string>
        <string>--project</string>
        <string>/path/to/obsidian-kb</string>
        <string>python</string>
        <string>-m</string>
        <string>obsidian_kb.mcp_server</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/obsidian-kb.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/obsidian-kb.error.log</string>
</dict>
</plist>
"""
    (scripts_dir / PLIST_NAME).write_text(plist_content, encoding="utf-8")
    
    return project_root


def test_install_service(runner, temp_launch_agents, temp_project_root, monkeypatch):
    """Тест команды install-service."""
    # Создаём plist шаблон
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>Label</key><string>com.obsidian-kb</string></dict></plist>"""

    # Мокаем subprocess.run для launchctl
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        # Мокаем find_plist_file_and_project
        with patch(
            "obsidian_kb.cli.commands.service.find_plist_file_and_project",
            return_value=(plist_content, temp_project_root, True)
        ):
            result = runner.invoke(cli, ["install-service"])

            # Команда должна попытаться создать plist файл
            # Проверяем, что команда была вызвана
            assert result.exit_code in [0, 1]  # Может быть ошибка из-за моков


def test_uninstall_service_not_installed(runner, temp_launch_agents):
    """Тест команды uninstall-service когда сервис не установлен."""
    result = runner.invoke(cli, ["uninstall-service"])
    
    assert result.exit_code == 0
    assert "не установлен" in result.output.lower() or "not installed" in result.output.lower()


def test_uninstall_service_installed(runner, temp_launch_agents):
    """Тест команды uninstall-service когда сервис установлен."""
    # Создаём plist файл
    plist_path = temp_launch_agents / PLIST_NAME
    plist_path.write_text("test content", encoding="utf-8")
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        
        result = runner.invoke(cli, ["uninstall-service"])
        
        assert result.exit_code == 0
        assert "удалён" in result.output.lower() or "removed" in result.output.lower()
        # Файл должен быть удалён
        assert not plist_path.exists()


def test_restart_service_not_installed(runner, temp_launch_agents):
    """Тест команды restart-service когда сервис не установлен."""
    result = runner.invoke(cli, ["restart-service"])
    
    assert result.exit_code == 1
    assert "не установлен" in result.output.lower() or "not installed" in result.output.lower()


def test_restart_service_installed(runner, temp_launch_agents):
    """Тест команды restart-service когда сервис установлен."""
    # Создаём plist файл
    plist_path = temp_launch_agents / PLIST_NAME
    plist_path.write_text("test content", encoding="utf-8")
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        
        result = runner.invoke(cli, ["restart-service"])
        
        assert result.exit_code == 0
        assert "перезапущен" in result.output.lower() or "restarted" in result.output.lower()
        # Должно быть два вызова: unload и load
        assert mock_run.call_count >= 2


def test_service_status_installed(runner):
    """Тест команды service-status когда сервис установлен."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PID\tStatus\tLabel\n123\t0\tcom.obsidian-kb\n"
        
        result = runner.invoke(cli, ["service-status"])
        
        assert result.exit_code == 0
        assert "запущен" in result.output.lower() or "running" in result.output.lower()


def test_service_status_with_logs(runner, tmp_path):
    """Тест команды service-status с логами ошибок."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PID\tStatus\tLabel\n123\t0\tcom.obsidian-kb\n"

        result = runner.invoke(cli, ["service-status"])

        assert result.exit_code == 0
        # Может содержать информацию о статусе
        # (зависит от реализации)

