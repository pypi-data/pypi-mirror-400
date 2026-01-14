"""Интерфейсы (Protocol) для основных компонентов системы.

Используются для улучшения тестируемости и разделения ответственности.
"""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, TypedDict

from obsidian_kb.query.where_parser import WhereCondition
from obsidian_kb.types import (
    Chunk,
    ChunkEnrichment,
    ChunkSearchResult,
    Document,
    DocumentSearchResult,
    DocumentChunk,
    DocumentInfo,
    FieldInfo,
    FrontmatterSchema,
    HealthCheck,
    IntentDetectionResult,
    KnowledgeCluster,
    PropertyAggregation,
    SearchRequest,
    SearchResponse,
    SystemHealth,
    VaultStats,
)

if TYPE_CHECKING:
    from obsidian_kb.metrics import MetricsSummary
    from obsidian_kb.performance_monitor import OperationMetrics, PerformanceReport
    from obsidian_kb.recovery import CircuitBreaker


# Type aliases для повышения читаемости и типобезопасности
LogContextValue = str | int | float | bool | None
LogContext = dict[str, LogContextValue]


class IndexingProgress(TypedDict, total=False):
    """Прогресс индексации vault'а."""

    vault_name: str
    total_files: int
    indexed_files: int
    failed_files: int
    last_indexed_file: str | None
    started_at: str  # ISO datetime
    updated_at: str  # ISO datetime


class VaultStatsDict(TypedDict, total=False):
    """Статистика vault'а для логирования."""

    file_count: int
    chunk_count: int
    total_size_bytes: int
    tags_count: int


class IEmbeddingService(Protocol):
    """Интерфейс для сервиса генерации embeddings."""

    async def get_embedding(self, text: str) -> list[float]:
        """Генерация embedding для текста.

        Args:
            text: Текст для генерации embedding

        Returns:
            Векторное представление текста

        Raises:
            OllamaConnectionError: При ошибке подключения к Ollama
        """
        ...

    async def get_embeddings_batch(
        self, texts: list[str], batch_size: int = 10
    ) -> list[list[float]]:
        """Батчевая генерация embeddings.

        Args:
            texts: Список текстов для генерации embeddings
            batch_size: Размер батча

        Returns:
            Список векторных представлений

        Raises:
            OllamaConnectionError: При ошибке подключения к Ollama
        """
        ...


class IDatabaseManager(Protocol):
    """Интерфейс для менеджера базы данных.
    
    В v5 используйте репозитории (chunks, documents) для доступа к данным.
    Для поиска используйте ISearchService.
    """

    # === Репозитории (v5) ===
    
    @property
    def chunks(self) -> "IChunkRepository":
        """Репозиторий чанков."""
        ...
    
    @property
    def documents(self) -> "IDocumentRepository":
        """Репозиторий документов."""
        ...

    async def upsert_chunks(
        self,
        vault_name: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Добавление или обновление чанков в БД.
        
        Примечание: В v4 записывает данные в 4 таблицы:
        - documents (метаданные файла)
        - chunks (векторизованное содержимое)
        - document_properties (свойства из frontmatter)
        - metadata (полный frontmatter в JSON)

        Args:
            vault_name: Имя vault'а
            chunks: Список чанков
            embeddings: Список векторов (должен соответствовать chunks)

        Raises:
            DatabaseError: При ошибке работы с БД
            ValueError: При несоответствии количества chunks и embeddings
        """
        ...

    async def delete_file(self, vault_name: str, file_path: str) -> None:
        """Удаление файла из индекса.
        
        Примечание: В v4 удаляет данные из всех 4 таблиц (documents, chunks, document_properties, metadata).

        Args:
            vault_name: Имя vault'а
            file_path: Путь к файлу

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...

    async def get_vault_stats(self, vault_name: str) -> VaultStats:
        """Получение статистики по vault'у.
        
        Примечание: В v4 собирает статистику из таблицы documents.

        Args:
            vault_name: Имя vault'а

        Returns:
            Статистика vault'а

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...

    async def list_vaults(self) -> list[str]:
        """Получение списка всех проиндексированных vault'ов.

        Returns:
            Список имён vault'ов

        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...

    async def get_documents_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
        property_value_pattern: str | None = None,
    ) -> set[str]:
        """Получение document_id документов с указанным свойством (v4).
        
        Используется для двухэтапных запросов: сначала фильтрация по документам,
        затем поиск среди чанков этих документов.

        Args:
            vault_name: Имя vault'а
            property_key: Ключ свойства (type, author, team, status, etc.)
            property_value: Точное значение свойства (для точного поиска)
            property_value_pattern: Паттерн для поиска (LIKE, для fuzzy matching)

        Returns:
            Множество document_id документов с указанным свойством

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...

    async def get_document_properties(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, str]:
        """Получение всех свойств документа (v4).

        Args:
            vault_name: Имя vault'а
            document_id: ID документа

        Returns:
            Словарь {property_key: property_value} всех свойств документа

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...

    async def get_documents_by_tags(
        self,
        vault_name: str,
        tags: list[str],
        match_all: bool = True,
    ) -> set[str]:
        """Получение document_id документов с указанными frontmatter тегами (v4).
        
        Используется для двухэтапных запросов: сначала фильтрация по документам,
        затем поиск среди чанков этих документов.
        
        Args:
            vault_name: Имя vault'а
            tags: Список тегов для поиска
            match_all: Если True, документ должен содержать все теги (AND).
                      Если False, документ должен содержать хотя бы один тег (OR).
        
        Returns:
            Множество document_id документов с указанными тегами
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...

    async def get_document_info(
        self,
        vault_name: str,
        document_id: str,
    ) -> DocumentInfo | None:
        """Получение метаданных документа (v4).

        Args:
            vault_name: Имя vault'а
            document_id: ID документа

        Returns:
            DocumentInfo или None если документ не найден

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...


class IVaultIndexer(Protocol):
    """Интерфейс для индексатора vault'ов."""

    async def scan_all(
        self,
        max_workers: int = 4,
        progress_callback: Callable[[str, str], None] | None = None,
    ) -> AsyncIterator[DocumentChunk]:
        """Сканирование всех файлов в vault'е.

        Args:
            max_workers: Максимальное количество параллельных воркеров
            progress_callback: Callback для отслеживания прогресса (file_path, status)

        Yields:
            DocumentChunk для каждого найденного чанка

        Raises:
            IndexingError: При ошибке индексации
        """
        ...

    async def scan_file(self, file_path: Path) -> list[DocumentChunk]:
        """Сканирование одного файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Список чанков документа

        Raises:
            IndexingError: При ошибке индексации
        """
        ...

    def watch(self, callback: Callable[[Path, str], None]) -> None:
        """Запуск наблюдения за изменениями файлов.

        Args:
            callback: Функция, вызываемая при изменении файла (file_path, event_type)

        Raises:
            IndexingError: При ошибке запуска наблюдения
        """
        ...

    def stop_watching(self) -> None:
        """Остановка наблюдения за изменениями файлов."""
        ...


class IEmbeddingCache(Protocol):
    """Интерфейс для кэша embeddings."""

    async def get_cached_embeddings(
        self, texts: list[str], model_name: str
    ) -> dict[str, list[float]]:
        """Получение кэшированных embeddings.

        Args:
            texts: Список текстов
            model_name: Имя модели embedding

        Returns:
            Словарь {hash(text): embedding} для кэшированных текстов
        """
        ...

    async def cache_embeddings(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        model_name: str,
    ) -> None:
        """Сохранение embeddings в кэш.

        Args:
            texts: Список текстов
            embeddings: Список embeddings
            model_name: Имя модели embedding

        Raises:
            DatabaseError: При ошибке записи в БД
        """
        ...

    async def invalidate_file(self, file_path: str) -> None:
        """Инвалидация кэша для файла.

        Args:
            file_path: Путь к файлу
        """
        ...


class IDiagnosticsService(Protocol):
    """Интерфейс для сервиса диагностики системы."""

    async def check_ollama(self) -> HealthCheck:
        """Проверка доступности Ollama.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def check_lancedb(self) -> HealthCheck:
        """Проверка базы данных LanceDB.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def check_vaults(self) -> HealthCheck:
        """Проверка конфигурации vault'ов.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def check_disk_space(self) -> HealthCheck:
        """Проверка свободного места на диске.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def check_memory(self) -> HealthCheck:
        """Проверка использования памяти.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def check_cpu(self) -> HealthCheck:
        """Проверка использования CPU.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def check_performance(self) -> HealthCheck:
        """Проверка производительности системы.

        Returns:
            HealthCheck с результатом проверки
        """
        ...

    async def full_check(self, send_notifications: bool = False) -> SystemHealth:
        """Полная диагностика системы.

        Args:
            send_notifications: Отправлять ли уведомления о проблемах

        Returns:
            SystemHealth с результатами всех проверок
        """
        ...

    async def index_coverage(self, vault_name: str) -> dict[str, Any]:
        """Проверка покрытия индекса для vault'а.

        Args:
            vault_name: Имя vault'а

        Returns:
            Словарь со статистикой покрытия индекса
        """
        ...

    async def check_metrics(self, days: int = 1) -> dict[str, Any]:
        """Проверка записи метрик.

        Args:
            days: Количество дней для проверки

        Returns:
            Словарь со статистикой метрик
        """
        ...

    async def check_index(self, vault_name: str) -> dict[str, Any]:
        """Проверка индексации vault'а.

        Args:
            vault_name: Имя vault'а

        Returns:
            Словарь с результатами проверки индексации
        """
        ...


class IMetricsCollector(Protocol):
    """Интерфейс для сборщика метрик."""

    async def record_search(
        self,
        vault_name: str | None,
        query: str,
        search_type: str,
        result_count: int,
        execution_time_ms: float,
        user: str | None = None,
        avg_relevance_score: float = 0.0,
    ) -> None:
        """Запись метрики поиска.

        Args:
            vault_name: Имя vault'а (None для multi-vault поиска)
            query: Поисковый запрос
            search_type: Тип поиска (vector, fts, hybrid)
            result_count: Количество результатов
            execution_time_ms: Время выполнения в миллисекундах
            user: Идентификатор пользователя (опционально)
            avg_relevance_score: Средняя релевантность результатов (0-1)
        """
        ...

    async def get_summary(
        self,
        days: int = 7,
        limit: int = 10,
        vault_name: str | None = None,
    ) -> "MetricsSummary":
        """Получение сводки метрик за период.

        Args:
            days: Количество дней для анализа (по умолчанию 7)
            limit: Максимальное количество популярных запросов/vault'ов
            vault_name: Фильтр по конкретному vault'у (опционально)

        Returns:
            Сводка метрик
        """
        ...

    async def export_to_json(self, output_path: Path, days: int = 30) -> None:
        """Экспорт метрик в JSON файл.

        Args:
            output_path: Путь к выходному файлу
            days: Количество дней для экспорта
        """
        ...

    async def export_to_csv(self, output_path: Path, days: int = 30) -> None:
        """Экспорт метрик в CSV файл.

        Args:
            output_path: Путь к выходному файлу
            days: Количество дней для экспорта
        """
        ...

    async def clear_old_metrics(self, days_to_keep: int = 90) -> int:
        """Очистка старых метрик.

        Args:
            days_to_keep: Количество дней для хранения метрик

        Returns:
            Количество удалённых записей
        """
        ...


class IRecoveryService(Protocol):
    """Интерфейс для сервиса восстановления после сбоев."""

    def get_circuit_breaker(self, name: str) -> "CircuitBreaker":
        """Получение или создание circuit breaker для операции.

        Args:
            name: Имя операции

        Returns:
            CircuitBreaker для операции
        """
        ...

    async def retry_with_backoff(
        self,
        func: Callable[..., Any],
        *args: Any,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        operation_name: str = "operation",
        **kwargs: Any,
    ) -> Any:
        """Выполнение функции с повторными попытками и exponential backoff.

        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            max_retries: Максимальное количество попыток
            initial_delay: Начальная задержка в секундах
            max_delay: Максимальная задержка в секундах
            exponential_base: База для exponential backoff
            operation_name: Имя операции для логирования
            **kwargs: Именованные аргументы

        Returns:
            Результат выполнения функции

        Raises:
            Последнее исключение, если все попытки неудачны
        """
        ...

    async def recover_database_connection(
        self, db_manager: "IDatabaseManager", max_retries: int = 3
    ) -> bool:
        """Восстановление подключения к базе данных.

        Args:
            db_manager: Менеджер базы данных
            max_retries: Максимальное количество попыток

        Returns:
            True если подключение восстановлено, False иначе
        """
        ...

    async def recover_ollama_connection(
        self, embedding_service: "IEmbeddingService", max_retries: int = 3
    ) -> bool:
        """Восстановление подключения к Ollama.

        Args:
            embedding_service: Сервис embeddings
            max_retries: Максимальное количество попыток

        Returns:
            True если подключение восстановлено, False иначе
        """
        ...

    def save_indexing_progress(
        self, vault_name: str, progress: IndexingProgress
    ) -> None:
        """Сохранение прогресса индексации.

        Args:
            vault_name: Имя vault'а
            progress: Словарь с информацией о прогрессе
        """
        ...

    def load_indexing_progress(self, vault_name: str) -> IndexingProgress | None:
        """Загрузка прогресса индексации.

        Args:
            vault_name: Имя vault'а

        Returns:
            Прогресс индексации или None если не найден
        """
        ...

    def clear_indexing_progress(self, vault_name: str) -> None:
        """Очистка прогресса индексации.

        Args:
            vault_name: Имя vault'а
        """
        ...


class ISearchLogger(Protocol):
    """Интерфейс для логгера поисковых запросов."""

    def log_search(
        self,
        original_query: str,
        normalized_query: str | None = None,
        vault_name: str | None = None,
        search_type: str = "hybrid",
        result_count: int = 0,
        execution_time_ms: float = 0.0,
        avg_relevance_score: float = 0.0,
        empty_results: bool = False,
        used_optimizer: bool = False,
        source: str = "mcp",
        requested_search_type: str | None = None,
        was_fallback: bool = False,
        ollama_available: bool = True,
        filters: dict[str, Any] | None = None,
        where_clause: str | None = None,
        embedding_time_ms: float | None = None,
        query_length: int | None = None,
        limit: int | None = None,
        cache_hit: bool | None = None,
        error: str | None = None,
        vault_stats: VaultStatsDict | None = None,
        embedding_model: str | None = None,
        rerank_used: bool | None = None,
        feature_ranking_used: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Логирование поискового запроса.

        Args:
            original_query: Исходный запрос (до нормализации)
            normalized_query: Нормализованный запрос (после обработки)
            vault_name: Имя vault'а (None для multi-vault поиска)
            search_type: Тип поиска (vector, fts, hybrid, links)
            result_count: Количество результатов
            execution_time_ms: Время выполнения в миллисекундах
            avg_relevance_score: Средняя релевантность результатов (0-1)
            empty_results: Пустые результаты
            used_optimizer: Использовался ли оптимизатор поиска
            source: Источник запроса (mcp, cli, api)
            **kwargs: Дополнительные поля для логирования
        """
        ...

    def get_logs(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        vault_name: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Получить логи поисковых запросов за период.

        Args:
            start_date: Начальная дата (по умолчанию сегодня)
            end_date: Конечная дата (по умолчанию сегодня)
            vault_name: Фильтр по vault'у (опционально)
            limit: Максимальное количество записей (опционально)

        Returns:
            Список записей логов
        """
        ...

    def clear_old_logs(self, days_to_keep: int = 90) -> int:
        """Очистка старых логов.

        Args:
            days_to_keep: Количество дней для хранения логов

        Returns:
            Количество удалённых файлов
        """
        ...


class IPerformanceMonitor(Protocol):
    """Интерфейс для монитора производительности."""

    def measure(self, operation_name: str) -> AbstractAsyncContextManager[None]:
        """Измерение времени выполнения операции (context manager).

        Args:
            operation_name: Имя операции для измерения

        Returns:
            Context manager для измерения времени выполнения

        Examples:
            >>> monitor = PerformanceMonitor()
            >>> async with monitor.measure("search"):
            ...     results = await search(query)
            >>> report = monitor.get_report("search")
        """
        ...

    async def record(self, operation_name: str, duration: float) -> None:
        """Запись времени выполнения операции.

        Args:
            operation_name: Имя операции
            duration: Время выполнения в секундах
        """
        ...

    def get_metrics(self, operation_name: str) -> "OperationMetrics | None":
        """Получение метрик для операции.

        Args:
            operation_name: Имя операции

        Returns:
            Метрики операции или None если операция не найдена
        """
        ...

    def get_report(self, operation_name: str) -> "PerformanceReport | None":
        """Получение отчета о производительности для операции.

        Args:
            operation_name: Имя операции

        Returns:
            Отчет о производительности или None если операция не найдена
        """
        ...

    def get_all_reports(self) -> list["PerformanceReport"]:
        """Получение отчетов для всех операций.

        Returns:
            Список отчетов о производительности
        """
        ...

    def reset(self, operation_name: str | None = None) -> None:
        """Сброс метрик.

        Args:
            operation_name: Имя операции для сброса (None для сброса всех)
        """
        ...

    def get_summary(self) -> dict[str, Any]:
        """Получение сводки по всем операциям.

        Returns:
            Словарь со сводкой метрик
        """
        ...


# ============================================================================
# Интерфейсы для адаптивного поиска v5
# ============================================================================


class IChunkRepository(Protocol):
    """Репозиторий для работы с чанками (низкий уровень).
    
    Отвечает за:
    - CRUD операции с чанками
    - Низкоуровневый поиск (vector, FTS)
    - Не знает о бизнес-логике поиска
    """
    
    async def upsert(
        self,
        vault_name: str,
        chunks: list[Chunk],
    ) -> None:
        """Сохранение/обновление чанков."""
        ...
    
    async def delete_by_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> int:
        """Удаление всех чанков документа. Возвращает количество удалённых."""
        ...
    
    async def get_by_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> list[Chunk]:
        """Получение всех чанков документа, отсортированных по chunk_index."""
        ...
    
    async def vector_search(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 10,
        filter_document_ids: set[str] | None = None,
        where: str | None = None,
    ) -> list[ChunkSearchResult]:
        """Векторный поиск по чанкам.
        
        Args:
            vault_name: Имя vault'а
            query_vector: Вектор запроса
            limit: Максимум результатов
            filter_document_ids: Ограничить поиск этими документами
            where: SQL WHERE условие для дополнительной фильтрации
        """
        ...
    
    async def fts_search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
        filter_document_ids: set[str] | None = None,
        where: str | None = None,
    ) -> list[ChunkSearchResult]:
        """Полнотекстовый поиск по чанкам."""
        ...


class IDocumentRepository(Protocol):
    """Репозиторий для работы с документами (низкий уровень).
    
    Отвечает за:
    - CRUD операции с документами
    - Фильтрация по метаданным
    - Не знает о бизнес-логике поиска
    """
    
    async def get(
        self,
        vault_name: str,
        document_id: str,
    ) -> Document | None:
        """Получение документа по ID."""
        ...
    
    async def get_many(
        self,
        vault_name: str,
        document_ids: set[str],
    ) -> list[Document]:
        """Получение нескольких документов."""
        ...
    
    async def get_many_metadata_only(
        self,
        vault_name: str,
        document_ids: set[str],
    ) -> list[Document]:
        """Получение нескольких документов только с метаданными (без свойств).
        
        Оптимизированный метод для процедурных запросов, где свойства не нужны
        на этапе проверки по названиям.
        
        Args:
            vault_name: Имя vault'а
            document_ids: Множество document_ids для получения
            
        Returns:
            Список документов с метаданными (title, file_path), но без properties
        """
        ...
    
    async def find_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str,
    ) -> set[str]:
        """Поиск document_ids по свойству."""
        ...
    
    async def find_by_tags(
        self,
        vault_name: str,
        tags: list[str],
        match_all: bool = True,
    ) -> set[str]:
        """Поиск document_ids по тегам."""
        ...
    
    async def find_by_date_range(
        self,
        vault_name: str,
        field: str,  # "created_at" | "modified_at"
        after: datetime | None = None,
        before: datetime | None = None,
        after_exclusive: bool = False,  # Если True, используется > вместо >=
        before_exclusive: bool = False,  # Если True, используется < вместо <=
    ) -> set[str]:
        """Поиск document_ids по диапазону дат."""
        ...
    
    async def get_content(
        self,
        vault_name: str,
        document_id: str,
    ) -> str:
        """Получение полного контента документа.
        
        Приоритет: файл напрямую > сборка из чанков.
        """
        ...
    
    async def get_properties(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, Any]:
        """Получение всех свойств документа."""
        ...
    
    async def find_by_filename(
        self,
        vault_name: str,
        filename: str,
        exact_match: bool = True,
    ) -> set[str]:
        """Поиск document_ids по имени файла.
        
        Args:
            vault_name: Имя vault'а
            filename: Имя файла для поиска (может быть с расширением или без)
            exact_match: Если True, ищет точное совпадение, иначе частичное (LIKE)
            
        Returns:
            Множество document_ids документов с указанным именем файла
        """
        ...
    
    async def find_by_keywords_in_name(
        self,
        vault_name: str,
        keywords: set[str],
        procedural_keywords: set[str] | None = None,
        require_all_keywords: bool = False,
        limit: int | None = None,
    ) -> set[str]:
        """Поиск document_ids по ключевым словам в названиях файлов и заголовках.
        
        Оптимизированный метод для процедурных запросов. Использует SQL-запросы
        для предварительной фильтрации документов.
        
        Args:
            vault_name: Имя vault'а
            keywords: Множество ключевых слов для поиска
            procedural_keywords: Опциональное множество процедурных ключевых слов
            require_all_keywords: Если True, требует совпадение всех ключевых слов (AND),
                                 иначе хотя бы одного (OR)
            limit: Опциональное ограничение количества результатов на уровне SQL
            
        Returns:
            Множество document_ids документов, содержащих ключевые слова в названиях
        """
        ...
    
    async def get_all_document_ids(
        self,
        vault_name: str,
    ) -> set[str]:
        """Получение всех document_ids из vault'а.
        
        Используется для оптимизации процедурных запросов.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Множество всех document_ids в vault'е
        """
        ...


class IIntentDetector(Protocol):
    """Детектор намерения поискового запроса."""
    
    def detect(
        self,
        query: str,
        parsed_filters: dict[str, Any],
    ) -> IntentDetectionResult:
        """Определение intent на основе запроса и фильтров.
        
        Args:
            query: Исходный текстовый запрос
            parsed_filters: Извлечённые фильтры (tags, type, dates, etc.)
        """
        ...


class ISearchStrategy(Protocol):
    """Стратегия выполнения поиска."""
    
    @property
    def name(self) -> str:
        """Имя стратегии для логирования."""
        ...
    
    async def search(
        self,
        vault_name: str,
        query: str,
        parsed_filters: dict[str, Any],
        limit: int = 10,
        options: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        """Выполнение поиска согласно стратегии.
        
        Args:
            vault_name: Имя vault'а
            query: Текстовый запрос (может быть пустым)
            parsed_filters: Извлечённые фильтры
            limit: Максимум результатов
            options: Дополнительные опции (include_content, max_content_length, search_type)
        """
        ...


class ISearchService(Protocol):
    """Сервис поиска (главный интерфейс для MCP).
    
    Оркестрирует:
    - Парсинг запроса
    - Определение intent
    - Выбор стратегии
    - Выполнение поиска
    - Агрегацию результатов
    """
    
    async def search(
        self,
        request: SearchRequest,
    ) -> SearchResponse:
        """Выполнение поиска.
        
        Args:
            request: Структурированный запрос
            
        Returns:
            Структурированный ответ с результатами
        """
        ...
    
    async def search_multi_vault(
        self,
        vault_names: list[str],
        request: SearchRequest,
    ) -> SearchResponse:
        """Поиск по нескольким vault'ам."""
        ...
    
    def get_available_strategies(self) -> list[str]:
        """Список доступных стратегий поиска."""
        ...


class IResultFormatter(Protocol):
    """Форматирование результатов для вывода."""
    
    def format_markdown(
        self,
        response: SearchResponse,
    ) -> str:
        """Форматирование в Markdown для агента."""
        ...
    
    def format_json(
        self,
        response: SearchResponse,
    ) -> dict[str, Any]:
        """Форматирование в JSON для структурированного вывода."""
        ...


# ============================================================================
# Extended Query API Interfaces (v6)
# ============================================================================


class IFrontmatterAPI(Protocol):
    """Интерфейс для работы с frontmatter метаданными.
    
    Предоставляет прямой доступ к метаданным документов, включая
    схему данных vault'а и агрегации по свойствам.
    """
    
    async def get_frontmatter(
        self,
        vault_name: str,
        file_path: str,
    ) -> dict[str, Any] | None:
        """Получить frontmatter конкретного файла.
        
        Args:
            vault_name: Имя vault'а
            file_path: Путь к файлу (относительный от корня vault)
        
        Returns:
            Словарь с frontmatter или None, если файл не найден
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_schema(
        self,
        vault_name: str,
        doc_type: str | None = None,
        top_values: int = 20,
    ) -> FrontmatterSchema:
        """Получить схему frontmatter vault'а.
        
        Анализирует все документы (или документы определённого типа)
        и возвращает информацию о всех используемых полях.
        
        Args:
            vault_name: Имя vault'а
            doc_type: Опционально — ограничить типом документа
            top_values: Количество примеров значений для каждого поля
        
        Returns:
            Схема frontmatter с информацией о полях
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def list_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Получить документы по значению свойства.
        
        Если property_value не указан, возвращает все документы с этим полем.
        
        Args:
            vault_name: Имя vault'а
            property_key: Имя свойства (например "status", "role", "project")
            property_value: Значение свойства (если None — все документы с этим полем)
            limit: Максимум результатов
        
        Returns:
            Список документов с запрошенным свойством
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def aggregate_by_property(
        self,
        vault_name: str,
        property_key: str,
        doc_type: str | None = None,
    ) -> PropertyAggregation:
        """Агрегация по свойству — количество документов для каждого значения.
        
        Args:
            vault_name: Имя vault'а
            property_key: Имя свойства для группировки (status, priority, role, etc.)
            doc_type: Опционально — ограничить типом документа
        
        Returns:
            Результат агрегации с распределением значений
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_property_values(
        self,
        vault_name: str,
        property_key: str,
        limit: int = 100,
    ) -> list[tuple[str, int]]:
        """Получить уникальные значения свойства с количеством.
        
        Args:
            vault_name: Имя vault'а
            property_key: Имя свойства
            limit: Максимум результатов
        
        Returns:
            Список кортежей (значение, количество), отсортированных по убыванию количества
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...


# ============================================================================
# Dataview Service Types (v6 Phase 2)
# ============================================================================


@dataclass
class DataviewQuery:
    """Структурированный Dataview запрос."""
    select: list[str]  # Поля или ["*"]
    from_type: str | None = None  # type:X
    from_path: str | None = None  # path:Y
    where: list[WhereCondition] | None = None
    sort_by: str | None = None
    sort_order: str = "desc"  # "asc" | "desc"
    limit: int = 50


@dataclass
class DataviewResult:
    """Результат Dataview запроса."""
    documents: list[dict[str, Any]]  # Документы с запрошенными полями
    total_count: int
    query_time_ms: float
    query_string: str  # Исходный запрос для отладки


class IDataviewService(Protocol):
    """Интерфейс Dataview-подобных запросов."""
    
    async def query(
        self,
        vault_name: str,
        query: DataviewQuery,
    ) -> DataviewResult:
        """Выполнить структурированный запрос.
        
        Args:
            vault_name: Имя vault'а
            query: Структурированный DataviewQuery
        
        Returns:
            Результат запроса с документами и метаданными
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def query_string(
        self,
        vault_name: str,
        query_string: str,
    ) -> DataviewResult:
        """Выполнить запрос из строки SQL-like синтаксиса.
        
        Args:
            vault_name: Имя vault'а
            query_string: SQL-like строка запроса
        
        Returns:
            Результат запроса с документами и метаданными
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    def parse_query(self, query_string: str) -> DataviewQuery:
        """Распарсить строку запроса.
        
        Args:
            query_string: SQL-like строка запроса
        
        Returns:
            Структурированный DataviewQuery
        """
        ...


# ============================================================================
# Ripgrep Service Types (v6 Phase 3)
# ============================================================================


@dataclass
class RipgrepMatch:
    """Результат поиска ripgrep — одно совпадение с контекстом."""
    file_path: str  # Относительный путь от корня vault
    line_number: int  # Номер строки (1-based)
    line_content: str  # Содержимое строки
    match_text: str  # Найденный текст
    match_start: int  # Начало совпадения в строке (0-based)
    match_end: int  # Конец совпадения в строке (0-based)
    context_before: list[str]  # Строки до совпадения
    context_after: list[str]  # Строки после совпадения


@dataclass
class RipgrepResult:
    """Результат ripgrep поиска."""
    matches: list[RipgrepMatch]  # Список совпадений
    total_matches: int  # Общее количество совпадений
    files_searched: int  # Количество проверенных файлов
    search_time_ms: float  # Время поиска в миллисекундах


class IRipgrepService(Protocol):
    """Интерфейс для ripgrep поиска.
    
    Предоставляет прямой текстовый поиск по файлам vault'а без использования индекса.
    Использует ripgrep если установлен, иначе fallback на grep или python.
    """
    
    async def search_text(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск текста в файлах vault'а.
        
        Args:
            vault_path: Путь к vault'у
            query: Текст для поиска
            case_sensitive: Учитывать регистр (default: False)
            whole_word: Искать целые слова (default: False)
            context_lines: Количество строк контекста до/после (default: 2)
            file_pattern: Паттерн файлов для поиска (default: "*.md")
            max_results: Максимум результатов (default: 100)
        
        Returns:
            Результат поиска с совпадениями и метаданными
        """
        ...
    
    async def search_regex(
        self,
        vault_path: str,
        pattern: str,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск по regex паттерну.
        
        Args:
            vault_path: Путь к vault'у
            pattern: Regex паттерн для поиска
            context_lines: Количество строк контекста до/после (default: 2)
            file_pattern: Паттерн файлов для поиска (default: "*.md")
            max_results: Максимум результатов (default: 100)
        
        Returns:
            Результат поиска с совпадениями и метаданными
        """
        ...
    
    async def find_files(
        self,
        vault_path: str,
        name_pattern: str,
        content_contains: str | None = None
    ) -> list[str]:
        """Поиск файлов по имени и/или содержимому.
        
        Args:
            vault_path: Путь к vault'у
            name_pattern: Паттерн имени файла (например, "*.md" или "**/test*.md")
            content_contains: Опционально — текст, который должен содержаться в файле
        
        Returns:
            Список относительных путей к найденным файлам
        """
        ...
    
    def is_ripgrep_available(self) -> bool:
        """Проверка доступности ripgrep.
        
        Returns:
            True если ripgrep доступен, False иначе
        """
        ...


# ============================================================================
# Graph Query Service Types (v6 Phase 4)
# ============================================================================


@dataclass
class ConnectedDocument:
    """Связанный документ через wikilinks."""
    file_path: str  # Путь к документу
    title: str  # Заголовок документа
    direction: str  # "incoming" | "outgoing"
    link_text: str  # Текст ссылки (нормализованный)
    link_context: str | None = None  # Контекст вокруг ссылки (опционально)


@dataclass
class GraphQueryResult:
    """Результат граф-запроса."""
    center_document: str  # Путь к центральному документу
    connected: list[ConnectedDocument]  # Список связанных документов
    depth: int  # Глубина поиска
    total_incoming: int  # Общее количество входящих ссылок
    total_outgoing: int  # Общее количество исходящих ссылок


class IGraphQueryService(Protocol):
    """Интерфейс для граф-запросов по связям между документами."""
    
    async def find_connected(
        self,
        vault_name: str,
        document_path: str,
        direction: str = "both",  # "incoming" | "outgoing" | "both"
        depth: int = 1,
        limit: int = 50
    ) -> GraphQueryResult:
        """Найти связанные документы через wikilinks.
        
        Args:
            vault_name: Имя vault'а
            document_path: Путь к документу (относительный от корня vault)
            direction: Направление связей ("incoming", "outgoing", "both")
            depth: Глубина поиска (1 = прямые связи, 2 = связи связей)
            limit: Максимум результатов
        
        Returns:
            Результат граф-запроса с связанными документами
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def find_orphans(
        self,
        vault_name: str,
        doc_type: str | None = None
    ) -> list[str]:
        """Найти документы без входящих ссылок (orphans).
        
        Args:
            vault_name: Имя vault'а
            doc_type: Опционально — ограничить типом документа
        
        Returns:
            Список путей к orphan документам
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def find_broken_links(
        self,
        vault_name: str
    ) -> list[tuple[str, str]]:
        """Найти битые wikilinks — ссылки на несуществующие документы.
        
        Args:
            vault_name: Имя vault'а
        
        Returns:
            Список кортежей (file_path, broken_link) для каждого битого ссылки
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_backlinks(
        self,
        vault_name: str,
        document_path: str
    ) -> list[ConnectedDocument]:
        """Получить все backlinks (входящие ссылки) для документа.
        
        Args:
            vault_name: Имя vault'а
            document_path: Путь к документу
        
        Returns:
            Список документов, которые ссылаются на указанный документ
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...


# ============================================================================
# Timeline Service Types (v6 Phase 4)
# ============================================================================


class ITimelineService(Protocol):
    """Интерфейс для хронологических запросов."""
    
    async def timeline(
        self,
        vault_name: str,
        doc_type: str | None = None,
        date_field: str = "created",  # "created" | "modified" | кастомное поле
        after: str | None = None,  # ISO дата или "last_week", "last_month"
        before: str | None = None,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Хронологическая лента документов.
        
        Args:
            vault_name: Имя vault'а
            doc_type: Опционально — фильтр по типу документа
            date_field: Поле для сортировки ("created", "modified" или кастомное)
            after: Документы после даты (ISO или "last_week", "last_month")
            before: Документы до даты
            limit: Максимум результатов
        
        Returns:
            Список документов с метаданными, отсортированных по дате
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def recent_changes(
        self,
        vault_name: str,
        days: int = 7,
        doc_type: str | None = None
    ) -> dict[str, Any]:
        """Документы, изменённые за последние N дней.
        
        Разделяет на созданные и изменённые.
        
        Args:
            vault_name: Имя vault'а
            days: Количество дней (default: 7)
            doc_type: Опционально — фильтр по типу документа
        
        Returns:
            Словарь с ключами:
            - "created": список созданных документов
            - "modified": список изменённых документов
            - "total": общее количество
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...


# ============================================================================
# Batch Operations Types (v6 Phase 5)
# ============================================================================


class IBatchOperations(Protocol):
    """Интерфейс для массовых операций над vault'ами."""
    
    async def export_to_csv(
        self,
        vault_name: str,
        output_path: str | None = None,
        doc_type: str | None = None,
        fields: str | None = None,
        where: str | None = None
    ) -> str:
        """Экспорт данных vault'а в CSV файл.
        
        Args:
            vault_name: Имя vault'а
            output_path: Путь для сохранения (если не указан — временный файл)
            doc_type: Опционально — фильтр по типу документа
            fields: Поля через запятую (если не указано — все поля)
            where: Условия фильтрации (SQL-like WHERE clause)
        
        Returns:
            Путь к созданному CSV файлу
        
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
            IOError: При ошибке записи файла
        """
        ...
    
    async def compare_schemas(
        self,
        vault_names: list[str]
    ) -> dict[str, Any]:
        """Сравнить схемы frontmatter нескольких vault'ов.
        
        Показывает общие поля, уникальные поля и различия в значениях.
        
        Args:
            vault_names: Список имён vault'ов для сравнения
        
        Returns:
            Словарь с результатами сравнения:
            - "common_fields": список общих полей
            - "unique_fields": словарь {vault_name: [поля]}
            - "field_differences": словарь {field: {vault_name: пример_значения}}
            - "vault_stats": словарь {vault_name: количество_документов}
        
        Raises:
            VaultNotFoundError: Если хотя бы один vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...


# ============================================================================
# LLM Enrichment Interfaces
# ============================================================================


class ILLMEnrichmentService(Protocol):
    """Интерфейс сервиса LLM-обогащения."""
    
    async def enrich_chunk(
        self,
        chunk: DocumentChunk,
    ) -> ChunkEnrichment:
        """Обогащение одного чанка через LLM.
        
        Args:
            chunk: Чанк для обогащения
            
        Returns:
            Обогащенные данные чанка
            
        Raises:
            OllamaConnectionError: При ошибке подключения к LLM
        """
        ...
    
    async def enrich_chunks_batch(
        self,
        chunks: list[DocumentChunk],
    ) -> list[ChunkEnrichment]:
        """Батчевое обогащение чанков через LLM.
        
        Args:
            chunks: Список чанков для обогащения
            
        Returns:
            Список обогащенных данных
            
        Raises:
            OllamaConnectionError: При ошибке подключения к LLM
        """
        ...
    
    async def health_check(self) -> bool:
        """Проверка доступности LLM.
        
        Returns:
            True если LLM доступен, False иначе
        """
        ...


class IKnowledgeClusterService(Protocol):
    """Интерфейс сервиса кластеризации знаний."""
    
    async def cluster_documents(
        self,
        vault_name: str,
        n_clusters: int | None = None,
        method: str = "kmeans",
    ) -> list[KnowledgeCluster]:
        """Кластеризация документов vault'а.
        
        Args:
            vault_name: Имя vault'а
            n_clusters: Количество кластеров (None для автоматического определения)
            method: Метод кластеризации ("kmeans" | "dbscan")
            
        Returns:
            Список кластеров знаний
            
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def update_clusters(
        self,
        vault_name: str,
    ) -> list[KnowledgeCluster]:
        """Обновление кластеров после изменений в vault'е.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Обновленный список кластеров
            
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_cluster_for_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> KnowledgeCluster | None:
        """Получение кластера для документа.
        
        Args:
            vault_name: Имя vault'а
            document_id: ID документа
            
        Returns:
            Кластер документа или None если не найден
            
        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        ...


class IChunkEnrichmentRepository(Protocol):
    """Интерфейс репозитория обогащенных данных чанков."""
    
    async def upsert(
        self,
        vault_name: str,
        enrichments: list[ChunkEnrichment],
    ) -> None:
        """Сохранение обогащенных данных.
        
        Args:
            vault_name: Имя vault'а
            enrichments: Список обогащенных данных
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get(
        self,
        vault_name: str,
        chunk_id: str,
    ) -> ChunkEnrichment | None:
        """Получение обогащения для чанка.
        
        Args:
            vault_name: Имя vault'а
            chunk_id: ID чанка
            
        Returns:
            Обогащение чанка или None если не найдено
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_many(
        self,
        vault_name: str,
        chunk_ids: list[str],
    ) -> dict[str, ChunkEnrichment]:
        """Получение обогащений для нескольких чанков.
        
        Args:
            vault_name: Имя vault'а
            chunk_ids: Список ID чанков
            
        Returns:
            Словарь {chunk_id: ChunkEnrichment}
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def delete_by_chunk(
        self,
        vault_name: str,
        chunk_id: str,
    ) -> None:
        """Удаление обогащения для чанка.
        
        Args:
            vault_name: Имя vault'а
            chunk_id: ID чанка
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def delete_by_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> None:
        """Удаление всех обогащений документа.
        
        Args:
            vault_name: Имя vault'а
            document_id: ID документа
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
    ) -> list[ChunkEnrichment]:
        """Поиск по обогащенным данным (summary, key_concepts).
        
        Args:
            vault_name: Имя vault'а
            query: Поисковый запрос
            limit: Максимум результатов
            
        Returns:
            Список найденных обогащений
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...


class IKnowledgeClusterRepository(Protocol):
    """Интерфейс репозитория кластеров знаний."""
    
    async def upsert(
        self,
        vault_name: str,
        clusters: list[KnowledgeCluster],
    ) -> None:
        """Сохранение кластеров.
        
        Args:
            vault_name: Имя vault'а
            clusters: Список кластеров
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_all(
        self,
        vault_name: str,
    ) -> list[KnowledgeCluster]:
        """Получение всех кластеров vault'а.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Список всех кластеров
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get(
        self,
        vault_name: str,
        cluster_id: str,
    ) -> KnowledgeCluster | None:
        """Получение кластера по ID.
        
        Args:
            vault_name: Имя vault'а
            cluster_id: ID кластера
            
        Returns:
            Кластер или None если не найден
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def get_for_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> KnowledgeCluster | None:
        """Получение кластера для документа.
        
        Args:
            vault_name: Имя vault'а
            document_id: ID документа
            
        Returns:
            Кластер документа или None если не найден
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...
    
    async def search_similar(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[KnowledgeCluster]:
        """Поиск похожих кластеров по вектору.
        
        Args:
            vault_name: Имя vault'а
            query_vector: Вектор запроса
            limit: Максимум результатов
            
        Returns:
            Список похожих кластеров
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        ...

