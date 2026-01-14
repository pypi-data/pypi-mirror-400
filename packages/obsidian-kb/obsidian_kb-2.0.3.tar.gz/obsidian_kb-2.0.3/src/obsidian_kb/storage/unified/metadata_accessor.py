"""Unified Metadata Accessor for combined SQLite and LanceDB access.

This module provides a single interface for reading document metadata
from both SQLite (primary) and LanceDB (fallback) storage backends.

Phase 2.0.5 - Unified Metadata Access Layer
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from obsidian_kb.core.ttl_cache import TTLCache
from obsidian_kb.storage.unified.types import (
    ChunkInfo,
    DataSource,
    UnifiedDocumentInfo,
)

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager
    from obsidian_kb.storage.sqlite.manager import SQLiteManager
    from obsidian_kb.storage.sqlite.repositories.document import SQLiteDocumentRepository
    from obsidian_kb.storage.sqlite.repositories.vault import VaultRepository

logger = logging.getLogger(__name__)


class UnifiedMetadataAccessor:
    """Unified access layer for document metadata.

    Provides a single interface for reading document metadata with:
    - SQLite as the primary source (faster for metadata queries)
    - LanceDB as fallback when data is not in SQLite
    - TTL cache for frequently accessed data

    Usage:
        accessor = UnifiedMetadataAccessor(
            sqlite_manager=sqlite_manager,
            lancedb_manager=lancedb_manager,
        )

        # Get document metadata
        doc = await accessor.get_document("vault::path/to/note.md")

        # Get all documents in a vault
        docs = await accessor.get_documents_by_vault("my-vault")

        # Get chunks for a document
        chunks = await accessor.get_document_chunks("vault::path/to/note.md")
    """

    # Cache configuration
    CACHE_TTL_SECONDS: float = 300.0  # 5 minutes
    CACHE_MAX_SIZE: int = 5000

    def __init__(
        self,
        sqlite_manager: "SQLiteManager | None" = None,
        lancedb_manager: "LanceDBManager | None" = None,
        document_repo: "SQLiteDocumentRepository | None" = None,
        vault_repo: "VaultRepository | None" = None,
        cache: TTLCache | None = None,
    ) -> None:
        """Initialize the unified metadata accessor.

        Args:
            sqlite_manager: SQLiteManager instance (optional if repos provided)
            lancedb_manager: LanceDBManager instance for fallback
            document_repo: SQLiteDocumentRepository (optional, created from manager)
            vault_repo: VaultRepository (optional, created from manager)
            cache: TTLCache for caching (optional, created if not provided)
        """
        self._sqlite_manager = sqlite_manager
        self._lancedb_manager = lancedb_manager
        self._document_repo = document_repo
        self._vault_repo = vault_repo

        # Initialize cache
        if cache is not None:
            self._cache = cache
        else:
            self._cache = TTLCache(
                ttl_seconds=self.CACHE_TTL_SECONDS,
                max_size=self.CACHE_MAX_SIZE,
            )

        # Lazy initialization of repositories
        self._repos_initialized = False

    async def _ensure_repos(self) -> None:
        """Ensure repositories are initialized."""
        if self._repos_initialized:
            return

        if self._sqlite_manager and not self._document_repo:
            from obsidian_kb.storage.sqlite.repositories.document import (
                SQLiteDocumentRepository,
            )
            from obsidian_kb.storage.sqlite.repositories.vault import VaultRepository

            self._document_repo = SQLiteDocumentRepository(self._sqlite_manager)
            self._vault_repo = VaultRepository(self._sqlite_manager)

        self._repos_initialized = True

    def _cache_key(self, prefix: str, *args: str) -> str:
        """Generate a cache key."""
        return f"{prefix}:{':'.join(args)}"

    # =========================================================================
    # Document Access
    # =========================================================================

    async def get_document(
        self,
        document_id: str,
        use_cache: bool = True,
    ) -> UnifiedDocumentInfo | None:
        """Get document metadata by document_id.

        Tries SQLite first, falls back to LanceDB if not found.

        Args:
            document_id: Document ID (vault_name::file_path)
            use_cache: Whether to use cache (default True)

        Returns:
            UnifiedDocumentInfo if found, None otherwise
        """
        # Check cache first
        cache_key = self._cache_key("doc", document_id)
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        await self._ensure_repos()

        # Try SQLite first
        doc_info = await self._get_from_sqlite(document_id)
        if doc_info:
            if use_cache:
                self._cache.set(cache_key, doc_info)
            return doc_info

        # Fallback to LanceDB
        doc_info = await self._get_from_lancedb(document_id)
        if doc_info and use_cache:
            self._cache.set(cache_key, doc_info)

        return doc_info

    async def _get_from_sqlite(self, document_id: str) -> UnifiedDocumentInfo | None:
        """Get document from SQLite."""
        if not self._document_repo:
            return None

        try:
            sqlite_doc = await self._document_repo.get_by_document_id(document_id)
            if not sqlite_doc:
                return None

            # Get vault name from document_id
            vault_name = document_id.split("::", 1)[0] if "::" in document_id else ""

            # Get properties if available
            metadata = await self._get_properties_from_sqlite(sqlite_doc.id or 0)

            return UnifiedDocumentInfo(
                document_id=sqlite_doc.document_id,
                vault_name=vault_name,
                file_path=sqlite_doc.file_path,
                title=sqlite_doc.title or sqlite_doc.file_name,
                content_hash=sqlite_doc.content_hash,
                chunk_count=sqlite_doc.chunk_count,
                metadata=metadata,
                created_at=sqlite_doc.created_at,
                modified_at=sqlite_doc.modified_at,
                source=DataSource.SQLITE,
            )
        except Exception as e:
            logger.warning(f"Failed to get document from SQLite: {e}")
            return None

    async def _get_from_lancedb(self, document_id: str) -> UnifiedDocumentInfo | None:
        """Get document from LanceDB."""
        if not self._lancedb_manager:
            return None

        try:
            vault_name = document_id.split("::", 1)[0] if "::" in document_id else ""
            doc_info = await self._lancedb_manager.get_document_info(vault_name, document_id)

            if not doc_info:
                return None

            # Get properties from LanceDB
            properties = await self._lancedb_manager.get_document_properties(vault_name, document_id)

            return UnifiedDocumentInfo(
                document_id=doc_info.document_id,
                vault_name=doc_info.vault_name,
                file_path=doc_info.file_path,
                title=doc_info.title,
                content_hash="",  # LanceDB doesn't store content_hash in documents table
                chunk_count=doc_info.chunk_count,
                metadata=properties,
                created_at=doc_info.created_at,
                modified_at=doc_info.modified_at,
                source=DataSource.LANCEDB,
            )
        except Exception as e:
            logger.warning(f"Failed to get document from LanceDB: {e}")
            return None

    async def _get_properties_from_sqlite(self, document_db_id: int) -> dict[str, Any]:
        """Get document properties from SQLite."""
        if not self._sqlite_manager:
            return {}

        try:
            rows = await self._sqlite_manager.fetch_all(
                """
                SELECT property_key, property_value, value_type, value_number,
                       value_date, value_link_target, list_index
                FROM document_properties
                WHERE document_id = ?
                ORDER BY property_key, list_index
                """,
                (document_db_id,),
            )

            properties: dict[str, Any] = {}
            list_properties: dict[str, list[Any]] = {}

            for row in rows:
                key = row["property_key"]
                value_type = row["value_type"]
                list_index = row["list_index"]

                # Determine the value based on type
                if value_type == "number" and row["value_number"] is not None:
                    value = row["value_number"]
                elif value_type == "date" and row["value_date"]:
                    value = row["value_date"]
                elif value_type == "link" and row["value_link_target"]:
                    value = row["value_link_target"]
                else:
                    value = row["property_value"]

                # Handle list values
                if list_index > 0 or key in list_properties:
                    if key not in list_properties:
                        # Convert existing scalar to list
                        if key in properties:
                            list_properties[key] = [properties.pop(key)]
                        else:
                            list_properties[key] = []
                    list_properties[key].append(value)
                else:
                    properties[key] = value

            # Merge list properties back
            properties.update(list_properties)
            return properties

        except Exception as e:
            logger.warning(f"Failed to get properties from SQLite: {e}")
            return {}

    # =========================================================================
    # Vault-scoped Access
    # =========================================================================

    async def get_documents_by_vault(
        self,
        vault_name: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[UnifiedDocumentInfo]:
        """Get all documents in a vault.

        Args:
            vault_name: Vault name
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of UnifiedDocumentInfo
        """
        await self._ensure_repos()

        # Try SQLite first
        docs = await self._get_documents_from_sqlite(vault_name, limit, offset)
        if docs:
            return docs

        # Fallback to LanceDB
        return await self._get_documents_from_lancedb(vault_name, limit, offset)

    async def _get_documents_from_sqlite(
        self,
        vault_name: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[UnifiedDocumentInfo]:
        """Get documents from SQLite by vault name."""
        if not self._document_repo or not self._vault_repo:
            return []

        try:
            # Get vault ID
            vault = await self._vault_repo.get_by_name(vault_name)
            if not vault or not vault.id:
                return []

            # Get documents
            sqlite_docs = await self._document_repo.find_by_vault(
                vault.id, limit=limit, offset=offset
            )

            results = []
            for sqlite_doc in sqlite_docs:
                metadata = await self._get_properties_from_sqlite(sqlite_doc.id or 0)
                results.append(
                    UnifiedDocumentInfo(
                        document_id=sqlite_doc.document_id,
                        vault_name=vault_name,
                        file_path=sqlite_doc.file_path,
                        title=sqlite_doc.title or sqlite_doc.file_name,
                        content_hash=sqlite_doc.content_hash,
                        chunk_count=sqlite_doc.chunk_count,
                        metadata=metadata,
                        created_at=sqlite_doc.created_at,
                        modified_at=sqlite_doc.modified_at,
                        source=DataSource.SQLITE,
                    )
                )

            return results
        except Exception as e:
            logger.warning(f"Failed to get documents from SQLite: {e}")
            return []

    async def _get_documents_from_lancedb(
        self,
        vault_name: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[UnifiedDocumentInfo]:
        """Get documents from LanceDB by vault name."""
        if not self._lancedb_manager:
            return []

        try:
            # Get all document IDs from documents table
            documents_table = await self._lancedb_manager._ensure_table(vault_name, "documents")

            def _get_docs() -> list[dict[str, Any]]:
                try:
                    query = documents_table.search()
                    if limit:
                        # LanceDB doesn't support offset directly, so we need to handle it
                        query = query.limit(limit + offset)
                    arrow_table = query.to_arrow()
                    rows = arrow_table.to_pylist()
                    if offset:
                        rows = rows[offset:]
                    if limit:
                        rows = rows[:limit]
                    return rows
                except Exception:
                    return []

            rows = await asyncio.to_thread(_get_docs)

            results = []
            for row in rows:
                doc_id = row.get("document_id", "")
                results.append(
                    UnifiedDocumentInfo(
                        document_id=doc_id,
                        vault_name=vault_name,
                        file_path=row.get("file_path", ""),
                        title=row.get("title", ""),
                        content_hash="",  # Not stored in LanceDB documents
                        chunk_count=row.get("chunk_count", 0),
                        metadata={},  # Would need separate query for properties
                        created_at=row.get("created_at"),
                        modified_at=row.get("modified_at"),
                        source=DataSource.LANCEDB,
                    )
                )

            return results
        except Exception as e:
            logger.warning(f"Failed to get documents from LanceDB: {e}")
            return []

    # =========================================================================
    # Chunk Access
    # =========================================================================

    async def get_document_chunks(
        self,
        document_id: str,
    ) -> list[ChunkInfo]:
        """Get all chunks for a document.

        Chunks are stored only in LanceDB, so this always queries LanceDB.

        Args:
            document_id: Document ID (vault_name::file_path)

        Returns:
            List of ChunkInfo sorted by chunk_index
        """
        if not self._lancedb_manager:
            return []

        try:
            vault_name = document_id.split("::", 1)[0] if "::" in document_id else ""
            chunks_table = await self._lancedb_manager._ensure_table(vault_name, "chunks")

            def _get_chunks() -> list[dict[str, Any]]:
                try:
                    arrow_table = (
                        chunks_table.search()
                        .where(f"document_id = '{document_id}'")
                        .to_arrow()
                    )
                    return arrow_table.to_pylist()
                except Exception:
                    return []

            rows = await asyncio.to_thread(_get_chunks)

            chunks = [
                ChunkInfo(
                    chunk_id=row.get("chunk_id", ""),
                    document_id=row.get("document_id", ""),
                    chunk_index=row.get("chunk_index", 0),
                    section=row.get("section", ""),
                    content=row.get("content", ""),
                    inline_tags=row.get("inline_tags", []) or [],
                    links=row.get("links", []) or [],
                    source=DataSource.LANCEDB,
                )
                for row in rows
            ]

            # Sort by chunk_index
            chunks.sort(key=lambda c: c.chunk_index)
            return chunks

        except Exception as e:
            logger.warning(f"Failed to get chunks from LanceDB: {e}")
            return []

    # =========================================================================
    # Search by Property
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
        await self._ensure_repos()

        # Try SQLite first
        docs = await self._search_property_sqlite(vault_name, key, value)
        if docs:
            return docs

        # Fallback to LanceDB
        return await self._search_property_lancedb(vault_name, key, value)

    async def _search_property_sqlite(
        self,
        vault_name: str,
        key: str,
        value: str,
    ) -> list[UnifiedDocumentInfo]:
        """Search by property in SQLite."""
        if not self._sqlite_manager or not self._vault_repo:
            return []

        try:
            vault = await self._vault_repo.get_by_name(vault_name)
            if not vault or not vault.id:
                return []

            # Query documents with matching property
            rows = await self._sqlite_manager.fetch_all(
                """
                SELECT DISTINCT d.*
                FROM documents d
                JOIN document_properties dp ON d.id = dp.document_id
                WHERE d.vault_id = ?
                  AND dp.property_key = ?
                  AND (dp.property_value = ? OR dp.value_link_target = ?)
                """,
                (vault.id, key, value, value),
            )

            results = []
            for row in rows:
                doc_id = row.get("id", 0)
                metadata = await self._get_properties_from_sqlite(doc_id)
                results.append(
                    UnifiedDocumentInfo(
                        document_id=row["document_id"],
                        vault_name=vault_name,
                        file_path=row["file_path"],
                        title=row.get("title") or row["file_name"],
                        content_hash=row["content_hash"],
                        chunk_count=row.get("chunk_count", 0),
                        metadata=metadata,
                        created_at=row.get("created_at"),
                        modified_at=row.get("modified_at"),
                        source=DataSource.SQLITE,
                    )
                )

            return results
        except Exception as e:
            logger.warning(f"Failed to search property in SQLite: {e}")
            return []

    async def _search_property_lancedb(
        self,
        vault_name: str,
        key: str,
        value: str,
    ) -> list[UnifiedDocumentInfo]:
        """Search by property in LanceDB."""
        if not self._lancedb_manager:
            return []

        try:
            # Use LanceDB's get_documents_by_property method
            doc_ids = await self._lancedb_manager.get_documents_by_property(
                vault_name=vault_name,
                property_key=key,
                property_value=value,
            )

            if not doc_ids:
                return []

            # Get full document info for each
            results = []
            for doc_id in doc_ids:
                doc_info = await self._get_from_lancedb(doc_id)
                if doc_info:
                    results.append(doc_info)

            return results
        except Exception as e:
            logger.warning(f"Failed to search property in LanceDB: {e}")
            return []

    # =========================================================================
    # Cache Management
    # =========================================================================

    def invalidate_document(self, document_id: str) -> None:
        """Invalidate cached data for a document.

        Args:
            document_id: Document ID to invalidate
        """
        cache_key = self._cache_key("doc", document_id)
        self._cache.invalidate(cache_key)

    def invalidate_vault(self, vault_name: str) -> int:
        """Invalidate all cached data for a vault.

        Args:
            vault_name: Vault name

        Returns:
            Number of invalidated entries
        """
        return self._cache.invalidate_prefix(f"doc:{vault_name}::")

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    @property
    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._cache.stats

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def get_document_ids_by_vault(
        self,
        vault_name: str,
    ) -> set[str]:
        """Get all document IDs in a vault.

        Args:
            vault_name: Vault name

        Returns:
            Set of document IDs
        """
        await self._ensure_repos()

        # Try SQLite first
        if self._document_repo and self._vault_repo:
            try:
                vault = await self._vault_repo.get_by_name(vault_name)
                if vault and vault.id:
                    return await self._document_repo.get_document_ids_by_vault(vault.id)
            except Exception as e:
                logger.warning(f"Failed to get document IDs from SQLite: {e}")

        # Fallback to LanceDB
        if self._lancedb_manager:
            try:
                documents_table = await self._lancedb_manager._ensure_table(vault_name, "documents")

                def _get_ids() -> set[str]:
                    try:
                        arrow_table = documents_table.to_arrow()
                        if arrow_table.num_rows == 0:
                            return set()
                        return set(arrow_table["document_id"].to_pylist())
                    except Exception:
                        return set()

                return await asyncio.to_thread(_get_ids)
            except Exception as e:
                logger.warning(f"Failed to get document IDs from LanceDB: {e}")

        return set()

    async def document_exists(self, document_id: str) -> bool:
        """Check if a document exists.

        Args:
            document_id: Document ID

        Returns:
            True if document exists in either storage
        """
        await self._ensure_repos()

        # Check SQLite first
        if self._document_repo:
            try:
                if await self._document_repo.exists_by_document_id(document_id):
                    return True
            except Exception:
                pass

        # Check LanceDB
        vault_name = document_id.split("::", 1)[0] if "::" in document_id else ""
        if self._lancedb_manager and vault_name:
            try:
                doc_info = await self._lancedb_manager.get_document_info(vault_name, document_id)
                return doc_info is not None
            except Exception:
                pass

        return False
