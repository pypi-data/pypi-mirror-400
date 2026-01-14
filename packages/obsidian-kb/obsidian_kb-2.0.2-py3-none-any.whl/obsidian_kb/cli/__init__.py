"""CLI интерфейс для obsidian-kb.

Refactored modular CLI structure for better maintainability.
"""

import logging

import click

from obsidian_kb.cli.commands.config import config
from obsidian_kb.cli.commands.diagnostics import (
    check_index,
    check_metrics,
    doctor,
    index_coverage,
    stats,
)
from obsidian_kb.cli.commands.index import index, index_all, reindex
from obsidian_kb.cli.commands.watch import watch
from obsidian_kb.cli.commands.misc import (
    claude_config,
    clear_metrics,
    metrics,
    reset_circuit_breaker,
    serve,
    version,
)
from obsidian_kb.cli.commands.search import search, search_links
from obsidian_kb.cli.commands.service import (
    install_service,
    restart_service,
    service_status,
    uninstall_service,
)
from obsidian_kb.cli.commands.vault import (
    cluster,
    delete_all_vaults,
    delete_vault,
    enrich,
    list_vaults,
)
from obsidian_kb.structured_logging import setup_structured_logging


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Включить подробный вывод")
@click.option("--json-logs", is_flag=True, help="Вывод логов в JSON формате")
def cli(verbose: bool, json_logs: bool) -> None:
    """obsidian-kb - локальная система управления знаниями для Obsidian vault'ов."""
    level = logging.DEBUG if verbose else logging.INFO
    setup_structured_logging(level=level, json_format=json_logs)


# Register all commands
cli.add_command(index_all)
cli.add_command(index)
cli.add_command(reindex)
cli.add_command(watch)
cli.add_command(search)
cli.add_command(search_links)
cli.add_command(stats)
cli.add_command(serve)
cli.add_command(doctor)
cli.add_command(index_coverage)
cli.add_command(check_metrics)
cli.add_command(check_index)
cli.add_command(install_service)
cli.add_command(uninstall_service)
cli.add_command(service_status)
cli.add_command(restart_service)
cli.add_command(version)
cli.add_command(list_vaults)
cli.add_command(delete_vault)
cli.add_command(delete_all_vaults)
cli.add_command(config)
cli.add_command(claude_config)
cli.add_command(metrics)
cli.add_command(clear_metrics)
cli.add_command(enrich)
cli.add_command(reset_circuit_breaker)
cli.add_command(cluster)


def main() -> None:
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
