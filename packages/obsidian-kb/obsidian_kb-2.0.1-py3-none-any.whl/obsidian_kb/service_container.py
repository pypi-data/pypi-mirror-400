"""Контейнер сервисов для dependency injection.

Обеспечивает централизованное управление зависимостями и упрощает тестирование.

Все сервисы соответствуют соответствующим интерфейсам Protocol:
- db_manager: IDatabaseManager
- embedding_service: IEmbeddingService
- embedding_cache: IEmbeddingCache
- diagnostics_service: IDiagnosticsService
- metrics_collector: IMetricsCollector
- recovery_service: IRecoveryService
- search_logger: ISearchLogger
- performance_monitor: IPerformanceMonitor
- chunk_enrichment_repository: IChunkEnrichmentRepository
- llm_enrichment_service: ILLMEnrichmentService

Это позволяет использовать моки в тестах, соответствующие интерфейсам.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from obsidian_kb.config import Settings, settings
from obsidian_kb.diagnostics import DiagnosticsService
from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.providers.adapter import EmbeddingProviderAdapter
from obsidian_kb.providers.factory import ProviderFactory
from obsidian_kb.metrics import MetricsCollector
from obsidian_kb.performance_monitor import PerformanceMonitor
from obsidian_kb.presentation.formatter import MCPResultFormatter
from obsidian_kb.recovery import RecoveryService
from obsidian_kb.search.intent_detector import IntentDetector
from obsidian_kb.search.service import SearchService
from obsidian_kb.search_logger import SearchLogger
from obsidian_kb.rate_limiter import RateLimiter
# Lazy imports для избежания циклических зависимостей
# Импорты выполняются внутри методов property
from obsidian_kb.storage.chunk_repository import ChunkRepository
from obsidian_kb.storage.document_repository import DocumentRepository

if TYPE_CHECKING:
    from obsidian_kb.interfaces import (
        IBatchOperations,
        IDataviewService,
        IFrontmatterAPI,
        IGraphQueryService,
        IRipgrepService,
        ITimelineService,
        IChunkEnrichmentRepository,
        IChunkRepository,
        IDatabaseManager,
        IDiagnosticsService,
        IDocumentRepository,
        IEmbeddingCache,
        IEmbeddingService,
        IIntentDetector,
        ILLMEnrichmentService,
        IKnowledgeClusterService,
        IKnowledgeClusterRepository,
        IMetricsCollector,
        IPerformanceMonitor,
        IRecoveryService,
        IResultFormatter,
        ISearchLogger,
        ISearchService,
    )
    from obsidian_kb.providers.interfaces import (
        IChatCompletionProvider,
        IEmbeddingProvider,
    )

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Контейнер для управления зависимостями сервисов.
    
    Обеспечивает единую точку создания и управления сервисами,
    что упрощает тестирование и управление зависимостями.
    """
    
    def __init__(
        self,
        db_path: Path | None = None,
        ollama_url: str | None = None,
        embedding_model: str | None = None,
        custom_settings: Settings | None = None,
    ) -> None:
        """Инициализация контейнера сервисов.
        
        Args:
            db_path: Путь к базе данных (по умолчанию из settings)
            ollama_url: URL Ollama (по умолчанию из settings)
            embedding_model: Модель embedding (по умолчанию из settings)
            custom_settings: Кастомные настройки (для тестирования)
        """
        self._settings = custom_settings or settings
        
        # Переопределяем настройки если указаны
        if db_path:
            self._db_path = db_path
        else:
            self._db_path = Path(self._settings.db_path)
        
        # Инициализация сервисов (lazy loading)
        self._db_manager: LanceDBManager | None = None
        self._embedding_service: EmbeddingService | None = None
        self._embedding_cache: EmbeddingCache | None = None
        
        # V6: Multi-provider support
        self._embedding_provider: "IEmbeddingProvider | None" = None
        self._chat_provider: "IChatCompletionProvider | None" = None
        self._enrichment_chat_provider: "IChatCompletionProvider | None" = None
        self._diagnostics_service: DiagnosticsService | None = None
        self._metrics_collector: MetricsCollector | None = None
        self._recovery_service: RecoveryService | None = None
        self._search_logger: SearchLogger | None = None
        self._performance_monitor: PerformanceMonitor | None = None
        
        # V5: Новые сервисы (Storage, Search, Presentation layers)
        self._chunk_repository: ChunkRepository | None = None
        self._document_repository: DocumentRepository | None = None
        self._intent_detector: IntentDetector | None = None
        self._search_service: SearchService | None = None
        self._formatter: MCPResultFormatter | None = None
        
        # V6: Extended Query API services (lazy imports для избежания циклических зависимостей)
        self._frontmatter_api: "FrontmatterAPI | None" = None  # noqa: F821
        self._dataview_service: "DataviewService | None" = None  # noqa: F821
        
        # LLM Enrichment и Knowledge Clustering
        self._chunk_enrichment_repository: "IChunkEnrichmentRepository | None" = None
        self._llm_enrichment_service: "ILLMEnrichmentService | None" = None
        self._knowledge_cluster_repository: "IKnowledgeClusterRepository | None" = None
        self._knowledge_cluster_service: "IKnowledgeClusterService | None" = None
        self._ripgrep_service: "RipgrepService | None" = None  # noqa: F821
        self._graph_query_service: "GraphQueryService | None" = None  # noqa: F821
        self._timeline_service: "TimelineService | None" = None  # noqa: F821
        self._batch_operations: "BatchOperations | None" = None  # noqa: F821

        # MCP-specific services
        self._mcp_rate_limiter: RateLimiter | None = None
        self._job_queue: "BackgroundJobQueue | None" = None  # noqa: F821

        # Phase 2.0.5/2.0.6: Unified Metadata Access Layer
        self._sqlite_manager: "SQLiteManager | None" = None  # noqa: F821
        self._unified_metadata_accessor: "UnifiedMetadataAccessor | None" = None  # noqa: F821
        self._unified_document_service: "UnifiedDocumentService | None" = None  # noqa: F821
        self._metadata_sync_service: "MetadataSyncService | None" = None  # noqa: F821

        # Настройки для embedding service
        self._ollama_url = ollama_url or self._settings.ollama_url
        self._embedding_model = embedding_model or self._settings.embedding_model
    
    @property
    def db_manager(self) -> "IDatabaseManager":
        """Получение менеджера базы данных.
        
        Returns:
            Менеджер базы данных, соответствующий IDatabaseManager
        """
        if self._db_manager is None:
            self._db_manager = LanceDBManager(db_path=self._db_path)
        return self._db_manager
    
    @property
    def embedding_provider(self) -> "IEmbeddingProvider":
        """Получение провайдера embeddings (v6).
        
        Returns:
            Провайдер embeddings, соответствующий IEmbeddingProvider
        """
        if self._embedding_provider is None:
            # Используем ProviderFactory для создания провайдера
            # По умолчанию используем Ollama для обратной совместимости
            provider_name = getattr(self._settings, "embedding_provider", None) or "ollama"
            self._embedding_provider = ProviderFactory.get_embedding_provider(
                provider_name=provider_name,
                model=self._embedding_model,
                base_url=self._ollama_url,
            )
        return self._embedding_provider
    
    @property
    def chat_provider(self) -> "IChatCompletionProvider":
        """Получение провайдера chat completion (v6).
        
        Используется для обычного чата. Для enrichment используйте enrichment_chat_provider.
        
        Returns:
            Провайдер chat completion, соответствующий IChatCompletionProvider
        """
        if self._chat_provider is None:
            # Используем ProviderFactory для создания провайдера
            provider_name = getattr(self._settings, "chat_provider", None) or "ollama"
            self._chat_provider = ProviderFactory.get_chat_provider(
                provider_name=provider_name,
                model=self._settings.llm_model,
                base_url=self._ollama_url,
            )
        return self._chat_provider
    
    @property
    def enrichment_chat_provider(self) -> "IChatCompletionProvider":
        """Получение провайдера chat completion для enrichment (v6).
        
        Использует специальную модель для enrichment (например, qwen3-235b для JSON).
        Для Yandex использует yandex_enrichment_model, для других провайдеров - обычную модель.
        
        Returns:
            Провайдер chat completion для enrichment
        """
        if self._enrichment_chat_provider is None:
            provider_name = getattr(self._settings, "chat_provider", None) or "ollama"
            
            # Для Yandex используем enrichment_model, для других - обычную модель
            if provider_name.lower() == "yandex":
                enrichment_model = getattr(self._settings, "yandex_enrichment_model", None)
                if enrichment_model:
                    self._enrichment_chat_provider = ProviderFactory.get_chat_provider(
                        provider_name=provider_name,
                        model=enrichment_model,
                        use_for_enrichment=True,
                    )
                else:
                    # Fallback на обычный chat_provider
                    self._enrichment_chat_provider = self.chat_provider
            else:
                # Для других провайдеров используем обычную модель
                self._enrichment_chat_provider = self.chat_provider
        
        return self._enrichment_chat_provider
    
    @property
    def embedding_service(self) -> "IEmbeddingService":
        """Получение сервиса embeddings (обратная совместимость).
        
        Использует адаптер для преобразования IEmbeddingProvider в IEmbeddingService.
        В будущем этот метод будет deprecated, используйте embedding_provider напрямую.
        
        Returns:
            Сервис embeddings, соответствующий IEmbeddingService
        """
        if self._embedding_service is None:
            # Используем адаптер для обратной совместимости
            provider = self.embedding_provider
            self._embedding_service = EmbeddingProviderAdapter(provider)
        return self._embedding_service
    
    @property
    def embedding_cache(self) -> "IEmbeddingCache":
        """Получение кэша embeddings.
        
        Returns:
            Кэш embeddings, соответствующий IEmbeddingCache
        """
        if self._embedding_cache is None:
            self._embedding_cache = EmbeddingCache(db_path=self._db_path)
        return self._embedding_cache
    
    @property
    def diagnostics_service(self) -> "IDiagnosticsService":
        """Получение сервиса диагностики.
        
        Returns:
            Сервис диагностики, соответствующий IDiagnosticsService
        """
        if self._diagnostics_service is None:
            self._diagnostics_service = DiagnosticsService()
        return self._diagnostics_service
    
    @property
    def metrics_collector(self) -> "IMetricsCollector":
        """Получение сборщика метрик.
        
        Returns:
            Сборщик метрик, соответствующий IMetricsCollector
        """
        if self._metrics_collector is None:
            self._metrics_collector = MetricsCollector()
        return self._metrics_collector
    
    @property
    def recovery_service(self) -> "IRecoveryService":
        """Получение сервиса восстановления.
        
        Returns:
            Сервис восстановления, соответствующий IRecoveryService
        """
        if self._recovery_service is None:
            self._recovery_service = RecoveryService()
        return self._recovery_service
    
    @property
    def search_logger(self) -> "ISearchLogger":
        """Получение логгера поиска.
        
        Returns:
            Логгер поиска, соответствующий ISearchLogger
        """
        if self._search_logger is None:
            self._search_logger = SearchLogger()
        return self._search_logger
    
    @property
    def performance_monitor(self) -> "IPerformanceMonitor":
        """Получение монитора производительности.
        
        Returns:
            Монитор производительности, соответствующий IPerformanceMonitor
        """
        if self._performance_monitor is None:
            self._performance_monitor = PerformanceMonitor()
        return self._performance_monitor

    # ============================================================================
    # V5: Storage Layer (Repositories)
    # ============================================================================

    @property
    def chunk_repository(self) -> "IChunkRepository":
        """Получение репозитория чанков (v5).
        
        Returns:
            Репозиторий чанков, соответствующий IChunkRepository
        """
        if self._chunk_repository is None:
            self._chunk_repository = ChunkRepository(self.db_manager)
        return self._chunk_repository

    @property
    def document_repository(self) -> "IDocumentRepository":
        """Получение репозитория документов (v5).
        
        Returns:
            Репозиторий документов, соответствующий IDocumentRepository
        """
        if self._document_repository is None:
            self._document_repository = DocumentRepository(self.db_manager)
        return self._document_repository

    # ============================================================================
    # V5: Search Layer
    # ============================================================================

    @property
    def intent_detector(self) -> "IIntentDetector":
        """Получение детектора intent (v5).
        
        Returns:
            Детектор intent, соответствующий IIntentDetector
        """
        if self._intent_detector is None:
            self._intent_detector = IntentDetector()
        return self._intent_detector

    @property
    def search_service(self) -> "ISearchService":
        """Получение сервиса поиска (v5).
        
        Returns:
            Сервис поиска, соответствующий ISearchService
        """
        if self._search_service is None:
            self._search_service = SearchService(
                chunk_repo=self.chunk_repository,
                document_repo=self.document_repository,
                embedding_service=self.embedding_service,
                intent_detector=self.intent_detector,
            )
        return self._search_service

    # ============================================================================
    # V5: Presentation Layer
    # ============================================================================

    @property
    def formatter(self) -> "IResultFormatter":
        """Получение форматтера результатов (v5).
        
        Returns:
            Форматтер результатов, соответствующий IResultFormatter
        """
        if self._formatter is None:
            self._formatter = MCPResultFormatter()
        return self._formatter

    # ============================================================================
    # V6: Extended Query API
    # ============================================================================

    @property
    def frontmatter_api(self) -> "IFrontmatterAPI":
        """Получение FrontmatterAPI (v6).
        
        Returns:
            FrontmatterAPI, соответствующий IFrontmatterAPI
        """
        if self._frontmatter_api is None:
            from obsidian_kb.services.frontmatter_api import FrontmatterAPI
            self._frontmatter_api = FrontmatterAPI(services=self)
        return self._frontmatter_api
    
    @property
    def dataview_service(self) -> "IDataviewService":
        """Получение DataviewService (v6 Phase 2).
        
        Returns:
            DataviewService, соответствующий IDataviewService
        """
        if self._dataview_service is None:
            from obsidian_kb.services.dataview_service import DataviewService
            self._dataview_service = DataviewService()
        return self._dataview_service
    
    @property
    def ripgrep_service(self) -> "IRipgrepService":
        """Получение RipgrepService (v6 Phase 3).
        
        Returns:
            RipgrepService, соответствующий IRipgrepService
        """
        if self._ripgrep_service is None:
            from obsidian_kb.services.ripgrep_service import RipgrepService
            self._ripgrep_service = RipgrepService()
        return self._ripgrep_service
    
    @property
    def graph_query_service(self) -> "IGraphQueryService":
        """Получение GraphQueryService (v6 Phase 4).
        
        Returns:
            GraphQueryService, соответствующий IGraphQueryService
        """
        if self._graph_query_service is None:
            from obsidian_kb.services.graph_query_service import GraphQueryService
            self._graph_query_service = GraphQueryService()
        return self._graph_query_service
    
    @property
    def timeline_service(self) -> "ITimelineService":
        """Получение TimelineService (v6 Phase 4).
        
        Returns:
            TimelineService, соответствующий ITimelineService
        """
        if self._timeline_service is None:
            from obsidian_kb.services.timeline_service import TimelineService
            self._timeline_service = TimelineService()
        return self._timeline_service
    
    @property
    def batch_operations(self) -> "IBatchOperations":
        """Получение BatchOperations (v6 Phase 5).
        
        Returns:
            BatchOperations, соответствующий IBatchOperations
        """
        if self._batch_operations is None:
            from obsidian_kb.services.batch_operations import BatchOperations
            self._batch_operations = BatchOperations()
        return self._batch_operations

    # ============================================================================
    # MCP-specific Services
    # ============================================================================

    @property
    def mcp_rate_limiter(self) -> RateLimiter | None:
        """Получение rate limiter для MCP сервера.

        Returns:
            RateLimiter если включен в настройках, иначе None
        """
        if self._mcp_rate_limiter is None and self._settings.mcp_rate_limit_enabled:
            self._mcp_rate_limiter = RateLimiter(
                max_requests=self._settings.mcp_rate_limit_max_requests,
                window_seconds=self._settings.mcp_rate_limit_window_seconds,
                name="MCPRateLimiter",
            )
        return self._mcp_rate_limiter

    @property
    def job_queue(self) -> "BackgroundJobQueue | None":  # noqa: F821
        """Получение очереди фоновых задач.

        Returns:
            BackgroundJobQueue или None если не инициализирована
        """
        return self._job_queue

    def set_job_queue(self, job_queue: "BackgroundJobQueue | None") -> None:  # noqa: F821
        """Установка очереди фоновых задач.

        Args:
            job_queue: Экземпляр BackgroundJobQueue или None
        """
        self._job_queue = job_queue

    # ============================================================================
    # LLM Enrichment Services
    # ============================================================================
    
    @property
    def chunk_enrichment_repository(self) -> "IChunkEnrichmentRepository":
        """Получение репозитория обогащений.
        
        Returns:
            Репозиторий обогащений, соответствующий IChunkEnrichmentRepository
        """
        if self._chunk_enrichment_repository is None:
            from obsidian_kb.storage.chunk_enrichment_repository import ChunkEnrichmentRepository
            self._chunk_enrichment_repository = ChunkEnrichmentRepository(self.db_manager)
        return self._chunk_enrichment_repository
    
    @property
    def llm_enrichment_service(self) -> "ILLMEnrichmentService":
        """Получение сервиса LLM-обогащения.

        Returns:
            Сервис LLM-обогащения, соответствующий ILLMEnrichmentService
        """
        if self._llm_enrichment_service is None:
            from obsidian_kb.enrichment.llm_enrichment_service import LLMEnrichmentService
            from obsidian_kb.enrichment.strategies.full_enrichment_strategy import FullEnrichmentStrategy
            from obsidian_kb.enrichment.strategies.fast_enrichment_strategy import FastEnrichmentStrategy

            # Получаем chat provider для enrichment (работает с любым провайдером)
            chat_provider = self.enrichment_chat_provider

            # Выбираем стратегию на основе настроек
            strategy_name = self._settings.llm_enrichment_strategy.lower()
            if strategy_name == "fast":
                strategy = FastEnrichmentStrategy(
                    chat_provider=chat_provider,
                )
            else:  # По умолчанию "full"
                strategy = FullEnrichmentStrategy(
                    chat_provider=chat_provider,
                )

            self._llm_enrichment_service = LLMEnrichmentService(
                repository=self.chunk_enrichment_repository,
                recovery_service=self.recovery_service,
                chat_provider=chat_provider,
                strategy=strategy,
            )
        return self._llm_enrichment_service
    
    @property
    def knowledge_cluster_repository(self) -> "IKnowledgeClusterRepository":
        """Получение репозитория кластеров знаний.
        
        Returns:
            Репозиторий кластеров, соответствующий IKnowledgeClusterRepository
        """
        if self._knowledge_cluster_repository is None:
            from obsidian_kb.storage.knowledge_cluster_repository import KnowledgeClusterRepository
            self._knowledge_cluster_repository = KnowledgeClusterRepository(self.db_manager)
        return self._knowledge_cluster_repository
    
    @property
    def knowledge_cluster_service(self) -> "IKnowledgeClusterService":
        """Получение сервиса кластеризации знаний.
        
        Returns:
            Сервис кластеризации, соответствующий IKnowledgeClusterService
        """
        if self._knowledge_cluster_service is None:
            from obsidian_kb.enrichment.knowledge_cluster_service import KnowledgeClusterService
            from obsidian_kb.enrichment.strategies.clustering.kmeans_clustering import (
                KMeansClusteringStrategy,
            )
            
            # Создаем стратегию
            strategy = KMeansClusteringStrategy()
            
            self._knowledge_cluster_service = KnowledgeClusterService(
                db_manager=self.db_manager,
                embedding_service=self.embedding_service,
                llm_enrichment_service=self.llm_enrichment_service,
                chunk_repository=self.chunk_repository,
                document_repository=self.document_repository,
                cluster_repository=self.knowledge_cluster_repository,
                strategy=strategy,
            )
        return self._knowledge_cluster_service

    # ============================================================================
    # Phase 2.0.5/2.0.6: Unified Metadata Access Layer
    # ============================================================================

    @property
    def sqlite_manager(self) -> "SQLiteManager":
        """Получение SQLite менеджера (Phase 2.0.x).

        Returns:
            SQLiteManager для работы с метаданными
        """
        if self._sqlite_manager is None:
            from obsidian_kb.storage.sqlite.manager import SQLiteManager
            # SQLite DB располагается рядом с LanceDB
            sqlite_path = self._db_path / "metadata.db"
            self._sqlite_manager = SQLiteManager(db_path=sqlite_path)
        return self._sqlite_manager

    @property
    def unified_metadata_accessor(self) -> "UnifiedMetadataAccessor":
        """Получение UnifiedMetadataAccessor (Phase 2.0.5).

        Returns:
            UnifiedMetadataAccessor для унифицированного доступа к метаданным
        """
        if self._unified_metadata_accessor is None:
            from obsidian_kb.storage.unified import UnifiedMetadataAccessor
            self._unified_metadata_accessor = UnifiedMetadataAccessor(
                sqlite_manager=self.sqlite_manager,
                lancedb_manager=self.db_manager,
            )
        return self._unified_metadata_accessor

    @property
    def unified_document_service(self) -> "UnifiedDocumentService":
        """Получение UnifiedDocumentService (Phase 2.0.5).

        Высокоуровневый сервис для работы с документами через
        унифицированный доступ к SQLite и LanceDB.

        Returns:
            UnifiedDocumentService для высокоуровневых операций с документами
        """
        if self._unified_document_service is None:
            from obsidian_kb.storage.unified import UnifiedDocumentService
            self._unified_document_service = UnifiedDocumentService(
                sqlite_manager=self.sqlite_manager,
                lancedb_manager=self.db_manager,
                accessor=self.unified_metadata_accessor,
            )
        return self._unified_document_service

    @property
    def metadata_sync_service(self) -> "MetadataSyncService":
        """Получение MetadataSyncService (Phase 2.0.5).

        Сервис для синхронизации метаданных между SQLite и LanceDB.

        Returns:
            MetadataSyncService для синхронизации метаданных
        """
        if self._metadata_sync_service is None:
            from obsidian_kb.storage.unified import MetadataSyncService
            self._metadata_sync_service = MetadataSyncService(
                sqlite_manager=self.sqlite_manager,
                lancedb_manager=self.db_manager,
            )
        return self._metadata_sync_service

    async def cleanup(self) -> None:
        """Очистка ресурсов (закрытие соединений и т.д.)."""
        # Закрываем embedding service (адаптер или старый сервис)
        if self._embedding_service:
            if hasattr(self._embedding_service, "close"):
                await self._embedding_service.close()

        # Закрываем провайдеры напрямую
        if self._embedding_provider and hasattr(self._embedding_provider, "close"):
            await self._embedding_provider.close()

        if self._chat_provider and hasattr(self._chat_provider, "close"):
            await self._chat_provider.close()

        # Закрываем стратегии обогащения если они были созданы
        if self._llm_enrichment_service:
            strategy = getattr(self._llm_enrichment_service, "_strategy", None)
            if strategy and hasattr(strategy, "close"):
                await strategy.close()

        # Закрываем SQLite manager (Phase 2.0.x)
        if self._sqlite_manager and hasattr(self._sqlite_manager, "close"):
            await self._sqlite_manager.close()

        logger.debug("ServiceContainer cleaned up")


# Глобальный контейнер сервисов (singleton)
_global_container: ServiceContainer | None = None


def get_service_container(
    db_path: Path | None = None,
    ollama_url: str | None = None,
    embedding_model: str | None = None,
    custom_settings: Settings | None = None,
) -> ServiceContainer:
    """Получение глобального контейнера сервисов.
    
    Args:
        db_path: Путь к базе данных (используется только при первом создании)
        ollama_url: URL Ollama (используется только при первом создании)
        embedding_model: Модель embedding (используется только при первом создании)
        custom_settings: Кастомные настройки (для тестирования)
    
    Returns:
        Глобальный экземпляр ServiceContainer
    """
    global _global_container
    if _global_container is None:
        _global_container = ServiceContainer(
            db_path=db_path,
            ollama_url=ollama_url,
            embedding_model=embedding_model,
            custom_settings=custom_settings,
        )
    return _global_container


def reset_service_container() -> None:
    """Сброс глобального контейнера (для тестирования)."""
    global _global_container
    _global_container = None

