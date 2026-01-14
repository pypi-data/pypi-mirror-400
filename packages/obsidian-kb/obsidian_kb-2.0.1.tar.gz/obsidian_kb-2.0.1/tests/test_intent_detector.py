"""Unit-тесты для IntentDetector."""

import pytest

from obsidian_kb.search.intent_detector import IntentDetector
from obsidian_kb.types import RetrievalGranularity, SearchIntent


@pytest.fixture
def intent_detector():
    """IntentDetector для тестов."""
    return IntentDetector()


class TestIntentDetector:
    """Тесты для IntentDetector."""

    def test_detect_metadata_filter_only(self, intent_detector):
        """Определение METADATA_FILTER для запроса только с фильтрами."""
        result = intent_detector.detect("", {"tags": ["python"]})
        assert result.intent == SearchIntent.METADATA_FILTER
        assert result.confidence >= 0.7
        assert result.recommended_granularity == RetrievalGranularity.DOCUMENT

    def test_detect_known_item_file_name(self, intent_detector):
        """Определение KNOWN_ITEM для имени файла."""
        result = intent_detector.detect("README.md", {})
        assert result.intent == SearchIntent.KNOWN_ITEM
        assert result.confidence >= 0.7
        assert result.recommended_granularity == RetrievalGranularity.DOCUMENT

    def test_detect_known_item_changelog(self, intent_detector):
        """Определение KNOWN_ITEM для CHANGELOG."""
        result = intent_detector.detect("CHANGELOG", {})
        assert result.intent == SearchIntent.KNOWN_ITEM
        assert result.confidence >= 0.7

    def test_detect_procedural_how_to(self, intent_detector):
        """Определение PROCEDURAL для how-to запросов."""
        result = intent_detector.detect("how to install python", {})
        assert result.intent == SearchIntent.PROCEDURAL
        assert result.confidence >= 0.7
        assert result.recommended_granularity == RetrievalGranularity.DOCUMENT

    def test_detect_procedural_kak(self, intent_detector):
        """Определение PROCEDURAL для запросов на русском."""
        result = intent_detector.detect("как установить python", {})
        assert result.intent == SearchIntent.PROCEDURAL
        assert result.confidence >= 0.7

    def test_detect_exploratory_question(self, intent_detector):
        """Определение EXPLORATORY для вопросов."""
        result = intent_detector.detect("what is python", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.7
        assert result.recommended_granularity == RetrievalGranularity.CHUNK

    def test_detect_exploratory_russian(self, intent_detector):
        """Определение EXPLORATORY для вопросов на русском."""
        result = intent_detector.detect("что такое python", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.7

    def test_detect_semantic_default(self, intent_detector):
        """Определение SEMANTIC как значение по умолчанию."""
        result = intent_detector.detect("python async programming", {})
        assert result.intent == SearchIntent.SEMANTIC
        assert result.confidence >= 0.5
        assert result.recommended_granularity == RetrievalGranularity.CHUNK

    def test_detect_with_filters_and_text(self, intent_detector):
        """Определение intent при наличии и текста, и фильтров."""
        result = intent_detector.detect("python programming", {"tags": ["async"]})
        # Должен быть SEMANTIC, так как есть текст
        assert result.intent == SearchIntent.SEMANTIC
        assert "has_filters" in result.signals

    def test_detect_priority_order(self, intent_detector):
        """Проверка приоритета определения intent."""
        # METADATA_FILTER должен иметь приоритет над SEMANTIC
        result1 = intent_detector.detect("", {"tags": ["python"]})
        assert result1.intent == SearchIntent.METADATA_FILTER
        
        # KNOWN_ITEM должен иметь приоритет над SEMANTIC
        result2 = intent_detector.detect("README.md", {})
        assert result2.intent == SearchIntent.KNOWN_ITEM
        
        # PROCEDURAL должен иметь приоритет над SEMANTIC
        result3 = intent_detector.detect("how to do something", {})
        assert result3.intent == SearchIntent.PROCEDURAL
        
        # EXPLORATORY должен иметь приоритет над SEMANTIC
        result4 = intent_detector.detect("what is something", {})
        assert result4.intent == SearchIntent.EXPLORATORY

    def test_signals_metadata_filter(self, intent_detector):
        """Проверка signals для METADATA_FILTER."""
        result = intent_detector.detect("", {"tags": ["python"]})
        assert "has_text" in result.signals
        assert "has_filters" in result.signals
        assert result.signals["has_text"] is False
        assert result.signals["has_filters"] is True

    def test_signals_semantic(self, intent_detector):
        """Проверка signals для SEMANTIC."""
        result = intent_detector.detect("python programming", {})
        assert "has_text" in result.signals
        assert result.signals["has_text"] is True

    def test_detect_known_item_id_pattern(self, intent_detector):
        """Определение KNOWN_ITEM для ID документов типа ADR-001."""
        result = intent_detector.detect("ADR-001", {})
        assert result.intent == SearchIntent.KNOWN_ITEM
        assert result.confidence >= 0.7
        assert result.recommended_granularity == RetrievalGranularity.DOCUMENT

    def test_detect_known_item_proj_id(self, intent_detector):
        """Определение KNOWN_ITEM для ID проектов."""
        result = intent_detector.detect("PROJ-123", {})
        assert result.intent == SearchIntent.KNOWN_ITEM
        assert result.confidence >= 0.7

    def test_detect_exploratory_chto_takoe(self, intent_detector):
        """Определение EXPLORATORY для 'что такое X'."""
        result = intent_detector.detect("что такое экосистема SMRM", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85  # Высокая уверенность для специфичного паттерна
        assert result.recommended_granularity == RetrievalGranularity.CHUNK

    def test_detect_exploratory_what_is(self, intent_detector):
        """Определение EXPLORATORY для 'what is X'."""
        result = intent_detector.detect("what is DDD", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_exploratory_pochemu(self, intent_detector):
        """Определение EXPLORATORY для 'почему X'."""
        result = intent_detector.detect("почему нужна интеграция", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_exploratory_kakie_problemy(self, intent_detector):
        """Определение EXPLORATORY для 'какие проблемы X'."""
        result = intent_detector.detect("какие проблемы с текущей архитектурой", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_procedural_kakie_shagi(self, intent_detector):
        """Определение PROCEDURAL для 'какие шаги'."""
        result = intent_detector.detect("какие шаги нужны для установки", {})
        assert result.intent == SearchIntent.PROCEDURAL
        assert result.confidence >= 0.7

    def test_detect_exploratory_vs_procedural(self, intent_detector):
        """Проверка приоритета EXPLORATORY над PROCEDURAL для 'какие проблемы'."""
        # "какие проблемы" должно быть EXPLORATORY, а не PROCEDURAL
        result = intent_detector.detect("какие проблемы с интеграцией", {})
        assert result.intent == SearchIntent.EXPLORATORY
        # "какие шаги" должно быть PROCEDURAL
        result2 = intent_detector.detect("какие шаги для настройки", {})
        assert result2.intent == SearchIntent.PROCEDURAL

    def test_detect_exploratory_kak_rabotaet(self, intent_detector):
        """Определение EXPLORATORY для 'как работает X'."""
        result = intent_detector.detect("как работает система", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_exploratory_how_does(self, intent_detector):
        """Определение EXPLORATORY для 'how does X work'."""
        result = intent_detector.detect("how does it work", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_exploratory_kak_vybrat(self, intent_detector):
        """Определение EXPLORATORY для 'как выбрать X'."""
        result = intent_detector.detect("как выбрать лучший вариант", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_exploratory_how_to_choose(self, intent_detector):
        """Определение EXPLORATORY для 'how to choose X'."""
        result = intent_detector.detect("how to choose the best option", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.85

    def test_detect_known_item_id_lowercase(self, intent_detector):
        """Определение KNOWN_ITEM для ID документов в нижнем регистре."""
        result = intent_detector.detect("adr-001", {})
        assert result.intent == SearchIntent.KNOWN_ITEM
        assert result.confidence >= 0.7

    def test_detect_known_item_id_mixed_case(self, intent_detector):
        """Определение KNOWN_ITEM для ID документов в смешанном регистре."""
        result = intent_detector.detect("Proj-123", {})
        assert result.intent == SearchIntent.KNOWN_ITEM
        assert result.confidence >= 0.7

    def test_detect_semantic_adr_shablon(self, intent_detector):
        """Проверка, что 'ADR шаблон' не попадает в KNOWN_ITEM.

        Note: 'шаблон' (template) - это procedural паттерн, поэтому
        'ADR шаблон' определяется как PROCEDURAL.
        """
        # "ADR шаблон" не должно быть KNOWN_ITEM, так как нет дефиса и цифр
        result = intent_detector.detect("ADR шаблон", {})
        assert result.intent != SearchIntent.KNOWN_ITEM
        # "шаблон" - это procedural паттерн
        assert result.intent == SearchIntent.PROCEDURAL

    def test_detect_procedural_kak_nastroit(self, intent_detector):
        """Проверка, что 'как настроить' остается PROCEDURAL."""
        result = intent_detector.detect("как настроить интеграцию", {})
        assert result.intent == SearchIntent.PROCEDURAL
        assert result.confidence >= 0.7

    def test_detect_exploratory_chto_takoe_critical(self, intent_detector):
        """Проверка критического паттерна 'что такое X' с ключевыми словами."""
        # Эти запросы должны быть EXPLORATORY независимо от ключевых слов
        test_cases = [
            "что такое экосистема SMRM",
            "что такое DDD",
            "что такое Python",
            "что такое архитектура",
        ]
        for query in test_cases:
            result = intent_detector.detect(query, {})
            assert result.intent == SearchIntent.EXPLORATORY, f"Failed for: {query}"
            assert result.confidence >= 0.90, f"Low confidence for: {query}"

    def test_detect_exploratory_zachem_critical(self, intent_detector):
        """Проверка критического паттерна 'зачем X'."""
        test_cases = [
            "зачем нужна централизация",
            "зачем нужна интеграция",
            "зачем использовать DDD",
        ]
        for query in test_cases:
            result = intent_detector.detect(query, {})
            assert result.intent == SearchIntent.EXPLORATORY, f"Failed for: {query}"
            assert result.confidence >= 0.90, f"Low confidence for: {query}"

    def test_detect_exploratory_v_chem_sut_critical(self, intent_detector):
        """Проверка критического паттерна 'в чём суть X'."""
        test_cases = [
            "в чём суть экосистемного подхода",
            "в чем суть микросервисов",  # альтернативное написание
            "в чём суть DDD",
        ]
        for query in test_cases:
            result = intent_detector.detect(query, {})
            assert result.intent == SearchIntent.EXPLORATORY, f"Failed for: {query}"
            assert result.confidence >= 0.90, f"Low confidence for: {query}"

    def test_detect_exploratory_critical_priority(self, intent_detector):
        """Проверка, что критические паттерны имеют приоритет над SEMANTIC."""
        # Даже если запрос содержит специфичные ключевые слова, критические паттерны должны работать
        result = intent_detector.detect("что такое экосистема SMRM", {})
        assert result.intent == SearchIntent.EXPLORATORY
        assert result.confidence >= 0.90
        assert "critical_pattern" in result.signals or "exploratory_pattern" in result.signals

