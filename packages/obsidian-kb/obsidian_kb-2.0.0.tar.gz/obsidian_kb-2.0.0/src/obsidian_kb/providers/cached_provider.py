"""Cached embedding provider wrapper.

This module provides a caching wrapper around any IEmbeddingProvider
to avoid re-vectorization of identical content.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from obsidian_kb.providers.interfaces import IEmbeddingProvider, ProviderHealth
from obsidian_kb.storage.sqlite.embedding_cache import EmbeddingCache

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Metrics for cached embedding provider.

    Attributes:
        cache_hits: Number of cache hits
        cache_misses: Number of cache misses
        total_requests: Total number of embedding requests
        hit_rate: Cache hit rate (0.0 to 1.0)
        embeddings_generated: Number of embeddings generated via provider
        bytes_saved: Estimated bytes saved by caching
    """

    cache_hits: int = 0
    cache_misses: int = 0
    embeddings_generated: int = 0

    @property
    def total_requests(self) -> int:
        """Total number of embedding requests."""
        return self.cache_hits + self.cache_misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    def reset(self) -> None:
        """Reset all metrics."""
        self.cache_hits = 0
        self.cache_misses = 0
        self.embeddings_generated = 0


class CachedEmbeddingProvider:
    """Caching wrapper for embedding providers.

    Wraps any IEmbeddingProvider and caches embeddings by content hash.
    Automatically checks cache before calling the underlying provider
    and saves results to cache.

    Usage:
        from obsidian_kb.providers.ollama import OllamaEmbeddingProvider
        from obsidian_kb.storage.sqlite import EmbeddingCache, SQLiteManager

        async with SQLiteManager("db.sqlite") as manager:
            cache = EmbeddingCache(manager)
            provider = OllamaEmbeddingProvider()
            cached_provider = CachedEmbeddingProvider(provider, cache)

            # First call - cache miss, calls provider
            emb1 = await cached_provider.get_embedding("Hello world")

            # Second call with same content - cache hit
            emb2 = await cached_provider.get_embedding("Hello world")

    Attributes:
        provider: Underlying embedding provider
        cache: EmbeddingCache instance
        metrics: CacheMetrics for monitoring
    """

    def __init__(
        self,
        provider: IEmbeddingProvider,
        cache: EmbeddingCache,
        cache_enabled: bool = True,
    ) -> None:
        """Initialize cached provider.

        Args:
            provider: Underlying embedding provider (must implement IEmbeddingProvider)
            cache: EmbeddingCache instance for storing embeddings
            cache_enabled: Whether caching is enabled (default: True)
        """
        self._provider = provider
        self._cache = cache
        self._cache_enabled = cache_enabled
        self._metrics = CacheMetrics()

    @property
    def name(self) -> str:
        """Provider name with cache indicator."""
        return f"cached_{self._provider.name}"

    @property
    def model(self) -> str:
        """Underlying model name."""
        return self._provider.model

    @property
    def dimensions(self) -> int:
        """Embedding dimensions."""
        return self._provider.dimensions

    @property
    def provider(self) -> IEmbeddingProvider:
        """Get underlying provider."""
        return self._provider

    @property
    def cache(self) -> EmbeddingCache:
        """Get cache instance."""
        return self._cache

    @property
    def metrics(self) -> CacheMetrics:
        """Get cache metrics."""
        return self._metrics

    @property
    def cache_enabled(self) -> bool:
        """Whether caching is enabled."""
        return self._cache_enabled

    @cache_enabled.setter
    def cache_enabled(self, value: bool) -> None:
        """Enable or disable caching."""
        self._cache_enabled = value

    async def get_embedding(
        self,
        text: str,
        embedding_type: str = "doc",
    ) -> list[float]:
        """Get embedding for text, using cache when possible.

        Args:
            text: Text to embed
            embedding_type: Type of embedding ("doc" or "query")

        Returns:
            Embedding vector as list of floats

        Raises:
            ProviderError: If embedding generation fails
        """
        if not self._cache_enabled:
            embedding = await self._provider.get_embedding(text, embedding_type)
            self._metrics.embeddings_generated += 1
            return embedding

        # Compute content hash
        content_hash = EmbeddingCache.compute_hash(text)

        # Check cache
        cached = await self._cache.get(content_hash, self.model)
        if cached is not None:
            self._metrics.cache_hits += 1
            logger.debug(f"Cache HIT for hash {content_hash[:8]}...")
            return cached.tolist()

        # Cache miss - generate embedding
        self._metrics.cache_misses += 1
        logger.debug(f"Cache MISS for hash {content_hash[:8]}...")

        embedding = await self._provider.get_embedding(text, embedding_type)
        self._metrics.embeddings_generated += 1

        # Save to cache
        await self._cache.set(content_hash, self.model, embedding)

        return embedding

    async def get_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        embedding_type: str = "doc",
    ) -> list[list[float]]:
        """Get embeddings for multiple texts, using cache when possible.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for provider (passed through)
            embedding_type: Type of embedding ("doc" or "query")

        Returns:
            List of embedding vectors

        Raises:
            ProviderError: If embedding generation fails
        """
        if not texts:
            return []

        if not self._cache_enabled:
            embeddings = await self._provider.get_embeddings_batch(
                texts, batch_size, embedding_type
            )
            self._metrics.embeddings_generated += len(texts)
            return embeddings

        # Compute hashes for all texts
        hashes = [EmbeddingCache.compute_hash(t) for t in texts]
        hash_to_idx = {h: i for i, h in enumerate(hashes)}

        # Batch get from cache
        cached = await self._cache.get_batch(hashes, self.model)

        # Prepare result array
        results: list[list[float] | None] = [None] * len(texts)

        # Fill in cached results
        texts_to_embed: list[str] = []
        hashes_to_embed: list[str] = []
        indices_to_embed: list[int] = []

        for i, (text, h) in enumerate(zip(texts, hashes)):
            if h in cached:
                results[i] = cached[h].tolist()
                self._metrics.cache_hits += 1
            else:
                texts_to_embed.append(text)
                hashes_to_embed.append(h)
                indices_to_embed.append(i)
                self._metrics.cache_misses += 1

        logger.debug(
            f"Cache batch: {len(cached)} hits, {len(texts_to_embed)} misses "
            f"out of {len(texts)} texts"
        )

        # Generate missing embeddings
        if texts_to_embed:
            new_embeddings = await self._provider.get_embeddings_batch(
                texts_to_embed, batch_size, embedding_type
            )
            self._metrics.embeddings_generated += len(texts_to_embed)

            # Save to cache and fill results
            cache_items: list[tuple[str, list[float]]] = []
            for idx, h, emb in zip(indices_to_embed, hashes_to_embed, new_embeddings):
                results[idx] = emb
                cache_items.append((h, emb))

            # Batch save to cache
            if cache_items:
                await self._cache.set_batch(cache_items, self.model)

        # All results should be filled now
        return [r for r in results if r is not None]

    async def health_check(self) -> ProviderHealth:
        """Check health of underlying provider.

        Returns:
            ProviderHealth from underlying provider
        """
        return await self._provider.health_check()

    async def close(self) -> None:
        """Close underlying provider."""
        if hasattr(self._provider, "close"):
            await self._provider.close()

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics as dictionary.

        Returns:
            Dict with cache metrics
        """
        return {
            "cache_hits": self._metrics.cache_hits,
            "cache_misses": self._metrics.cache_misses,
            "total_requests": self._metrics.total_requests,
            "hit_rate": self._metrics.hit_rate,
            "embeddings_generated": self._metrics.embeddings_generated,
            "cache_enabled": self._cache_enabled,
            "provider_name": self._provider.name,
            "model": self.model,
        }

    def reset_metrics(self) -> None:
        """Reset cache metrics."""
        self._metrics.reset()

    async def __aenter__(self) -> "CachedEmbeddingProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()


# Convenience function for creating cached provider
def wrap_with_cache(
    provider: IEmbeddingProvider,
    cache: EmbeddingCache,
    enabled: bool = True,
) -> CachedEmbeddingProvider:
    """Wrap an embedding provider with caching.

    Args:
        provider: Embedding provider to wrap
        cache: EmbeddingCache instance
        enabled: Whether caching is enabled

    Returns:
        CachedEmbeddingProvider wrapping the provider
    """
    return CachedEmbeddingProvider(provider, cache, cache_enabled=enabled)
