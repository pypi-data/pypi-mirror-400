"""Embedding cache for SQLite storage.

This module provides caching of embeddings to avoid re-vectorization
during reindexing. Uses content hash + model name as cache key.
"""

import hashlib
import logging
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from obsidian_kb.storage.sqlite.manager import SQLiteManager

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cached embedding entry.

    Attributes:
        id: Database primary key
        content_hash: SHA256 hash of content
        model_name: Embedding model name
        embedding: Embedding vector as numpy array
        embedding_dim: Dimension of embedding vector
        created_at: When entry was created
        last_used_at: When entry was last accessed
        access_count: Number of times accessed
    """

    content_hash: str
    model_name: str
    embedding: np.ndarray
    embedding_dim: int
    created_at: datetime | None = None
    last_used_at: datetime | None = None
    access_count: int = 1
    id: int | None = None


@dataclass
class CacheStats:
    """Cache statistics.

    Attributes:
        total_entries: Total number of cached embeddings
        total_hits: Number of cache hits
        total_misses: Number of cache misses
        hit_rate: Cache hit rate (0.0 to 1.0)
        size_bytes: Approximate size of cache in bytes
        models: Dict of entries per model
    """

    total_entries: int
    total_hits: int
    total_misses: int
    hit_rate: float
    size_bytes: int
    models: dict[str, int]


class EmbeddingCache:
    """Hash-based embedding cache using SQLite.

    Caches embeddings with content_hash + model_name as key.
    Supports batch operations for efficiency.

    Usage:
        cache = EmbeddingCache(manager)

        # Single operations
        embedding = await cache.get(content_hash, "bge-m3")
        if embedding is None:
            embedding = await provider.embed(content)
            await cache.set(content_hash, "bge-m3", embedding)

        # Batch operations
        results = await cache.get_batch(hashes, "bge-m3")
        await cache.set_batch(items, "bge-m3")
    """

    def __init__(self, manager: SQLiteManager) -> None:
        """Initialize embedding cache.

        Args:
            manager: SQLiteManager instance
        """
        self._manager = manager
        self._hits = 0
        self._misses = 0

    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA256 hash of content.

        Args:
            content: Text content to hash

        Returns:
            Hex-encoded SHA256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _serialize_embedding(embedding: list[float] | np.ndarray) -> bytes:
        """Serialize embedding to bytes (float32 array).

        Args:
            embedding: Embedding vector

        Returns:
            Bytes representation
        """
        if isinstance(embedding, np.ndarray):
            arr = embedding.astype(np.float32)
        else:
            arr = np.array(embedding, dtype=np.float32)
        return arr.tobytes()

    @staticmethod
    def _deserialize_embedding(data: bytes, dim: int) -> np.ndarray:
        """Deserialize embedding from bytes.

        Args:
            data: Bytes data
            dim: Expected dimension

        Returns:
            Numpy array of float32
        """
        return np.frombuffer(data, dtype=np.float32).copy()

    # =========================================================================
    # Single operations
    # =========================================================================

    async def get(
        self,
        content_hash: str,
        model: str,
    ) -> np.ndarray | None:
        """Get embedding from cache.

        Args:
            content_hash: SHA256 hash of content
            model: Embedding model name

        Returns:
            Embedding vector as numpy array, or None if not cached
        """
        row = await self._manager.fetch_one(
            """
            SELECT id, embedding, embedding_dim
            FROM embedding_cache
            WHERE content_hash = ? AND model_name = ?
            """,
            (content_hash, model),
        )

        if row is None:
            self._misses += 1
            return None

        # Update access statistics
        await self._manager.execute(
            """
            UPDATE embedding_cache
            SET last_used_at = datetime('now'),
                access_count = access_count + 1
            WHERE id = ?
            """,
            (row["id"],),
        )

        self._hits += 1
        return self._deserialize_embedding(row["embedding"], row["embedding_dim"])

    async def set(
        self,
        content_hash: str,
        model: str,
        embedding: list[float] | np.ndarray,
    ) -> int:
        """Save embedding to cache.

        Args:
            content_hash: SHA256 hash of content
            model: Embedding model name
            embedding: Embedding vector

        Returns:
            ID of cached entry
        """
        if isinstance(embedding, np.ndarray):
            dim = embedding.shape[0]
        else:
            dim = len(embedding)

        blob = self._serialize_embedding(embedding)

        cursor = await self._manager.execute(
            """
            INSERT INTO embedding_cache (content_hash, model_name, embedding, embedding_dim)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(content_hash, model_name) DO UPDATE SET
                embedding = excluded.embedding,
                embedding_dim = excluded.embedding_dim,
                last_used_at = datetime('now'),
                access_count = access_count + 1
            """,
            (content_hash, model, blob, dim),
        )

        return cursor.lastrowid or 0

    async def delete(self, content_hash: str, model: str) -> bool:
        """Delete embedding from cache.

        Args:
            content_hash: SHA256 hash of content
            model: Embedding model name

        Returns:
            True if entry was deleted
        """
        cursor = await self._manager.execute(
            """
            DELETE FROM embedding_cache
            WHERE content_hash = ? AND model_name = ?
            """,
            (content_hash, model),
        )
        return cursor.rowcount > 0

    async def exists(self, content_hash: str, model: str) -> bool:
        """Check if embedding is cached.

        Args:
            content_hash: SHA256 hash of content
            model: Embedding model name

        Returns:
            True if cached
        """
        count = await self._manager.fetch_value(
            """
            SELECT COUNT(*) FROM embedding_cache
            WHERE content_hash = ? AND model_name = ?
            """,
            (content_hash, model),
        )
        return count > 0

    # =========================================================================
    # Batch operations
    # =========================================================================

    async def get_batch(
        self,
        content_hashes: list[str],
        model: str,
    ) -> dict[str, np.ndarray]:
        """Get multiple embeddings from cache.

        Args:
            content_hashes: List of SHA256 hashes
            model: Embedding model name

        Returns:
            Dict mapping hash to embedding (only includes cached entries)
        """
        if not content_hashes:
            return {}

        # Build query with placeholders
        placeholders = ",".join("?" * len(content_hashes))
        rows = await self._manager.fetch_all(
            f"""
            SELECT id, content_hash, embedding, embedding_dim
            FROM embedding_cache
            WHERE content_hash IN ({placeholders}) AND model_name = ?
            """,
            (*content_hashes, model),
        )

        if not rows:
            self._misses += len(content_hashes)
            return {}

        result: dict[str, np.ndarray] = {}
        ids_to_update: list[int] = []

        for row in rows:
            result[row["content_hash"]] = self._deserialize_embedding(
                row["embedding"], row["embedding_dim"]
            )
            ids_to_update.append(row["id"])

        # Update access statistics for all found entries
        if ids_to_update:
            id_placeholders = ",".join("?" * len(ids_to_update))
            await self._manager.execute(
                f"""
                UPDATE embedding_cache
                SET last_used_at = datetime('now'),
                    access_count = access_count + 1
                WHERE id IN ({id_placeholders})
                """,
                tuple(ids_to_update),
            )

        self._hits += len(result)
        self._misses += len(content_hashes) - len(result)

        return result

    async def set_batch(
        self,
        items: list[tuple[str, list[float] | np.ndarray]],
        model: str,
    ) -> int:
        """Save multiple embeddings to cache.

        Args:
            items: List of (content_hash, embedding) tuples
            model: Embedding model name

        Returns:
            Number of entries saved
        """
        if not items:
            return 0

        # Prepare batch insert
        rows = []
        for content_hash, embedding in items:
            if isinstance(embedding, np.ndarray):
                dim = embedding.shape[0]
            else:
                dim = len(embedding)
            blob = self._serialize_embedding(embedding)
            rows.append((content_hash, model, blob, dim))

        # Use executemany with ON CONFLICT
        cursor = await self._manager.execute_many(
            """
            INSERT INTO embedding_cache (content_hash, model_name, embedding, embedding_dim)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(content_hash, model_name) DO UPDATE SET
                embedding = excluded.embedding,
                embedding_dim = excluded.embedding_dim,
                last_used_at = datetime('now'),
                access_count = access_count + 1
            """,
            rows,
        )

        return cursor.rowcount

    # =========================================================================
    # Statistics and maintenance
    # =========================================================================

    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats with cache information
        """
        # Get total entries
        total_entries = await self._manager.fetch_value(
            "SELECT COUNT(*) FROM embedding_cache"
        ) or 0

        # Get entries per model
        model_rows = await self._manager.fetch_all(
            """
            SELECT model_name, COUNT(*) as count
            FROM embedding_cache
            GROUP BY model_name
            """
        )
        models = {row["model_name"]: row["count"] for row in model_rows}

        # Estimate size (approximation based on average embedding size)
        size_row = await self._manager.fetch_one(
            """
            SELECT SUM(LENGTH(embedding)) as total_size
            FROM embedding_cache
            """
        )
        size_bytes = size_row["total_size"] if size_row and size_row["total_size"] else 0

        # Calculate hit rate
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return CacheStats(
            total_entries=total_entries,
            total_hits=self._hits,
            total_misses=self._misses,
            hit_rate=hit_rate,
            size_bytes=size_bytes,
            models=models,
        )

    def reset_stats(self) -> None:
        """Reset hit/miss counters."""
        self._hits = 0
        self._misses = 0

    async def cleanup(self, max_age_days: int = 30) -> int:
        """Remove old cache entries.

        Args:
            max_age_days: Maximum age in days for entries to keep

        Returns:
            Number of entries deleted
        """
        cursor = await self._manager.execute(
            """
            DELETE FROM embedding_cache
            WHERE last_used_at < datetime('now', ?)
            """,
            (f"-{max_age_days} days",),
        )
        deleted = cursor.rowcount
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old cache entries")
        return deleted

    async def cleanup_by_access_count(self, min_access_count: int = 1) -> int:
        """Remove rarely accessed entries.

        Args:
            min_access_count: Minimum access count to keep

        Returns:
            Number of entries deleted
        """
        cursor = await self._manager.execute(
            """
            DELETE FROM embedding_cache
            WHERE access_count < ?
            """,
            (min_access_count,),
        )
        return cursor.rowcount

    async def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries deleted
        """
        cursor = await self._manager.execute("DELETE FROM embedding_cache")
        deleted = cursor.rowcount
        self.reset_stats()
        logger.info(f"Cleared {deleted} cache entries")
        return deleted

    async def clear_model(self, model: str) -> int:
        """Clear cache entries for specific model.

        Args:
            model: Model name to clear

        Returns:
            Number of entries deleted
        """
        cursor = await self._manager.execute(
            "DELETE FROM embedding_cache WHERE model_name = ?",
            (model,),
        )
        return cursor.rowcount

    async def get_entry(
        self,
        content_hash: str,
        model: str,
    ) -> CacheEntry | None:
        """Get full cache entry with metadata.

        Args:
            content_hash: SHA256 hash of content
            model: Embedding model name

        Returns:
            CacheEntry with full metadata, or None if not cached
        """
        row = await self._manager.fetch_one(
            """
            SELECT id, content_hash, model_name, embedding, embedding_dim,
                   created_at, last_used_at, access_count
            FROM embedding_cache
            WHERE content_hash = ? AND model_name = ?
            """,
            (content_hash, model),
        )

        if row is None:
            return None

        # Parse datetime strings
        created_at = None
        last_used_at = None
        if row["created_at"]:
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except ValueError:
                pass
        if row["last_used_at"]:
            try:
                last_used_at = datetime.fromisoformat(row["last_used_at"])
            except ValueError:
                pass

        return CacheEntry(
            id=row["id"],
            content_hash=row["content_hash"],
            model_name=row["model_name"],
            embedding=self._deserialize_embedding(row["embedding"], row["embedding_dim"]),
            embedding_dim=row["embedding_dim"],
            created_at=created_at,
            last_used_at=last_used_at,
            access_count=row["access_count"],
        )

    async def count(self, model: str | None = None) -> int:
        """Count cache entries.

        Args:
            model: Optional model name to filter by

        Returns:
            Number of entries
        """
        if model is None:
            result = await self._manager.fetch_value(
                "SELECT COUNT(*) FROM embedding_cache"
            )
        else:
            result = await self._manager.fetch_value(
                "SELECT COUNT(*) FROM embedding_cache WHERE model_name = ?",
                (model,),
            )
        return result or 0
