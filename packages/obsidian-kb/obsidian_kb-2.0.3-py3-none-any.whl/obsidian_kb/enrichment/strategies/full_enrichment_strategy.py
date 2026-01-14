"""Стратегия полного обогащения чанков (summary + concepts + tags)."""

import hashlib
import json
import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING, Any

from obsidian_kb.enrichment.prompts import ENRICHMENT_SYSTEM_PROMPT, FULL_ENRICHMENT_PROMPT
from obsidian_kb.providers.exceptions import ProviderError
from obsidian_kb.types import ChunkEnrichment, DocumentChunk

if TYPE_CHECKING:
    from obsidian_kb.providers.interfaces import IChatCompletionProvider

logger = logging.getLogger(__name__)


class FullEnrichmentStrategy:
    """Стратегия полного обогащения чанков через LLM.

    Генерирует:
    - Summary (краткое резюме)
    - Key concepts (ключевые понятия)
    - Semantic tags (семантические теги)

    Использует IChatCompletionProvider для работы с любым LLM провайдером
    (Ollama, Yandex, OpenAI и т.д.).
    """

    def __init__(
        self,
        chat_provider: "IChatCompletionProvider",
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> None:
        """Инициализация стратегии.

        Args:
            chat_provider: Провайдер chat completion (Ollama, Yandex, etc.)
            temperature: Температура генерации (по умолчанию 0.1 для детерминизма)
            max_tokens: Максимальное количество токенов в ответе
        """
        self._chat_provider = chat_provider
        self._temperature = temperature
        self._max_tokens = max_tokens

        # Статистика парсинга JSON
        self._parse_success_count = 0
        self._parse_failure_count = 0

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

    def _parse_llm_response(self, response_text: str) -> dict[str, Any]:
        """Парсинг ответа LLM в JSON формат с fallback-стратегиями.

        Args:
            response_text: Текст ответа от LLM

        Returns:
            Словарь с полями summary, key_concepts, semantic_tags

        Raises:
            ValueError: Если не удалось распарсить ответ
        """
        raw_response = response_text.strip()

        # Стратегия 1: Прямой парсинг (если ответ чистый JSON)
        try:
            data = json.loads(raw_response)
            result = self._normalize_enrichment_data(data)
            self._parse_success_count += 1
            return result
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
                result = self._normalize_enrichment_data(data)
                self._parse_success_count += 1
                return result
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
                result = self._normalize_enrichment_data(data)
                self._parse_success_count += 1
                return result
            except json.JSONDecodeError:
                pass

        # Стратегия 4: Очистка и исправление common issues
        cleaned = raw_response

        # Удаление trailing commas: ,] → ] и ,} → }
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)

        # Замена одинарных кавычек на двойные (осторожно!)
        # Только если это явно JSON-like структура
        if cleaned.startswith("{") or cleaned.startswith("["):
            # Заменяем только кавычки вокруг ключей/значений
            cleaned = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', cleaned)
            cleaned = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned)

        try:
            data = json.loads(cleaned)
            result = self._normalize_enrichment_data(data)
            self._parse_success_count += 1
            return result
        except json.JSONDecodeError as e:
            self._parse_failure_count += 1
            logger.warning(
                f"Failed to parse LLM response as JSON: {e}, "
                f"response (first 300 chars): {raw_response[:300]}"
            )
            raise ValueError(f"Invalid JSON response from LLM: {e}") from e

    def _normalize_enrichment_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Нормализация и валидация данных обогащения.

        Args:
            data: Распарсенный JSON

        Returns:
            Нормализованный словарь с гарантированными типами
        """
        if not isinstance(data, dict):
            raise ValueError("LLM response is not a JSON object")

        # Извлечение с fallback
        summary = data.get("summary", "")
        key_concepts = data.get("key_concepts", [])
        semantic_tags = data.get("semantic_tags", [])

        # Нормализация summary
        if not isinstance(summary, str):
            summary = str(summary) if summary else ""
        summary = summary.strip()

        # Нормализация списков (если модель вернула строку)
        if isinstance(key_concepts, str):
            key_concepts = [s.strip() for s in key_concepts.split(",") if s.strip()]
        if isinstance(semantic_tags, str):
            semantic_tags = [s.strip() for s in semantic_tags.split(",") if s.strip()]

        # Валидация и очистка списков
        if not isinstance(key_concepts, list):
            key_concepts = []
        if not isinstance(semantic_tags, list):
            semantic_tags = []

        key_concepts = [
            str(c).strip()
            for c in key_concepts
            if c and str(c).strip()
        ][:5]

        semantic_tags = [
            str(t).strip()
            for t in semantic_tags
            if t and str(t).strip()
        ][:5]

        return {
            "summary": summary,
            "key_concepts": key_concepts,
            "semantic_tags": semantic_tags,
        }

    def get_parse_stats(self) -> dict[str, int | float]:
        """Получение статистики парсинга JSON."""
        total = self._parse_success_count + self._parse_failure_count
        success_rate = (
            self._parse_success_count / total * 100
            if total > 0 else 0.0
        )
        return {
            "success": self._parse_success_count,
            "failure": self._parse_failure_count,
            "total": total,
            "success_rate_percent": round(success_rate, 2),
        }

    async def _call_llm(self, content: str) -> dict[str, Any]:
        """Вызов LLM через IChatCompletionProvider.

        Args:
            content: Контент чанка для обогащения

        Returns:
            Словарь с полями summary, key_concepts, semantic_tags

        Raises:
            ProviderError: При ошибке провайдера
        """
        # Формируем промпт
        user_prompt = FULL_ENRICHMENT_PROMPT.format(content=content)

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
        except ValueError as e:
            # Ошибка парсинга JSON
            raise ProviderError(f"Failed to parse LLM response: {e}") from e
        except Exception as e:
            # Неожиданные ошибки оборачиваем в ProviderError
            raise ProviderError(f"Unexpected error calling {self.provider_name}: {e}") from e

    async def enrich(self, chunk: DocumentChunk) -> ChunkEnrichment:
        """Обогащение чанка через LLM.

        Args:
            chunk: Чанк для обогащения

        Returns:
            Обогащенные данные чанка

        Raises:
            ProviderError: При ошибке провайдера
        """
        # Вычисляем content_hash
        content_hash = self._compute_content_hash(chunk)

        # Вызываем LLM
        enrichment_data = await self._call_llm(chunk.content)

        # Создаем ChunkEnrichment
        enrichment = ChunkEnrichment(
            chunk_id=chunk.id,
            vault_name=chunk.vault_name,
            summary=enrichment_data["summary"],
            key_concepts=enrichment_data["key_concepts"],
            semantic_tags=enrichment_data["semantic_tags"],
            enriched_at=datetime.now(),
            content_hash=content_hash,
        )

        return enrichment
