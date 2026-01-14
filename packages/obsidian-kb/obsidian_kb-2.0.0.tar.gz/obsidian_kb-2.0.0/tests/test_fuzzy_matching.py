"""Тесты для fuzzy matching."""

import pytest

from obsidian_kb.fuzzy_matching import FuzzyMatcher


class TestFuzzyMatcher:
    """Тесты для FuzzyMatcher."""
    
    def test_substring_match_exact(self):
        """Тест точного совпадения через substring."""
        candidates = ["amuratov", "amur", "amur_notes", "python", "async"]
        results = FuzzyMatcher.fuzzy_match("amuratov", candidates, algorithm="substring")
        assert "amuratov" in results
        assert results[0] == "amuratov"  # Точное совпадение должно быть первым
    
    def test_substring_match_partial(self):
        """Тест частичного совпадения через substring."""
        candidates = ["amuratov", "amur", "amur_notes", "python", "async"]
        results = FuzzyMatcher.fuzzy_match("amur", candidates, algorithm="substring")
        assert "amuratov" in results
        assert "amur" in results
        assert "amur_notes" in results
        assert "python" not in results
        assert "async" not in results
    
    def test_substring_match_no_results(self):
        """Тест отсутствия результатов."""
        candidates = ["python", "async"]
        results = FuzzyMatcher.fuzzy_match("amur", candidates, algorithm="substring")
        assert len(results) == 0
    
    def test_substring_match_max_results(self):
        """Тест ограничения количества результатов."""
        candidates = [f"amur_{i}" for i in range(100)]
        results = FuzzyMatcher.fuzzy_match("amur", candidates, algorithm="substring", max_results=10)
        assert len(results) == 10
    
    def test_levenshtein_match(self):
        """Тест поиска через расстояние Левенштейна."""
        candidates = ["amuratov", "amur", "amur_notes", "python", "async"]
        results = FuzzyMatcher.fuzzy_match("amur", candidates, algorithm="levenshtein", min_score=0.3)
        assert "amur" in results
        assert "amuratov" in results
        assert "amur_notes" in results
    
    def test_levenshtein_match_min_score(self):
        """Тест фильтрации по минимальному score."""
        candidates = ["amuratov", "amur", "python"]
        results = FuzzyMatcher.fuzzy_match("amur", candidates, algorithm="levenshtein", min_score=0.8)
        # "amur" должен иметь score 1.0, "amuratov" - меньше
        assert "amur" in results
    
    def test_fuzzy_match_link(self):
        """Тест fuzzy matching для ссылок."""
        all_links = ["amuratov", "amur", "amur_notes", "python", "async"]
        results = FuzzyMatcher.fuzzy_match_link("amur", all_links)
        assert "amuratov" in results
        assert "amur" in results
        assert "amur_notes" in results
    
    def test_fuzzy_match_tag(self):
        """Тест fuzzy matching для тегов."""
        all_tags = ["meeting", "meetings", "meetup", "python", "async"]
        results = FuzzyMatcher.fuzzy_match_tag("meet", all_tags)
        assert "meeting" in results
        assert "meetings" in results
        assert "meetup" in results
    
    def test_levenshtein_distance(self):
        """Тест вычисления расстояния Левенштейна."""
        assert FuzzyMatcher._levenshtein_distance("kitten", "sitting") == 3
        assert FuzzyMatcher._levenshtein_distance("amur", "amur") == 0
        assert FuzzyMatcher._levenshtein_distance("amur", "amuratov") == 4
        assert FuzzyMatcher._levenshtein_distance("", "test") == 4
        assert FuzzyMatcher._levenshtein_distance("test", "") == 4

