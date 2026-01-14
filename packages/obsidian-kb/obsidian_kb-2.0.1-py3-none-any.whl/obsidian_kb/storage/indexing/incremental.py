"""Incremental indexer for efficient reindexing.

This module provides incremental indexing that only processes
changed files, using ChangeDetector and CachedEmbeddingProvider.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from obsidian_kb.storage.change_detector import ChangeDetector, ChangeSet
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository

if TYPE_CHECKING:
    from obsidian_kb.providers.cached_provider import CachedEmbeddingProvider
    from obsidian_kb.providers.interfaces import IEmbeddingProvider
    from obsidian_kb.storage.sqlite.embedding_cache import EmbeddingCache

logger = logging.getLogger(__name__)


@dataclass
class IndexingStats:
    """Statistics from incremental indexing.

    Attributes:
        files_added: Number of new files indexed
        files_updated: Number of modified files reindexed
        files_deleted: Number of deleted files removed from index
        files_unchanged: Number of unchanged files skipped
        chunks_created: Number of chunks created
        chunks_deleted: Number of chunks deleted
        embeddings_cached: Number of embeddings retrieved from cache
        embeddings_generated: Number of new embeddings generated
        duration_ms: Total indexing duration in milliseconds
        errors: List of error messages
    """

    files_added: int = 0
    files_updated: int = 0
    files_deleted: int = 0
    files_unchanged: int = 0
    chunks_created: int = 0
    chunks_deleted: int = 0
    embeddings_cached: int = 0
    embeddings_generated: int = 0
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        """Total number of files processed."""
        return self.files_added + self.files_updated

    @property
    def cache_hit_rate(self) -> float:
        """Embedding cache hit rate."""
        total = self.embeddings_cached + self.embeddings_generated
        return self.embeddings_cached / total if total > 0 else 0.0

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"IndexingStats(added={self.files_added}, updated={self.files_updated}, "
            f"deleted={self.files_deleted}, unchanged={self.files_unchanged}, "
            f"chunks={self.chunks_created}, cache_hit_rate={self.cache_hit_rate:.1%}, "
            f"duration={self.duration_ms:.1f}ms)"
        )


@dataclass
class DocumentParseResult:
    """Result of parsing a document file.

    Attributes:
        file_path: Relative path to file
        title: Document title
        content: Full document content
        content_hash: SHA256 hash of content
        metadata: Frontmatter metadata
        chunks: List of chunk texts
        file_size: File size in bytes
        created_at: File creation time
        modified_at: File modification time
    """

    file_path: Path
    title: str
    content: str
    content_hash: str
    metadata: dict[str, Any]
    chunks: list[str]
    file_size: int
    created_at: datetime | None
    modified_at: datetime


# Type alias for document parser function
DocumentParser = Callable[[Path, Path], DocumentParseResult]


class IncrementalIndexer:
    """Incremental indexer for efficient reindexing.

    Only indexes files that have changed (added, modified, deleted)
    compared to the stored index. Uses ChangeDetector for change
    detection and CachedEmbeddingProvider for embedding caching.

    Usage:
        indexer = IncrementalIndexer(
            sqlite_manager=manager,
            embedding_provider=cached_provider,
            document_parser=parse_document,
        )

        # Run incremental indexing
        stats = await indexer.index_vault(
            vault_name="my-vault",
            vault_path=Path("/path/to/vault"),
        )

        print(f"Processed {stats.total_processed} files")
        print(f"Cache hit rate: {stats.cache_hit_rate:.1%}")

    Attributes:
        manager: SQLiteManager for database access
        embedding_provider: Provider for generating embeddings
        change_detector: ChangeDetector for detecting file changes
    """

    def __init__(
        self,
        sqlite_manager: SQLiteManager,
        embedding_provider: "IEmbeddingProvider | CachedEmbeddingProvider",
        document_parser: DocumentParser | None = None,
        chunk_storage_callback: Callable[[str, list[dict[str, Any]]], Any] | None = None,
    ) -> None:
        """Initialize incremental indexer.

        Args:
            sqlite_manager: SQLiteManager instance
            embedding_provider: Embedding provider (preferably CachedEmbeddingProvider)
            document_parser: Function to parse documents into chunks.
                            Signature: (vault_path, file_path) -> DocumentParseResult
            chunk_storage_callback: Async callback to store chunks in LanceDB.
                                   Signature: (vault_name, chunks_data) -> None
        """
        self._manager = sqlite_manager
        self._embedding_provider = embedding_provider
        self._document_parser = document_parser or self._default_document_parser
        self._chunk_storage_callback = chunk_storage_callback

        self._change_detector = ChangeDetector(sqlite_manager)
        self._doc_repo = SQLiteDocumentRepository(sqlite_manager)
        self._vault_repo = VaultRepository(sqlite_manager)

    @staticmethod
    def _default_document_parser(vault_path: Path, file_path: Path) -> DocumentParseResult:
        """Default document parser (placeholder).

        This is a minimal implementation. Users should provide their own
        parser that handles frontmatter, chunking, etc.

        Args:
            vault_path: Root path of vault
            file_path: Relative path to file

        Returns:
            DocumentParseResult with parsed content
        """
        full_path = vault_path / file_path

        content = full_path.read_text(encoding="utf-8")
        content_hash = ChangeDetector.compute_content_hash(full_path)

        stat = full_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime)

        # Simple title extraction (first H1 or filename)
        title = file_path.stem
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Simple chunking by double newlines
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]

        return DocumentParseResult(
            file_path=file_path,
            title=title,
            content=content,
            content_hash=content_hash,
            metadata={},
            chunks=chunks,
            file_size=stat.st_size,
            created_at=None,
            modified_at=modified_at,
        )

    async def _ensure_vault(self, vault_name: str, vault_path: Path) -> int:
        """Ensure vault exists in database.

        Args:
            vault_name: Name of the vault
            vault_path: Path to vault directory

        Returns:
            Vault database ID
        """
        vault = await self._vault_repo.get_by_name(vault_name)
        if vault:
            return vault.id or 0

        # Create new vault
        new_vault = Vault(
            name=vault_name,
            path=str(vault_path),
        )
        return await self._vault_repo.create(new_vault)

    async def _process_file(
        self,
        vault_name: str,
        vault_id: int,
        vault_path: Path,
        file_path: Path,
        stats: IndexingStats,
    ) -> list[dict[str, Any]]:
        """Process a single file: parse, embed, and prepare for storage.

        Args:
            vault_name: Name of the vault
            vault_id: Vault database ID
            vault_path: Root path of vault
            file_path: Relative path to file
            stats: IndexingStats to update

        Returns:
            List of chunk records ready for storage
        """
        try:
            # Parse document
            parsed = await asyncio.to_thread(
                self._document_parser, vault_path, file_path
            )

            # Create document record
            document_id = f"{vault_name}::{file_path}"
            doc = SQLiteDocument(
                document_id=document_id,
                vault_id=vault_id,
                file_path=str(file_path),
                file_name=file_path.name,
                content_hash=parsed.content_hash,
                title=parsed.title,
                file_size=parsed.file_size,
                chunk_count=len(parsed.chunks),
                created_at=parsed.created_at,
                modified_at=parsed.modified_at,
            )

            # Upsert document to SQLite
            await self._doc_repo.upsert(doc)

            # Generate embeddings for chunks
            if parsed.chunks:
                embeddings = await self._embedding_provider.get_embeddings_batch(
                    parsed.chunks
                )

                # Track cache stats if using CachedEmbeddingProvider
                if hasattr(self._embedding_provider, "metrics"):
                    metrics = self._embedding_provider.metrics
                    stats.embeddings_cached = metrics.cache_hits
                    stats.embeddings_generated = metrics.embeddings_generated

                # Prepare chunk records
                chunk_records = []
                for i, (chunk_text, embedding) in enumerate(zip(parsed.chunks, embeddings)):
                    chunk_id = f"{document_id}::{i}"
                    chunk_records.append({
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "vault_name": vault_name,
                        "chunk_index": i,
                        "content": chunk_text,
                        "vector": embedding,
                        "section": "",
                        "links": [],
                        "inline_tags": [],
                    })

                stats.chunks_created += len(chunk_records)
                return chunk_records

            return []

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            logger.error(error_msg)
            stats.errors.append(error_msg)
            return []

    async def _delete_document(
        self,
        vault_id: int,
        document_id: str,
        stats: IndexingStats,
    ) -> None:
        """Delete document and its chunks from index.

        Args:
            vault_id: Vault database ID
            document_id: Document ID to delete
            stats: IndexingStats to update
        """
        try:
            # Get chunk count before deletion
            doc = await self._doc_repo.get_by_document_id(document_id)
            if doc:
                stats.chunks_deleted += doc.chunk_count

            # Delete from SQLite
            await self._doc_repo.delete_by_document_id(document_id)

            stats.files_deleted += 1

        except Exception as e:
            error_msg = f"Error deleting {document_id}: {e}"
            logger.error(error_msg)
            stats.errors.append(error_msg)

    async def index_vault(
        self,
        vault_name: str,
        vault_path: Path,
        force: bool = False,
        batch_size: int = 50,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> IndexingStats:
        """Run incremental indexing on vault.

        Args:
            vault_name: Name of the vault
            vault_path: Path to vault directory
            force: If True, reindex all files regardless of changes
            batch_size: Number of files to process in each batch
            progress_callback: Optional callback(processed, total) for progress updates

        Returns:
            IndexingStats with indexing results
        """
        import time

        start_time = time.perf_counter()
        stats = IndexingStats()

        try:
            # Ensure vault exists
            vault_id = await self._ensure_vault(vault_name, vault_path)

            # Detect changes
            if force:
                # Force mode: treat all files as added
                files = self._change_detector._scan_vault_files(vault_path)
                changes = ChangeSet(
                    added=files,
                    modified=[],
                    deleted=[],
                    unchanged=0,
                )
            else:
                changes = await self._change_detector.detect_changes(
                    vault_name, vault_path
                )

            stats.files_unchanged = changes.unchanged

            if not changes.has_changes and not force:
                logger.info(f"No changes detected in vault '{vault_name}'")
                stats.duration_ms = (time.perf_counter() - start_time) * 1000
                return stats

            total_to_process = changes.total_to_process + len(changes.deleted)
            processed = 0

            # Process added files
            all_chunks: list[dict[str, Any]] = []
            for file_path in changes.added:
                chunks = await self._process_file(
                    vault_name, vault_id, vault_path, file_path, stats
                )
                all_chunks.extend(chunks)
                stats.files_added += 1
                processed += 1

                if progress_callback:
                    progress_callback(processed, total_to_process)

                # Batch store chunks
                if len(all_chunks) >= batch_size and self._chunk_storage_callback:
                    await self._chunk_storage_callback(vault_name, all_chunks)
                    all_chunks = []

            # Process modified files
            for file_path in changes.modified:
                # Delete existing chunks first (handled by LanceDB upsert)
                chunks = await self._process_file(
                    vault_name, vault_id, vault_path, file_path, stats
                )
                all_chunks.extend(chunks)
                stats.files_updated += 1
                processed += 1

                if progress_callback:
                    progress_callback(processed, total_to_process)

                # Batch store chunks
                if len(all_chunks) >= batch_size and self._chunk_storage_callback:
                    await self._chunk_storage_callback(vault_name, all_chunks)
                    all_chunks = []

            # Store remaining chunks
            if all_chunks and self._chunk_storage_callback:
                await self._chunk_storage_callback(vault_name, all_chunks)

            # Delete removed files
            for document_id in changes.deleted:
                await self._delete_document(vault_id, document_id, stats)
                processed += 1

                if progress_callback:
                    progress_callback(processed, total_to_process)

            # Update vault stats
            doc_count = await self._doc_repo.count_by_vault(vault_id)
            await self._vault_repo.update_index_stats(
                vault_name,
                document_count=doc_count,
                chunk_count=stats.chunks_created,
            )

            stats.duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                f"Incremental indexing completed for '{vault_name}': {stats}"
            )

            return stats

        except Exception as e:
            error_msg = f"Indexing failed for vault '{vault_name}': {e}"
            logger.error(error_msg)
            stats.errors.append(error_msg)
            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

    async def index_files(
        self,
        vault_name: str,
        vault_path: Path,
        file_paths: list[Path],
    ) -> IndexingStats:
        """Index specific files (for targeted reindexing).

        Args:
            vault_name: Name of the vault
            vault_path: Path to vault directory
            file_paths: List of relative file paths to index

        Returns:
            IndexingStats with indexing results
        """
        import time

        start_time = time.perf_counter()
        stats = IndexingStats()

        try:
            vault_id = await self._ensure_vault(vault_name, vault_path)

            all_chunks: list[dict[str, Any]] = []
            for file_path in file_paths:
                full_path = vault_path / file_path
                if not full_path.exists():
                    stats.errors.append(f"File not found: {file_path}")
                    continue

                # Check if file is already indexed
                document_id = f"{vault_name}::{file_path}"
                existing = await self._doc_repo.get_by_document_id(document_id)

                chunks = await self._process_file(
                    vault_name, vault_id, vault_path, file_path, stats
                )
                all_chunks.extend(chunks)

                if existing:
                    stats.files_updated += 1
                else:
                    stats.files_added += 1

            # Store all chunks
            if all_chunks and self._chunk_storage_callback:
                await self._chunk_storage_callback(vault_name, all_chunks)

            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

        except Exception as e:
            error_msg = f"Indexing failed: {e}"
            logger.error(error_msg)
            stats.errors.append(error_msg)
            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

    async def delete_files(
        self,
        vault_name: str,
        file_paths: list[str],
    ) -> IndexingStats:
        """Delete specific files from index.

        Args:
            vault_name: Name of the vault
            file_paths: List of relative file paths to delete

        Returns:
            IndexingStats with deletion results
        """
        import time

        start_time = time.perf_counter()
        stats = IndexingStats()

        try:
            vault_id = await self._vault_repo.get_id_by_name(vault_name)
            if vault_id is None:
                stats.errors.append(f"Vault not found: {vault_name}")
                return stats

            for file_path in file_paths:
                document_id = f"{vault_name}::{file_path}"
                await self._delete_document(vault_id, document_id, stats)

            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

        except Exception as e:
            error_msg = f"Deletion failed: {e}"
            logger.error(error_msg)
            stats.errors.append(error_msg)
            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

    async def clear_vault(self, vault_name: str) -> IndexingStats:
        """Clear all indexed data for a vault.

        Args:
            vault_name: Name of the vault

        Returns:
            IndexingStats with deletion results
        """
        import time

        start_time = time.perf_counter()
        stats = IndexingStats()

        try:
            vault_id = await self._vault_repo.get_id_by_name(vault_name)
            if vault_id is None:
                logger.warning(f"Vault not found: {vault_name}")
                return stats

            # Get document count before deletion
            doc_count = await self._doc_repo.count_by_vault(vault_id)
            stats.files_deleted = doc_count

            # Delete all documents for vault
            deleted = await self._doc_repo.delete_by_vault(vault_id)
            logger.info(f"Deleted {deleted} documents from vault '{vault_name}'")

            # Update vault stats
            await self._vault_repo.update_index_stats(
                vault_name,
                document_count=0,
                chunk_count=0,
            )

            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

        except Exception as e:
            error_msg = f"Clear vault failed: {e}"
            logger.error(error_msg)
            stats.errors.append(error_msg)
            stats.duration_ms = (time.perf_counter() - start_time) * 1000
            return stats

    async def get_indexing_stats(self, vault_name: str) -> dict[str, Any]:
        """Get current indexing statistics for a vault.

        Args:
            vault_name: Name of the vault

        Returns:
            Dict with indexing statistics
        """
        vault = await self._vault_repo.get_by_name(vault_name)
        if vault is None:
            return {
                "vault_name": vault_name,
                "exists": False,
                "document_count": 0,
                "chunk_count": 0,
            }

        # Get embedding cache stats if available
        cache_stats = {}
        if hasattr(self._embedding_provider, "metrics"):
            metrics = self._embedding_provider.metrics
            cache_stats = {
                "cache_hits": metrics.cache_hits,
                "cache_misses": metrics.cache_misses,
                "hit_rate": metrics.hit_rate,
            }

        return {
            "vault_name": vault_name,
            "exists": True,
            "document_count": vault.document_count,
            "chunk_count": vault.chunk_count,
            "last_indexed_at": vault.last_indexed_at.isoformat() if vault.last_indexed_at else None,
            "cache_stats": cache_stats,
        }
