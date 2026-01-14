"""Unified Metadata Access Layer for obsidian-kb.

This package provides a unified interface for accessing document metadata
across SQLite and LanceDB storage backends.

Phase 2.0.5 - Unified Metadata Access Layer

Components:
- UnifiedMetadataAccessor: Low-level unified access to metadata
- UnifiedDocumentService: High-level document operations
- MetadataSyncService: Synchronization between storage backends

Types:
- UnifiedDocumentInfo: Unified document metadata
- ChunkInfo: Chunk information
- ConsistencyReport: Report on metadata consistency
- SyncResult: Result of sync operations
- DataSource: Enum for data source identification
"""

from obsidian_kb.storage.unified.document_service import UnifiedDocumentService
from obsidian_kb.storage.unified.metadata_accessor import UnifiedMetadataAccessor
from obsidian_kb.storage.unified.sync_service import MetadataSyncService
from obsidian_kb.storage.unified.types import (
    ChunkInfo,
    ConsistencyReport,
    DataSource,
    SyncResult,
    UnifiedDocumentInfo,
)

__all__ = [
    # Services
    "UnifiedMetadataAccessor",
    "UnifiedDocumentService",
    "MetadataSyncService",
    # Types
    "UnifiedDocumentInfo",
    "ChunkInfo",
    "ConsistencyReport",
    "SyncResult",
    "DataSource",
]
