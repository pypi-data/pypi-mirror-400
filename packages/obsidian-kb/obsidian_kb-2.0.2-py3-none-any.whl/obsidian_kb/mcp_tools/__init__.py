"""MCP tools для управления индексацией и другими операциями."""

from obsidian_kb.mcp_tools.indexing_tools import (
    enrich_document,
    index_documents,
    index_status,
    preview_chunks,
    reindex_vault,
)
from obsidian_kb.mcp_tools.provider_tools import (
    estimate_cost,
    list_providers,
    list_yandex_models,
    provider_health,
    set_provider,
    test_provider,
)
from obsidian_kb.mcp_tools.quality_tools import (
    audit_index,
    cost_report,
    index_coverage,
    performance_report,
    test_retrieval,
)

__all__ = [
    # Indexing tools
    "index_documents",
    "reindex_vault",
    "index_status",
    "preview_chunks",
    "enrich_document",
    # Provider tools
    "list_providers",
    "list_yandex_models",
    "set_provider",
    "test_provider",
    "provider_health",
    "estimate_cost",
    # Quality tools
    "index_coverage",
    "test_retrieval",
    "audit_index",
    "cost_report",
    "performance_report",
]

