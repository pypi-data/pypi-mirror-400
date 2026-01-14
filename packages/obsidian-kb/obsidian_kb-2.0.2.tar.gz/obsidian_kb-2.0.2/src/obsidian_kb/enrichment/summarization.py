"""Сервис для генерации summary документов через LLM."""

import logging
from dataclasses import dataclass
from typing import Any

from obsidian_kb.config.schema import EnrichmentConfig

logger = logging.getLogger(__name__)


@dataclass
class DocumentSummary:
    """Summary документа."""
    
    summary_text: str  # Краткое описание документа (250-300 токенов)
    provider_info: dict[str, str] | None = None  # Информация о провайдере


class SummarizationService:
    """Сервис для генерации summary документов через LLM.
    
    Summary содержит краткое описание документа, что улучшает качество
    поиска на уровне документов.
    """
    
    def __init__(
        self,
        chat_provider: Any,  # IChatCompletionProvider
        config: EnrichmentConfig | None = None,
    ) -> None:
        """Инициализация сервиса.
        
        Args:
            chat_provider: Провайдер для генерации summary
            config: Конфигурация обогащения
        """
        self._chat = chat_provider
        self._config = config or EnrichmentConfig()
    
    async def summarize_document(
        self,
        content: str,
        metadata: dict[str, Any],
    ) -> DocumentSummary:
        """Генерирует summary для документа.
        
        Args:
            content: Полное содержимое документа
            metadata: Метаданные документа (frontmatter)
            
        Returns:
            DocumentSummary с кратким описанием документа
        """
        # Проверяем, нужно ли генерировать summary
        # Summary генерируется только для документов > 1000 токенов
        estimated_tokens = len(content) // 3
        if estimated_tokens < 1000:
            logger.debug("Document too short for summarization, skipping")
            return DocumentSummary(
                summary_text="",
                provider_info=None,
            )
        
        try:
            summary_text = await self._generate_summary(content, metadata)
            
            return DocumentSummary(
                summary_text=summary_text,
                provider_info={
                    "provider": self._chat.name,
                    "model": self._chat.model,
                },
            )
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Graceful degradation: возвращаем пустой summary
            return DocumentSummary(
                summary_text="",
                provider_info=None,
            )
    
    async def _generate_summary(
        self,
        content: str,
        metadata: dict[str, Any],
    ) -> str:
        """Генерация summary для документа.
        
        Args:
            content: Содержимое документа
            metadata: Метаданные документа
            
        Returns:
            Summary документа (250-300 токенов)
        """
        # Формируем промпт для генерации summary
        prompt = self._build_prompt(content, metadata)
        
        # Генерируем через LLM
        messages = [
            {
                "role": "system",
                "content": "Ты помощник для генерации кратких резюме документов. "
                           "Твоя задача - создать краткое описание документа (250-300 токенов), "
                           "которое поможет понять основное содержание документа при поиске.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        try:
            max_tokens = self._config.summary_tokens + 50  # Небольшой запас
            response = await self._chat.complete(
                messages=messages,
                temperature=0.3,  # Низкая температура для более детерминированных результатов
                max_tokens=max_tokens,
            )
            
            # Обрезаем до нужной длины (примерно)
            summary = response.strip()
            
            # Проверяем длину и обрезаем если нужно
            estimated_tokens = len(summary) // 3  # Примерная оценка токенов
            if estimated_tokens > self._config.summary_tokens:
                # Обрезаем до нужной длины
                max_chars = self._config.summary_tokens * 3
                summary = summary[:max_chars].rsplit(".", 1)[0] + "."
            
            return summary
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise
    
    def _build_prompt(self, content: str, metadata: dict[str, Any]) -> str:
        """Построение промпта для генерации summary.
        
        Args:
            content: Содержимое документа
            metadata: Метаданные документа
            
        Returns:
            Промпт для LLM
        """
        # Извлекаем заголовок из метаданных
        title = metadata.get("title", "")
        doc_type = metadata.get("type", "")
        
        # Ограничиваем длину контента для промпта
        max_content_length = 5000  # Примерно 1500-2000 токенов
        content_preview = content[:max_content_length]
        if len(content) > max_content_length:
            content_preview += "\n\n[... документ продолжается ...]"
        
        prompt = f"""Создай краткое резюме следующего документа.

Метаданные:
- Заголовок: {title}
- Тип: {doc_type}

Содержимое документа:
{content_preview}

Создай краткое резюме (250-300 токенов), которое поможет понять основное содержание документа при поиске.
Резюме должно быть информативным и содержать ключевые идеи и понятия из документа.

Резюме:"""
        
        return prompt

