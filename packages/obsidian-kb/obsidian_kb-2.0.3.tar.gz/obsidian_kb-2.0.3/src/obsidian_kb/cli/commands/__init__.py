"""CLI commands package."""

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

__all__ = [
    # Config
    "config",
    # Diagnostics
    "check_index",
    "check_metrics",
    "doctor",
    "index_coverage",
    "stats",
    # Index
    "index",
    "index_all",
    "reindex",
    "watch",
    # Misc
    "claude_config",
    "clear_metrics",
    "metrics",
    "reset_circuit_breaker",
    "serve",
    "version",
    # Search
    "search",
    "search_links",
    # Service
    "install_service",
    "restart_service",
    "service_status",
    "uninstall_service",
    # Vault
    "cluster",
    "delete_all_vaults",
    "delete_vault",
    "enrich",
    "list_vaults",
]
