"""Unit-тесты для MCPResultFormatter."""

from datetime import datetime

import pytest

from obsidian_kb.presentation.formatter import MCPResultFormatter
from obsidian_kb.types import (
    Document,
    DocumentSearchResult,
    MatchType,
    RelevanceScore,
    RetrievalGranularity,
    SearchIntent,
    SearchRequest,
    SearchResponse,
)


@pytest.fixture
def formatter():
    """MCPResultFormatter для тестов."""
    return MCPResultFormatter()


@pytest.fixture
def sample_document():
    """Пример документа для тестов."""
    return Document(
        document_id="test::file.md",
        vault_name="test",
        file_path="file.md",
        title="Test File",
        content="Full content here",
        summary="Summary",
        tags=["python", "async"],
        properties={"type": "guide"},
        created_at=datetime(2024, 1, 1),
        modified_at=datetime(2024, 1, 2),
        chunk_count=3,
        content_length=100,
    )


@pytest.fixture
def sample_search_response(sample_document):
    """Пример SearchResponse для тестов."""
    result = DocumentSearchResult(
        document=sample_document,
        score=RelevanceScore(value=0.85, match_type=MatchType.SEMANTIC),
        matched_chunks=[],
        matched_sections=["Introduction"],
    )
    
    request = SearchRequest(
        vault_name="test",
        query="python programming",
        limit=10,
    )
    
    return SearchResponse(
        request=request,
        detected_intent=SearchIntent.SEMANTIC,
        intent_confidence=0.9,
        results=[result],
        total_found=1,
        execution_time_ms=50.0,
        has_more=False,
        strategy_used="chunk_level",
        filters_applied={},
    )


class TestMCPResultFormatter:
    """Тесты для MCPResultFormatter."""

    def test_format_markdown_empty(self, formatter):
        """Форматирование пустого ответа."""
        request = SearchRequest(
            vault_name="test",
            query="test",
        )
        response = SearchResponse(
            request=request,
            detected_intent=SearchIntent.SEMANTIC,
            intent_confidence=0.9,
            results=[],
            total_found=0,
            execution_time_ms=10.0,
            has_more=False,
            strategy_used="chunk_level",
            filters_applied={},
        )
        
        markdown = formatter.format_markdown(response)
        
        assert "Результаты поиска" in markdown
        assert "Результаты не найдены" in markdown

    def test_format_markdown_with_results(self, formatter, sample_search_response):
        """Форматирование ответа с результатами."""
        markdown = formatter.format_markdown(sample_search_response)
        
        assert "Результаты поиска" in markdown
        assert "python programming" in markdown
        assert "Test File" in markdown
        assert "test::file.md" in markdown or "file.md" in markdown

    def test_format_markdown_intent_labels(self, formatter, sample_document):
        """Проверка меток intent в markdown."""
        intents = [
            SearchIntent.METADATA_FILTER,
            SearchIntent.KNOWN_ITEM,
            SearchIntent.SEMANTIC,
            SearchIntent.EXPLORATORY,
            SearchIntent.PROCEDURAL,
        ]
        
        for intent in intents:
            result = DocumentSearchResult(
                document=sample_document,
                score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
                matched_chunks=[],
                matched_sections=[],
            )
            
            request = SearchRequest(vault_name="test", query="test")
            response = SearchResponse(
                request=request,
                detected_intent=intent,
                intent_confidence=0.9,
                results=[result],
                total_found=1,
                execution_time_ms=10.0,
                has_more=False,
                strategy_used="chunk_level",
                filters_applied={},
            )
            
            markdown = formatter.format_markdown(response)
            assert intent.value in markdown or formatter.INTENT_LABELS[intent] in markdown

    def test_format_json(self, formatter, sample_search_response):
        """Форматирование в JSON."""
        json_data = formatter.format_json(sample_search_response)
        
        assert "query" in json_data
        assert "intent" in json_data
        assert "results" in json_data
        assert json_data["query"] == "python programming"
        assert json_data["intent"] == SearchIntent.SEMANTIC.value
        assert len(json_data["results"]) == 1

    def test_format_json_result_structure(self, formatter, sample_search_response):
        """Структура результата в JSON."""
        json_data = formatter.format_json(sample_search_response)
        result = json_data["results"][0]
        
        assert "documentId" in result
        assert "title" in result
        assert "relevance" in result
        assert "matchType" in result
        assert result["documentId"] == "test::file.md"
        assert result["title"] == "Test File"
        assert result["relevance"] == 0.85

    def test_score_label_high(self, formatter):
        """Метка для высокой релевантности."""
        score = RelevanceScore(value=0.95, match_type=MatchType.SEMANTIC)
        label = formatter._score_label(score)
        assert "Высокая" in label or "🟢" in label

    def test_score_label_medium(self, formatter):
        """Метка для средней релевантности."""
        score = RelevanceScore(value=0.75, match_type=MatchType.SEMANTIC)
        label = formatter._score_label(score)
        assert "Средняя" in label or "🟡" in label

    def test_score_label_low(self, formatter):
        """Метка для низкой релевантности."""
        score = RelevanceScore(value=0.55, match_type=MatchType.SEMANTIC)
        label = formatter._score_label(score)
        assert "Низкая" in label or "🟠" in label

    def test_score_label_minimal(self, formatter):
        """Метка для минимальной релевантности."""
        score = RelevanceScore(value=0.3, match_type=MatchType.SEMANTIC)
        label = formatter._score_label(score)
        assert "Минимальная" in label or "🔴" in label

    def test_format_result_with_snippet(self, formatter, sample_document):
        """Форматирование результата со snippet."""
        result = DocumentSearchResult(
            document=sample_document,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
            matched_chunks=[],
            matched_sections=[],
        )
        
        lines = formatter._format_result(1, result)
        markdown = "\n".join(lines)
        
        assert "Test File" in markdown
        assert "obsidian://" in markdown

    def test_format_result_with_sections(self, formatter, sample_document):
        """Форматирование результата с секциями."""
        result = DocumentSearchResult(
            document=sample_document,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
            matched_chunks=[],
            matched_sections=["Introduction", "Main", "Conclusion"],
        )
        
        lines = formatter._format_result(1, result)
        markdown = "\n".join(lines)
        
        assert "Секции" in markdown
        assert "Introduction" in markdown

    def test_format_result_with_tags(self, formatter, sample_document):
        """Форматирование результата с тегами."""
        result = DocumentSearchResult(
            document=sample_document,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
            matched_chunks=[],
            matched_sections=[],
        )
        
        lines = formatter._format_result(1, result)
        markdown = "\n".join(lines)
        
        assert "Теги" in markdown
        assert "python" in markdown or "#python" in markdown

    def test_format_result_match_type(self, formatter, sample_document):
        """Форматирование с указанием типа совпадения."""
        result = DocumentSearchResult(
            document=sample_document,
            score=RelevanceScore(value=1.0, match_type=MatchType.EXACT_METADATA),
            matched_chunks=[],
            matched_sections=[],
        )
        
        lines = formatter._format_result(1, result)
        markdown = "\n".join(lines)
        
        assert "Точное совпадение" in markdown or "exact" in markdown.lower()

