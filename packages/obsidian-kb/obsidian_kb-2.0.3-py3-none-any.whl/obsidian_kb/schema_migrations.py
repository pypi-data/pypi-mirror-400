"""Модуль для управления схемой базы данных."""

import pyarrow as pa


def get_base_schema(embedding_dimensions: int) -> pa.Schema:
    """Получение базовой схемы таблицы (v3).
    
    Args:
        embedding_dimensions: Размерность векторов
        
    Returns:
        Схема таблицы v3
    """
    return pa.schema([
        pa.field("id", pa.string()),
        pa.field("vault_name", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("title", pa.string()),
        pa.field("section", pa.string()),
        pa.field("content", pa.string()),
        pa.field("tags", pa.list_(pa.string())),  # Объединенные теги для обратной совместимости
        pa.field("frontmatter_tags", pa.list_(pa.string())),  # Теги из frontmatter
        pa.field("inline_tags", pa.list_(pa.string())),  # Inline теги из текста
        pa.field("links", pa.list_(pa.string())),
        pa.field("created_at", pa.string()),
        pa.field("modified_at", pa.string()),
        pa.field("metadata_json", pa.string()),
        pa.field("doc_type", pa.string()),  # Тип документа
        # Денормализованные поля из metadata (v3)
        pa.field("author", pa.string()),  # Автор документа
        pa.field("status", pa.string()),  # Статус (draft, published, archived)
        pa.field("priority", pa.string()),  # Приоритет (low, medium, high)
        pa.field("project", pa.string()),  # Проект/категория
        pa.field("vector", pa.list_(pa.float32(), embedding_dimensions)),
    ])


# ============================================================================
# Схемы для нормализованной схемы v4
# ============================================================================


def get_documents_schema() -> pa.Schema:
    """Получение схемы таблицы documents (v4 + Phase 3).
    
    Таблица хранит метаданные файлов/документов.
    
    Phase 3 добавления:
    - summary_vector: Векторное представление summary документа
    - summary_text: Текстовый summary документа (250-300 токенов)
    - enrichment_status: Статус обогащения (none | partial | complete)
    - provider_info: Информация о провайдере (JSON)
    
    Returns:
        Схема таблицы documents
    """
    return pa.schema([
        pa.field("document_id", pa.string()),  # Primary Key: {vault_name}::{file_path}
        pa.field("vault_name", pa.string()),
        pa.field("file_path", pa.string()),  # Относительный путь к файлу
        pa.field("file_path_full", pa.string()),  # Полный абсолютный путь
        pa.field("file_name", pa.string()),  # Имя файла (без пути)
        pa.field("file_extension", pa.string()),  # Расширение файла (.md, .pdf)
        pa.field("content_type", pa.string()),  # Тип контента (markdown, pdf, image)
        pa.field("title", pa.string()),  # Заголовок документа (frontmatter или H1)
        pa.field("created_at", pa.string()),  # Дата создания файла (ISO)
        pa.field("modified_at", pa.string()),  # Дата последнего изменения (ISO)
        pa.field("file_size", pa.int64()),  # Размер файла в байтах
        pa.field("chunk_count", pa.int32()),  # Количество чанков документа
        pa.field("content_hash", pa.string()),  # SHA256 hash контента для отслеживания изменений
        # Phase 3: Hybrid Indexing Pipeline
        # Примечание: summary_vector будет добавлен динамически при создании таблицы
        # так как требует embedding_dimensions
        pa.field("summary_text", pa.string()),  # Текстовый summary документа
        pa.field("enrichment_status", pa.string()),  # none | partial | complete
        pa.field("provider_info", pa.string()),  # JSON: {provider, model, timestamp}
    ])


def get_chunks_schema(embedding_dimensions: int) -> pa.Schema:
    """Получение схемы таблицы chunks (v4 + Phase 3).
    
    Таблица хранит векторизованное содержимое документов.
    
    Phase 3 добавления:
    - context_prefix: Contextual Retrieval prefix для улучшения поиска
    - provider_info: Информация о провайдере (JSON)
    
    Args:
        embedding_dimensions: Размерность векторов
        
    Returns:
        Схема таблицы chunks
    """
    return pa.schema([
        pa.field("chunk_id", pa.string()),  # Primary Key: {document_id}::{chunk_index}
        pa.field("document_id", pa.string()),  # FK на documents.document_id
        pa.field("vault_name", pa.string()),
        pa.field("chunk_index", pa.int32()),  # Порядковый номер чанка в документе
        pa.field("section", pa.string()),  # Заголовок секции (H1-H3)
        pa.field("content", pa.string()),  # Текст чанка (размер зависит от chunk_size в настройках)
        pa.field("vector", pa.list_(pa.float32(), embedding_dimensions)),  # Векторное представление
        pa.field("links", pa.list_(pa.string())),  # Wikilinks из чанка [[note]]
        pa.field("inline_tags", pa.list_(pa.string())),  # Inline теги #tag из текста
        # Phase 3: Hybrid Indexing Pipeline
        pa.field("context_prefix", pa.string()),  # Contextual Retrieval prefix (80-100 токенов)
        pa.field("provider_info", pa.string()),  # JSON: {provider, model, timestamp}
    ])


def get_properties_schema() -> pa.Schema:
    """Получение схемы таблицы document_properties (v4).
    
    Таблица хранит произвольные свойства из frontmatter в формате key-value.
    
    Returns:
        Схема таблицы document_properties
    """
    return pa.schema([
        pa.field("property_id", pa.string()),  # Primary Key: {document_id}::{property_key}
        pa.field("document_id", pa.string()),  # FK на documents.document_id
        pa.field("vault_name", pa.string()),
        pa.field("property_key", pa.string()),  # Ключ свойства (type, author, team, status, etc.)
        pa.field("property_value", pa.string()),  # Значение свойства (нормализованное)
        pa.field("property_value_raw", pa.string()),  # Оригинальное значение (для fuzzy matching)
        pa.field("property_type", pa.string()),  # Тип значения (string, number, date, array)
    ])


def get_metadata_schema() -> pa.Schema:
    """Получение схемы таблицы metadata (v4).
    
    Таблица хранит полный frontmatter в JSON формате для расширенных запросов.
    
    Returns:
        Схема таблицы metadata
    """
    return pa.schema([
        pa.field("document_id", pa.string()),  # Primary Key: FK на documents.document_id
        pa.field("vault_name", pa.string()),
        pa.field("metadata_json", pa.string()),  # Полный frontmatter в JSON
        pa.field("frontmatter_tags", pa.list_(pa.string())),  # Теги из frontmatter (денормализовано)
        pa.field("metadata_hash", pa.string()),  # SHA256 хеш metadata для отслеживания изменений
    ])


def get_documents_schema_with_summary_vector(embedding_dimensions: int) -> pa.Schema:
    """Получение схемы таблицы documents с summary_vector (Phase 3).
    
    Args:
        embedding_dimensions: Размерность векторов для summary_vector
        
    Returns:
        Схема таблицы documents с summary_vector
    """
    base_schema = get_documents_schema()
    # Добавляем summary_vector поле
    fields = list(base_schema)
    # Вставляем summary_vector после chunk_count
    chunk_count_idx = next(i for i, f in enumerate(fields) if f.name == "chunk_count")
    fields.insert(
        chunk_count_idx + 1,
        pa.field("summary_vector", pa.list_(pa.float32(), embedding_dimensions), nullable=True),
    )
    return pa.schema(fields)


def get_schema_for_table_type(table_type: str, embedding_dimensions: int) -> pa.Schema:
    """Получение схемы для типа таблицы (v4 + LLM Enrichment + Phase 3).
    
    Args:
        table_type: Тип таблицы (documents, chunks, document_properties, metadata, chunk_enrichments, knowledge_clusters)
        embedding_dimensions: Размерность векторов (требуется для chunks и knowledge_clusters)
        
    Returns:
        Схема таблицы
        
    Raises:
        ValueError: Если указан неизвестный тип таблицы
    """
    if table_type == "documents":
        return get_documents_schema_with_summary_vector(embedding_dimensions)
    elif table_type == "chunks":
        return get_chunks_schema(embedding_dimensions)
    elif table_type == "document_properties":
        return get_properties_schema()
    elif table_type == "metadata":
        return get_metadata_schema()
    elif table_type == "chunk_enrichments":
        return get_chunk_enrichments_schema()
    elif table_type == "knowledge_clusters":
        return get_knowledge_clusters_schema(embedding_dimensions)
    else:
        raise ValueError(
            f"Unknown table type: {table_type}. "
            f"Must be one of: documents, chunks, document_properties, metadata, chunk_enrichments, knowledge_clusters"
        )


def get_v4_schemas(embedding_dimensions: int) -> dict[str, pa.Schema]:
    """Получение всех схем таблиц v4 для vault'а.
    
    Args:
        embedding_dimensions: Размерность векторов
        
    Returns:
        Словарь {table_type: schema} со всеми схемами v4
    """
    return {
        "documents": get_documents_schema(),
        "chunks": get_chunks_schema(embedding_dimensions),
        "document_properties": get_properties_schema(),
        "metadata": get_metadata_schema(),
    }


# ============================================================================
# LLM Enrichment Schemas
# ============================================================================


def get_chunk_enrichments_schema() -> pa.Schema:
    """Получение схемы таблицы chunk_enrichments.
    
    Таблица хранит обогащенные данные чанков через LLM.
    
    Returns:
        Схема таблицы chunk_enrichments
    """
    return pa.schema([
        pa.field("chunk_id", pa.string()),  # Primary Key: vault_name::file_path::chunk_index
        pa.field("vault_name", pa.string()),
        pa.field("summary", pa.string()),  # Краткое резюме (1-2 предложения)
        pa.field("key_concepts", pa.list_(pa.string())),  # Ключевые понятия (3-5)
        pa.field("semantic_tags", pa.list_(pa.string())),  # Семантические теги (3-5)
        pa.field("enriched_at", pa.string()),  # ISO datetime
        pa.field("content_hash", pa.string()),  # SHA256 hash контента для кэширования
    ])


def get_knowledge_clusters_schema(embedding_dimensions: int) -> pa.Schema:
    """Получение схемы таблицы knowledge_clusters.
    
    Таблица хранит кластеры знаний - группы связанных документов.
    
    Args:
        embedding_dimensions: Размерность векторов (для centroid_vector)
        
    Returns:
        Схема таблицы knowledge_clusters
    """
    return pa.schema([
        pa.field("cluster_id", pa.string()),  # Primary Key: vault_name::cluster_{index}
        pa.field("vault_name", pa.string()),
        pa.field("cluster_name", pa.string()),  # LLM-генерированное название
        pa.field("description", pa.string()),  # Описание кластера (LLM)
        pa.field("document_ids", pa.list_(pa.string())),  # Документы в кластере
        pa.field("keywords", pa.list_(pa.string())),  # Ключевые слова кластера
        pa.field("centroid_vector", pa.list_(pa.float32(), embedding_dimensions), nullable=True),  # Центроид кластера (опционально)
        pa.field("created_at", pa.string()),  # ISO datetime
        pa.field("updated_at", pa.string()),  # ISO datetime
    ])

