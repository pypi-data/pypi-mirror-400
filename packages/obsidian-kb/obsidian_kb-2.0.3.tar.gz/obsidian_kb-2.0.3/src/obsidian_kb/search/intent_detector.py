"""Детектор намерения поискового запроса."""

import logging
import re
from typing import Any

from obsidian_kb.types import IntentDetectionResult, RetrievalGranularity, SearchIntent

logger = logging.getLogger(__name__)


class IntentDetector:
    """Реализация IIntentDetector для определения intent запроса."""

    # Паттерны для known-item
    FILE_PATTERNS = [
        r'\b[\w-]+\.(md|pdf|txt)\b',  # Имена файлов с расширениями
        r'\b(README|CHANGELOG|LICENSE|TODO|CONTRIBUTING|INSTALLATION)\b',  # Стандартные файлы
    ]
    
    # Паттерн для ID документов (отдельно, так как требует особой обработки)
    ID_PATTERN = r'\b[A-Za-z]{2,}-\d+\b'  # ID документов: ADR-001, adr-001, PROJ-123, etc.
    
    # Паттерн для project-id (без расширения): smrm-ecosystem, project-name
    PROJECT_ID_PATTERN = r'^[a-z]+-[a-z]+$'  # project-id: smrm-ecosystem
    
    # Паттерн для ID людей (только строчные буквы): amuratov, ivanov
    PERSON_ID_PATTERN = r'^[a-z]+$'  # ID людей: amuratov, ivanov

    # Специфичные паттерны для exploratory запросов (высокий приоритет)
    # ВАЖНО: Более специфичные паттерны должны идти первыми
    EXPLORATORY_PATTERNS = [
        # Специфичные паттерны "how to" для exploratory (должны быть перед общим "how to" в PROCEDURAL)
        r'^how to choose\b',  # "how to choose X" (exploratory - выбор/сравнение)
        r'^как выбрать\b',  # "как выбрать X" (exploratory - выбор/сравнение)
        r'^как работает\b',  # "как работает X" (exploratory, не procedural)
        r'^how does\b',  # "how does X work" (exploratory)
        r'^how it works\b',  # "how it works" (exploratory)
        # Общие exploratory паттерны
        r'^почему\b',  # "почему X"
        r'^why\b',  # "why X"
        r'^какова цель\b',  # "какова цель X"
        r'^what is the purpose\b',  # "what is the purpose of X"
        r'^что означает\b',  # "что означает X"
        r'^what means\b',  # "what means X"
        r'^в чём смысл\b',  # "в чём смысл X"
        r'^в чем смысл\b',  # альтернативное написание
        r'^what is the meaning\b',  # "what is the meaning of X"
        r'^какие проблемы\b',  # "какие проблемы X"
        r'^what problems\b',  # "what problems with X"
        r'^какие риски\b',  # "какие риски X"
        r'^what risks\b',  # "what risks with X"
        r'^какие преимущества\b',  # "какие преимущества X"
        r'^what advantages\b',  # "what advantages of X"
    ]

    # Паттерны для procedural (how-to запросы)
    PROCEDURAL_PATTERNS = [
        r'^(how to|как|steps to|guide|tutorial|инструкция)',  # Начало запроса
        r'\b(настроить|установить|configure|setup|install|создать|make|build)\b',  # Действия
        r'\b(шаблон|template)\b',  # "шаблон для X", "template for X"
        r'\bкакие шаги\b',  # "какие шаги нужны"
        r'\bwhat steps\b',  # "what steps to"
        r'\bкакие действия\b',  # "какие действия"
        r'\bwhat actions\b',  # "what actions"
        r'\bкакие этапы\b',  # "какие этапы"
        r'\bwhat stages\b',  # "what stages"
    ]

    # Вопросительные слова для exploratory запросов (низкий приоритет, fallback)
    QUESTION_WORDS = {
        'что', 'как', 'почему', 'когда', 'где', 'кто', 'какой', 'сколько', 'зачем',
        'what', 'how', 'why', 'when', 'where', 'who', 'which', 'how many', 'how much',
    }

    def detect(
        self,
        query: str,
        parsed_filters: dict[str, Any],
        text_query: str | None = None,
    ) -> IntentDetectionResult:
        """Определение intent на основе запроса и фильтров.
        
        Args:
            query: Исходный текстовый запрос (ВАЖНО: должен быть исходным, до нормализации)
            parsed_filters: Извлечённые фильтры (tags, type, dates, etc.)
            text_query: Распарсенный текстовый запрос (без фильтров). Если None, используется query.
            
        Returns:
            IntentDetectionResult с определённым intent и confidence
        """
        signals: dict[str, Any] = {}
        
        # Для METADATA_FILTER проверяем text_query (распарсенный текст без фильтров)
        # Для паттернов (EXPLORATORY, KNOWN_ITEM) используем исходный query
        if text_query is not None:
            has_text_for_metadata = bool(text_query and text_query.strip())
        else:
            # Fallback: если text_query не передан, используем query
            has_text_for_metadata = bool(query and query.strip())
        
        has_text_for_patterns = bool(query and query.strip())
        has_filters = self._has_filters(parsed_filters)
        
        signals['has_text'] = has_text_for_patterns
        signals['has_text_for_metadata'] = has_text_for_metadata
        signals['has_filters'] = has_filters
        signals['query_length'] = len(query) if query else 0
        
        # Логируем для отладки (только если включен DEBUG уровень)
        logger.debug(f"Intent detection: query='{query[:100]}', text_query='{text_query[:100] if text_query else None}', has_text_for_metadata={has_text_for_metadata}, has_filters={has_filters}")
        
        # 1. METADATA_FILTER: только фильтры, без текста (проверяем text_query!)
        if has_filters and not has_text_for_metadata:
            return IntentDetectionResult(
                intent=SearchIntent.METADATA_FILTER,
                confidence=0.95,
                signals=signals,
                recommended_granularity=RetrievalGranularity.DOCUMENT,
            )
        
        # 2. KNOWN_ITEM: ссылка на конкретный файл
        # Проверяем паттерны файлов и ID документов (используем исходный query для паттернов)
        query_lower = query.lower().strip()
        file_match = (
            any(re.search(p, query, re.IGNORECASE) for p in self.FILE_PATTERNS) or
            re.search(self.ID_PATTERN, query) or
            re.search(self.PROJECT_ID_PATTERN, query_lower) or
            re.search(self.PERSON_ID_PATTERN, query_lower)
        )
        
        if has_text_for_patterns and file_match:
            signals['file_reference'] = True
            # Определяем тип known-item для более точного confidence
            if re.search(self.PERSON_ID_PATTERN, query_lower):
                signals['person_id'] = True
                confidence = 0.85  # Немного ниже, так как может быть семантический запрос
            elif re.search(self.PROJECT_ID_PATTERN, query_lower):
                signals['project_id'] = True
                confidence = 0.90
            else:
                confidence = 0.90
            
            return IntentDetectionResult(
                intent=SearchIntent.KNOWN_ITEM,
                confidence=confidence,
                signals=signals,
                recommended_granularity=RetrievalGranularity.DOCUMENT,
            )
        
        # 3. EXPLORATORY: специфичные exploratory паттерны (высокий приоритет)
        # Критические паттерны проверяются первыми с максимальным приоритетом
        query_lower = query.lower().strip()
        
        # Критические exploratory триггеры (обязательные, независимо от других слов)
        critical_exploratory_patterns = [
            r'^что такое\b',
            r'^what is\b',
            r'^зачем\b',
            r'^what for\b',
            r'^в чём суть\b',
            r'^what is the essence\b',
            r'^в чем суть\b',  # альтернативное написание
        ]
        
        # Проверяем критические паттерны первыми
        for pattern in critical_exploratory_patterns:
            if re.search(pattern, query_lower):
                signals['exploratory_pattern'] = True
                signals['critical_pattern'] = pattern
                return IntentDetectionResult(
                    intent=SearchIntent.EXPLORATORY,
                    confidence=0.95,  # Максимальная уверенность для критических паттернов
                    signals=signals,
                    recommended_granularity=RetrievalGranularity.CHUNK,
                )
        
        # Остальные exploratory паттерны (используем исходный query для паттернов)
        if has_text_for_patterns and any(re.search(p, query_lower) for p in self.EXPLORATORY_PATTERNS):
            signals['exploratory_pattern'] = True
            return IntentDetectionResult(
                intent=SearchIntent.EXPLORATORY,
                confidence=0.90,  # Повышенная уверенность для специфичных паттернов
                signals=signals,
                recommended_granularity=RetrievalGranularity.CHUNK,
            )
        
        # 4. PROCEDURAL: how-to запросы (проверяется после EXPLORATORY)
        if has_text_for_patterns and any(re.search(p, query, re.IGNORECASE) for p in self.PROCEDURAL_PATTERNS):
            signals['procedural_pattern'] = True
            return IntentDetectionResult(
                intent=SearchIntent.PROCEDURAL,
                confidence=0.85,
                signals=signals,
                recommended_granularity=RetrievalGranularity.DOCUMENT,
            )
        
        # 5. EXPLORATORY: общие вопросительные слова (fallback)
        if has_text_for_patterns:
            first_word = query.split()[0].lower() if query.split() else ""
            # Исключаем "как" из EXPLORATORY, так как оно обрабатывается в PROCEDURAL
            exploratory_words = self.QUESTION_WORDS - {'как', 'how'}
            if first_word in exploratory_words:
                signals['question'] = True
                return IntentDetectionResult(
                    intent=SearchIntent.EXPLORATORY,
                    confidence=0.80,
                    signals=signals,
                    recommended_granularity=RetrievalGranularity.CHUNK,
                )
        
        # 6. SEMANTIC: текстовый поиск по умолчанию
        return IntentDetectionResult(
            intent=SearchIntent.SEMANTIC,
            confidence=0.75 if has_text_for_patterns else 0.50,
            signals=signals,
            recommended_granularity=RetrievalGranularity.CHUNK,
        )

    def _has_filters(self, parsed_filters: dict[str, Any]) -> bool:
        """Проверка наличия фильтров в parsed_filters.
        
        Args:
            parsed_filters: Словарь с фильтрами (может быть ParsedQuery или dict)
            
        Returns:
            True если есть хотя бы один фильтр
        """
        if not parsed_filters:
            return False
        
        # Если это ParsedQuery объект, используем метод has_filters()
        if hasattr(parsed_filters, 'has_filters'):
            return parsed_filters.has_filters()
        
        # Если это словарь, проверяем наличие ключей фильтров
        filter_keys = {
            'tags', 'tags_or', 'tags_not',
            'inline_tags', 'inline_tags_or', 'inline_tags_not',
            'date_filters', 'doc_type', 'doc_type_or', 'doc_type_not',
            'links', 'links_or', 'links_not',
        }
        
        return any(
            key in parsed_filters and parsed_filters[key]
            for key in filter_keys
        )

