"""Diagnostics commands: doctor, index_coverage, check_metrics, check_index, stats."""

import asyncio
import json
import sys

import click
from rich.table import Table

from obsidian_kb.cli.utils import console, get_services, logger
from obsidian_kb.types import HealthStatus, VaultNotFoundError


@click.command()
@click.option("--check", type=click.Choice(["ollama", "lancedb", "vaults", "disk"]), help="Проверить конкретный компонент")
@click.option("--json", "output_json", is_flag=True, help="Вывод в JSON формате")
def doctor(check: str | None, output_json: bool) -> None:
    """Полная проверка системы."""
    async def doctor_async() -> None:
        services = get_services()
        diagnostics_service = services.diagnostics_service

        if check:
            check_result = None
            if check == "ollama":
                check_result = await diagnostics_service.check_ollama()
            elif check == "lancedb":
                check_result = await diagnostics_service.check_lancedb()
            elif check == "vaults":
                check_result = await diagnostics_service.check_vaults()
            else:
                check_result = await diagnostics_service.check_disk_space()

            if check_result is None:
                return

            if output_json:
                print(json.dumps({
                    "component": check_result.component,
                    "status": check_result.status.value,
                    "message": check_result.message,
                    "details": check_result.details,
                }, indent=2, default=str))
            else:
                status_emoji = {"ok": "✅", "warning": "⚠️", "error": "❌"}
                console.print(f"{status_emoji[check_result.status.value]} [{check_result.component}] {check_result.message}")
                if check_result.details:
                    console.print(f"  Детали: {check_result.details}")
        else:
            health = await diagnostics_service.full_check()

            if output_json:
                print(json.dumps({
                    "overall": health.overall.value,
                    "timestamp": health.timestamp.isoformat(),
                    "checks": [
                        {
                            "component": c.component,
                            "status": c.status.value,
                            "message": c.message,
                            "details": c.details,
                        }
                        for c in health.checks
                    ],
                }, indent=2, default=str))
            else:
                status_emoji = {"ok": "✅", "warning": "⚠️", "error": "❌"}
                overall_emoji = status_emoji[health.overall.value]

                console.print(f"\n{overall_emoji} [bold]Общий статус:[/bold] {health.overall.value.upper()}\n")

                table = Table()
                table.add_column("Компонент", style="cyan")
                table.add_column("Статус", style="yellow")
                table.add_column("Сообщение", style="white")

                for health_check in health.checks:
                    emoji = status_emoji[health_check.status.value]
                    table.add_row(health_check.component, f"{emoji} {health_check.status.value.upper()}", health_check.message)

                console.print(table)

                errors = [c for c in health.checks if c.status == HealthStatus.ERROR]
                warnings = [c for c in health.checks if c.status == HealthStatus.WARNING]

                if errors:
                    console.print("\n[red]Обнаруженные проблемы:[/red]")
                    for error_check in errors:
                        console.print(f"  • {error_check.component}: {error_check.message}")

                if warnings:
                    console.print("\n[yellow]Предупреждения:[/yellow]")
                    for warning_check in warnings:
                        console.print(f"  • {warning_check.component}: {warning_check.message}")

    asyncio.run(doctor_async())


@click.command("index-coverage")
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--json", "output_json", is_flag=True, help="Вывод в JSON формате")
def index_coverage(vault: str, output_json: bool) -> None:
    """Проверка покрытия индекса для vault'а."""
    async def coverage_async() -> None:
        services = get_services()
        diagnostics_service = services.diagnostics_service

        result = await diagnostics_service.index_coverage(vault)

        if output_json:
            print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        else:
            if "error" in result:
                console.print(f"[red]Ошибка:[/red] {result['error']}")
                return

            console.print(f"\n[bold]Покрытие индекса для vault '{vault}':[/bold]\n")

            table = Table()
            table.add_column("Параметр", style="cyan")
            table.add_column("Значение", style="white")

            table.add_row("Всего файлов", str(result.get("total_files", 0)))
            table.add_row("Индексировано файлов", str(result.get("indexed_files", 0)))
            table.add_row("Покрытие", f"{result.get('coverage_percent', 0):.1f}%")
            table.add_row("Всего чанков", str(result.get("total_chunks", 0)))

            console.print(table)

            type_stats = result.get("type_stats", {})
            if type_stats:
                console.print("\n[bold]Статистика по типам документов:[/bold]")
                type_table = Table()
                type_table.add_column("Тип", style="cyan")
                type_table.add_column("Количество", style="white")
                for doc_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
                    type_table.add_row(doc_type, str(count))
                console.print(type_table)

            tag_stats = result.get("tag_stats", {})
            if tag_stats:
                frontmatter_tags = tag_stats.get("frontmatter", {})
                inline_tags = tag_stats.get("inline", {})

                if frontmatter_tags:
                    console.print("\n[bold]Топ-10 frontmatter тегов:[/bold]")
                    tag_table = Table()
                    tag_table.add_column("Тег", style="cyan")
                    tag_table.add_column("Количество", style="white")
                    for tag, count in sorted(frontmatter_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
                        tag_table.add_row(tag, str(count))
                    console.print(tag_table)

                if inline_tags:
                    console.print("\n[bold]Топ-10 inline тегов:[/bold]")
                    tag_table = Table()
                    tag_table.add_column("Тег", style="cyan")
                    tag_table.add_column("Количество", style="white")
                    for tag, count in sorted(inline_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
                        tag_table.add_row(tag, str(count))
                    console.print(tag_table)

            link_stats = result.get("link_stats", {})
            if link_stats:
                console.print("\n[bold]Топ-10 ссылок:[/bold]")
                link_table = Table()
                link_table.add_column("Ссылка", style="cyan")
                link_table.add_column("Количество", style="white")
                for link, count in sorted(link_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                    link_table.add_row(link, str(count))
                console.print(link_table)

    asyncio.run(coverage_async())


@click.command("check-metrics")
@click.option("--days", default=1, help="Количество дней для проверки (default: 1)")
@click.option("--json", "output_json", is_flag=True, help="Вывод в JSON формате")
def check_metrics(days: int, output_json: bool) -> None:
    """Проверка записи метрик."""
    async def check_metrics_async() -> None:
        services = get_services()
        diagnostics_service = services.diagnostics_service

        result = await diagnostics_service.check_metrics(days=days)

        if output_json:
            print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        else:
            if "error" in result:
                console.print(f"[red]Ошибка:[/red] {result['error']}")
                return

            console.print(f"\n[bold]Проверка метрик (за {days} дней):[/bold]\n")

            table = Table()
            table.add_column("Параметр", style="cyan")
            table.add_column("Значение", style="white")

            table.add_row("Всего запросов", str(result.get("total_queries", 0)))
            table.add_row("Всего поисков", str(result.get("total_searches", 0)))
            table.add_row("Среднее время ответа", f"{result.get('average_response_time', 0):.2f} мс")
            table.add_row("БД метрик существует", "✅" if result.get("metrics_db_exists", False) else "❌")

            console.print(table)

            if result.get("total_queries", 0) == 0:
                console.print("\n[yellow]Предупреждение:[/yellow] Метрики не записываются или нет данных за указанный период.")

    asyncio.run(check_metrics_async())


@click.command("check-index")
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--json", "output_json", is_flag=True, help="Вывод в JSON формате")
def check_index(vault: str, output_json: bool) -> None:
    """Проверка индексации vault'а."""
    async def check_index_async() -> None:
        services = get_services()
        diagnostics_service = services.diagnostics_service

        result = await diagnostics_service.check_index(vault)

        if output_json:
            print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        else:
            if "error" in result:
                console.print(f"[red]Ошибка:[/red] {result['error']}")
                if result.get("needs_indexing"):
                    console.print(f"[yellow]Рекомендация:[/yellow] Выполните индексацию: obsidian-kb index --vault {vault} --path <path>")
                return

            console.print(f"\n[bold]Проверка индексации vault '{vault}':[/bold]\n")

            table = Table()
            table.add_column("Параметр", style="cyan")
            table.add_column("Значение", style="white")

            status = result.get("status", "unknown")
            status_emoji = {"ok": "✅", "warning": "⚠️", "error": "❌"}
            table.add_row("Статус", f"{status_emoji.get(status, '❓')} {status.upper()}")
            table.add_row("Индексировано", "✅" if result.get("indexed", False) else "❌")
            table.add_row("Всего чанков", str(result.get("total_chunks", 0)))

            console.print(table)

            issues = result.get("issues", [])
            if issues:
                console.print("\n[yellow]Обнаруженные проблемы:[/yellow]")
                for issue in issues:
                    console.print(f"  • {issue}")
            else:
                console.print("\n[green]Проблем не обнаружено.[/green]")

    asyncio.run(check_index_async())


@click.command()
@click.option("--vault", required=True, help="Имя vault'а")
def stats(vault: str) -> None:
    """Статистика vault'а."""
    async def stats_async() -> None:
        services = get_services()
        db_manager = services.db_manager

        try:
            vault_stats = await db_manager.get_vault_stats(vault)

            table = Table(title=f"Статистика vault: {vault}")
            table.add_column("Параметр", style="cyan")
            table.add_column("Значение", style="green")

            table.add_row("Файлов", str(vault_stats.file_count))
            table.add_row("Чанков", str(vault_stats.chunk_count))
            table.add_row("Размер", f"{vault_stats.total_size_bytes / 1024:.1f} KB")
            table.add_row("Тегов", str(len(vault_stats.tags)))

            if vault_stats.oldest_file:
                table.add_row("Старейший файл", vault_stats.oldest_file.strftime("%Y-%m-%d %H:%M:%S"))
            if vault_stats.newest_file:
                table.add_row("Новейший файл", vault_stats.newest_file.strftime("%Y-%m-%d %H:%M:%S"))

            console.print(table)

            if vault_stats.tags:
                console.print(f"\n[cyan]Теги ({len(vault_stats.tags)}):[/cyan]")
                console.print(", ".join(vault_stats.tags[:50]))
                if len(vault_stats.tags) > 50:
                    console.print(f"... и ещё {len(vault_stats.tags) - 50} тегов")

        except VaultNotFoundError:
            console.print(f"[red]Vault '{vault}' не найден[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception("Error getting stats")
            sys.exit(1)

    asyncio.run(stats_async())
