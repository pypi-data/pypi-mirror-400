"""Пресеты конфигурации для быстрой настройки.

Предопределённые наборы настроек для различных сценариев использования.
"""

from obsidian_kb.config.schema import (
    EnrichmentConfig,
    EnrichmentStrategy,
    IndexingConfig,
    ProviderConfig,
    SearchConfig,
    VaultConfig,
)


class ConfigPresets:
    """Пресеты конфигурации."""
    
    @staticmethod
    def get_preset(preset_name: str) -> VaultConfig:
        """Получение пресета конфигурации по имени.
        
        Args:
            preset_name: Имя пресета (fast, balanced, quality, local, cloud)
            
        Returns:
            VaultConfig с настройками пресета
            
        Raises:
            ValueError: Если пресет не найден
        """
        presets = ConfigPresets._get_all_presets()
        if preset_name not in presets:
            available = ", ".join(presets.keys())
            raise ValueError(
                f"Unknown preset: {preset_name}. Available presets: {available}"
            )
        return presets[preset_name]
    
    @staticmethod
    def list_presets() -> dict[str, str]:
        """Список доступных пресетов с описаниями.
        
        Returns:
            Словарь {preset_name: description}
        """
        return {
            "fast": (
                "Минимальное обогащение, быстрая индексация. "
                "Подходит для больших vault'ов с частыми обновлениями."
            ),
            "balanced": (
                "Contextual Retrieval включен, оптимальный баланс скорости и качества. "
                "Рекомендуется для большинства случаев."
            ),
            "quality": (
                "Полное обогащение (context + summary), максимальное качество retrieval. "
                "Медленнее и дороже, но лучшее качество поиска."
            ),
            "local": (
                "Только локальные провайдеры (Ollama). "
                "Без облачных API, полная приватность."
            ),
            "cloud": (
                "Оптимизация под облачные провайдеры (OpenAI/Yandex). "
                "Увеличенный batch_size для эффективности."
            ),
        }
    
    @staticmethod
    def _get_all_presets() -> dict[str, VaultConfig]:
        """Все доступные пресеты."""
        return {
            "fast": VaultConfig(
                indexing=IndexingConfig(
                    chunk_size=1000,
                    chunk_overlap=100,
                ),
                enrichment=EnrichmentConfig(
                    strategy=EnrichmentStrategy.NONE,
                ),
                search=SearchConfig(
                    rerank_enabled=False,
                ),
            ),
            "balanced": VaultConfig(
                indexing=IndexingConfig(
                    chunk_size=800,
                    chunk_overlap=100,
                ),
                enrichment=EnrichmentConfig(
                    strategy=EnrichmentStrategy.CONTEXTUAL,
                    context_prefix_tokens=80,
                ),
                search=SearchConfig(
                    hybrid_alpha=0.7,
                    rerank_enabled=True,
                ),
            ),
            "quality": VaultConfig(
                indexing=IndexingConfig(
                    chunk_size=600,
                    chunk_overlap=100,
                    complexity_threshold=0.6,
                ),
                enrichment=EnrichmentConfig(
                    strategy=EnrichmentStrategy.FULL,
                    context_prefix_tokens=100,
                    summary_tokens=300,
                    batch_size=5,  # Меньше для лучшего качества
                ),
                search=SearchConfig(
                    hybrid_alpha=0.8,
                    rerank_enabled=True,
                ),
            ),
            "local": VaultConfig(
                providers=ProviderConfig(
                    embedding="ollama",
                    chat="ollama",
                ),
                enrichment=EnrichmentConfig(
                    strategy=EnrichmentStrategy.CONTEXTUAL,
                    batch_size=5,  # Меньше для локальных моделей
                ),
            ),
            "cloud": VaultConfig(
                providers=ProviderConfig(
                    embedding="openai",
                    chat="openai",
                ),
                enrichment=EnrichmentConfig(
                    strategy=EnrichmentStrategy.CONTEXTUAL,
                    batch_size=20,  # Больше для облачных API
                ),
            ),
        }

