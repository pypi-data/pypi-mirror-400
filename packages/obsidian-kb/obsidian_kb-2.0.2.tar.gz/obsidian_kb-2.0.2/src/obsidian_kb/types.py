"""Типы данных для obsidian-kb."""

import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


@dataclass
class DocumentChunk:
    """Чанк документа для индексирования (v4).
    
    Примечание: В v4 удалены денормализованные поля (author, status, priority, project).
    Все свойства теперь извлекаются из metadata и сохраняются в таблицу document_properties.
    """

    id: str  # vault_name::filepath::chunk_index
    vault_name: str
    file_path: str
    title: str  # Из frontmatter или H1
    section: str  # Заголовок секции
    content: str  # Текст чанка
    tags: list[str]  # Теги из frontmatter + inline (для обратной совместимости)
    frontmatter_tags: list[str]  # Теги из frontmatter (tags: [tag])
    inline_tags: list[str]  # Inline теги из текста (#tag)
    links: list[str]  # Wikilinks (связанные заметки) [[link]]
    created_at: datetime | None
    modified_at: datetime
    metadata: dict  # Весь frontmatter (для извлечения свойств)
    # УДАЛЕНЫ денормализованные поля: author, status, priority, project (v3)


@dataclass
class SearchResult:
    """Результат поиска."""

    chunk_id: str
    vault_name: str
    file_path: str
    title: str
    section: str
    content: str
    tags: list[str]
    score: float  # Релевантность (0.0 - 1.0)
    created_at: datetime | None
    modified_at: datetime


@dataclass
class VaultStats:
    """Статистика vault'а."""

    vault_name: str
    file_count: int
    chunk_count: int
    total_size_bytes: int
    tags: list[str]
    oldest_file: datetime | None
    newest_file: datetime | None


@dataclass
class DocumentInfo:
    """Метаданные документа из таблицы documents (v4)."""

    document_id: str  # {vault_name}::{file_path}
    vault_name: str
    file_path: str  # Относительный путь к файлу
    file_path_full: str  # Полный абсолютный путь
    file_name: str  # Имя файла (без пути)
    file_extension: str  # Расширение файла (.md, .pdf)
    content_type: str  # Тип контента (markdown, pdf, image)
    title: str  # Заголовок документа
    created_at: datetime  # Дата создания файла
    modified_at: datetime  # Дата последнего изменения
    file_size: int  # Размер файла в байтах
    chunk_count: int  # Количество чанков документа


@dataclass
class DocumentProperty:
    """Свойство документа из таблицы document_properties (v4)."""

    property_id: str  # {document_id}::{property_key}
    document_id: str  # FK на documents.document_id
    vault_name: str
    property_key: str  # Ключ свойства (type, author, team, status, etc.)
    property_value: str  # Значение свойства (нормализованное)
    property_value_raw: str  # Оригинальное значение (для fuzzy matching)
    property_type: str  # Тип значения (string, number, date, array)


# Исключения
class ObsidianKBError(Exception):
    """Базовый класс ошибок obsidian-kb."""
    
    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Инициализация ошибки с контекстом.
        
        Args:
            message: Сообщение об ошибке
            context: Дополнительный контекст для отладки
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self) -> str:
        """Строковое представление ошибки с контекстом."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class VaultNotFoundError(ObsidianKBError):
    """Vault не найден или не проиндексирован."""
    
    def __init__(self, vault_name: str, context: dict[str, Any] | None = None) -> None:
        """Инициализация ошибки vault не найден.
        
        Args:
            vault_name: Имя vault'а
            context: Дополнительный контекст
        """
        message = f"Vault '{vault_name}' не найден или не проиндексирован"
        full_context = {"vault_name": vault_name}
        if context:
            full_context.update(context)
        super().__init__(message, full_context)
        self.vault_name = vault_name


class OllamaConnectionError(ObsidianKBError):
    """Ollama недоступна.

    DEPRECATED: Используйте ProviderConnectionError из providers/exceptions.py.
    Этот класс будет удалён в v2.0.0.
    """

    def __init__(self, message: str = "Ollama недоступна", url: str | None = None, context: dict[str, Any] | None = None) -> None:
        """Инициализация ошибки подключения к Ollama.

        Args:
            message: Сообщение об ошибке
            url: URL Ollama сервера
            context: Дополнительный контекст

        .. deprecated::
            Используйте :class:`~obsidian_kb.providers.exceptions.ProviderConnectionError`.
        """
        warnings.warn(
            "OllamaConnectionError is deprecated. Use ProviderConnectionError from "
            "obsidian_kb.providers.exceptions instead. Will be removed in v2.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        full_context = {}
        if url:
            full_context["ollama_url"] = url
        if context:
            full_context.update(context)
        super().__init__(message, full_context)
        self.url = url


class IndexingError(ObsidianKBError):
    """Ошибка при индексировании."""
    
    def __init__(self, message: str, vault_name: str | None = None, file_path: str | None = None, context: dict[str, Any] | None = None) -> None:
        """Инициализация ошибки индексирования.
        
        Args:
            message: Сообщение об ошибке
            vault_name: Имя vault'а
            file_path: Путь к файлу (если ошибка связана с конкретным файлом)
            context: Дополнительный контекст
        """
        full_context = {}
        if vault_name:
            full_context["vault_name"] = vault_name
        if file_path:
            full_context["file_path"] = file_path
        if context:
            full_context.update(context)
        super().__init__(message, full_context)
        self.vault_name = vault_name
        self.file_path = file_path


class DatabaseError(ObsidianKBError):
    """Ошибка работы с базой данных."""

    def __init__(self, message: str, operation: str | None = None, vault_name: str | None = None, context: dict[str, Any] | None = None) -> None:
        """Инициализация ошибки БД.

        Args:
            message: Сообщение об ошибке
            operation: Операция, которая вызвала ошибку
            vault_name: Имя vault'а (если применимо)
            context: Дополнительный контекст
        """
        full_context = {}
        if operation:
            full_context["operation"] = operation
        if vault_name:
            full_context["vault_name"] = vault_name
        if context:
            full_context.update(context)
        super().__init__(message, full_context)
        self.operation = operation
        self.vault_name = vault_name


# ============================================================================
# MCP Tool Exceptions (v0.6.0)
# ============================================================================


class MCPToolError(ObsidianKBError):
    """Базовый класс ошибок MCP инструментов.

    Иерархия исключений для MCP tools позволяет:
    - Унифицировать обработку ошибок в MCP сервере
    - Формировать информативные сообщения для Claude
    - Логировать с правильным контекстом
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        user_message: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки MCP инструмента.

        Args:
            message: Техническое сообщение для логов
            tool_name: Имя MCP инструмента (search_vault, index_vault, etc.)
            user_message: Понятное сообщение для пользователя/Claude (если отличается)
            context: Дополнительный контекст
        """
        full_context = {"tool_name": tool_name}
        if context:
            full_context.update(context)
        super().__init__(message, full_context)
        self.tool_name = tool_name
        self.user_message = user_message or message

    def to_user_response(self) -> str:
        """Формирование ответа для пользователя/Claude.

        Returns:
            Человекочитаемое сообщение об ошибке
        """
        return f"Error in {self.tool_name}: {self.user_message}"


class MCPValidationError(MCPToolError):
    """Ошибка валидации параметров MCP инструмента.

    Возникает при некорректных входных параметрах.
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        param_name: str,
        param_value: Any = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки валидации.

        Args:
            message: Сообщение об ошибке
            tool_name: Имя MCP инструмента
            param_name: Имя некорректного параметра
            param_value: Значение параметра (если безопасно логировать)
            context: Дополнительный контекст
        """
        full_context = {"param_name": param_name}
        if param_value is not None:
            full_context["param_value"] = param_value
        if context:
            full_context.update(context)

        user_message = f"Invalid parameter '{param_name}': {message}"
        super().__init__(message, tool_name, user_message, full_context)
        self.param_name = param_name
        self.param_value = param_value


class MCPVaultError(MCPToolError):
    """Ошибка связанная с vault в MCP инструменте.

    Vault не найден, не проиндексирован, или недоступен.
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        vault_name: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки vault.

        Args:
            message: Сообщение об ошибке
            tool_name: Имя MCP инструмента
            vault_name: Имя vault'а
            context: Дополнительный контекст
        """
        full_context = {"vault_name": vault_name}
        if context:
            full_context.update(context)

        user_message = f"Vault '{vault_name}' error: {message}"
        super().__init__(message, tool_name, user_message, full_context)
        self.vault_name = vault_name


class MCPSearchError(MCPToolError):
    """Ошибка поиска в MCP инструменте.

    Возникает при ошибках векторного, текстового или гибридного поиска.
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        query: str | None = None,
        search_type: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки поиска.

        Args:
            message: Сообщение об ошибке
            tool_name: Имя MCP инструмента
            query: Поисковый запрос (если безопасно логировать)
            search_type: Тип поиска (vector, fts, hybrid)
            context: Дополнительный контекст
        """
        full_context = {}
        if query:
            full_context["query"] = query
        if search_type:
            full_context["search_type"] = search_type
        if context:
            full_context.update(context)

        super().__init__(message, tool_name, context=full_context)
        self.query = query
        self.search_type = search_type


class MCPTimeoutError(MCPToolError):
    """Ошибка таймаута в MCP инструменте.

    Операция превысила допустимое время выполнения.
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        timeout_seconds: float,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки таймаута.

        Args:
            message: Сообщение об ошибке
            tool_name: Имя MCP инструмента
            timeout_seconds: Значение таймаута в секундах
            context: Дополнительный контекст
        """
        full_context = {"timeout_seconds": timeout_seconds}
        if context:
            full_context.update(context)

        user_message = f"Operation timed out after {timeout_seconds}s: {message}"
        super().__init__(message, tool_name, user_message, full_context)
        self.timeout_seconds = timeout_seconds


class MCPRateLimitError(MCPToolError):
    """Ошибка превышения rate limit в MCP инструменте."""

    def __init__(
        self,
        tool_name: str,
        retry_after_seconds: float | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки rate limit.

        Args:
            tool_name: Имя MCP инструмента
            retry_after_seconds: Через сколько секунд можно повторить
            context: Дополнительный контекст
        """
        message = "Rate limit exceeded"
        full_context = {}
        if retry_after_seconds:
            full_context["retry_after_seconds"] = retry_after_seconds
            user_message = f"Rate limit exceeded. Retry after {retry_after_seconds}s"
        else:
            user_message = "Rate limit exceeded. Please try again later"
        if context:
            full_context.update(context)

        super().__init__(message, tool_name, user_message, full_context)
        self.retry_after_seconds = retry_after_seconds


class MCPServiceUnavailableError(MCPToolError):
    """Ошибка недоступности сервиса (Ollama, LanceDB, etc.)."""

    def __init__(
        self,
        message: str,
        tool_name: str,
        service_name: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Инициализация ошибки недоступности сервиса.

        Args:
            message: Сообщение об ошибке
            tool_name: Имя MCP инструмента
            service_name: Имя недоступного сервиса
            context: Дополнительный контекст
        """
        full_context = {"service_name": service_name}
        if context:
            full_context.update(context)

        user_message = f"Service '{service_name}' is unavailable: {message}"
        super().__init__(message, tool_name, user_message, full_context)
        self.service_name = service_name


# Типы для диагностики
class HealthStatus(Enum):
    """Статус здоровья компонента."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class HealthCheck:
    """Результат проверки одного компонента."""

    component: str
    status: HealthStatus
    message: str
    details: dict | None = None


@dataclass
class SystemHealth:
    """Общее состояние системы."""

    overall: HealthStatus
    checks: list[HealthCheck]
    timestamp: datetime


# ============================================================================
# Типы данных для адаптивного поиска v5
# ============================================================================


class SearchIntent(Enum):
    """Намерение поискового запроса."""

    METADATA_FILTER = "metadata_filter"  # tags:x type:y без текста
    KNOWN_ITEM = "known_item"  # Конкретный документ по имени
    SEMANTIC = "semantic"  # Поиск по смыслу
    EXPLORATORY = "exploratory"  # Исследовательский вопрос
    PROCEDURAL = "procedural"  # How-to запрос


class RetrievalGranularity(Enum):
    """Гранулярность результатов."""

    DOCUMENT = "document"  # Полный документ
    CHUNK = "chunk"  # Отдельные чанки
    AUTO = "auto"  # Автоматический выбор


class MatchType(Enum):
    """Тип совпадения."""

    EXACT_METADATA = "exact_metadata"  # Точное совпадение фильтров
    SEMANTIC = "semantic"  # Семантическое сходство
    KEYWORD = "keyword"  # Ключевые слова (FTS)
    HYBRID = "hybrid"  # Комбинация


@dataclass
class RelevanceScore:
    """Структурированная оценка релевантности."""

    value: float  # 0.0 - 1.0
    match_type: MatchType
    confidence: float = 1.0  # Уверенность в оценке
    components: dict[str, float] = field(default_factory=dict)  # vector: 0.8, fts: 0.6

    @property
    def label(self) -> str:
        """Человекочитаемая метка."""
        if self.value >= 0.9:
            return "высокая"
        elif self.value >= 0.7:
            return "средняя"
        elif self.value >= 0.5:
            return "низкая"
        return "минимальная"

    @classmethod
    def exact_match(cls) -> "RelevanceScore":
        """Создание score для точного совпадения метаданных."""
        return cls(
            value=1.0,
            match_type=MatchType.EXACT_METADATA,
            confidence=1.0,
        )

    @classmethod
    def from_distance(cls, distance: float, match_type: MatchType = MatchType.SEMANTIC) -> "RelevanceScore":
        """Создание score из расстояния (distance -> similarity).
        
        Args:
            distance: Расстояние (чем меньше, тем лучше)
            match_type: Тип совпадения
        """
        # Конвертация distance в similarity (1 - distance, но с нормализацией)
        similarity = max(0.0, min(1.0, 1.0 - distance))
        return cls(
            value=similarity,
            match_type=match_type,
            confidence=1.0,
        )


@dataclass
class Chunk:
    """Чанк документа (единица индексации) - Storage Layer."""

    chunk_id: str  # vault::file::index
    document_id: str  # vault::file
    vault_name: str
    chunk_index: int
    section: str
    content: str
    vector: list[float] | None = None

    # Метаданные чанка (для фильтрации)
    inline_tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)


@dataclass
class ChunkSearchResult:
    """Результат поиска на уровне чанка (внутренний тип)."""

    chunk: Chunk
    score: RelevanceScore

    def to_legacy(self) -> SearchResult:
        """Конвертация в legacy SearchResult для обратной совместимости."""
        return SearchResult(
            chunk_id=self.chunk.chunk_id,
            vault_name=self.chunk.vault_name,
            file_path=self.chunk.document_id.split("::", 1)[1] if "::" in self.chunk.document_id else "",
            title="",  # Нужно будет получить из документа
            section=self.chunk.section,
            content=self.chunk.content,
            tags=self.chunk.inline_tags,
            score=self.score.value,
            created_at=None,  # Нужно будет получить из документа
            modified_at=datetime.now(),  # Нужно будет получить из документа
        )


@dataclass
class Document:
    """Документ (единица контента для агента) - Search Layer."""

    document_id: str  # vault::file
    vault_name: str
    file_path: str
    title: str

    # Контент (опционально, для progressive disclosure)
    content: str | None = None
    summary: str | None = None

    # Метаданные
    tags: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)

    # Временные метки
    created_at: datetime | None = None
    modified_at: datetime | None = None

    # Статистика
    chunk_count: int = 0
    content_length: int = 0

    @classmethod
    def from_document_info(cls, doc_info: DocumentInfo, properties: dict[str, Any] | None = None) -> "Document":
        """Создание Document из DocumentInfo."""
        return cls(
            document_id=doc_info.document_id,
            vault_name=doc_info.vault_name,
            file_path=doc_info.file_path,
            title=doc_info.title,
            created_at=doc_info.created_at,
            modified_at=doc_info.modified_at,
            chunk_count=doc_info.chunk_count,
            content_length=doc_info.file_size,
            properties=properties or {},
        )


@dataclass
class DocumentSearchResult:
    """Результат поиска на уровне документа (для агента)."""

    document: Document
    score: RelevanceScore

    # Контекст совпадений (для chunk-level поиска)
    matched_chunks: list[ChunkSearchResult] = field(default_factory=list)
    matched_sections: list[str] = field(default_factory=list)

    @property
    def best_chunk(self) -> ChunkSearchResult | None:
        """Лучший совпавший чанк."""
        if not self.matched_chunks:
            return None
        return max(self.matched_chunks, key=lambda c: c.score.value)

    @property
    def snippet(self) -> str:
        """Snippet из лучшего чанка для отображения."""
        if self.best_chunk:
            content = self.best_chunk.chunk.content
            # Обрезаем до 200 символов
            if len(content) > 200:
                return content[:197] + "..."
            return content
        if self.document.content:
            if len(self.document.content) > 200:
                return self.document.content[:197] + "..."
            return self.document.content
        return ""


@dataclass
class SearchRequest:
    """Запрос на поиск (входные данные для ISearchService)."""

    vault_name: str
    query: str

    # Опции поиска
    limit: int = 10
    search_type: str = "hybrid"  # vector | fts | hybrid

    # Уровень детализации
    granularity: RetrievalGranularity = RetrievalGranularity.AUTO
    include_content: bool = True
    max_content_length: int = 10000

    # Переопределение intent (опционально)
    force_intent: SearchIntent | None = None


@dataclass
class IntentDetectionResult:
    """Результат определения intent."""

    intent: SearchIntent
    confidence: float
    signals: dict[str, Any] = field(default_factory=dict)
    recommended_granularity: RetrievalGranularity = RetrievalGranularity.AUTO


@dataclass
class SearchResponse:
    """Ответ поиска (выход ISearchService)."""

    # Метаданные запроса
    request: SearchRequest
    detected_intent: SearchIntent
    intent_confidence: float

    # Результаты
    results: list[DocumentSearchResult]

    # Агрегация
    total_found: int
    execution_time_ms: float

    # Пагинация
    has_more: bool = False
    next_cursor: str | None = None

    # Диагностика
    strategy_used: str = ""  # "document_level" | "chunk_level"
    filters_applied: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Extended Query API Types (v6)
# ============================================================================


@dataclass
class FieldInfo:
    """Информация о поле frontmatter."""
    
    field_name: str
    field_type: str  # "string" | "list" | "date" | "number" | "boolean"
    unique_values: list[str]  # Топ-N уникальных значений
    unique_count: int  # Общее количество уникальных значений
    document_count: int  # Сколько документов имеют это поле
    nullable_count: int  # Сколько документов имеют пустое значение
    example_documents: list[str]  # Примеры document_id с этим полем


@dataclass
class FrontmatterSchema:
    """Схема frontmatter vault'а."""
    
    vault_name: str
    total_documents: int
    doc_type_filter: str | None  # Если схема для конкретного типа
    fields: dict[str, FieldInfo]
    common_patterns: list[str]  # Часто встречающиеся комбинации полей


@dataclass
class PropertyAggregation:
    """Результат агрегации по свойству."""
    
    property_key: str
    total_documents: int  # Всего документов с этим свойством
    values: dict[str, int]  # Значение → количество
    null_count: int  # Документы без значения


# ============================================================================
# LLM Enrichment Types
# ============================================================================


@dataclass
class ChunkEnrichment:
    """Обогащенные данные чанка через LLM."""
    
    chunk_id: str  # Primary key: vault_name::file_path::chunk_index
    vault_name: str
    summary: str  # Краткое резюме (1-2 предложения)
    key_concepts: list[str]  # Ключевые понятия (3-5)
    semantic_tags: list[str]  # Семантические теги (3-5)
    enriched_at: datetime
    content_hash: str  # SHA256 hash контента для кэширования


@dataclass
class KnowledgeCluster:
    """Кластер знаний - группа связанных документов."""
    
    cluster_id: str  # Primary key: vault_name::cluster_{index}
    vault_name: str
    cluster_name: str  # LLM-генерированное название
    description: str  # Описание кластера (LLM)
    document_ids: list[str]  # Документы в кластере
    keywords: list[str]  # Ключевые слова кластера
    created_at: datetime
    updated_at: datetime
    centroid_vector: list[float] | None = None  # Центроид кластера (опционально)

