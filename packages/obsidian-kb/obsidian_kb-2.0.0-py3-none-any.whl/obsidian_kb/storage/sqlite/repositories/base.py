"""Base repository class for SQLite storage.

This module provides the abstract base class for all SQLite repositories,
implementing common CRUD operations and transaction support.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from obsidian_kb.storage.sqlite.manager import SQLiteManager

logger = logging.getLogger(__name__)

# Generic type for entity
T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for SQLite repositories.

    Provides common CRUD operations and transaction support.
    Subclasses must implement abstract methods for specific entities.

    Type Parameters:
        T: Entity type this repository manages

    Attributes:
        manager: SQLiteManager instance for database access
        table_name: Name of the database table

    Usage:
        class UserRepository(BaseRepository[User]):
            table_name = "users"

            def _row_to_entity(self, row: dict) -> User:
                return User(**row)

            def _entity_to_row(self, entity: User) -> dict:
                return {"name": entity.name, "email": entity.email}
    """

    # Subclasses must set this
    table_name: str = ""

    def __init__(self, manager: SQLiteManager) -> None:
        """Initialize repository with SQLite manager.

        Args:
            manager: SQLiteManager instance
        """
        if not self.table_name:
            raise ValueError(f"{self.__class__.__name__} must define table_name")

        self._manager = manager

    @property
    def manager(self) -> SQLiteManager:
        """Get the SQLite manager."""
        return self._manager

    # =========================================================================
    # Abstract methods - must be implemented by subclasses
    # =========================================================================

    @abstractmethod
    def _row_to_entity(self, row: dict[str, Any]) -> T:
        """Convert database row to entity.

        Args:
            row: Database row as dict

        Returns:
            Entity instance
        """
        ...

    @abstractmethod
    def _entity_to_row(self, entity: T) -> dict[str, Any]:
        """Convert entity to database row.

        Args:
            entity: Entity instance

        Returns:
            Dict suitable for database insert/update
        """
        ...

    # =========================================================================
    # Common CRUD operations
    # =========================================================================

    async def get_by_id(self, id_value: int) -> T | None:
        """Get entity by primary key ID.

        Args:
            id_value: Primary key value

        Returns:
            Entity if found, None otherwise
        """
        row = await self._manager.fetch_one(
            f"SELECT * FROM {self.table_name} WHERE id = ?",
            (id_value,),
        )
        if row is None:
            return None
        return self._row_to_entity(row)

    async def get_all(self, limit: int | None = None, offset: int = 0) -> list[T]:
        """Get all entities with optional pagination.

        Args:
            limit: Maximum number of results (None for all)
            offset: Number of results to skip

        Returns:
            List of entities
        """
        sql = f"SELECT * FROM {self.table_name}"
        params: list[Any] = []

        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        rows = await self._manager.fetch_all(sql, params if params else None)
        return [self._row_to_entity(row) for row in rows]

    async def count(self, where: str | None = None, params: tuple[Any, ...] | None = None) -> int:
        """Count entities with optional filter.

        Args:
            where: Optional WHERE clause (without 'WHERE' keyword)
            params: Optional parameters for WHERE clause

        Returns:
            Count of matching entities
        """
        sql = f"SELECT COUNT(*) as count FROM {self.table_name}"
        if where:
            sql += f" WHERE {where}"

        result = await self._manager.fetch_value(sql, params)
        return result or 0

    async def exists(self, id_value: int) -> bool:
        """Check if entity exists by ID.

        Args:
            id_value: Primary key value

        Returns:
            True if entity exists
        """
        count = await self.count("id = ?", (id_value,))
        return count > 0

    async def create(self, entity: T) -> int:
        """Create new entity.

        Args:
            entity: Entity to create

        Returns:
            ID of created entity
        """
        row = self._entity_to_row(entity)
        columns = ", ".join(row.keys())
        placeholders = ", ".join("?" * len(row))

        cursor = await self._manager.execute(
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
            tuple(row.values()),
        )
        return cursor.lastrowid or 0

    async def create_many(self, entities: list[T]) -> int:
        """Create multiple entities.

        Args:
            entities: List of entities to create

        Returns:
            Number of created entities
        """
        if not entities:
            return 0

        rows = [self._entity_to_row(e) for e in entities]
        columns = ", ".join(rows[0].keys())
        placeholders = ", ".join("?" * len(rows[0]))

        cursor = await self._manager.execute_many(
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
            [tuple(row.values()) for row in rows],
        )
        return cursor.rowcount

    async def update(self, id_value: int, entity: T) -> bool:
        """Update existing entity.

        Args:
            id_value: Primary key of entity to update
            entity: Entity with updated values

        Returns:
            True if entity was updated
        """
        row = self._entity_to_row(entity)
        set_clause = ", ".join(f"{k} = ?" for k in row.keys())

        cursor = await self._manager.execute(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?",
            (*row.values(), id_value),
        )
        return cursor.rowcount > 0

    async def update_fields(
        self,
        id_value: int,
        fields: dict[str, Any],
    ) -> bool:
        """Update specific fields of an entity.

        Args:
            id_value: Primary key of entity to update
            fields: Dict of field names to new values

        Returns:
            True if entity was updated
        """
        if not fields:
            return False

        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())

        cursor = await self._manager.execute(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?",
            (*fields.values(), id_value),
        )
        return cursor.rowcount > 0

    async def delete(self, id_value: int) -> bool:
        """Delete entity by ID.

        Args:
            id_value: Primary key of entity to delete

        Returns:
            True if entity was deleted
        """
        cursor = await self._manager.execute(
            f"DELETE FROM {self.table_name} WHERE id = ?",
            (id_value,),
        )
        return cursor.rowcount > 0

    async def delete_where(
        self,
        where: str,
        params: tuple[Any, ...] | None = None,
    ) -> int:
        """Delete entities matching condition.

        Args:
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause

        Returns:
            Number of deleted entities
        """
        cursor = await self._manager.execute(
            f"DELETE FROM {self.table_name} WHERE {where}",
            params,
        )
        return cursor.rowcount

    # =========================================================================
    # Query helpers
    # =========================================================================

    async def find_one(
        self,
        where: str,
        params: tuple[Any, ...] | None = None,
    ) -> T | None:
        """Find single entity matching condition.

        Args:
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause

        Returns:
            Entity if found, None otherwise
        """
        row = await self._manager.fetch_one(
            f"SELECT * FROM {self.table_name} WHERE {where} LIMIT 1",
            params,
        )
        if row is None:
            return None
        return self._row_to_entity(row)

    async def find_many(
        self,
        where: str,
        params: tuple[Any, ...] | None = None,
        limit: int | None = None,
        offset: int = 0,
        order_by: str | None = None,
    ) -> list[T]:
        """Find entities matching condition.

        Args:
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: ORDER BY clause (without 'ORDER BY' keyword)

        Returns:
            List of matching entities
        """
        sql = f"SELECT * FROM {self.table_name} WHERE {where}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit is not None:
            sql += f" LIMIT {limit} OFFSET {offset}"

        rows = await self._manager.fetch_all(sql, params)
        return [self._row_to_entity(row) for row in rows]

    async def find_ids(
        self,
        where: str,
        params: tuple[Any, ...] | None = None,
    ) -> list[int]:
        """Find IDs of entities matching condition.

        Args:
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause

        Returns:
            List of matching entity IDs
        """
        rows = await self._manager.fetch_all(
            f"SELECT id FROM {self.table_name} WHERE {where}",
            params,
        )
        return [row["id"] for row in rows]

    # =========================================================================
    # Transaction support
    # =========================================================================

    async def create_in_transaction(
        self,
        conn: Any,
        entity: T,
    ) -> int:
        """Create entity within existing transaction.

        Args:
            conn: Database connection in transaction
            entity: Entity to create

        Returns:
            ID of created entity
        """
        row = self._entity_to_row(entity)
        columns = ", ".join(row.keys())
        placeholders = ", ".join("?" * len(row))

        cursor = await conn.execute(
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
            tuple(row.values()),
        )
        return cursor.lastrowid or 0

    async def update_in_transaction(
        self,
        conn: Any,
        id_value: int,
        entity: T,
    ) -> bool:
        """Update entity within existing transaction.

        Args:
            conn: Database connection in transaction
            id_value: Primary key of entity to update
            entity: Entity with updated values

        Returns:
            True if entity was updated
        """
        row = self._entity_to_row(entity)
        set_clause = ", ".join(f"{k} = ?" for k in row.keys())

        cursor = await conn.execute(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?",
            (*row.values(), id_value),
        )
        return cursor.rowcount > 0

    async def delete_in_transaction(
        self,
        conn: Any,
        id_value: int,
    ) -> bool:
        """Delete entity within existing transaction.

        Args:
            conn: Database connection in transaction
            id_value: Primary key of entity to delete

        Returns:
            True if entity was deleted
        """
        cursor = await conn.execute(
            f"DELETE FROM {self.table_name} WHERE id = ?",
            (id_value,),
        )
        return cursor.rowcount > 0
