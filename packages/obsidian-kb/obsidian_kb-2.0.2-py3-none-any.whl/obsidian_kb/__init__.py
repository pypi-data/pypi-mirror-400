"""Obsidian Knowledge Base with vector search."""

__version__ = "1.0.1"

from obsidian_kb.config import Settings, settings
from obsidian_kb.diagnostics import DiagnosticsService, send_notification
from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.error_handler import handle_errors, log_error_with_context, safe_execute
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.metrics import MetricsCollector, MetricsSummary, SearchMetric
from obsidian_kb.query_parser import ParsedQuery, QueryParser
from obsidian_kb.types import (
    DatabaseError,
    DocumentChunk,
    HealthCheck,
    HealthStatus,
    IndexingError,
    ObsidianKBError,
    OllamaConnectionError,
    SearchResult,
    SystemHealth,
    VaultNotFoundError,
    VaultStats,
)
from obsidian_kb.interfaces import (
    IDatabaseManager,
    IDiagnosticsService,
    IEmbeddingCache,
    IEmbeddingService,
    IMetricsCollector,
    IPerformanceMonitor,
    IRecoveryService,
    ISearchLogger,
    IVaultIndexer,
)
from obsidian_kb.search_optimizer import (
    AdaptiveAlphaCalculator,
    AgentQueryCache,
    AgentQueryNormalizer,
    FeatureExtractor,
    QueryExpander,
    RankingFeatures,
    RankingModel,
    ReRanker,
    SearchOptimizer,
)
from obsidian_kb.frontmatter_parser import FrontmatterData, FrontmatterParser
from obsidian_kb.fuzzy_matching import FuzzyMatcher
from obsidian_kb.rate_limiter import RateLimiter
from obsidian_kb.relative_date_parser import RelativeDateParser
from obsidian_kb.service_container import ServiceContainer, get_service_container, reset_service_container
from obsidian_kb.validation import ValidationError, validate_db_path, validate_vault_config, validate_vault_path
from obsidian_kb.vault_indexer import VaultIndexer

__all__ = [
    "__version__",
    "Settings",
    "settings",
    "VaultIndexer",
    "EmbeddingService",
    "LanceDBManager",
    "DiagnosticsService",
    "send_notification",
    "QueryParser",
    "ParsedQuery",
    "DocumentChunk",
    "SearchResult",
    "VaultStats",
    "HealthStatus",
    "HealthCheck",
    "SystemHealth",
    "ObsidianKBError",
    "VaultNotFoundError",
    "OllamaConnectionError",
    "IndexingError",
    "DatabaseError",
    "ValidationError",
    "validate_vault_config",
    "validate_vault_path",
    "validate_db_path",
    "handle_errors",
    "log_error_with_context",
    "safe_execute",
    "MetricsCollector",
    "MetricsSummary",
    "SearchMetric",
    "SearchOptimizer",
    "AdaptiveAlphaCalculator",
    "AgentQueryNormalizer",
    "AgentQueryCache",
    "QueryExpander",
    "ReRanker",
    "FeatureExtractor",
    "RankingModel",
    "RankingFeatures",
    # Интерфейсы (Protocol)
    "IEmbeddingService",
    "IDatabaseManager",
    "IVaultIndexer",
    "IEmbeddingCache",
    "IDiagnosticsService",
    "IMetricsCollector",
    "IRecoveryService",
    "ISearchLogger",
    "IPerformanceMonitor",
    # Парсеры
    "FrontmatterParser",
    "FrontmatterData",
    # Fuzzy Matching
    "FuzzyMatcher",
    # Relative Date Parser
    "RelativeDateParser",
    # Rate Limiting
    "RateLimiter",
    # Dependency Injection
    "ServiceContainer",
    "get_service_container",
    "reset_service_container",
]