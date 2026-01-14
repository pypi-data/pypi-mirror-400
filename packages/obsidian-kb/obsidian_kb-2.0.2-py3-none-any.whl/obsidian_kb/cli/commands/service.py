"""Service commands: install_service, uninstall_service, service_status, restart_service."""

import os
import subprocess
import sys
from pathlib import Path

import click

from obsidian_kb.cli.utils import (
    LAUNCH_AGENTS_DIR,
    PLIST_NAME,
    console,
    find_plist_file_and_project,
    get_python_path,
    get_uv_path,
    logger,
)


@click.command("install-service")
def install_service() -> None:
    """Установить автозапуск сервиса через launchd."""
    try:
        plist_content, project_root, is_dev_mode = find_plist_file_and_project()
    except Exception as e:
        console.print(f"[red]Ошибка поиска файла plist: {e}[/red]")
        sys.exit(1)

    if is_dev_mode:
        if project_root is None or not (project_root / "pyproject.toml").exists():
            console.print("[red]Ошибка: Не найден проект obsidian-kb[/red]")
            console.print(f"Текущая директория: {Path.cwd()}")
            if project_root:
                console.print(f"Проверенный путь: {project_root}")
            console.print("\n[cyan]Возможные решения:[/cyan]")
            console.print("1. Перейдите в корень проекта obsidian-kb и запустите команду оттуда:")
            console.print("   [green]cd /path/to/obsidian-kb && uv run obsidian-kb install-service[/green]")
            console.print("2. Установите переменную окружения OBSIDIAN_KB_PROJECT_ROOT:")
            console.print("   [green]export OBSIDIAN_KB_PROJECT_ROOT=/path/to/obsidian-kb[/green]")
            console.print("   [green]uv run obsidian-kb install-service[/green]")
            sys.exit(1)

    plist_dst = LAUNCH_AGENTS_DIR / PLIST_NAME

    try:
        home_dir = Path.home()
        username = os.environ.get("USER", "")

        if is_dev_mode:
            if project_root is None:
                console.print("[red]Ошибка: Не найден корень проекта в режиме разработки[/red]")
                sys.exit(1)
            uv_path = get_uv_path()
            try:
                content = plist_content.format(
                    uv_path=uv_path,
                    project_root=str(project_root),
                    home_dir=str(home_dir),
                )
            except KeyError:
                content = plist_content
                content = content.replace("/path/to/obsidian-kb", str(project_root))
                content = content.replace("/Users/USERNAME/.local/bin/uv", uv_path)
                content = content.replace("/Users/USERNAME/", f"{home_dir}/")
                content = content.replace("USERNAME", username)
        else:
            python_path = get_python_path()
            try:
                content = plist_content.format(
                    python_path=python_path,
                    home_dir=str(home_dir),
                )
            except KeyError:
                content = plist_content
                content = content.replace("/Users/USERNAME/", f"{home_dir}/")
                content = content.replace("USERNAME", username)
                if "{python_path}" in content:
                    content = content.replace("{python_path}", python_path)

        LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        plist_dst.write_text(content, encoding="utf-8")

        subprocess.run(["launchctl", "load", str(plist_dst)], check=True)
        console.print("[green]✓ Сервис установлен и запущен[/green]")
        if is_dev_mode:
            console.print("  Режим: разработка")
            console.print(f"  uv: {uv_path}")
            console.print(f"  project: {project_root}")
        else:
            console.print("  Режим: установленный пакет")
            console.print(f"  python: {python_path}")

    except Exception as e:
        console.print(f"[red]Ошибка установки сервиса: {e}[/red]")
        logger.exception("Error installing service")
        sys.exit(1)


@click.command("uninstall-service")
def uninstall_service() -> None:
    """Удалить автозапуск сервиса."""
    plist_path = LAUNCH_AGENTS_DIR / PLIST_NAME
    if plist_path.exists():
        try:
            subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
            plist_path.unlink()
            console.print("[yellow]✓ Сервис удалён[/yellow]")
        except Exception as e:
            console.print(f"[red]Ошибка удаления сервиса: {e}[/red]")
            sys.exit(1)
    else:
        console.print("[yellow]Сервис не установлен[/yellow]")


@click.command("service-status")
def service_status() -> None:
    """Проверить статус сервиса."""
    result = subprocess.run(
        ["launchctl", "list", "com.obsidian-kb"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        console.print("[green]● Сервис запущен[/green]")
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split("\t")
            if len(parts) >= 3:
                pid, status = parts[0], parts[1]
                console.print(f"  PID: {pid}")
                console.print(f"  Exit status: {status}")
    else:
        console.print("[red]○ Сервис не запущен[/red]")

    error_path = Path("/tmp/obsidian-kb.error.log")
    if error_path.exists() and error_path.stat().st_size > 0:
        console.print("\n[yellow]Последние ошибки:[/yellow]")
        console.print(error_path.read_text(encoding="utf-8")[-500:])


@click.command("restart-service")
def restart_service() -> None:
    """Перезапустить сервис."""
    plist_path = LAUNCH_AGENTS_DIR / PLIST_NAME
    if plist_path.exists():
        try:
            subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
            subprocess.run(["launchctl", "load", str(plist_path)], check=True)
            console.print("[green]✓ Сервис перезапущен[/green]")
        except Exception as e:
            console.print(f"[red]Ошибка перезапуска сервиса: {e}[/red]")
            sys.exit(1)
    else:
        console.print("[red]Сервис не установлен. Используйте: obsidian-kb install-service[/red]")
        sys.exit(1)
