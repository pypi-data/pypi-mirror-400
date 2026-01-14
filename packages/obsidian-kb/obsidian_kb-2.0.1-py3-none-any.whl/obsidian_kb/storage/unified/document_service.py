"""Unified Document Service for high-level document operations.

This module provides a high-level service for document operations that
combines both SQLite and LanceDB backends through UnifiedMetadataAccessor.

Phase 2.0.5 - Unified Metadata Access Layer
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from obsidian_kb.storage.unified.metadata_accessor import UnifiedMetadataAccessor
from obsidian_kb.storage.unified.types import (
    ChunkInfo,
    DataSource,
    UnifiedDocumentInfo,
)

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager
    from obsidian_kb.storage.sqlite.manager import SQLiteManager

logger = logging.getLogger(__name__)


class UnifiedDocumentService:
    """High-level service for document operations.

    Provides a clean API for:
    - Getting document metadata
    - Listing documents by vault
    - Getting document chunks
    - Searching by properties
    - Reading document content

    Usage:
        service = UnifiedDocumentService(
            sqlite_manager=sqlite_manager,
            lancedb_manager=lancedb_manager,
        )

        # Get a document
        doc = await service.get_document("vault::path/to/note.md")

        # Get documents by vault
        docs = await service.get_documents_by_vault("my-vault")

        # Search by property
        docs = await service.search_by_property("my-vault", "status", "active")
    """

    def __init__(
        self,
        sqlite_manager: "SQLiteManager | None" = None,
        lancedb_manager: "LanceDBManager | None" = None,
        accessor: UnifiedMetadataAccessor | None = None,
        vault_paths: dict[str, Path] | None = None,
    ) -> None:
        """Initialize the document service.

        Args:
            sqlite_manager: SQLiteManager instance
            lancedb_manager: LanceDBManager instance
            accessor: Pre-configured UnifiedMetadataAccessor (optional)
            vault_paths: Mapping of vault names to their filesystem paths
        """
        self._sqlite_manager = sqlite_manager
        self._lancedb_manager = lancedb_manager
        self._vault_paths = vault_paths or {}

        # Use provided accessor or create new one
        self._accessor = accessor or UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            lancedb_manager=lancedb_manager,
        )

    # =========================================================================
    # Document Retrieval
    # =========================================================================

    async def get_document(
        self,
        document_id: str,
        include_content: bool = False,
    ) -> UnifiedDocumentInfo | None:
        """Get document metadata by document_id.

        Args:
            document_id: Document ID (vault_name::file_path)
            include_content: If True, include full document content

        Returns:
            UnifiedDocumentInfo if found, None otherwise
        """
        doc = await self._accessor.get_document(document_id)

        if doc and include_content:
            content = await self._get_document_content(doc)
            if content:
                doc.metadata["_content"] = content

        return doc

    async def get_documents_by_vault(
        self,
        vault_name: str,
        limit: int | None = None,
        offset: int = 0,
        include_metadata: bool = True,
    ) -> list[UnifiedDocumentInfo]:
        """Get all documents in a vault.

        Args:
            vault_name: Vault name
            limit: Maximum number of results
            offset: Number of results to skip
            include_metadata: If True, include document metadata (default True)

        Returns:
            List of UnifiedDocumentInfo
        """
        docs = await self._accessor.get_documents_by_vault(
            vault_name=vault_name,
            limit=limit,
            offset=offset,
        )

        # If metadata not needed, strip it for performance
        if not include_metadata:
            for doc in docs:
                doc.metadata = {}

        return docs

    async def get_document_chunks(
        self,
        document_id: str,
    ) -> list[ChunkInfo]:
        """Get all chunks for a document.

        Args:
            document_id: Document ID (vault_name::file_path)

        Returns:
            List of ChunkInfo sorted by chunk_index
        """
        return await self._accessor.get_document_chunks(document_id)

    async def get_document_content(
        self,
        document_id: str,
    ) -> str:
        """Get full content of a document.

        Tries to read from file first, falls back to concatenating chunks.

        Args:
            document_id: Document ID (vault_name::file_path)

        Returns:
            Document content as string
        """
        doc = await self._accessor.get_document(document_id)
        if not doc:
            return ""

        return await self._get_document_content(doc)

    async def _get_document_content(self, doc: UnifiedDocumentInfo) -> str:
        """Internal method to get content for a document."""
        # Try reading from file first
        file_content = await self._read_file_content(doc)
        if file_content:
            return file_content

        # Fallback to concatenating chunks
        chunks = await self._accessor.get_document_chunks(doc.document_id)
        if chunks:
            return "\n\n".join(chunk.content for chunk in chunks)

        return ""

    async def _read_file_content(self, doc: UnifiedDocumentInfo) -> str | None:
        """Try to read content directly from file."""
        vault_path = self._vault_paths.get(doc.vault_name)
        if not vault_path:
            # Try to get from LanceDB metadata
            if self._lancedb_manager:
                try:
                    lance_doc = await self._lancedb_manager.get_document_info(
                        doc.vault_name, doc.document_id
                    )
                    if lance_doc and lance_doc.file_path_full:
                        file_path = Path(lance_doc.file_path_full)
                        if file_path.exists():
                            try:
                                return file_path.read_text(encoding="utf-8")
                            except Exception as e:
                                logger.debug(f"Failed to read file {file_path}: {e}")
                except Exception:
                    pass
            return None

        file_path = vault_path / doc.file_path
        if not file_path.exists():
            return None

        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {e}")
            return None

    # =========================================================================
    # Search Operations
    # =========================================================================

    async def search_by_property(
        self,
        vault_name: str,
        key: str,
        value: str,
    ) -> list[UnifiedDocumentInfo]:
        """Search documents by property key-value pair.

        Args:
            vault_name: Vault name
            key: Property key
            value: Property value to match

        Returns:
            List of matching UnifiedDocumentInfo
        """
        return await self._accessor.search_by_property(vault_name, key, value)

    async def search_by_properties(
        self,
        vault_name: str,
        properties: dict[str, str],
        match_all: bool = True,
    ) -> list[UnifiedDocumentInfo]:
        """Search documents by multiple properties.

        Args:
            vault_name: Vault name
            properties: Dict of property key-value pairs
            match_all: If True, document must match all properties (AND)
                      If False, document matches if any property matches (OR)

        Returns:
            List of matching UnifiedDocumentInfo
        """
        if not properties:
            return []

        # Search for each property
        results_per_property: list[set[str]] = []
        all_docs: dict[str, UnifiedDocumentInfo] = {}

        for key, value in properties.items():
            docs = await self._accessor.search_by_property(vault_name, key, value)
            doc_ids = set()
            for doc in docs:
                doc_ids.add(doc.document_id)
                all_docs[doc.document_id] = doc
            results_per_property.append(doc_ids)

        if not results_per_property:
            return []

        # Combine results
        if match_all:
            # Intersection of all sets
            matching_ids = results_per_property[0]
            for ids in results_per_property[1:]:
                matching_ids &= ids
        else:
            # Union of all sets
            matching_ids = set()
            for ids in results_per_property:
                matching_ids |= ids

        return [all_docs[doc_id] for doc_id in matching_ids if doc_id in all_docs]

    async def search_by_title(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
    ) -> list[UnifiedDocumentInfo]:
        """Search documents by title.

        Args:
            vault_name: Vault name
            query: Search query (partial match)
            limit: Maximum results

        Returns:
            List of matching UnifiedDocumentInfo
        """
        # Get all documents and filter by title
        # This is not optimal but works for now
        # TODO: Add title search to SQLite repo
        docs = await self._accessor.get_documents_by_vault(vault_name)

        query_lower = query.lower()
        matching = [
            doc for doc in docs
            if query_lower in doc.title.lower()
        ]

        # Sort by relevance (exact match first, then starts with, then contains)
        def sort_key(doc: UnifiedDocumentInfo) -> tuple[int, str]:
            title_lower = doc.title.lower()
            if title_lower == query_lower:
                return (0, doc.title)
            elif title_lower.startswith(query_lower):
                return (1, doc.title)
            else:
                return (2, doc.title)

        matching.sort(key=sort_key)
        return matching[:limit]

    async def search_by_tags(
        self,
        vault_name: str,
        tags: list[str],
        match_all: bool = True,
    ) -> list[UnifiedDocumentInfo]:
        """Search documents by tags.

        Args:
            vault_name: Vault name
            tags: List of tags to search for
            match_all: If True, document must have all tags (AND)
                      If False, document matches if any tag matches (OR)

        Returns:
            List of matching UnifiedDocumentInfo
        """
        if not tags:
            return []

        # Use LanceDB for tag search if available
        if self._lancedb_manager:
            try:
                doc_ids = await self._lancedb_manager.get_documents_by_tags(
                    vault_name=vault_name,
                    tags=tags,
                    match_all=match_all,
                )

                # Get full document info for each
                results = []
                for doc_id in doc_ids:
                    doc = await self._accessor.get_document(doc_id)
                    if doc:
                        results.append(doc)
                return results
            except Exception as e:
                logger.warning(f"Failed to search by tags in LanceDB: {e}")

        return []

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def get_vault_document_count(self, vault_name: str) -> int:
        """Get the number of documents in a vault.

        Args:
            vault_name: Vault name

        Returns:
            Number of documents
        """
        doc_ids = await self._accessor.get_document_ids_by_vault(vault_name)
        return len(doc_ids)

    async def get_all_document_ids(self, vault_name: str) -> set[str]:
        """Get all document IDs in a vault.

        Args:
            vault_name: Vault name

        Returns:
            Set of document IDs
        """
        return await self._accessor.get_document_ids_by_vault(vault_name)

    async def document_exists(self, document_id: str) -> bool:
        """Check if a document exists.

        Args:
            document_id: Document ID

        Returns:
            True if document exists
        """
        return await self._accessor.document_exists(document_id)

    async def get_document_modified_at(
        self,
        document_id: str,
    ) -> datetime | None:
        """Get the modification timestamp of a document.

        Args:
            document_id: Document ID

        Returns:
            Modification datetime or None if not found
        """
        doc = await self._accessor.get_document(document_id)
        return doc.modified_at if doc else None

    async def get_documents_modified_since(
        self,
        vault_name: str,
        since: datetime,
    ) -> list[UnifiedDocumentInfo]:
        """Get documents modified since a given datetime.

        Args:
            vault_name: Vault name
            since: Datetime to compare against

        Returns:
            List of documents modified after `since`
        """
        docs = await self._accessor.get_documents_by_vault(vault_name)
        return [
            doc for doc in docs
            if doc.modified_at and doc.modified_at > since
        ]

    # =========================================================================
    # Batch Operations
    # =========================================================================

    async def get_documents_batch(
        self,
        document_ids: list[str],
    ) -> list[UnifiedDocumentInfo]:
        """Get multiple documents by their IDs.

        Args:
            document_ids: List of document IDs

        Returns:
            List of UnifiedDocumentInfo (only found documents)
        """
        # Fetch documents in parallel
        tasks = [self._accessor.get_document(doc_id) for doc_id in document_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        docs = []
        for result in results:
            if isinstance(result, UnifiedDocumentInfo):
                docs.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"Error fetching document: {result}")

        return docs

    async def get_chunk_count(self, document_id: str) -> int:
        """Get the number of chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            Number of chunks
        """
        doc = await self._accessor.get_document(document_id)
        if doc:
            return doc.chunk_count

        # Fallback to counting chunks directly
        chunks = await self._accessor.get_document_chunks(document_id)
        return len(chunks)

    # =========================================================================
    # Cache Management (delegated to accessor)
    # =========================================================================

    def invalidate_document(self, document_id: str) -> None:
        """Invalidate cached data for a document."""
        self._accessor.invalidate_document(document_id)

    def invalidate_vault(self, vault_name: str) -> int:
        """Invalidate all cached data for a vault."""
        return self._accessor.invalidate_vault(vault_name)

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._accessor.clear_cache()

    @property
    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._accessor.cache_stats

    # =========================================================================
    # Configuration
    # =========================================================================

    def set_vault_path(self, vault_name: str, path: Path) -> None:
        """Set the filesystem path for a vault.

        Args:
            vault_name: Vault name
            path: Filesystem path to the vault
        """
        self._vault_paths[vault_name] = path

    def get_vault_path(self, vault_name: str) -> Path | None:
        """Get the filesystem path for a vault.

        Args:
            vault_name: Vault name

        Returns:
            Path or None if not set
        """
        return self._vault_paths.get(vault_name)
