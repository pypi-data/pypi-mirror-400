"""Стратегии поиска."""

from obsidian_kb.search.strategies.base import BaseSearchStrategy
from obsidian_kb.search.strategies.chunk_level import ChunkLevelStrategy
from obsidian_kb.search.strategies.document_level import DocumentLevelStrategy

__all__ = ["BaseSearchStrategy", "DocumentLevelStrategy", "ChunkLevelStrategy"]

