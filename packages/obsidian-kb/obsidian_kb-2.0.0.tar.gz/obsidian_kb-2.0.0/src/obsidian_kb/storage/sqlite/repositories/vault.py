"""Vault repository for SQLite storage.

This module provides repository for managing vault metadata in SQLite.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


@dataclass
class Vault:
    """Vault entity representing an Obsidian vault.

    Attributes:
        id: Database primary key (None for new entities)
        name: Unique vault name
        path: Filesystem path to vault
        created_at: When vault was added
        last_indexed_at: When vault was last indexed
        document_count: Number of documents in vault
        chunk_count: Number of chunks in vault
        settings: Vault-specific settings
    """

    name: str
    path: str
    id: int | None = None
    created_at: datetime | None = None
    last_indexed_at: datetime | None = None
    document_count: int = 0
    chunk_count: int = 0
    settings: dict[str, Any] = field(default_factory=dict)


class VaultRepository(BaseRepository[Vault]):
    """Repository for vault metadata operations.

    Provides CRUD operations and specialized queries for vaults.

    Usage:
        repo = VaultRepository(manager)

        # Create vault
        vault = Vault(name="my-vault", path="/path/to/vault")
        vault_id = await repo.create(vault)

        # Find by name
        vault = await repo.get_by_name("my-vault")

        # Update index stats
        await repo.update_index_stats("my-vault", document_count=100, chunk_count=500)
    """

    table_name = "vaults"

    def __init__(self, manager: SQLiteManager) -> None:
        """Initialize vault repository.

        Args:
            manager: SQLiteManager instance
        """
        super().__init__(manager)

    def _row_to_entity(self, row: dict[str, Any]) -> Vault:
        """Convert database row to Vault entity.

        Args:
            row: Database row as dict

        Returns:
            Vault instance
        """
        settings = {}
        if row.get("settings_json"):
            try:
                settings = json.loads(row["settings_json"])
            except json.JSONDecodeError:
                logger.warning(f"Invalid settings JSON for vault {row.get('name')}")

        return Vault(
            id=row["id"],
            name=row["name"],
            path=row["path"],
            created_at=_parse_datetime(row.get("created_at")),
            last_indexed_at=_parse_datetime(row.get("last_indexed_at")),
            document_count=row.get("document_count", 0),
            chunk_count=row.get("chunk_count", 0),
            settings=settings,
        )

    def _entity_to_row(self, entity: Vault) -> dict[str, Any]:
        """Convert Vault entity to database row.

        Args:
            entity: Vault instance

        Returns:
            Dict for database operations
        """
        row: dict[str, Any] = {
            "name": entity.name,
            "path": entity.path,
            "document_count": entity.document_count,
            "chunk_count": entity.chunk_count,
        }

        if entity.last_indexed_at:
            row["last_indexed_at"] = entity.last_indexed_at.isoformat()

        if entity.settings:
            row["settings_json"] = json.dumps(entity.settings)

        return row

    # =========================================================================
    # Specialized queries
    # =========================================================================

    async def get_by_name(self, name: str) -> Vault | None:
        """Get vault by unique name.

        Args:
            name: Vault name

        Returns:
            Vault if found, None otherwise
        """
        return await self.find_one("name = ?", (name,))

    async def exists_by_name(self, name: str) -> bool:
        """Check if vault exists by name.

        Args:
            name: Vault name

        Returns:
            True if vault exists
        """
        count = await self.count("name = ?", (name,))
        return count > 0

    async def get_id_by_name(self, name: str) -> int | None:
        """Get vault ID by name.

        Args:
            name: Vault name

        Returns:
            Vault ID if found, None otherwise
        """
        result = await self._manager.fetch_value(
            "SELECT id FROM vaults WHERE name = ?",
            (name,),
        )
        return result

    async def list_all(self) -> list[Vault]:
        """List all vaults.

        Returns:
            List of all vaults
        """
        return await self.get_all()

    async def list_names(self) -> list[str]:
        """List all vault names.

        Returns:
            List of vault names
        """
        rows = await self._manager.fetch_all("SELECT name FROM vaults ORDER BY name")
        return [row["name"] for row in rows]

    # =========================================================================
    # Update operations
    # =========================================================================

    async def update_index_stats(
        self,
        name: str,
        document_count: int,
        chunk_count: int,
    ) -> bool:
        """Update vault indexing statistics.

        Args:
            name: Vault name
            document_count: New document count
            chunk_count: New chunk count

        Returns:
            True if vault was updated
        """
        cursor = await self._manager.execute(
            """
            UPDATE vaults SET
                document_count = ?,
                chunk_count = ?,
                last_indexed_at = datetime('now')
            WHERE name = ?
            """,
            (document_count, chunk_count, name),
        )
        return cursor.rowcount > 0

    async def touch_indexed(self, name: str) -> bool:
        """Update last_indexed_at timestamp.

        Args:
            name: Vault name

        Returns:
            True if vault was updated
        """
        cursor = await self._manager.execute(
            "UPDATE vaults SET last_indexed_at = datetime('now') WHERE name = ?",
            (name,),
        )
        return cursor.rowcount > 0

    async def update_settings(
        self,
        name: str,
        settings: dict[str, Any],
    ) -> bool:
        """Update vault settings.

        Args:
            name: Vault name
            settings: New settings dict

        Returns:
            True if vault was updated
        """
        cursor = await self._manager.execute(
            "UPDATE vaults SET settings_json = ? WHERE name = ?",
            (json.dumps(settings), name),
        )
        return cursor.rowcount > 0

    # =========================================================================
    # Delete operations
    # =========================================================================

    async def delete_by_name(self, name: str) -> bool:
        """Delete vault by name.

        Args:
            name: Vault name

        Returns:
            True if vault was deleted
        """
        cursor = await self._manager.execute(
            "DELETE FROM vaults WHERE name = ?",
            (name,),
        )
        return cursor.rowcount > 0

    # =========================================================================
    # Upsert operations
    # =========================================================================

    async def upsert(self, vault: Vault) -> int:
        """Create or update vault.

        Creates vault if it doesn't exist, updates if it does.

        Args:
            vault: Vault entity

        Returns:
            Vault ID (existing or new)
        """
        existing = await self.get_by_name(vault.name)
        if existing:
            # Update existing
            row = self._entity_to_row(vault)
            set_clause = ", ".join(f"{k} = ?" for k in row.keys())
            await self._manager.execute(
                f"UPDATE vaults SET {set_clause} WHERE name = ?",
                (*row.values(), vault.name),
            )
            return existing.id or 0
        else:
            # Create new
            return await self.create(vault)


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
