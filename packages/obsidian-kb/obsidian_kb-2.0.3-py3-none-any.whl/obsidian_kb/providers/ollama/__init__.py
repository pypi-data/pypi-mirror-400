"""Ollama провайдеры для embedding и chat completion."""

from obsidian_kb.providers.ollama.embedding_provider import OllamaEmbeddingProvider
from obsidian_kb.providers.ollama.chat_provider import OllamaChatProvider

__all__ = [
    "OllamaEmbeddingProvider",
    "OllamaChatProvider",
]

