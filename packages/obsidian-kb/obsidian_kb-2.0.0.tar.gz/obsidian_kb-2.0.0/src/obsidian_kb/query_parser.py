"""Модуль для парсинга расширенных поисковых запросов."""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from obsidian_kb.filters import FilterBuilder
from obsidian_kb.normalization import DataNormalizer
from obsidian_kb.relative_date_parser import RelativeDateParser

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IDatabaseManager

logger = logging.getLogger(__name__)


class QueryNormalizer:
    """Нормализация поисковых запросов: стоп-слова, синонимы, lowercase."""
    
    # Стоп-слова (русские и английские)
    STOP_WORDS = {
        # Русские
        "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "об", "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между",
        # Английские
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "will", "with", "the", "this", "but", "they", "have", "had", "what", "said", "each", "which", "their", "time", "if", "up", "out", "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "into", "him", "has", "two", "more", "very", "after", "words", "long", "than", "first", "been", "call", "who", "oil", "sit", "now", "find", "down", "day", "did", "get", "come", "made", "may", "part", "over", "new", "sound", "take", "only", "little", "work", "know", "place", "year", "live", "me", "back", "give", "most", "very", "after", "thing", "our", "just", "name", "good", "sentence", "man", "think", "say", "great", "where", "help", "through", "much", "before", "line", "right", "too", "mean", "old", "any", "same", "tell", "boy", "follow", "came", "want", "show", "also", "around", "form", "three", "small", "set", "put", "end", "does", "another", "well", "large", "must", "big", "even", "such", "because", "turn", "here", "why", "ask", "went", "men", "read", "need", "land", "different", "home", "us", "move", "try", "kind", "hand", "picture", "again", "change", "off", "play", "spell", "air", "away", "animal", "house", "point", "page", "letter", "mother", "answer", "found", "study", "still", "learn", "should", "America", "world", "high", "every", "near", "add", "food", "between", "own", "below", "country", "plant", "last", "school", "father", "keep", "tree", "never", "start", "city", "earth", "eye", "light", "thought", "head", "under", "story", "saw", "left", "don't", "few", "while", "along", "might", "close", "something", "seem", "next", "hard", "open", "example", "begin", "life", "always", "those", "both", "paper", "together", "got", "group", "often", "run", "important", "until", "children", "side", "feet", "car", "mile", "night", "walk", "white", "sea", "began", "grow", "took", "river", "four", "carry", "state", "once", "book", "hear", "stop", "without", "second", "later", "miss", "idea", "enough", "eat", "face", "watch", "far", "indian", "real", "almost", "let", "above", "girl", "sometimes", "mountain", "cut", "young", "talk", "soon", "list", "song", "leave", "family", "it's"
    }
    
    # Базовый словарь синонимов (можно расширить)
    SYNONYMS = {
        # Русские
        "проблема": ["ошибка", "баг", "issue", "проблемы"],
        "ошибка": ["проблема", "баг", "issue", "error"],
        "баг": ["ошибка", "проблема", "issue", "bug"],
        "производительность": ["performance", "скорость", "быстродействие"],
        "скорость": ["производительность", "performance", "быстродействие"],
        "установка": ["инсталляция", "installation", "setup"],
        "настройка": ["конфигурация", "configuration", "config", "setup"],
        "документация": ["docs", "документы", "руководство"],
        "руководство": ["документация", "docs", "manual", "guide"],
        # Английские
        "problem": ["issue", "error", "bug", "проблема"],
        "error": ["problem", "issue", "bug", "ошибка"],
        "bug": ["error", "problem", "issue", "баг"],
        "performance": ["speed", "производительность", "скорость"],
        "speed": ["performance", "производительность", "скорость"],
        "installation": ["setup", "install", "установка"],
        "configuration": ["config", "setup", "настройка"],
        "documentation": ["docs", "документация"],
        "guide": ["manual", "руководство", "документация"],
    }
    
    @classmethod
    def normalize(cls, query: str) -> str:
        """Нормализация запроса: lowercase, удаление стоп-слов, расширение синонимами.
        
        Args:
            query: Исходный запрос
            
        Returns:
            Нормализованный запрос
        """
        if not query:
            return ""
        
        # Приводим к lowercase
        normalized = query.lower().strip()
        
        # Удаляем лишние пробелы
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Разбиваем на слова
        words = normalized.split()
        
        # Удаляем стоп-слова (но сохраняем важные слова)
        filtered_words = [w for w in words if w not in cls.STOP_WORDS]
        
        # Если после удаления стоп-слов ничего не осталось, возвращаем исходный запрос
        if not filtered_words:
            return normalized
        
        # Расширяем синонимами (добавляем первые 2 синонима для каждого слова)
        expanded_words = []
        for word in filtered_words:
            expanded_words.append(word)
            # Ищем синонимы
            if word in cls.SYNONYMS:
                synonyms = cls.SYNONYMS[word]
                # Добавляем первые 2 синонима, которых ещё нет в запросе
                added = 0
                for synonym in synonyms:
                    if synonym not in expanded_words and synonym not in filtered_words and added < 2:
                        expanded_words.append(synonym)
                        added += 1
        
        return ' '.join(expanded_words)
    
    @classmethod
    def remove_stop_words(cls, query: str) -> str:
        """Удаление стоп-слов из запроса.
        
        Args:
            query: Исходный запрос
            
        Returns:
            Запрос без стоп-слов
        """
        if not query:
            return ""
        
        words = query.lower().split()
        filtered = [w for w in words if w not in cls.STOP_WORDS]
        return ' '.join(filtered) if filtered else query
    
    @classmethod
    def expand_synonyms(cls, query: str, max_expansions: int = 2) -> str:
        """Расширение запроса синонимами.
        
        Args:
            query: Исходный запрос
            max_expansions: Максимальное количество синонимов на слово
            
        Returns:
            Расширенный запрос
        """
        if not query:
            return ""
        
        words = query.lower().split()
        expanded = []
        
        for word in words:
            expanded.append(word)
            if word in cls.SYNONYMS:
                synonyms = cls.SYNONYMS[word]
                added = 0
                for synonym in synonyms:
                    if synonym not in expanded and added < max_expansions:
                        expanded.append(synonym)
                        added += 1
        
        return ' '.join(expanded)


@dataclass
class FilterGroup:
    """Группа фильтров с оператором."""
    tags: list[str] | None = None
    links: list[str] | None = None
    doc_type: str | None = None
    operator: str = "AND"  # "AND" | "OR"
    negated: bool = False  # Для NOT


@dataclass
class ParsedQuery:
    """Распарсенный поисковый запрос."""
    
    text_query: str  # Основной текстовый запрос
    tags: list[str] | None = None  # Теги из frontmatter для фильтрации (AND по умолчанию)
    tags_or: list[str] | None = None  # Теги из frontmatter для OR фильтрации
    tags_not: list[str] | None = None  # Теги из frontmatter для исключения (NOT)
    inline_tags: list[str] | None = None  # Inline теги (#tag) для фильтрации
    inline_tags_or: list[str] | None = None  # Inline теги для OR фильтрации
    inline_tags_not: list[str] | None = None  # Inline теги для исключения (NOT)
    date_filters: dict[str, dict[str, datetime]] | None = None  # Фильтры по датам: {"created": {"op": ">=", "value": datetime}}
    doc_type: str | None = None  # Тип документа для фильтрации
    doc_type_or: list[str] | None = None  # Типы документов для OR фильтрации
    doc_type_not: str | None = None  # Тип документа для исключения (NOT)
    links: list[str] | None = None  # Связанные заметки (wikilinks) для фильтрации
    links_or: list[str] | None = None  # Links для OR фильтрации
    links_not: list[str] | None = None  # Links для исключения (NOT)
    
    def has_filters(self) -> bool:
        """Проверка наличия фильтров."""
        return (
            self.tags is not None
            or self.tags_or is not None
            or self.tags_not is not None
            or self.inline_tags is not None
            or self.inline_tags_or is not None
            or self.inline_tags_not is not None
            or self.date_filters is not None
            or self.doc_type is not None
            or self.doc_type_or is not None
            or self.doc_type_not is not None
            or self.links is not None
            or self.links_or is not None
            or self.links_not is not None
        )


class QueryParser:
    """Парсер расширенных поисковых запросов."""
    
    # Паттерны для парсинга
    # Паттерн для тегов из frontmatter: tags: или tag: за которым следует список тегов
    # Используем non-greedy match до следующего фильтра или конца строки
    # Для tags и links поддерживаем множественные значения через пробел (tags:python javascript)
    # Разделение на значения и текст запроса происходит при парсинге через проверку последнего слова
    # Важно: negative lookbehind для исключения #tags: (inline теги обрабатываются отдельно)
    TAG_PATTERN = re.compile(r'(?<!#)tags?:\s*([^:]+?)(?=\s+(?:tags?|#tags?|links?|type|created|modified):|$)', re.IGNORECASE)
    # Паттерн для inline тегов: #tags: или #tag: за которым следует список тегов
    INLINE_TAG_PATTERN = re.compile(r'#tags?:\s*([^:]+?)(?=\s+(?:tags?|#tags?|links?|type|created|modified):|$)', re.IGNORECASE)
    # Паттерн для links: links: или link: за которым следует список связанных заметок
    LINK_PATTERN = re.compile(r'links?:\s*([^:]+?)(?=\s+(?:tags?|#tags?|links?|type|created|modified):|$)', re.IGNORECASE)
    DATE_PATTERN = re.compile(
        r'(created|modified):\s*(>=|<=|>|<|=)?\s*(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?)',
        re.IGNORECASE
    )
    # Поддержка значений с пробелами, дефисами и другими символами
    # Примеры: type:person, type: person, type:1-1, type:adr
    # Используем non-greedy match до следующего фильтра, пробела (если следующий токен не фильтр) или конца строки
    # Важно: останавливаемся на пробеле, если после него нет фильтра, чтобы не захватывать текст запроса
    TYPE_PATTERN = re.compile(r'type:\s*([^\s:]+?)(?=\s+(?:tags?|links?|type|created|modified):|\s|$)', re.IGNORECASE)
    
    @classmethod
    def _remove_pattern_from_text(cls, text: str, pattern: re.Pattern, match_obj: re.Match, preserve_trailing_text: str | None = None) -> str:
        """Удаление найденного паттерна из текста.
        
        Args:
            text: Исходный текст
            pattern: Паттерн для поиска
            match_obj: Найденное совпадение
            preserve_trailing_text: Текст после паттерна, который нужно сохранить в text_query
        """
        start, end = match_obj.span()
        # Удаляем паттерн и окружающие пробелы
        before = text[:start].rstrip()
        after = text[end:].lstrip()
        
        # Если нужно сохранить часть текста после паттерна (текст запроса, отделенный от значения фильтра)
        if preserve_trailing_text:
            # Сохраняем отделенный текст запроса
            result = f"{before} {preserve_trailing_text} {after}".strip()
        else:
            result = f"{before} {after}".strip()
        
        return result
    
    @classmethod
    def parse(cls, query: str) -> ParsedQuery:
        """Парсинг поискового запроса.
        
        Args:
            query: Исходный запрос
            
        Returns:
            ParsedQuery с распарсенными компонентами
            
        Examples:
            >>> parser = QueryParser()
            >>> result = parser.parse("Python async tags:python async")
            >>> result.text_query
            'Python async'
            >>> result.tags
            ['python', 'async']
            
            >>> result = parser.parse("created:2024-01-01 modified:>2024-12-01")
            >>> result.date_filters['created']['op']
            '='
            >>> result.date_filters['modified']['op']
            '>'
            
            >>> result = parser.parse("tags:python OR tags:javascript")
            >>> result.tags_or
            ['javascript']
        """
        text_query = query
        tags: list[str] | None = None
        tags_or: list[str] | None = None
        tags_not: list[str] | None = None
        inline_tags: list[str] | None = None
        inline_tags_or: list[str] | None = None
        inline_tags_not: list[str] | None = None
        date_filters: dict[str, dict[str, Any]] | None = None
        doc_type: str | None = None
        doc_type_or: list[str] | None = None
        doc_type_not: str | None = None
        links: list[str] | None = None
        links_or: list[str] | None = None
        links_not: list[str] | None = None
        
        # Парсинг тегов с OR оператором: tags:python OR tags:javascript (сначала OR, чтобы исключить их из обычных)
        # Используем тот же подход, что и для обычных тегов - lookahead до следующего фильтра
        or_tag_pattern = re.compile(r'\s+OR\s+tags?:\s*([^:]+?)(?=\s+(?:OR\s+)?(?:NOT\s+)?(?:tags?|links?|type|created|modified):|$)', re.IGNORECASE)
        or_matches = list(or_tag_pattern.finditer(query))
        if or_matches:
            all_tags_or = []
            for match in or_matches:
                tags_str = match.group(1).strip()
                split_tags = re.split(r'[\s,]+', tags_str)
                all_tags_or.extend([DataNormalizer.normalize_tag(tag) for tag in split_tags 
                                  if tag.strip() and not tag.startswith('tags:') and tag.lower() not in ('or', 'not')])
            
            if all_tags_or:
                tags_or = DataNormalizer.normalize_tags(all_tags_or)
                # Удаляем OR теги из исходного query (сохраняем индексы)
                for match in reversed(or_matches):
                    text_query = cls._remove_pattern_from_text(text_query, or_tag_pattern, match)
                # Удаляем OR операторы
                text_query = re.sub(r'\s+OR\s+', ' ', text_query, flags=re.IGNORECASE)
        
        # Парсинг тегов с NOT оператором: tags:python NOT tags:deprecated
        # Используем тот же подход, что и для обычных тегов - lookahead до следующего фильтра
        # Ищем в исходном query, но удаляем из text_query
        not_tag_pattern = re.compile(r'\s+NOT\s+tags?:\s*([^:]+?)(?=\s+(?:NOT\s+)?(?:OR\s+)?(?:tags?|links?|type|created|modified):|$)', re.IGNORECASE)
        not_matches = list(not_tag_pattern.finditer(query))
        if not_matches:
            all_tags_not = []
            for match in not_matches:
                tags_str = match.group(1).strip()
                split_tags = re.split(r'[\s,]+', tags_str)
                all_tags_not.extend([DataNormalizer.normalize_tag(tag) for tag in split_tags 
                                    if tag.strip() and not tag.startswith('tags:') and tag.lower() not in ('not', 'or')])
            
            if all_tags_not:
                tags_not = DataNormalizer.normalize_tags(all_tags_not)
                # Удаляем NOT теги из text_query (который уже был изменен после OR)
                # Используем простую замену строки, так как паттерн уже найден
                for match in reversed(not_matches):
                    # Находим соответствующий блок в text_query
                    not_text = match.group(0)  # " NOT tags:deprecated"
                    if not_text in text_query:
                        text_query = text_query.replace(not_text, '', 1).strip()
                # Удаляем оставшиеся NOT операторы
                text_query = re.sub(r'\s+NOT\s+', ' ', text_query, flags=re.IGNORECASE)
        
        # Парсинг тегов (обычные, AND по умолчанию) - после удаления OR и NOT из text_query
        tag_matches = list(cls.TAG_PATTERN.finditer(text_query))
        if tag_matches:
            all_tags = []
            preserved_texts = {}  # Сохраняем текст запроса для каждого match
            for idx, match in enumerate(tag_matches):
                tags_str = match.group(1).strip()
                split_tags = re.split(r'[\s,]+', tags_str)
                
                # Проверяем последнее слово: если оно начинается с заглавной или содержит кириллицу,
                # это текст запроса, а не часть значения фильтра
                preserved_text = None
                if len(split_tags) > 1:
                    last_word = split_tags[-1]
                    # Проверка: начинается с заглавной или содержит кириллицу
                    is_text_query = (
                        last_word[0].isupper() if last_word else False
                    ) or any('\u0400' <= c <= '\u04FF' for c in last_word)
                    
                    if is_text_query:
                        # Последнее слово - это текст запроса, не тег
                        # Сохраняем все слова после первого, которые выглядят как текст запроса
                        text_words = []
                        for i in range(len(split_tags) - 1, -1, -1):
                            word = split_tags[i]
                            word_is_text = (
                                word[0].isupper() if word else False
                            ) or any('\u0400' <= c <= '\u04FF' for c in word)
                            if word_is_text:
                                text_words.insert(0, word)
                                split_tags = split_tags[:-1]
                            else:
                                break
                        if text_words:
                            preserved_text = ' '.join(text_words)
                            preserved_texts[idx] = preserved_text
                
                all_tags.extend([DataNormalizer.normalize_tag(tag) for tag in split_tags 
                                if tag.strip() and not tag.startswith('tags:')])
            
            if all_tags:
                tags = DataNormalizer.normalize_tags(all_tags)
                for idx, match in enumerate(reversed(tag_matches)):
                    preserved_text = preserved_texts.get(len(tag_matches) - 1 - idx)
                    text_query = cls._remove_pattern_from_text(text_query, cls.TAG_PATTERN, match, preserve_trailing_text=preserved_text)
        
        # Парсинг inline тегов (#tags:)
        inline_tag_matches = list(cls.INLINE_TAG_PATTERN.finditer(text_query))
        if inline_tag_matches:
            all_inline_tags = []
            preserved_texts = {}
            for idx, match in enumerate(inline_tag_matches):
                tags_str = match.group(1).strip()
                split_tags = re.split(r'[\s,]+', tags_str)
                
                # Проверяем последнее слово: если оно начинается с заглавной или содержит кириллицу,
                # это текст запроса, а не часть значения фильтра
                preserved_text = None
                if len(split_tags) > 1:
                    last_word = split_tags[-1]
                    is_text_query = (
                        last_word[0].isupper() if last_word else False
                    ) or any('\u0400' <= c <= '\u04FF' for c in last_word)
                    
                    if is_text_query:
                        # Сохраняем все слова после первого, которые выглядят как текст запроса
                        text_words = []
                        for i in range(len(split_tags) - 1, -1, -1):
                            word = split_tags[i]
                            word_is_text = (
                                word[0].isupper() if word else False
                            ) or any('\u0400' <= c <= '\u04FF' for c in word)
                            if word_is_text:
                                text_words.insert(0, word)
                                split_tags = split_tags[:-1]
                            else:
                                break
                        if text_words:
                            preserved_text = ' '.join(text_words)
                            preserved_texts[idx] = preserved_text
                
                all_inline_tags.extend([DataNormalizer.normalize_tag(tag) for tag in split_tags 
                                       if tag.strip() and not tag.startswith('#tags:')])
            
            if all_inline_tags:
                inline_tags = DataNormalizer.normalize_tags(all_inline_tags)
                for idx, match in enumerate(reversed(inline_tag_matches)):
                    preserved_text = preserved_texts.get(len(inline_tag_matches) - 1 - idx)
                    text_query = cls._remove_pattern_from_text(text_query, cls.INLINE_TAG_PATTERN, match, preserve_trailing_text=preserved_text)
        
        # Парсинг дат
        date_matches = list(cls.DATE_PATTERN.finditer(query))
        if date_matches:
            date_filters = {}
            for match in date_matches:
                field = match.group(1).lower()
                op = match.group(2) or '='  # По умолчанию равенство
                op = op.strip() if op else '='
                date_str = match.group(3)
                
                try:
                    # Проверяем, является ли дата относительной
                    if RelativeDateParser.is_relative_date(date_str):
                        # Парсим относительную дату
                        date_value = RelativeDateParser.parse_relative_date(date_str)
                        if date_value is None:
                            logger.warning(f"Failed to parse relative date '{date_str}'")
                            continue
                    else:
                        # Парсим абсолютную дату (ISO формат)
                        if ' ' in date_str:
                            # С датой и временем
                            date_value = datetime.fromisoformat(date_str.replace(' ', 'T'))
                        else:
                            # Только дата
                            date_value = datetime.fromisoformat(date_str)
                    
                    # Поддержка множественных фильтров для одного поля (например, created:>=2024-12-01 created:<=2024-12-31)
                    if field not in date_filters:
                        date_filters[field] = []
                    
                    date_filters[field].append({
                        'op': op,
                        'value': date_value
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse date '{date_str}': {e}")
                    continue
            
            # Удаляем все фильтры дат из текстового запроса (в обратном порядке, чтобы сохранить индексы)
            for match in reversed(date_matches):
                text_query = cls._remove_pattern_from_text(text_query, cls.DATE_PATTERN, match)
            
            # Очищаем пробелы в начале и конце
            text_query = text_query.strip()
            
            # Нормализуем date_filters: конвертируем списки в единый формат с after/before
            normalized_date_filters = {}
            for field, conditions_list in date_filters.items():
                if isinstance(conditions_list, list):
                    # Обрабатываем список условий
                    after = None
                    before = None
                    after_exclusive = False  # True если был оператор >
                    before_exclusive = False  # True если был оператор <
                    for condition in conditions_list:
                        op = condition.get('op', '=')
                        value = condition.get('value')
                        if op in ['>', '>=']:
                            if after is None or (op == '>' and value > after) or (op == '>=' and value >= after):
                                after = value
                                after_exclusive = (op == '>')  # Сохраняем информацию о строгости
                        elif op in ['<', '<=']:
                            if before is None or (op == '<' and value < before) or (op == '<=' and value <= before):
                                before = value
                                before_exclusive = (op == '<')  # Сохраняем информацию о строгости
                        elif op == '=':
                            # Для равенства используем диапазон
                            after = value.replace(hour=0, minute=0, second=0, microsecond=0)
                            before = value.replace(hour=23, minute=59, second=59, microsecond=999999)
                            after_exclusive = False
                            before_exclusive = False
                    
                    normalized_date_filters[field] = {
                        'after': after,
                        'before': before,
                        'after_exclusive': after_exclusive,
                        'before_exclusive': before_exclusive,
                    }
                else:
                    # Уже нормализованный формат (может быть без after_exclusive/before_exclusive для обратной совместимости)
                    normalized_date_filters[field] = {
                        'after': conditions_list.get('after'),
                        'before': conditions_list.get('before'),
                        'after_exclusive': conditions_list.get('after_exclusive', False),
                        'before_exclusive': conditions_list.get('before_exclusive', False),
                    }
            
            date_filters = normalized_date_filters
        
        # Парсинг links с OR: links:note1 OR links:note2 (сначала OR)
        or_link_pattern = re.compile(r'\s+OR\s+links?:\s*([^:]+?)(?=\s+(?:OR\s+)?(?:tags?|links?|type|created|modified):|$)', re.IGNORECASE)
        or_link_matches = list(or_link_pattern.finditer(query))
        if or_link_matches:
            all_links_or = []
            for match in or_link_matches:
                links_str = match.group(1).strip()
                split_links = re.split(r'[\s,]+', links_str)
                all_links_or.extend([DataNormalizer.normalize_link(link) for link in split_links 
                                    if link.strip() and not link.startswith('links:')])
            
            if all_links_or:
                links_or = DataNormalizer.normalize_links(all_links_or)
                for match in reversed(or_link_matches):
                    text_query = cls._remove_pattern_from_text(text_query, or_link_pattern, match)
                text_query = re.sub(r'\s+OR\s+', ' ', text_query, flags=re.IGNORECASE)
        
        # Парсинг links с NOT: links:note1 NOT links:note2
        not_link_pattern = re.compile(r'\s+NOT\s+links?:\s*([^:]+?)(?=\s+(?:NOT\s+)?(?:tags?|links?|type|created|modified):|$)', re.IGNORECASE)
        not_link_matches = list(not_link_pattern.finditer(query))
        if not_link_matches:
            all_links_not = []
            for match in not_link_matches:
                links_str = match.group(1).strip()
                split_links = re.split(r'[\s,]+', links_str)
                all_links_not.extend([DataNormalizer.normalize_link(link) for link in split_links 
                                     if link.strip() and not link.startswith('links:')])
            
            if all_links_not:
                links_not = DataNormalizer.normalize_links(all_links_not)
                for match in reversed(not_link_matches):
                    text_query = cls._remove_pattern_from_text(text_query, not_link_pattern, match)
                text_query = re.sub(r'\s+NOT\s+', ' ', text_query, flags=re.IGNORECASE)
        
        # Парсинг связанных заметок (wikilinks) - после удаления OR и NOT
        link_matches = list(cls.LINK_PATTERN.finditer(text_query))
        if link_matches:
            # Объединяем все найденные links
            all_links = []
            preserved_texts = {}
            for idx, match in enumerate(link_matches):
                # Разделяем links по пробелам и запятым
                links_str = match.group(1).strip()
                # Поддерживаем разделение через пробелы и запятые
                split_links = re.split(r'[\s,]+', links_str)
                
                # Проверяем последнее слово: если оно начинается с заглавной или содержит кириллицу,
                # это текст запроса, а не часть значения фильтра
                preserved_text = None
                if len(split_links) > 1:
                    last_word = split_links[-1]
                    is_text_query = (
                        last_word[0].isupper() if last_word else False
                    ) or any('\u0400' <= c <= '\u04FF' for c in last_word)
                    
                    if is_text_query:
                        # Сохраняем все слова после первого, которые выглядят как текст запроса
                        text_words = []
                        for i in range(len(split_links) - 1, -1, -1):
                            word = split_links[i]
                            word_is_text = (
                                word[0].isupper() if word else False
                            ) or any('\u0400' <= c <= '\u04FF' for c in word)
                            if word_is_text:
                                text_words.insert(0, word)
                                split_links = split_links[:-1]
                            else:
                                break
                        if text_words:
                            preserved_text = ' '.join(text_words)
                            preserved_texts[idx] = preserved_text
                
                all_links.extend([DataNormalizer.normalize_link(link) for link in split_links 
                                 if link.strip() and not link.startswith('links:')])
            
            if all_links:
                # Нормализуем и убираем дубликаты
                links = DataNormalizer.normalize_links(all_links)
                # Удаляем links из текстового запроса (в обратном порядке чтобы не сбить индексы)
                for idx, match in enumerate(reversed(link_matches)):
                    preserved_text = preserved_texts.get(len(link_matches) - 1 - idx)
                    text_query = cls._remove_pattern_from_text(text_query, cls.LINK_PATTERN, match, preserve_trailing_text=preserved_text)
        
        # Парсинг типа документа с OR: type:протокол OR type:договор (сначала OR)
        or_type_pattern = re.compile(r'\s+OR\s+type:\s*([^:]+?)(?=\s+(?:OR\s+)?(?:tags?|links?|type|created|modified):|$)', re.IGNORECASE)
        or_type_matches = list(or_type_pattern.finditer(query))
        if or_type_matches:
            all_types_or = []
            for match in or_type_matches:
                type_str = match.group(1).strip()
                all_types_or.append(DataNormalizer.normalize_doc_type(type_str))
            
            if all_types_or:
                # Нормализуем и убираем дубликаты
                doc_type_or = list(dict.fromkeys([DataNormalizer.normalize_doc_type(t) for t in all_types_or]))
                for match in reversed(or_type_matches):
                    text_query = cls._remove_pattern_from_text(text_query, or_type_pattern, match)
                text_query = re.sub(r'\s+OR\s+', ' ', text_query, flags=re.IGNORECASE)
        
        # Парсинг типа документа с NOT: type:протокол NOT type:архив
        not_type_pattern = re.compile(r'\s+NOT\s+type:\s*([^:]+?)(?=\s+(?:NOT\s+)?(?:tags?|links?|type|created|modified):|$)', re.IGNORECASE)
        not_type_matches = list(not_type_pattern.finditer(query))
        if not_type_matches:
            # Берём первый NOT тип
            doc_type_not = DataNormalizer.normalize_doc_type(not_type_matches[0].group(1))
            for match in reversed(not_type_matches):
                text_query = cls._remove_pattern_from_text(text_query, not_type_pattern, match)
            text_query = re.sub(r'\s+NOT\s+', ' ', text_query, flags=re.IGNORECASE)
        
        # Парсинг типа документа (ищем в text_query после удаления OR и NOT)
        # Если не найден, ищем в исходном query (на случай, если был удален при обработке OR/NOT)
        type_matches = list(cls.TYPE_PATTERN.finditer(text_query))
        if not type_matches:
            # Пробуем найти в исходном query
            type_matches = list(cls.TYPE_PATTERN.finditer(query))
            # Фильтруем те, которые не были обработаны как OR/NOT
            filtered_matches = []
            for match in type_matches:
                type_text = match.group(0)
                # Проверяем, что это не OR или NOT тип
                before_text = query[max(0, match.start()-10):match.start()]
                if 'or' not in before_text.lower() and 'not' not in before_text.lower():
                    filtered_matches.append(match)
            type_matches = filtered_matches
        
        if type_matches:
            # Берём первый найденный тип и нормализуем
            doc_type = DataNormalizer.normalize_doc_type(type_matches[0].group(1))
            # Удаляем все вхождения типа из текстового запроса
            # Используем простую замену строки, так как паттерн уже найден
            for match in reversed(type_matches):
                type_text = match.group(0)  # Полный текст паттерна "type:протокол"
                # Удаляем из text_query
                if type_text in text_query:
                    text_query = text_query.replace(type_text, '', 1).strip()
        
        # Очищаем текст от лишних пробелов
        text_query = re.sub(r'\s+', ' ', text_query).strip()
        
        # Нормализуем текстовый запрос (lowercase, стоп-слова, синонимы)
        if text_query:
            text_query = QueryNormalizer.normalize(text_query)
        
        return ParsedQuery(
            text_query=text_query or "",  # Если весь запрос был фильтрами, оставляем пустую строку
            tags=tags if tags else None,
            tags_or=tags_or if 'tags_or' in locals() and tags_or else None,
            tags_not=tags_not if 'tags_not' in locals() and tags_not else None,
            inline_tags=inline_tags if 'inline_tags' in locals() and inline_tags else None,
            inline_tags_or=inline_tags_or if 'inline_tags_or' in locals() and inline_tags_or else None,
            inline_tags_not=inline_tags_not if 'inline_tags_not' in locals() and inline_tags_not else None,
            date_filters=date_filters if date_filters else None,
            doc_type=doc_type if doc_type else None,
            doc_type_or=doc_type_or if 'doc_type_or' in locals() and doc_type_or else None,
            doc_type_not=doc_type_not if 'doc_type_not' in locals() and doc_type_not else None,
            links=links if links else None,
            links_or=links_or if 'links_or' in locals() and links_or else None,
            links_not=links_not if 'links_not' in locals() and links_not else None,
        )
    
    @classmethod
    async def build_where_clause(
        cls,
        parsed: ParsedQuery,
        fuzzy: bool = False,
        all_links: list[str] | None = None,
        all_tags: list[str] | None = None,
        all_inline_tags: list[str] | None = None,
        db_manager: "IDatabaseManager | None" = None,
        vault_name: str | None = None,
    ) -> tuple[str | None, set[str] | None]:
        """Построение SQL WHERE условия для LanceDB (v4).
        
        В v4 поддерживает двухэтапные запросы для фильтров по свойствам.
        
        Args:
            parsed: Распарсенный запрос
            fuzzy: Использовать fuzzy matching для links и tags
            all_links: Список всех ссылок для fuzzy matching (опционально)
            all_tags: Список всех frontmatter тегов для fuzzy matching (опционально)
            all_inline_tags: Список всех inline тегов для fuzzy matching (опционально)
            db_manager: Менеджер БД для двухэтапных запросов (опционально)
            vault_name: Имя vault'а для двухэтапных запросов (опционально)
            
        Returns:
            Кортеж (where_clause, document_ids):
            - where_clause: SQL WHERE условие для фильтрации чанков
            - document_ids: Множество document_id для фильтрации (если используется двухэтапный запрос)
            
        Examples:
            >>> parsed = ParsedQuery(text_query="test", tags=["python", "async"])
            >>> where_clause, doc_ids = await QueryParser.build_where_clause(parsed)
            >>> where_clause
            "array_contains(tags, 'python') AND array_contains(tags, 'async')"
        """
        return await FilterBuilder.build_where_clause(
            tags=parsed.tags,
            tags_or=parsed.tags_or,
            tags_not=parsed.tags_not,
            inline_tags=parsed.inline_tags,
            inline_tags_or=parsed.inline_tags_or,
            inline_tags_not=parsed.inline_tags_not,
            links=parsed.links,
            links_or=parsed.links_or,
            links_not=parsed.links_not,
            doc_type=parsed.doc_type,
            doc_type_or=parsed.doc_type_or,
            doc_type_not=parsed.doc_type_not,
            date_filters=parsed.date_filters,
            fuzzy=fuzzy,
            all_links=all_links,
            all_tags=all_tags,
            all_inline_tags=all_inline_tags,
            db_manager=db_manager,
            vault_name=vault_name,
        )

