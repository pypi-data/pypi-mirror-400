"""Конфигурация obsidian-kb через Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения obsidian-kb."""

    # Paths
    db_path: Path = Path.home() / ".obsidian-kb" / "lancedb"
    vaults_config: Path = Path.home() / ".obsidian-kb" / "vaults.json"

    # === Provider Selection (v6) ===
    embedding_provider: str = "ollama"  # ollama | yandex
    chat_provider: str = "ollama"  # ollama | yandex
    
    # === Ollama (default) ===
    ollama_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = 768
    embedding_timeout: int = 10  # Таймаут для получения embeddings (в секундах). Оптимизировано для быстрого поиска
    ollama_max_concurrent: int = 10  # Максимальное количество одновременных запросов к Ollama
    ollama_connector_limit: int = 20  # Максимальное количество соединений в пуле
    ollama_connector_limit_per_host: int = 10  # Максимальное количество соединений на хост
    
    # Rate Limiting для Ollama
    ollama_rate_limit_enabled: bool = True  # Включить rate limiting для Ollama
    ollama_rate_limit_max_requests: int = 15  # Максимальное количество запросов в окне времени (увеличено для ускорения)
    ollama_rate_limit_window_seconds: float = 1.0  # Размер окна времени в секундах (sliding window)
    
    # Rate Limiting для MCP сервера
    mcp_rate_limit_enabled: bool = True  # Включить rate limiting для MCP сервера
    mcp_rate_limit_max_requests: int = 100  # Максимальное количество запросов в окне времени
    mcp_rate_limit_window_seconds: float = 60.0  # Размер окна времени в секундах (1 минута)

    # Indexing
    chunk_size: int = 2000
    chunk_overlap: int = 250
    batch_size: int = 32
    max_workers: int = 10  # Максимальное количество параллельных файлов при индексации
    
    # Reliability: File size limits (in bytes)
    max_file_size: int = 50 * 1024 * 1024  # 50 MB по умолчанию
    max_file_size_streaming: int = 10 * 1024 * 1024  # 10 MB - использовать потоковую обработку

    # Search
    default_search_type: str = "hybrid"
    hybrid_alpha: float = 0.7  # Вес векторного поиска
    
    # Search Optimization
    enable_search_optimizer: bool = True  # Включить оптимизатор поиска
    enable_rerank: bool = True  # Включить re-ranking
    enable_query_expansion: bool = False  # Включить расширение запросов (может замедлить поиск)
    enable_feature_ranking: bool = True  # Включить feature-based ranking
    adaptive_alpha: bool = True  # Использовать адаптивный alpha для hybrid search
    
    # Adaptive Search v5 (Feature Flags)
    enable_intent_detection: bool = True  # Включить определение intent запроса
    enable_document_level_strategy: bool = True  # Включить стратегию поиска на уровне документов
    default_granularity: str = "auto"  # auto | document | chunk
    chunk_aggregation_method: str = "max"  # max | mean | rrf - метод агрегации scores для chunk-level поиска
    
    # === Yandex Cloud ===
    yandex_folder_id: str | None = None  # ID папки в Yandex Cloud
    yandex_api_key: str | None = None  # API ключ Yandex Cloud
    yandex_instance_id: str | None = None  # ID dedicated instance (опционально)
    
    # Embedding модели (asymmetric)
    yandex_embedding_doc_model: str = "text-search-doc/latest"  # Модель для индексации документов
    yandex_embedding_query_model: str = "text-search-query/latest"  # Модель для поисковых запросов
    
    # LLM модели (разделение по задачам)
    # Доступные модели: yandexgpt/latest, yandexgpt/rc, yandexgpt-lite, aliceai-llm,
    #                   qwen3-235b-a22b-fp8/latest, gpt-oss-120b/latest, gpt-oss-20b/latest, gemma-3-27b-it/latest
    yandex_enrichment_model: str = "qwen3-235b-a22b-fp8/latest"  # Модель для enrichment (JSON-генерация, 262K контекст)
    yandex_chat_model: str = "qwen3-235b-a22b-fp8/latest"  # Модель для общего чата (Qwen3-235B FP8)
    
    # LLM Enrichment
    enable_llm_enrichment: bool = True  # Включить LLM-обогащение чанков
    llm_model: str = "qwen2.5:7b-instruct"  # Модель для chat completion (используется для Ollama)
    llm_timeout: int = 60  # Таймаут для LLM запросов (в секундах) - увеличено для стабильности
    llm_max_concurrent: int = 5  # Максимальное количество одновременных LLM запросов (увеличено для производительности)
    llm_enrichment_cache_size: int = 1000  # Размер кэша обогащений
    llm_enrichment_strategy: str = "full"  # full | fast | custom - стратегия обогащения
    
    # Knowledge Clusters
    enable_knowledge_clusters: bool = True  # Включить кластеризацию знаний
    cluster_method: str = "kmeans"  # kmeans | dbscan - метод кластеризации
    auto_cluster_count: bool = True  # Автоматическое определение количества кластеров
    min_cluster_size: int = 5  # Минимальный размер кластера
    max_clusters: int = 10  # Максимальное количество кластеров
    
    # Logging
    structured_logging: bool = False  # Использовать структурированное логирование (JSON)
    log_file: Path | None = None  # Путь к файлу логов (опционально)
    performance_alert_threshold: float = 5.0  # Порог времени выполнения для алертов (в секундах)

    model_config = SettingsConfigDict(
        env_prefix="OBSIDIAN_KB_",
        case_sensitive=False,
    )


# Глобальный экземпляр настроек
settings = Settings()

