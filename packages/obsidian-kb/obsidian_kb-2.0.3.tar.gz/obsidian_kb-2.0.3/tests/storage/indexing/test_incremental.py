"""Tests for IncrementalIndexer."""

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from obsidian_kb.storage.change_detector import ChangeDetector
from obsidian_kb.storage.indexing.incremental import (
    DocumentParseResult,
    IncrementalIndexer,
    IndexingStats,
)
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
    return tmp_path / "test_incremental.sqlite"


@pytest.fixture
def temp_vault_path(tmp_path: Path) -> Path:
    """Create temporary vault directory."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir(parents=True)
    return vault_path


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset SQLiteManager singleton before each test."""
    SQLiteManager.reset_instance()
    yield
    SQLiteManager.reset_instance()


@pytest_asyncio.fixture
async def manager_with_schema(temp_db_path: Path) -> SQLiteManager:
    """Create manager with schema initialized."""
    manager = SQLiteManager(temp_db_path)
    await manager.initialize()
    await create_schema(manager)
    yield manager
    await manager.close()


@pytest.fixture
def mock_embedding_provider():
    """Create mock embedding provider."""
    provider = MagicMock()
    provider.get_embeddings_batch = AsyncMock(
        return_value=[[0.1] * 768, [0.2] * 768]
    )
    return provider


@pytest.fixture
def mock_cached_provider():
    """Create mock cached embedding provider with metrics."""
    provider = MagicMock()
    provider.get_embeddings_batch = AsyncMock(
        return_value=[[0.1] * 768, [0.2] * 768]
    )
    provider.metrics = MagicMock()
    provider.metrics.cache_hits = 5
    provider.metrics.cache_misses = 2
    provider.metrics.embeddings_generated = 2
    provider.metrics.hit_rate = 5 / 7
    return provider


def create_mock_parser(chunks_per_doc: int = 2):
    """Create a mock document parser."""
    def parser(vault_path: Path, file_path: Path) -> DocumentParseResult:
        full_path = vault_path / file_path
        content = full_path.read_text(encoding="utf-8")
        content_hash = ChangeDetector.compute_content_hash(full_path)

        stat = full_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime)

        # Simple chunking
        chunks = [f"Chunk {i}" for i in range(chunks_per_doc)]

        return DocumentParseResult(
            file_path=file_path,
            title=file_path.stem,
            content=content,
            content_hash=content_hash,
            metadata={"tags": ["test"]},
            chunks=chunks,
            file_size=stat.st_size,
            created_at=None,
            modified_at=modified_at,
        )

    return parser


class TestIndexingStats:
    """Tests for IndexingStats dataclass."""

    def test_empty_stats(self):
        """Test empty IndexingStats."""
        stats = IndexingStats()
        assert stats.total_processed == 0
        assert stats.cache_hit_rate == 0.0
        assert stats.errors == []

    def test_stats_with_values(self):
        """Test IndexingStats with values."""
        stats = IndexingStats(
            files_added=5,
            files_updated=3,
            files_deleted=2,
            files_unchanged=10,
            embeddings_cached=80,
            embeddings_generated=20,
        )
        assert stats.total_processed == 8
        assert stats.cache_hit_rate == 0.8

    def test_stats_repr(self):
        """Test IndexingStats string representation."""
        stats = IndexingStats(
            files_added=1,
            files_updated=2,
            chunks_created=10,
            duration_ms=1500.0,
        )
        repr_str = repr(stats)
        assert "added=1" in repr_str
        assert "updated=2" in repr_str
        assert "chunks=10" in repr_str


class TestDocumentParseResult:
    """Tests for DocumentParseResult."""

    def test_parse_result_creation(self):
        """Test creating DocumentParseResult."""
        result = DocumentParseResult(
            file_path=Path("note.md"),
            title="Note",
            content="# Note\n\nContent",
            content_hash="abc123" + "0" * 58,
            metadata={"tags": ["test"]},
            chunks=["Chunk 1", "Chunk 2"],
            file_size=100,
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )
        assert result.title == "Note"
        assert len(result.chunks) == 2


class TestIncrementalIndexerInit:
    """Tests for IncrementalIndexer initialization."""

    @pytest.mark.asyncio
    async def test_init_with_manager(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
    ):
        """Test initialization with SQLiteManager."""
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )
        assert indexer is not None

    @pytest.mark.asyncio
    async def test_init_with_custom_parser(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
    ):
        """Test initialization with custom document parser."""
        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )
        assert indexer._document_parser == parser


class TestIndexVault:
    """Tests for index_vault method."""

    @pytest.mark.asyncio
    async def test_index_empty_vault(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test indexing an empty vault."""
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        stats = await indexer.index_vault("test-vault", temp_vault_path)

        assert stats.total_processed == 0
        assert stats.files_unchanged == 0
        assert not stats.errors

    @pytest.mark.asyncio
    async def test_index_new_files(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test indexing new files."""
        # Create files
        (temp_vault_path / "note1.md").write_text("# Note 1")
        (temp_vault_path / "note2.md").write_text("# Note 2")

        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=create_mock_parser(),
        )

        stats = await indexer.index_vault("test-vault", temp_vault_path)

        assert stats.files_added == 2
        assert stats.files_updated == 0
        assert stats.files_deleted == 0
        assert stats.chunks_created == 4  # 2 chunks per file

    @pytest.mark.asyncio
    async def test_index_with_cached_provider(
        self,
        manager_with_schema: SQLiteManager,
        mock_cached_provider,
        temp_vault_path: Path,
    ):
        """Test indexing with cached embedding provider."""
        (temp_vault_path / "note.md").write_text("# Note")

        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_cached_provider,
            document_parser=create_mock_parser(),
        )

        stats = await indexer.index_vault("test-vault", temp_vault_path)

        # Should have cache metrics
        assert stats.embeddings_cached >= 0
        assert stats.embeddings_generated >= 0

    @pytest.mark.asyncio
    async def test_incremental_index_unchanged_files(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test that unchanged files are skipped."""
        # Create file
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Note")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # First index
        stats1 = await indexer.index_vault("test-vault", temp_vault_path)
        assert stats1.files_added == 1

        # Second index - should skip unchanged file
        stats2 = await indexer.index_vault("test-vault", temp_vault_path)
        assert stats2.files_added == 0
        assert stats2.files_unchanged == 1

    @pytest.mark.asyncio
    async def test_incremental_index_modified_files(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test that modified files are reindexed."""
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Original")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # First index
        await indexer.index_vault("test-vault", temp_vault_path)

        # Modify file
        file_path.write_text("# Modified")

        # Second index
        stats = await indexer.index_vault("test-vault", temp_vault_path)
        assert stats.files_updated == 1

    @pytest.mark.asyncio
    async def test_incremental_index_deleted_files(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test that deleted files are removed from index."""
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Note")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # First index
        await indexer.index_vault("test-vault", temp_vault_path)

        # Delete file
        file_path.unlink()

        # Second index
        stats = await indexer.index_vault("test-vault", temp_vault_path)
        assert stats.files_deleted == 1

    @pytest.mark.asyncio
    async def test_force_reindex(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test force reindexing all files."""
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Note")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # First index
        await indexer.index_vault("test-vault", temp_vault_path)

        # Force reindex
        stats = await indexer.index_vault(
            "test-vault", temp_vault_path, force=True
        )

        # With force=True, file should be processed again
        assert stats.files_added == 1  # Treated as added in force mode

    @pytest.mark.asyncio
    async def test_progress_callback(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test progress callback is called."""
        (temp_vault_path / "note1.md").write_text("# Note 1")
        (temp_vault_path / "note2.md").write_text("# Note 2")

        progress_calls = []

        def progress_callback(processed: int, total: int):
            progress_calls.append((processed, total))

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        await indexer.index_vault(
            "test-vault",
            temp_vault_path,
            progress_callback=progress_callback,
        )

        assert len(progress_calls) == 2
        assert progress_calls[-1][0] == 2  # Last call should show 2 processed

    @pytest.mark.asyncio
    async def test_chunk_storage_callback(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test chunk storage callback is called."""
        (temp_vault_path / "note.md").write_text("# Note")

        stored_chunks = []

        async def storage_callback(vault_name: str, chunks: list):
            stored_chunks.extend(chunks)

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
            chunk_storage_callback=storage_callback,
        )

        await indexer.index_vault("test-vault", temp_vault_path)

        assert len(stored_chunks) == 2  # 2 chunks from 1 file


class TestIndexFiles:
    """Tests for index_files method."""

    @pytest.mark.asyncio
    async def test_index_specific_files(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test indexing specific files."""
        (temp_vault_path / "note1.md").write_text("# Note 1")
        (temp_vault_path / "note2.md").write_text("# Note 2")
        (temp_vault_path / "note3.md").write_text("# Note 3")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # Only index note1 and note2
        stats = await indexer.index_files(
            "test-vault",
            temp_vault_path,
            [Path("note1.md"), Path("note2.md")],
        )

        assert stats.files_added == 2

    @pytest.mark.asyncio
    async def test_index_nonexistent_file(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test indexing nonexistent file adds error."""
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        stats = await indexer.index_files(
            "test-vault",
            temp_vault_path,
            [Path("nonexistent.md")],
        )

        assert stats.files_added == 0
        assert len(stats.errors) == 1


class TestDeleteFiles:
    """Tests for delete_files method."""

    @pytest.mark.asyncio
    async def test_delete_files(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test deleting specific files from index."""
        (temp_vault_path / "note.md").write_text("# Note")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # First index
        await indexer.index_vault("test-vault", temp_vault_path)

        # Delete from index (not from disk)
        stats = await indexer.delete_files("test-vault", ["note.md"])

        assert stats.files_deleted == 1

    @pytest.mark.asyncio
    async def test_delete_nonexistent_vault(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
    ):
        """Test deleting from nonexistent vault."""
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        stats = await indexer.delete_files("nonexistent-vault", ["note.md"])

        assert len(stats.errors) == 1


class TestClearVault:
    """Tests for clear_vault method."""

    @pytest.mark.asyncio
    async def test_clear_vault(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test clearing all indexed data for a vault."""
        (temp_vault_path / "note1.md").write_text("# Note 1")
        (temp_vault_path / "note2.md").write_text("# Note 2")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        # First index
        await indexer.index_vault("test-vault", temp_vault_path)

        # Clear vault
        stats = await indexer.clear_vault("test-vault")

        assert stats.files_deleted == 2

    @pytest.mark.asyncio
    async def test_clear_nonexistent_vault(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
    ):
        """Test clearing nonexistent vault."""
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        stats = await indexer.clear_vault("nonexistent-vault")

        assert stats.files_deleted == 0
        assert not stats.errors


class TestGetIndexingStats:
    """Tests for get_indexing_stats method."""

    @pytest.mark.asyncio
    async def test_stats_nonexistent_vault(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
    ):
        """Test stats for nonexistent vault."""
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        stats = await indexer.get_indexing_stats("nonexistent-vault")

        assert stats["exists"] is False
        assert stats["document_count"] == 0

    @pytest.mark.asyncio
    async def test_stats_existing_vault(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test stats for existing vault."""
        (temp_vault_path / "note.md").write_text("# Note")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=parser,
        )

        await indexer.index_vault("test-vault", temp_vault_path)

        stats = await indexer.get_indexing_stats("test-vault")

        assert stats["exists"] is True
        assert stats["document_count"] == 1

    @pytest.mark.asyncio
    async def test_stats_with_cache_metrics(
        self,
        manager_with_schema: SQLiteManager,
        mock_cached_provider,
        temp_vault_path: Path,
    ):
        """Test stats include cache metrics."""
        (temp_vault_path / "note.md").write_text("# Note")

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_cached_provider,
            document_parser=parser,
        )

        await indexer.index_vault("test-vault", temp_vault_path)

        stats = await indexer.get_indexing_stats("test-vault")

        assert "cache_stats" in stats
        assert stats["cache_stats"]["cache_hits"] == 5


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_parser_error_handling(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test handling of parser errors."""
        (temp_vault_path / "note.md").write_text("# Note")

        def failing_parser(vault_path: Path, file_path: Path):
            raise ValueError("Parse error")

        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
            document_parser=failing_parser,
        )

        stats = await indexer.index_vault("test-vault", temp_vault_path)

        # Should have error but not crash
        assert len(stats.errors) == 1
        assert "Parse error" in stats.errors[0]

    @pytest.mark.asyncio
    async def test_embedding_error_handling(
        self,
        manager_with_schema: SQLiteManager,
        temp_vault_path: Path,
    ):
        """Test handling of embedding errors."""
        (temp_vault_path / "note.md").write_text("# Note")

        provider = MagicMock()
        provider.get_embeddings_batch = AsyncMock(
            side_effect=RuntimeError("Embedding error")
        )

        parser = create_mock_parser()
        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=provider,
            document_parser=parser,
        )

        stats = await indexer.index_vault("test-vault", temp_vault_path)

        assert len(stats.errors) >= 1


class TestDefaultDocumentParser:
    """Tests for default document parser."""

    @pytest.mark.asyncio
    async def test_default_parser_extracts_title(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test default parser extracts title from H1."""
        (temp_vault_path / "note.md").write_text("# My Title\n\nContent here.")

        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        result = indexer._default_document_parser(
            temp_vault_path, Path("note.md")
        )

        assert result.title == "My Title"

    @pytest.mark.asyncio
    async def test_default_parser_chunks_by_paragraphs(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test default parser chunks by double newlines."""
        content = "# Title\n\nParagraph 1\n\nParagraph 2\n\nParagraph 3"
        (temp_vault_path / "note.md").write_text(content)

        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        result = indexer._default_document_parser(
            temp_vault_path, Path("note.md")
        )

        assert len(result.chunks) == 4  # Title + 3 paragraphs

    @pytest.mark.asyncio
    async def test_default_parser_uses_filename_as_title(
        self,
        manager_with_schema: SQLiteManager,
        mock_embedding_provider,
        temp_vault_path: Path,
    ):
        """Test default parser uses filename when no H1."""
        (temp_vault_path / "my-note.md").write_text("Content without H1")

        indexer = IncrementalIndexer(
            sqlite_manager=manager_with_schema,
            embedding_provider=mock_embedding_provider,
        )

        result = indexer._default_document_parser(
            temp_vault_path, Path("my-note.md")
        )

        assert result.title == "my-note"
