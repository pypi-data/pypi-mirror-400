"""Tests for Unified Metadata Access Layer types."""

from datetime import datetime

import pytest

from obsidian_kb.storage.unified.types import (
    ChunkInfo,
    ConsistencyReport,
    DataSource,
    SyncResult,
    UnifiedDocumentInfo,
)


class TestDataSource:
    """Tests for DataSource enum."""

    def test_data_source_values(self):
        """Test DataSource enum values."""
        assert DataSource.SQLITE.value == "sqlite"
        assert DataSource.LANCEDB.value == "lancedb"
        assert DataSource.MERGED.value == "merged"

    def test_data_source_string_comparison(self):
        """Test DataSource can be compared to strings."""
        assert DataSource.SQLITE == "sqlite"
        assert DataSource.LANCEDB == "lancedb"


class TestUnifiedDocumentInfo:
    """Tests for UnifiedDocumentInfo dataclass."""

    def test_basic_creation(self):
        """Test creating UnifiedDocumentInfo with required fields."""
        doc = UnifiedDocumentInfo(
            document_id="vault::path/to/note.md",
            vault_name="vault",
            file_path="path/to/note.md",
            title="My Note",
            content_hash="abc123",
            chunk_count=3,
        )

        assert doc.document_id == "vault::path/to/note.md"
        assert doc.vault_name == "vault"
        assert doc.file_path == "path/to/note.md"
        assert doc.title == "My Note"
        assert doc.content_hash == "abc123"
        assert doc.chunk_count == 3
        assert doc.source == DataSource.SQLITE  # Default

    def test_full_creation(self):
        """Test creating UnifiedDocumentInfo with all fields."""
        now = datetime.now()
        doc = UnifiedDocumentInfo(
            document_id="vault::note.md",
            vault_name="vault",
            file_path="note.md",
            title="Note",
            content_hash="hash123",
            chunk_count=5,
            metadata={"type": "1-1", "status": "active"},
            created_at=now,
            modified_at=now,
            source=DataSource.LANCEDB,
        )

        assert doc.metadata == {"type": "1-1", "status": "active"}
        assert doc.created_at == now
        assert doc.modified_at == now
        assert doc.source == DataSource.LANCEDB

    def test_file_name_property(self):
        """Test file_name property extraction."""
        doc1 = UnifiedDocumentInfo(
            document_id="vault::path/to/note.md",
            vault_name="vault",
            file_path="path/to/note.md",
            title="Note",
            content_hash="hash",
            chunk_count=1,
        )
        assert doc1.file_name == "note.md"

        doc2 = UnifiedDocumentInfo(
            document_id="vault::note.md",
            vault_name="vault",
            file_path="note.md",
            title="Note",
            content_hash="hash",
            chunk_count=1,
        )
        assert doc2.file_name == "note.md"

    def test_default_metadata_is_empty_dict(self):
        """Test that default metadata is empty dict."""
        doc = UnifiedDocumentInfo(
            document_id="vault::note.md",
            vault_name="vault",
            file_path="note.md",
            title="Note",
            content_hash="hash",
            chunk_count=1,
        )
        assert doc.metadata == {}
        assert isinstance(doc.metadata, dict)


class TestChunkInfo:
    """Tests for ChunkInfo dataclass."""

    def test_basic_creation(self):
        """Test creating ChunkInfo with required fields."""
        chunk = ChunkInfo(
            chunk_id="vault::note.md::0",
            document_id="vault::note.md",
            chunk_index=0,
            section="Introduction",
            content="This is the introduction.",
        )

        assert chunk.chunk_id == "vault::note.md::0"
        assert chunk.document_id == "vault::note.md"
        assert chunk.chunk_index == 0
        assert chunk.section == "Introduction"
        assert chunk.content == "This is the introduction."
        assert chunk.source == DataSource.LANCEDB  # Default

    def test_with_tags_and_links(self):
        """Test ChunkInfo with tags and links."""
        chunk = ChunkInfo(
            chunk_id="vault::note.md::1",
            document_id="vault::note.md",
            chunk_index=1,
            section="Body",
            content="Content with #tag and [[link]]",
            inline_tags=["tag"],
            links=["link"],
        )

        assert chunk.inline_tags == ["tag"]
        assert chunk.links == ["link"]


class TestConsistencyReport:
    """Tests for ConsistencyReport dataclass."""

    def test_consistent_report(self):
        """Test creating a consistent report."""
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=100,
            sqlite_count=100,
            lancedb_count=100,
        )

        assert report.vault_name == "test-vault"
        assert report.total_documents == 100
        assert report.is_consistent
        assert report.inconsistency_count == 0

    def test_inconsistent_sqlite_only(self):
        """Test report with SQLite-only documents."""
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=105,
            sqlite_count=105,
            lancedb_count=100,
            sqlite_only=["doc1", "doc2", "doc3", "doc4", "doc5"],
        )

        assert not report.is_consistent
        assert report.inconsistency_count == 5

    def test_inconsistent_lancedb_only(self):
        """Test report with LanceDB-only documents."""
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=103,
            sqlite_count=100,
            lancedb_count=103,
            lancedb_only=["doc1", "doc2", "doc3"],
        )

        assert not report.is_consistent
        assert report.inconsistency_count == 3

    def test_inconsistent_hash_mismatches(self):
        """Test report with hash mismatches."""
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=100,
            sqlite_count=100,
            lancedb_count=100,
            hash_mismatches=["doc1", "doc2"],
        )

        assert not report.is_consistent
        assert report.inconsistency_count == 2

    def test_multiple_inconsistencies(self):
        """Test report with multiple types of inconsistencies."""
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=110,
            sqlite_count=102,
            lancedb_count=105,
            sqlite_only=["s1", "s2"],
            lancedb_only=["l1", "l2", "l3", "l4", "l5"],
            hash_mismatches=["h1", "h2", "h3"],
        )

        assert not report.is_consistent
        assert report.inconsistency_count == 10  # 2 + 5 + 3

    def test_checked_at_default(self):
        """Test checked_at has default value."""
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=100,
        )

        assert report.checked_at is not None
        assert isinstance(report.checked_at, datetime)


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_successful_sync(self):
        """Test successful sync result."""
        result = SyncResult(
            vault_name="test-vault",
            documents_synced=50,
            documents_created=10,
            documents_updated=35,
            documents_deleted=5,
            duration_ms=150.5,
        )

        assert result.vault_name == "test-vault"
        assert result.documents_synced == 50
        assert result.success
        assert result.duration_ms == 150.5

    def test_failed_sync(self):
        """Test failed sync result."""
        result = SyncResult(
            vault_name="test-vault",
            documents_synced=10,
            errors=["Error 1", "Error 2"],
        )

        assert not result.success
        assert len(result.errors) == 2

    def test_default_values(self):
        """Test default values."""
        result = SyncResult(vault_name="test-vault")

        assert result.documents_synced == 0
        assert result.documents_created == 0
        assert result.documents_updated == 0
        assert result.documents_deleted == 0
        assert result.errors == []
        assert result.success
        assert result.duration_ms == 0.0
