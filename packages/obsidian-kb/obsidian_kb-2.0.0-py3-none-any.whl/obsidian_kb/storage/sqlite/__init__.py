"""SQLite storage layer for metadata, cache, and graph data.

This module provides SQLite-based storage for:
- Document metadata (normalized frontmatter)
- Tags and links graph
- Embedding cache
- Search history

Usage:
    from obsidian_kb.storage.sqlite import SQLiteManager, create_schema

    async with SQLiteManager("path/to/db.sqlite") as manager:
        await create_schema(manager)
        await manager.execute("SELECT * FROM documents")
"""

from obsidian_kb.storage.sqlite.frontmatter_parser import (
    FrontmatterParseResult,
    FrontmatterParser,
    ParsedProperty,
    PropertyValueType,
)
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.schema import (
    SCHEMA_VERSION,
    create_schema,
    drop_all_tables,
    get_schema_version,
)
from obsidian_kb.storage.sqlite.schema_builder import (
    PropertySchema,
    PropertySchemaBuilder,
    VaultSchema,
)
from obsidian_kb.storage.sqlite.embedding_cache import (
    CacheEntry,
    CacheStats,
    EmbeddingCache,
)

__all__ = [
    # Manager
    "SQLiteManager",
    # Schema
    "SCHEMA_VERSION",
    "create_schema",
    "get_schema_version",
    "drop_all_tables",
    # Frontmatter parser
    "FrontmatterParser",
    "FrontmatterParseResult",
    "ParsedProperty",
    "PropertyValueType",
    # Schema builder
    "PropertySchemaBuilder",
    "PropertySchema",
    "VaultSchema",
    # Embedding cache
    "EmbeddingCache",
    "CacheEntry",
    "CacheStats",
]
