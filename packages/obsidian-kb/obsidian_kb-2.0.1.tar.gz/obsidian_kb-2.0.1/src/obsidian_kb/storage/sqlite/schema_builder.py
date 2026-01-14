"""Property schema builder for automatic schema inference.

This module provides automatic schema inference for document properties
in a vault. Analyzes existing properties to determine common types,
sample values, and usage statistics.
"""

import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from obsidian_kb.storage.sqlite.frontmatter_parser import PropertyValueType
from obsidian_kb.storage.sqlite.manager import SQLiteManager

logger = logging.getLogger(__name__)


@dataclass
class PropertySchema:
    """Schema information for a single property key.

    Attributes:
        id: Database primary key (None for new schemas)
        vault_id: Vault database ID
        property_key: Property key name
        inferred_type: Most common type for this property
        sample_values: Sample values for this property
        document_count: Number of documents using this property
        created_at: When schema was first created
        updated_at: When schema was last updated
    """

    vault_id: int
    property_key: str
    inferred_type: str = "string"
    sample_values: list[str] = field(default_factory=list)
    document_count: int = 0
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class VaultSchema:
    """Complete schema for a vault.

    Attributes:
        vault_id: Vault database ID
        properties: List of property schemas
        total_documents: Total documents in vault
        total_properties: Total property records
        built_at: When schema was built
    """

    vault_id: int
    properties: list[PropertySchema] = field(default_factory=list)
    total_documents: int = 0
    total_properties: int = 0
    built_at: datetime = field(default_factory=datetime.now)

    def get_property(self, key: str) -> PropertySchema | None:
        """Get schema for a specific property key.

        Args:
            key: Property key

        Returns:
            PropertySchema if found, None otherwise
        """
        for prop in self.properties:
            if prop.property_key == key:
                return prop
        return None

    def get_keys_by_type(self, value_type: str) -> list[str]:
        """Get property keys filtered by type.

        Args:
            value_type: Type to filter by

        Returns:
            List of property keys with that type
        """
        return [
            p.property_key
            for p in self.properties
            if p.inferred_type == value_type
        ]


class PropertySchemaBuilder:
    """Builder for automatic property schema inference.

    Analyzes document properties in a vault to determine:
    - Most common type for each property key
    - Sample values
    - Usage statistics

    Updates the property_schemas table with inferred schemas.

    Usage:
        builder = PropertySchemaBuilder(manager)

        # Build schema for a vault
        schema = await builder.build_schema(vault_id)

        # Infer type from values
        inferred = builder.infer_type(["active", "pending", "done"])
        # Returns "string"

        inferred = builder.infer_type([1, 2, 3])
        # Returns "number"
    """

    def __init__(self, manager: SQLiteManager) -> None:
        """Initialize schema builder.

        Args:
            manager: SQLiteManager instance
        """
        self._manager = manager

    async def build_schema(self, vault_id: int) -> VaultSchema:
        """Build complete schema for a vault.

        Analyzes all properties and updates property_schemas table.

        Args:
            vault_id: Vault database ID

        Returns:
            VaultSchema with all property schemas
        """
        schema = VaultSchema(vault_id=vault_id)

        # Get total documents and properties counts
        stats = await self._get_vault_stats(vault_id)
        schema.total_documents = stats["document_count"]
        schema.total_properties = stats["property_count"]

        # Get unique property keys with their type distributions
        key_stats = await self._get_key_statistics(vault_id)

        for key, stats in key_stats.items():
            prop_schema = PropertySchema(
                vault_id=vault_id,
                property_key=key,
                inferred_type=stats["inferred_type"],
                sample_values=stats["sample_values"],
                document_count=stats["document_count"],
            )
            schema.properties.append(prop_schema)

            # Update database
            await self._upsert_property_schema(prop_schema)

        schema.built_at = datetime.now()
        logger.info(
            f"Built schema for vault {vault_id}: "
            f"{len(schema.properties)} properties, "
            f"{schema.total_documents} documents"
        )

        return schema

    async def _get_vault_stats(self, vault_id: int) -> dict[str, int]:
        """Get vault statistics.

        Args:
            vault_id: Vault database ID

        Returns:
            Dict with document_count and property_count
        """
        row = await self._manager.fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM documents WHERE vault_id = ?) as document_count,
                (SELECT COUNT(*) FROM document_properties dp
                 JOIN documents d ON dp.document_id = d.id
                 WHERE d.vault_id = ?) as property_count
            """,
            (vault_id, vault_id),
        )

        if row is None:
            return {"document_count": 0, "property_count": 0}

        return {
            "document_count": row["document_count"],
            "property_count": row["property_count"],
        }

    async def _get_key_statistics(
        self,
        vault_id: int,
    ) -> dict[str, dict[str, Any]]:
        """Get statistics for all property keys.

        Args:
            vault_id: Vault database ID

        Returns:
            Dict mapping key to stats dict
        """
        # Get type distribution for each key
        rows = await self._manager.fetch_all(
            """
            SELECT
                dp.property_key,
                dp.value_type,
                COUNT(*) as type_count,
                COUNT(DISTINCT dp.document_id) as doc_count
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
            GROUP BY dp.property_key, dp.value_type
            ORDER BY dp.property_key, type_count DESC
            """,
            (vault_id,),
        )

        # Process into key statistics
        key_stats: dict[str, dict[str, Any]] = {}

        for row in rows:
            key = row["property_key"]
            if key not in key_stats:
                key_stats[key] = {
                    "types": Counter(),
                    "document_count": 0,
                }

            key_stats[key]["types"][row["value_type"]] = row["type_count"]
            # Take max doc count since same doc can have multiple types
            key_stats[key]["document_count"] = max(
                key_stats[key]["document_count"],
                row["doc_count"],
            )

        # Get sample values for each key
        for key in key_stats:
            samples = await self._get_sample_values(vault_id, key)
            key_stats[key]["sample_values"] = samples

            # Infer type from distribution
            type_counts = key_stats[key]["types"]
            key_stats[key]["inferred_type"] = self._infer_type_from_counts(
                type_counts
            )

        return key_stats

    async def _get_sample_values(
        self,
        vault_id: int,
        key: str,
        limit: int = 10,
    ) -> list[str]:
        """Get sample values for a property key.

        Args:
            vault_id: Vault database ID
            key: Property key
            limit: Maximum samples to return

        Returns:
            List of sample values
        """
        rows = await self._manager.fetch_all(
            """
            SELECT DISTINCT dp.property_value
            FROM document_properties dp
            JOIN documents d ON dp.document_id = d.id
            WHERE d.vault_id = ?
              AND dp.property_key = ?
              AND dp.property_value IS NOT NULL
            LIMIT ?
            """,
            (vault_id, key, limit),
        )
        return [row["property_value"] for row in rows]

    def _infer_type_from_counts(self, type_counts: Counter) -> str:
        """Infer property type from type distribution.

        Args:
            type_counts: Counter of value types

        Returns:
            Inferred type string
        """
        if not type_counts:
            return PropertyValueType.STRING.value

        # Get most common type
        most_common = type_counts.most_common(1)[0][0]
        return most_common

    async def _upsert_property_schema(
        self,
        schema: PropertySchema,
    ) -> int:
        """Insert or update property schema.

        Args:
            schema: PropertySchema to save

        Returns:
            Schema ID
        """
        sample_json = json.dumps(schema.sample_values, ensure_ascii=False)

        cursor = await self._manager.execute(
            """
            INSERT INTO property_schemas
                (vault_id, property_key, inferred_type, sample_values, document_count, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(vault_id, property_key) DO UPDATE SET
                inferred_type = excluded.inferred_type,
                sample_values = excluded.sample_values,
                document_count = excluded.document_count,
                updated_at = datetime('now')
            """,
            (
                schema.vault_id,
                schema.property_key,
                schema.inferred_type,
                sample_json,
                schema.document_count,
            ),
        )
        return cursor.lastrowid or 0

    async def get_schema(self, vault_id: int) -> VaultSchema | None:
        """Get existing schema from database.

        Args:
            vault_id: Vault database ID

        Returns:
            VaultSchema if exists, None otherwise
        """
        rows = await self._manager.fetch_all(
            """
            SELECT * FROM property_schemas
            WHERE vault_id = ?
            ORDER BY property_key
            """,
            (vault_id,),
        )

        if not rows:
            return None

        schema = VaultSchema(vault_id=vault_id)

        for row in rows:
            sample_values = []
            if row.get("sample_values"):
                try:
                    sample_values = json.loads(row["sample_values"])
                except json.JSONDecodeError:
                    pass

            prop_schema = PropertySchema(
                id=row["id"],
                vault_id=row["vault_id"],
                property_key=row["property_key"],
                inferred_type=row["inferred_type"],
                sample_values=sample_values,
                document_count=row.get("document_count", 0),
                created_at=_parse_datetime(row.get("created_at")),
                updated_at=_parse_datetime(row.get("updated_at")),
            )
            schema.properties.append(prop_schema)

        # Get total counts
        stats = await self._get_vault_stats(vault_id)
        schema.total_documents = stats["document_count"]
        schema.total_properties = stats["property_count"]

        return schema

    async def delete_schema(self, vault_id: int) -> int:
        """Delete all schema entries for a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            Number of deleted entries
        """
        cursor = await self._manager.execute(
            "DELETE FROM property_schemas WHERE vault_id = ?",
            (vault_id,),
        )
        return cursor.rowcount

    def infer_type(self, values: list[Any]) -> str:
        """Infer property type from a list of values.

        Analyzes values to determine the most appropriate type.

        Args:
            values: List of property values

        Returns:
            Inferred type string
        """
        if not values:
            return PropertyValueType.STRING.value

        type_counts: Counter[str] = Counter()

        for value in values:
            detected_type = self._detect_value_type(value)
            type_counts[detected_type] += 1

        # Return most common type
        most_common = type_counts.most_common(1)[0][0]
        return most_common

    def _detect_value_type(self, value: Any) -> str:
        """Detect type of a single value.

        Args:
            value: Value to analyze

        Returns:
            Type string
        """
        if value is None:
            return PropertyValueType.STRING.value

        if isinstance(value, bool):
            return PropertyValueType.BOOLEAN.value

        if isinstance(value, (int, float)):
            return PropertyValueType.NUMBER.value

        if isinstance(value, (datetime,)):
            return PropertyValueType.DATE.value

        if isinstance(value, str):
            # Check for link
            if "[[" in value and "]]" in value:
                return PropertyValueType.LINK.value

            # Check for date
            if self._looks_like_date(value):
                return PropertyValueType.DATE.value

            # Check for boolean strings
            if value.lower() in ("true", "false", "yes", "no"):
                return PropertyValueType.BOOLEAN.value

            # Check for number strings
            try:
                float(value)
                return PropertyValueType.NUMBER.value
            except ValueError:
                pass

        return PropertyValueType.STRING.value

    def _looks_like_date(self, value: str) -> bool:
        """Check if string looks like a date.

        Args:
            value: String to check

        Returns:
            True if looks like a date
        """
        value = value.strip()

        # Check YYYY-MM-DD pattern
        if len(value) >= 10:
            if value[4] in "-/" and value[7] in "-/":
                try:
                    year = int(value[0:4])
                    month = int(value[5:7])
                    day = int(value[8:10])
                    if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                        return True
                except ValueError:
                    pass

        return False

    async def get_property_keys(self, vault_id: int) -> list[str]:
        """Get all property keys for a vault.

        Args:
            vault_id: Vault database ID

        Returns:
            List of property keys
        """
        rows = await self._manager.fetch_all(
            """
            SELECT property_key FROM property_schemas
            WHERE vault_id = ?
            ORDER BY property_key
            """,
            (vault_id,),
        )
        return [row["property_key"] for row in rows]

    async def get_property_schema(
        self,
        vault_id: int,
        key: str,
    ) -> PropertySchema | None:
        """Get schema for a specific property.

        Args:
            vault_id: Vault database ID
            key: Property key

        Returns:
            PropertySchema if found
        """
        row = await self._manager.fetch_one(
            """
            SELECT * FROM property_schemas
            WHERE vault_id = ? AND property_key = ?
            """,
            (vault_id, key),
        )

        if row is None:
            return None

        sample_values = []
        if row.get("sample_values"):
            try:
                sample_values = json.loads(row["sample_values"])
            except json.JSONDecodeError:
                pass

        return PropertySchema(
            id=row["id"],
            vault_id=row["vault_id"],
            property_key=row["property_key"],
            inferred_type=row["inferred_type"],
            sample_values=sample_values,
            document_count=row.get("document_count", 0),
            created_at=_parse_datetime(row.get("created_at")),
            updated_at=_parse_datetime(row.get("updated_at")),
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
