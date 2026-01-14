"""Адаптер для совместимости между IEmbeddingProvider и IEmbeddingService."""

from typing import TYPE_CHECKING

from obsidian_kb.providers.interfaces import IEmbeddingProvider

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IEmbeddingService


class EmbeddingProviderAdapter:
    """Адаптер, который делает IEmbeddingProvider совместимым с IEmbeddingService.
    
    Это временное решение для обратной совместимости. В будущем весь код
    должен использовать IEmbeddingProvider напрямую.
    """
    
    def __init__(self, provider: IEmbeddingProvider) -> None:
        """Инициализация адаптера.
        
        Args:
            provider: Провайдер embeddings
        """
        self._provider = provider
    
    async def get_embedding(self, text: str, embedding_type: str = "doc") -> list[float]:
        """Получение embedding для одного текста.
        
        Делегирует вызов провайдеру.
        """
        return await self._provider.get_embedding(text, embedding_type=embedding_type)
    
    async def get_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int = 10,
        embedding_type: str = "doc",
    ) -> list[list[float]]:
        """Батчевая генерация embeddings.
        
        Делегирует вызов провайдеру.
        """
        return await self._provider.get_embeddings_batch(texts, batch_size=batch_size, embedding_type=embedding_type)
    
    async def health_check(self) -> bool:
        """Проверка доступности провайдера.
        
        Returns:
            True если провайдер доступен, False иначе
        """
        health = await self._provider.health_check()
        return health.available
    
    async def close(self) -> None:
        """Закрытие ресурсов провайдера."""
        if hasattr(self._provider, "close"):
            await self._provider.close()
    
    @property
    def model(self) -> str:
        """Название модели провайдера."""
        return self._provider.model
    
    @property
    def base_url(self) -> str:
        """Базовый URL (если есть)."""
        if hasattr(self._provider, "_base_url"):
            return getattr(self._provider, "_base_url", "")
        return ""

