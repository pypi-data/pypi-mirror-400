"""Tests for CachedEmbeddingProvider."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio

from obsidian_kb.providers.cached_provider import (
    CachedEmbeddingProvider,
    CacheMetrics,
    wrap_with_cache,
)
from obsidian_kb.providers.interfaces import IEmbeddingProvider, ProviderHealth
from obsidian_kb.storage.sqlite.embedding_cache import EmbeddingCache
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.schema import create_schema


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test_cached_provider.sqlite"


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


class MockEmbeddingProvider:
    """Mock embedding provider for testing."""

    def __init__(
        self,
        name: str = "mock",
        model: str = "mock-model",
        dimensions: int = 128,
    ):
        self._name = name
        self._model = model
        self._dimensions = dimensions
        self.embed_calls: list[str] = []
        self.batch_embed_calls: list[list[str]] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def get_embedding(
        self,
        text: str,
        embedding_type: str = "doc",
    ) -> list[float]:
        """Generate mock embedding."""
        self.embed_calls.append(text)
        # Generate deterministic embedding based on text
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(self._dimensions).tolist()

    async def get_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        embedding_type: str = "doc",
    ) -> list[list[float]]:
        """Generate mock batch embeddings."""
        self.batch_embed_calls.append(texts)
        return [await self.get_embedding(t, embedding_type) for t in texts]

    async def health_check(self) -> ProviderHealth:
        """Return healthy status."""
        return ProviderHealth(
            available=True,
            latency_ms=10.0,
            model=self._model,
            dimensions=self._dimensions,
        )

    async def close(self) -> None:
        """Mock close."""
        pass


@pytest.fixture
def mock_provider() -> MockEmbeddingProvider:
    """Create mock provider."""
    return MockEmbeddingProvider()


@pytest_asyncio.fixture
async def cached_provider(
    mock_provider: MockEmbeddingProvider,
    cache: EmbeddingCache,
) -> CachedEmbeddingProvider:
    """Create cached provider instance."""
    return CachedEmbeddingProvider(mock_provider, cache)


# ============================================================================
# Tests
# ============================================================================


class TestCacheMetrics:
    """Tests for CacheMetrics dataclass."""

    def test_initial_values(self):
        """Test initial metric values."""
        metrics = CacheMetrics()
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.embeddings_generated == 0
        assert metrics.total_requests == 0
        assert metrics.hit_rate == 0.0

    def test_total_requests(self):
        """Test total_requests calculation."""
        metrics = CacheMetrics(cache_hits=5, cache_misses=3)
        assert metrics.total_requests == 8

    def test_hit_rate(self):
        """Test hit_rate calculation."""
        metrics = CacheMetrics(cache_hits=3, cache_misses=1)
        assert metrics.hit_rate == 0.75

    def test_hit_rate_zero_requests(self):
        """Test hit_rate with zero requests."""
        metrics = CacheMetrics()
        assert metrics.hit_rate == 0.0

    def test_reset(self):
        """Test reset method."""
        metrics = CacheMetrics(cache_hits=10, cache_misses=5, embeddings_generated=15)
        metrics.reset()
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.embeddings_generated == 0


class TestCachedEmbeddingProviderInit:
    """Tests for CachedEmbeddingProvider initialization."""

    @pytest.mark.asyncio
    async def test_init(self, mock_provider: MockEmbeddingProvider, cache: EmbeddingCache):
        """Test initialization."""
        provider = CachedEmbeddingProvider(mock_provider, cache)
        assert provider.provider is mock_provider
        assert provider.cache is cache
        assert provider.cache_enabled is True

    @pytest.mark.asyncio
    async def test_init_disabled_cache(
        self, mock_provider: MockEmbeddingProvider, cache: EmbeddingCache
    ):
        """Test initialization with disabled cache."""
        provider = CachedEmbeddingProvider(mock_provider, cache, cache_enabled=False)
        assert provider.cache_enabled is False


class TestCachedEmbeddingProviderProperties:
    """Tests for CachedEmbeddingProvider properties."""

    @pytest.mark.asyncio
    async def test_name(self, cached_provider: CachedEmbeddingProvider):
        """Test name property."""
        assert cached_provider.name == "cached_mock"

    @pytest.mark.asyncio
    async def test_model(self, cached_provider: CachedEmbeddingProvider):
        """Test model property."""
        assert cached_provider.model == "mock-model"

    @pytest.mark.asyncio
    async def test_dimensions(self, cached_provider: CachedEmbeddingProvider):
        """Test dimensions property."""
        assert cached_provider.dimensions == 128

    @pytest.mark.asyncio
    async def test_cache_enabled_toggle(self, cached_provider: CachedEmbeddingProvider):
        """Test toggling cache_enabled."""
        assert cached_provider.cache_enabled is True
        cached_provider.cache_enabled = False
        assert cached_provider.cache_enabled is False
        cached_provider.cache_enabled = True
        assert cached_provider.cache_enabled is True


class TestSingleEmbedding:
    """Tests for single embedding operations."""

    @pytest.mark.asyncio
    async def test_get_embedding_cache_miss(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test embedding generation on cache miss."""
        text = "Hello world"
        embedding = await cached_provider.get_embedding(text)

        assert len(embedding) == 128
        assert len(mock_provider.embed_calls) == 1
        assert mock_provider.embed_calls[0] == text
        assert cached_provider.metrics.cache_misses == 1
        assert cached_provider.metrics.cache_hits == 0

    @pytest.mark.asyncio
    async def test_get_embedding_cache_hit(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test embedding retrieval on cache hit."""
        text = "Hello world"

        # First call - cache miss
        emb1 = await cached_provider.get_embedding(text)

        # Second call - should be cache hit
        emb2 = await cached_provider.get_embedding(text)

        # Same embedding returned
        np.testing.assert_array_almost_equal(emb1, emb2)

        # Provider only called once
        assert len(mock_provider.embed_calls) == 1
        assert cached_provider.metrics.cache_hits == 1
        assert cached_provider.metrics.cache_misses == 1

    @pytest.mark.asyncio
    async def test_get_embedding_different_texts(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test that different texts get different embeddings."""
        emb1 = await cached_provider.get_embedding("Text one")
        emb2 = await cached_provider.get_embedding("Text two")

        # Different embeddings
        assert not np.allclose(emb1, emb2)

        # Both calls to provider
        assert len(mock_provider.embed_calls) == 2
        assert cached_provider.metrics.cache_misses == 2

    @pytest.mark.asyncio
    async def test_get_embedding_cache_disabled(
        self,
        mock_provider: MockEmbeddingProvider,
        cache: EmbeddingCache,
    ):
        """Test embedding generation with cache disabled."""
        provider = CachedEmbeddingProvider(mock_provider, cache, cache_enabled=False)
        text = "Hello world"

        await provider.get_embedding(text)
        await provider.get_embedding(text)

        # Provider called twice (no caching)
        assert len(mock_provider.embed_calls) == 2
        assert provider.metrics.cache_hits == 0
        assert provider.metrics.cache_misses == 0
        assert provider.metrics.embeddings_generated == 2


class TestBatchEmbeddings:
    """Tests for batch embedding operations."""

    @pytest.mark.asyncio
    async def test_batch_embeddings_all_miss(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test batch embeddings with all cache misses."""
        texts = ["Text A", "Text B", "Text C"]
        embeddings = await cached_provider.get_embeddings_batch(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 128 for e in embeddings)
        assert len(mock_provider.batch_embed_calls) == 1
        assert mock_provider.batch_embed_calls[0] == texts
        assert cached_provider.metrics.cache_misses == 3
        assert cached_provider.metrics.cache_hits == 0

    @pytest.mark.asyncio
    async def test_batch_embeddings_all_hit(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test batch embeddings with all cache hits."""
        texts = ["Text A", "Text B", "Text C"]

        # First call - cache misses
        emb1 = await cached_provider.get_embeddings_batch(texts)

        # Reset call tracking
        mock_provider.batch_embed_calls.clear()

        # Second call - cache hits
        emb2 = await cached_provider.get_embeddings_batch(texts)

        # Same embeddings returned
        for e1, e2 in zip(emb1, emb2):
            np.testing.assert_array_almost_equal(e1, e2)

        # No new provider calls
        assert len(mock_provider.batch_embed_calls) == 0
        assert cached_provider.metrics.cache_hits == 3  # 3 hits on second batch call
        assert cached_provider.metrics.cache_misses == 3  # 3 misses on first batch call

    @pytest.mark.asyncio
    async def test_batch_embeddings_partial_hit(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test batch embeddings with partial cache hits."""
        # First, cache some texts
        await cached_provider.get_embedding("Cached A")
        await cached_provider.get_embedding("Cached B")
        mock_provider.embed_calls.clear()

        # Request batch with mix of cached and uncached
        texts = ["Cached A", "New X", "Cached B", "New Y"]
        embeddings = await cached_provider.get_embeddings_batch(texts)

        assert len(embeddings) == 4
        # Only new texts should be requested from provider
        assert len(mock_provider.batch_embed_calls) == 1
        assert set(mock_provider.batch_embed_calls[0]) == {"New X", "New Y"}

    @pytest.mark.asyncio
    async def test_batch_embeddings_empty(self, cached_provider: CachedEmbeddingProvider):
        """Test batch embeddings with empty input."""
        embeddings = await cached_provider.get_embeddings_batch([])
        assert embeddings == []

    @pytest.mark.asyncio
    async def test_batch_embeddings_cache_disabled(
        self,
        mock_provider: MockEmbeddingProvider,
        cache: EmbeddingCache,
    ):
        """Test batch embeddings with cache disabled."""
        provider = CachedEmbeddingProvider(mock_provider, cache, cache_enabled=False)
        texts = ["A", "B", "C"]

        await provider.get_embeddings_batch(texts)
        await provider.get_embeddings_batch(texts)

        # Provider called twice
        assert len(mock_provider.batch_embed_calls) == 2


class TestHealthCheck:
    """Tests for health check."""

    @pytest.mark.asyncio
    async def test_health_check(self, cached_provider: CachedEmbeddingProvider):
        """Test health check delegates to underlying provider."""
        health = await cached_provider.health_check()

        assert health.available is True
        assert health.model == "mock-model"
        assert health.dimensions == 128


class TestMetrics:
    """Tests for metrics tracking."""

    @pytest.mark.asyncio
    async def test_get_metrics(self, cached_provider: CachedEmbeddingProvider):
        """Test get_metrics returns correct data."""
        await cached_provider.get_embedding("text1")
        await cached_provider.get_embedding("text1")  # hit
        await cached_provider.get_embedding("text2")  # miss

        metrics = cached_provider.get_metrics()

        assert metrics["cache_hits"] == 1
        assert metrics["cache_misses"] == 2
        assert metrics["total_requests"] == 3
        assert metrics["hit_rate"] == pytest.approx(1 / 3)
        assert metrics["embeddings_generated"] == 2
        assert metrics["cache_enabled"] is True
        assert metrics["provider_name"] == "mock"
        assert metrics["model"] == "mock-model"

    @pytest.mark.asyncio
    async def test_reset_metrics(self, cached_provider: CachedEmbeddingProvider):
        """Test reset_metrics clears counters."""
        await cached_provider.get_embedding("text")

        cached_provider.reset_metrics()

        metrics = cached_provider.get_metrics()
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 0
        assert metrics["embeddings_generated"] == 0


class TestContextManager:
    """Tests for context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager(
        self, mock_provider: MockEmbeddingProvider, cache: EmbeddingCache
    ):
        """Test async context manager."""
        async with CachedEmbeddingProvider(mock_provider, cache) as provider:
            await provider.get_embedding("test")

        # Provider should be closed (mock doesn't do anything, but method called)

    @pytest.mark.asyncio
    async def test_close(self, cached_provider: CachedEmbeddingProvider):
        """Test explicit close."""
        await cached_provider.close()
        # Should not raise


class TestWrapWithCache:
    """Tests for wrap_with_cache helper function."""

    @pytest.mark.asyncio
    async def test_wrap_with_cache(
        self, mock_provider: MockEmbeddingProvider, cache: EmbeddingCache
    ):
        """Test wrap_with_cache creates CachedEmbeddingProvider."""
        wrapped = wrap_with_cache(mock_provider, cache)

        assert isinstance(wrapped, CachedEmbeddingProvider)
        assert wrapped.provider is mock_provider
        assert wrapped.cache is cache
        assert wrapped.cache_enabled is True

    @pytest.mark.asyncio
    async def test_wrap_with_cache_disabled(
        self, mock_provider: MockEmbeddingProvider, cache: EmbeddingCache
    ):
        """Test wrap_with_cache with disabled cache."""
        wrapped = wrap_with_cache(mock_provider, cache, enabled=False)

        assert wrapped.cache_enabled is False


class TestIntegration:
    """Integration tests with real embedding-like scenarios."""

    @pytest.mark.asyncio
    async def test_reindexing_scenario(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test cache behavior in reindexing scenario."""
        # Initial indexing
        documents = ["Doc 1 content", "Doc 2 content", "Doc 3 content"]
        await cached_provider.get_embeddings_batch(documents)

        initial_calls = len(mock_provider.batch_embed_calls)
        initial_generated = cached_provider.metrics.embeddings_generated

        # Reindexing (same documents)
        await cached_provider.get_embeddings_batch(documents)

        # Should use cache, no new provider calls
        assert len(mock_provider.batch_embed_calls) == initial_calls
        assert cached_provider.metrics.embeddings_generated == initial_generated
        assert cached_provider.metrics.cache_hits == 3

    @pytest.mark.asyncio
    async def test_incremental_indexing_scenario(
        self,
        cached_provider: CachedEmbeddingProvider,
        mock_provider: MockEmbeddingProvider,
    ):
        """Test cache behavior in incremental indexing scenario."""
        # Initial indexing
        existing = ["Existing 1", "Existing 2"]
        await cached_provider.get_embeddings_batch(existing)

        mock_provider.batch_embed_calls.clear()

        # Incremental: some new, some existing
        incremental = ["Existing 1", "New 1", "Existing 2", "New 2"]
        await cached_provider.get_embeddings_batch(incremental)

        # Only new documents should be embedded
        assert len(mock_provider.batch_embed_calls) == 1
        assert set(mock_provider.batch_embed_calls[0]) == {"New 1", "New 2"}

    @pytest.mark.asyncio
    async def test_high_hit_rate(
        self,
        cached_provider: CachedEmbeddingProvider,
    ):
        """Test achieving high hit rate."""
        # Cache some content
        await cached_provider.get_embeddings_batch([f"Doc {i}" for i in range(100)])

        cached_provider.reset_metrics()

        # Access same content multiple times
        for _ in range(10):
            await cached_provider.get_embeddings_batch([f"Doc {i}" for i in range(100)])

        metrics = cached_provider.get_metrics()
        assert metrics["hit_rate"] == 1.0  # 100% hit rate
        assert metrics["embeddings_generated"] == 0


class TestConcurrency:
    """Tests for concurrent access."""

    @pytest.mark.asyncio
    async def test_concurrent_same_text(
        self,
        cached_provider: CachedEmbeddingProvider,
    ):
        """Test concurrent requests for same text."""
        text = "Concurrent test"

        async def get_embedding():
            return await cached_provider.get_embedding(text)

        # Run concurrent requests
        results = await asyncio.gather(*[get_embedding() for _ in range(10)])

        # All results should be identical
        for r in results[1:]:
            np.testing.assert_array_almost_equal(results[0], r)

    @pytest.mark.asyncio
    async def test_concurrent_different_texts(
        self,
        cached_provider: CachedEmbeddingProvider,
    ):
        """Test concurrent requests for different texts."""
        async def get_embedding(i: int):
            return await cached_provider.get_embedding(f"Text {i}")

        # Run concurrent requests
        results = await asyncio.gather(*[get_embedding(i) for i in range(10)])

        assert len(results) == 10
        assert all(len(r) == 128 for r in results)
