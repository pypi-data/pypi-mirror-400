"""Change detector for incremental indexing.

This module provides change detection by comparing content hashes
of files in vault against stored hashes in SQLite or LanceDB.

Phase 2.0.6 - Consolidated ChangeDetector

Supports multiple backends:
- SQLite (primary, recommended): Uses SQLiteManager for metadata storage
- LanceDB (legacy): Uses DocumentRepository for backward compatibility
- Manual: Uses provided indexed_files dict (for tests)
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from obsidian_kb.storage.document_repository import DocumentRepository
    from obsidian_kb.storage.sqlite.manager import SQLiteManager

logger = logging.getLogger(__name__)


@dataclass
class ChangeSet:
    """Result of change detection.

    Attributes:
        added: List of new file paths (files not in database)
        modified: List of modified file paths (hash differs)
        deleted: List of document_ids or file_paths for deleted files
        unchanged: Count of files with no changes
        scan_time_ms: Time taken to scan filesystem in milliseconds
        compare_time_ms: Time taken to compare hashes in milliseconds
    """

    added: list[Path] = field(default_factory=list)
    modified: list[Path] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    unchanged: int = 0
    scan_time_ms: float = 0.0
    compare_time_ms: float = 0.0

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes to process."""
        return bool(self.added or self.modified or self.deleted)

    @property
    def total_to_process(self) -> int:
        """Get total number of files to process (add + modify)."""
        return len(self.added) + len(self.modified)

    @property
    def total_deleted(self) -> int:
        """Get number of deleted files."""
        return len(self.deleted)

    # Backward compatibility aliases
    @property
    def new_files(self) -> list[Path]:
        """Alias for added (backward compatibility)."""
        return self.added

    @property
    def modified_files(self) -> list[Path]:
        """Alias for modified (backward compatibility)."""
        return self.modified

    @property
    def deleted_files(self) -> list[str]:
        """Alias for deleted (backward compatibility)."""
        return self.deleted

    def is_empty(self) -> bool:
        """Check if there are no changes (backward compatibility)."""
        return not self.has_changes

    def __len__(self) -> int:
        """Total number of changes (backward compatibility)."""
        return len(self.added) + len(self.modified) + len(self.deleted)

    def __repr__(self) -> str:
        """String representation of ChangeSet."""
        return (
            f"ChangeSet(added={len(self.added)}, modified={len(self.modified)}, "
            f"deleted={len(self.deleted)}, unchanged={self.unchanged}, "
            f"scan_time_ms={self.scan_time_ms:.1f}, compare_time_ms={self.compare_time_ms:.1f})"
        )


class ChangeDetector:
    """Detects changes in vault files for incremental indexing.

    Compares content hashes of files on disk against stored hashes
    in SQLite or LanceDB to determine which files need reindexing.

    Supports multiple backends:
    - SQLite (primary): Pass sqlite_manager parameter
    - LanceDB (legacy): Pass document_repository parameter
    - Neither: Uses indexed_files parameter in detect_changes()

    Usage with SQLite:
        detector = ChangeDetector(sqlite_manager=manager)
        changes = await detector.detect_changes("my-vault", Path("/path/to/vault"))

    Usage with LanceDB (legacy):
        detector = ChangeDetector(document_repository=repo)
        changes = await detector.detect_changes(
            vault_path=Path("/path/to/vault"),
            vault_name="my-vault",
        )

    Usage with manual indexed_files:
        detector = ChangeDetector()
        changes = await detector.detect_changes(
            vault_path=Path("/path/to/vault"),
            vault_name="my-vault",
            indexed_files={"file.md": "abc123hash"},
        )
    """

    def __init__(
        self,
        sqlite_manager: "SQLiteManager | None" = None,
        document_repository: "DocumentRepository | None" = None,
        file_filter: Callable[[Path], bool] | None = None,
        # Backward compatibility alias
        manager: "SQLiteManager | None" = None,
    ) -> None:
        """Initialize change detector.

        Args:
            sqlite_manager: SQLiteManager instance (primary backend)
            document_repository: DocumentRepository for LanceDB (legacy backend)
            file_filter: Optional function to filter files (returns True to include)
                        Default filters only .md files
            manager: Alias for sqlite_manager (backward compatibility)
        """
        # Handle backward compatibility
        self._manager = sqlite_manager or manager
        self._document_repository = document_repository
        self._file_filter = file_filter or self._default_file_filter

        # Initialize SQLite repos if manager provided
        self._doc_repo = None
        self._vault_repo = None
        if self._manager:
            from obsidian_kb.storage.sqlite.repositories.document import SQLiteDocumentRepository
            from obsidian_kb.storage.sqlite.repositories.vault import VaultRepository
            self._doc_repo = SQLiteDocumentRepository(self._manager)
            self._vault_repo = VaultRepository(self._manager)

    @staticmethod
    def _default_file_filter(path: Path) -> bool:
        """Default filter for markdown files only.

        Args:
            path: File path to check

        Returns:
            True if file should be included (is .md file)
        """
        return path.suffix.lower() == ".md"

    @staticmethod
    def compute_content_hash(file_path: Path) -> str:
        """Compute SHA256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            Hex-encoded SHA256 hash

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def _get_vault_id(self, vault_name: str) -> int | None:
        """Get vault ID by name.

        Args:
            vault_name: Name of the vault

        Returns:
            Vault ID if found, None otherwise
        """
        if self._vault_repo is None:
            return None
        return await self._vault_repo.get_id_by_name(vault_name)

    async def _get_stored_hashes(self, vault_id: int) -> dict[str, str]:
        """Get all stored file_path -> content_hash mappings from SQLite.

        Args:
            vault_id: Database ID of the vault

        Returns:
            Dict mapping file_path to content_hash
        """
        if self._manager is None:
            return {}
        rows = await self._manager.fetch_all(
            "SELECT file_path, content_hash FROM documents WHERE vault_id = ?",
            (vault_id,),
        )
        return {row["file_path"]: row["content_hash"] for row in rows}

    async def _get_stored_document_ids(self, vault_id: int) -> dict[str, str]:
        """Get all stored file_path -> document_id mappings from SQLite.

        Args:
            vault_id: Database ID of the vault

        Returns:
            Dict mapping file_path to document_id
        """
        if self._manager is None:
            return {}
        rows = await self._manager.fetch_all(
            "SELECT file_path, document_id FROM documents WHERE vault_id = ?",
            (vault_id,),
        )
        return {row["file_path"]: row["document_id"] for row in rows}

    async def _load_indexed_files_from_lancedb(self, vault_name: str) -> dict[str, str]:
        """Load indexed files from LanceDB DocumentRepository (legacy).

        Args:
            vault_name: Name of the vault

        Returns:
            Dict mapping file_path to content_hash
        """
        if not self._document_repository:
            return {}

        try:
            # Get all document_ids from vault
            document_ids = await self._document_repository.get_all_document_ids(vault_name)

            if not document_ids:
                return {}

            # Get content_hash from LanceDB documents table
            db_manager = self._document_repository._db_manager
            documents_table = await db_manager._ensure_table(vault_name, "documents")

            def _load_hashes() -> dict[str, str]:
                try:
                    arrow_table = documents_table.to_arrow()
                    if arrow_table.num_rows == 0:
                        return {}

                    # Get file_path and content_hash columns
                    file_paths = arrow_table["file_path"].to_pylist()
                    content_hashes = (
                        arrow_table["content_hash"].to_pylist()
                        if "content_hash" in arrow_table.column_names
                        else [""] * len(file_paths)
                    )

                    # Create dict {file_path: content_hash}
                    indexed_files = {}
                    for file_path, content_hash in zip(file_paths, content_hashes):
                        if file_path:
                            indexed_files[file_path] = content_hash or ""

                    return indexed_files
                except Exception as e:
                    logger.error(f"Error loading indexed files from LanceDB: {e}")
                    return {}

            return await asyncio.to_thread(_load_hashes)
        except Exception as e:
            logger.error(f"Failed to load indexed files from LanceDB: {e}")
            return {}

    def _scan_vault_files(self, vault_path: Path) -> list[Path]:
        """Scan vault directory for files matching filter.

        Args:
            vault_path: Root path of vault

        Returns:
            List of file paths relative to vault_path
        """
        files: list[Path] = []
        for file_path in vault_path.rglob("*"):
            if file_path.is_file() and self._file_filter(file_path):
                # Skip hidden files and directories
                if any(part.startswith(".") for part in file_path.parts):
                    continue
                # Store relative path
                rel_path = file_path.relative_to(vault_path)
                files.append(rel_path)
        return files

    async def detect_changes(
        self,
        vault_name: str | None = None,
        vault_path: Path | None = None,
        indexed_files: dict[str, str] | None = None,
        # Backward compatibility: support positional args in old order
        *,
        _vault_path_positional: Path | None = None,
        _vault_name_positional: str | None = None,
    ) -> ChangeSet:
        """Detect changes between vault files and stored index.

        Compares files on disk with stored hashes in database to identify:
        - Added files: exist on disk but not in database
        - Modified files: exist in both but hash differs
        - Deleted files: exist in database but not on disk
        - Unchanged files: exist in both with same hash

        Supports multiple calling conventions:
        - SQLite mode: detect_changes(vault_name, vault_path)
        - LanceDB mode: detect_changes(vault_path=..., vault_name=..., indexed_files=...)

        Args:
            vault_name: Name of the vault
            vault_path: Path to vault directory
            indexed_files: Optional dict {file_path: content_hash} of already indexed files.
                          If None, loads from SQLite or LanceDB depending on backend.

        Returns:
            ChangeSet with categorized file changes

        Raises:
            ValueError: If vault_path is not a directory
        """
        import time

        # Handle backward compatibility with old (vault_path, vault_name) order
        # New signature: (vault_name, vault_path)
        # Old signature: (vault_path, vault_name, indexed_files)
        if vault_name is not None and isinstance(vault_name, Path):
            # Old calling convention: first arg is vault_path
            vault_path = vault_name
            vault_name = vault_path if isinstance(vault_path, str) else None

        if vault_path is None:
            raise ValueError("vault_path is required")

        if vault_name is None:
            raise ValueError("vault_name is required")

        vault_path = Path(vault_path).resolve()

        if not vault_path.exists():
            logger.warning(f"Vault path does not exist: {vault_path}")
            return ChangeSet()

        if not vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault_path}")

        changes = ChangeSet()

        # Phase 1: Scan filesystem
        scan_start = time.perf_counter()
        disk_files = await asyncio.to_thread(self._scan_vault_files, vault_path)
        disk_file_set = set(disk_files)
        changes.scan_time_ms = (time.perf_counter() - scan_start) * 1000

        logger.debug(f"Scanned {len(disk_files)} files in {changes.scan_time_ms:.1f}ms")

        # Phase 2: Get stored data
        compare_start = time.perf_counter()

        # Determine source of indexed files
        stored_hashes: dict[str, str] = {}
        stored_doc_ids: dict[str, str] = {}

        if indexed_files is not None:
            # Manual mode: use provided indexed_files
            stored_hashes = indexed_files
            # No document IDs in manual mode
        elif self._manager:
            # SQLite mode
            vault_id = await self._get_vault_id(vault_name)
            if vault_id is None:
                # New vault - all files are added
                changes.added = disk_files
                changes.compare_time_ms = (time.perf_counter() - compare_start) * 1000
                logger.info(
                    f"New vault '{vault_name}': {len(changes.added)} files to index"
                )
                return changes

            stored_hashes = await self._get_stored_hashes(vault_id)
            stored_doc_ids = await self._get_stored_document_ids(vault_id)
        elif self._document_repository:
            # LanceDB mode (legacy)
            stored_hashes = await self._load_indexed_files_from_lancedb(vault_name)
        else:
            # No backend - all files are new
            changes.added = disk_files
            changes.compare_time_ms = (time.perf_counter() - compare_start) * 1000
            logger.info(
                f"No backend configured for '{vault_name}': {len(changes.added)} files to index"
            )
            return changes

        stored_paths = set(stored_hashes.keys())

        # Phase 3: Categorize changes
        for rel_path in disk_files:
            path_str = str(rel_path)
            full_path = vault_path / rel_path

            if path_str not in stored_hashes:
                # New file
                changes.added.append(rel_path)
            else:
                # Existing file - check hash
                try:
                    current_hash = await asyncio.to_thread(
                        self.compute_content_hash, full_path
                    )
                    if current_hash != stored_hashes[path_str]:
                        changes.modified.append(rel_path)
                    else:
                        changes.unchanged += 1
                except (FileNotFoundError, IOError) as e:
                    logger.warning(f"Could not read file {full_path}: {e}")
                    # Treat as deleted since we can't read it
                    if path_str in stored_doc_ids:
                        changes.deleted.append(stored_doc_ids[path_str])
                    else:
                        changes.deleted.append(path_str)

        # Find deleted files (in DB but not on disk)
        for path_str in stored_paths:
            rel_path = Path(path_str)
            if rel_path not in disk_file_set:
                if path_str in stored_doc_ids:
                    changes.deleted.append(stored_doc_ids[path_str])
                else:
                    changes.deleted.append(path_str)

        changes.compare_time_ms = (time.perf_counter() - compare_start) * 1000

        logger.info(
            f"Change detection for '{vault_name}': "
            f"added={len(changes.added)}, modified={len(changes.modified)}, "
            f"deleted={len(changes.deleted)}, unchanged={changes.unchanged} "
            f"(scan={changes.scan_time_ms:.1f}ms, compare={changes.compare_time_ms:.1f}ms)"
        )

        return changes

    async def get_file_hash(
        self,
        vault_name: str,
        file_path: str,
    ) -> str | None:
        """Get stored content hash for a specific file.

        Args:
            vault_name: Name of the vault
            file_path: Relative file path within vault

        Returns:
            Content hash if file is indexed, None otherwise
        """
        if self._manager is None:
            return None

        vault_id = await self._get_vault_id(vault_name)
        if vault_id is None:
            return None

        result = await self._manager.fetch_value(
            "SELECT content_hash FROM documents WHERE vault_id = ? AND file_path = ?",
            (vault_id, file_path),
        )
        return result

    async def is_file_changed(
        self,
        vault_name: str,
        vault_path: Path,
        file_path: Path,
    ) -> bool:
        """Check if a specific file has changed.

        Args:
            vault_name: Name of the vault
            vault_path: Root path of vault
            file_path: Relative file path within vault

        Returns:
            True if file is new or modified, False if unchanged

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = vault_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        stored_hash = await self.get_file_hash(vault_name, str(file_path))
        if stored_hash is None:
            return True  # New file

        current_hash = await asyncio.to_thread(self.compute_content_hash, full_path)
        return current_hash != stored_hash

    async def get_stats(self, vault_name: str) -> dict[str, int]:
        """Get statistics about indexed files in vault.

        Args:
            vault_name: Name of the vault

        Returns:
            Dict with statistics (total_files, total_chunks, etc.)
        """
        if self._manager is None:
            return {
                "total_files": 0,
                "total_chunks": 0,
            }

        vault_id = await self._get_vault_id(vault_name)
        if vault_id is None:
            return {
                "total_files": 0,
                "total_chunks": 0,
            }

        total_files = await self._manager.fetch_value(
            "SELECT COUNT(*) FROM documents WHERE vault_id = ?",
            (vault_id,),
        )

        total_chunks = await self._manager.fetch_value(
            "SELECT SUM(chunk_count) FROM documents WHERE vault_id = ?",
            (vault_id,),
        )

        return {
            "total_files": total_files or 0,
            "total_chunks": total_chunks or 0,
        }
