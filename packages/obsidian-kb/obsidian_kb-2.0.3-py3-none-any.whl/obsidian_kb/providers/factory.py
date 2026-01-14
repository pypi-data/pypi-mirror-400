"""Фабрика для создания провайдеров LLM."""

import logging
from typing import TYPE_CHECKING

from obsidian_kb.config import settings
from obsidian_kb.config.manager import get_config_manager
from obsidian_kb.providers.exceptions import ProviderConfigurationError
from obsidian_kb.providers.interfaces import (
    IChatCompletionProvider,
    IEmbeddingProvider,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Фабрика для создания провайдеров embedding и chat completion.

    Поддерживает:
    - ollama (локальный)
    - yandex (Yandex Cloud)
    """
    
    @staticmethod
    def get_embedding_provider(
        provider_name: str | None = None,
        model: str | None = None,
        vault_name: str | None = None,
        **kwargs,
    ) -> IEmbeddingProvider:
        """Создание провайдера embeddings.

        Args:
            provider_name: Имя провайдера (по умолчанию из env или 'ollama')
            model: Название модели (по умолчанию из ConfigManager или settings)
            vault_name: Имя vault'а для получения конфигурации (опционально)
            **kwargs: Дополнительные параметры для провайдера

        Returns:
            Провайдер embeddings

        Raises:
            ProviderConfigurationError: Если провайдер не поддерживается или не настроен
        """
        # Получаем конфигурацию из ConfigManager
        config_manager = get_config_manager()
        config = config_manager.get_config(vault_name)

        # Приоритет провайдера: аргумент > ConfigManager > settings > default
        if not provider_name:
            provider_name = config.providers.embedding or getattr(settings, "embedding_provider", None) or "ollama"
        provider_name = provider_name.lower()

        if provider_name == "ollama":
            from obsidian_kb.providers.ollama.embedding_provider import OllamaEmbeddingProvider

            base_url = kwargs.get("base_url") or settings.ollama_url
            # Приоритет модели: аргумент > ConfigManager > settings
            if not model:
                model = config.providers.embedding_model or settings.embedding_model

            return OllamaEmbeddingProvider(
                base_url=base_url,
                model=model,
                timeout=kwargs.get("timeout"),
            )

        elif provider_name == "yandex":
            from obsidian_kb.providers.yandex.embedding_provider import YandexEmbeddingProvider

            folder_id = kwargs.get("folder_id") or getattr(settings, "yandex_folder_id", None)
            api_key = kwargs.get("api_key") or getattr(settings, "yandex_api_key", None)

            # Поддержка новых параметров для asymmetric embeddings
            doc_model = kwargs.get("doc_model") or getattr(settings, "yandex_embedding_doc_model", "text-search-doc/latest")
            query_model = kwargs.get("query_model") or getattr(settings, "yandex_embedding_query_model", "text-search-query/latest")

            # Обратная совместимость: аргумент model > ConfigManager > defaults
            if model:
                doc_model = model
            elif config.providers.embedding_model:
                doc_model = config.providers.embedding_model

            if not folder_id or not api_key:
                raise ProviderConfigurationError(
                    "Yandex provider requires folder_id and api_key. "
                    "Set OBSIDIAN_KB_YANDEX_FOLDER_ID and OBSIDIAN_KB_YANDEX_API_KEY"
                )

            return YandexEmbeddingProvider(
                folder_id=folder_id,
                api_key=api_key,
                doc_model=doc_model,
                query_model=query_model,
                timeout=kwargs.get("timeout"),
            )

        else:
            raise ProviderConfigurationError(
                f"Unsupported embedding provider: {provider_name}. "
                f"Supported: ollama, yandex"
            )
    
    @staticmethod
    def get_chat_provider(
        provider_name: str | None = None,
        model: str | None = None,
        vault_name: str | None = None,
        **kwargs,
    ) -> IChatCompletionProvider:
        """Создание провайдера chat completion.

        Args:
            provider_name: Имя провайдера (по умолчанию из env или 'ollama')
            model: Название модели (по умолчанию из ConfigManager или settings)
            vault_name: Имя vault'а для получения конфигурации (опционально)
            **kwargs: Дополнительные параметры для провайдера

        Returns:
            Провайдер chat completion

        Raises:
            ProviderConfigurationError: Если провайдер не поддерживается или не настроен
        """
        # Получаем конфигурацию из ConfigManager
        config_manager = get_config_manager()
        config = config_manager.get_config(vault_name)

        # Приоритет провайдера: аргумент > ConfigManager > settings > default
        if not provider_name:
            provider_name = config.providers.chat or getattr(settings, "chat_provider", None) or "ollama"
        provider_name = provider_name.lower()

        if provider_name == "ollama":
            from obsidian_kb.providers.ollama.chat_provider import OllamaChatProvider

            base_url = kwargs.get("base_url") or settings.ollama_url
            # Приоритет модели: аргумент > ConfigManager > settings
            if not model:
                model = config.providers.chat_model or settings.llm_model

            return OllamaChatProvider(
                base_url=base_url,
                model=model,
                timeout=kwargs.get("timeout"),
            )

        elif provider_name == "yandex":
            from obsidian_kb.providers.yandex.chat_provider import YandexChatProvider

            folder_id = kwargs.get("folder_id") or getattr(settings, "yandex_folder_id", None)
            api_key = kwargs.get("api_key") or getattr(settings, "yandex_api_key", None)

            # Определяем модель в зависимости от контекста использования
            # Приоритет: аргумент > ConfigManager > settings > default
            if not model:
                # Сначала проверяем ConfigManager
                model = config.providers.chat_model

                if not model:
                    # Если не указана в конфиге, берём из settings
                    use_for_enrichment = kwargs.get("use_for_enrichment", False)
                    if use_for_enrichment:
                        model = getattr(settings, "yandex_enrichment_model", "qwen3-235b-a22b-fp8/latest")
                    else:
                        model = getattr(settings, "yandex_chat_model", "qwen3-235b-a22b-fp8/latest")

            # instance_id: ConfigManager > settings
            instance_id = kwargs.get("instance_id") or config.providers.yandex_instance_id or getattr(settings, "yandex_instance_id", None)

            if not folder_id or not api_key:
                raise ProviderConfigurationError(
                    "Yandex provider requires folder_id and api_key. "
                    "Set OBSIDIAN_KB_YANDEX_FOLDER_ID and OBSIDIAN_KB_YANDEX_API_KEY"
                )

            return YandexChatProvider(
                folder_id=folder_id,
                api_key=api_key,
                model=model,
                timeout=kwargs.get("timeout"),
                instance_id=instance_id,
            )

        else:
            raise ProviderConfigurationError(
                f"Unsupported chat provider: {provider_name}. "
                f"Supported: ollama, yandex"
            )

