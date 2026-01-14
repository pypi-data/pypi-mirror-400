"""Утилиты для агрегации результатов поиска."""

from obsidian_kb.types import ChunkSearchResult, RelevanceScore


def aggregate_scores_max(chunks: list[ChunkSearchResult]) -> RelevanceScore:
    """Агрегация scores через максимум."""
    # TODO: Реализовать
    return RelevanceScore.exact_match()


def aggregate_scores_mean(chunks: list[ChunkSearchResult]) -> RelevanceScore:
    """Агрегация scores через среднее."""
    # TODO: Реализовать
    return RelevanceScore.exact_match()


def aggregate_scores_rrf(chunks: list[ChunkSearchResult], k: int = 60) -> RelevanceScore:
    """Агрегация scores через Reciprocal Rank Fusion (RRF)."""
    # TODO: Реализовать
    return RelevanceScore.exact_match()

