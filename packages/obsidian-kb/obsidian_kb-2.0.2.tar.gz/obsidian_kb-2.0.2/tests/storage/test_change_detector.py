"""Tests for ChangeDetector."""

import asyncio
from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.storage.change_detector import (
    ChangeDetector,
    ChangeSet,
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
    return tmp_path / "test_change_detector.sqlite"


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


@pytest_asyncio.fixture
async def detector(manager_with_schema: SQLiteManager) -> ChangeDetector:
    """Create ChangeDetector instance."""
    return ChangeDetector(manager_with_schema)


@pytest_asyncio.fixture
async def vault_id(manager_with_schema: SQLiteManager) -> int:
    """Create a test vault and return its ID."""
    repo = VaultRepository(manager_with_schema)
    vault = Vault(name="test-vault", path="/test/path")
    vault_id = await repo.create(vault)
    return vault_id


class TestChangeSet:
    """Tests for ChangeSet dataclass."""

    def test_empty_changeset(self):
        """Test empty ChangeSet properties."""
        cs = ChangeSet()
        assert cs.has_changes is False
        assert cs.total_to_process == 0
        assert cs.total_deleted == 0
        assert cs.unchanged == 0

    def test_changeset_with_added(self):
        """Test ChangeSet with added files."""
        cs = ChangeSet(added=[Path("a.md"), Path("b.md")])
        assert cs.has_changes is True
        assert cs.total_to_process == 2
        assert cs.total_deleted == 0

    def test_changeset_with_modified(self):
        """Test ChangeSet with modified files."""
        cs = ChangeSet(modified=[Path("a.md")])
        assert cs.has_changes is True
        assert cs.total_to_process == 1

    def test_changeset_with_deleted(self):
        """Test ChangeSet with deleted files."""
        cs = ChangeSet(deleted=["vault::a.md", "vault::b.md"])
        assert cs.has_changes is True
        assert cs.total_to_process == 0
        assert cs.total_deleted == 2

    def test_changeset_mixed(self):
        """Test ChangeSet with mixed changes."""
        cs = ChangeSet(
            added=[Path("new.md")],
            modified=[Path("changed.md")],
            deleted=["vault::old.md"],
            unchanged=5,
        )
        assert cs.has_changes is True
        assert cs.total_to_process == 2
        assert cs.total_deleted == 1
        assert cs.unchanged == 5

    def test_changeset_repr(self):
        """Test ChangeSet string representation."""
        cs = ChangeSet(
            added=[Path("a.md")],
            modified=[Path("b.md")],
            deleted=["c"],
            unchanged=10,
        )
        repr_str = repr(cs)
        assert "added=1" in repr_str
        assert "modified=1" in repr_str
        assert "deleted=1" in repr_str
        assert "unchanged=10" in repr_str


class TestComputeContentHash:
    """Tests for content hash computation."""

    def test_compute_hash_file(self, temp_vault_path: Path):
        """Test computing hash of a file."""
        file_path = temp_vault_path / "test.md"
        file_path.write_text("# Test\n\nContent here.")

        hash1 = ChangeDetector.compute_content_hash(file_path)
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA256 hex

    def test_hash_deterministic(self, temp_vault_path: Path):
        """Test that hash is deterministic."""
        file_path = temp_vault_path / "test.md"
        file_path.write_text("Same content")

        hash1 = ChangeDetector.compute_content_hash(file_path)
        hash2 = ChangeDetector.compute_content_hash(file_path)
        assert hash1 == hash2

    def test_hash_changes_with_content(self, temp_vault_path: Path):
        """Test that hash changes when content changes."""
        file_path = temp_vault_path / "test.md"

        file_path.write_text("Content 1")
        hash1 = ChangeDetector.compute_content_hash(file_path)

        file_path.write_text("Content 2")
        hash2 = ChangeDetector.compute_content_hash(file_path)

        assert hash1 != hash2

    def test_hash_unicode_content(self, temp_vault_path: Path):
        """Test hash with unicode content."""
        file_path = temp_vault_path / "unicode.md"
        file_path.write_text("Привет мир 你好世界 🎉", encoding="utf-8")

        hash_val = ChangeDetector.compute_content_hash(file_path)
        assert len(hash_val) == 64


class TestChangeDetectorInit:
    """Tests for ChangeDetector initialization."""

    @pytest.mark.asyncio
    async def test_init_with_manager(self, manager_with_schema: SQLiteManager):
        """Test initialization with SQLiteManager."""
        detector = ChangeDetector(manager_with_schema)
        assert detector is not None

    @pytest.mark.asyncio
    async def test_init_with_custom_filter(self, manager_with_schema: SQLiteManager):
        """Test initialization with custom file filter."""
        def custom_filter(path: Path) -> bool:
            return path.suffix in [".md", ".txt"]

        detector = ChangeDetector(manager_with_schema, file_filter=custom_filter)
        assert detector._file_filter == custom_filter


class TestDetectChangesNewVault:
    """Tests for detecting changes in a new vault."""

    @pytest.mark.asyncio
    async def test_new_vault_all_files_added(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test that all files are added in a new vault."""
        # Create some files
        (temp_vault_path / "note1.md").write_text("# Note 1")
        (temp_vault_path / "note2.md").write_text("# Note 2")
        (temp_vault_path / "subdir").mkdir()
        (temp_vault_path / "subdir" / "note3.md").write_text("# Note 3")

        changes = await detector.detect_changes("new-vault", temp_vault_path)

        assert len(changes.added) == 3
        assert changes.modified == []
        assert changes.deleted == []
        assert changes.unchanged == 0

    @pytest.mark.asyncio
    async def test_empty_vault(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test empty vault."""
        changes = await detector.detect_changes("empty-vault", temp_vault_path)

        assert changes.added == []
        assert changes.modified == []
        assert changes.deleted == []
        assert changes.has_changes is False

    @pytest.mark.asyncio
    async def test_ignores_hidden_files(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test that hidden files are ignored."""
        (temp_vault_path / "visible.md").write_text("# Visible")
        (temp_vault_path / ".hidden.md").write_text("# Hidden")
        (temp_vault_path / ".hidden_dir").mkdir()
        (temp_vault_path / ".hidden_dir" / "note.md").write_text("# Hidden dir note")

        changes = await detector.detect_changes("vault", temp_vault_path)

        # Only visible.md should be added
        assert len(changes.added) == 1
        assert changes.added[0].name == "visible.md"

    @pytest.mark.asyncio
    async def test_only_markdown_files(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test that only .md files are detected."""
        (temp_vault_path / "note.md").write_text("# Note")
        (temp_vault_path / "data.json").write_text("{}")
        (temp_vault_path / "image.png").write_bytes(b"PNG")
        (temp_vault_path / "readme.txt").write_text("readme")

        changes = await detector.detect_changes("vault", temp_vault_path)

        assert len(changes.added) == 1
        assert changes.added[0].name == "note.md"


class TestDetectChangesExistingVault:
    """Tests for detecting changes in an existing vault."""

    @pytest.mark.asyncio
    async def test_unchanged_files(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test unchanged files are detected correctly."""
        # Create file
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Test Note")
        content_hash = ChangeDetector.compute_content_hash(file_path)

        # Store in database
        doc_repo = SQLiteDocumentRepository(manager_with_schema)
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash=content_hash,
        )
        await doc_repo.create(doc)

        # Detect changes
        changes = await detector.detect_changes("test-vault", temp_vault_path)

        assert changes.added == []
        assert changes.modified == []
        assert changes.deleted == []
        assert changes.unchanged == 1

    @pytest.mark.asyncio
    async def test_modified_file(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test modified files are detected."""
        # Create file
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Original")

        # Store with OLD hash
        doc_repo = SQLiteDocumentRepository(manager_with_schema)
        doc = SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="old_hash_000000000000000000000000000000000000000000000000",
        )
        await doc_repo.create(doc)

        # Detect changes
        changes = await detector.detect_changes("test-vault", temp_vault_path)

        assert len(changes.modified) == 1
        assert changes.modified[0].name == "note.md"
        assert changes.added == []
        assert changes.deleted == []

    @pytest.mark.asyncio
    async def test_deleted_file(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test deleted files are detected."""
        # Store file in database that doesn't exist on disk
        doc_repo = SQLiteDocumentRepository(manager_with_schema)
        doc = SQLiteDocument(
            document_id="test-vault::deleted.md",
            vault_id=vault_id,
            file_path="deleted.md",
            file_name="deleted.md",
            content_hash="some_hash_00000000000000000000000000000000000000000000",
        )
        await doc_repo.create(doc)

        # Detect changes
        changes = await detector.detect_changes("test-vault", temp_vault_path)

        assert len(changes.deleted) == 1
        assert "test-vault::deleted.md" in changes.deleted
        assert changes.added == []
        assert changes.modified == []

    @pytest.mark.asyncio
    async def test_mixed_changes(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test mixed changes (added, modified, deleted, unchanged)."""
        doc_repo = SQLiteDocumentRepository(manager_with_schema)

        # 1. Create unchanged file
        unchanged = temp_vault_path / "unchanged.md"
        unchanged.write_text("# Unchanged")
        unchanged_hash = ChangeDetector.compute_content_hash(unchanged)
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::unchanged.md",
            vault_id=vault_id,
            file_path="unchanged.md",
            file_name="unchanged.md",
            content_hash=unchanged_hash,
        ))

        # 2. Create modified file
        modified = temp_vault_path / "modified.md"
        modified.write_text("# Modified - new content")
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::modified.md",
            vault_id=vault_id,
            file_path="modified.md",
            file_name="modified.md",
            content_hash="old_hash_00000000000000000000000000000000000000000000000",
        ))

        # 3. Create new file (not in DB)
        new_file = temp_vault_path / "new.md"
        new_file.write_text("# New file")

        # 4. Deleted file (in DB but not on disk)
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::deleted.md",
            vault_id=vault_id,
            file_path="deleted.md",
            file_name="deleted.md",
            content_hash="deleted_hash_0000000000000000000000000000000000000000",
        ))

        # Detect changes
        changes = await detector.detect_changes("test-vault", temp_vault_path)

        assert len(changes.added) == 1
        assert len(changes.modified) == 1
        assert len(changes.deleted) == 1
        assert changes.unchanged == 1


class TestGetFileHash:
    """Tests for get_file_hash method."""

    @pytest.mark.asyncio
    async def test_get_hash_existing_file(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
    ):
        """Test getting hash for existing file."""
        doc_repo = SQLiteDocumentRepository(manager_with_schema)
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="abc123def456" + "0" * 52,
        ))

        hash_val = await detector.get_file_hash("test-vault", "note.md")
        assert hash_val == "abc123def456" + "0" * 52

    @pytest.mark.asyncio
    async def test_get_hash_nonexistent_file(
        self, detector: ChangeDetector
    ):
        """Test getting hash for nonexistent file."""
        hash_val = await detector.get_file_hash("test-vault", "nonexistent.md")
        assert hash_val is None

    @pytest.mark.asyncio
    async def test_get_hash_nonexistent_vault(
        self, detector: ChangeDetector
    ):
        """Test getting hash for nonexistent vault."""
        hash_val = await detector.get_file_hash("nonexistent-vault", "note.md")
        assert hash_val is None


class TestIsFileChanged:
    """Tests for is_file_changed method."""

    @pytest.mark.asyncio
    async def test_new_file_is_changed(
        self,
        detector: ChangeDetector,
        temp_vault_path: Path,
    ):
        """Test that new file is marked as changed."""
        file_path = temp_vault_path / "new.md"
        file_path.write_text("# New file")

        is_changed = await detector.is_file_changed(
            "test-vault", temp_vault_path, Path("new.md")
        )
        assert is_changed is True

    @pytest.mark.asyncio
    async def test_unchanged_file(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test that unchanged file is not marked as changed."""
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Note")
        content_hash = ChangeDetector.compute_content_hash(file_path)

        doc_repo = SQLiteDocumentRepository(manager_with_schema)
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash=content_hash,
        ))

        is_changed = await detector.is_file_changed(
            "test-vault", temp_vault_path, Path("note.md")
        )
        assert is_changed is False

    @pytest.mark.asyncio
    async def test_modified_file_is_changed(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test that modified file is marked as changed."""
        file_path = temp_vault_path / "note.md"
        file_path.write_text("# Modified content")

        doc_repo = SQLiteDocumentRepository(manager_with_schema)
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::note.md",
            vault_id=vault_id,
            file_path="note.md",
            file_name="note.md",
            content_hash="old_hash_00000000000000000000000000000000000000000000000",
        ))

        is_changed = await detector.is_file_changed(
            "test-vault", temp_vault_path, Path("note.md")
        )
        assert is_changed is True

    @pytest.mark.asyncio
    async def test_file_not_found_raises(
        self,
        detector: ChangeDetector,
        temp_vault_path: Path,
    ):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            await detector.is_file_changed(
                "test-vault", temp_vault_path, Path("nonexistent.md")
            )


class TestGetStats:
    """Tests for get_stats method."""

    @pytest.mark.asyncio
    async def test_stats_nonexistent_vault(self, detector: ChangeDetector):
        """Test stats for nonexistent vault."""
        stats = await detector.get_stats("nonexistent-vault")
        assert stats["total_files"] == 0
        assert stats["total_chunks"] == 0

    @pytest.mark.asyncio
    async def test_stats_existing_vault(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
    ):
        """Test stats for existing vault with documents."""
        doc_repo = SQLiteDocumentRepository(manager_with_schema)

        # Create documents with chunk counts
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::note1.md",
            vault_id=vault_id,
            file_path="note1.md",
            file_name="note1.md",
            content_hash="hash1" + "0" * 59,
            chunk_count=5,
        ))
        await doc_repo.create(SQLiteDocument(
            document_id="test-vault::note2.md",
            vault_id=vault_id,
            file_path="note2.md",
            file_name="note2.md",
            content_hash="hash2" + "0" * 59,
            chunk_count=3,
        ))

        stats = await detector.get_stats("test-vault")
        assert stats["total_files"] == 2
        assert stats["total_chunks"] == 8


class TestCustomFileFilter:
    """Tests for custom file filter."""

    @pytest.mark.asyncio
    async def test_custom_filter_includes_txt(
        self,
        manager_with_schema: SQLiteManager,
        temp_vault_path: Path,
    ):
        """Test custom filter that includes .txt files."""
        def custom_filter(path: Path) -> bool:
            return path.suffix.lower() in [".md", ".txt"]

        detector = ChangeDetector(manager_with_schema, file_filter=custom_filter)

        (temp_vault_path / "note.md").write_text("# Note")
        (temp_vault_path / "readme.txt").write_text("readme")
        (temp_vault_path / "data.json").write_text("{}")

        changes = await detector.detect_changes("vault", temp_vault_path)

        assert len(changes.added) == 2
        names = {p.name for p in changes.added}
        assert "note.md" in names
        assert "readme.txt" in names
        assert "data.json" not in names


class TestPerformance:
    """Performance tests for change detection."""

    @pytest.mark.asyncio
    async def test_scan_many_files(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test scanning many files."""
        # Create 100 files
        for i in range(100):
            (temp_vault_path / f"note_{i:03d}.md").write_text(f"# Note {i}")

        changes = await detector.detect_changes("vault", temp_vault_path)

        assert len(changes.added) == 100
        assert changes.scan_time_ms < 5000  # Should be fast

    @pytest.mark.asyncio
    async def test_compare_many_files(
        self,
        manager_with_schema: SQLiteManager,
        detector: ChangeDetector,
        vault_id: int,
        temp_vault_path: Path,
    ):
        """Test comparing many files with database."""
        doc_repo = SQLiteDocumentRepository(manager_with_schema)

        # Create 100 files and store them
        for i in range(100):
            file_path = temp_vault_path / f"note_{i:03d}.md"
            file_path.write_text(f"# Note {i}")
            content_hash = ChangeDetector.compute_content_hash(file_path)

            await doc_repo.create(SQLiteDocument(
                document_id=f"test-vault::note_{i:03d}.md",
                vault_id=vault_id,
                file_path=f"note_{i:03d}.md",
                file_name=f"note_{i:03d}.md",
                content_hash=content_hash,
            ))

        # Detect changes - all should be unchanged
        changes = await detector.detect_changes("test-vault", temp_vault_path)

        assert changes.added == []
        assert changes.modified == []
        assert changes.deleted == []
        assert changes.unchanged == 100
        assert changes.compare_time_ms < 5000  # Should be fast


class TestEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_invalid_vault_path(self, detector: ChangeDetector, tmp_path: Path):
        """Test with invalid vault path - returns empty ChangeSet."""
        # Non-existent path returns empty ChangeSet (no ValueError)
        changes = await detector.detect_changes("vault", tmp_path / "nonexistent")
        assert not changes.has_changes
        assert changes.added == []
        assert changes.modified == []
        assert changes.deleted == []

    @pytest.mark.asyncio
    async def test_file_as_vault_path(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test with file instead of directory."""
        file_path = temp_vault_path / "file.md"
        file_path.write_text("content")

        with pytest.raises(ValueError):
            await detector.detect_changes("vault", file_path)

    @pytest.mark.asyncio
    async def test_unicode_filenames(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test with unicode filenames."""
        (temp_vault_path / "заметка.md").write_text("# Заметка")
        (temp_vault_path / "笔记.md").write_text("# 笔记")

        changes = await detector.detect_changes("vault", temp_vault_path)

        assert len(changes.added) == 2

    @pytest.mark.asyncio
    async def test_deeply_nested_files(
        self, detector: ChangeDetector, temp_vault_path: Path
    ):
        """Test with deeply nested files."""
        deep_path = temp_vault_path / "a" / "b" / "c" / "d" / "e"
        deep_path.mkdir(parents=True)
        (deep_path / "deep.md").write_text("# Deep")

        changes = await detector.detect_changes("vault", temp_vault_path)

        assert len(changes.added) == 1
        assert "a/b/c/d/e/deep.md" in str(changes.added[0])
