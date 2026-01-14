"""Tests for SQLite schema."""

from pathlib import Path

import pytest

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.schema import (
    ALL_TABLES,
    SCHEMA_VERSION,
    create_schema,
    drop_all_tables,
    get_schema_version,
)


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


class TestSchemaConstants:
    """Tests for schema constants."""

    def test_schema_version_format(self):
        """Test schema version has semantic versioning format."""
        parts = SCHEMA_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_all_tables_not_empty(self):
        """Test ALL_TABLES contains table definitions."""
        assert len(ALL_TABLES) == 12  # All 12 tables

    def test_all_tables_contain_create_table(self):
        """Test all table definitions contain CREATE TABLE."""
        for table_ddl in ALL_TABLES:
            assert "CREATE TABLE" in table_ddl


class TestCreateSchema:
    """Tests for schema creation."""

    @pytest.mark.asyncio
    async def test_create_schema_creates_all_tables(self, temp_db_path: Path):
        """Test that create_schema creates all tables."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            # Get all tables
            tables = await manager.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            table_names = {t["name"] for t in tables}

            # Verify all expected tables exist
            expected_tables = {
                "schema_metadata",
                "vaults",
                "documents",
                "document_properties",
                "property_schemas",
                "tags",
                "document_tags",
                "links",
                "embedding_cache",
                "search_history",
                "entities",
                "document_entities",
            }

            assert table_names == expected_tables

    @pytest.mark.asyncio
    async def test_create_schema_idempotent(self, temp_db_path: Path):
        """Test that create_schema can be called multiple times."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)
            await create_schema(manager)  # Should not raise

            # Verify tables still exist
            count = await manager.fetch_value(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            assert count == 12

    @pytest.mark.asyncio
    async def test_create_schema_sets_version(self, temp_db_path: Path):
        """Test that create_schema sets schema version."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            version = await get_schema_version(manager)
            assert version == SCHEMA_VERSION


class TestGetSchemaVersion:
    """Tests for get_schema_version."""

    @pytest.mark.asyncio
    async def test_get_version_returns_none_before_init(self, temp_db_path: Path):
        """Test version is None before schema creation."""
        async with SQLiteManager(temp_db_path) as manager:
            version = await get_schema_version(manager)
            assert version is None

    @pytest.mark.asyncio
    async def test_get_version_returns_version_after_init(self, temp_db_path: Path):
        """Test version is returned after schema creation."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)
            version = await get_schema_version(manager)
            assert version == SCHEMA_VERSION


class TestDropAllTables:
    """Tests for drop_all_tables."""

    @pytest.mark.asyncio
    async def test_drop_all_tables_removes_all(self, temp_db_path: Path):
        """Test drop_all_tables removes all tables."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            # Verify tables exist
            count_before = await manager.fetch_value(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            assert count_before == 12

            # Drop all
            await drop_all_tables(manager)

            # Verify tables removed
            count_after = await manager.fetch_value(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            assert count_after == 0

    @pytest.mark.asyncio
    async def test_drop_all_tables_safe_when_empty(self, temp_db_path: Path):
        """Test drop_all_tables is safe when no tables exist."""
        async with SQLiteManager(temp_db_path) as manager:
            await drop_all_tables(manager)  # Should not raise


class TestTableStructure:
    """Tests for individual table structures."""

    @pytest.mark.asyncio
    async def test_vaults_table_columns(self, temp_db_path: Path):
        """Test vaults table has correct columns."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            columns = await manager.fetch_all("PRAGMA table_info(vaults)")
            column_names = {c["name"] for c in columns}

            expected = {"id", "name", "path", "created_at", "last_indexed_at",
                       "document_count", "chunk_count", "settings_json"}
            assert expected <= column_names

    @pytest.mark.asyncio
    async def test_documents_table_columns(self, temp_db_path: Path):
        """Test documents table has correct columns."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            columns = await manager.fetch_all("PRAGMA table_info(documents)")
            column_names = {c["name"] for c in columns}

            expected = {"id", "document_id", "vault_id", "file_path", "file_name",
                       "title", "content_hash", "file_size", "chunk_count",
                       "created_at", "modified_at", "indexed_at"}
            assert expected <= column_names

    @pytest.mark.asyncio
    async def test_document_properties_table_columns(self, temp_db_path: Path):
        """Test document_properties table has correct columns."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            columns = await manager.fetch_all("PRAGMA table_info(document_properties)")
            column_names = {c["name"] for c in columns}

            expected = {"id", "document_id", "property_key", "property_value",
                       "value_type", "value_number", "value_date", "value_link_target",
                       "list_index"}
            assert expected <= column_names

    @pytest.mark.asyncio
    async def test_embedding_cache_table_columns(self, temp_db_path: Path):
        """Test embedding_cache table has correct columns."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            columns = await manager.fetch_all("PRAGMA table_info(embedding_cache)")
            column_names = {c["name"] for c in columns}

            expected = {"id", "content_hash", "model_name", "embedding",
                       "embedding_dim", "created_at", "last_used_at", "access_count"}
            assert expected <= column_names

    @pytest.mark.asyncio
    async def test_links_table_columns(self, temp_db_path: Path):
        """Test links table has correct columns."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            columns = await manager.fetch_all("PRAGMA table_info(links)")
            column_names = {c["name"] for c in columns}

            expected = {"id", "source_document_id", "target_name", "target_document_id",
                       "link_type", "context", "line_number", "created_at"}
            assert expected <= column_names


class TestIndexes:
    """Tests for index creation."""

    @pytest.mark.asyncio
    async def test_indexes_created(self, temp_db_path: Path):
        """Test that indexes are created."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            indexes = await manager.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
            )

            # Should have multiple indexes
            assert len(indexes) > 10

            # Check some key indexes exist
            index_names = {i["name"] for i in indexes}
            assert "idx_documents_document_id" in index_names
            assert "idx_documents_vault_id" in index_names
            assert "idx_doc_props_document_id" in index_names


class TestForeignKeys:
    """Tests for foreign key constraints."""

    @pytest.mark.asyncio
    async def test_documents_references_vaults(self, temp_db_path: Path):
        """Test documents table references vaults."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            # Insert vault
            await manager.execute(
                "INSERT INTO vaults (name, path) VALUES (?, ?)",
                ("test-vault", "/path/to/vault"),
            )

            # Insert document referencing vault
            await manager.execute(
                """INSERT INTO documents
                   (document_id, vault_id, file_path, file_name, content_hash)
                   VALUES (?, ?, ?, ?, ?)""",
                ("test-vault::note.md", 1, "note.md", "note.md", "abc123"),
            )

            # Verify it exists
            doc = await manager.fetch_one(
                "SELECT * FROM documents WHERE document_id = ?",
                ("test-vault::note.md",),
            )
            assert doc is not None

    @pytest.mark.asyncio
    async def test_cascade_delete_documents(self, temp_db_path: Path):
        """Test that deleting vault cascades to documents."""
        async with SQLiteManager(temp_db_path) as manager:
            await create_schema(manager)

            # Insert vault and document
            await manager.execute(
                "INSERT INTO vaults (name, path) VALUES (?, ?)",
                ("test-vault", "/path"),
            )
            await manager.execute(
                """INSERT INTO documents
                   (document_id, vault_id, file_path, file_name, content_hash)
                   VALUES (?, ?, ?, ?, ?)""",
                ("test-vault::note.md", 1, "note.md", "note.md", "abc123"),
            )

            # Delete vault
            await manager.execute("DELETE FROM vaults WHERE id = 1")

            # Document should be deleted too
            count = await manager.fetch_value("SELECT COUNT(*) FROM documents")
            assert count == 0
