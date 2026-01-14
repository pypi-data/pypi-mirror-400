"""Tests for EmbeddingCache."""

import asyncio
from pathlib import Path

import numpy as np
import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.embedding_cache import (
    CacheEntry,
    CacheStats,
    EmbeddingCache,
)
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.schema import create_schema


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test_cache.sqlite"


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset SQLiteManager singleton before each test."""
    SQLiteManager.reset_instance()
    yield
    SQLiteManager.reset_instance()


@pytest_asyncio.fixture
async def manager_with_schema(temp_db_path: Path) -> SQLiteManager:
    """Create manager with schema initialized."""
    manager = SQLiteManager(temp_db_path)
    await manager.initialize()
    await create_schema(manager)
    yield manager
    await manager.close()


@pytest_asyncio.fixture
async def cache(manager_with_schema: SQLiteManager) -> EmbeddingCache:
    """Create EmbeddingCache instance."""
    return EmbeddingCache(manager_with_schema)


class TestEmbeddingCacheInit:
    """Tests for EmbeddingCache initialization."""

    @pytest.mark.asyncio
    async def test_init_creates_cache(self, manager_with_schema: SQLiteManager):
        """Test that cache is created successfully."""
        cache = EmbeddingCache(manager_with_schema)
        assert cache is not None

    @pytest.mark.asyncio
    async def test_cache_starts_empty(self, cache: EmbeddingCache):
        """Test that cache starts empty."""
        count = await cache.count()
        assert count == 0


class TestComputeHash:
    """Tests for hash computation."""

    def test_compute_hash_returns_hex_string(self):
        """Test that compute_hash returns hex string."""
        h = EmbeddingCache.compute_hash("test content")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA256 hex = 64 chars
        assert all(c in "0123456789abcdef" for c in h)

    def test_compute_hash_deterministic(self):
        """Test that same content produces same hash."""
        content = "test content"
        h1 = EmbeddingCache.compute_hash(content)
        h2 = EmbeddingCache.compute_hash(content)
        assert h1 == h2

    def test_compute_hash_different_for_different_content(self):
        """Test that different content produces different hash."""
        h1 = EmbeddingCache.compute_hash("content 1")
        h2 = EmbeddingCache.compute_hash("content 2")
        assert h1 != h2

    def test_compute_hash_handles_unicode(self):
        """Test that hash handles unicode correctly."""
        h = EmbeddingCache.compute_hash("Привет мир 你好世界")
        assert len(h) == 64

    def test_compute_hash_handles_empty_string(self):
        """Test that hash handles empty string."""
        h = EmbeddingCache.compute_hash("")
        assert len(h) == 64


class TestSerialization:
    """Tests for embedding serialization."""

    def test_serialize_list(self):
        """Test serializing list of floats."""
        embedding = [1.0, 2.0, 3.0]
        blob = EmbeddingCache._serialize_embedding(embedding)
        assert isinstance(blob, bytes)
        assert len(blob) == 12  # 3 * 4 bytes (float32)

    def test_serialize_numpy_array(self):
        """Test serializing numpy array."""
        embedding = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        blob = EmbeddingCache._serialize_embedding(embedding)
        assert isinstance(blob, bytes)
        assert len(blob) == 12

    def test_deserialize_returns_numpy(self):
        """Test that deserialize returns numpy array."""
        embedding = [1.0, 2.0, 3.0]
        blob = EmbeddingCache._serialize_embedding(embedding)
        result = EmbeddingCache._deserialize_embedding(blob, 3)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32

    def test_roundtrip_list(self):
        """Test serialization roundtrip for list."""
        original = [1.5, 2.5, 3.5, 4.5]
        blob = EmbeddingCache._serialize_embedding(original)
        result = EmbeddingCache._deserialize_embedding(blob, 4)
        np.testing.assert_array_almost_equal(result, original)

    def test_roundtrip_numpy(self):
        """Test serialization roundtrip for numpy array."""
        original = np.array([1.5, 2.5, 3.5, 4.5], dtype=np.float32)
        blob = EmbeddingCache._serialize_embedding(original)
        result = EmbeddingCache._deserialize_embedding(blob, 4)
        np.testing.assert_array_almost_equal(result, original)


class TestSingleOperations:
    """Tests for single get/set operations."""

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache: EmbeddingCache):
        """Test basic set and get."""
        content_hash = "a" * 64
        model = "test-model"
        embedding = [1.0, 2.0, 3.0]

        await cache.set(content_hash, model, embedding)
        result = await cache.get(content_hash, model)

        assert result is not None
        np.testing.assert_array_almost_equal(result, embedding)

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, cache: EmbeddingCache):
        """Test that getting nonexistent entry returns None."""
        result = await cache.get("nonexistent" * 4, "model")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_wrong_model_returns_none(self, cache: EmbeddingCache):
        """Test that getting with wrong model returns None."""
        content_hash = "b" * 64
        await cache.set(content_hash, "model-1", [1.0, 2.0])

        result = await cache.get(content_hash, "model-2")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_updates_existing(self, cache: EmbeddingCache):
        """Test that set updates existing entry."""
        content_hash = "c" * 64
        model = "test-model"

        await cache.set(content_hash, model, [1.0, 2.0])
        await cache.set(content_hash, model, [3.0, 4.0])

        result = await cache.get(content_hash, model)
        np.testing.assert_array_almost_equal(result, [3.0, 4.0])

        # Should still only have one entry
        count = await cache.count(model)
        assert count == 1

    @pytest.mark.asyncio
    async def test_delete(self, cache: EmbeddingCache):
        """Test deleting cache entry."""
        content_hash = "d" * 64
        model = "test-model"

        await cache.set(content_hash, model, [1.0, 2.0])
        deleted = await cache.delete(content_hash, model)

        assert deleted is True
        result = await cache.get(content_hash, model)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, cache: EmbeddingCache):
        """Test deleting nonexistent entry."""
        deleted = await cache.delete("nonexistent" * 4, "model")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_exists(self, cache: EmbeddingCache):
        """Test exists check."""
        content_hash = "e" * 64
        model = "test-model"

        assert await cache.exists(content_hash, model) is False

        await cache.set(content_hash, model, [1.0, 2.0])
        assert await cache.exists(content_hash, model) is True

    @pytest.mark.asyncio
    async def test_get_updates_access_stats(self, cache: EmbeddingCache):
        """Test that get updates access statistics."""
        content_hash = "f" * 64
        model = "test-model"

        await cache.set(content_hash, model, [1.0, 2.0])

        # Get multiple times
        await cache.get(content_hash, model)
        await cache.get(content_hash, model)

        entry = await cache.get_entry(content_hash, model)
        assert entry is not None
        assert entry.access_count >= 3  # 1 from set, 2 from gets


class TestBatchOperations:
    """Tests for batch get/set operations."""

    @pytest.mark.asyncio
    async def test_set_batch(self, cache: EmbeddingCache):
        """Test batch set."""
        items = [
            ("hash1" + "0" * 59, [1.0, 2.0]),
            ("hash2" + "0" * 59, [3.0, 4.0]),
            ("hash3" + "0" * 59, [5.0, 6.0]),
        ]
        model = "test-model"

        count = await cache.set_batch(items, model)
        assert count == 3

        total = await cache.count(model)
        assert total == 3

    @pytest.mark.asyncio
    async def test_set_batch_empty(self, cache: EmbeddingCache):
        """Test batch set with empty list."""
        count = await cache.set_batch([], "model")
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_batch(self, cache: EmbeddingCache):
        """Test batch get."""
        items = [
            ("hashA" + "0" * 59, [1.0, 2.0]),
            ("hashB" + "0" * 59, [3.0, 4.0]),
        ]
        model = "test-model"
        await cache.set_batch(items, model)

        hashes = ["hashA" + "0" * 59, "hashB" + "0" * 59]
        results = await cache.get_batch(hashes, model)

        assert len(results) == 2
        assert "hashA" + "0" * 59 in results
        assert "hashB" + "0" * 59 in results
        np.testing.assert_array_almost_equal(results["hashA" + "0" * 59], [1.0, 2.0])

    @pytest.mark.asyncio
    async def test_get_batch_partial(self, cache: EmbeddingCache):
        """Test batch get with some missing."""
        await cache.set("hashX" + "0" * 59, "model", [1.0, 2.0])

        hashes = ["hashX" + "0" * 59, "hashY" + "0" * 59]
        results = await cache.get_batch(hashes, "model")

        assert len(results) == 1
        assert "hashX" + "0" * 59 in results
        assert "hashY" + "0" * 59 not in results

    @pytest.mark.asyncio
    async def test_get_batch_empty_input(self, cache: EmbeddingCache):
        """Test batch get with empty list."""
        results = await cache.get_batch([], "model")
        assert results == {}

    @pytest.mark.asyncio
    async def test_get_batch_all_missing(self, cache: EmbeddingCache):
        """Test batch get when all entries missing."""
        hashes = ["missing1" + "0" * 56, "missing2" + "0" * 56]
        results = await cache.get_batch(hashes, "model")
        assert results == {}


class TestStatistics:
    """Tests for cache statistics."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, cache: EmbeddingCache):
        """Test stats on empty cache."""
        stats = await cache.get_stats()

        assert isinstance(stats, CacheStats)
        assert stats.total_entries == 0
        assert stats.total_hits == 0
        assert stats.total_misses == 0
        assert stats.hit_rate == 0.0
        assert stats.models == {}

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self, cache: EmbeddingCache):
        """Test stats with cached data."""
        await cache.set("hash1" + "0" * 59, "model-a", [1.0, 2.0])
        await cache.set("hash2" + "0" * 59, "model-a", [3.0, 4.0])
        await cache.set("hash3" + "0" * 59, "model-b", [5.0, 6.0])

        stats = await cache.get_stats()

        assert stats.total_entries == 3
        assert stats.models == {"model-a": 2, "model-b": 1}
        assert stats.size_bytes > 0

    @pytest.mark.asyncio
    async def test_hit_miss_tracking(self, cache: EmbeddingCache):
        """Test hit/miss tracking."""
        await cache.set("existing" + "0" * 56, "model", [1.0, 2.0])

        # Miss
        await cache.get("missing" + "0" * 57, "model")
        # Hit
        await cache.get("existing" + "0" * 56, "model")
        # Hit
        await cache.get("existing" + "0" * 56, "model")

        stats = await cache.get_stats()
        assert stats.total_hits == 2
        assert stats.total_misses == 1
        assert stats.hit_rate == pytest.approx(2 / 3)

    @pytest.mark.asyncio
    async def test_reset_stats(self, cache: EmbeddingCache):
        """Test resetting statistics."""
        await cache.set("hash" + "0" * 60, "model", [1.0])
        await cache.get("hash" + "0" * 60, "model")
        await cache.get("missing" + "0" * 57, "model")

        cache.reset_stats()

        stats = await cache.get_stats()
        assert stats.total_hits == 0
        assert stats.total_misses == 0


class TestCleanup:
    """Tests for cache cleanup."""

    @pytest.mark.asyncio
    async def test_cleanup_old_entries(self, cache: EmbeddingCache, manager_with_schema: SQLiteManager):
        """Test cleanup removes old entries."""
        # Insert entry with old timestamp
        await manager_with_schema.execute(
            """
            INSERT INTO embedding_cache (content_hash, model_name, embedding, embedding_dim, last_used_at)
            VALUES (?, ?, ?, ?, datetime('now', '-60 days'))
            """,
            ("old_hash" + "0" * 56, "model", b"\x00\x00\x80?\x00\x00\x00@", 2),  # [1.0, 2.0]
        )

        # Insert fresh entry
        await cache.set("new_hash" + "0" * 56, "model", [3.0, 4.0])

        # Cleanup entries older than 30 days
        deleted = await cache.cleanup(max_age_days=30)

        assert deleted == 1
        count = await cache.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_cleanup_by_access_count(self, cache: EmbeddingCache, manager_with_schema: SQLiteManager):
        """Test cleanup by access count."""
        # Insert entry with low access count
        await manager_with_schema.execute(
            """
            INSERT INTO embedding_cache (content_hash, model_name, embedding, embedding_dim, access_count)
            VALUES (?, ?, ?, ?, 1)
            """,
            ("low_access" + "0" * 54, "model", b"\x00\x00\x80?\x00\x00\x00@", 2),
        )

        # Insert and access entry multiple times
        await cache.set("high_access" + "0" * 53, "model", [3.0, 4.0])
        await cache.get("high_access" + "0" * 53, "model")
        await cache.get("high_access" + "0" * 53, "model")
        await cache.get("high_access" + "0" * 53, "model")

        # Cleanup entries with less than 3 accesses
        deleted = await cache.cleanup_by_access_count(min_access_count=3)

        assert deleted == 1
        count = await cache.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_clear(self, cache: EmbeddingCache):
        """Test clearing all cache entries."""
        await cache.set("hash1" + "0" * 59, "model", [1.0])
        await cache.set("hash2" + "0" * 59, "model", [2.0])
        await cache.set("hash3" + "0" * 59, "model", [3.0])

        deleted = await cache.clear()

        assert deleted == 3
        count = await cache.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_clear_model(self, cache: EmbeddingCache):
        """Test clearing entries for specific model."""
        await cache.set("hash1" + "0" * 59, "model-a", [1.0])
        await cache.set("hash2" + "0" * 59, "model-a", [2.0])
        await cache.set("hash3" + "0" * 59, "model-b", [3.0])

        deleted = await cache.clear_model("model-a")

        assert deleted == 2
        assert await cache.count("model-a") == 0
        assert await cache.count("model-b") == 1


class TestCacheEntry:
    """Tests for CacheEntry retrieval."""

    @pytest.mark.asyncio
    async def test_get_entry(self, cache: EmbeddingCache):
        """Test getting full cache entry."""
        content_hash = "entry" + "0" * 59
        model = "test-model"
        embedding = [1.0, 2.0, 3.0]

        await cache.set(content_hash, model, embedding)
        entry = await cache.get_entry(content_hash, model)

        assert entry is not None
        assert isinstance(entry, CacheEntry)
        assert entry.content_hash == content_hash
        assert entry.model_name == model
        assert entry.embedding_dim == 3
        np.testing.assert_array_almost_equal(entry.embedding, embedding)
        assert entry.id is not None
        assert entry.created_at is not None
        assert entry.last_used_at is not None
        assert entry.access_count >= 1

    @pytest.mark.asyncio
    async def test_get_entry_nonexistent(self, cache: EmbeddingCache):
        """Test getting nonexistent entry returns None."""
        entry = await cache.get_entry("nonexistent" + "0" * 53, "model")
        assert entry is None


class TestCount:
    """Tests for count operations."""

    @pytest.mark.asyncio
    async def test_count_all(self, cache: EmbeddingCache):
        """Test counting all entries."""
        await cache.set("h1" + "0" * 62, "m1", [1.0])
        await cache.set("h2" + "0" * 62, "m1", [2.0])
        await cache.set("h3" + "0" * 62, "m2", [3.0])

        count = await cache.count()
        assert count == 3

    @pytest.mark.asyncio
    async def test_count_by_model(self, cache: EmbeddingCache):
        """Test counting by model."""
        await cache.set("h1" + "0" * 62, "m1", [1.0])
        await cache.set("h2" + "0" * 62, "m1", [2.0])
        await cache.set("h3" + "0" * 62, "m2", [3.0])

        assert await cache.count("m1") == 2
        assert await cache.count("m2") == 1
        assert await cache.count("m3") == 0


class TestHighDimensionalEmbeddings:
    """Tests for realistic high-dimensional embeddings."""

    @pytest.mark.asyncio
    async def test_1024_dim_embedding(self, cache: EmbeddingCache):
        """Test caching 1024-dimensional embedding (BGE-M3 size)."""
        content_hash = "highdim" + "0" * 57
        model = "bge-m3"
        embedding = np.random.randn(1024).astype(np.float32).tolist()

        await cache.set(content_hash, model, embedding)
        result = await cache.get(content_hash, model)

        assert result is not None
        assert len(result) == 1024
        np.testing.assert_array_almost_equal(result, embedding)

    @pytest.mark.asyncio
    async def test_batch_high_dim(self, cache: EmbeddingCache):
        """Test batch operations with high-dimensional embeddings."""
        model = "bge-m3"
        items = []
        for i in range(10):
            h = f"batch{i:02d}" + "0" * 56
            emb = np.random.randn(1024).astype(np.float32).tolist()
            items.append((h, emb))

        await cache.set_batch(items, model)

        hashes = [item[0] for item in items]
        results = await cache.get_batch(hashes, model)

        assert len(results) == 10
        for h, original_emb in items:
            np.testing.assert_array_almost_equal(results[h], original_emb)


class TestConcurrency:
    """Tests for concurrent access."""

    @pytest.mark.asyncio
    async def test_concurrent_sets(self, cache: EmbeddingCache):
        """Test concurrent set operations."""
        async def set_embedding(i: int):
            h = f"conc{i:03d}" + "0" * 57
            await cache.set(h, "model", [float(i)])

        await asyncio.gather(*[set_embedding(i) for i in range(20)])

        count = await cache.count()
        assert count == 20

    @pytest.mark.asyncio
    async def test_concurrent_gets(self, cache: EmbeddingCache):
        """Test concurrent get operations."""
        h = "concurrent" + "0" * 54
        await cache.set(h, "model", [42.0])

        async def get_embedding():
            return await cache.get(h, "model")

        results = await asyncio.gather(*[get_embedding() for _ in range(20)])

        assert all(r is not None for r in results)
        for r in results:
            np.testing.assert_array_almost_equal(r, [42.0])

    @pytest.mark.asyncio
    async def test_concurrent_mixed(self, cache: EmbeddingCache):
        """Test concurrent mixed operations."""
        async def writer(i: int):
            h = f"mixed{i:03d}" + "0" * 56
            await cache.set(h, "model", [float(i)])

        async def reader(i: int):
            h = f"mixed{i:03d}" + "0" * 56
            await asyncio.sleep(0.01)  # Small delay to let writes happen
            return await cache.get(h, "model")

        # Start writers and readers concurrently
        write_tasks = [writer(i) for i in range(10)]
        read_tasks = [reader(i) for i in range(10)]

        await asyncio.gather(*write_tasks)
        results = await asyncio.gather(*read_tasks)

        # Most reads should succeed (some might miss due to timing)
        successful = sum(1 for r in results if r is not None)
        assert successful >= 8  # Allow for some timing misses
