"""
obsidian-kb Database Layer v2.1
Hybrid storage: SQLite for relational data, LanceDB for vectors
Normalized frontmatter in DOCUMENT_PROPERTIES table
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Protocol

import lancedb
import numpy as np
import pyarrow as pa


# ============================================================
# Enums & Constants
# ============================================================

class ValueType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    LINK = "link"


class LinkType(str, Enum):
    WIKILINK = "wikilink"
    EMBED = "embed"
    PROPERTY = "property"
    EXTERNAL = "external"


class ContextType(str, Enum):
    FRONTMATTER = "frontmatter"
    HEADING = "heading"
    PARAGRAPH = "paragraph"


# ============================================================
# Data Models
# ============================================================

@dataclass
class Vault:
    id: str
    name: str
    path: str
    config: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_indexed_at: Optional[datetime] = None
    doc_count: int = 0
    chunk_count: int = 0


@dataclass
class Document:
    id: str
    vault_id: str
    path: str
    doc_id: Optional[str]
    title: Optional[str]
    doc_type: Optional[str]
    content_hash: str
    content: Optional[str] = None
    file_created_at: Optional[datetime] = None
    file_modified_at: Optional[datetime] = None
    indexed_at: datetime = field(default_factory=datetime.now)
    chunk_count: int = 0
    link_count: int = 0
    backlink_count: int = 0


@dataclass
class PropertySchema:
    id: str
    vault_id: str
    key: str
    value_type: ValueType
    description: Optional[str] = None
    allowed_values: Optional[list[str]] = None
    is_required: bool = False
    is_list: bool = False
    doc_count: int = 0


@dataclass
class DocumentProperty:
    id: str
    document_id: str
    schema_id: Optional[str]
    key: str
    value_type: ValueType
    value_string: Optional[str] = None
    value_number: Optional[float] = None
    value_date: Optional[str] = None
    value_boolean: Optional[bool] = None
    value_link_target: Optional[str] = None
    value_link_raw: Optional[str] = None
    list_index: int = 0
    source: str = "frontmatter"


@dataclass
class Tag:
    id: str
    vault_id: str
    name: str
    normalized: str
    parent_tag_id: Optional[str] = None
    doc_count: int = 0


@dataclass
class Link:
    id: str
    source_doc_id: str
    target_doc_id: Optional[str]
    target_raw: str
    link_type: LinkType
    anchor_text: Optional[str] = None
    context_type: Optional[ContextType] = None
    context_value: Optional[str] = None
    position: int = 0


@dataclass
class Entity:
    id: str
    vault_id: str
    name: str
    normalized_id: str
    entity_type: str
    canonical_doc_id: Optional[str] = None
    aliases: list[str] = field(default_factory=list)
    mention_count: int = 0


@dataclass
class Chunk:
    id: str
    document_id: str
    vault_id: str
    chunk_index: int
    content: str
    context: str
    embedding: np.ndarray
    start_offset: int
    end_offset: int
    heading: Optional[str] = None
    doc_type: Optional[str] = None
    doc_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    file_modified_at: Optional[datetime] = None


# ============================================================
# Repository Protocols
# ============================================================

class IDocumentRepository(Protocol):
    def upsert(self, doc: Document) -> bool: ...
    def get_by_id(self, doc_id: str) -> Optional[Document]: ...
    def get_by_doc_id(self, vault_id: str, doc_id: str) -> Optional[Document]: ...
    def get_changed(self, vault_id: str, file_hashes: dict[str, str]) -> dict: ...
    def delete(self, doc_id: str) -> bool: ...


class IPropertyRepository(Protocol):
    def upsert_batch(self, properties: list[DocumentProperty]) -> int: ...
    def get_by_document(self, document_id: str) -> list[DocumentProperty]: ...
    def find_by_property(self, vault_id: str, key: str, value: Any) -> list[str]: ...
    def aggregate_by_key(self, vault_id: str, key: str, doc_type: Optional[str]) -> dict: ...


class IChunkRepository(Protocol):
    def upsert_batch(self, chunks: list[Chunk]) -> int: ...
    def delete_by_document(self, document_id: str) -> int: ...
    def search_vector(self, vault_id: str, embedding: np.ndarray, 
                      filters: Optional[dict], limit: int) -> list[dict]: ...
    def search_hybrid(self, vault_id: str, query: str, embedding: np.ndarray,
                      filters: Optional[dict], limit: int) -> list[dict]: ...


# ============================================================
# SQLite Database Manager
# ============================================================

class SQLiteManager:
    """Manages SQLite connection and schema for metadata."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Create all SQLite tables."""
        self.conn.executescript("""
            -- Vaults
            CREATE TABLE IF NOT EXISTS vaults (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                path TEXT NOT NULL,
                config JSON DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_indexed_at TIMESTAMP,
                doc_count INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0
            );
            
            -- Documents
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
                path TEXT NOT NULL,
                doc_id TEXT,
                title TEXT,
                doc_type TEXT,
                content_hash TEXT NOT NULL,
                content TEXT,
                file_created_at TIMESTAMP,
                file_modified_at TIMESTAMP,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chunk_count INTEGER DEFAULT 0,
                link_count INTEGER DEFAULT 0,
                backlink_count INTEGER DEFAULT 0,
                UNIQUE(vault_id, path)
            );
            
            CREATE INDEX IF NOT EXISTS idx_documents_vault_type 
                ON documents(vault_id, doc_type);
            CREATE INDEX IF NOT EXISTS idx_documents_doc_id 
                ON documents(vault_id, doc_id);
            CREATE INDEX IF NOT EXISTS idx_documents_hash 
                ON documents(content_hash);
            CREATE INDEX IF NOT EXISTS idx_documents_modified 
                ON documents(vault_id, file_modified_at DESC);
            
            -- Property Schemas
            CREATE TABLE IF NOT EXISTS property_schemas (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
                key TEXT NOT NULL,
                value_type TEXT NOT NULL,
                description TEXT,
                allowed_values JSON,
                is_required INTEGER DEFAULT 0,
                is_list INTEGER DEFAULT 0,
                doc_count INTEGER DEFAULT 0,
                UNIQUE(vault_id, key)
            );
            
            -- Document Properties (normalized frontmatter)
            CREATE TABLE IF NOT EXISTS document_properties (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                schema_id TEXT REFERENCES property_schemas(id),
                key TEXT NOT NULL,
                value_type TEXT NOT NULL,
                value_string TEXT,
                value_number REAL,
                value_date TEXT,
                value_boolean INTEGER,
                value_link_target TEXT,
                value_link_raw TEXT,
                list_index INTEGER DEFAULT 0,
                source TEXT DEFAULT 'frontmatter'
            );
            
            CREATE INDEX IF NOT EXISTS idx_props_document 
                ON document_properties(document_id);
            CREATE INDEX IF NOT EXISTS idx_props_key 
                ON document_properties(key);
            CREATE INDEX IF NOT EXISTS idx_props_key_string 
                ON document_properties(key, value_string);
            CREATE INDEX IF NOT EXISTS idx_props_key_number 
                ON document_properties(key, value_number);
            CREATE INDEX IF NOT EXISTS idx_props_key_date 
                ON document_properties(key, value_date);
            CREATE INDEX IF NOT EXISTS idx_props_link_target 
                ON document_properties(value_link_target);
            
            -- Tags
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                normalized TEXT NOT NULL,
                parent_tag_id TEXT REFERENCES tags(id),
                doc_count INTEGER DEFAULT 0,
                UNIQUE(vault_id, normalized)
            );
            
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                tag_id TEXT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                source TEXT DEFAULT 'frontmatter',
                PRIMARY KEY(document_id, tag_id)
            );
            
            -- Links (Graph)
            CREATE TABLE IF NOT EXISTS links (
                id TEXT PRIMARY KEY,
                source_doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                target_doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
                target_raw TEXT NOT NULL,
                link_type TEXT NOT NULL,
                anchor_text TEXT,
                context_type TEXT,
                context_value TEXT,
                position INTEGER
            );
            
            CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_doc_id);
            CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_doc_id);
            CREATE INDEX IF NOT EXISTS idx_links_type ON links(link_type);
            
            -- Entities (NER)
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                normalized_id TEXT,
                entity_type TEXT NOT NULL,
                canonical_doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
                aliases JSON DEFAULT '[]',
                mention_count INTEGER DEFAULT 0,
                UNIQUE(vault_id, normalized_id)
            );
            
            CREATE TABLE IF NOT EXISTS document_entities (
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
                mention_count INTEGER DEFAULT 1,
                positions JSON,
                confidence REAL DEFAULT 1.0,
                PRIMARY KEY(document_id, entity_id)
            );
            
            -- Embedding Cache
            CREATE TABLE IF NOT EXISTS embedding_cache (
                content_hash TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                embedding BLOB NOT NULL,
                embedding_dim INTEGER NOT NULL,
                token_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Search History
            CREATE TABLE IF NOT EXISTS search_history (
                id TEXT PRIMARY KEY,
                vault_id TEXT REFERENCES vaults(id),
                query TEXT NOT NULL,
                intent TEXT,
                filters JSON,
                results_count INTEGER,
                top_doc_ids JSON,
                latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)
    
    def executemany(self, sql: str, params_list: list[tuple]) -> sqlite3.Cursor:
        return self.conn.executemany(sql, params_list)
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.conn.close()


# ============================================================
# Document Property Repository
# ============================================================

class PropertyRepository:
    """Repository for normalized frontmatter properties."""
    
    def __init__(self, db: SQLiteManager):
        self.db = db
    
    def upsert_batch(self, properties: list[DocumentProperty]) -> int:
        """Upsert multiple properties."""
        if not properties:
            return 0
        
        # Delete existing properties for these documents
        doc_ids = list(set(p.document_id for p in properties))
        placeholders = ",".join("?" * len(doc_ids))
        self.db.execute(
            f"DELETE FROM document_properties WHERE document_id IN ({placeholders})",
            tuple(doc_ids)
        )
        
        # Insert new properties
        self.db.executemany("""
            INSERT INTO document_properties 
                (id, document_id, schema_id, key, value_type,
                 value_string, value_number, value_date, value_boolean,
                 value_link_target, value_link_raw, list_index, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (p.id, p.document_id, p.schema_id, p.key, p.value_type.value,
             p.value_string, p.value_number, p.value_date, 
             1 if p.value_boolean else (0 if p.value_boolean is False else None),
             p.value_link_target, p.value_link_raw, p.list_index, p.source)
            for p in properties
        ])
        
        self.db.commit()
        return len(properties)
    
    def get_by_document(self, document_id: str) -> list[DocumentProperty]:
        """Get all properties for a document."""
        rows = self.db.execute(
            "SELECT * FROM document_properties WHERE document_id = ? ORDER BY key, list_index",
            (document_id,)
        ).fetchall()
        
        return [self._row_to_property(row) for row in rows]
    
    def find_by_property(
        self, 
        vault_id: str, 
        key: str, 
        value: Any,
        value_type: Optional[ValueType] = None
    ) -> list[str]:
        """Find document IDs by property value."""
        
        # Determine value type and column
        if value_type == ValueType.NUMBER or isinstance(value, (int, float)):
            column = "value_number"
            typed_value = float(value)
        elif value_type == ValueType.DATE:
            column = "value_date"
            typed_value = str(value)
        elif value_type == ValueType.BOOLEAN or isinstance(value, bool):
            column = "value_boolean"
            typed_value = 1 if value else 0
        elif value_type == ValueType.LINK:
            column = "value_link_target"
            typed_value = str(value)
        else:
            column = "value_string"
            typed_value = str(value)
        
        rows = self.db.execute(f"""
            SELECT DISTINCT p.document_id
            FROM document_properties p
            JOIN documents d ON p.document_id = d.id
            WHERE d.vault_id = ? AND p.key = ? AND p.{column} = ?
        """, (vault_id, key, typed_value)).fetchall()
        
        return [row["document_id"] for row in rows]
    
    def aggregate_by_key(
        self, 
        vault_id: str, 
        key: str, 
        doc_type: Optional[str] = None
    ) -> dict[str, int]:
        """Aggregate document count by property value."""
        
        sql = """
            SELECT 
                COALESCE(p.value_string, CAST(p.value_number AS TEXT), p.value_date) as value,
                COUNT(DISTINCT p.document_id) as count
            FROM document_properties p
            JOIN documents d ON p.document_id = d.id
            WHERE d.vault_id = ? AND p.key = ?
        """
        params = [vault_id, key]
        
        if doc_type:
            sql += " AND d.doc_type = ?"
            params.append(doc_type)
        
        sql += " GROUP BY value ORDER BY count DESC"
        
        rows = self.db.execute(sql, tuple(params)).fetchall()
        return {row["value"]: row["count"] for row in rows}
    
    def _row_to_property(self, row: sqlite3.Row) -> DocumentProperty:
        return DocumentProperty(
            id=row["id"],
            document_id=row["document_id"],
            schema_id=row["schema_id"],
            key=row["key"],
            value_type=ValueType(row["value_type"]),
            value_string=row["value_string"],
            value_number=row["value_number"],
            value_date=row["value_date"],
            value_boolean=bool(row["value_boolean"]) if row["value_boolean"] is not None else None,
            value_link_target=row["value_link_target"],
            value_link_raw=row["value_link_raw"],
            list_index=row["list_index"],
            source=row["source"]
        )


# ============================================================
# Frontmatter Parser
# ============================================================

class FrontmatterParser:
    """Parse frontmatter dict into normalized DocumentProperty records."""
    
    # Fields stored in documents table, not properties
    SKIP_FIELDS = {"title", "type", "id"}
    
    # Date pattern
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    
    # Wikilink pattern
    WIKILINK_PATTERN = re.compile(r"^\[\[(.+?)(?:\|.+?)?\]\]$")
    
    def parse(
        self, 
        document_id: str, 
        frontmatter: dict[str, Any],
        schema_cache: Optional[dict[str, str]] = None
    ) -> list[DocumentProperty]:
        """Convert frontmatter to property records."""
        
        properties = []
        schema_cache = schema_cache or {}
        
        for key, value in frontmatter.items():
            if key in self.SKIP_FIELDS:
                continue
            
            schema_id = schema_cache.get(key)
            
            # Handle lists
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    prop = self._create_property(document_id, schema_id, key, item, idx)
                    if prop:
                        properties.append(prop)
            else:
                prop = self._create_property(document_id, schema_id, key, value, 0)
                if prop:
                    properties.append(prop)
        
        return properties
    
    def _create_property(
        self,
        document_id: str,
        schema_id: Optional[str],
        key: str,
        value: Any,
        list_index: int
    ) -> Optional[DocumentProperty]:
        """Create a single property with detected type."""
        
        if value is None:
            return None
        
        prop = DocumentProperty(
            id=f"{document_id}_{key}_{list_index}",
            document_id=document_id,
            schema_id=schema_id,
            key=key,
            value_type=ValueType.STRING,
            list_index=list_index
        )
        
        # Detect type
        if isinstance(value, bool):
            prop.value_type = ValueType.BOOLEAN
            prop.value_boolean = value
        
        elif isinstance(value, (int, float)):
            prop.value_type = ValueType.NUMBER
            prop.value_number = float(value)
        
        elif isinstance(value, str):
            # Check wikilink
            match = self.WIKILINK_PATTERN.match(value)
            if match:
                prop.value_type = ValueType.LINK
                prop.value_link_raw = value
                prop.value_link_target = self._extract_doc_id(match.group(1))
            
            # Check date
            elif self.DATE_PATTERN.match(value):
                prop.value_type = ValueType.DATE
                prop.value_date = value
            
            # String
            else:
                prop.value_type = ValueType.STRING
                prop.value_string = value
        
        else:
            # Convert to string
            prop.value_type = ValueType.STRING
            prop.value_string = str(value)
        
        return prop
    
    def _extract_doc_id(self, link_content: str) -> str:
        """Extract doc_id from link path."""
        # Remove alias: path/to/doc|alias → path/to/doc
        if "|" in link_content:
            link_content = link_content.split("|")[0]
        
        # Get last component without .md
        doc_id = link_content.split("/")[-1]
        if doc_id.endswith(".md"):
            doc_id = doc_id[:-3]
        
        return doc_id


# ============================================================
# LanceDB Manager
# ============================================================

class LanceDBManager:
    """Manages LanceDB for vector storage."""
    
    EMBEDDING_DIM = 1024  # BGE-M3
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db = lancedb.connect(str(db_path))
        self._init_schema()
    
    def _init_schema(self):
        """Create chunks table if not exists."""
        if "chunks" not in self.db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("document_id", pa.string()),
                pa.field("vault_id", pa.string()),
                pa.field("chunk_index", pa.int32()),
                pa.field("content", pa.string()),
                pa.field("context", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), self.EMBEDDING_DIM)),
                pa.field("start_offset", pa.int32()),
                pa.field("end_offset", pa.int32()),
                pa.field("heading", pa.string()),
                pa.field("doc_type", pa.string()),
                pa.field("doc_id", pa.string()),
                pa.field("tags", pa.list_(pa.string())),
                pa.field("file_modified_at", pa.timestamp("us")),
            ])
            self.db.create_table("chunks", schema=schema)
    
    def upsert_chunks(self, chunks: list[Chunk]) -> int:
        """Upsert chunks with vectors."""
        if not chunks:
            return 0
        
        table = self.db.open_table("chunks")
        
        # Delete existing chunks for these documents
        doc_ids = list(set(c.document_id for c in chunks))
        for doc_id in doc_ids:
            try:
                table.delete(f"document_id = '{doc_id}'")
            except Exception:
                pass  # Table might be empty
        
        # Insert new chunks
        data = [{
            "id": c.id,
            "document_id": c.document_id,
            "vault_id": c.vault_id,
            "chunk_index": c.chunk_index,
            "content": c.content,
            "context": c.context,
            "embedding": c.embedding.tolist(),
            "start_offset": c.start_offset,
            "end_offset": c.end_offset,
            "heading": c.heading or "",
            "doc_type": c.doc_type or "",
            "doc_id": c.doc_id or "",
            "tags": c.tags,
            "file_modified_at": c.file_modified_at.isoformat() if c.file_modified_at else None,
        } for c in chunks]
        
        table.add(data)
        return len(chunks)
    
    def search_vector(
        self,
        vault_id: str,
        embedding: np.ndarray,
        filters: Optional[dict] = None,
        limit: int = 10
    ) -> list[dict]:
        """Vector similarity search."""
        table = self.db.open_table("chunks")
        
        query = table.search(embedding.tolist())
        
        # Build filter
        where_clauses = [f"vault_id = '{vault_id}'"]
        if filters:
            if "doc_type" in filters:
                where_clauses.append(f"doc_type = '{filters['doc_type']}'")
            if "doc_id" in filters:
                where_clauses.append(f"doc_id = '{filters['doc_id']}'")
        
        query = query.where(" AND ".join(where_clauses))
        
        return query.limit(limit).to_list()
    
    def search_hybrid(
        self,
        vault_id: str,
        text_query: str,
        embedding: np.ndarray,
        filters: Optional[dict] = None,
        limit: int = 10
    ) -> list[dict]:
        """Hybrid vector + FTS search."""
        table = self.db.open_table("chunks")
        
        query = table.search(embedding.tolist(), query_type="hybrid")
        
        where_clauses = [f"vault_id = '{vault_id}'"]
        if filters:
            if "doc_type" in filters:
                where_clauses.append(f"doc_type = '{filters['doc_type']}'")
        
        query = query.where(" AND ".join(where_clauses))
        
        return query.limit(limit).to_list()


# ============================================================
# Unified Database Manager
# ============================================================

class ObsidianKBDatabase:
    """Unified database manager combining SQLite and LanceDB."""
    
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize stores
        self.sqlite = SQLiteManager(self.data_dir / "metadata.db")
        self.lance = LanceDBManager(self.data_dir / "vectors.lance")
        
        # Initialize repositories
        self.properties = PropertyRepository(self.sqlite)
        self.parser = FrontmatterParser()
    
    # --------------------------------------------------------
    # Document Operations
    # --------------------------------------------------------
    
    def upsert_document(self, doc: Document, frontmatter: dict[str, Any]) -> bool:
        """Upsert document with normalized frontmatter."""
        
        # Check if changed
        existing = self.sqlite.execute(
            "SELECT content_hash FROM documents WHERE vault_id = ? AND path = ?",
            (doc.vault_id, doc.path)
        ).fetchone()
        
        if existing and existing["content_hash"] == doc.content_hash:
            return False  # No changes
        
        # Upsert document
        self.sqlite.execute("""
            INSERT INTO documents 
                (id, vault_id, path, doc_id, title, doc_type, content_hash,
                 content, file_created_at, file_modified_at, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(vault_id, path) DO UPDATE SET
                doc_id = excluded.doc_id,
                title = excluded.title,
                doc_type = excluded.doc_type,
                content_hash = excluded.content_hash,
                content = excluded.content,
                file_modified_at = excluded.file_modified_at,
                indexed_at = excluded.indexed_at
        """, (
            doc.id, doc.vault_id, doc.path, doc.doc_id, doc.title,
            doc.doc_type, doc.content_hash, doc.content,
            doc.file_created_at.isoformat() if doc.file_created_at else None,
            doc.file_modified_at.isoformat() if doc.file_modified_at else None,
            doc.indexed_at.isoformat()
        ))
        self.sqlite.commit()
        
        # Parse and store properties
        properties = self.parser.parse(doc.id, frontmatter)
        self.properties.upsert_batch(properties)
        
        return True
    
    def get_document_by_doc_id(self, vault_id: str, doc_id: str) -> Optional[dict]:
        """Get document by semantic ID."""
        row = self.sqlite.execute(
            "SELECT * FROM documents WHERE vault_id = ? AND doc_id = ?",
            (vault_id, doc_id)
        ).fetchone()
        return dict(row) if row else None
    
    # --------------------------------------------------------
    # Property Queries
    # --------------------------------------------------------
    
    def find_documents_by_property(
        self,
        vault_id: str,
        key: str,
        value: Any
    ) -> list[dict]:
        """Find documents by frontmatter property."""
        doc_ids = self.properties.find_by_property(vault_id, key, value)
        
        if not doc_ids:
            return []
        
        placeholders = ",".join("?" * len(doc_ids))
        rows = self.sqlite.execute(
            f"SELECT * FROM documents WHERE id IN ({placeholders})",
            tuple(doc_ids)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_property_stats(
        self,
        vault_id: str,
        key: str,
        doc_type: Optional[str] = None
    ) -> dict[str, int]:
        """Get aggregation stats for a property."""
        return self.properties.aggregate_by_key(vault_id, key, doc_type)
    
    def get_vault_schema(self, vault_id: str) -> list[dict]:
        """Get property schema for vault."""
        rows = self.sqlite.execute("""
            SELECT key, value_type, is_list, allowed_values, doc_count
            FROM property_schemas
            WHERE vault_id = ?
            ORDER BY doc_count DESC
        """, (vault_id,)).fetchall()
        return [dict(row) for row in rows]
    
    # --------------------------------------------------------
    # Vector Search
    # --------------------------------------------------------
    
    def search(
        self,
        vault_id: str,
        query_embedding: np.ndarray,
        filters: Optional[dict] = None,
        limit: int = 10,
        hybrid: bool = False,
        text_query: Optional[str] = None
    ) -> list[dict]:
        """Search chunks with optional filters."""
        if hybrid and text_query:
            return self.lance.search_hybrid(
                vault_id, text_query, query_embedding, filters, limit
            )
        return self.lance.search_vector(
            vault_id, query_embedding, filters, limit
        )
    
    # --------------------------------------------------------
    # Graph Queries
    # --------------------------------------------------------
    
    def get_backlinks(self, document_id: str) -> list[dict]:
        """Get documents linking to this one."""
        rows = self.sqlite.execute("""
            SELECT d.*, l.link_type, l.anchor_text, l.context_type, l.context_value
            FROM documents d
            JOIN links l ON d.id = l.source_doc_id
            WHERE l.target_doc_id = ?
        """, (document_id,)).fetchall()
        return [dict(row) for row in rows]
    
    def get_outlinks(self, document_id: str) -> list[dict]:
        """Get documents this one links to."""
        rows = self.sqlite.execute("""
            SELECT d.*, l.link_type, l.anchor_text, l.context_type, l.context_value
            FROM documents d
            JOIN links l ON d.id = l.target_doc_id
            WHERE l.source_doc_id = ?
        """, (document_id,)).fetchall()
        return [dict(row) for row in rows]
    
    def close(self):
        """Close database connections."""
        self.sqlite.close()


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    # Initialize database
    db = ObsidianKBDatabase("/Users/mdemyanov/.obsidian-kb/data")
    
    # Create document with frontmatter
    doc = Document(
        id=str(uuid.uuid4()),
        vault_id="vault_001",
        path="07_PEOPLE/vshadrin/1-1/2025-01-08.md",
        doc_id="2025-01-08",
        title="1-1 Шадрин 08.01.2025",
        doc_type="1-1",
        content_hash=hashlib.md5(b"...content...").hexdigest(),
        content="# 1-1 с Шадриным\n\n## Повестка\n...",
        file_modified_at=datetime.now()
    )
    
    frontmatter = {
        "type": "1-1",
        "participant": "[[07_PEOPLE/vshadrin/vshadrin|Шадрин]]",
        "date": "2025-01-08",
        "status": "active",
        "tags": ["meeting", "q1-planning"],
        "priority": 1
    }
    
    # Upsert
    changed = db.upsert_document(doc, frontmatter)
    print(f"Document changed: {changed}")
    
    # Query by property
    active_docs = db.find_documents_by_property("vault_001", "status", "active")
    print(f"Active documents: {len(active_docs)}")
    
    # Get aggregation
    status_stats = db.get_property_stats("vault_001", "status", "1-1")
    print(f"1-1 by status: {status_stats}")
    
    # Find by participant link
    vshadrin_meetings = db.find_documents_by_property(
        "vault_001", "participant", "vshadrin"
    )
    print(f"Meetings with vshadrin: {len(vshadrin_meetings)}")
    
    db.close()
