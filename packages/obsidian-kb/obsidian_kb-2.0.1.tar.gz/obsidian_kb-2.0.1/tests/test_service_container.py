"""Тесты для ServiceContainer (service_container.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.config import Settings
from obsidian_kb.service_container import (
    ServiceContainer,
    get_service_container,
    reset_service_container,
)


@pytest.fixture
def mock_settings():
    """Мок Settings."""
    settings = MagicMock(spec=Settings)
    settings.db_path = "/tmp/test_db"
    settings.ollama_url = "http://localhost:11434"
    settings.embedding_model = "nomic-embed-text"
    settings.llm_model = "llama3.2"
    settings.llm_enrichment_strategy = "full"
    settings.mcp_rate_limit_enabled = False
    settings.mcp_rate_limit_max_requests = 100
    settings.mcp_rate_limit_window_seconds = 60
    return settings


@pytest.fixture
def container(mock_settings):
    """ServiceContainer с моками."""
    return ServiceContainer(custom_settings=mock_settings)


@pytest.fixture(autouse=True)
def reset_global_container():
    """Сброс глобального контейнера перед каждым тестом."""
    reset_service_container()
    yield
    reset_service_container()


class TestServiceContainerInit:
    """Тесты инициализации."""

    def test_init_with_defaults(self, mock_settings):
        """Инициализация с настройками по умолчанию."""
        container = ServiceContainer(custom_settings=mock_settings)

        assert container._settings is mock_settings
        assert container._db_path == Path("/tmp/test_db")
        assert container._ollama_url == "http://localhost:11434"
        assert container._embedding_model == "nomic-embed-text"

    def test_init_with_custom_db_path(self, mock_settings):
        """Инициализация с кастомным db_path."""
        custom_path = Path("/custom/path")
        container = ServiceContainer(
            db_path=custom_path,
            custom_settings=mock_settings,
        )

        assert container._db_path == custom_path

    def test_init_with_custom_ollama_url(self, mock_settings):
        """Инициализация с кастомным ollama_url."""
        custom_url = "http://custom:8080"
        container = ServiceContainer(
            ollama_url=custom_url,
            custom_settings=mock_settings,
        )

        assert container._ollama_url == custom_url

    def test_init_with_custom_embedding_model(self, mock_settings):
        """Инициализация с кастомной моделью embedding."""
        custom_model = "custom-model"
        container = ServiceContainer(
            embedding_model=custom_model,
            custom_settings=mock_settings,
        )

        assert container._embedding_model == custom_model

    def test_lazy_initialization(self, container):
        """Все сервисы None при инициализации (lazy loading)."""
        assert container._db_manager is None
        assert container._embedding_service is None
        assert container._embedding_cache is None
        assert container._embedding_provider is None
        assert container._chat_provider is None
        assert container._diagnostics_service is None
        assert container._metrics_collector is None
        assert container._recovery_service is None
        assert container._search_logger is None
        assert container._performance_monitor is None
        assert container._chunk_repository is None
        assert container._document_repository is None
        assert container._intent_detector is None
        assert container._search_service is None
        assert container._formatter is None


class TestDbManager:
    """Тесты db_manager property."""

    def test_creates_lance_db_manager(self, container):
        """Создаёт LanceDBManager при первом обращении."""
        with patch("obsidian_kb.service_container.LanceDBManager") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.db_manager

            assert result is mock_instance
            mock_class.assert_called_once_with(db_path=container._db_path)

    def test_caches_instance(self, container):
        """Кэширует экземпляр (singleton в контейнере)."""
        with patch("obsidian_kb.service_container.LanceDBManager") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result1 = container.db_manager
            result2 = container.db_manager

            assert result1 is result2
            mock_class.assert_called_once()  # Вызван только один раз


class TestEmbeddingProvider:
    """Тесты embedding_provider property."""

    def test_creates_provider(self, container):
        """Создаёт провайдер через ProviderFactory."""
        with patch("obsidian_kb.service_container.ProviderFactory") as mock_factory:
            mock_provider = MagicMock()
            mock_factory.get_embedding_provider.return_value = mock_provider

            result = container.embedding_provider

            assert result is mock_provider
            mock_factory.get_embedding_provider.assert_called_once()

    def test_uses_ollama_by_default(self, container):
        """По умолчанию использует ollama."""
        with patch("obsidian_kb.service_container.ProviderFactory") as mock_factory:
            mock_provider = MagicMock()
            mock_factory.get_embedding_provider.return_value = mock_provider

            container.embedding_provider

            call_kwargs = mock_factory.get_embedding_provider.call_args
            assert call_kwargs.kwargs.get("provider_name") == "ollama"


class TestEmbeddingService:
    """Тесты embedding_service property."""

    def test_creates_adapter(self, container):
        """Создаёт адаптер для обратной совместимости."""
        with (
            patch("obsidian_kb.service_container.ProviderFactory") as mock_factory,
            patch("obsidian_kb.service_container.EmbeddingProviderAdapter") as mock_adapter_class,
        ):
            mock_provider = MagicMock()
            mock_factory.get_embedding_provider.return_value = mock_provider
            mock_adapter = MagicMock()
            mock_adapter_class.return_value = mock_adapter

            result = container.embedding_service

            assert result is mock_adapter
            mock_adapter_class.assert_called_once_with(mock_provider)


class TestEmbeddingCache:
    """Тесты embedding_cache property."""

    def test_creates_embedding_cache(self, container):
        """Создаёт EmbeddingCache."""
        with patch("obsidian_kb.service_container.EmbeddingCache") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.embedding_cache

            assert result is mock_instance
            mock_class.assert_called_once_with(db_path=container._db_path)


class TestDiagnosticsService:
    """Тесты diagnostics_service property."""

    def test_creates_diagnostics_service(self, container):
        """Создаёт DiagnosticsService."""
        with patch("obsidian_kb.service_container.DiagnosticsService") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.diagnostics_service

            assert result is mock_instance
            mock_class.assert_called_once()


class TestMetricsCollector:
    """Тесты metrics_collector property."""

    def test_creates_metrics_collector(self, container):
        """Создаёт MetricsCollector."""
        with patch("obsidian_kb.service_container.MetricsCollector") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.metrics_collector

            assert result is mock_instance
            mock_class.assert_called_once()


class TestRecoveryService:
    """Тесты recovery_service property."""

    def test_creates_recovery_service(self, container):
        """Создаёт RecoveryService."""
        with patch("obsidian_kb.service_container.RecoveryService") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.recovery_service

            assert result is mock_instance
            mock_class.assert_called_once()


class TestSearchLogger:
    """Тесты search_logger property."""

    def test_creates_search_logger(self, container):
        """Создаёт SearchLogger."""
        with patch("obsidian_kb.service_container.SearchLogger") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.search_logger

            assert result is mock_instance
            mock_class.assert_called_once()


class TestPerformanceMonitor:
    """Тесты performance_monitor property."""

    def test_creates_performance_monitor(self, container):
        """Создаёт PerformanceMonitor."""
        with patch("obsidian_kb.service_container.PerformanceMonitor") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.performance_monitor

            assert result is mock_instance
            mock_class.assert_called_once()


class TestChunkRepository:
    """Тесты chunk_repository property."""

    def test_creates_chunk_repository(self, container):
        """Создаёт ChunkRepository."""
        with (
            patch("obsidian_kb.service_container.ChunkRepository") as mock_class,
            patch("obsidian_kb.service_container.LanceDBManager"),
        ):
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.chunk_repository

            assert result is mock_instance
            mock_class.assert_called_once()


class TestDocumentRepository:
    """Тесты document_repository property."""

    def test_creates_document_repository(self, container):
        """Создаёт DocumentRepository."""
        with (
            patch("obsidian_kb.service_container.DocumentRepository") as mock_class,
            patch("obsidian_kb.service_container.LanceDBManager"),
        ):
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.document_repository

            assert result is mock_instance
            mock_class.assert_called_once()


class TestIntentDetector:
    """Тесты intent_detector property."""

    def test_creates_intent_detector(self, container):
        """Создаёт IntentDetector."""
        with patch("obsidian_kb.service_container.IntentDetector") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.intent_detector

            assert result is mock_instance
            mock_class.assert_called_once()


class TestSearchService:
    """Тесты search_service property."""

    def test_creates_search_service(self, container):
        """Создаёт SearchService с зависимостями."""
        with (
            patch("obsidian_kb.service_container.SearchService") as mock_class,
            patch("obsidian_kb.service_container.ChunkRepository"),
            patch("obsidian_kb.service_container.DocumentRepository"),
            patch("obsidian_kb.service_container.IntentDetector"),
            patch("obsidian_kb.service_container.LanceDBManager"),
            patch("obsidian_kb.service_container.ProviderFactory"),
            patch("obsidian_kb.service_container.EmbeddingProviderAdapter"),
        ):
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.search_service

            assert result is mock_instance
            mock_class.assert_called_once()

    def test_search_service_dependencies(self, container):
        """SearchService получает правильные зависимости."""
        with (
            patch("obsidian_kb.service_container.SearchService") as mock_class,
            patch("obsidian_kb.service_container.ChunkRepository") as mock_chunk_repo,
            patch("obsidian_kb.service_container.DocumentRepository") as mock_doc_repo,
            patch("obsidian_kb.service_container.IntentDetector") as mock_intent,
            patch("obsidian_kb.service_container.LanceDBManager"),
            patch("obsidian_kb.service_container.ProviderFactory"),
            patch("obsidian_kb.service_container.EmbeddingProviderAdapter"),
        ):
            container.search_service

            call_kwargs = mock_class.call_args.kwargs
            assert "chunk_repo" in call_kwargs
            assert "document_repo" in call_kwargs
            assert "embedding_service" in call_kwargs
            assert "intent_detector" in call_kwargs


class TestFormatter:
    """Тесты formatter property."""

    def test_creates_formatter(self, container):
        """Создаёт MCPResultFormatter."""
        with patch("obsidian_kb.service_container.MCPResultFormatter") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.formatter

            assert result is mock_instance
            mock_class.assert_called_once()


class TestMcpRateLimiter:
    """Тесты mcp_rate_limiter property."""

    def test_returns_none_when_disabled(self, container, mock_settings):
        """Возвращает None когда rate_limit выключен."""
        mock_settings.mcp_rate_limit_enabled = False

        result = container.mcp_rate_limiter

        assert result is None

    def test_creates_rate_limiter_when_enabled(self, mock_settings):
        """Создаёт RateLimiter когда включен."""
        mock_settings.mcp_rate_limit_enabled = True
        container = ServiceContainer(custom_settings=mock_settings)

        with patch("obsidian_kb.service_container.RateLimiter") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = container.mcp_rate_limiter

            assert result is mock_instance
            mock_class.assert_called_once_with(
                max_requests=100,
                window_seconds=60,
                name="MCPRateLimiter",
            )


class TestJobQueue:
    """Тесты job_queue property и set_job_queue."""

    def test_job_queue_initially_none(self, container):
        """job_queue изначально None."""
        assert container.job_queue is None

    def test_set_job_queue(self, container):
        """set_job_queue устанавливает очередь."""
        mock_queue = MagicMock()

        container.set_job_queue(mock_queue)

        assert container.job_queue is mock_queue

    def test_set_job_queue_to_none(self, container):
        """set_job_queue может установить None."""
        mock_queue = MagicMock()
        container.set_job_queue(mock_queue)

        container.set_job_queue(None)

        assert container.job_queue is None


class TestCleanup:
    """Тесты cleanup метода."""

    @pytest.mark.asyncio
    async def test_cleanup_closes_embedding_service(self, container):
        """cleanup закрывает embedding_service."""
        mock_service = MagicMock()
        mock_service.close = AsyncMock()
        container._embedding_service = mock_service

        await container.cleanup()

        mock_service.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_closes_embedding_provider(self, container):
        """cleanup закрывает embedding_provider."""
        mock_provider = MagicMock()
        mock_provider.close = AsyncMock()
        container._embedding_provider = mock_provider

        await container.cleanup()

        mock_provider.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_closes_chat_provider(self, container):
        """cleanup закрывает chat_provider."""
        mock_provider = MagicMock()
        mock_provider.close = AsyncMock()
        container._chat_provider = mock_provider

        await container.cleanup()

        mock_provider.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_closes_enrichment_strategy(self, container):
        """cleanup закрывает стратегию обогащения."""
        mock_strategy = MagicMock()
        mock_strategy.close = AsyncMock()
        mock_service = MagicMock()
        mock_service._strategy = mock_strategy
        container._llm_enrichment_service = mock_service

        await container.cleanup()

        mock_strategy.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_handles_missing_close_method(self, container):
        """cleanup не падает если нет метода close."""
        mock_service = MagicMock(spec=[])  # spec без close
        container._embedding_service = mock_service

        # Не должен вызвать ошибку
        await container.cleanup()


class TestGlobalContainer:
    """Тесты глобального контейнера."""

    def test_get_service_container_creates_singleton(self, mock_settings):
        """get_service_container создаёт singleton."""
        with patch("obsidian_kb.service_container.settings", mock_settings):
            container1 = get_service_container(custom_settings=mock_settings)
            container2 = get_service_container()

            assert container1 is container2

    def test_reset_service_container(self, mock_settings):
        """reset_service_container сбрасывает singleton."""
        with patch("obsidian_kb.service_container.settings", mock_settings):
            container1 = get_service_container(custom_settings=mock_settings)
            reset_service_container()
            container2 = get_service_container(custom_settings=mock_settings)

            assert container1 is not container2

    def test_get_service_container_with_custom_params(self, mock_settings):
        """get_service_container с кастомными параметрами."""
        custom_path = Path("/custom/db")

        with patch("obsidian_kb.service_container.settings", mock_settings):
            container = get_service_container(
                db_path=custom_path,
                ollama_url="http://custom:8080",
                embedding_model="custom-model",
                custom_settings=mock_settings,
            )

            assert container._db_path == custom_path
            assert container._ollama_url == "http://custom:8080"
            assert container._embedding_model == "custom-model"


class TestLazyLoadedServices:
    """Тесты lazy-loaded сервисов (Extended Query API)."""

    def test_frontmatter_api_lazy_import(self, container):
        """frontmatter_api использует lazy import."""
        with patch.dict("sys.modules", {"obsidian_kb.services.frontmatter_api": MagicMock()}):
            with patch(
                "obsidian_kb.services.frontmatter_api.FrontmatterAPI"
            ) as mock_class:
                mock_instance = MagicMock()
                mock_class.return_value = mock_instance

                # Доступ к property вызывает импорт
                result = container.frontmatter_api

                # Проверяем что сервис создан
                assert container._frontmatter_api is not None

    def test_dataview_service_lazy_import(self, container):
        """dataview_service использует lazy import."""
        with patch.dict("sys.modules", {"obsidian_kb.services.dataview_service": MagicMock()}):
            with patch(
                "obsidian_kb.services.dataview_service.DataviewService"
            ) as mock_class:
                mock_instance = MagicMock()
                mock_class.return_value = mock_instance

                result = container.dataview_service

                assert container._dataview_service is not None


class TestServiceCaching:
    """Тесты кэширования сервисов."""

    def test_all_services_cached(self, container):
        """Все сервисы кэшируются после первого создания."""
        services_to_test = [
            ("diagnostics_service", "DiagnosticsService"),
            ("metrics_collector", "MetricsCollector"),
            ("recovery_service", "RecoveryService"),
            ("search_logger", "SearchLogger"),
            ("performance_monitor", "PerformanceMonitor"),
            ("intent_detector", "IntentDetector"),
            ("formatter", "MCPResultFormatter"),
        ]

        for prop_name, class_name in services_to_test:
            with patch(f"obsidian_kb.service_container.{class_name}") as mock_class:
                mock_instance = MagicMock()
                mock_class.return_value = mock_instance

                # Первый доступ
                result1 = getattr(container, prop_name)
                # Второй доступ
                result2 = getattr(container, prop_name)

                # Должен быть тот же экземпляр
                assert result1 is result2
                # Класс вызван только один раз
                mock_class.assert_called_once()

                # Сбросим для следующей итерации
                setattr(container, f"_{prop_name}", None)
