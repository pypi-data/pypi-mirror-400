"""SQLite database schema DDL for obsidian-kb v2.0.

This module defines the complete database schema for storing:
- Vault and document metadata
- Normalized frontmatter properties
- Tags and links graph
- Embedding cache
- Search history
- Entity extraction results (prepared for Release 2.1)

Schema version: 2.0.0
"""

from typing import Final

# Schema version for migrations
SCHEMA_VERSION: Final[str] = "2.0.0"

# =============================================================================
# Core Tables DDL
# =============================================================================

CREATE_VAULTS_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS vaults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_indexed_at TEXT,
    document_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,

    -- Metadata
    settings_json TEXT  -- Vault-specific settings as JSON
);

CREATE INDEX IF NOT EXISTS idx_vaults_name ON vaults(name);
"""

CREATE_DOCUMENTS_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL UNIQUE,  -- {vault_name}::{file_path}
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,

    -- File information
    file_path TEXT NOT NULL,           -- Relative path within vault
    file_name TEXT NOT NULL,           -- File name only (e.g., "note.md")
    title TEXT,                        -- From frontmatter or H1

    -- Content tracking
    content_hash TEXT NOT NULL,        -- SHA256 of file content for change detection
    file_size INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    modified_at TEXT NOT NULL DEFAULT (datetime('now')),
    indexed_at TEXT NOT NULL DEFAULT (datetime('now')),

    UNIQUE(vault_id, file_path)
);

CREATE INDEX IF NOT EXISTS idx_documents_document_id ON documents(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_vault_id ON documents(vault_id);
CREATE INDEX IF NOT EXISTS idx_documents_file_path ON documents(file_path);
CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_modified_at ON documents(modified_at);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);
"""

# =============================================================================
# Normalized Frontmatter Tables DDL
# =============================================================================

CREATE_DOCUMENT_PROPERTIES_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS document_properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Property key-value
    property_key TEXT NOT NULL,
    property_value TEXT,              -- String value (for all types as string)

    -- Type information
    value_type TEXT NOT NULL DEFAULT 'string',  -- string|number|date|boolean|link|list
    value_number REAL,                -- For numeric values
    value_date TEXT,                  -- For date values (ISO 8601)
    value_link_target TEXT,           -- For [[link]] targets (normalized)

    -- List support
    list_index INTEGER DEFAULT 0,     -- Index in array (0 for non-arrays)

    UNIQUE(document_id, property_key, list_index)
);

CREATE INDEX IF NOT EXISTS idx_doc_props_document_id ON document_properties(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_props_key ON document_properties(property_key);
CREATE INDEX IF NOT EXISTS idx_doc_props_key_value ON document_properties(property_key, property_value);
CREATE INDEX IF NOT EXISTS idx_doc_props_value_type ON document_properties(value_type);
CREATE INDEX IF NOT EXISTS idx_doc_props_value_number ON document_properties(value_number) WHERE value_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_doc_props_value_date ON document_properties(value_date) WHERE value_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_doc_props_value_link ON document_properties(value_link_target) WHERE value_link_target IS NOT NULL;
"""

CREATE_PROPERTY_SCHEMAS_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS property_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,

    property_key TEXT NOT NULL,
    inferred_type TEXT NOT NULL DEFAULT 'string',  -- Most common type
    sample_values TEXT,               -- JSON array of sample values
    document_count INTEGER NOT NULL DEFAULT 0,  -- How many documents use this property

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    UNIQUE(vault_id, property_key)
);

CREATE INDEX IF NOT EXISTS idx_prop_schemas_vault_id ON property_schemas(vault_id);
CREATE INDEX IF NOT EXISTS idx_prop_schemas_key ON property_schemas(property_key);
"""

# =============================================================================
# Tags Tables DDL
# =============================================================================

CREATE_TAGS_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,

    name TEXT NOT NULL,               -- Normalized tag name (without #)
    tag_type TEXT NOT NULL DEFAULT 'inline',  -- frontmatter|inline

    -- Statistics
    document_count INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    UNIQUE(vault_id, name, tag_type)
);

CREATE INDEX IF NOT EXISTS idx_tags_vault_id ON tags(vault_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_tags_type ON tags(tag_type);
"""

CREATE_DOCUMENT_TAGS_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS document_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,

    -- Context
    occurrence_count INTEGER NOT NULL DEFAULT 1,  -- How many times in document

    UNIQUE(document_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_doc_tags_document_id ON document_tags(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_tags_tag_id ON document_tags(tag_id);
"""

# =============================================================================
# Links Tables DDL
# =============================================================================

CREATE_LINKS_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Link target
    target_name TEXT NOT NULL,        -- Original link text (e.g., "vshadrin")
    target_document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,  -- Resolved document

    -- Link metadata
    link_type TEXT NOT NULL DEFAULT 'wikilink',  -- wikilink|markdown|external
    context TEXT,                     -- Surrounding text for context

    -- Position in document
    line_number INTEGER,

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_links_source_doc ON links(source_document_id);
CREATE INDEX IF NOT EXISTS idx_links_target_doc ON links(target_document_id) WHERE target_document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_links_target_name ON links(target_name);
CREATE INDEX IF NOT EXISTS idx_links_type ON links(link_type);
"""

# =============================================================================
# Cache Tables DDL
# =============================================================================

CREATE_EMBEDDING_CACHE_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS embedding_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL,       -- SHA256 of content
    model_name TEXT NOT NULL,         -- Embedding model name (e.g., "bge-m3")

    -- Embedding data
    embedding BLOB NOT NULL,          -- Serialized embedding vector (float32 array)
    embedding_dim INTEGER NOT NULL,   -- Dimension of embedding

    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_used_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Access statistics
    access_count INTEGER NOT NULL DEFAULT 1,

    UNIQUE(content_hash, model_name)
);

CREATE INDEX IF NOT EXISTS idx_embed_cache_hash ON embedding_cache(content_hash);
CREATE INDEX IF NOT EXISTS idx_embed_cache_model ON embedding_cache(model_name);
CREATE INDEX IF NOT EXISTS idx_embed_cache_hash_model ON embedding_cache(content_hash, model_name);
CREATE INDEX IF NOT EXISTS idx_embed_cache_last_used ON embedding_cache(last_used_at);
"""

CREATE_SEARCH_HISTORY_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,

    -- Query information
    query_text TEXT NOT NULL,
    query_hash TEXT NOT NULL,         -- For deduplication

    -- Results
    result_count INTEGER NOT NULL DEFAULT 0,
    execution_time_ms INTEGER,

    -- Search parameters
    search_type TEXT NOT NULL DEFAULT 'hybrid',  -- vector|fts|hybrid
    limit_used INTEGER,
    filters_json TEXT,                -- JSON of applied filters

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_search_history_vault_id ON search_history(vault_id);
CREATE INDEX IF NOT EXISTS idx_search_history_query_hash ON search_history(query_hash);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at);
"""

# =============================================================================
# Entity Tables DDL (prepared for Release 2.1)
# =============================================================================

CREATE_ENTITIES_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,

    -- Entity information
    name TEXT NOT NULL,               -- Display name
    canonical_name TEXT NOT NULL,     -- Normalized name for matching
    entity_type TEXT NOT NULL,        -- person|organization|project|location|concept

    -- Aliases for fuzzy matching
    aliases TEXT,                     -- JSON array of alternative names

    -- Link to canonical document
    linked_document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,

    -- Metadata
    metadata_json TEXT,               -- Additional entity metadata

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    UNIQUE(vault_id, canonical_name, entity_type)
);

CREATE INDEX IF NOT EXISTS idx_entities_vault_id ON entities(vault_id);
CREATE INDEX IF NOT EXISTS idx_entities_canonical ON entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_linked_doc ON entities(linked_document_id) WHERE linked_document_id IS NOT NULL;
"""

CREATE_DOCUMENT_ENTITIES_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS document_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,

    -- Occurrence information
    mention_count INTEGER NOT NULL DEFAULT 1,
    context_snippets TEXT,            -- JSON array of context snippets

    -- Confidence
    confidence REAL NOT NULL DEFAULT 1.0,  -- 0.0 to 1.0

    UNIQUE(document_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_doc_entities_document_id ON document_entities(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_entities_entity_id ON document_entities(entity_id);
"""

# =============================================================================
# Schema Metadata Table
# =============================================================================

CREATE_SCHEMA_METADATA_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS schema_metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Ensure single row
    schema_version TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

# =============================================================================
# Complete Schema
# =============================================================================

# All CREATE TABLE statements in order (respecting foreign key dependencies)
ALL_TABLES: Final[list[str]] = [
    CREATE_SCHEMA_METADATA_TABLE,
    CREATE_VAULTS_TABLE,
    CREATE_DOCUMENTS_TABLE,
    CREATE_DOCUMENT_PROPERTIES_TABLE,
    CREATE_PROPERTY_SCHEMAS_TABLE,
    CREATE_TAGS_TABLE,
    CREATE_DOCUMENT_TAGS_TABLE,
    CREATE_LINKS_TABLE,
    CREATE_EMBEDDING_CACHE_TABLE,
    CREATE_SEARCH_HISTORY_TABLE,
    CREATE_ENTITIES_TABLE,
    CREATE_DOCUMENT_ENTITIES_TABLE,
]

# Complete schema as single script
COMPLETE_SCHEMA: Final[str] = "\n\n".join(ALL_TABLES)


async def create_schema(manager: "SQLiteManager") -> None:  # noqa: F821
    """Create all database tables if they don't exist.

    Args:
        manager: SQLiteManager instance

    Raises:
        aiosqlite.Error: If schema creation fails
    """
    from obsidian_kb.storage.sqlite.manager import SQLiteManager

    if not isinstance(manager, SQLiteManager):
        raise TypeError(f"Expected SQLiteManager, got {type(manager)}")

    await manager.execute_script(COMPLETE_SCHEMA)

    # Insert or update schema version
    await manager.execute(
        """
        INSERT INTO schema_metadata (id, schema_version, updated_at)
        VALUES (1, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            schema_version = excluded.schema_version,
            updated_at = datetime('now')
        """,
        (SCHEMA_VERSION,),
    )


async def get_schema_version(manager: "SQLiteManager") -> str | None:  # noqa: F821
    """Get current schema version from database.

    Args:
        manager: SQLiteManager instance

    Returns:
        Schema version string, or None if not initialized
    """
    try:
        result = await manager.fetch_value(
            "SELECT schema_version FROM schema_metadata WHERE id = 1"
        )
        return result
    except Exception:
        return None


async def drop_all_tables(manager: "SQLiteManager") -> None:  # noqa: F821
    """Drop all tables (for testing/reset).

    Args:
        manager: SQLiteManager instance

    Warning:
        This will delete ALL data!
    """
    tables = [
        "document_entities",
        "entities",
        "search_history",
        "embedding_cache",
        "links",
        "document_tags",
        "tags",
        "property_schemas",
        "document_properties",
        "documents",
        "vaults",
        "schema_metadata",
    ]

    for table in tables:
        await manager.execute(f"DROP TABLE IF EXISTS {table}")
