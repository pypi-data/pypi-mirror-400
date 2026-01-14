"""Модуль для fuzzy matching (нечеткого поиска) по частичному совпадению.

Используется для поиска ссылок и тегов по частичному совпадению,
например: links:amur → amuratov, tags:meet → meeting.
"""

import logging

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """Класс для fuzzy matching по частичному совпадению.
    
    Поддерживает два алгоритма:
    1. Substring matching - поиск по подстроке (быстрый)
    2. Levenshtein distance - поиск по расстоянию редактирования (точный)
    """
    
    @staticmethod
    def fuzzy_match(
        partial: str,
        candidates: list[str],
        algorithm: str = "substring",
        max_results: int = 10,
        min_score: float = 0.0,
    ) -> list[str]:
        """Поиск кандидатов по частичному совпадению.
        
        Args:
            partial: Частичная строка для поиска
            candidates: Список кандидатов для поиска
            algorithm: Алгоритм поиска - "substring" (быстрый) или "levenshtein" (точный)
            max_results: Максимальное количество результатов
            min_score: Минимальный score для включения в результаты (0.0-1.0)
            
        Returns:
            Список найденных кандидатов, отсортированных по релевантности
        """
        if not partial or not candidates:
            return []
        
        partial_lower = partial.lower().strip()
        if not partial_lower:
            return []
        
        if algorithm == "substring":
            return FuzzyMatcher._substring_match(partial_lower, candidates, max_results)
        elif algorithm == "levenshtein":
            return FuzzyMatcher._levenshtein_match(
                partial_lower, candidates, max_results, min_score
            )
        else:
            logger.warning(f"Unknown algorithm: {algorithm}, using substring")
            return FuzzyMatcher._substring_match(partial_lower, candidates, max_results)
    
    @staticmethod
    def _substring_match(
        partial: str, candidates: list[str], max_results: int
    ) -> list[str]:
        """Поиск по подстроке (быстрый алгоритм).
        
        Находит все кандидаты, которые содержат частичную строку.
        Сортирует по позиции вхождения (раньше = лучше) и длине (короче = лучше).
        
        Args:
            partial: Частичная строка для поиска
            candidates: Список кандидатов
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных кандидатов
        """
        matches: list[tuple[str, int, int]] = []  # (candidate, position, length)
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            position = candidate_lower.find(partial)
            
            if position >= 0:
                # Найдено совпадение
                matches.append((candidate, position, len(candidate)))
        
        # Сортируем по позиции (раньше = лучше), затем по длине (короче = лучше)
        matches.sort(key=lambda x: (x[1], x[2]))
        
        # Возвращаем только кандидаты
        return [match[0] for match in matches[:max_results]]
    
    @staticmethod
    def _levenshtein_match(
        partial: str,
        candidates: list[str],
        max_results: int,
        min_score: float,
    ) -> list[str]:
        """Поиск по расстоянию Левенштейна (точный алгоритм).
        
        Вычисляет расстояние редактирования между частичной строкой и кандидатами.
        Сортирует по score (меньше расстояние = выше score).
        
        Args:
            partial: Частичная строка для поиска
            candidates: Список кандидатов
            max_results: Максимальное количество результатов
            min_score: Минимальный score для включения
            
        Returns:
            Список найденных кандидатов с score >= min_score
        """
        scored_matches: list[tuple[str, float]] = []
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            
            # Вычисляем расстояние Левенштейна
            distance = FuzzyMatcher._levenshtein_distance(partial, candidate_lower)
            
            # Вычисляем score: 1.0 - normalized_distance
            max_len = max(len(partial), len(candidate_lower))
            if max_len == 0:
                score = 1.0
            else:
                normalized_distance = distance / max_len
                score = 1.0 - normalized_distance
            
            if score >= min_score:
                scored_matches.append((candidate, score))
        
        # Сортируем по score (выше = лучше)
        scored_matches.sort(key=lambda x: x[1], reverse=True)
        
        return [match[0] for match in scored_matches[:max_results]]
    
    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Вычисление расстояния Левенштейна между двумя строками.
        
        Args:
            s1: Первая строка
            s2: Вторая строка
            
        Returns:
            Расстояние Левенштейна (количество операций редактирования)
        """
        if len(s1) < len(s2):
            return FuzzyMatcher._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        # Инициализация матрицы
        previous_row = list(range(len(s2) + 1))
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Стоимость операций
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def fuzzy_match_link(
        partial_link: str,
        all_links: list[str],
        algorithm: str = "substring",
        max_results: int = 10,
    ) -> list[str]:
        """Поиск ссылок по частичному совпадению.
        
        Args:
            partial_link: Частичная ссылка (например, "amur")
            all_links: Список всех ссылок для поиска
            algorithm: Алгоритм поиска
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных ссылок
        """
        return FuzzyMatcher.fuzzy_match(
            partial_link, all_links, algorithm=algorithm, max_results=max_results
        )
    
    @staticmethod
    def fuzzy_match_tag(
        partial_tag: str,
        all_tags: list[str],
        algorithm: str = "substring",
        max_results: int = 10,
    ) -> list[str]:
        """Поиск тегов по частичному совпадению.
        
        Args:
            partial_tag: Частичный тег (например, "meet")
            all_tags: Список всех тегов для поиска
            algorithm: Алгоритм поиска
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных тегов
        """
        return FuzzyMatcher.fuzzy_match(
            partial_tag, all_tags, algorithm=algorithm, max_results=max_results
        )

