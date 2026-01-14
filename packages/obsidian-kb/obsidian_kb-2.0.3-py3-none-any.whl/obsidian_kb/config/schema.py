"""Pydantic схемы для конфигурации obsidian-kb.

Определяет структуру конфигурации для индексации, обогащения и провайдеров.
"""

from enum import Enum
from typing import Literal, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EnrichmentStrategy(str, Enum):
    """Стратегия обогащения документов."""
    NONE = "none"
    CONTEXTUAL = "contextual"
    FULL = "full"


class IndexingConfig(BaseModel):
    """Конфигурация индексации документов."""
    
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=2000,
        description="Максимальный размер чанка в токенах",
    )
    chunk_overlap: int = Field(
        default=100,
        ge=0,
        le=500,
        description="Перекрытие между чанками в токенах",
    )
    min_chunk_size: int = Field(
        default=100,
        ge=50,
        le=500,
        description="Минимальный размер чанка в токенах",
    )
    complexity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Порог сложности для семантического уточнения (0.0-1.0)",
    )
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        """Проверка, что overlap не превышает chunk_size."""
        chunk_size = info.data.get("chunk_size", 800)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) must be less than chunk_size ({chunk_size})")
        return v


class EnrichmentConfig(BaseModel):
    """Конфигурация обогащения документов через LLM."""
    
    strategy: EnrichmentStrategy = Field(
        default=EnrichmentStrategy.CONTEXTUAL,
        description="Стратегия обогащения: none, contextual, full",
    )
    context_prefix_tokens: int = Field(
        default=80,
        ge=0,
        le=200,
        description="Количество токенов для context prefix (Contextual Retrieval)",
    )
    summary_tokens: int = Field(
        default=250,
        ge=50,
        le=500,
        description="Количество токенов для summary документа",
    )
    batch_size: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Размер батча для обогащения",
    )
    max_concurrent: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Максимальное количество параллельных запросов к LLM для обогащения",
    )

    @property
    def is_enabled(self) -> bool:
        """Проверка, включено ли обогащение."""
        return self.strategy != EnrichmentStrategy.NONE


class ProviderConfig(BaseModel):
    """Конфигурация провайдеров LLM."""
    
    embedding: Literal["ollama", "yandex", "openai"] = Field(
        default="ollama",
        description="Провайдер для embeddings",
    )
    chat: Literal["ollama", "yandex", "openai"] = Field(
        default="ollama",
        description="Провайдер для chat completion",
    )
    embedding_model: str | None = Field(
        default=None,
        description="Конкретная модель для embeddings (None = default для провайдера)",
    )
    chat_model: str | None = Field(
        default=None,
        description="Конкретная модель для chat completion (None = default для провайдера)",
    )
    # Yandex specific
    yandex_instance_id: str | None = Field(
        default=None,
        description="ID dedicated instance для Yandex (опционально)",
    )


class SearchConfig(BaseModel):
    """Конфигурация поиска."""
    
    hybrid_alpha: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Вес векторного поиска в hybrid search (0.0-1.0)",
    )
    rerank_enabled: bool = Field(
        default=True,
        description="Включить re-ranking результатов",
    )


class VaultConfig(BaseModel):
    """Полная конфигурация для vault'а.
    
    Объединяет все секции конфигурации:
    - indexing: параметры индексации
    - enrichment: параметры обогащения
    - providers: настройки провайдеров LLM
    - search: параметры поиска
    """
    
    indexing: IndexingConfig = Field(
        default_factory=IndexingConfig,
        description="Конфигурация индексации",
    )
    enrichment: EnrichmentConfig = Field(
        default_factory=EnrichmentConfig,
        description="Конфигурация обогащения",
    )
    providers: ProviderConfig = Field(
        default_factory=ProviderConfig,
        description="Конфигурация провайдеров",
    )
    search: SearchConfig = Field(
        default_factory=SearchConfig,
        description="Конфигурация поиска",
    )
    
    model_config = ConfigDict(
        use_enum_values=True,
    )

