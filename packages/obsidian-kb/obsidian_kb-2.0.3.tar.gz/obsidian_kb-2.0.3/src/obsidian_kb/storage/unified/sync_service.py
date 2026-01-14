"""Metadata Sync Service for synchronizing SQLite and LanceDB.

This module provides synchronization between SQLite and LanceDB storage
backends, ensuring metadata consistency.

Phase 2.0.5 - Unified Metadata Access Layer
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any

from obsidian_kb.storage.unified.types import (
    ConsistencyReport,
    DataSource,
    SyncResult,
    UnifiedDocumentInfo,
)

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager
    from obsidian_kb.storage.sqlite.manager import SQLiteManager
    from obsidian_kb.storage.sqlite.repositories.document import (
        SQLiteDocument,
        SQLiteDocumentRepository,
    )
    from obsidian_kb.storage.sqlite.repositories.vault import VaultRepository

logger = logging.getLogger(__name__)


class MetadataSyncService:
    """Service for synchronizing metadata between SQLite and LanceDB.

    Provides:
    - Full vault synchronization
    - Single document synchronization
    - Consistency verification

    The sync direction is typically LanceDB → SQLite, since LanceDB is the
    primary storage for indexed data and SQLite is the metadata cache.

    Usage:
        sync_service = MetadataSyncService(
            sqlite_manager=sqlite_manager,
            lancedb_manager=lancedb_manager,
        )

        # Sync entire vault
        result = await sync_service.sync_vault("my-vault")

        # Sync single document
        result = await sync_service.sync_document("vault::path/to/note.md")

        # Verify consistency
        report = await sync_service.verify_consistency("my-vault")
    """

    def __init__(
        self,
        sqlite_manager: "SQLiteManager | None" = None,
        lancedb_manager: "LanceDBManager | None" = None,
        document_repo: "SQLiteDocumentRepository | None" = None,
        vault_repo: "VaultRepository | None" = None,
    ) -> None:
        """Initialize the sync service.

        Args:
            sqlite_manager: SQLiteManager instance
            lancedb_manager: LanceDBManager instance
            document_repo: SQLiteDocumentRepository (optional, created from manager)
            vault_repo: VaultRepository (optional, created from manager)
        """
        self._sqlite_manager = sqlite_manager
        self._lancedb_manager = lancedb_manager
        self._document_repo = document_repo
        self._vault_repo = vault_repo
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

    # =========================================================================
    # Full Vault Sync
    # =========================================================================

    async def sync_vault(
        self,
        vault_name: str,
        direction: str = "lancedb_to_sqlite",
    ) -> SyncResult:
        """Synchronize all documents in a vault.

        Args:
            vault_name: Vault name
            direction: Sync direction ("lancedb_to_sqlite" or "sqlite_to_lancedb")

        Returns:
            SyncResult with statistics
        """
        start_time = time.monotonic()
        result = SyncResult(vault_name=vault_name)

        await self._ensure_repos()

        if direction == "lancedb_to_sqlite":
            result = await self._sync_lancedb_to_sqlite(vault_name, result)
        elif direction == "sqlite_to_lancedb":
            result = await self._sync_sqlite_to_lancedb(vault_name, result)
        else:
            result.errors.append(f"Unknown sync direction: {direction}")
            result.success = False

        result.duration_ms = (time.monotonic() - start_time) * 1000
        return result

    async def _sync_lancedb_to_sqlite(
        self,
        vault_name: str,
        result: SyncResult,
    ) -> SyncResult:
        """Sync from LanceDB to SQLite."""
        if not self._lancedb_manager or not self._sqlite_manager:
            result.errors.append("Both LanceDB and SQLite managers are required")
            result.success = False
            return result

        try:
            # Get documents from LanceDB
            lance_docs = await self._get_lancedb_documents(vault_name)
            if not lance_docs:
                logger.info(f"No documents found in LanceDB for vault {vault_name}")
                return result

            # Ensure vault exists in SQLite
            vault_id = await self._ensure_vault_in_sqlite(vault_name)
            if not vault_id:
                result.errors.append(f"Failed to create/get vault {vault_name} in SQLite")
                result.success = False
                return result

            # Get existing documents from SQLite
            existing_docs = await self._get_sqlite_document_map(vault_id)

            # Sync each document
            for lance_doc in lance_docs:
                try:
                    doc_id = lance_doc.get("document_id", "")
                    if not doc_id:
                        continue

                    if doc_id in existing_docs:
                        # Update existing
                        await self._update_sqlite_document(
                            existing_docs[doc_id], lance_doc, vault_id
                        )
                        result.documents_updated += 1
                    else:
                        # Create new
                        await self._create_sqlite_document(lance_doc, vault_id)
                        result.documents_created += 1

                    result.documents_synced += 1

                except Exception as e:
                    result.errors.append(f"Error syncing document {doc_id}: {e}")

            # Handle documents that exist in SQLite but not in LanceDB
            lance_doc_ids = {d.get("document_id", "") for d in lance_docs}
            for doc_id, sqlite_id in existing_docs.items():
                if doc_id not in lance_doc_ids:
                    try:
                        await self._document_repo.delete(sqlite_id)
                        result.documents_deleted += 1
                    except Exception as e:
                        result.errors.append(f"Error deleting document {doc_id}: {e}")

        except Exception as e:
            result.errors.append(f"Sync failed: {e}")
            logger.exception(f"Failed to sync vault {vault_name}")

        result.success = len(result.errors) == 0
        return result

    async def _sync_sqlite_to_lancedb(
        self,
        vault_name: str,
        result: SyncResult,
    ) -> SyncResult:
        """Sync from SQLite to LanceDB.

        Note: This is typically not needed as LanceDB is the primary storage.
        SQLite is used as a metadata cache for faster queries.
        """
        result.errors.append("sqlite_to_lancedb sync not implemented - LanceDB is primary storage")
        result.success = False
        return result

    async def _get_lancedb_documents(self, vault_name: str) -> list[dict[str, Any]]:
        """Get all documents from LanceDB."""
        if not self._lancedb_manager:
            return []

        try:
            documents_table = await self._lancedb_manager._ensure_table(vault_name, "documents")

            def _get_docs() -> list[dict[str, Any]]:
                try:
                    arrow_table = documents_table.to_arrow()
                    return arrow_table.to_pylist()
                except Exception:
                    return []

            return await asyncio.to_thread(_get_docs)
        except Exception as e:
            logger.warning(f"Failed to get documents from LanceDB: {e}")
            return []

    async def _ensure_vault_in_sqlite(self, vault_name: str) -> int | None:
        """Ensure vault exists in SQLite and return its ID."""
        if not self._vault_repo:
            return None

        try:
            vault = await self._vault_repo.get_by_name(vault_name)
            if vault and vault.id:
                return vault.id

            # Create new vault
            from obsidian_kb.storage.sqlite.repositories.vault import Vault

            new_vault = Vault(name=vault_name, path="")
            vault_id = await self._vault_repo.create(new_vault)
            return vault_id
        except Exception as e:
            logger.error(f"Failed to ensure vault in SQLite: {e}")
            return None

    async def _get_sqlite_document_map(self, vault_id: int) -> dict[str, int]:
        """Get mapping of document_id to SQLite id."""
        if not self._document_repo:
            return {}

        try:
            docs = await self._document_repo.find_by_vault(vault_id)
            return {doc.document_id: doc.id or 0 for doc in docs if doc.id}
        except Exception as e:
            logger.warning(f"Failed to get SQLite documents: {e}")
            return {}

    async def _create_sqlite_document(
        self,
        lance_doc: dict[str, Any],
        vault_id: int,
    ) -> int | None:
        """Create a new document in SQLite from LanceDB data."""
        if not self._document_repo:
            return None

        try:
            from obsidian_kb.storage.sqlite.repositories.document import SQLiteDocument

            doc = SQLiteDocument(
                document_id=lance_doc.get("document_id", ""),
                vault_id=vault_id,
                file_path=lance_doc.get("file_path", ""),
                file_name=lance_doc.get("file_name", ""),
                title=lance_doc.get("title"),
                content_hash=lance_doc.get("content_hash", ""),
                file_size=lance_doc.get("file_size", 0),
                chunk_count=lance_doc.get("chunk_count", 0),
                created_at=self._parse_datetime(lance_doc.get("created_at")),
                modified_at=self._parse_datetime(lance_doc.get("modified_at")),
            )

            return await self._document_repo.create(doc)
        except Exception as e:
            logger.error(f"Failed to create document in SQLite: {e}")
            return None

    async def _update_sqlite_document(
        self,
        sqlite_id: int,
        lance_doc: dict[str, Any],
        vault_id: int,
    ) -> bool:
        """Update an existing document in SQLite from LanceDB data."""
        if not self._document_repo:
            return False

        try:
            from obsidian_kb.storage.sqlite.repositories.document import SQLiteDocument

            doc = SQLiteDocument(
                id=sqlite_id,
                document_id=lance_doc.get("document_id", ""),
                vault_id=vault_id,
                file_path=lance_doc.get("file_path", ""),
                file_name=lance_doc.get("file_name", ""),
                title=lance_doc.get("title"),
                content_hash=lance_doc.get("content_hash", ""),
                file_size=lance_doc.get("file_size", 0),
                chunk_count=lance_doc.get("chunk_count", 0),
                created_at=self._parse_datetime(lance_doc.get("created_at")),
                modified_at=self._parse_datetime(lance_doc.get("modified_at")),
            )

            return await self._document_repo.update(sqlite_id, doc)
        except Exception as e:
            logger.error(f"Failed to update document in SQLite: {e}")
            return False

    def _parse_datetime(self, value: Any) -> datetime | None:
        """Parse datetime from various formats."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    # =========================================================================
    # Single Document Sync
    # =========================================================================

    async def sync_document(
        self,
        document_id: str,
        direction: str = "lancedb_to_sqlite",
    ) -> SyncResult:
        """Synchronize a single document.

        Args:
            document_id: Document ID (vault_name::file_path)
            direction: Sync direction

        Returns:
            SyncResult with statistics
        """
        start_time = time.monotonic()
        vault_name = document_id.split("::", 1)[0] if "::" in document_id else ""
        result = SyncResult(vault_name=vault_name)

        await self._ensure_repos()

        if direction != "lancedb_to_sqlite":
            result.errors.append(f"Direction {direction} not supported for single document sync")
            result.success = False
            result.duration_ms = (time.monotonic() - start_time) * 1000
            return result

        if not self._lancedb_manager or not self._sqlite_manager:
            result.errors.append("Both LanceDB and SQLite managers are required")
            result.success = False
            result.duration_ms = (time.monotonic() - start_time) * 1000
            return result

        try:
            # Get document from LanceDB
            lance_doc = await self._get_lancedb_document(vault_name, document_id)

            # Ensure vault exists
            vault_id = await self._ensure_vault_in_sqlite(vault_name)
            if not vault_id:
                result.errors.append(f"Failed to create/get vault {vault_name}")
                result.success = False
                result.duration_ms = (time.monotonic() - start_time) * 1000
                return result

            if lance_doc:
                # Check if exists in SQLite
                if self._document_repo:
                    existing = await self._document_repo.get_by_document_id(document_id)
                    if existing and existing.id:
                        await self._update_sqlite_document(existing.id, lance_doc, vault_id)
                        result.documents_updated += 1
                    else:
                        await self._create_sqlite_document(lance_doc, vault_id)
                        result.documents_created += 1
                    result.documents_synced += 1
            else:
                # Document doesn't exist in LanceDB, delete from SQLite
                if self._document_repo:
                    deleted = await self._document_repo.delete_by_document_id(document_id)
                    if deleted:
                        result.documents_deleted += 1

        except Exception as e:
            result.errors.append(f"Sync failed: {e}")
            logger.exception(f"Failed to sync document {document_id}")

        result.success = len(result.errors) == 0
        result.duration_ms = (time.monotonic() - start_time) * 1000
        return result

    async def _get_lancedb_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, Any] | None:
        """Get a single document from LanceDB."""
        if not self._lancedb_manager:
            return None

        try:
            documents_table = await self._lancedb_manager._ensure_table(vault_name, "documents")

            def _get_doc() -> dict[str, Any] | None:
                try:
                    safe_id = document_id.replace("'", "''")
                    arrow_table = (
                        documents_table.search()
                        .where(f"document_id = '{safe_id}'")
                        .limit(1)
                        .to_arrow()
                    )
                    if arrow_table.num_rows > 0:
                        return arrow_table.to_pylist()[0]
                    return None
                except Exception:
                    return None

            return await asyncio.to_thread(_get_doc)
        except Exception as e:
            logger.warning(f"Failed to get document from LanceDB: {e}")
            return None

    # =========================================================================
    # Consistency Verification
    # =========================================================================

    async def verify_consistency(
        self,
        vault_name: str,
    ) -> ConsistencyReport:
        """Verify consistency between SQLite and LanceDB for a vault.

        Args:
            vault_name: Vault name

        Returns:
            ConsistencyReport with details of any inconsistencies
        """
        await self._ensure_repos()

        # Get document IDs from both sources
        sqlite_docs = await self._get_sqlite_docs_for_vault(vault_name)
        lancedb_docs = await self._get_lancedb_docs_for_vault(vault_name)

        sqlite_ids = set(sqlite_docs.keys())
        lancedb_ids = set(lancedb_docs.keys())

        # Find differences
        sqlite_only = list(sqlite_ids - lancedb_ids)
        lancedb_only = list(lancedb_ids - sqlite_ids)

        # Check hash mismatches for documents in both
        common_ids = sqlite_ids & lancedb_ids
        hash_mismatches = []
        for doc_id in common_ids:
            sqlite_hash = sqlite_docs[doc_id].get("content_hash", "")
            lancedb_hash = lancedb_docs[doc_id].get("content_hash", "")
            # Only compare if both have hashes
            if sqlite_hash and lancedb_hash and sqlite_hash != lancedb_hash:
                hash_mismatches.append(doc_id)

        total_unique = len(sqlite_ids | lancedb_ids)

        return ConsistencyReport(
            vault_name=vault_name,
            total_documents=total_unique,
            sqlite_count=len(sqlite_ids),
            lancedb_count=len(lancedb_ids),
            sqlite_only=sorted(sqlite_only),
            lancedb_only=sorted(lancedb_only),
            hash_mismatches=sorted(hash_mismatches),
            checked_at=datetime.now(),
        )

    async def _get_sqlite_docs_for_vault(
        self,
        vault_name: str,
    ) -> dict[str, dict[str, Any]]:
        """Get all documents from SQLite for a vault."""
        if not self._document_repo or not self._vault_repo:
            return {}

        try:
            vault = await self._vault_repo.get_by_name(vault_name)
            if not vault or not vault.id:
                return {}

            docs = await self._document_repo.find_by_vault(vault.id)
            return {
                doc.document_id: {
                    "content_hash": doc.content_hash,
                    "chunk_count": doc.chunk_count,
                    "modified_at": doc.modified_at,
                }
                for doc in docs
            }
        except Exception as e:
            logger.warning(f"Failed to get SQLite docs: {e}")
            return {}

    async def _get_lancedb_docs_for_vault(
        self,
        vault_name: str,
    ) -> dict[str, dict[str, Any]]:
        """Get all documents from LanceDB for a vault."""
        if not self._lancedb_manager:
            return {}

        try:
            lance_docs = await self._get_lancedb_documents(vault_name)
            return {
                doc.get("document_id", ""): {
                    "content_hash": doc.get("content_hash", ""),
                    "chunk_count": doc.get("chunk_count", 0),
                    "modified_at": doc.get("modified_at"),
                }
                for doc in lance_docs
                if doc.get("document_id")
            }
        except Exception as e:
            logger.warning(f"Failed to get LanceDB docs: {e}")
            return {}

    # =========================================================================
    # Repair Operations
    # =========================================================================

    async def repair_inconsistencies(
        self,
        vault_name: str,
        report: ConsistencyReport | None = None,
    ) -> SyncResult:
        """Repair inconsistencies found in a consistency report.

        Args:
            vault_name: Vault name
            report: Optional pre-computed ConsistencyReport

        Returns:
            SyncResult with repair statistics
        """
        start_time = time.monotonic()
        result = SyncResult(vault_name=vault_name)

        # Get or compute report
        if report is None:
            report = await self.verify_consistency(vault_name)

        if report.is_consistent:
            result.duration_ms = (time.monotonic() - start_time) * 1000
            return result

        await self._ensure_repos()

        # Sync documents only in LanceDB (create in SQLite)
        for doc_id in report.lancedb_only:
            try:
                doc_result = await self.sync_document(doc_id)
                result.documents_created += doc_result.documents_created
                result.documents_synced += doc_result.documents_synced
                result.errors.extend(doc_result.errors)
            except Exception as e:
                result.errors.append(f"Failed to sync {doc_id}: {e}")

        # Delete documents only in SQLite
        if self._document_repo:
            for doc_id in report.sqlite_only:
                try:
                    deleted = await self._document_repo.delete_by_document_id(doc_id)
                    if deleted:
                        result.documents_deleted += 1
                except Exception as e:
                    result.errors.append(f"Failed to delete {doc_id}: {e}")

        # Re-sync documents with hash mismatches
        for doc_id in report.hash_mismatches:
            try:
                doc_result = await self.sync_document(doc_id)
                result.documents_updated += doc_result.documents_updated
                result.documents_synced += doc_result.documents_synced
                result.errors.extend(doc_result.errors)
            except Exception as e:
                result.errors.append(f"Failed to re-sync {doc_id}: {e}")

        result.success = len(result.errors) == 0
        result.duration_ms = (time.monotonic() - start_time) * 1000
        return result
