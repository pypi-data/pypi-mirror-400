"""File watcher for real-time change detection.

This module provides a file system watcher using watchdog
to trigger incremental indexing when files change.
"""

import asyncio
import logging
import threading
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class FileChangeType(Enum):
    """Type of file change."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileChange:
    """Represents a file change event.

    Attributes:
        change_type: Type of change (created, modified, deleted, moved)
        path: Path to the changed file (relative to vault)
        timestamp: When the change occurred
        old_path: Original path for moved files
    """

    change_type: FileChangeType
    path: Path
    timestamp: datetime = field(default_factory=datetime.now)
    old_path: Path | None = None


@dataclass
class DebouncedChanges:
    """Accumulated changes during debounce period.

    Attributes:
        created: Set of created file paths
        modified: Set of modified file paths
        deleted: Set of deleted file paths
        moved: Dict mapping old path to new path
    """

    created: set[Path] = field(default_factory=set)
    modified: set[Path] = field(default_factory=set)
    deleted: set[Path] = field(default_factory=set)
    moved: dict[Path, Path] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """Check if there are no changes."""
        return not (self.created or self.modified or self.deleted or self.moved)

    def clear(self) -> None:
        """Clear all accumulated changes."""
        self.created.clear()
        self.modified.clear()
        self.deleted.clear()
        self.moved.clear()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DebouncedChanges(created={len(self.created)}, "
            f"modified={len(self.modified)}, deleted={len(self.deleted)}, "
            f"moved={len(self.moved)})"
        )


# Type alias for change handler callback
ChangeHandler = Callable[[str, DebouncedChanges], Coroutine[Any, Any, None]]


class VaultEventHandler(FileSystemEventHandler):
    """File system event handler for a vault.

    Filters events to only markdown files and accumulates changes
    for debouncing before triggering the callback.
    """

    def __init__(
        self,
        vault_name: str,
        vault_path: Path,
        debounce_seconds: float = 1.0,
        file_filter: Callable[[Path], bool] | None = None,
    ) -> None:
        """Initialize event handler.

        Args:
            vault_name: Name of the vault
            vault_path: Root path of the vault
            debounce_seconds: Time to wait for more changes before triggering
            file_filter: Optional filter function (returns True to include)
        """
        super().__init__()
        self.vault_name = vault_name
        self.vault_path = vault_path.resolve()
        self.debounce_seconds = debounce_seconds
        self._file_filter = file_filter or self._default_filter
        self._changes = DebouncedChanges()
        self._lock = threading.Lock()
        self._debounce_timer: threading.Timer | None = None
        self._change_callback: ChangeHandler | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    @staticmethod
    def _default_filter(path: Path) -> bool:
        """Default filter for markdown files.

        Args:
            path: Path to check

        Returns:
            True if file should be watched
        """
        # Only watch .md files
        if path.suffix.lower() != ".md":
            return False

        # Skip hidden files and directories
        if any(part.startswith(".") for part in path.parts):
            return False

        return True

    def set_callback(
        self,
        callback: ChangeHandler,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        """Set the change callback.

        Args:
            callback: Async function to call when changes are detected
            loop: Event loop to schedule callback on
        """
        self._change_callback = callback
        self._loop = loop

    def _get_relative_path(self, path: str) -> Path:
        """Convert absolute path to relative path.

        Args:
            path: Absolute path string

        Returns:
            Path relative to vault root
        """
        abs_path = Path(path).resolve()
        return abs_path.relative_to(self.vault_path)

    def _should_process(self, path: str) -> bool:
        """Check if path should be processed.

        Args:
            path: Path to check

        Returns:
            True if path should be processed
        """
        try:
            abs_path = Path(path).resolve()
            # Must be within vault
            abs_path.relative_to(self.vault_path)
            return self._file_filter(abs_path)
        except ValueError:
            return False

    def _schedule_callback(self) -> None:
        """Schedule debounced callback."""
        if self._debounce_timer is not None:
            self._debounce_timer.cancel()

        self._debounce_timer = threading.Timer(
            self.debounce_seconds,
            self._trigger_callback,
        )
        self._debounce_timer.start()

    def _trigger_callback(self) -> None:
        """Trigger the callback with accumulated changes."""
        with self._lock:
            if self._changes.is_empty():
                return

            # Copy changes and clear
            changes = DebouncedChanges(
                created=self._changes.created.copy(),
                modified=self._changes.modified.copy(),
                deleted=self._changes.deleted.copy(),
                moved=self._changes.moved.copy(),
            )
            self._changes.clear()

        if self._change_callback and self._loop:
            # Schedule async callback on event loop
            asyncio.run_coroutine_threadsafe(
                self._change_callback(self.vault_name, changes),
                self._loop,
            )

            logger.info(
                f"Triggered change callback for vault '{self.vault_name}': {changes}"
            )

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file created event."""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        path = self._get_relative_path(event.src_path)

        with self._lock:
            # If file was in deleted, it's now modified (recreated)
            if path in self._changes.deleted:
                self._changes.deleted.discard(path)
                self._changes.modified.add(path)
            else:
                self._changes.created.add(path)

        logger.debug(f"File created: {path}")
        self._schedule_callback()

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modified event."""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        path = self._get_relative_path(event.src_path)

        with self._lock:
            # Don't add to modified if already in created
            if path not in self._changes.created:
                self._changes.modified.add(path)

        logger.debug(f"File modified: {path}")
        self._schedule_callback()

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deleted event."""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        path = self._get_relative_path(event.src_path)

        with self._lock:
            # Remove from created/modified if present
            self._changes.created.discard(path)
            self._changes.modified.discard(path)
            # Add to deleted
            self._changes.deleted.add(path)

        logger.debug(f"File deleted: {path}")
        self._schedule_callback()

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file moved event."""
        if event.is_directory:
            return

        if not isinstance(event, FileMovedEvent):
            return

        src_valid = self._should_process(event.src_path)
        dst_valid = self._should_process(event.dest_path)

        with self._lock:
            if src_valid and dst_valid:
                # Move within vault - track as moved
                src_path = self._get_relative_path(event.src_path)
                dst_path = self._get_relative_path(event.dest_path)

                # Remove source from any existing sets
                self._changes.created.discard(src_path)
                self._changes.modified.discard(src_path)

                # Track as moved
                self._changes.moved[src_path] = dst_path

            elif src_valid and not dst_valid:
                # Moved out of vault - treat as deleted
                src_path = self._get_relative_path(event.src_path)
                self._changes.created.discard(src_path)
                self._changes.modified.discard(src_path)
                self._changes.deleted.add(src_path)

            elif not src_valid and dst_valid:
                # Moved into vault - treat as created
                dst_path = self._get_relative_path(event.dest_path)
                self._changes.created.add(dst_path)

        if src_valid or dst_valid:
            logger.debug(f"File moved: {event.src_path} -> {event.dest_path}")
            self._schedule_callback()


class FileWatcher:
    """File system watcher for vaults.

    Monitors one or more vault directories for file changes
    and triggers callbacks with debounced change sets.

    Usage:
        watcher = FileWatcher(debounce_seconds=2.0)

        async def on_changes(vault_name: str, changes: DebouncedChanges):
            print(f"Changes in {vault_name}: {changes}")

        # Start watching
        await watcher.watch_vault(
            "my-vault",
            Path("/path/to/vault"),
            on_changes,
        )

        # Later, stop watching
        await watcher.stop_vault("my-vault")

        # Or stop all
        await watcher.stop_all()
    """

    def __init__(
        self,
        debounce_seconds: float = 1.0,
        file_filter: Callable[[Path], bool] | None = None,
    ) -> None:
        """Initialize file watcher.

        Args:
            debounce_seconds: Time to wait for more changes before triggering
            file_filter: Optional filter function for files
        """
        self._debounce_seconds = debounce_seconds
        self._file_filter = file_filter
        self._observer = Observer()
        self._handlers: dict[str, VaultEventHandler] = {}
        self._watches: dict[str, Any] = {}  # watchdog watch objects
        self._started = False

    async def watch_vault(
        self,
        vault_name: str,
        vault_path: Path,
        callback: ChangeHandler,
    ) -> None:
        """Start watching a vault directory.

        Args:
            vault_name: Name of the vault
            vault_path: Path to vault directory
            callback: Async callback for change notifications

        Raises:
            ValueError: If vault_path is not a directory
            RuntimeError: If vault is already being watched
        """
        if not vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault_path}")

        if vault_name in self._handlers:
            raise RuntimeError(f"Vault '{vault_name}' is already being watched")

        # Create event handler
        handler = VaultEventHandler(
            vault_name=vault_name,
            vault_path=vault_path,
            debounce_seconds=self._debounce_seconds,
            file_filter=self._file_filter,
        )

        # Set callback with current event loop
        loop = asyncio.get_event_loop()
        handler.set_callback(callback, loop)

        # Schedule watch on observer
        watch = self._observer.schedule(
            handler,
            str(vault_path),
            recursive=True,
        )

        self._handlers[vault_name] = handler
        self._watches[vault_name] = watch

        # Start observer if not already running
        if not self._started:
            self._observer.start()
            self._started = True

        logger.info(
            f"Started watching vault '{vault_name}' at {vault_path} "
            f"(debounce={self._debounce_seconds}s)"
        )

    async def stop_vault(self, vault_name: str) -> None:
        """Stop watching a vault.

        Args:
            vault_name: Name of the vault to stop watching
        """
        if vault_name not in self._handlers:
            logger.warning(f"Vault '{vault_name}' is not being watched")
            return

        watch = self._watches.pop(vault_name)
        self._observer.unschedule(watch)

        handler = self._handlers.pop(vault_name)
        if handler._debounce_timer:
            handler._debounce_timer.cancel()

        logger.info(f"Stopped watching vault '{vault_name}'")

    async def stop_all(self) -> None:
        """Stop watching all vaults."""
        # Cancel all debounce timers
        for handler in self._handlers.values():
            if handler._debounce_timer:
                handler._debounce_timer.cancel()

        # Clear handlers and watches
        self._handlers.clear()
        self._watches.clear()

        # Stop observer
        if self._started:
            self._observer.stop()
            self._observer.join(timeout=5.0)
            self._started = False

        logger.info("Stopped all file watchers")

    def is_watching(self, vault_name: str) -> bool:
        """Check if a vault is being watched.

        Args:
            vault_name: Name of the vault

        Returns:
            True if vault is being watched
        """
        return vault_name in self._handlers

    def get_watched_vaults(self) -> list[str]:
        """Get list of watched vault names.

        Returns:
            List of vault names being watched
        """
        return list(self._handlers.keys())

    @property
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._started and self._observer.is_alive()
