"""Интерфейсы (Protocol) для LLM провайдеров.

Используются для поддержки нескольких провайдеров через единый интерфейс.
"""

from typing import Protocol, runtime_checkable
from dataclasses import dataclass


@dataclass
class ProviderHealth:
    """Статус здоровья провайдера."""
    available: bool
    latency_ms: float | None = None
    error: str | None = None
    model: str | None = None
    dimensions: int | None = None  # Для embedding провайдеров


@runtime_checkable
class IEmbeddingProvider(Protocol):
    """Интерфейс для провайдера embeddings.
    
    Все провайдеры embeddings должны реализовывать этот протокол.
    """
    
    @property
    def name(self) -> str:
        """Имя провайдера (например, 'ollama', 'yandex', 'openai')."""
        ...
    
    @property
    def model(self) -> str:
        """Название модели для embeddings."""
        ...
    
    @property
    def dimensions(self) -> int:
        """Размерность векторов embeddings."""
        ...
    
    async def get_embedding(self, text: str, embedding_type: str = "doc") -> list[float]:
        """Получение embedding для одного текста.
        
        Args:
            text: Текст для генерации embedding
            embedding_type: Тип embedding ("doc" для документов, "query" для запросов).
                           Поддерживается не всеми провайдерами (по умолчанию "doc").
            
        Returns:
            Векторное представление текста (список float)
            
        Raises:
            ProviderError: При ошибке получения embedding
        """
        ...
    
    async def get_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        embedding_type: str = "doc",
    ) -> list[list[float]]:
        """Батчевая генерация embeddings.
        
        Args:
            texts: Список текстов для генерации embeddings
            batch_size: Размер батча (None = использовать default провайдера)
            embedding_type: Тип embedding ("doc" для документов, "query" для запросов).
                           Поддерживается не всеми провайдерами (по умолчанию "doc").
            
        Returns:
            Список векторных представлений
            
        Raises:
            ProviderError: При ошибке получения embeddings
        """
        ...
    
    async def health_check(self) -> ProviderHealth:
        """Проверка доступности провайдера.
        
        Returns:
            ProviderHealth с информацией о статусе провайдера
        """
        ...


@runtime_checkable
class IChatCompletionProvider(Protocol):
    """Интерфейс для провайдера chat completion.
    
    Все провайдеры chat completion должны реализовывать этот протокол.
    """
    
    @property
    def name(self) -> str:
        """Имя провайдера (например, 'ollama', 'yandex', 'openai')."""
        ...
    
    @property
    def model(self) -> str:
        """Название модели для chat completion."""
        ...
    
    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Генерация ответа на основе сообщений.
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Температура генерации (0.0-2.0)
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            Сгенерированный текст
            
        Raises:
            ProviderError: При ошибке генерации
        """
        ...
    
    async def health_check(self) -> ProviderHealth:
        """Проверка доступности провайдера.
        
        Returns:
            ProviderHealth с информацией о статусе провайдера
        """
        ...

