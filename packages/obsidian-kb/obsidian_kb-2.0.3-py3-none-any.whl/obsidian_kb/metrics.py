"""Модуль для сбора и анализа метрик использования."""

import asyncio
import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa

from obsidian_kb.config import settings
from obsidian_kb.db_connection_manager import DBConnectionManager

logger = logging.getLogger(__name__)


@dataclass
class SearchMetric:
    """Метрика поискового запроса."""

    timestamp: datetime
    vault_name: str | None
    query: str
    search_type: str  # vector, fts, hybrid
    result_count: int
    execution_time_ms: float
    user: str | None = None  # Для будущего использования
    empty_results: bool = False  # Пустые результаты
    avg_relevance_score: float = 0.0  # Средняя релевантность результатов


@dataclass
class MetricsSummary:
    """Сводка метрик за период."""

    period_start: datetime
    period_end: datetime
    total_searches: int
    searches_by_type: dict[str, int]
    popular_queries: list[tuple[str, int]]  # (query, count)
    popular_vaults: list[tuple[str, int]]  # (vault_name, count)
    avg_execution_time_ms: float
    total_vaults_searched: int
    empty_results_count: int  # Количество запросов с пустыми результатами
    empty_results_percentage: float  # Процент пустых результатов
    avg_relevance_score: float  # Средняя релевантность результатов
    queries_with_no_results: list[tuple[str, int]]  # Запросы без результатов


class MetricsCollector:
    """Сборщик метрик использования системы."""

    def __init__(self, db_path: Path | None = None) -> None:
        """Инициализация сборщика метрик.

        Args:
            db_path: Путь к базе данных (по умолчанию из settings)
        """
        self.db_path = Path(db_path or settings.db_path).parent / "metrics.lance"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection_manager = DBConnectionManager.get_instance(self.db_path.parent)

    def _get_db(self) -> lancedb.DBConnection:
        """Получение подключения к БД через connection manager."""
        # Используем connection manager для получения соединения из пула
        ctx = self.connection_manager.get_connection(self.db_path.parent)
        return ctx.__enter__()

    def _get_table(self) -> lancedb.table.Table:
        """Получение или создание таблицы метрик с миграцией схемы."""
        db = self._get_db()
        table_name = "search_metrics"

        try:
            table = db.open_table(table_name)
            # Проверяем, нужна ли миграция схемы
            arrow_table = table.to_arrow()
            field_names = [field.name for field in arrow_table.schema]
            
            # Проверяем наличие новых полей
            needs_migration = "empty_results" not in field_names or "avg_relevance_score" not in field_names
            
            if needs_migration:
                logger.info("Migrating metrics table: adding new fields")
                # Читаем все данные
                old_data = arrow_table.to_pylist()
                # Добавляем новые поля со значениями по умолчанию
                for row in old_data:
                    if "empty_results" not in row:
                        row["empty_results"] = row.get("result_count", 0) == 0
                    if "avg_relevance_score" not in row:
                        row["avg_relevance_score"] = 0.0
                
                # Создаём новую схему
                new_schema = pa.schema([
                    pa.field("timestamp", pa.timestamp("us")),
                    pa.field("vault_name", pa.string()),
                    pa.field("query", pa.string()),
                    pa.field("search_type", pa.string()),
                    pa.field("result_count", pa.int32()),
                    pa.field("execution_time_ms", pa.float64()),
                    pa.field("user", pa.string()),
                    pa.field("empty_results", pa.bool_()),
                    pa.field("avg_relevance_score", pa.float64()),
                ])
                
                # Создаём новую таблицу
                new_table = pa.Table.from_pylist(old_data, schema=new_schema)
                db.drop_table(table_name)
                table = db.create_table(table_name, new_table, mode="overwrite")
                logger.info("Metrics table migrated successfully")
            
            return table
        except Exception as e:
            # Создаём новую таблицу (таблица не существует или ошибка миграции)
            logger.debug(f"Creating new metrics table (reason: {e})")
            schema = pa.schema([
                pa.field("timestamp", pa.timestamp("us")),
                pa.field("vault_name", pa.string()),
                pa.field("query", pa.string()),
                pa.field("search_type", pa.string()),
                pa.field("result_count", pa.int32()),
                pa.field("execution_time_ms", pa.float64()),
                pa.field("user", pa.string()),
                pa.field("empty_results", pa.bool_()),
                pa.field("avg_relevance_score", pa.float64()),
            ])
            table = db.create_table(table_name, schema=schema, mode="overwrite")
            logger.info(f"Created metrics table: {table_name}")
            return table

    async def record_search(
        self,
        vault_name: str | None,
        query: str,
        search_type: str,
        result_count: int,
        execution_time_ms: float,
        user: str | None = None,
        avg_relevance_score: float = 0.0,
    ) -> None:
        """Запись метрики поиска.

        Args:
            vault_name: Имя vault'а (None для multi-vault поиска)
            query: Поисковый запрос
            search_type: Тип поиска (vector, fts, hybrid)
            result_count: Количество результатов
            execution_time_ms: Время выполнения в миллисекундах
            user: Идентификатор пользователя (опционально)
            avg_relevance_score: Средняя релевантность результатов (0-1)
        """
        try:
            logger.debug(
                f"Recording search metric: vault={vault_name}, query={query[:50]}, "
                f"type={search_type}, results={result_count}, time={execution_time_ms:.2f}ms"
            )
            
            metric = SearchMetric(
                timestamp=datetime.now(),
                vault_name=vault_name,
                query=query,
                search_type=search_type,
                result_count=result_count,
                execution_time_ms=execution_time_ms,
                user=user,
                empty_results=result_count == 0,
                avg_relevance_score=avg_relevance_score,
            )

            # Проверяем путь к БД
            logger.debug(f"Metrics DB path: {self.db_path}")
            if not self.db_path.parent.exists():
                logger.warning(f"Metrics DB directory does not exist: {self.db_path.parent}, creating...")
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

            table = self._get_table()
            logger.debug("Got metrics table, inserting metric...")

            def _insert() -> None:
                try:
                    data = {
                        "timestamp": metric.timestamp,
                        "vault_name": metric.vault_name or "",
                        "query": metric.query,
                        "search_type": metric.search_type,
                        "result_count": metric.result_count,
                        "execution_time_ms": metric.execution_time_ms,
                        "user": metric.user or "",
                        "empty_results": metric.empty_results,
                        "avg_relevance_score": metric.avg_relevance_score,
                    }
                    arrow_table = pa.Table.from_pylist([data])
                    table.add(arrow_table)
                    logger.debug("Successfully inserted metric into table")
                except Exception as inner_e:
                    logger.error(f"Error in _insert(): {inner_e}", exc_info=True)
                    raise

            await asyncio.to_thread(_insert)
            logger.debug(f"Successfully recorded search metric: {query[:50]}...")

        except Exception as e:
            logger.error(
                f"Failed to record search metric: {e}. "
                f"DB path: {self.db_path}, "
                f"Query: {query[:50]}, "
                f"Vault: {vault_name}",
                exc_info=True
            )

    async def get_summary(
        self,
        days: int = 7,
        limit: int = 10,
        vault_name: str | None = None,
    ) -> MetricsSummary:
        """Получение сводки метрик за период.

        Args:
            days: Количество дней для анализа (по умолчанию 7)
            limit: Максимальное количество популярных запросов/vault'ов
            vault_name: Фильтр по конкретному vault'у (опционально)

        Returns:
            Сводка метрик
        """
        try:
            table = self._get_table()
            period_start = datetime.now() - timedelta(days=days)
            period_end = datetime.now()

            def _query() -> list[dict[str, Any]]:
                # Фильтруем по дате
                arrow_table = table.to_arrow()
                data = arrow_table.to_pylist()

                # Фильтруем по timestamp
                filtered = [
                    row
                    for row in data
                    if row["timestamp"] and row["timestamp"] >= period_start
                ]
                
                # Фильтруем по vault_name если указан
                if vault_name:
                    filtered = [
                        row
                        for row in filtered
                        if row.get("vault_name") == vault_name
                    ]

                return filtered

            data = await asyncio.to_thread(_query)

            if not data:
                return MetricsSummary(
                    period_start=period_start,
                    period_end=period_end,
                    total_searches=0,
                    searches_by_type={},
                    popular_queries=[],
                    popular_vaults=[],
                    avg_execution_time_ms=0.0,
                    total_vaults_searched=0,
                    empty_results_count=0,
                    empty_results_percentage=0.0,
                    avg_relevance_score=0.0,
                    queries_with_no_results=[],
                )

            # Анализируем данные
            total_searches = len(data)
            searches_by_type = Counter(row["search_type"] for row in data)
            query_counter = Counter(row["query"] for row in data)
            vault_counter = Counter(row["vault_name"] for row in data if row["vault_name"])

            # Убираем пустые vault'ы
            vault_counter.pop("", None)

            execution_times = [row["execution_time_ms"] for row in data if row.get("execution_time_ms")]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0

            # Метрики качества поиска
            empty_results_count = sum(1 for row in data if row.get("empty_results", False))
            empty_results_percentage = (empty_results_count / total_searches * 100) if total_searches > 0 else 0.0
            
            relevance_scores = [row.get("avg_relevance_score", 0.0) for row in data if row.get("avg_relevance_score", 0.0) > 0]
            avg_relevance_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
            
            # Запросы без результатов
            queries_with_no_results = [
                (query, count) for query, count in query_counter.items()
                if any(row["query"] == query and row.get("empty_results", False) for row in data)
            ]
            queries_with_no_results.sort(key=lambda x: x[1], reverse=True)
            queries_with_no_results = queries_with_no_results[:limit]

            # Топ запросов и vault'ов
            popular_queries = query_counter.most_common(limit)
            popular_vaults = vault_counter.most_common(limit)

            return MetricsSummary(
                period_start=period_start,
                period_end=period_end,
                total_searches=total_searches,
                searches_by_type=dict(searches_by_type),
                popular_queries=popular_queries,
                popular_vaults=popular_vaults,
                avg_execution_time_ms=avg_execution_time,
                total_vaults_searched=len(vault_counter),
                empty_results_count=empty_results_count,
                empty_results_percentage=empty_results_percentage,
                avg_relevance_score=avg_relevance_score,
                queries_with_no_results=queries_with_no_results,
            )

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            # Возвращаем пустую сводку при ошибке
            period_start = datetime.now() - timedelta(days=days)
            period_end = datetime.now()
            return MetricsSummary(
                period_start=period_start,
                period_end=period_end,
                total_searches=0,
                searches_by_type={},
                popular_queries=[],
                popular_vaults=[],
                avg_execution_time_ms=0.0,
                total_vaults_searched=0,
                empty_results_count=0,
                empty_results_percentage=0.0,
                avg_relevance_score=0.0,
                queries_with_no_results=[],
            )

    async def export_to_json(self, output_path: Path, days: int = 30) -> None:
        """Экспорт метрик в JSON файл.

        Args:
            output_path: Путь для сохранения JSON
            days: Количество дней для экспорта
        """
        try:
            summary = await self.get_summary(days=days, limit=100)

            # Конвертируем в JSON-совместимый формат
            export_data = {
                "period": {
                    "start": summary.period_start.isoformat(),
                    "end": summary.period_end.isoformat(),
                },
                "summary": {
                    "total_searches": summary.total_searches,
                    "searches_by_type": summary.searches_by_type,
                    "avg_execution_time_ms": summary.avg_execution_time_ms,
                    "total_vaults_searched": summary.total_vaults_searched,
                },
                "popular_queries": [{"query": q, "count": c} for q, c in summary.popular_queries],
                "popular_vaults": [{"vault": v, "count": c} for v, c in summary.popular_vaults],
            }

            output_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"Exported metrics to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            raise

    async def export_to_csv(self, output_path: Path, days: int = 30) -> None:
        """Экспорт метрик в CSV файл.

        Args:
            output_path: Путь для сохранения CSV
            days: Количество дней для экспорта
        """
        try:
            import csv

            table = self._get_table()
            period_start = datetime.now() - timedelta(days=days)

            def _query() -> list[dict[str, Any]]:
                arrow_table = table.to_arrow()
                data = arrow_table.to_pylist()
                filtered = [
                    row
                    for row in data
                    if row["timestamp"] and row["timestamp"] >= period_start
                ]
                return filtered

            data = await asyncio.to_thread(_query)

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["timestamp", "vault_name", "query", "search_type", "result_count", "execution_time_ms"],
                )
                writer.writeheader()
                for row in data:
                    writer.writerow({
                        "timestamp": row["timestamp"].isoformat() if row["timestamp"] else "",
                        "vault_name": row["vault_name"] or "",
                        "query": row["query"],
                        "search_type": row["search_type"],
                        "result_count": row["result_count"],
                        "execution_time_ms": f"{row['execution_time_ms']:.2f}",
                    })

            logger.info(f"Exported {len(data)} metrics to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export metrics to CSV: {e}")
            raise

    async def clear_old_metrics(self, days_to_keep: int = 90) -> int:
        """Очистка старых метрик.

        Args:
            days_to_keep: Количество дней для хранения метрик

        Returns:
            Количество удалённых записей
        """
        try:
            table = self._get_table()
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            def _delete() -> int:
                arrow_table = table.to_arrow()
                data = arrow_table.to_pylist()

                # Фильтруем записи для удаления
                to_keep = [
                    row
                    for row in data
                    if row["timestamp"] and row["timestamp"] >= cutoff_date
                ]

                deleted_count = len(data) - len(to_keep)

                if deleted_count > 0:
                    # Пересоздаём таблицу только с нужными записями
                    if to_keep:
                        new_data = [
                            {
                                "timestamp": row["timestamp"],
                                "vault_name": row["vault_name"] or "",
                                "query": row["query"],
                                "search_type": row["search_type"],
                                "result_count": row["result_count"],
                                "execution_time_ms": row["execution_time_ms"],
                                "user": row.get("user", "") or "",
                            }
                            for row in to_keep
                        ]
                        new_table = pa.Table.from_pylist(new_data)
                        table.add(new_table, mode="overwrite")
                    else:
                        # Если нет записей для сохранения, очищаем таблицу
                        table.add(pa.Table.from_pylist([]), mode="overwrite")

                return deleted_count

            deleted = await asyncio.to_thread(_delete)
            if deleted > 0:
                logger.info(f"Cleared {deleted} old metrics (older than {days_to_keep} days)")
            return deleted

        except Exception as e:
            logger.error(f"Failed to clear old metrics: {e}")
            return 0

