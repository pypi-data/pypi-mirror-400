"""Data types for the Unified Metadata Access Layer.

This module defines data classes for unified access to document metadata
across SQLite and LanceDB storage backends.

Phase 2.0.5 - Unified Metadata Access Layer
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DataSource(str, Enum):
    """Source of the metadata."""

    SQLITE = "sqlite"
    LANCEDB = "lancedb"
    MERGED = "merged"  # Data merged from both sources


@dataclass
class UnifiedDocumentInfo:
    """Unified document metadata from SQLite or LanceDB.

    Provides a single interface for document metadata regardless of
    the underlying storage backend.

    Attributes:
        document_id: Unique document ID (vault_name::file_path)
        vault_name: Name of the vault
        file_path: Relative path within vault
        title: Document title from frontmatter or H1
        content_hash: SHA256 hash of file content
        chunk_count: Number of chunks in the document
        metadata: Additional document metadata (frontmatter properties)
        created_at: File creation timestamp
        modified_at: File modification timestamp
        source: Data source (sqlite, lancedb, or merged)
    """

    document_id: str
    vault_name: str
    file_path: str
    title: str
    content_hash: str
    chunk_count: int
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    modified_at: datetime | None = None
    source: DataSource = DataSource.SQLITE

    @property
    def file_name(self) -> str:
        """Extract file name from path."""
        return self.file_path.rsplit("/", 1)[-1] if "/" in self.file_path else self.file_path


@dataclass
class ChunkInfo:
    """Information about a document chunk.

    Attributes:
        chunk_id: Unique chunk ID (vault_name::file_path::chunk_index)
        document_id: Parent document ID
        chunk_index: Index within the document
        section: Section title/header
        content: Chunk text content
        inline_tags: Tags found in the chunk
        links: Wiki links found in the chunk
        source: Data source
    """

    chunk_id: str
    document_id: str
    chunk_index: int
    section: str
    content: str
    inline_tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    source: DataSource = DataSource.LANCEDB


@dataclass
class ConsistencyReport:
    """Report on metadata consistency between SQLite and LanceDB.

    Attributes:
        vault_name: Name of the vault
        total_documents: Total unique documents across both sources
        sqlite_count: Documents in SQLite
        lancedb_count: Documents in LanceDB
        sqlite_only: Document IDs only in SQLite
        lancedb_only: Document IDs only in LanceDB
        hash_mismatches: Document IDs with different content hashes
        is_consistent: True if all data is consistent
        checked_at: Timestamp of the consistency check
    """

    vault_name: str
    total_documents: int
    sqlite_count: int = 0
    lancedb_count: int = 0
    sqlite_only: list[str] = field(default_factory=list)
    lancedb_only: list[str] = field(default_factory=list)
    hash_mismatches: list[str] = field(default_factory=list)
    is_consistent: bool = True
    checked_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Calculate is_consistent based on lists."""
        self.is_consistent = (
            len(self.sqlite_only) == 0
            and len(self.lancedb_only) == 0
            and len(self.hash_mismatches) == 0
        )

    @property
    def inconsistency_count(self) -> int:
        """Total number of inconsistencies."""
        return len(self.sqlite_only) + len(self.lancedb_only) + len(self.hash_mismatches)


@dataclass
class SyncResult:
    """Result of a synchronization operation.

    Attributes:
        vault_name: Name of the vault
        documents_synced: Number of documents synchronized
        documents_created: Number of new documents created
        documents_updated: Number of existing documents updated
        documents_deleted: Number of documents deleted
        errors: List of error messages
        success: True if sync completed without errors
        duration_ms: Duration of sync in milliseconds
    """

    vault_name: str
    documents_synced: int = 0
    documents_created: int = 0
    documents_updated: int = 0
    documents_deleted: int = 0
    errors: list[str] = field(default_factory=list)
    success: bool = True
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        """Calculate success based on errors."""
        self.success = len(self.errors) == 0
