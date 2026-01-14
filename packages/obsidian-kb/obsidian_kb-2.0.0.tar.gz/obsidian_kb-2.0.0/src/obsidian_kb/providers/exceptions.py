"""Исключения для провайдеров LLM."""


class ProviderError(Exception):
    """Базовое исключение для ошибок провайдеров."""
    pass


class ProviderConnectionError(ProviderError):
    """Ошибка подключения к провайдеру."""
    pass


class ProviderTimeoutError(ProviderError):
    """Таймаут запроса к провайдеру."""
    pass


class ProviderAuthenticationError(ProviderError):
    """Ошибка аутентификации у провайдера."""
    pass


class ProviderRateLimitError(ProviderError):
    """Превышен лимит запросов к провайдеру."""
    pass


class ProviderModelNotFoundError(ProviderError):
    """Модель не найдена у провайдера."""
    pass


class ProviderConfigurationError(ProviderError):
    """Ошибка конфигурации провайдера."""
    pass

