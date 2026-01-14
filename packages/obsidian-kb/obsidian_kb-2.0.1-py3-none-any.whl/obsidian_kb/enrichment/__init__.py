"""Модуль LLM-обогащения чанков."""

from obsidian_kb.enrichment.contextual_retrieval import (
    EnrichedChunk,
    EnrichmentStats,
    EnrichmentStatus,
)
from obsidian_kb.enrichment.llm_enrichment_service import LLMEnrichmentService

__all__ = [
    "EnrichedChunk",
    "EnrichmentStats",
    "EnrichmentStatus",
    "LLMEnrichmentService",
]

