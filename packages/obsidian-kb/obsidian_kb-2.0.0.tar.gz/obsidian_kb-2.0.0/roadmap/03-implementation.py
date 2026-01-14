"""
obsidian-kb Database Layer v2.1
With DOCUMENT_PROPERTIES for frontmatter key-value storage
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Literal
from datetime import datetime, date
import hashlib
import json
import sqlite3
import re
import uuid

import lancedb
import pyarrow as pa
import numpy as np


# ============================================================
# Value Types
# ============================================================

ValueType = Literal["string", "number", "date", "list", "link"]


@dataclass
class PropertyValue:
    """Typed property value from frontmatter."""
    key: str
    value_type: ValueType
    value_string: Optional[str] = None
    value_number: Optional[float] = None
    value_date: Optional[date] = None
    value_list: Optional[list] = None
    value_link_target: Optional[str] = None  # doc_id of linked document
    
    @classmethod
    def from_raw(cls, key: str, value: Any) -> "PropertyValue":
        """Parse raw frontmatter value into typed PropertyValue."""
        if isinstance(value, bool):
            return cls(key=key, value_type="string", 
                      value_string="true" if value else "false")
        
        if isinstance(value, (int, float)):
            return cls(key=key, value_type="number", value_number=float(value))
        
        if isinstance(value, list):
            return cls(key=key, value_type="list", value_list=value)
        
        if isinstance(value, str):
            # Check for wikilink: [[doc_id]] or [[doc_id|alias]]
            link_match = re.match(r'^\[\[([^\]|]+)(?:\|[^\]]+)?\]\]$', value)
            if link_match:
                return cls(key=key, value_type="link", 
                          value_link_target=link_match.group(1))
            
            # Check for date: YYYY-MM-DD
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return cls(key=key, value_type="date", 
                          value_date=date.fromisoformat(value))
            
            return cls(key=key, value_type="string", value_string=value)
        
        # Fallback
        return cls(key=key, value_type="string", value_string=str(value))
    
    def to_text_search(self) -> Optional[str]:
        """Get normalized text for FTS."""
        if self.value_string:
            return self.value_string.lower()
        if self.value_list:
            return " ".join(str(v).lower() for v in self.value_list)
        return None


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


@dataclass
class Document:
    id: str
    vault_id: str
    path: str
    doc_id: Optional[str]
    title: Optional[str]
    type: Optional[str]
    content_hash: str
    frontmatter_raw: dict
    content: str
    file_modified_at: datetime
    indexed_at: datetime = field(default_factory=datetime.now)


@dataclass
class DocumentProperty:
    id: str
    document_id: str
    property_key: str
    value: PropertyValue
    
    @classmethod
    def from_frontmatter(cls, document_id: str, 
                         frontmatter: dict) -> list["DocumentProperty"]:
        """Extract properties from frontmatter dict."""
        # Skip special fields that are stored elsewhere
        skip_keys = {'id', 'title', 'type', 'tags', 'aliases'}
        
        properties = []
        for key, value in frontmatter.items():
            if key in skip_keys:
                continue
            if value is None:
                continue
                
            prop_value = PropertyValue.from_raw(key, value)
            properties.append(cls(
                id=f"prop_{uuid.uuid4().hex[:12]}",
                document_id=document_id,
                property_key=key,
                value=prop_value
            ))
        
        return properties


@dataclass
class PropertySchema:
    """Discovered schema for a property in vault."""
    id: str
    vault_id: str
    property_key: str
    value_type: ValueType
    allowed_values: Optional[list] = None
    usage_count: int = 0
    sample_values: Optional[list] = None
    is_indexed: bool = False


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
    doc_type: Optional[str]
    doc_id: Optional[str]
    tags: list[str]


@dataclass
class Link:
    id: str
    source_doc_id: str
    target_doc_id: Optional[str]
    target_raw: str
    link_type: str
    anchor_text: Optional[str]
    position: int


# ============================================================
# Database Manager
# ============================================================

class ObsidianKBDatabase:
    """Hybrid storage: LanceDB for vectors, SQLite for metadata."""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.lance_db = lancedb.connect(self.data_dir / "vectors.lance")
        self.sqlite_conn = sqlite3.connect(
            self.data_dir / "metadata.db",
            check_same_thread=False
        )
        self.sqlite_conn.row_factory = sqlite3.Row
        
        self._init_sqlite_schema()
        self._init_lance_schema()
    
    def _init_sqlite_schema(self):
        """Create SQLite tables."""
        self.sqlite_conn.executescript("""
            -- Vaults
            CREATE TABLE IF NOT EXISTS vaults (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                path TEXT NOT NULL,
                config JSON DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_indexed_at TIMESTAMP
            );
            
            -- Documents
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id),
                path TEXT NOT NULL,
                doc_id TEXT,
                title TEXT,
                type TEXT,
                content_hash TEXT NOT NULL,
                frontmatter_raw JSON,
                file_modified_at TIMESTAMP,
                indexed_at TIMESTAMP,
                UNIQUE(vault_id, path)
            );
            
            CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(vault_id, type);
            CREATE INDEX IF NOT EXISTS idx_doc_id ON documents(vault_id, doc_id);
            CREATE INDEX IF NOT EXISTS idx_doc_hash ON documents(content_hash);
            
            -- Document Properties (EAV)
            CREATE TABLE IF NOT EXISTS document_properties (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                property_key TEXT NOT NULL,
                value_type TEXT NOT NULL,
                value_string TEXT,
                value_number REAL,
                value_date DATE,
                value_list JSON,
                value_link_target TEXT,
                value_text_search TEXT,
                UNIQUE(document_id, property_key)
            );
            
            CREATE INDEX IF NOT EXISTS idx_props_key 
                ON document_properties(property_key);
            CREATE INDEX IF NOT EXISTS idx_props_key_string 
                ON document_properties(property_key, value_string);
            CREATE INDEX IF NOT EXISTS idx_props_key_number 
                ON document_properties(property_key, value_number);
            CREATE INDEX IF NOT EXISTS idx_props_key_date 
                ON document_properties(property_key, value_date);
            CREATE INDEX IF NOT EXISTS idx_props_link 
                ON document_properties(value_link_target);
            CREATE INDEX IF NOT EXISTS idx_props_doc_key 
                ON document_properties(document_id, property_key);
            
            -- Property Schema (discovered)
            CREATE TABLE IF NOT EXISTS property_schema (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id),
                property_key TEXT NOT NULL,
                value_type TEXT NOT NULL,
                allowed_values JSON,
                usage_count INT DEFAULT 0,
                sample_values JSON,
                is_indexed BOOLEAN DEFAULT FALSE,
                UNIQUE(vault_id, property_key)
            );
            
            -- Tags
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL REFERENCES vaults(id),
                name TEXT NOT NULL,
                normalized TEXT NOT NULL,
                doc_count INT DEFAULT 0,
                UNIQUE(vault_id, normalized)
            );
            
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
                tag_id TEXT REFERENCES tags(id),
                source TEXT DEFAULT 'frontmatter',
                PRIMARY KEY(document_id, tag_id)
            );
            
            -- Links (graph)
            CREATE TABLE IF NOT EXISTS links (
                id TEXT PRIMARY KEY,
                source_doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                target_doc_id TEXT REFERENCES documents(id),
                target_raw TEXT,
                link_type TEXT NOT NULL,
                anchor_text TEXT,
                position INT
            );
            
            CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_doc_id);
            CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_doc_id);
            
            -- Embedding Cache
            CREATE TABLE IF NOT EXISTS embedding_cache (
                content_hash TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                embedding BLOB NOT NULL,
                token_count INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.sqlite_conn.commit()
    
    def _init_lance_schema(self):
        """Create LanceDB table for chunks."""
        if "chunks" not in self.lance_db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("document_id", pa.string()),
                pa.field("vault_id", pa.string()),
                pa.field("chunk_index", pa.int32()),
                pa.field("content", pa.string()),
                pa.field("context", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), 1024)),
                pa.field("start_offset", pa.int32()),
                pa.field("end_offset", pa.int32()),
                pa.field("doc_type", pa.string()),
                pa.field("doc_id", pa.string()),
                pa.field("tags", pa.list_(pa.string())),
            ])
            self.lance_db.create_table("chunks", schema=schema)
    
    # --------------------------------------------------------
    # Document Operations
    # --------------------------------------------------------
    
    def upsert_document(self, doc: Document) -> bool:
        """Insert or update document. Returns True if changed."""
        cursor = self.sqlite_conn.cursor()
        
        existing = cursor.execute(
            "SELECT id, content_hash FROM documents WHERE vault_id=? AND path=?",
            (doc.vault_id, doc.path)
        ).fetchone()
        
        if existing and existing["content_hash"] == doc.content_hash:
            return False
        
        # Upsert document
        cursor.execute("""
            INSERT INTO documents 
                (id, vault_id, path, doc_id, title, type, 
                 content_hash, frontmatter_raw, file_modified_at, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(vault_id, path) DO UPDATE SET
                doc_id = excluded.doc_id,
                title = excluded.title,
                type = excluded.type,
                content_hash = excluded.content_hash,
                frontmatter_raw = excluded.frontmatter_raw,
                file_modified_at = excluded.file_modified_at,
                indexed_at = excluded.indexed_at
        """, (
            doc.id, doc.vault_id, doc.path, doc.doc_id, doc.title,
            doc.type, doc.content_hash, json.dumps(doc.frontmatter_raw),
            doc.file_modified_at.isoformat(), doc.indexed_at.isoformat()
        ))
        
        # Get actual document ID (might be existing)
        actual_doc_id = existing["id"] if existing else doc.id
        
        # Delete old properties
        cursor.execute(
            "DELETE FROM document_properties WHERE document_id = ?",
            (actual_doc_id,)
        )
        
        # Insert new properties
        properties = DocumentProperty.from_frontmatter(
            actual_doc_id, doc.frontmatter_raw
        )
        for prop in properties:
            self._insert_property(cursor, prop)
        
        self.sqlite_conn.commit()
        return True
    
    def _insert_property(self, cursor, prop: DocumentProperty):
        """Insert a single property."""
        v = prop.value
        cursor.execute("""
            INSERT INTO document_properties 
                (id, document_id, property_key, value_type,
                 value_string, value_number, value_date, 
                 value_list, value_link_target, value_text_search)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prop.id, prop.document_id, prop.property_key, v.value_type,
            v.value_string, v.value_number,
            v.value_date.isoformat() if v.value_date else None,
            json.dumps(v.value_list) if v.value_list else None,
            v.value_link_target, v.to_text_search()
        ))
    
    # --------------------------------------------------------
    # Property Queries
    # --------------------------------------------------------
    
    def find_by_property(self, vault_id: str, key: str, 
                         value: Any = None, 
                         operator: str = "=") -> list[dict]:
        """Find documents by property value.
        
        Args:
            vault_id: Vault to search in
            key: Property key (e.g., "status", "priority")
            value: Value to match (None = any value)
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE)
        """
        cursor = self.sqlite_conn.cursor()
        
        if value is None:
            # Find all documents with this property
            return [dict(row) for row in cursor.execute("""
                SELECT d.* FROM documents d
                JOIN document_properties p ON d.id = p.document_id
                WHERE d.vault_id = ? AND p.property_key = ?
            """, (vault_id, key))]
        
        # Determine value column based on type
        if isinstance(value, (int, float)):
            value_col = "value_number"
        elif isinstance(value, date):
            value_col = "value_date"
            value = value.isoformat()
        else:
            value_col = "value_string"
        
        query = f"""
            SELECT d.* FROM documents d
            JOIN document_properties p ON d.id = p.document_id
            WHERE d.vault_id = ? 
              AND p.property_key = ?
              AND p.{value_col} {operator} ?
        """
        
        return [dict(row) for row in cursor.execute(query, (vault_id, key, value))]
    
    def find_by_link_property(self, vault_id: str, key: str, 
                              target_doc_id: str) -> list[dict]:
        """Find documents where property links to target."""
        cursor = self.sqlite_conn.cursor()
        return [dict(row) for row in cursor.execute("""
            SELECT d.* FROM documents d
            JOIN document_properties p ON d.id = p.document_id
            WHERE d.vault_id = ?
              AND p.property_key = ?
              AND p.value_link_target = ?
        """, (vault_id, key, target_doc_id))]
    
    def aggregate_by_property(self, vault_id: str, key: str, 
                              doc_type: Optional[str] = None) -> list[dict]:
        """Get counts grouped by property value."""
        cursor = self.sqlite_conn.cursor()
        
        if doc_type:
            return [dict(row) for row in cursor.execute("""
                SELECT p.value_string as value, COUNT(*) as count
                FROM document_properties p
                JOIN documents d ON p.document_id = d.id
                WHERE d.vault_id = ? AND d.type = ? AND p.property_key = ?
                GROUP BY p.value_string
                ORDER BY count DESC
            """, (vault_id, doc_type, key))]
        
        return [dict(row) for row in cursor.execute("""
            SELECT p.value_string as value, COUNT(*) as count
            FROM document_properties p
            JOIN documents d ON p.document_id = d.id
            WHERE d.vault_id = ? AND p.property_key = ?
            GROUP BY p.value_string
            ORDER BY count DESC
        """, (vault_id, key))]
    
    def get_document_properties(self, document_id: str) -> dict[str, Any]:
        """Get all properties for a document as dict."""
        cursor = self.sqlite_conn.cursor()
        
        result = {}
        for row in cursor.execute("""
            SELECT property_key, value_type, value_string, value_number,
                   value_date, value_list, value_link_target
            FROM document_properties
            WHERE document_id = ?
        """, (document_id,)):
            key = row["property_key"]
            vtype = row["value_type"]
            
            if vtype == "string":
                result[key] = row["value_string"]
            elif vtype == "number":
                result[key] = row["value_number"]
            elif vtype == "date":
                result[key] = row["value_date"]
            elif vtype == "list":
                result[key] = json.loads(row["value_list"])
            elif vtype == "link":
                result[key] = f"[[{row['value_link_target']}]]"
        
        return result
    
    # --------------------------------------------------------
    # Schema Discovery
    # --------------------------------------------------------
    
    def discover_schema(self, vault_id: str) -> list[PropertySchema]:
        """Discover property schema from indexed documents."""
        cursor = self.sqlite_conn.cursor()
        
        schemas = []
        for row in cursor.execute("""
            SELECT 
                p.property_key,
                p.value_type,
                COUNT(DISTINCT p.document_id) as usage_count,
                GROUP_CONCAT(DISTINCT p.value_string) as samples
            FROM document_properties p
            JOIN documents d ON p.document_id = d.id
            WHERE d.vault_id = ?
            GROUP BY p.property_key, p.value_type
            ORDER BY usage_count DESC
        """, (vault_id,)):
            samples = row["samples"].split(",")[:10] if row["samples"] else []
            
            schema = PropertySchema(
                id=f"schema_{uuid.uuid4().hex[:8]}",
                vault_id=vault_id,
                property_key=row["property_key"],
                value_type=row["value_type"],
                usage_count=row["usage_count"],
                sample_values=samples
            )
            schemas.append(schema)
            
            # Upsert to property_schema table
            cursor.execute("""
                INSERT INTO property_schema 
                    (id, vault_id, property_key, value_type, usage_count, sample_values)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(vault_id, property_key) DO UPDATE SET
                    usage_count = excluded.usage_count,
                    sample_values = excluded.sample_values
            """, (
                schema.id, vault_id, schema.property_key, 
                schema.value_type, schema.usage_count,
                json.dumps(samples)
            ))
        
        self.sqlite_conn.commit()
        return schemas
    
    def get_schema(self, vault_id: str) -> list[dict]:
        """Get cached schema for vault."""
        cursor = self.sqlite_conn.cursor()
        return [dict(row) for row in cursor.execute("""
            SELECT * FROM property_schema
            WHERE vault_id = ?
            ORDER BY usage_count DESC
        """, (vault_id,))]


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    db = ObsidianKBDatabase("/Users/mdemyanov/.obsidian-kb/data")
    
    # Create test document
    doc = Document(
        id="doc_001",
        vault_id="vault_001",
        path="07_PEOPLE/vshadrin/vshadrin.md",
        doc_id="vshadrin",
        title="Всеволод Шадрин",
        type="person",
        content_hash=hashlib.md5(b"test").hexdigest(),
        frontmatter_raw={
            "type": "person",
            "title": "Всеволод Шадрин",
            "role": "Lead Developer",
            "team": "Platform",
            "manager": "[[amuratov]]",
            "joined": "2020-03-15",
            "skills": ["Python", "SQL", "Architecture"],
            "level": 3,
        },
        content="# Всеволод Шадрин\n...",
        file_modified_at=datetime.now()
    )
    
    changed = db.upsert_document(doc)
    print(f"Document changed: {changed}")
    
    # Query by property
    leads = db.find_by_property("vault_001", "role", "Lead Developer")
    print(f"Lead Developers: {len(leads)}")
    
    # Query by link property
    amuratov_reports = db.find_by_link_property("vault_001", "manager", "amuratov")
    print(f"Reports to amuratov: {len(amuratov_reports)}")
    
    # Aggregate
    roles = db.aggregate_by_property("vault_001", "role", doc_type="person")
    print(f"Roles: {roles}")
    
    # Discover schema
    schema = db.discover_schema("vault_001")
    print(f"Schema: {[s.property_key for s in schema]}")
