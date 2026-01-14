"""Document repository for SQLite storage.

This module provides repository for managing document metadata in SQLite.
Handles document CRUD operations, change detection, and metadata queries.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


@dataclass
class SQLiteDocument:
    """Document entity for SQLite storage.

    Represents document metadata stored in SQLite.
    Note: This is different from the existing Document class in types.py
    which is used for LanceDB operations.

    Attributes:
        id: Database primary key (None for new entities)
        document_id: Unique document ID (vault_name::file_path)
        vault_id: Foreign key to vaults table
        file_path: Relative path within vault
        file_name: File name only
        title: Document title from frontmatter or H1
        content_hash: SHA256 hash for change detection
        file_size: File size in bytes
        chunk_count: Number of chunks
        created_at: File creation time
        modified_at: File modification time
        indexed_at: Last indexing time
    """

    document_id: str
    vault_id: int
    file_path: str
    file_name: str
    content_hash: str
    id: int | None = None
    title: str | None = None
    file_size: int = 0
    chunk_count: int = 0
    created_at: datetime | None = None
    modified_at: datetime | None = None
    indexed_at: datetime | None = None


class SQLiteDocumentRepository(BaseRepository[SQLiteDocument]):
    """Repository for document metadata operations in SQLite.

    Provides CRUD operations and specialized queries for documents,
    optimized for change detection and metadata search.

    Usage:
        repo = SQLiteDocumentRepository(manager)

        # Create document
        doc = SQLiteDocument(
            document_id="vault::path/to/note.md",
            vault_id=1,
            file_path="path/to/note.md",
            file_name="note.md",
            content_hash="abc123...",
        )
        doc_id = await repo.create(doc)

        # Find by document_id
        doc = await repo.get_by_document_id("vault::path/to/note.md")

        # Check for changes
        hash = await repo.get_content_hash("vault::path/to/note.md")
    """

    table_name = "documents"

    def __init__(self, manager: SQLiteManager) -> None:
        """Initialize document repository.

        Args:
            manager: SQLiteManager instance
        """
        super().__init__(manager)

    def _row_to_entity(self, row: dict[str, Any]) -> SQLiteDocument:
        """Convert database row to SQLiteDocument entity.

        Args:
            row: Database row as dict

        Returns:
            SQLiteDocument instance
        """
        return SQLiteDocument(
            id=row["id"],
            document_id=row["document_id"],
            vault_id=row["vault_id"],
            file_path=row["file_path"],
            file_name=row["file_name"],
            title=row.get("title"),
            content_hash=row["content_hash"],
            file_size=row.get("file_size", 0),
            chunk_count=row.get("chunk_count", 0),
            created_at=_parse_datetime(row.get("created_at")),
            modified_at=_parse_datetime(row.get("modified_at")),
            indexed_at=_parse_datetime(row.get("indexed_at")),
        )

    def _entity_to_row(self, entity: SQLiteDocument) -> dict[str, Any]:
        """Convert SQLiteDocument entity to database row.

        Args:
            entity: SQLiteDocument instance

        Returns:
            Dict for database operations
        """
        row: dict[str, Any] = {
            "document_id": entity.document_id,
            "vault_id": entity.vault_id,
            "file_path": entity.file_path,
            "file_name": entity.file_name,
            "content_hash": entity.content_hash,
            "file_size": entity.file_size,
            "chunk_count": entity.chunk_count,
        }

        if entity.title:
            row["title"] = entity.title

        if entity.created_at:
            row["created_at"] = entity.created_at.isoformat()

        if entity.modified_at:
            row["modified_at"] = entity.modified_at.isoformat()

        return row

    # =========================================================================
    # Primary lookups
    # =========================================================================

    async def get_by_document_id(self, document_id: str) -> SQLiteDocument | None:
        """Get document by unique document_id.

        Args:
            document_id: Document ID (vault_name::file_path)

        Returns:
            Document if found, None otherwise
        """
        return await self.find_one("document_id = ?", (document_id,))

    async def get_id_by_document_id(self, document_id: str) -> int | None:
        """Get database ID by document_id.

        Args:
            document_id: Document ID (vault_name::file_path)

        Returns:
            Database ID if found, None otherwise
        """
        result = await self._manager.fetch_value(
            "SELECT id FROM documents WHERE document_id = ?",
            (document_id,),
        )
        return result

    async def exists_by_document_id(self, document_id: str) -> bool:
        """Check if document exists by document_id.

        Args:
            document_id: Document ID

        Returns:
            True if document exists
        """
        count = await self.count("document_id = ?", (document_id,))
        return count > 0

    # =========================================================================
    # Vault-scoped queries
    # =========================================================================

    async def find_by_vault(
        self,
        vault_id: int,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SQLiteDocument]:
        """Find all documents in a vault.

        Args:
            vault_id: Vault database ID
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of documents
        """
        return await self.find_many(
            "vault_id = ?",
            (vault_id,),
            limit=limit,
            offset=offset,
            order_by="file_path",
        )

    async def find_by_vault_name(
        self,
        vault_name: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SQLiteDocument]:
        """Find all documents by vault name.

        Args:
            vault_name: Vault name
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of documents
        """
        rows = await self._manager.fetch_all(
            """
            SELECT d.* FROM documents d
            JOIN vaults v ON d.vault_id = v.id
            WHERE v.name = ?
            ORDER BY d.file_path
            LIMIT ? OFFSET ?
            """,
            (vault_name, limit or -1, offset),
        )
        return [self._row_to_entity(row) for row in rows]

    async def count_by_vault(self, vault_id: int) -> int:
        """Count documents in a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            Document count
        """
        return await self.count("vault_id = ?", (vault_id,))

    async def get_document_ids_by_vault(self, vault_id: int) -> set[str]:
        """Get all document_ids in a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            Set of document_ids
        """
        rows = await self._manager.fetch_all(
            "SELECT document_id FROM documents WHERE vault_id = ?",
            (vault_id,),
        )
        return {row["document_id"] for row in rows}

    # =========================================================================
    # Change detection
    # =========================================================================

    async def get_content_hash(self, document_id: str) -> str | None:
        """Get content hash for change detection.

        Args:
            document_id: Document ID

        Returns:
            Content hash if found, None otherwise
        """
        result = await self._manager.fetch_value(
            "SELECT content_hash FROM documents WHERE document_id = ?",
            (document_id,),
        )
        return result

    async def find_by_content_hash(
        self,
        vault_id: int,
        content_hash: str,
    ) -> SQLiteDocument | None:
        """Find document by content hash.

        Useful for detecting duplicate content.

        Args:
            vault_id: Vault database ID
            content_hash: Content hash to find

        Returns:
            Document if found, None otherwise
        """
        return await self.find_one(
            "vault_id = ? AND content_hash = ?",
            (vault_id, content_hash),
        )

    async def get_all_hashes(self, vault_id: int) -> dict[str, str]:
        """Get all document_id -> content_hash mappings.

        Efficient for bulk change detection.

        Args:
            vault_id: Vault database ID

        Returns:
            Dict mapping document_id to content_hash
        """
        rows = await self._manager.fetch_all(
            "SELECT document_id, content_hash FROM documents WHERE vault_id = ?",
            (vault_id,),
        )
        return {row["document_id"]: row["content_hash"] for row in rows}

    async def get_file_paths(self, vault_id: int) -> set[str]:
        """Get all file paths in a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            Set of file paths
        """
        rows = await self._manager.fetch_all(
            "SELECT file_path FROM documents WHERE vault_id = ?",
            (vault_id,),
        )
        return {row["file_path"] for row in rows}

    # =========================================================================
    # Update operations
    # =========================================================================

    async def update_content_hash(
        self,
        document_id: str,
        content_hash: str,
    ) -> bool:
        """Update content hash and indexed_at timestamp.

        Args:
            document_id: Document ID
            content_hash: New content hash

        Returns:
            True if document was updated
        """
        cursor = await self._manager.execute(
            """
            UPDATE documents SET
                content_hash = ?,
                indexed_at = datetime('now')
            WHERE document_id = ?
            """,
            (content_hash, document_id),
        )
        return cursor.rowcount > 0

    async def update_chunk_count(
        self,
        document_id: str,
        chunk_count: int,
    ) -> bool:
        """Update document chunk count.

        Args:
            document_id: Document ID
            chunk_count: New chunk count

        Returns:
            True if document was updated
        """
        cursor = await self._manager.execute(
            "UPDATE documents SET chunk_count = ? WHERE document_id = ?",
            (chunk_count, document_id),
        )
        return cursor.rowcount > 0

    async def touch_indexed(self, document_id: str) -> bool:
        """Update indexed_at timestamp.

        Args:
            document_id: Document ID

        Returns:
            True if document was updated
        """
        cursor = await self._manager.execute(
            "UPDATE documents SET indexed_at = datetime('now') WHERE document_id = ?",
            (document_id,),
        )
        return cursor.rowcount > 0

    # =========================================================================
    # Delete operations
    # =========================================================================

    async def delete_by_document_id(self, document_id: str) -> bool:
        """Delete document by document_id.

        Args:
            document_id: Document ID

        Returns:
            True if document was deleted
        """
        cursor = await self._manager.execute(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,),
        )
        return cursor.rowcount > 0

    async def delete_by_vault(self, vault_id: int) -> int:
        """Delete all documents in a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            Number of deleted documents
        """
        return await self.delete_where("vault_id = ?", (vault_id,))

    async def delete_by_file_paths(
        self,
        vault_id: int,
        file_paths: list[str],
    ) -> int:
        """Delete documents by file paths.

        Args:
            vault_id: Vault database ID
            file_paths: List of file paths to delete

        Returns:
            Number of deleted documents
        """
        if not file_paths:
            return 0

        placeholders = ", ".join("?" * len(file_paths))
        cursor = await self._manager.execute(
            f"DELETE FROM documents WHERE vault_id = ? AND file_path IN ({placeholders})",
            (vault_id, *file_paths),
        )
        return cursor.rowcount

    # =========================================================================
    # Upsert operations
    # =========================================================================

    async def upsert(self, doc: SQLiteDocument) -> int:
        """Create or update document.

        Creates document if it doesn't exist, updates if it does.

        Args:
            doc: Document entity

        Returns:
            Document database ID
        """
        existing_id = await self.get_id_by_document_id(doc.document_id)
        if existing_id:
            # Update existing
            await self.update(existing_id, doc)
            return existing_id
        else:
            # Create new
            return await self.create(doc)

    async def upsert_many(self, docs: list[SQLiteDocument]) -> int:
        """Create or update multiple documents.

        Uses transaction for atomicity.

        Args:
            docs: List of document entities

        Returns:
            Number of documents processed
        """
        if not docs:
            return 0

        count = 0
        async with self._manager.transaction() as conn:
            for doc in docs:
                row = self._entity_to_row(doc)
                columns = ", ".join(row.keys())
                placeholders = ", ".join("?" * len(row))
                update_clause = ", ".join(f"{k} = excluded.{k}" for k in row.keys())

                await conn.execute(
                    f"""
                    INSERT INTO documents ({columns}) VALUES ({placeholders})
                    ON CONFLICT(document_id) DO UPDATE SET
                        {update_clause},
                        indexed_at = datetime('now')
                    """,
                    tuple(row.values()),
                )
                count += 1

        return count

    # =========================================================================
    # Search operations
    # =========================================================================

    async def search_by_title(
        self,
        vault_id: int,
        query: str,
        limit: int = 10,
    ) -> list[SQLiteDocument]:
        """Search documents by title.

        Args:
            vault_id: Vault database ID
            query: Search query
            limit: Maximum results

        Returns:
            Matching documents
        """
        # Escape SQL wildcards in query
        safe_query = query.replace("%", "\\%").replace("_", "\\_")

        return await self.find_many(
            "vault_id = ? AND title LIKE ? ESCAPE '\\'",
            (vault_id, f"%{safe_query}%"),
            limit=limit,
            order_by="title",
        )

    async def search_by_file_path(
        self,
        vault_id: int,
        path_pattern: str,
        limit: int | None = None,
    ) -> list[SQLiteDocument]:
        """Search documents by file path pattern.

        Args:
            vault_id: Vault database ID
            path_pattern: Path pattern (supports SQL LIKE wildcards)
            limit: Maximum results

        Returns:
            Matching documents
        """
        return await self.find_many(
            "vault_id = ? AND file_path LIKE ?",
            (vault_id, path_pattern),
            limit=limit,
            order_by="file_path",
        )


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime string.

    Args:
        value: ISO datetime string or None

    Returns:
        Parsed datetime or None
    """
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logger.warning(f"Invalid datetime format: {value}")
        return None
