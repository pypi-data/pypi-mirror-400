"""Storage Layer - репозитории для работы с данными."""

from obsidian_kb.storage.change_detector import ChangeDetector, ChangeSet
from obsidian_kb.storage.chunk_enrichment_repository import ChunkEnrichmentRepository
from obsidian_kb.storage.chunk_repository import ChunkRepository
from obsidian_kb.storage.document_repository import DocumentRepository
from obsidian_kb.storage.file_watcher import (
    DebouncedChanges,
    FileChange,
    FileChangeType,
    FileWatcher,
)
from obsidian_kb.storage.indexing import (
    IncrementalIndexer,
    IndexingService,
    IndexingStats,
)
from obsidian_kb.storage.knowledge_cluster_repository import KnowledgeClusterRepository
from obsidian_kb.storage.metadata_service import MetadataService

__all__ = [
    # Repositories
    "ChunkRepository",
    "DocumentRepository",
    "ChunkEnrichmentRepository",
    "KnowledgeClusterRepository",
    # Services
    "IndexingService",
    "MetadataService",
    # Phase 2.0.4: Incremental Indexing
    "ChangeDetector",
    "ChangeSet",
    "IncrementalIndexer",
    "IndexingStats",
    "FileWatcher",
    "FileChange",
    "FileChangeType",
    "DebouncedChanges",
]

