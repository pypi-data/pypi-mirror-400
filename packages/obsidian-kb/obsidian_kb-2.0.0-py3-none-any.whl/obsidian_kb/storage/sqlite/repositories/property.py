"""Property repository for SQLite storage.

This module provides repository for managing document properties in SQLite.
Handles CRUD operations and specialized queries for frontmatter properties.
"""

import logging
from dataclasses import dataclass
from typing import Any

from obsidian_kb.storage.sqlite.frontmatter_parser import (
    FrontmatterParseResult,
    ParsedProperty,
    PropertyValueType,
)
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


@dataclass
class DocumentProperty:
    """Document property entity for SQLite storage.

    Represents a single property value from document frontmatter.

    Attributes:
        id: Database primary key (None for new entities)
        document_id: Foreign key to documents table
        property_key: Property key (e.g., "status", "tags")
        property_value: String representation of value
        value_type: Type of value (string, number, date, boolean, link)
        value_number: Numeric value if applicable
        value_date: ISO 8601 date string if applicable
        value_link_target: Link target if value is a [[wikilink]]
        list_index: Index in array (0 for non-array values)
    """

    document_id: int
    property_key: str
    value_type: str
    property_value: str | None = None
    value_number: float | None = None
    value_date: str | None = None
    value_link_target: str | None = None
    list_index: int = 0
    id: int | None = None


class PropertyRepository(BaseRepository[DocumentProperty]):
    """Repository for document property operations in SQLite.

    Provides CRUD operations and specialized queries for frontmatter
    properties, optimized for filtering and aggregation.

    Usage:
        repo = PropertyRepository(manager)

        # Create properties from parsed frontmatter
        await repo.create_from_parsed(document_id, parse_result)

        # Find documents by property
        doc_ids = await repo.find_by_key_value(vault_id, "status", "active")

        # Find by number range
        doc_ids = await repo.find_by_number_range(vault_id, "priority", 1, 5)
    """

    table_name = "document_properties"

    def __init__(self, manager: SQLiteManager) -> None:
        """Initialize property repository.

        Args:
            manager: SQLiteManager instance
        """
        super().__init__(manager)

    def _row_to_entity(self, row: dict[str, Any]) -> DocumentProperty:
        """Convert database row to DocumentProperty entity.

        Args:
            row: Database row as dict

        Returns:
            DocumentProperty instance
        """
        return DocumentProperty(
            id=row["id"],
            document_id=row["document_id"],
            property_key=row["property_key"],
            property_value=row.get("property_value"),
            value_type=row["value_type"],
            value_number=row.get("value_number"),
            value_date=row.get("value_date"),
            value_link_target=row.get("value_link_target"),
            list_index=row.get("list_index", 0),
        )

    def _entity_to_row(self, entity: DocumentProperty) -> dict[str, Any]:
        """Convert DocumentProperty entity to database row.

        Args:
            entity: DocumentProperty instance

        Returns:
            Dict for database operations
        """
        return {
            "document_id": entity.document_id,
            "property_key": entity.property_key,
            "property_value": entity.property_value,
            "value_type": entity.value_type,
            "value_number": entity.value_number,
            "value_date": entity.value_date,
            "value_link_target": entity.value_link_target,
            "list_index": entity.list_index,
        }

    # =========================================================================
    # Create operations
    # =========================================================================

    async def create_from_parsed(
        self,
        document_id: int,
        result: FrontmatterParseResult,
    ) -> int:
        """Create properties from parsed frontmatter.

        Args:
            document_id: Database ID of the document
            result: Parsed frontmatter result

        Returns:
            Number of properties created
        """
        if not result.properties:
            return 0

        entities = [
            self._parsed_to_entity(document_id, prop)
            for prop in result.properties
        ]

        return await self.create_many(entities)

    async def create_from_parsed_property(
        self,
        document_id: int,
        prop: ParsedProperty,
    ) -> int:
        """Create a single property from ParsedProperty.

        Args:
            document_id: Database ID of the document
            prop: Parsed property

        Returns:
            ID of created property
        """
        entity = self._parsed_to_entity(document_id, prop)
        return await self.create(entity)

    def _parsed_to_entity(
        self,
        document_id: int,
        prop: ParsedProperty,
    ) -> DocumentProperty:
        """Convert ParsedProperty to DocumentProperty entity.

        Args:
            document_id: Database ID of the document
            prop: Parsed property

        Returns:
            DocumentProperty entity
        """
        return DocumentProperty(
            document_id=document_id,
            property_key=prop.key,
            property_value=prop.property_value,
            value_type=prop.value_type.value,
            value_number=prop.value_number,
            value_date=prop.value_date,
            value_link_target=prop.value_link_target,
            list_index=prop.list_index,
        )

    # =========================================================================
    # Document-scoped queries
    # =========================================================================

    async def get_document_properties(
        self,
        document_id: int,
    ) -> list[DocumentProperty]:
        """Get all properties for a document.

        Args:
            document_id: Database ID of the document

        Returns:
            List of properties
        """
        return await self.find_many(
            "document_id = ?",
            (document_id,),
            order_by="property_key, list_index",
        )

    async def get_document_property(
        self,
        document_id: int,
        key: str,
    ) -> list[DocumentProperty]:
        """Get specific property for a document.

        Returns all values if property is a list.

        Args:
            document_id: Database ID of the document
            key: Property key

        Returns:
            List of properties (multiple for list values)
        """
        return await self.find_many(
            "document_id = ? AND property_key = ?",
            (document_id, key),
            order_by="list_index",
        )

    async def delete_document_properties(self, document_id: int) -> int:
        """Delete all properties for a document.

        Args:
            document_id: Database ID of the document

        Returns:
            Number of deleted properties
        """
        return await self.delete_where("document_id = ?", (document_id,))

    # =========================================================================
    # Vault-scoped search queries
    # =========================================================================

    async def find_by_key(
        self,
        vault_id: int,
        key: str,
    ) -> list[int]:
        """Find all documents with a specific property key.

        Args:
            vault_id: Vault database ID
            key: Property key to search for

        Returns:
            List of document IDs
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ? AND dp.property_key = ?
            """,
            (vault_id, key),
        )
        return [row["document_id"] for row in rows]

    async def find_by_key_value(
        self,
        vault_id: int,
        key: str,
        value: str,
    ) -> list[int]:
        """Find documents with exact property key-value match.

        Args:
            vault_id: Vault database ID
            key: Property key
            value: Property value (exact match)

        Returns:
            List of document IDs
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.property_value = ?
            """,
            (vault_id, key, value),
        )
        return [row["document_id"] for row in rows]

    async def find_by_key_value_like(
        self,
        vault_id: int,
        key: str,
        pattern: str,
    ) -> list[int]:
        """Find documents with property value matching pattern.

        Args:
            vault_id: Vault database ID
            key: Property key
            pattern: SQL LIKE pattern (e.g., "%active%")

        Returns:
            List of document IDs
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.property_value LIKE ?
            """,
            (vault_id, key, pattern),
        )
        return [row["document_id"] for row in rows]

    async def find_by_number_range(
        self,
        vault_id: int,
        key: str,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> list[int]:
        """Find documents with numeric property in range.

        Args:
            vault_id: Vault database ID
            key: Property key
            min_value: Minimum value (inclusive), None for no lower bound
            max_value: Maximum value (inclusive), None for no upper bound

        Returns:
            List of document IDs
        """
        sql = """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.value_type = 'number'
              AND dp.value_number IS NOT NULL
        """
        params: list[Any] = [vault_id, key]

        if min_value is not None:
            sql += " AND dp.value_number >= ?"
            params.append(min_value)

        if max_value is not None:
            sql += " AND dp.value_number <= ?"
            params.append(max_value)

        rows = await self._manager.fetch_all(sql, params)
        return [row["document_id"] for row in rows]

    async def find_by_date_range(
        self,
        vault_id: int,
        key: str,
        after: str | None = None,
        before: str | None = None,
    ) -> list[int]:
        """Find documents with date property in range.

        Args:
            vault_id: Vault database ID
            key: Property key
            after: Minimum date (inclusive, ISO 8601), None for no lower bound
            before: Maximum date (inclusive, ISO 8601), None for no upper bound

        Returns:
            List of document IDs
        """
        sql = """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.value_type = 'date'
              AND dp.value_date IS NOT NULL
        """
        params: list[Any] = [vault_id, key]

        if after is not None:
            sql += " AND dp.value_date >= ?"
            params.append(after)

        if before is not None:
            sql += " AND dp.value_date <= ?"
            params.append(before)

        rows = await self._manager.fetch_all(sql, params)
        return [row["document_id"] for row in rows]

    async def find_by_link_target(
        self,
        vault_id: int,
        target: str,
    ) -> list[int]:
        """Find documents with property linking to target.

        Args:
            vault_id: Vault database ID
            target: Link target (without brackets)

        Returns:
            List of document IDs
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.value_type = 'link'
              AND dp.value_link_target = ?
            """,
            (vault_id, target),
        )
        return [row["document_id"] for row in rows]

    async def find_by_boolean(
        self,
        vault_id: int,
        key: str,
        value: bool,
    ) -> list[int]:
        """Find documents with boolean property value.

        Args:
            vault_id: Vault database ID
            key: Property key
            value: Boolean value to match

        Returns:
            List of document IDs
        """
        str_values = ("true", "yes") if value else ("false", "no")

        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.document_id
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.value_type = 'boolean'
              AND dp.property_value IN (?, ?)
            """,
            (vault_id, key, str_values[0], str_values[1]),
        )
        return [row["document_id"] for row in rows]

    # =========================================================================
    # Aggregation queries
    # =========================================================================

    async def get_unique_keys(self, vault_id: int) -> list[str]:
        """Get all unique property keys in a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            List of unique property keys
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.property_key
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
            ORDER BY dp.property_key
            """,
            (vault_id,),
        )
        return [row["property_key"] for row in rows]

    async def get_unique_values(
        self,
        vault_id: int,
        key: str,
        limit: int = 100,
    ) -> list[str]:
        """Get unique values for a property key.

        Args:
            vault_id: Vault database ID
            key: Property key
            limit: Maximum number of values to return

        Returns:
            List of unique values
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.property_value
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.property_value IS NOT NULL
            ORDER BY dp.property_value
            LIMIT ?
            """,
            (vault_id, key, limit),
        )
        return [row["property_value"] for row in rows]

    async def get_value_counts(
        self,
        vault_id: int,
        key: str,
    ) -> dict[str, int]:
        """Get count of documents for each value of a property.

        Args:
            vault_id: Vault database ID
            key: Property key

        Returns:
            Dict mapping values to document counts
        """
        rows = await self._manager.fetch_all(
            """
            SELECT dp.property_value, COUNT(DISTINCT dp.document_id) as count
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.property_value IS NOT NULL
            GROUP BY dp.property_value
            ORDER BY count DESC
            """,
            (vault_id, key),
        )
        return {row["property_value"]: row["count"] for row in rows}

    async def get_key_statistics(
        self,
        vault_id: int,
        key: str,
    ) -> dict[str, Any]:
        """Get statistics for a numeric property.

        Args:
            vault_id: Vault database ID
            key: Property key

        Returns:
            Dict with min, max, avg, count statistics
        """
        row = await self._manager.fetch_one(
            """
            SELECT
                MIN(dp.value_number) as min_value,
                MAX(dp.value_number) as max_value,
                AVG(dp.value_number) as avg_value,
                COUNT(DISTINCT dp.document_id) as document_count
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.value_type = 'number'
              AND dp.value_number IS NOT NULL
            """,
            (vault_id, key),
        )

        if row is None:
            return {
                "min_value": None,
                "max_value": None,
                "avg_value": None,
                "document_count": 0,
            }

        return {
            "min_value": row["min_value"],
            "max_value": row["max_value"],
            "avg_value": row["avg_value"],
            "document_count": row["document_count"],
        }

    async def get_link_targets(self, vault_id: int) -> list[str]:
        """Get all unique link targets from properties.

        Args:
            vault_id: Vault database ID

        Returns:
            List of unique link targets
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.value_link_target
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.value_type = 'link'
              AND dp.value_link_target IS NOT NULL
            ORDER BY dp.value_link_target
            """,
            (vault_id,),
        )
        return [row["value_link_target"] for row in rows]

    # =========================================================================
    # Batch operations
    # =========================================================================

    async def replace_document_properties(
        self,
        document_id: int,
        result: FrontmatterParseResult,
    ) -> int:
        """Replace all properties for a document.

        Deletes existing properties and creates new ones from
        parsed frontmatter within a transaction.

        Args:
            document_id: Database ID of the document
            result: Parsed frontmatter result

        Returns:
            Number of properties created
        """
        async with self._manager.transaction() as conn:
            # Delete existing properties
            await conn.execute(
                "DELETE FROM document_properties WHERE document_id = ?",
                (document_id,),
            )

            if not result.properties:
                return 0

            # Insert new properties
            for prop in result.properties:
                entity = self._parsed_to_entity(document_id, prop)
                row = self._entity_to_row(entity)
                columns = ", ".join(row.keys())
                placeholders = ", ".join("?" * len(row))

                await conn.execute(
                    f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                    tuple(row.values()),
                )

        return len(result.properties)

    async def delete_by_vault(self, vault_id: int) -> int:
        """Delete all properties for documents in a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            Number of deleted properties
        """
        cursor = await self._manager.execute(
            """
            DELETE FROM document_properties
            WHERE document_id IN (
                SELECT id FROM documents WHERE vault_id = ?
            )
            """,
            (vault_id,),
        )
        return cursor.rowcount
