"""Tests for MetadataSyncService."""

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository
from obsidian_kb.storage.sqlite.schema import create_schema
from obsidian_kb.storage.unified.sync_service import MetadataSyncService
from obsidian_kb.storage.unified.types import ConsistencyReport, SyncResult


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test_sync.sqlite"


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset SQLiteManager singleton before each test."""
    SQLiteManager.reset_instance()
    yield
    SQLiteManager.reset_instance()


@pytest_asyncio.fixture
async def sqlite_manager(temp_db_path: Path) -> SQLiteManager:
    """Create SQLiteManager with schema."""
    mgr = SQLiteManager(temp_db_path)
    await mgr.initialize()
    await create_schema(mgr)
    yield mgr
    await mgr.close()


@pytest_asyncio.fixture
async def vault_id(sqlite_manager: SQLiteManager) -> int:
    """Create a test vault and return its ID."""
    vault_repo = VaultRepository(sqlite_manager)
    return await vault_repo.create(Vault(name="test-vault", path="/path/to/vault"))


@pytest_asyncio.fixture
async def document_repo(sqlite_manager: SQLiteManager) -> SQLiteDocumentRepository:
    """Create SQLiteDocumentRepository."""
    return SQLiteDocumentRepository(sqlite_manager)


@pytest_asyncio.fixture
async def vault_repo(sqlite_manager: SQLiteManager) -> VaultRepository:
    """Create VaultRepository."""
    return VaultRepository(sqlite_manager)


class TestMetadataSyncServiceInit:
    """Tests for MetadataSyncService initialization."""

    def test_init_with_managers(self, sqlite_manager: SQLiteManager):
        """Test initialization with SQLite manager."""
        service = MetadataSyncService(sqlite_manager=sqlite_manager)
        assert service._sqlite_manager is sqlite_manager

    def test_init_with_repos(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test initialization with repositories."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )
        assert service._document_repo is document_repo
        assert service._vault_repo is vault_repo


class TestMetadataSyncServiceVerifyConsistency:
    """Tests for verify_consistency method."""

    @pytest.mark.asyncio
    async def test_verify_consistency_empty_vault(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test consistency check on empty vault."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        report = await service.verify_consistency("test-vault")

        assert report.vault_name == "test-vault"
        assert report.total_documents == 0
        assert report.is_consistent

    @pytest.mark.asyncio
    async def test_verify_consistency_sqlite_only(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test consistency check with SQLite-only documents."""
        # Create documents in SQLite only
        for i in range(3):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
                chunk_count=1,
            )
            await document_repo.create(doc)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=None,  # No LanceDB
        )

        report = await service.verify_consistency("test-vault")

        assert report.vault_name == "test-vault"
        assert report.sqlite_count == 3
        assert report.lancedb_count == 0
        assert len(report.sqlite_only) == 3
        assert not report.is_consistent

    @pytest.mark.asyncio
    async def test_verify_consistency_with_mock_lancedb(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test consistency with mocked LanceDB."""
        # Create document in SQLite
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="hash123",
            chunk_count=1,
        )
        await document_repo.create(doc)

        # Mock LanceDB manager
        mock_lancedb = MagicMock()
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.to_pylist.return_value = [
            {
                "document_id": "test-vault::note.md",
                "content_hash": "hash123",
                "chunk_count": 1,
            }
        ]
        mock_table.to_arrow.return_value = mock_arrow
        mock_lancedb._ensure_table = AsyncMock(return_value=mock_table)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=mock_lancedb,
        )

        report = await service.verify_consistency("test-vault")

        assert report.sqlite_count == 1
        assert report.lancedb_count == 1
        assert report.is_consistent

    @pytest.mark.asyncio
    async def test_verify_consistency_hash_mismatch(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test consistency detects hash mismatches."""
        # Create document in SQLite with one hash
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="sqlite_hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        # Mock LanceDB with different hash
        mock_lancedb = MagicMock()
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.to_pylist.return_value = [
            {
                "document_id": "test-vault::note.md",
                "content_hash": "lancedb_hash",  # Different hash
                "chunk_count": 1,
            }
        ]
        mock_table.to_arrow.return_value = mock_arrow
        mock_lancedb._ensure_table = AsyncMock(return_value=mock_table)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=mock_lancedb,
        )

        report = await service.verify_consistency("test-vault")

        assert not report.is_consistent
        assert len(report.hash_mismatches) == 1
        assert "test-vault::note.md" in report.hash_mismatches


class TestMetadataSyncServiceSyncVault:
    """Tests for sync_vault method."""

    @pytest.mark.asyncio
    async def test_sync_vault_no_lancedb(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sync_vault fails gracefully without LanceDB."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=None,
        )

        result = await service.sync_vault("test-vault")

        assert not result.success
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_sync_vault_invalid_direction(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sync_vault with invalid direction."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        result = await service.sync_vault("test-vault", direction="invalid")

        assert not result.success
        assert "Unknown sync direction" in result.errors[0]

    @pytest.mark.asyncio
    async def test_sync_vault_sqlite_to_lancedb_not_supported(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sqlite_to_lancedb direction is not supported."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        result = await service.sync_vault("test-vault", direction="sqlite_to_lancedb")

        assert not result.success
        assert "not implemented" in result.errors[0].lower()

    @pytest.mark.asyncio
    async def test_sync_vault_creates_new_documents(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sync_vault creates new documents from LanceDB."""
        # Mock LanceDB with documents
        mock_lancedb = MagicMock()
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.to_pylist.return_value = [
            {
                "document_id": "test-vault::new1.md",
                "file_path": "new1.md",
                "file_name": "new1.md",
                "title": "New Note 1",
                "content_hash": "hash1",
                "file_size": 100,
                "chunk_count": 2,
            },
            {
                "document_id": "test-vault::new2.md",
                "file_path": "new2.md",
                "file_name": "new2.md",
                "title": "New Note 2",
                "content_hash": "hash2",
                "file_size": 200,
                "chunk_count": 3,
            },
        ]
        mock_table.to_arrow.return_value = mock_arrow
        mock_lancedb._ensure_table = AsyncMock(return_value=mock_table)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=mock_lancedb,
        )

        result = await service.sync_vault("test-vault")

        assert result.success
        assert result.documents_created == 2
        assert result.documents_synced == 2
        assert result.duration_ms > 0

        # Verify documents were created in SQLite
        docs = await document_repo.find_by_vault_name("test-vault")
        assert len(docs) == 2


class TestMetadataSyncServiceSyncDocument:
    """Tests for sync_document method."""

    @pytest.mark.asyncio
    async def test_sync_document_no_lancedb(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sync_document fails gracefully without LanceDB."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=None,
        )

        result = await service.sync_document("test-vault::note.md")

        assert not result.success

    @pytest.mark.asyncio
    async def test_sync_document_invalid_direction(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sync_document with unsupported direction."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        result = await service.sync_document(
            "test-vault::note.md",
            direction="sqlite_to_lancedb",
        )

        assert not result.success

    @pytest.mark.asyncio
    async def test_sync_document_creates_new(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test sync_document creates a new document."""
        # Mock LanceDB
        mock_lancedb = MagicMock()
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.num_rows = 1
        mock_arrow.to_pylist.return_value = [
            {
                "document_id": "test-vault::new.md",
                "file_path": "new.md",
                "file_name": "new.md",
                "title": "New Note",
                "content_hash": "hash123",
                "file_size": 100,
                "chunk_count": 1,
            }
        ]
        mock_search = MagicMock()
        mock_search.where.return_value = mock_search
        mock_search.limit.return_value = mock_search
        mock_search.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_search
        mock_lancedb._ensure_table = AsyncMock(return_value=mock_table)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=mock_lancedb,
        )

        result = await service.sync_document("test-vault::new.md")

        assert result.success
        assert result.documents_created == 1
        assert result.documents_synced == 1

    @pytest.mark.asyncio
    async def test_sync_document_updates_existing(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test sync_document updates an existing document."""
        # Create existing document in SQLite
        doc = SQLiteDocument(
            document_id="test-vault::existing.md",
            vault_id=vault_id,
            file_path="existing.md",
            file_name="existing.md",
            content_hash="old_hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        # Mock LanceDB with updated data
        mock_lancedb = MagicMock()
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.num_rows = 1
        mock_arrow.to_pylist.return_value = [
            {
                "document_id": "test-vault::existing.md",
                "file_path": "existing.md",
                "file_name": "existing.md",
                "title": "Updated Note",
                "content_hash": "new_hash",
                "file_size": 200,
                "chunk_count": 3,
            }
        ]
        mock_search = MagicMock()
        mock_search.where.return_value = mock_search
        mock_search.limit.return_value = mock_search
        mock_search.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_search
        mock_lancedb._ensure_table = AsyncMock(return_value=mock_table)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=mock_lancedb,
        )

        result = await service.sync_document("test-vault::existing.md")

        assert result.success
        assert result.documents_updated == 1


class TestMetadataSyncServiceRepairInconsistencies:
    """Tests for repair_inconsistencies method."""

    @pytest.mark.asyncio
    async def test_repair_already_consistent(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test repair does nothing for consistent state."""
        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        # Create a consistent report
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=10,
            sqlite_count=10,
            lancedb_count=10,
        )

        result = await service.repair_inconsistencies("test-vault", report)

        assert result.success
        assert result.documents_synced == 0
        assert result.documents_deleted == 0

    @pytest.mark.asyncio
    async def test_repair_deletes_sqlite_only(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test repair deletes documents that only exist in SQLite."""
        # Create document in SQLite only
        doc = SQLiteDocument(
            document_id="test-vault::orphan.md",
            vault_id=vault_id,
            file_path="orphan.md",
            file_name="orphan.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
            lancedb_manager=None,
        )

        # Create report with sqlite_only documents
        report = ConsistencyReport(
            vault_name="test-vault",
            total_documents=1,
            sqlite_count=1,
            lancedb_count=0,
            sqlite_only=["test-vault::orphan.md"],
        )

        result = await service.repair_inconsistencies("test-vault", report)

        assert result.documents_deleted == 1

        # Verify document was deleted
        exists = await document_repo.exists_by_document_id("test-vault::orphan.md")
        assert not exists


class TestSyncResultDataclass:
    """Tests for SyncResult."""

    def test_default_values(self):
        """Test default values."""
        result = SyncResult(vault_name="test")
        assert result.documents_synced == 0
        assert result.success
        assert result.errors == []

    def test_success_with_errors(self):
        """Test that errors set success to False."""
        result = SyncResult(
            vault_name="test",
            errors=["error 1"],
        )
        assert not result.success


class TestConsistencyReportDataclass:
    """Tests for ConsistencyReport."""

    def test_is_consistent_true(self):
        """Test is_consistent is True when no issues."""
        report = ConsistencyReport(
            vault_name="test",
            total_documents=10,
            sqlite_count=10,
            lancedb_count=10,
        )
        assert report.is_consistent

    def test_is_consistent_false_with_sqlite_only(self):
        """Test is_consistent is False with sqlite_only."""
        report = ConsistencyReport(
            vault_name="test",
            total_documents=11,
            sqlite_only=["doc1"],
        )
        assert not report.is_consistent

    def test_inconsistency_count(self):
        """Test inconsistency_count calculation."""
        report = ConsistencyReport(
            vault_name="test",
            total_documents=20,
            sqlite_only=["s1", "s2"],
            lancedb_only=["l1", "l2", "l3"],
            hash_mismatches=["h1"],
        )
        assert report.inconsistency_count == 6
