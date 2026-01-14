"""Стратегия быстрого обогащения чанков (только summary)."""

import hashlib
import json
import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING

from obsidian_kb.enrichment.prompts import ENRICHMENT_SYSTEM_PROMPT, FAST_ENRICHMENT_PROMPT
from obsidian_kb.providers.exceptions import ProviderError
from obsidian_kb.types import ChunkEnrichment, DocumentChunk

if TYPE_CHECKING:
    from obsidian_kb.providers.interfaces import IChatCompletionProvider

logger = logging.getLogger(__name__)


class FastEnrichmentStrategy:
    """Стратегия быстрого обогащения чанков через LLM.

    Генерирует только summary (краткое резюме).
    Key concepts и semantic tags остаются пустыми списками.

    Использует IChatCompletionProvider для работы с любым LLM провайдером
    (Ollama, Yandex, OpenAI и т.д.).
    """

    def __init__(
        self,
        chat_provider: "IChatCompletionProvider",
        temperature: float = 0.1,
        max_tokens: int = 256,
    ) -> None:
        """Инициализация стратегии.

        Args:
            chat_provider: Провайдер chat completion (Ollama, Yandex, etc.)
            temperature: Температура генерации (по умолчанию 0.1 для детерминизма)
            max_tokens: Максимальное количество токенов в ответе (меньше для быстрого обогащения)
        """
        self._chat_provider = chat_provider
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def provider_name(self) -> str:
        """Имя используемого провайдера."""
        return self._chat_provider.name

    @property
    def model(self) -> str:
        """Название используемой модели."""
        return self._chat_provider.model

    async def close(self) -> None:
        """Закрытие ресурсов (для совместимости с предыдущим API)."""
        # IChatCompletionProvider не требует явного закрытия
        pass

    def _compute_content_hash(self, chunk: DocumentChunk) -> str:
        """Вычисление SHA256 hash контента чанка.

        Args:
            chunk: Чанк для вычисления hash

        Returns:
            SHA256 hash в hex формате
        """
        content = chunk.content
        return hashlib.sha256(content.encode()).hexdigest()

    def _parse_llm_response(self, response_text: str) -> str:
        """Парсинг ответа LLM для извлечения summary с fallback-стратегиями.

        Args:
            response_text: Текст ответа от LLM

        Returns:
            Summary (краткое резюме)

        Raises:
            ValueError: Если не удалось распарсить ответ
        """
        raw_response = response_text.strip()

        # Стратегия 1: Прямой парсинг (если ответ чистый JSON)
        try:
            data = json.loads(raw_response)
            if isinstance(data, dict):
                summary = data.get("summary", "")
                if isinstance(summary, str) and summary.strip():
                    return summary.strip()
        except json.JSONDecodeError:
            pass

        # Стратегия 2: Извлечение из markdown code block
        code_block_match = re.search(
            r'```(?:json)?\s*(\{.*?\})\s*```',
            raw_response,
            re.DOTALL
        )
        if code_block_match:
            try:
                data = json.loads(code_block_match.group(1))
                if isinstance(data, dict):
                    summary = data.get("summary", "")
                    if isinstance(summary, str) and summary.strip():
                        return summary.strip()
            except json.JSONDecodeError:
                pass

        # Стратегия 3: Поиск JSON-объекта в тексте (greedy)
        json_match = re.search(
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            raw_response,
            re.DOTALL
        )
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if isinstance(data, dict):
                    summary = data.get("summary", "")
                    if isinstance(summary, str) and summary.strip():
                        return summary.strip()
            except json.JSONDecodeError:
                pass

        # Стратегия 4: Очистка и исправление common issues
        cleaned = raw_response

        # Удаление trailing commas: ,] → ] и ,} → }
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)

        # Замена одинарных кавычек на двойные (осторожно!)
        if cleaned.startswith("{") or cleaned.startswith("["):
            cleaned = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', cleaned)
            cleaned = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned)

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                summary = data.get("summary", "")
                if isinstance(summary, str) and summary.strip():
                    return summary.strip()
        except json.JSONDecodeError:
            pass

        # Fallback: если не удалось распарсить JSON, используем весь текст
        # (удаляем markdown обёртки если есть)
        fallback_text = raw_response
        if "```" in fallback_text:
            lines = fallback_text.split("\n")
            start_idx = 0
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    if start_idx == 0:
                        start_idx = i + 1
                    else:
                        end_idx = i
                        break
            if start_idx < end_idx:
                fallback_text = "\n".join(lines[start_idx:end_idx]).strip()

        logger.debug("LLM response is not valid JSON, using cleaned text as summary")
        return fallback_text.strip()

    async def _call_llm(self, content: str) -> str:
        """Вызов LLM через IChatCompletionProvider.

        Args:
            content: Контент чанка для обогащения

        Returns:
            Summary (краткое резюме)

        Raises:
            ProviderError: При ошибке провайдера
        """
        # Формируем промпт
        user_prompt = FAST_ENRICHMENT_PROMPT.format(content=content)

        messages = [
            {"role": "system", "content": ENRICHMENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response_text = await self._chat_provider.complete(
                messages=messages,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

            if not response_text:
                raise ProviderError(f"Empty response from {self.provider_name}")

            return self._parse_llm_response(response_text)

        except ProviderError:
            # Пробрасываем ошибки провайдера как есть
            raise
        except Exception as e:
            # Неожиданные ошибки оборачиваем в ProviderError
            raise ProviderError(f"Unexpected error calling {self.provider_name}: {e}") from e

    async def enrich(self, chunk: DocumentChunk) -> ChunkEnrichment:
        """Обогащение чанка через LLM (только summary).

        Args:
            chunk: Чанк для обогащения

        Returns:
            Обогащенные данные чанка (только summary заполнен)

        Raises:
            ProviderError: При ошибке провайдера
        """
        # Вычисляем content_hash
        content_hash = self._compute_content_hash(chunk)

        # Вызываем LLM
        summary = await self._call_llm(chunk.content)

        # Создаем ChunkEnrichment (key_concepts и semantic_tags пустые)
        enrichment = ChunkEnrichment(
            chunk_id=chunk.id,
            vault_name=chunk.vault_name,
            summary=summary,
            key_concepts=[],  # Пустой список для быстрого обогащения
            semantic_tags=[],  # Пустой список для быстрого обогащения
            enriched_at=datetime.now(),
            content_hash=content_hash,
        )

        return enrichment
