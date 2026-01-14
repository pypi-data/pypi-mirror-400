"""Комплексное тестирование качества поиска.

Тестирует качество поиска с использованием метрик:
- Precision@K, Recall@K
- MRR (Mean Reciprocal Rank)
- NDCG@K (Normalized Discounted Cumulative Gain)

Использует golden set запросов из fixtures/search_queries.json
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from obsidian_kb.service_container import get_service_container, reset_service_container
from obsidian_kb.types import RetrievalGranularity, SearchRequest

from tests.search_quality_metrics import (
    QualityMetrics,
    aggregate_metrics,
    calculate_quality_metrics,
)

logger = logging.getLogger(__name__)


class SearchQualityTester:
    """Тестер качества поиска."""

    def __init__(self, vault_name: str):
        """Инициализация тестера.

        Args:
            vault_name: Имя vault'а для тестирования
        """
        self.vault_name = vault_name
        self.services = get_service_container()
        self.search_service = self.services.search_service

    async def test_query(
        self,
        query_id: str,
        query: str,
        expected_results: list[str],
        search_type: str = "hybrid",
        limit: int = 20,
    ) -> tuple[QualityMetrics, dict[str, Any]]:
        """Тестирование одного запроса.

        Args:
            query_id: ID запроса
            query: Текст запроса
            expected_results: Список ожидаемых document_id (golden set)
            search_type: Тип поиска (hybrid, vector, fts)
            limit: Максимальное количество результатов

        Returns:
            Кортеж (метрики качества, детали результатов)
        """
        # Выполняем поиск
        request = SearchRequest(
            vault_name=self.vault_name,
            query=query,
            limit=limit,
            search_type=search_type,
            granularity=RetrievalGranularity.AUTO,
        )

        response = await self.search_service.search(request)

        # Извлекаем document_id из результатов
        retrieved_doc_ids = [result.document.document_id for result in response.results]
        relevant_doc_ids = set(expected_results)

        # Вычисляем метрики
        metrics = calculate_quality_metrics(retrieved_doc_ids, relevant_doc_ids)

        # Детали для отчета
        details = {
            "query_id": query_id,
            "query": query,
            "detected_intent": response.detected_intent.value if response.detected_intent else None,
            "strategy_used": response.strategy_used,
            "execution_time_ms": response.execution_time_ms,
            "total_found": response.total_found,
            "retrieved_doc_ids": retrieved_doc_ids[:10],  # Топ-10 для отчета
            "expected_doc_ids": list(relevant_doc_ids),
            "num_relevant": len(relevant_doc_ids),
            "num_retrieved": len(retrieved_doc_ids),
            "num_relevant_retrieved": metrics.num_relevant_retrieved,
        }

        return metrics, details

    async def test_from_golden_set(
        self,
        golden_set_path: Path | None = None,
    ) -> dict[str, Any]:
        """Тестирование на основе golden set запросов.

        Args:
            golden_set_path: Путь к файлу с golden set (по умолчанию fixtures/search_queries.json)

        Returns:
            Словарь с результатами тестирования
        """
        if golden_set_path is None:
            golden_set_path = Path(__file__).parent / "fixtures" / "search_queries.json"

        # Загружаем golden set
        if not golden_set_path.exists():
            raise FileNotFoundError(f"Golden set file not found: {golden_set_path}")

        with open(golden_set_path, "r", encoding="utf-8") as f:
            golden_set = json.load(f)

        queries = golden_set.get("queries", [])
        logger.info(f"Загружено {len(queries)} запросов из golden set")

        # Тестируем каждый запрос
        all_metrics: list[QualityMetrics] = []
        all_details: list[dict[str, Any]] = []

        for query_data in queries:
            query_id = query_data.get("id", "unknown")
            query = query_data.get("query", "")
            expected_results = query_data.get("expected_results", [])
            search_type = query_data.get("search_type", "hybrid")
            description = query_data.get("description", "")

            logger.info(f"Тестирование запроса {query_id}: {query} ({description})")

            try:
                metrics, details = await self.test_query(
                    query_id=query_id,
                    query=query,
                    expected_results=expected_results,
                    search_type=search_type,
                )
                all_metrics.append(metrics)
                all_details.append(details)
            except Exception as e:
                logger.error(f"Ошибка при тестировании запроса {query_id}: {e}")
                # Добавляем пустые метрики для статистики
                all_metrics.append(
                    QualityMetrics(
                        precision_at_1=0.0,
                        precision_at_5=0.0,
                        precision_at_10=0.0,
                        recall_at_1=0.0,
                        recall_at_5=0.0,
                        recall_at_10=0.0,
                        mrr=0.0,
                        ndcg_at_5=0.0,
                        ndcg_at_10=0.0,
                        num_relevant=0,
                        num_retrieved=0,
                        num_relevant_retrieved=0,
                    )
                )
                all_details.append({
                    "query_id": query_id,
                    "query": query,
                    "error": str(e),
                })

        # Агрегируем метрики
        aggregate = aggregate_metrics(all_metrics)

        return {
            "vault_name": self.vault_name,
            "num_queries": len(queries),
            "aggregate_metrics": {
                "avg_precision_at_1": aggregate.avg_precision_at_1,
                "avg_precision_at_5": aggregate.avg_precision_at_5,
                "avg_precision_at_10": aggregate.avg_precision_at_10,
                "avg_recall_at_1": aggregate.avg_recall_at_1,
                "avg_recall_at_5": aggregate.avg_recall_at_5,
                "avg_recall_at_10": aggregate.avg_recall_at_10,
                "avg_mrr": aggregate.avg_mrr,
                "avg_ndcg_at_5": aggregate.avg_ndcg_at_5,
                "avg_ndcg_at_10": aggregate.avg_ndcg_at_10,
            },
            "query_details": all_details,
            "individual_metrics": [
                {
                    "query_id": details.get("query_id"),
                    "precision_at_1": metrics.precision_at_1,
                    "precision_at_5": metrics.precision_at_5,
                    "precision_at_10": metrics.precision_at_10,
                    "recall_at_1": metrics.recall_at_1,
                    "recall_at_5": metrics.recall_at_5,
                    "recall_at_10": metrics.recall_at_10,
                    "mrr": metrics.mrr,
                    "ndcg_at_5": metrics.ndcg_at_5,
                    "ndcg_at_10": metrics.ndcg_at_10,
                }
                for metrics, details in zip(all_metrics, all_details)
            ],
        }

    def print_results(self, results: dict[str, Any]) -> None:
        """Вывод результатов тестирования.

        Args:
            results: Результаты тестирования
        """
        print("\n" + "=" * 80)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ КАЧЕСТВА ПОИСКА")
        print("=" * 80)
        print(f"\nVault: {results['vault_name']}")
        print(f"Количество запросов: {results['num_queries']}")

        agg = results["aggregate_metrics"]
        print("\n" + "-" * 80)
        print("АГРЕГИРОВАННЫЕ МЕТРИКИ:")
        print("-" * 80)
        print(f"Precision@1:  {agg['avg_precision_at_1']:.3f}")
        print(f"Precision@5:  {agg['avg_precision_at_5']:.3f}")
        print(f"Precision@10: {agg['avg_precision_at_10']:.3f}")
        print(f"Recall@1:     {agg['avg_recall_at_1']:.3f}")
        print(f"Recall@5:     {agg['avg_recall_at_5']:.3f}")
        print(f"Recall@10:    {agg['avg_recall_at_10']:.3f}")
        print(f"MRR:          {agg['avg_mrr']:.3f}")
        print(f"NDCG@5:       {agg['avg_ndcg_at_5']:.3f}")
        print(f"NDCG@10:      {agg['avg_ndcg_at_10']:.3f}")

        # Детали по запросам
        print("\n" + "-" * 80)
        print("ДЕТАЛИ ПО ЗАПРОСАМ:")
        print("-" * 80)
        for detail in results["query_details"]:
            query_id = detail.get("query_id", "unknown")
            query = detail.get("query", "")
            detected_intent = detail.get("detected_intent", "unknown")
            execution_time = detail.get("execution_time_ms", 0.0)
            total_found = detail.get("total_found", 0)

            print(f"\n[{query_id}] {query}")
            print(f"  Intent: {detected_intent}")
            print(f"  Найдено: {total_found}, Время: {execution_time:.2f}ms")

            if "error" in detail:
                print(f"  ❌ Ошибка: {detail['error']}")
            else:
                # Находим метрики для этого запроса
                metrics_data = next(
                    (
                        m
                        for m in results["individual_metrics"]
                        if m["query_id"] == query_id
                    ),
                    None,
                )
                if metrics_data:
                    print(f"  Precision@5: {metrics_data['precision_at_5']:.3f}")
                    print(f"  Recall@5:   {metrics_data['recall_at_5']:.3f}")
                    print(f"  MRR:        {metrics_data['mrr']:.3f}")
                    print(f"  NDCG@5:     {metrics_data['ndcg_at_5']:.3f}")


async def run_search_quality_tests(
    vault_name: str,
    golden_set_path: Path | None = None,
    output_json: Path | None = None,
) -> dict[str, Any]:
    """Запуск комплексного тестирования качества поиска.

    Args:
        vault_name: Имя vault'а для тестирования
        golden_set_path: Путь к файлу с golden set (опционально)
        output_json: Путь для сохранения результатов в JSON (опционально)

    Returns:
        Результаты тестирования
    """
    # Сбрасываем контейнер для чистого состояния
    reset_service_container()

    tester = SearchQualityTester(vault_name)
    results = await tester.test_from_golden_set(golden_set_path)
    tester.print_results(results)

    # Сохраняем результаты в JSON если указан путь
    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nРезультаты сохранены в {output_json}")

    return results


if __name__ == "__main__":
    import sys

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Параметры по умолчанию
    vault_name = "test_vault_real" if len(sys.argv) < 2 else sys.argv[1]

    # Запуск тестов
    results = asyncio.run(run_search_quality_tests(vault_name))

    # Вывод итоговой статистики
    agg = results["aggregate_metrics"]
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"Средняя Precision@10: {agg['avg_precision_at_10']:.3f}")
    print(f"Средняя Recall@10:    {agg['avg_recall_at_10']:.3f}")
    print(f"Средний MRR:          {agg['avg_mrr']:.3f}")
    print(f"Средний NDCG@10:      {agg['avg_ndcg_at_10']:.3f}")


