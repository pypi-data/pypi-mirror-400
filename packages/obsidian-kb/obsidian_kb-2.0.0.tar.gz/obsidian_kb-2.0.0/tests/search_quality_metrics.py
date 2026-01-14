"""Модуль для расчета метрик качества поиска.

Реализует стандартные метрики оценки качества поиска:
- Precision@K - точность топ-K результатов
- Recall@K - полнота топ-K результатов
- MRR (Mean Reciprocal Rank) - средний обратный ранг первого релевантного результата
- NDCG@K (Normalized Discounted Cumulative Gain) - нормализованный дисконтированный накопленный выигрыш
"""

from dataclasses import dataclass
from typing import Any

import math


@dataclass
class QualityMetrics:
    """Метрики качества поиска для одного запроса."""

    precision_at_1: float
    precision_at_5: float
    precision_at_10: float
    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    mrr: float  # Mean Reciprocal Rank
    ndcg_at_5: float
    ndcg_at_10: float
    num_relevant: int  # Количество релевантных документов в golden set
    num_retrieved: int  # Количество найденных документов
    num_relevant_retrieved: int  # Количество релевантных документов среди найденных


def calculate_precision_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: set[str],
    k: int,
) -> float:
    """Вычисление Precision@K.

    Args:
        retrieved_doc_ids: Список ID найденных документов (в порядке релевантности)
        relevant_doc_ids: Множество ID релевантных документов
        k: Количество топ результатов для оценки

    Returns:
        Precision@K (0.0 - 1.0)
    """
    if k == 0:
        return 0.0

    top_k = retrieved_doc_ids[:k]
    if not top_k:
        return 0.0

    relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_doc_ids)
    return relevant_in_top_k / len(top_k)


def calculate_recall_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: set[str],
    k: int,
) -> float:
    """Вычисление Recall@K.

    Args:
        retrieved_doc_ids: Список ID найденных документов (в порядке релевантности)
        relevant_doc_ids: Множество ID релевантных документов
        k: Количество топ результатов для оценки

    Returns:
        Recall@K (0.0 - 1.0)
    """
    if not relevant_doc_ids:
        return 0.0

    top_k = retrieved_doc_ids[:k]
    relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_doc_ids)
    return relevant_in_top_k / len(relevant_doc_ids)


def calculate_mrr(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: set[str],
) -> float:
    """Вычисление MRR (Mean Reciprocal Rank).

    MRR = 1 / rank первого релевантного результата
    Если релевантных результатов нет, MRR = 0

    Args:
        retrieved_doc_ids: Список ID найденных документов (в порядке релевантности)
        relevant_doc_ids: Множество ID релевантных документов

    Returns:
        MRR (0.0 - 1.0)
    """
    if not relevant_doc_ids:
        return 0.0

    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in relevant_doc_ids:
            return 1.0 / rank

    return 0.0


def calculate_dcg_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: set[str],
    k: int,
) -> float:
    """Вычисление DCG@K (Discounted Cumulative Gain).

    DCG@K = sum(rel_i / log2(i + 1)) для i от 1 до K
    где rel_i = 1 если документ релевантен, иначе 0

    Args:
        retrieved_doc_ids: Список ID найденных документов (в порядке релевантности)
        relevant_doc_ids: Множество ID релевантных документов
        k: Количество топ результатов для оценки

    Returns:
        DCG@K
    """
    top_k = retrieved_doc_ids[:k]
    dcg = 0.0

    for i, doc_id in enumerate(top_k, start=1):
        relevance = 1.0 if doc_id in relevant_doc_ids else 0.0
        dcg += relevance / math.log2(i + 1)

    return dcg


def calculate_ndcg_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: set[str],
    k: int,
) -> float:
    """Вычисление NDCG@K (Normalized Discounted Cumulative Gain).

    NDCG@K = DCG@K / IDCG@K
    где IDCG@K - идеальный DCG (все релевантные документы в начале)

    Args:
        retrieved_doc_ids: Список ID найденных документов (в порядке релевантности)
        relevant_doc_ids: Множество ID релевантных документов
        k: Количество топ результатов для оценки

    Returns:
        NDCG@K (0.0 - 1.0)
    """
    dcg = calculate_dcg_at_k(retrieved_doc_ids, relevant_doc_ids, k)

    # Вычисляем IDCG (идеальный DCG)
    # Сортируем релевантные документы в идеальном порядке (все релевантные в начале)
    num_relevant = len(relevant_doc_ids)
    if num_relevant == 0:
        return 0.0

    # Идеальный порядок: все релевантные документы в начале
    ideal_dcg = 0.0
    for i in range(1, min(k, num_relevant) + 1):
        ideal_dcg += 1.0 / math.log2(i + 1)

    if ideal_dcg == 0.0:
        return 0.0

    return dcg / ideal_dcg


def calculate_quality_metrics(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: set[str],
) -> QualityMetrics:
    """Вычисление всех метрик качества поиска.

    Args:
        retrieved_doc_ids: Список ID найденных документов (в порядке релевантности)
        relevant_doc_ids: Множество ID релевантных документов

    Returns:
        QualityMetrics со всеми метриками
    """
    num_relevant = len(relevant_doc_ids)
    num_retrieved = len(retrieved_doc_ids)
    num_relevant_retrieved = sum(1 for doc_id in retrieved_doc_ids if doc_id in relevant_doc_ids)

    return QualityMetrics(
        precision_at_1=calculate_precision_at_k(retrieved_doc_ids, relevant_doc_ids, 1),
        precision_at_5=calculate_precision_at_k(retrieved_doc_ids, relevant_doc_ids, 5),
        precision_at_10=calculate_precision_at_k(retrieved_doc_ids, relevant_doc_ids, 10),
        recall_at_1=calculate_recall_at_k(retrieved_doc_ids, relevant_doc_ids, 1),
        recall_at_5=calculate_recall_at_k(retrieved_doc_ids, relevant_doc_ids, 5),
        recall_at_10=calculate_recall_at_k(retrieved_doc_ids, relevant_doc_ids, 10),
        mrr=calculate_mrr(retrieved_doc_ids, relevant_doc_ids),
        ndcg_at_5=calculate_ndcg_at_k(retrieved_doc_ids, relevant_doc_ids, 5),
        ndcg_at_10=calculate_ndcg_at_k(retrieved_doc_ids, relevant_doc_ids, 10),
        num_relevant=num_relevant,
        num_retrieved=num_retrieved,
        num_relevant_retrieved=num_relevant_retrieved,
    )


@dataclass
class AggregateQualityMetrics:
    """Агрегированные метрики качества для набора запросов."""

    num_queries: int
    avg_precision_at_1: float
    avg_precision_at_5: float
    avg_precision_at_10: float
    avg_recall_at_1: float
    avg_recall_at_5: float
    avg_recall_at_10: float
    avg_mrr: float
    avg_ndcg_at_5: float
    avg_ndcg_at_10: float


def aggregate_metrics(metrics_list: list[QualityMetrics]) -> AggregateQualityMetrics:
    """Агрегация метрик для набора запросов.

    Args:
        metrics_list: Список метрик для каждого запроса

    Returns:
        AggregateQualityMetrics со средними значениями
    """
    if not metrics_list:
        return AggregateQualityMetrics(
            num_queries=0,
            avg_precision_at_1=0.0,
            avg_precision_at_5=0.0,
            avg_precision_at_10=0.0,
            avg_recall_at_1=0.0,
            avg_recall_at_5=0.0,
            avg_recall_at_10=0.0,
            avg_mrr=0.0,
            avg_ndcg_at_5=0.0,
            avg_ndcg_at_10=0.0,
        )

    n = len(metrics_list)

    return AggregateQualityMetrics(
        num_queries=n,
        avg_precision_at_1=sum(m.precision_at_1 for m in metrics_list) / n,
        avg_precision_at_5=sum(m.precision_at_5 for m in metrics_list) / n,
        avg_precision_at_10=sum(m.precision_at_10 for m in metrics_list) / n,
        avg_recall_at_1=sum(m.recall_at_1 for m in metrics_list) / n,
        avg_recall_at_5=sum(m.recall_at_5 for m in metrics_list) / n,
        avg_recall_at_10=sum(m.recall_at_10 for m in metrics_list) / n,
        avg_mrr=sum(m.mrr for m in metrics_list) / n,
        avg_ndcg_at_5=sum(m.ndcg_at_5 for m in metrics_list) / n,
        avg_ndcg_at_10=sum(m.ndcg_at_10 for m in metrics_list) / n,
    )




