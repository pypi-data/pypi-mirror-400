"""Yandex Cloud провайдеры для embedding и chat completion."""

from obsidian_kb.providers.yandex.embedding_provider import YandexEmbeddingProvider
from obsidian_kb.providers.yandex.chat_provider import YandexChatProvider

__all__ = [
    "YandexEmbeddingProvider",
    "YandexChatProvider",
]

