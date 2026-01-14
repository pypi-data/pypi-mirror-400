"""Форматирование результатов поиска для MCP."""

from urllib.parse import quote
from typing import Any

from obsidian_kb.types import DocumentSearchResult, MatchType, RelevanceScore, SearchIntent, SearchResponse


class MCPResultFormatter:
    """Реализация IResultFormatter для форматирования результатов в Markdown и JSON."""

    INTENT_LABELS = {
        SearchIntent.METADATA_FILTER: "📋 Фильтр по метаданным",
        SearchIntent.KNOWN_ITEM: "📄 Поиск документа",
        SearchIntent.SEMANTIC: "🔍 Семантический поиск",
        SearchIntent.EXPLORATORY: "🧭 Исследовательский поиск",
        SearchIntent.PROCEDURAL: "📚 Инструкция",
    }

    def format_markdown(
        self,
        response: SearchResponse,
    ) -> str:
        """Форматирование в Markdown для агента.
        
        Args:
            response: Ответ поиска с результатами
            
        Returns:
            Отформатированная строка Markdown
        """
        lines = []
        
        # Заголовок
        lines.append(f"## Результаты поиска: \"{response.request.query}\"\n")
        
        # Метаданные
        intent_label = self.INTENT_LABELS.get(response.detected_intent, "🔍 Поиск")
        lines.append(
            f"*{intent_label} | "
            f"{response.total_found} документов | "
            f"{response.execution_time_ms:.0f} мс*\n"
        )
        
        if not response.results:
            lines.append("*Результаты не найдены*")
            return "\n".join(lines)
        
        # Результаты
        for idx, result in enumerate(response.results, 1):
            lines.extend(self._format_result(idx, result))
        
        return "\n".join(lines)

    def format_json(
        self,
        response: SearchResponse,
    ) -> dict[str, Any]:
        """Форматирование в JSON для структурированного вывода.
        
        Args:
            response: Ответ поиска с результатами
            
        Returns:
            Словарь с структурированными данными для structuredContent
        """
        return {
            "query": response.request.query,
            "intent": response.detected_intent.value,
            "intentConfidence": response.intent_confidence,
            "totalFound": response.total_found,
            "executionTimeMs": response.execution_time_ms,
            "strategyUsed": response.strategy_used,
            "results": [
                {
                    "documentId": r.document.document_id,
                    "vaultName": r.document.vault_name,
                    "filePath": r.document.file_path,
                    "title": r.document.title,
                    "relevance": r.score.value,
                    "relevanceLabel": r.score.label,
                    "matchType": r.score.match_type.value,
                    "tags": r.document.tags,
                    "snippet": r.snippet[:200] if r.snippet else None,
                    "matchedSections": r.matched_sections,
                    "modifiedAt": r.document.modified_at.isoformat() if r.document.modified_at else None,
                }
                for r in response.results
            ],
        }

    def _format_result(self, idx: int, result: DocumentSearchResult) -> list[str]:
        """Форматирование одного результата.
        
        Args:
            idx: Порядковый номер результата
            result: Результат поиска
            
        Returns:
            Список строк Markdown для результата
        """
        lines = []
        doc = result.document
        
        # Obsidian URL
        vault_encoded = quote(doc.vault_name)
        file_encoded = quote(doc.file_path)
        obsidian_url = f"obsidian://open?vault={vault_encoded}&file={file_encoded}"
        
        # Заголовок
        score_label = self._score_label(result.score)
        lines.append(f"### {idx}. [{doc.title}]({obsidian_url})")
        lines.append(f"**Релевантность:** {score_label} ({result.score.value:.0%})")
        
        # Match type
        if result.score.match_type == MatchType.EXACT_METADATA:
            lines.append("**Тип:** Точное совпадение фильтров")
        elif result.score.match_type == MatchType.SEMANTIC:
            lines.append("**Тип:** Семантическое сходство")
        elif result.score.match_type == MatchType.KEYWORD:
            lines.append("**Тип:** Ключевые слова")
        elif result.score.match_type == MatchType.HYBRID:
            lines.append("**Тип:** Гибридный поиск")
        
        # Теги
        if doc.tags:
            tags_str = " ".join(f"#{t}" for t in doc.tags[:5])
            if len(doc.tags) > 5:
                tags_str += f" и ещё {len(doc.tags) - 5}"
            lines.append(f"**Теги:** {tags_str}")
        
        # Контент (snippet)
        snippet = result.snippet
        if snippet:
            if len(snippet) > 500:
                snippet = snippet[:500] + "..."
            lines.append(f"\n> {snippet}\n")
        
        # Matched sections (для chunk-level)
        if result.matched_sections:
            sections = ", ".join(result.matched_sections[:3])
            if len(result.matched_sections) > 3:
                sections += f" и ещё {len(result.matched_sections) - 3}"
            lines.append(f"**Секции:** {sections}")
        
        lines.append("---\n")
        return lines

    def _score_label(self, score: RelevanceScore) -> str:
        """Метка релевантности.
        
        Args:
            score: Оценка релевантности
            
        Returns:
            Человекочитаемая метка с эмодзи
        """
        if score.value >= 0.9:
            return "🟢 Высокая"
        elif score.value >= 0.7:
            return "🟡 Средняя"
        elif score.value >= 0.5:
            return "🟠 Низкая"
        return "🔴 Минимальная"

