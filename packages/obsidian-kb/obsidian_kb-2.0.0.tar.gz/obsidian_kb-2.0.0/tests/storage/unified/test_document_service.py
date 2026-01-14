"""Tests for UnifiedDocumentService."""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository
from obsidian_kb.storage.sqlite.schema import create_schema
from obsidian_kb.storage.unified.document_service import UnifiedDocumentService
from obsidian_kb.storage.unified.metadata_accessor import UnifiedMetadataAccessor
from obsidian_kb.storage.unified.types import DataSource, UnifiedDocumentInfo


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test_doc_service.sqlite"


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


@pytest_asyncio.fixture
async def service(
    sqlite_manager: SQLiteManager,
    document_repo: SQLiteDocumentRepository,
    vault_repo: VaultRepository,
) -> UnifiedDocumentService:
    """Create UnifiedDocumentService."""
    accessor = UnifiedMetadataAccessor(
        sqlite_manager=sqlite_manager,
        document_repo=document_repo,
        vault_repo=vault_repo,
    )
    return UnifiedDocumentService(
        sqlite_manager=sqlite_manager,
        accessor=accessor,
    )


class TestUnifiedDocumentServiceInit:
    """Tests for UnifiedDocumentService initialization."""

    def test_init_with_managers(self, sqlite_manager: SQLiteManager):
        """Test initialization with managers."""
        service = UnifiedDocumentService(sqlite_manager=sqlite_manager)
        assert service._sqlite_manager is sqlite_manager
        assert service._accessor is not None

    def test_init_with_accessor(self, sqlite_manager: SQLiteManager):
        """Test initialization with existing accessor."""
        accessor = UnifiedMetadataAccessor(sqlite_manager=sqlite_manager)
        service = UnifiedDocumentService(
            sqlite_manager=sqlite_manager,
            accessor=accessor,
        )
        assert service._accessor is accessor

    def test_init_with_vault_paths(self, sqlite_manager: SQLiteManager, tmp_path: Path):
        """Test initialization with vault paths."""
        vault_paths = {"test-vault": tmp_path / "vault"}
        service = UnifiedDocumentService(
            sqlite_manager=sqlite_manager,
            vault_paths=vault_paths,
        )
        assert service._vault_paths == vault_paths


class TestUnifiedDocumentServiceGetDocument:
    """Tests for get_document method."""

    @pytest.mark.asyncio
    async def test_get_document(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting a document."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            title="Test Note",
            content_hash="hash123",
            chunk_count=2,
        )
        await document_repo.create(doc)

        result = await service.get_document("test-vault::note.md")

        assert result is not None
        assert result.document_id == "test-vault::note.md"
        assert result.title == "Test Note"

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, service: UnifiedDocumentService):
        """Test getting non-existent document."""
        result = await service.get_document("test-vault::nonexistent.md")
        assert result is None


class TestUnifiedDocumentServiceGetDocumentsByVault:
    """Tests for get_documents_by_vault method."""

    @pytest.mark.asyncio
    async def test_get_documents_by_vault(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting all documents in a vault."""
        for i in range(5):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
                chunk_count=1,
            )
            await document_repo.create(doc)

        results = await service.get_documents_by_vault("test-vault")

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_get_documents_by_vault_with_limit(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting documents with limit."""
        for i in range(10):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
                chunk_count=1,
            )
            await document_repo.create(doc)

        results = await service.get_documents_by_vault("test-vault", limit=5)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_get_documents_by_vault_no_metadata(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting documents without metadata."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        results = await service.get_documents_by_vault("test-vault", include_metadata=False)

        assert len(results) == 1
        assert results[0].metadata == {}


class TestUnifiedDocumentServiceSearchByProperty:
    """Tests for search_by_property method."""

    @pytest.mark.asyncio
    async def test_search_by_property(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
        sqlite_manager: SQLiteManager,
    ):
        """Test searching by property."""
        # Create documents
        doc1 = SQLiteDocument(
            document_id="test-vault::active.md",
            vault_id=vault_id,
            file_path="active.md",
            file_name="active.md",
            content_hash="hash1",
            chunk_count=1,
        )
        doc1_id = await document_repo.create(doc1)

        doc2 = SQLiteDocument(
            document_id="test-vault::inactive.md",
            vault_id=vault_id,
            file_path="inactive.md",
            file_name="inactive.md",
            content_hash="hash2",
            chunk_count=1,
        )
        await document_repo.create(doc2)

        # Add property to doc1
        await sqlite_manager.execute(
            """
            INSERT INTO document_properties
            (document_id, property_key, property_value, value_type)
            VALUES (?, ?, ?, ?)
            """,
            (doc1_id, "status", "active", "string"),
        )

        results = await service.search_by_property("test-vault", "status", "active")

        assert len(results) == 1
        assert results[0].document_id == "test-vault::active.md"

    @pytest.mark.asyncio
    async def test_search_by_properties_match_all(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
        sqlite_manager: SQLiteManager,
    ):
        """Test searching by multiple properties with match_all=True."""
        # Create document with two properties
        doc = SQLiteDocument(
            document_id="test-vault::matched.md",
            vault_id=vault_id,
            file_path="matched.md",
            file_name="matched.md",
            content_hash="hash",
            chunk_count=1,
        )
        doc_id = await document_repo.create(doc)

        # Add properties
        await sqlite_manager.execute(
            """
            INSERT INTO document_properties
            (document_id, property_key, property_value, value_type)
            VALUES (?, ?, ?, ?)
            """,
            (doc_id, "status", "active", "string"),
        )
        await sqlite_manager.execute(
            """
            INSERT INTO document_properties
            (document_id, property_key, property_value, value_type)
            VALUES (?, ?, ?, ?)
            """,
            (doc_id, "type", "1-1", "string"),
        )

        results = await service.search_by_properties(
            "test-vault",
            {"status": "active", "type": "1-1"},
            match_all=True,
        )

        assert len(results) == 1
        assert results[0].document_id == "test-vault::matched.md"


class TestUnifiedDocumentServiceSearchByTitle:
    """Tests for search_by_title method."""

    @pytest.mark.asyncio
    async def test_search_by_title(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test searching by title."""
        doc1 = SQLiteDocument(
            document_id="test-vault::meeting1.md",
            vault_id=vault_id,
            file_path="meeting1.md",
            file_name="meeting1.md",
            title="Team Meeting Notes",
            content_hash="hash1",
            chunk_count=1,
        )
        await document_repo.create(doc1)

        doc2 = SQLiteDocument(
            document_id="test-vault::project.md",
            vault_id=vault_id,
            file_path="project.md",
            file_name="project.md",
            title="Project Plan",
            content_hash="hash2",
            chunk_count=1,
        )
        await document_repo.create(doc2)

        results = await service.search_by_title("test-vault", "Meeting")

        assert len(results) == 1
        assert results[0].document_id == "test-vault::meeting1.md"

    @pytest.mark.asyncio
    async def test_search_by_title_case_insensitive(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test title search is case-insensitive."""
        doc = SQLiteDocument(
            document_id="test-vault::notes.md",
            vault_id=vault_id,
            file_path="notes.md",
            file_name="notes.md",
            title="Important Notes",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        # Search with different case
        results = await service.search_by_title("test-vault", "important")

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_by_title_with_limit(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test title search with limit."""
        for i in range(10):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                title=f"Note {i}",
                content_hash=f"hash{i}",
                chunk_count=1,
            )
            await document_repo.create(doc)

        results = await service.search_by_title("test-vault", "Note", limit=3)

        assert len(results) == 3


class TestUnifiedDocumentServiceUtilityMethods:
    """Tests for utility methods."""

    @pytest.mark.asyncio
    async def test_get_vault_document_count(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting document count."""
        for i in range(7):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
                chunk_count=1,
            )
            await document_repo.create(doc)

        count = await service.get_vault_document_count("test-vault")

        assert count == 7

    @pytest.mark.asyncio
    async def test_get_all_document_ids(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting all document IDs."""
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

        ids = await service.get_all_document_ids("test-vault")

        assert len(ids) == 3
        assert "test-vault::note0.md" in ids
        assert "test-vault::note1.md" in ids
        assert "test-vault::note2.md" in ids

    @pytest.mark.asyncio
    async def test_document_exists(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test checking if document exists."""
        doc = SQLiteDocument(
            document_id="test-vault::exists.md",
            vault_id=vault_id,
            file_path="exists.md",
            file_name="exists.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        assert await service.document_exists("test-vault::exists.md") is True
        assert await service.document_exists("test-vault::nonexistent.md") is False

    @pytest.mark.asyncio
    async def test_get_document_modified_at(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting document modification time."""
        now = datetime.now()
        doc = SQLiteDocument(
            document_id="test-vault::dated.md",
            vault_id=vault_id,
            file_path="dated.md",
            file_name="dated.md",
            content_hash="hash",
            chunk_count=1,
            modified_at=now,
        )
        await document_repo.create(doc)

        modified_at = await service.get_document_modified_at("test-vault::dated.md")

        # Note: SQLite stores datetime as string, so comparison might not be exact
        assert modified_at is not None


class TestUnifiedDocumentServiceBatchOperations:
    """Tests for batch operations."""

    @pytest.mark.asyncio
    async def test_get_documents_batch(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting multiple documents in batch."""
        for i in range(5):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
                chunk_count=1,
            )
            await document_repo.create(doc)

        # Request 3 existing and 1 non-existent
        doc_ids = [
            "test-vault::note0.md",
            "test-vault::note2.md",
            "test-vault::note4.md",
            "test-vault::nonexistent.md",
        ]
        results = await service.get_documents_batch(doc_ids)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_chunk_count(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test getting chunk count for a document."""
        doc = SQLiteDocument(
            document_id="test-vault::chunked.md",
            vault_id=vault_id,
            file_path="chunked.md",
            file_name="chunked.md",
            content_hash="hash",
            chunk_count=15,
        )
        await document_repo.create(doc)

        count = await service.get_chunk_count("test-vault::chunked.md")

        assert count == 15


class TestUnifiedDocumentServiceCacheManagement:
    """Tests for cache management."""

    @pytest.mark.asyncio
    async def test_invalidate_document(
        self,
        service: UnifiedDocumentService,
        document_repo: SQLiteDocumentRepository,
        vault_id: int,
    ):
        """Test invalidating document cache."""
        doc = SQLiteDocument(
            document_id="test-vault::cached.md",
            vault_id=vault_id,
            file_path="cached.md",
            file_name="cached.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        # Load into cache
        await service.get_document("test-vault::cached.md")

        # Invalidate
        service.invalidate_document("test-vault::cached.md")

        # No exception should be raised

    def test_clear_cache(self, service: UnifiedDocumentService):
        """Test clearing cache."""
        service.clear_cache()
        # Should not raise

    def test_cache_stats(self, service: UnifiedDocumentService):
        """Test getting cache stats."""
        stats = service.cache_stats
        assert isinstance(stats, dict)


class TestUnifiedDocumentServiceVaultPaths:
    """Tests for vault path configuration."""

    def test_set_vault_path(self, sqlite_manager: SQLiteManager, tmp_path: Path):
        """Test setting vault path."""
        service = UnifiedDocumentService(sqlite_manager=sqlite_manager)
        vault_path = tmp_path / "my-vault"

        service.set_vault_path("my-vault", vault_path)

        assert service.get_vault_path("my-vault") == vault_path

    def test_get_vault_path_not_set(self, sqlite_manager: SQLiteManager):
        """Test getting vault path when not set."""
        service = UnifiedDocumentService(sqlite_manager=sqlite_manager)

        assert service.get_vault_path("unknown-vault") is None
