"""Multi-provider support для LLM провайдеров (embedding и chat completion).

Поддерживаемые провайдеры:
- Ollama (локальный) - реализован
- Yandex Cloud - реализован
"""

from obsidian_kb.providers.base_provider import BaseProvider
from obsidian_kb.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderError,
    ProviderModelNotFoundError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from obsidian_kb.providers.factory import ProviderFactory
from obsidian_kb.providers.interfaces import (
    IChatCompletionProvider,
    IEmbeddingProvider,
    ProviderHealth,
)
from obsidian_kb.providers.provider_config import (
    PROVIDER_CONFIGS,
    ProviderConfig,
    get_provider_config,
)
from obsidian_kb.providers.cached_provider import (
    CachedEmbeddingProvider,
    CacheMetrics,
    wrap_with_cache,
)

__all__ = [
    "BaseProvider",
    "IChatCompletionProvider",
    "IEmbeddingProvider",
    "PROVIDER_CONFIGS",
    "ProviderAuthenticationError",
    "ProviderConfig",
    "ProviderConfigurationError",
    "ProviderConnectionError",
    "ProviderError",
    "ProviderFactory",
    "ProviderHealth",
    "ProviderModelNotFoundError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "get_provider_config",
    # Cached provider
    "CachedEmbeddingProvider",
    "CacheMetrics",
    "wrap_with_cache",
]

