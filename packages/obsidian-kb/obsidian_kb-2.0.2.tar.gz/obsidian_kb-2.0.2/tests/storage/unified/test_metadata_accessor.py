"""Tests for UnifiedMetadataAccessor."""

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from obsidian_kb.core.ttl_cache import TTLCache
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository
from obsidian_kb.storage.sqlite.schema import create_schema
from obsidian_kb.storage.unified.metadata_accessor import UnifiedMetadataAccessor
from obsidian_kb.storage.unified.types import DataSource, UnifiedDocumentInfo


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test_unified.sqlite"


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


class TestUnifiedMetadataAccessorInit:
    """Tests for UnifiedMetadataAccessor initialization."""

    @pytest.mark.asyncio
    async def test_init_with_manager(self, sqlite_manager: SQLiteManager):
        """Test initialization with SQLite manager."""
        accessor = UnifiedMetadataAccessor(sqlite_manager=sqlite_manager)
        assert accessor._sqlite_manager is not None
        assert accessor._cache is not None

    @pytest.mark.asyncio
    async def test_init_with_repos(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test initialization with repositories."""
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )
        assert accessor._document_repo is document_repo
        assert accessor._vault_repo is vault_repo

    @pytest.mark.asyncio
    async def test_init_with_custom_cache(self, sqlite_manager: SQLiteManager):
        """Test initialization with custom cache."""
        custom_cache = TTLCache(ttl_seconds=60.0, max_size=100)
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            cache=custom_cache,
        )
        assert accessor._cache is custom_cache


class TestUnifiedMetadataAccessorGetDocument:
    """Tests for get_document method."""

    @pytest.mark.asyncio
    async def test_get_document_from_sqlite(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test getting document from SQLite."""
        # Create a document
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

        # Create accessor
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        # Get document
        result = await accessor.get_document("test-vault::note.md")

        assert result is not None
        assert result.document_id == "test-vault::note.md"
        assert result.file_path == "note.md"
        assert result.title == "Test Note"
        assert result.content_hash == "hash123"
        assert result.chunk_count == 2
        assert result.source == DataSource.SQLITE

    @pytest.mark.asyncio
    async def test_get_document_not_found(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test getting non-existent document."""
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        result = await accessor.get_document("test-vault::nonexistent.md")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_document_uses_cache(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test that get_document uses cache."""
        # Create a document
        doc = SQLiteDocument(
            document_id="test-vault::cached.md",
            vault_id=vault_id,
            file_path="cached.md",
            file_name="cached.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        # First call - should hit database
        result1 = await accessor.get_document("test-vault::cached.md")
        assert result1 is not None

        # Second call - should use cache
        result2 = await accessor.get_document("test-vault::cached.md")
        assert result2 is not None
        assert result1.document_id == result2.document_id

    @pytest.mark.asyncio
    async def test_get_document_bypass_cache(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test get_document with cache bypass."""
        doc = SQLiteDocument(
            document_id="test-vault::bypass.md",
            vault_id=vault_id,
            file_path="bypass.md",
            file_name="bypass.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        # Call with cache bypass
        result = await accessor.get_document("test-vault::bypass.md", use_cache=False)
        assert result is not None


class TestUnifiedMetadataAccessorGetDocumentsByVault:
    """Tests for get_documents_by_vault method."""

    @pytest.mark.asyncio
    async def test_get_documents_by_vault(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test getting all documents in a vault."""
        # Create multiple documents
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

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        results = await accessor.get_documents_by_vault("test-vault")

        assert len(results) == 5
        for doc in results:
            assert doc.vault_name == "test-vault"
            assert doc.source == DataSource.SQLITE

    @pytest.mark.asyncio
    async def test_get_documents_by_vault_with_limit(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
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

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        results = await accessor.get_documents_by_vault("test-vault", limit=3)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_documents_by_vault_empty(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test getting documents from empty vault."""
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        results = await accessor.get_documents_by_vault("nonexistent-vault")
        assert results == []


class TestUnifiedMetadataAccessorSearchByProperty:
    """Tests for search_by_property method."""

    @pytest.mark.asyncio
    async def test_search_by_property(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test searching by property."""
        # Create document
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="hash",
            chunk_count=1,
        )
        doc_db_id = await document_repo.create(doc)

        # Add property
        await sqlite_manager.execute(
            """
            INSERT INTO document_properties
            (document_id, property_key, property_value, value_type)
            VALUES (?, ?, ?, ?)
            """,
            (doc_db_id, "status", "active", "string"),
        )

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        results = await accessor.search_by_property("test-vault", "status", "active")

        assert len(results) == 1
        assert results[0].document_id == "test-vault::note.md"

    @pytest.mark.asyncio
    async def test_search_by_property_no_match(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test searching for non-matching property."""
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        results = await accessor.search_by_property("test-vault", "status", "nonexistent")
        assert results == []


class TestUnifiedMetadataAccessorCacheManagement:
    """Tests for cache management methods."""

    @pytest.mark.asyncio
    async def test_invalidate_document(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test invalidating document cache."""
        doc = SQLiteDocument(
            document_id="test-vault::cache.md",
            vault_id=vault_id,
            file_path="cache.md",
            file_name="cache.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        # Load into cache
        await accessor.get_document("test-vault::cache.md")

        # Invalidate
        accessor.invalidate_document("test-vault::cache.md")

        # Verify cache is empty for this key
        cache_key = accessor._cache_key("doc", "test-vault::cache.md")
        assert accessor._cache.get(cache_key) is None

    def test_clear_cache(self, sqlite_manager: SQLiteManager):
        """Test clearing all cache."""
        accessor = UnifiedMetadataAccessor(sqlite_manager=sqlite_manager)

        # Add some data to cache
        accessor._cache.set("key1", "value1")
        accessor._cache.set("key2", "value2")

        # Clear cache
        accessor.clear_cache()

        # Verify cache is empty
        assert accessor._cache.get("key1") is None
        assert accessor._cache.get("key2") is None

    def test_cache_stats(self, sqlite_manager: SQLiteManager):
        """Test getting cache statistics."""
        accessor = UnifiedMetadataAccessor(sqlite_manager=sqlite_manager)

        stats = accessor.cache_stats
        assert "size" in stats
        assert "ttl_seconds" in stats
        assert "max_size" in stats


class TestUnifiedMetadataAccessorUtilityMethods:
    """Tests for utility methods."""

    @pytest.mark.asyncio
    async def test_get_document_ids_by_vault(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test getting all document IDs in a vault."""
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

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        doc_ids = await accessor.get_document_ids_by_vault("test-vault")

        assert len(doc_ids) == 3
        assert "test-vault::note0.md" in doc_ids
        assert "test-vault::note1.md" in doc_ids
        assert "test-vault::note2.md" in doc_ids

    @pytest.mark.asyncio
    async def test_document_exists_true(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
        vault_id: int,
    ):
        """Test document_exists returns True for existing document."""
        doc = SQLiteDocument(
            document_id="test-vault::exists.md",
            vault_id=vault_id,
            file_path="exists.md",
            file_name="exists.md",
            content_hash="hash",
            chunk_count=1,
        )
        await document_repo.create(doc)

        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        exists = await accessor.document_exists("test-vault::exists.md")
        assert exists is True

    @pytest.mark.asyncio
    async def test_document_exists_false(
        self,
        sqlite_manager: SQLiteManager,
        document_repo: SQLiteDocumentRepository,
        vault_repo: VaultRepository,
    ):
        """Test document_exists returns False for non-existent document."""
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            document_repo=document_repo,
            vault_repo=vault_repo,
        )

        exists = await accessor.document_exists("test-vault::nonexistent.md")
        assert exists is False
