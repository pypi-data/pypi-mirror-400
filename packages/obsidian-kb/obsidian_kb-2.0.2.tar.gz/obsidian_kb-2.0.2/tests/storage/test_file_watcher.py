"""Tests for FileWatcher."""

import asyncio
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from obsidian_kb.storage.file_watcher import (
    DebouncedChanges,
    FileChange,
    FileChangeType,
    FileWatcher,
    VaultEventHandler,
)


@pytest.fixture
def temp_vault_path(tmp_path: Path) -> Path:
    """Create temporary vault directory."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir(parents=True)
    return vault_path


class TestFileChangeType:
    """Tests for FileChangeType enum."""

    def test_change_types_exist(self):
        """Test that all change types exist."""
        assert FileChangeType.CREATED.value == "created"
        assert FileChangeType.MODIFIED.value == "modified"
        assert FileChangeType.DELETED.value == "deleted"
        assert FileChangeType.MOVED.value == "moved"


class TestFileChange:
    """Tests for FileChange dataclass."""

    def test_create_file_change(self):
        """Test creating FileChange."""
        change = FileChange(
            change_type=FileChangeType.CREATED,
            path=Path("note.md"),
        )
        assert change.change_type == FileChangeType.CREATED
        assert change.path == Path("note.md")
        assert change.timestamp is not None
        assert change.old_path is None

    def test_moved_file_change(self):
        """Test FileChange for moved file."""
        change = FileChange(
            change_type=FileChangeType.MOVED,
            path=Path("new/note.md"),
            old_path=Path("old/note.md"),
        )
        assert change.old_path == Path("old/note.md")


class TestDebouncedChanges:
    """Tests for DebouncedChanges dataclass."""

    def test_empty_changes(self):
        """Test empty DebouncedChanges."""
        changes = DebouncedChanges()
        assert changes.is_empty() is True
        assert len(changes.created) == 0
        assert len(changes.modified) == 0
        assert len(changes.deleted) == 0
        assert len(changes.moved) == 0

    def test_non_empty_changes(self):
        """Test non-empty DebouncedChanges."""
        changes = DebouncedChanges(
            created={Path("new.md")},
            modified={Path("changed.md")},
        )
        assert changes.is_empty() is False

    def test_clear_changes(self):
        """Test clearing DebouncedChanges."""
        changes = DebouncedChanges(
            created={Path("a.md")},
            modified={Path("b.md")},
            deleted={Path("c.md")},
            moved={Path("old.md"): Path("new.md")},
        )
        changes.clear()
        assert changes.is_empty() is True

    def test_repr(self):
        """Test string representation."""
        changes = DebouncedChanges(
            created={Path("a.md"), Path("b.md")},
            modified={Path("c.md")},
        )
        repr_str = repr(changes)
        assert "created=2" in repr_str
        assert "modified=1" in repr_str


class TestVaultEventHandler:
    """Tests for VaultEventHandler."""

    def test_init(self, temp_vault_path: Path):
        """Test initialization."""
        handler = VaultEventHandler(
            vault_name="test-vault",
            vault_path=temp_vault_path,
            debounce_seconds=1.0,
        )
        assert handler.vault_name == "test-vault"
        assert handler.vault_path == temp_vault_path.resolve()
        assert handler.debounce_seconds == 1.0

    def test_default_filter_markdown_only(self, temp_vault_path: Path):
        """Test default filter only accepts markdown files."""
        handler = VaultEventHandler(
            vault_name="test",
            vault_path=temp_vault_path,
        )

        assert handler._default_filter(Path("note.md")) is True
        assert handler._default_filter(Path("note.MD")) is True
        assert handler._default_filter(Path("data.json")) is False
        assert handler._default_filter(Path("image.png")) is False

    def test_default_filter_ignores_hidden(self, temp_vault_path: Path):
        """Test default filter ignores hidden files."""
        handler = VaultEventHandler(
            vault_name="test",
            vault_path=temp_vault_path,
        )

        assert handler._default_filter(Path(".hidden.md")) is False
        assert handler._default_filter(Path(".obsidian/note.md")) is False

    def test_custom_filter(self, temp_vault_path: Path):
        """Test custom file filter."""
        def custom_filter(path: Path) -> bool:
            return path.suffix in [".md", ".txt"]

        handler = VaultEventHandler(
            vault_name="test",
            vault_path=temp_vault_path,
            file_filter=custom_filter,
        )

        # Note: should_process also checks if path is within vault
        (temp_vault_path / "note.txt").touch()

        assert handler._should_process(str(temp_vault_path / "note.md")) is True
        assert handler._should_process(str(temp_vault_path / "note.txt")) is True
        assert handler._should_process(str(temp_vault_path / "note.json")) is False

    def test_get_relative_path(self, temp_vault_path: Path):
        """Test getting relative path."""
        handler = VaultEventHandler(
            vault_name="test",
            vault_path=temp_vault_path,
        )

        abs_path = str(temp_vault_path / "subdir" / "note.md")
        rel_path = handler._get_relative_path(abs_path)

        assert rel_path == Path("subdir/note.md")

    def test_should_process_outside_vault(self, temp_vault_path: Path, tmp_path: Path):
        """Test that paths outside vault are rejected."""
        handler = VaultEventHandler(
            vault_name="test",
            vault_path=temp_vault_path,
        )

        outside_path = str(tmp_path / "outside.md")
        assert handler._should_process(outside_path) is False


class TestVaultEventHandlerEvents:
    """Tests for VaultEventHandler event processing."""

    @pytest.fixture
    def handler(self, temp_vault_path: Path):
        """Create handler for tests."""
        handler = VaultEventHandler(
            vault_name="test-vault",
            vault_path=temp_vault_path,
            debounce_seconds=0.1,  # Short debounce for tests
        )
        # Create callback mock
        callback = AsyncMock()
        loop = asyncio.new_event_loop()
        handler.set_callback(callback, loop)
        return handler, callback, loop

    def test_on_created_accumulates(self, handler, temp_vault_path: Path):
        """Test created events accumulate."""
        h, callback, loop = handler

        # Create mock event
        event = MagicMock()
        event.is_directory = False
        event.src_path = str(temp_vault_path / "new.md")

        h.on_created(event)

        assert Path("new.md") in h._changes.created

    def test_on_modified_accumulates(self, handler, temp_vault_path: Path):
        """Test modified events accumulate."""
        h, callback, loop = handler

        event = MagicMock()
        event.is_directory = False
        event.src_path = str(temp_vault_path / "changed.md")

        h.on_modified(event)

        assert Path("changed.md") in h._changes.modified

    def test_on_deleted_accumulates(self, handler, temp_vault_path: Path):
        """Test deleted events accumulate."""
        h, callback, loop = handler

        event = MagicMock()
        event.is_directory = False
        event.src_path = str(temp_vault_path / "removed.md")

        h.on_deleted(event)

        assert Path("removed.md") in h._changes.deleted

    def test_on_modified_not_in_created(self, handler, temp_vault_path: Path):
        """Test modified doesn't add if already in created."""
        h, callback, loop = handler

        path = str(temp_vault_path / "new.md")

        # Create first
        event1 = MagicMock()
        event1.is_directory = False
        event1.src_path = path
        h.on_created(event1)

        # Then modify
        event2 = MagicMock()
        event2.is_directory = False
        event2.src_path = path
        h.on_modified(event2)

        assert Path("new.md") in h._changes.created
        assert Path("new.md") not in h._changes.modified

    def test_on_deleted_removes_from_created(self, handler, temp_vault_path: Path):
        """Test deleted removes from created set."""
        h, callback, loop = handler

        path = str(temp_vault_path / "temp.md")

        # Create first
        event1 = MagicMock()
        event1.is_directory = False
        event1.src_path = path
        h.on_created(event1)

        # Then delete
        event2 = MagicMock()
        event2.is_directory = False
        event2.src_path = path
        h.on_deleted(event2)

        assert Path("temp.md") not in h._changes.created
        assert Path("temp.md") in h._changes.deleted

    def test_directory_events_ignored(self, handler, temp_vault_path: Path):
        """Test directory events are ignored."""
        h, callback, loop = handler

        event = MagicMock()
        event.is_directory = True
        event.src_path = str(temp_vault_path / "subdir")

        h.on_created(event)
        h.on_modified(event)
        h.on_deleted(event)

        assert h._changes.is_empty()

    def test_on_moved_within_vault(self, handler, temp_vault_path: Path):
        """Test moved event within vault."""
        h, callback, loop = handler

        from watchdog.events import FileMovedEvent

        event = FileMovedEvent(
            src_path=str(temp_vault_path / "old.md"),
            dest_path=str(temp_vault_path / "new.md"),
        )

        h.on_moved(event)

        assert Path("old.md") in h._changes.moved
        assert h._changes.moved[Path("old.md")] == Path("new.md")

    def test_on_moved_out_of_vault(self, handler, temp_vault_path: Path, tmp_path: Path):
        """Test moved event out of vault becomes deleted."""
        h, callback, loop = handler

        from watchdog.events import FileMovedEvent

        event = FileMovedEvent(
            src_path=str(temp_vault_path / "note.md"),
            dest_path=str(tmp_path / "outside.md"),
        )

        h.on_moved(event)

        assert Path("note.md") in h._changes.deleted

    def test_on_moved_into_vault(self, handler, temp_vault_path: Path, tmp_path: Path):
        """Test moved event into vault becomes created."""
        h, callback, loop = handler

        from watchdog.events import FileMovedEvent

        # Create file outside vault first (so filter passes for destination)
        (temp_vault_path / "imported.md").touch()

        event = FileMovedEvent(
            src_path=str(tmp_path / "outside.md"),
            dest_path=str(temp_vault_path / "imported.md"),
        )

        h.on_moved(event)

        assert Path("imported.md") in h._changes.created


class TestFileWatcher:
    """Tests for FileWatcher class."""

    def test_init_default_settings(self):
        """Test initialization with default settings."""
        watcher = FileWatcher()
        assert watcher._debounce_seconds == 1.0
        assert watcher._file_filter is None
        assert watcher.is_running is False

    def test_init_custom_settings(self):
        """Test initialization with custom settings."""
        def custom_filter(path: Path) -> bool:
            return path.suffix == ".md"

        watcher = FileWatcher(
            debounce_seconds=2.0,
            file_filter=custom_filter,
        )
        assert watcher._debounce_seconds == 2.0
        assert watcher._file_filter == custom_filter

    @pytest.mark.asyncio
    async def test_watch_vault(self, temp_vault_path: Path):
        """Test starting to watch a vault."""
        watcher = FileWatcher(debounce_seconds=0.1)

        callback = AsyncMock()
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        assert watcher.is_watching("test-vault")
        assert watcher.is_running

        await watcher.stop_all()

    @pytest.mark.asyncio
    async def test_watch_invalid_path(self, tmp_path: Path):
        """Test watching invalid path raises error."""
        watcher = FileWatcher()
        callback = AsyncMock()

        with pytest.raises(ValueError):
            await watcher.watch_vault("test", tmp_path / "nonexistent", callback)

    @pytest.mark.asyncio
    async def test_watch_file_instead_of_dir(self, temp_vault_path: Path):
        """Test watching a file instead of directory raises error."""
        file_path = temp_vault_path / "file.md"
        file_path.touch()

        watcher = FileWatcher()
        callback = AsyncMock()

        with pytest.raises(ValueError):
            await watcher.watch_vault("test", file_path, callback)

    @pytest.mark.asyncio
    async def test_watch_duplicate_vault(self, temp_vault_path: Path):
        """Test watching same vault twice raises error."""
        watcher = FileWatcher(debounce_seconds=0.1)
        callback = AsyncMock()

        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        with pytest.raises(RuntimeError):
            await watcher.watch_vault("test-vault", temp_vault_path, callback)

        await watcher.stop_all()

    @pytest.mark.asyncio
    async def test_stop_vault(self, temp_vault_path: Path):
        """Test stopping a specific vault."""
        watcher = FileWatcher(debounce_seconds=0.1)
        callback = AsyncMock()

        await watcher.watch_vault("test-vault", temp_vault_path, callback)
        await watcher.stop_vault("test-vault")

        assert not watcher.is_watching("test-vault")

        await watcher.stop_all()

    @pytest.mark.asyncio
    async def test_stop_nonexistent_vault(self):
        """Test stopping nonexistent vault does not error."""
        watcher = FileWatcher()
        await watcher.stop_vault("nonexistent")  # Should not raise

    @pytest.mark.asyncio
    async def test_stop_all(self, temp_vault_path: Path):
        """Test stopping all watchers."""
        vault1 = temp_vault_path / "vault1"
        vault2 = temp_vault_path / "vault2"
        vault1.mkdir()
        vault2.mkdir()

        watcher = FileWatcher(debounce_seconds=0.1)
        callback = AsyncMock()

        await watcher.watch_vault("vault1", vault1, callback)
        await watcher.watch_vault("vault2", vault2, callback)

        await watcher.stop_all()

        assert not watcher.is_watching("vault1")
        assert not watcher.is_watching("vault2")
        assert not watcher.is_running

    @pytest.mark.asyncio
    async def test_get_watched_vaults(self, temp_vault_path: Path):
        """Test getting list of watched vaults."""
        vault1 = temp_vault_path / "vault1"
        vault2 = temp_vault_path / "vault2"
        vault1.mkdir()
        vault2.mkdir()

        watcher = FileWatcher(debounce_seconds=0.1)
        callback = AsyncMock()

        await watcher.watch_vault("vault1", vault1, callback)
        await watcher.watch_vault("vault2", vault2, callback)

        watched = watcher.get_watched_vaults()

        assert "vault1" in watched
        assert "vault2" in watched

        await watcher.stop_all()


class TestFileWatcherIntegration:
    """Integration tests for FileWatcher with real file operations."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_detect_file_creation(self, temp_vault_path: Path):
        """Test detecting file creation."""
        callback_called = asyncio.Event()
        received_changes = []

        async def callback(vault_name: str, changes: DebouncedChanges):
            received_changes.append((vault_name, changes))
            callback_called.set()

        watcher = FileWatcher(debounce_seconds=0.2)
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        try:
            # Create file
            (temp_vault_path / "new_note.md").write_text("# New Note")

            # Wait for callback
            await asyncio.wait_for(callback_called.wait(), timeout=5.0)

            assert len(received_changes) >= 1
            vault_name, changes = received_changes[-1]
            assert vault_name == "test-vault"
            # File may appear as created or modified depending on timing
            assert Path("new_note.md") in changes.created or Path("new_note.md") in changes.modified

        finally:
            await watcher.stop_all()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_detect_file_modification(self, temp_vault_path: Path):
        """Test detecting file modification."""
        # Create file first
        note_path = temp_vault_path / "note.md"
        note_path.write_text("# Original")

        callback_called = asyncio.Event()
        received_changes = []

        async def callback(vault_name: str, changes: DebouncedChanges):
            received_changes.append(changes)
            callback_called.set()

        watcher = FileWatcher(debounce_seconds=0.2)
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        try:
            # Wait a bit for watcher to start
            await asyncio.sleep(0.1)

            # Modify file
            note_path.write_text("# Modified")

            # Wait for callback
            await asyncio.wait_for(callback_called.wait(), timeout=5.0)

            assert len(received_changes) >= 1
            changes = received_changes[-1]
            assert Path("note.md") in changes.modified or Path("note.md") in changes.created

        finally:
            await watcher.stop_all()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_detect_file_deletion(self, temp_vault_path: Path):
        """Test detecting file deletion."""
        # Create file first
        note_path = temp_vault_path / "to_delete.md"
        note_path.write_text("# To Delete")

        callback_called = asyncio.Event()
        received_changes = []

        async def callback(vault_name: str, changes: DebouncedChanges):
            received_changes.append(changes)
            callback_called.set()

        watcher = FileWatcher(debounce_seconds=0.2)
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        try:
            # Wait a bit for watcher to start
            await asyncio.sleep(0.1)

            # Delete file
            note_path.unlink()

            # Wait for callback
            await asyncio.wait_for(callback_called.wait(), timeout=5.0)

            assert len(received_changes) >= 1
            changes = received_changes[-1]
            assert Path("to_delete.md") in changes.deleted

        finally:
            await watcher.stop_all()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_debounce_groups_changes(self, temp_vault_path: Path):
        """Test that rapid changes are debounced into single callback."""
        callback_count = 0
        all_changes = []

        async def callback(vault_name: str, changes: DebouncedChanges):
            nonlocal callback_count
            callback_count += 1
            all_changes.append(changes)

        watcher = FileWatcher(debounce_seconds=0.5)
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        try:
            # Create multiple files rapidly
            for i in range(5):
                (temp_vault_path / f"note_{i}.md").write_text(f"# Note {i}")
                await asyncio.sleep(0.05)  # Very short delay

            # Wait for debounce + processing
            await asyncio.sleep(1.0)

            # Should have been grouped into fewer callbacks
            assert callback_count <= 3  # Debounce should group some together

        finally:
            await watcher.stop_all()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_ignores_non_markdown_files(self, temp_vault_path: Path):
        """Test that non-markdown files are ignored."""
        received_changes = []

        async def callback(vault_name: str, changes: DebouncedChanges):
            received_changes.append(changes)

        watcher = FileWatcher(debounce_seconds=0.2)
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        try:
            # Create non-markdown files
            (temp_vault_path / "data.json").write_text("{}")
            (temp_vault_path / "image.png").write_bytes(b"PNG")

            # Wait a bit
            await asyncio.sleep(0.5)

            # Should not have received any changes
            for changes in received_changes:
                assert Path("data.json") not in changes.created
                assert Path("image.png") not in changes.created

        finally:
            await watcher.stop_all()

    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_nested_directory_changes(self, temp_vault_path: Path):
        """Test detecting changes in nested directories."""
        callback_called = asyncio.Event()
        received_changes = []

        async def callback(vault_name: str, changes: DebouncedChanges):
            received_changes.append(changes)
            callback_called.set()

        watcher = FileWatcher(debounce_seconds=0.2)
        await watcher.watch_vault("test-vault", temp_vault_path, callback)

        try:
            # Create nested directory and file
            nested_dir = temp_vault_path / "subdir" / "deep"
            nested_dir.mkdir(parents=True)
            (nested_dir / "nested_note.md").write_text("# Nested")

            # Wait for callback
            await asyncio.wait_for(callback_called.wait(), timeout=5.0)

            assert len(received_changes) >= 1
            changes = received_changes[-1]
            # Check if nested path is detected
            created_paths = {str(p) for p in changes.created}
            assert "subdir/deep/nested_note.md" in created_paths or any(
                "nested_note.md" in str(p) for p in changes.created
            )

        finally:
            await watcher.stop_all()
