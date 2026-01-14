"""Конфигурация провайдеров с учётом их производительности."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    """Конфигурация провайдера."""

    max_concurrent: int  # Максимум параллельных запросов для embeddings
    batch_size: int  # Размер батча для embeddings
    enrichment_concurrent: int  # Максимум параллельных LLM запросов для enrichment
    rate_limit_rps: int | None  # Rate limit (requests per second), None = без лимита
    timeout: int  # Таймаут запросов в секундах
    # Параметры адаптивного rate limiting
    adaptive_rate_limit: bool = False  # Включить адаптивный rate limiting
    rate_limit_min_rps: float = 1.0  # Минимальный RPS при backoff
    rate_limit_max_rps: float | None = None  # Максимальный RPS (None = rate_limit_rps)
    rate_limit_recovery: int = 50  # Успехов для увеличения RPS


# Пресеты для провайдеров
PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "ollama": ProviderConfig(
        max_concurrent=10,
        batch_size=32,
        enrichment_concurrent=5,
        rate_limit_rps=15,
        timeout=60,
        adaptive_rate_limit=False,  # Локальный, адаптация не нужна
    ),
    "yandex": ProviderConfig(
        max_concurrent=50,  # Yandex поддерживает больше параллельных запросов
        batch_size=100,  # Больший batch для embeddings
        enrichment_concurrent=10,  # Уменьшено с 20 для стабильности
        rate_limit_rps=20,  # Начальный RPS (уменьшено для безопасности)
        timeout=30,  # Меньший таймаут (облако быстрее)
        adaptive_rate_limit=True,  # Адаптация к лимитам Yandex API
        rate_limit_min_rps=2.0,  # Минимум при серии 429
        rate_limit_max_rps=100.0,  # Максимум после восстановления
        rate_limit_recovery=30,  # Успехов для увеличения RPS
    ),
}


def get_provider_config(provider_name: str) -> ProviderConfig:
    """Получить конфигурацию провайдера.

    Args:
        provider_name: Имя провайдера (ollama, yandex)

    Returns:
        Конфигурация провайдера (fallback на ollama если не найден)
    """
    return PROVIDER_CONFIGS.get(provider_name.lower(), PROVIDER_CONFIGS["ollama"])
