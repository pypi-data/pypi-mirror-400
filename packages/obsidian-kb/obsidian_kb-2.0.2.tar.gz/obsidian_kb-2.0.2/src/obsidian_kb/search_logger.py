"""Модуль для логирования поисковых запросов в формате JSON Lines для аналитики."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from obsidian_kb import __version__

logger = logging.getLogger(__name__)


class SearchLogger:
    """Логгер поисковых запросов в формате JSON Lines для аналитики."""

    def __init__(self, logs_dir: Path | None = None) -> None:
        """Инициализация логгера.

        Args:
            logs_dir: Директория для хранения логов (по умолчанию ~/.obsidian-kb/logs/)
        """
        if logs_dir is None:
            logs_dir = Path.home() / ".obsidian-kb" / "logs"
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file_path(self, date: datetime | None = None) -> Path:
        """Получить путь к файлу лога для указанной даты.

        Args:
            date: Дата для лога (по умолчанию сегодня)

        Returns:
            Путь к файлу лога
        """
        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        return self.logs_dir / f"search_queries_{date_str}.jsonl"

    def log_search(
        self,
        original_query: str,
        normalized_query: str | None = None,
        vault_name: str | None = None,
        search_type: str = "hybrid",
        result_count: int = 0,
        execution_time_ms: float = 0.0,
        avg_relevance_score: float = 0.0,
        empty_results: bool = False,
        used_optimizer: bool = False,
        source: str = "mcp",
        requested_search_type: str | None = None,
        was_fallback: bool = False,
        ollama_available: bool = True,
        # Дополнительные поля для диагностики
        filters: dict[str, Any] | None = None,  # Информация о фильтрах (tags, type, dates, links)
        where_clause: str | None = None,  # SQL WHERE условие
        embedding_time_ms: float | None = None,  # Время получения embedding
        query_length: int | None = None,  # Длина запроса
        limit: int | None = None,  # Запрошенный лимит результатов
        cache_hit: bool | None = None,  # Попадание в кэш
        error: str | None = None,  # Сообщение об ошибке (если была)
        vault_stats: dict[str, Any] | None = None,  # Статистика vault'а
        embedding_model: str | None = None,  # Модель embedding
        rerank_used: bool | None = None,  # Использовался ли re-ranking
        feature_ranking_used: bool | None = None,  # Использовался ли feature-based ranking
        **kwargs: Any,
    ) -> None:
        """Логирование поискового запроса.

        Args:
            original_query: Исходный запрос (до нормализации)
            normalized_query: Нормализованный запрос (после обработки)
            vault_name: Имя vault'а (None для multi-vault поиска)
            search_type: Тип поиска (vector, fts, hybrid, links)
            result_count: Количество результатов
            execution_time_ms: Время выполнения в миллисекундах
            avg_relevance_score: Средняя релевантность результатов (0-1)
            empty_results: Пустые результаты
            used_optimizer: Использовался ли оптимизатор поиска
            source: Источник запроса (mcp, cli, api)
            **kwargs: Дополнительные поля для логирования
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "version": __version__,  # Версия obsidian-kb
                "original_query": original_query,
                "normalized_query": normalized_query or original_query,
                "vault_name": vault_name,
                "search_type": search_type,
                "result_count": result_count,
                "execution_time_ms": round(execution_time_ms, 2),
                "avg_relevance_score": round(avg_relevance_score, 3),
                "empty_results": empty_results,
                "used_optimizer": used_optimizer,
            }
            
            # Добавляем дополнительные поля для диагностики
            if requested_search_type is not None:
                log_entry["requested_search_type"] = requested_search_type
            if was_fallback:
                log_entry["was_fallback"] = was_fallback
            if not ollama_available:
                log_entry["ollama_available"] = ollama_available
            
            # Детальная информация о фильтрах
            if filters:
                log_entry["filters"] = filters
            
            # WHERE clause для отладки
            if where_clause:
                log_entry["where_clause"] = where_clause
            
            # Время получения embedding
            if embedding_time_ms is not None:
                log_entry["embedding_time_ms"] = round(embedding_time_ms, 2)
            
            # Размер запроса
            if query_length is None:
                query_length = len(original_query)
            log_entry["query_length"] = query_length
            
            # Лимит результатов
            if limit is not None:
                log_entry["limit"] = limit
            
            # Информация о кэше
            if cache_hit is not None:
                log_entry["cache_hit"] = cache_hit
            
            # Ошибки
            if error:
                log_entry["error"] = error
            
            # Статистика vault'а
            if vault_stats:
                log_entry["vault_stats"] = vault_stats
            
            # Модель embedding
            if embedding_model:
                log_entry["embedding_model"] = embedding_model
            
            # Детали оптимизации
            if rerank_used is not None:
                log_entry["rerank_used"] = rerank_used
            if feature_ranking_used is not None:
                log_entry["feature_ranking_used"] = feature_ranking_used

            # Добавляем дополнительные поля если есть
            log_entry.update(kwargs)

            # Записываем в файл (JSON Lines формат)
            log_file = self._get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            logger.debug(f"Logged search query: {original_query[:50]}...")

        except Exception as e:
            logger.error(f"Failed to log search query: {e}")

    def get_logs(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        vault_name: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Получить логи поисковых запросов за период.

        Args:
            start_date: Начальная дата (по умолчанию сегодня)
            end_date: Конечная дата (по умолчанию сегодня)
            vault_name: Фильтр по vault'у (опционально)
            limit: Максимальное количество записей (опционально)

        Returns:
            Список записей логов
        """
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        all_logs = []

        # Проходим по всем дням в диапазоне
        current_date = start_date
        while current_date <= end_date:
            log_file = self._get_log_file_path(current_date)
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                log_entry = json.loads(line)
                                log_timestamp = datetime.fromisoformat(log_entry["timestamp"])

                                # Фильтруем по дате
                                if start_date <= log_timestamp <= end_date:
                                    # Фильтруем по vault если указан
                                    if vault_name is None or log_entry.get("vault_name") == vault_name:
                                        all_logs.append(log_entry)
                except Exception as e:
                    logger.warning(f"Failed to read log file {log_file}: {e}")

            # Переходим к следующему дню
            current_date += timedelta(days=1)

        # Сортируем по времени (новые сначала)
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)

        # Ограничиваем количество если указано
        if limit is not None:
            all_logs = all_logs[:limit]

        return all_logs

    def clear_old_logs(self, days_to_keep: int = 90) -> int:
        """Очистка старых логов.

        Args:
            days_to_keep: Количество дней для хранения логов

        Returns:
            Количество удалённых файлов
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0

            for log_file in self.logs_dir.glob("search_queries_*.jsonl"):
                try:
                    # Извлекаем дату из имени файла
                    date_str = log_file.stem.replace("search_queries_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")

                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old log file: {log_file}")
                except Exception as e:
                    logger.warning(f"Failed to process log file {log_file}: {e}")

            if deleted_count > 0:
                logger.info(f"Cleared {deleted_count} old log files (older than {days_to_keep} days)")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to clear old logs: {e}")
            return 0


# Глобальный экземпляр логгера
_search_logger: SearchLogger | None = None


def get_search_logger() -> SearchLogger:
    """Получить глобальный экземпляр SearchLogger."""
    global _search_logger
    if _search_logger is None:
        _search_logger = SearchLogger()
    return _search_logger

