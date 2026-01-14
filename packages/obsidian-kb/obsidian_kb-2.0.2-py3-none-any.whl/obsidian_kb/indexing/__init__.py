"""Гибридный пайплайн индексации для obsidian-kb.

Компоненты:
- ChunkingService: Markdown-aware разбиение документов
- ChangeDetector: Определение изменений в документах (consolidated in storage/)
- IndexingOrchestrator: Координация всего процесса индексации
"""

from obsidian_kb.indexing.chunking import ChunkInfo, ChunkingService, ChunkingStrategy
# Phase 2.0.6: ChangeDetector consolidated in storage/
from obsidian_kb.storage.change_detector import ChangeDetector, ChangeSet
from obsidian_kb.indexing.orchestrator import (
    EnrichmentStrategy,
    EnrichedDocument,
    IndexingJob,
    IndexingOrchestrator,
    IndexingResult,
    ProcessedDocument,
    VectorizedDocument,
)

__all__ = [
    "ChunkingService",
    "ChunkInfo",
    "ChunkingStrategy",
    "ChangeDetector",
    "ChangeSet",
    "IndexingOrchestrator",
    "IndexingJob",
    "EnrichmentStrategy",
    "ProcessedDocument",
    "EnrichedDocument",
    "VectorizedDocument",
    "IndexingResult",
]

