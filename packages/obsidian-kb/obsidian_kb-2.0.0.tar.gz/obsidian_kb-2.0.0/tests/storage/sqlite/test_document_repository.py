"""Tests for SQLiteDocumentRepository."""

from datetime import datetime
from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository
from obsidian_kb.storage.sqlite.schema import create_schema


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test.sqlite"


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset SQLiteManager singleton before each test."""
    SQLiteManager.reset_instance()
    yield
    SQLiteManager.reset_instance()


@pytest_asyncio.fixture
async def manager(temp_db_path: Path) -> SQLiteManager:
    """Create SQLiteManager with schema."""
    mgr = SQLiteManager(temp_db_path)
    await mgr.initialize()
    await create_schema(mgr)
    yield mgr
    await mgr.close()


@pytest_asyncio.fixture
async def vault_id(manager: SQLiteManager) -> int:
    """Create a test vault and return its ID."""
    vault_repo = VaultRepository(manager)
    return await vault_repo.create(Vault(name="test-vault", path="/path/to/vault"))


@pytest_asyncio.fixture
async def repo(manager: SQLiteManager) -> SQLiteDocumentRepository:
    """Create SQLiteDocumentRepository."""
    return SQLiteDocumentRepository(manager)


class TestSQLiteDocumentEntity:
    """Tests for SQLiteDocument dataclass."""

    def test_document_creation(self):
        """Test creating SQLiteDocument entity."""
        doc = SQLiteDocument(
            document_id="vault::note.md",
            vault_id=1,
            file_path="note.md",
            file_name="note.md",
            content_hash="abc123",
        )

        assert doc.document_id == "vault::note.md"
        assert doc.vault_id == 1
        assert doc.file_path == "note.md"
        assert doc.content_hash == "abc123"
        assert doc.id is None
        assert doc.title is None

    def test_document_with_all_fields(self):
        """Test creating SQLiteDocument with all fields."""
        now = datetime.now()
        doc = SQLiteDocument(
            id=1,
            document_id="vault::note.md",
            vault_id=1,
            file_path="path/to/note.md",
            file_name="note.md",
            title="My Note",
            content_hash="abc123def456",
            file_size=1024,
            chunk_count=5,
            created_at=now,
            modified_at=now,
            indexed_at=now,
        )

        assert doc.id == 1
        assert doc.title == "My Note"
        assert doc.file_size == 1024
        assert doc.chunk_count == 5


class TestDocumentRepositoryCreate:
    """Tests for SQLiteDocumentRepository create operations."""

    @pytest.mark.asyncio
    async def test_create_document(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test creating a document."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="abc123",
        )
        doc_id = await repo.create(doc)

        assert doc_id == 1

    @pytest.mark.asyncio
    async def test_create_document_with_title(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test creating document with title."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            title="My Note Title",
            content_hash="abc123",
        )
        doc_id = await repo.create(doc)

        retrieved = await repo.get_by_id(doc_id)
        assert retrieved is not None
        assert retrieved.title == "My Note Title"

    @pytest.mark.asyncio
    async def test_create_multiple_documents(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test creating multiple documents."""
        for i in range(3):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
            )
            await repo.create(doc)

        count = await repo.count()
        assert count == 3


class TestDocumentRepositoryRead:
    """Tests for SQLiteDocumentRepository read operations."""

    @pytest.mark.asyncio
    async def test_get_by_document_id(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test getting document by document_id."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="abc123",
        )
        await repo.create(doc)

        retrieved = await repo.get_by_document_id("test-vault::note.md")

        assert retrieved is not None
        assert retrieved.document_id == "test-vault::note.md"
        assert retrieved.file_path == "note.md"

    @pytest.mark.asyncio
    async def test_get_by_document_id_not_found(self, repo: SQLiteDocumentRepository):
        """Test getting non-existent document."""
        retrieved = await repo.get_by_document_id("nonexistent::path.md")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_exists_by_document_id(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test checking document existence."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="abc123",
        )
        await repo.create(doc)

        assert await repo.exists_by_document_id("test-vault::note.md") is True
        assert await repo.exists_by_document_id("nonexistent::path.md") is False

    @pytest.mark.asyncio
    async def test_get_id_by_document_id(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test getting database ID by document_id."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="abc123",
        )
        created_id = await repo.create(doc)

        retrieved_id = await repo.get_id_by_document_id("test-vault::note.md")
        assert retrieved_id == created_id


class TestDocumentRepositoryVaultQueries:
    """Tests for vault-scoped document queries."""

    @pytest_asyncio.fixture
    async def setup_documents(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Setup test documents."""
        for i in range(5):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
            )
            await repo.create(doc)

    @pytest.mark.asyncio
    async def test_find_by_vault(self, repo: SQLiteDocumentRepository, vault_id: int, setup_documents):
        """Test finding documents by vault."""
        docs = await repo.find_by_vault(vault_id)
        assert len(docs) == 5

    @pytest.mark.asyncio
    async def test_find_by_vault_with_limit(self, repo: SQLiteDocumentRepository, vault_id: int, setup_documents):
        """Test finding documents with limit."""
        docs = await repo.find_by_vault(vault_id, limit=3)
        assert len(docs) == 3

    @pytest.mark.asyncio
    async def test_find_by_vault_with_offset(self, repo: SQLiteDocumentRepository, vault_id: int, setup_documents):
        """Test finding documents with offset."""
        docs = await repo.find_by_vault(vault_id, limit=2, offset=3)
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_count_by_vault(self, repo: SQLiteDocumentRepository, vault_id: int, setup_documents):
        """Test counting documents in vault."""
        count = await repo.count_by_vault(vault_id)
        assert count == 5

    @pytest.mark.asyncio
    async def test_get_document_ids_by_vault(self, repo: SQLiteDocumentRepository, vault_id: int, setup_documents):
        """Test getting all document_ids in vault."""
        doc_ids = await repo.get_document_ids_by_vault(vault_id)

        assert len(doc_ids) == 5
        assert all(doc_id.startswith("test-vault::") for doc_id in doc_ids)


class TestDocumentRepositoryChangeDetection:
    """Tests for change detection operations."""

    @pytest.mark.asyncio
    async def test_get_content_hash(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test getting content hash."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="original_hash_123",
        )
        await repo.create(doc)

        hash_value = await repo.get_content_hash("test-vault::note.md")
        assert hash_value == "original_hash_123"

    @pytest.mark.asyncio
    async def test_get_content_hash_not_found(self, repo: SQLiteDocumentRepository):
        """Test getting content hash for non-existent document."""
        hash_value = await repo.get_content_hash("nonexistent::path.md")
        assert hash_value is None

    @pytest.mark.asyncio
    async def test_find_by_content_hash(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test finding document by content hash."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="unique_hash",
        )
        await repo.create(doc)

        found = await repo.find_by_content_hash(vault_id, "unique_hash")
        assert found is not None
        assert found.document_id == "test-vault::note.md"

    @pytest.mark.asyncio
    async def test_get_all_hashes(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test getting all content hashes."""
        for i in range(3):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash_{i}",
            )
            await repo.create(doc)

        hashes = await repo.get_all_hashes(vault_id)

        assert len(hashes) == 3
        assert hashes["test-vault::note0.md"] == "hash_0"
        assert hashes["test-vault::note1.md"] == "hash_1"
        assert hashes["test-vault::note2.md"] == "hash_2"

    @pytest.mark.asyncio
    async def test_get_file_paths(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test getting all file paths."""
        for i in range(3):
            doc = SQLiteDocument(
                document_id=f"test-vault::folder/note{i}.md",
                vault_id=vault_id,
                file_path=f"folder/note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
            )
            await repo.create(doc)

        paths = await repo.get_file_paths(vault_id)

        assert len(paths) == 3
        assert "folder/note0.md" in paths


class TestDocumentRepositoryUpdate:
    """Tests for SQLiteDocumentRepository update operations."""

    @pytest.mark.asyncio
    async def test_update_content_hash(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test updating content hash."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="old_hash",
        )
        await repo.create(doc)

        success = await repo.update_content_hash("test-vault::note.md", "new_hash")

        assert success is True
        new_hash = await repo.get_content_hash("test-vault::note.md")
        assert new_hash == "new_hash"

    @pytest.mark.asyncio
    async def test_update_chunk_count(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test updating chunk count."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="hash",
            chunk_count=0,
        )
        await repo.create(doc)

        success = await repo.update_chunk_count("test-vault::note.md", 10)

        assert success is True
        retrieved = await repo.get_by_document_id("test-vault::note.md")
        assert retrieved is not None
        assert retrieved.chunk_count == 10

    @pytest.mark.asyncio
    async def test_touch_indexed(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test updating indexed timestamp."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="hash",
        )
        await repo.create(doc)

        success = await repo.touch_indexed("test-vault::note.md")

        assert success is True
        retrieved = await repo.get_by_document_id("test-vault::note.md")
        assert retrieved is not None
        assert retrieved.indexed_at is not None


class TestDocumentRepositoryDelete:
    """Tests for SQLiteDocumentRepository delete operations."""

    @pytest.mark.asyncio
    async def test_delete_by_document_id(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test deleting document by document_id."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="hash",
        )
        await repo.create(doc)

        success = await repo.delete_by_document_id("test-vault::note.md")

        assert success is True
        assert await repo.get_by_document_id("test-vault::note.md") is None

    @pytest.mark.asyncio
    async def test_delete_by_vault(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test deleting all documents in vault."""
        for i in range(5):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
            )
            await repo.create(doc)

        count = await repo.delete_by_vault(vault_id)

        assert count == 5
        assert await repo.count_by_vault(vault_id) == 0

    @pytest.mark.asyncio
    async def test_delete_by_file_paths(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test deleting documents by file paths."""
        for i in range(5):
            doc = SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
            )
            await repo.create(doc)

        count = await repo.delete_by_file_paths(
            vault_id,
            ["note0.md", "note2.md", "note4.md"],
        )

        assert count == 3
        assert await repo.count_by_vault(vault_id) == 2


class TestDocumentRepositoryUpsert:
    """Tests for SQLiteDocumentRepository upsert operations."""

    @pytest.mark.asyncio
    async def test_upsert_creates_new(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test upsert creates new document."""
        doc = SQLiteDocument(
            document_id="test-vault::new.md",
            vault_id=vault_id,
            file_path="new.md",
            file_name="new.md",
            content_hash="hash",
        )
        doc_id = await repo.upsert(doc)

        assert doc_id > 0
        retrieved = await repo.get_by_document_id("test-vault::new.md")
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_upsert_updates_existing(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test upsert updates existing document."""
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="original_hash",
        )
        original_id = await repo.create(doc)

        updated_doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="new_hash",
            title="Updated Title",
        )
        result_id = await repo.upsert(updated_doc)

        assert result_id == original_id

        retrieved = await repo.get_by_document_id("test-vault::note.md")
        assert retrieved is not None
        assert retrieved.content_hash == "new_hash"
        assert retrieved.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_upsert_many(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Test upserting multiple documents."""
        docs = [
            SQLiteDocument(
                document_id=f"test-vault::note{i}.md",
                vault_id=vault_id,
                file_path=f"note{i}.md",
                file_name=f"note{i}.md",
                content_hash=f"hash{i}",
            )
            for i in range(5)
        ]

        count = await repo.upsert_many(docs)

        assert count == 5
        assert await repo.count_by_vault(vault_id) == 5


class TestDocumentRepositorySearch:
    """Tests for document search operations."""

    @pytest_asyncio.fixture
    async def setup_search_documents(self, repo: SQLiteDocumentRepository, vault_id: int):
        """Setup documents for search tests."""
        docs = [
            SQLiteDocument(
                document_id="test-vault::python-guide.md",
                vault_id=vault_id,
                file_path="guides/python-guide.md",
                file_name="python-guide.md",
                title="Python Programming Guide",
                content_hash="hash1",
            ),
            SQLiteDocument(
                document_id="test-vault::database-guide.md",
                vault_id=vault_id,
                file_path="guides/database-guide.md",
                file_name="database-guide.md",
                title="Database Design Guide",
                content_hash="hash2",
            ),
            SQLiteDocument(
                document_id="test-vault::meeting-notes.md",
                vault_id=vault_id,
                file_path="notes/meeting-notes.md",
                file_name="meeting-notes.md",
                title="Team Meeting Notes",
                content_hash="hash3",
            ),
        ]
        for doc in docs:
            await repo.create(doc)

    @pytest.mark.asyncio
    async def test_search_by_title(self, repo: SQLiteDocumentRepository, vault_id: int, setup_search_documents):
        """Test searching documents by title."""
        results = await repo.search_by_title(vault_id, "Guide")

        assert len(results) == 2
        titles = {r.title for r in results}
        assert "Python Programming Guide" in titles
        assert "Database Design Guide" in titles

    @pytest.mark.asyncio
    async def test_search_by_title_case_insensitive(self, repo: SQLiteDocumentRepository, vault_id: int, setup_search_documents):
        """Test case-insensitive title search."""
        results = await repo.search_by_title(vault_id, "guide")

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_by_file_path(self, repo: SQLiteDocumentRepository, vault_id: int, setup_search_documents):
        """Test searching by file path pattern."""
        results = await repo.search_by_file_path(vault_id, "guides/%")

        assert len(results) == 2
        for doc in results:
            assert doc.file_path.startswith("guides/")

    @pytest.mark.asyncio
    async def test_search_by_file_path_with_limit(self, repo: SQLiteDocumentRepository, vault_id: int, setup_search_documents):
        """Test searching by file path with limit."""
        results = await repo.search_by_file_path(vault_id, "%", limit=2)

        assert len(results) == 2
