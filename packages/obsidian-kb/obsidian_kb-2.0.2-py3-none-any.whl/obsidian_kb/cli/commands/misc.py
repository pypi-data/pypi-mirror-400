"""Misc commands: serve, version, claude_config, metrics, clear_metrics, reset_circuit_breaker."""

import asyncio
import json
import os
import sys
from pathlib import Path

import click
from rich.table import Table

from obsidian_kb.cli.utils import (
    CLAUDE_CONFIG_DIR,
    CLAUDE_CONFIG_FILE,
    console,
    find_project_in_common_locations,
    find_project_root,
    get_python_path,
    get_uv_path,
    is_development_mode,
    logger,
)
from obsidian_kb.metrics import MetricsCollector


@click.command()
def serve() -> None:
    """Запустить MCP сервер (для отладки)."""
    from obsidian_kb.mcp_server import main as mcp_main

    console.print("[cyan]Запуск MCP сервера...[/cyan]")
    mcp_main()


@click.command()
def version() -> None:
    """Показать версию obsidian-kb."""
    from obsidian_kb import __version__

    console.print(f"obsidian-kb {__version__}")


@click.command("claude-config")
@click.option("--apply", is_flag=True, help="Применить конфигурацию к Claude Desktop")
@click.option("--json", "output_json", is_flag=True, help="Вывести конфигурацию в JSON формате")
def claude_config(apply: bool, output_json: bool) -> None:
    """Показать или применить конфигурацию для Claude Desktop."""
    is_dev = is_development_mode()

    if is_dev:
        project_root = find_project_root()
        if not project_root:
            project_root = find_project_in_common_locations()
        if not project_root:
            env_project = os.environ.get("OBSIDIAN_KB_PROJECT_ROOT")
            if env_project:
                env_path = Path(env_project)
                if env_path.exists() and (env_path / "pyproject.toml").exists():
                    project_root = env_path

        if not project_root:
            console.print("[red]Ошибка: Не найден корень проекта obsidian-kb[/red]")
            console.print("\n[cyan]Возможные решения:[/cyan]")
            console.print("1. Перейдите в корень проекта obsidian-kb и запустите команду оттуда")
            console.print("2. Установите переменную окружения OBSIDIAN_KB_PROJECT_ROOT:")
            console.print("   [green]export OBSIDIAN_KB_PROJECT_ROOT=/path/to/obsidian-kb[/green]")
            console.print("3. Для установленного пакета используйте команду из любого места")
            sys.exit(1)

        try:
            uv_path = get_uv_path()
        except RuntimeError as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            sys.exit(1)

        obsidian_kb_config = {
            "command": uv_path,
            "args": [
                "run",
                "--project",
                str(project_root),
                "python",
                "-m",
                "obsidian_kb.mcp_server"
            ]
        }
    else:
        python_path = get_python_path()

        obsidian_kb_config = {
            "command": python_path,
            "args": [
                "-m",
                "obsidian_kb.mcp_server"
            ]
        }

    existing_config: dict = {}
    if CLAUDE_CONFIG_FILE.exists():
        try:
            with open(CLAUDE_CONFIG_FILE, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except json.JSONDecodeError as e:
            console.print(f"[yellow]Предупреждение: Ошибка чтения существующего конфига: {e}[/yellow]")
            console.print("[yellow]Будет создан новый конфиг[/yellow]")
            existing_config = {}
        except Exception as e:
            console.print(f"[yellow]Предупреждение: Не удалось прочитать конфиг: {e}[/yellow]")
            existing_config = {}

    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    existing_config["mcpServers"]["obsidian-kb"] = obsidian_kb_config

    if output_json:
        print(json.dumps(existing_config, indent=2, ensure_ascii=False))
    else:
        console.print("[cyan]Конфигурация для Claude Desktop:[/cyan]\n")
        if is_dev:
            console.print("[green]Режим:[/green] разработка")
            console.print(f"[green]Проект:[/green] {project_root}")
            console.print(f"[green]uv:[/green] {uv_path}")
        else:
            console.print("[green]Режим:[/green] установленный пакет")
            console.print(f"[green]Python:[/green] {python_path}")
        console.print(f"[green]Файл конфига:[/green] {CLAUDE_CONFIG_FILE}\n")

        console.print("[cyan]Конфигурация obsidian-kb:[/cyan]")
        console.print(json.dumps({"obsidian-kb": obsidian_kb_config}, indent=2, ensure_ascii=False))

        other_servers = {k: v for k, v in existing_config["mcpServers"].items() if k != "obsidian-kb"}
        if other_servers:
            console.print(f"\n[yellow]Другие MCP серверы в конфиге ({len(other_servers)}):[/yellow]")
            for server_name in other_servers.keys():
                console.print(f"  • {server_name}")

    if apply:
        try:
            CLAUDE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(CLAUDE_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_config, f, indent=2, ensure_ascii=False)

            try:
                with open(CLAUDE_CONFIG_FILE, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                console.print(f"[red]Ошибка: Невалидный JSON после записи: {e}[/red]")
                sys.exit(1)

            console.print("\n[green]✓ Конфигурация применена[/green]")
            console.print(f"  Файл: {CLAUDE_CONFIG_FILE}")
            console.print("\n[yellow]⚠️  Не забудьте перезапустить Claude Desktop для применения изменений![/yellow]")

        except PermissionError:
            console.print(f"[red]Ошибка: Нет прав на запись в {CLAUDE_CONFIG_FILE}[/red]")
            console.print("[yellow]Попробуйте запустить с правами администратора или измените права доступа[/yellow]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка при записи конфига: {e}[/red]")
            logger.exception("Error writing Claude Desktop config")
            sys.exit(1)
    elif not output_json:
        console.print("\n[yellow]💡 Для применения конфигурации используйте: obsidian-kb claude-config --apply[/yellow]")


@click.command()
@click.option("--days", default=7, help="Количество дней для анализа (default: 7)")
@click.option("--limit", default=10, help="Максимум популярных запросов/vault'ов (default: 10)")
@click.option("--vault", "vault_name", type=str, help="Фильтр по конкретному vault'у (опционально)")
@click.option("--export", "export_path", type=click.Path(), help="Путь для экспорта метрик")
@click.option("--format", "export_format", type=click.Choice(["json", "csv"]), help="Формат экспорта (json или csv)")
def metrics(days: int, limit: int, vault_name: str | None, export_path: str | None, export_format: str | None) -> None:
    """Просмотр метрик использования системы."""
    async def metrics_async() -> None:
        try:
            metrics_collector = MetricsCollector()

            if export_path:
                output_path = Path(export_path)
                if export_format == "json":
                    await metrics_collector.export_to_json(output_path, days=days)
                    console.print(f"[green]✓ Метрики экспортированы в JSON: {output_path}[/green]")
                elif export_format == "csv":
                    await metrics_collector.export_to_csv(output_path, days=days)
                    console.print(f"[green]✓ Метрики экспортированы в CSV: {output_path}[/green]")
                else:
                    console.print("[red]Укажите формат экспорта: --format json или --format csv[/red]")
                    sys.exit(1)
                return

            summary = await metrics_collector.get_summary(days=days, limit=limit, vault_name=vault_name)

            vault_filter_text = f" для vault '{vault_name}'" if vault_name else ""
            console.print(f"\n[cyan]📊 Метрики использования obsidian-kb{vault_filter_text}[/cyan]")
            console.print(f"Период: {summary.period_start.strftime('%Y-%m-%d')} - {summary.period_end.strftime('%Y-%m-%d')}\n")

            table = Table(title="Общая статистика")
            table.add_column("Параметр", style="cyan")
            table.add_column("Значение", style="green")

            table.add_row("Всего запросов", str(summary.total_searches))
            table.add_row("Среднее время выполнения", f"{summary.avg_execution_time_ms:.2f} мс")
            table.add_row("Уникальных vault'ов", str(summary.total_vaults_searched))

            console.print(table)

            if summary.searches_by_type:
                console.print("\n[cyan]По типам поиска:[/cyan]")
                type_table = Table()
                type_table.add_column("Тип", style="yellow")
                type_table.add_column("Количество", style="green")
                type_table.add_column("Процент", style="blue")

                for search_type, count in sorted(summary.searches_by_type.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / summary.total_searches * 100) if summary.total_searches > 0 else 0
                    type_table.add_row(search_type, str(count), f"{percentage:.1f}%")

                console.print(type_table)

            if summary.popular_queries:
                console.print("\n[cyan]Популярные запросы:[/cyan]")
                query_table = Table()
                query_table.add_column("№", style="cyan")
                query_table.add_column("Запрос", style="green")
                query_table.add_column("Количество", style="yellow")

                for idx, (query, count) in enumerate(summary.popular_queries, 1):
                    query_display = query[:60] + "..." if len(query) > 60 else query
                    query_table.add_row(str(idx), query_display, str(count))

                console.print(query_table)

            if summary.popular_vaults:
                console.print("\n[cyan]Популярные vault'ы:[/cyan]")
                vault_table = Table()
                vault_table.add_column("№", style="cyan")
                vault_table.add_column("Vault", style="green")
                vault_table.add_column("Запросов", style="yellow")

                for idx, (vault, count) in enumerate(summary.popular_vaults, 1):
                    vault_table.add_row(str(idx), vault, str(count))

                console.print(vault_table)

            if summary.total_searches == 0:
                console.print("\n[yellow]Метрики за указанный период отсутствуют[/yellow]")

        except Exception as e:
            console.print(f"[red]Ошибка получения метрик: {e}[/red]")
            logger.exception("Error getting metrics")
            sys.exit(1)

    asyncio.run(metrics_async())


@click.command("clear-metrics")
@click.option("--days", default=90, help="Количество дней для хранения метрик (default: 90)")
def clear_metrics(days: int) -> None:
    """Очистка старых метрик."""
    async def clear_metrics_async() -> None:
        try:
            metrics_collector = MetricsCollector()
            deleted = await metrics_collector.clear_old_metrics(days_to_keep=days)
            console.print(f"[green]✓ Удалено {deleted} старых метрик (старше {days} дней)[/green]")
        except Exception as e:
            console.print(f"[red]Ошибка очистки метрик: {e}[/red]")
            logger.exception("Error clearing metrics")
            sys.exit(1)

    asyncio.run(clear_metrics_async())


@click.command("reset-circuit-breaker")
@click.option("--operation", default="llm_enrichment", help="Имя операции для сброса circuit breaker (default: llm_enrichment)")
def reset_circuit_breaker(operation: str) -> None:
    """Сброс Circuit Breaker для указанной операции."""
    async def reset_async() -> None:
        from obsidian_kb.recovery import get_recovery_service

        recovery_service = get_recovery_service()
        circuit_breaker = recovery_service.get_circuit_breaker(operation)

        current_state = circuit_breaker.get_state()
        failure_count = circuit_breaker.failure_count

        console.print(f"[cyan]Сброс Circuit Breaker для операции: {operation}[/cyan]")
        console.print(f"  Текущее состояние: {current_state}")
        console.print(f"  Количество ошибок: {failure_count}")

        success = recovery_service.reset_circuit_breaker(operation)

        if success:
            console.print(f"[green]✓ Circuit Breaker для '{operation}' успешно сброшен[/green]")
            console.print(f"  Новое состояние: {circuit_breaker.get_state()}")
            console.print(f"  Количество ошибок: {circuit_breaker.failure_count}")
        else:
            console.print(f"[red]❌ Не удалось сбросить Circuit Breaker для '{operation}'[/red]")

    asyncio.run(reset_async())
