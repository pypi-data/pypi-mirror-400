"""Трекер затрат на LLM операции."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa

from obsidian_kb.config import settings
from obsidian_kb.db_connection_manager import DBConnectionManager

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Тип операции."""
    
    EMBEDDING = "embedding"
    CHAT_COMPLETION = "chat_completion"
    INDEXING = "indexing"
    ENRICHMENT = "enrichment"
    SEARCH = "search"


@dataclass
class CostRecord:
    """Запись о затратах на операцию."""
    
    timestamp: datetime
    vault_name: str | None
    provider: str
    model: str
    operation_type: OperationType
    input_tokens: int
    cost_usd: float
    output_tokens: int | None = None
    metadata: dict[str, Any] | None = None


class CostTracker:
    """Трекер затрат на LLM операции.
    
    Отслеживает затраты на embedding и chat completion операции,
    разбивку по провайдерам, vault'ам и типам операций.
    """
    
    def __init__(self, db_path: Path | None = None) -> None:
        """Инициализация трекера затрат.
        
        Args:
            db_path: Путь к базе данных (по умолчанию из settings)
        """
        self.db_path = Path(db_path or settings.db_path).parent / "costs.lance"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection_manager = DBConnectionManager.get_instance(self.db_path.parent)
    
    def _get_db(self) -> lancedb.DBConnection:
        """Получение подключения к БД через connection manager."""
        ctx = self.connection_manager.get_connection(self.db_path.parent)
        return ctx.__enter__()
    
    def _get_table(self) -> lancedb.table.Table:
        """Получение или создание таблицы затрат."""
        db = self._get_db()
        table_name = "costs"
        
        try:
            table = db.open_table(table_name)
            return table
        except Exception:
            # Создаём новую таблицу
            schema = pa.schema([
                pa.field("timestamp", pa.timestamp("us")),
                pa.field("vault_name", pa.string()),
                pa.field("provider", pa.string()),
                pa.field("model", pa.string()),
                pa.field("operation_type", pa.string()),
                pa.field("input_tokens", pa.int64()),
                pa.field("output_tokens", pa.int64()),
                pa.field("cost_usd", pa.float64()),
                pa.field("metadata_json", pa.string()),  # JSON для дополнительных метаданных
            ])
            table = db.create_table(table_name, schema=schema, mode="overwrite")
            logger.info(f"Created costs table: {table_name}")
            return table
    
    async def record_cost(
        self,
        provider: str,
        model: str,
        operation_type: OperationType,
        input_tokens: int,
        output_tokens: int | None = None,
        vault_name: str | None = None,
        cost_usd: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Запись затрат на операцию.
        
        Args:
            provider: Имя провайдера (ollama, yandex, openai)
            model: Название модели
            operation_type: Тип операции
            input_tokens: Количество входных токенов
            output_tokens: Количество выходных токенов (для chat completion)
            vault_name: Имя vault'а (опционально)
            cost_usd: Стоимость в USD (если None, будет вычислена автоматически)
            metadata: Дополнительные метаданные
        """
        try:
            # Вычисляем стоимость если не указана
            if cost_usd is None:
                cost_usd = self._calculate_cost(
                    provider=provider,
                    model=model,
                    operation_type=operation_type,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens or 0,
                )
            
            record = CostRecord(
                timestamp=datetime.now(),
                vault_name=vault_name,
                provider=provider,
                model=model,
                operation_type=operation_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                metadata=metadata,
            )
            
            table = self._get_table()
            
            def _insert() -> None:
                import json
                data = {
                    "timestamp": record.timestamp,
                    "vault_name": record.vault_name or "",
                    "provider": record.provider,
                    "model": record.model,
                    "operation_type": record.operation_type.value,
                    "input_tokens": record.input_tokens,
                    "output_tokens": record.output_tokens or 0,
                    "cost_usd": record.cost_usd,
                    "metadata_json": json.dumps(record.metadata or {}),
                }
                arrow_table = pa.Table.from_pylist([data])
                table.add(arrow_table)
            
            await asyncio.to_thread(_insert)
            
            logger.debug(
                f"Recorded cost: {provider}/{model} {operation_type.value} "
                f"({input_tokens} tokens) = ${cost_usd:.6f}"
            )
        
        except Exception as e:
            logger.error(f"Failed to record cost: {e}", exc_info=True)
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        operation_type: OperationType,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Вычисление стоимости операции на основе провайдера и модели.
        
        Args:
            provider: Имя провайдера
            model: Название модели
            operation_type: Тип операции
            input_tokens: Количество входных токенов
            output_tokens: Количество выходных токенов
            
        Returns:
            Стоимость в USD
        """
        # Базовая стоимость по провайдерам (примерные значения)
        # В реальной системе эти значения должны быть в конфигурации
        
        if provider.lower() == "ollama":
            # Ollama обычно бесплатен (локально)
            return 0.0
        
        elif provider.lower() == "yandex":
            # Примерные цены YandexGPT (нужно обновить актуальными)
            if operation_type == OperationType.EMBEDDING:
                # Yandex Embeddings: ~$0.01 за 1M токенов
                return (input_tokens / 1_000_000) * 0.01
            elif operation_type == OperationType.CHAT_COMPLETION:
                # YandexGPT: ~$0.002 за 1K входных токенов, ~$0.006 за 1K выходных
                input_cost = (input_tokens / 1_000) * 0.002
                output_cost = (output_tokens / 1_000) * 0.006
                return input_cost + output_cost
        
        elif provider.lower() == "openai":
            # Примерные цены OpenAI (нужно обновить актуальными)
            if operation_type == OperationType.EMBEDDING:
                # text-embedding-ada-002: $0.0001 за 1K токенов
                return (input_tokens / 1_000) * 0.0001
            elif operation_type == OperationType.CHAT_COMPLETION:
                # GPT-4: зависит от модели, примерные значения
                if "gpt-4" in model.lower():
                    input_cost = (input_tokens / 1_000) * 0.03
                    output_cost = (output_tokens / 1_000) * 0.06
                else:  # GPT-3.5
                    input_cost = (input_tokens / 1_000) * 0.0015
                    output_cost = (output_tokens / 1_000) * 0.002
                return input_cost + output_cost
        
        # По умолчанию возвращаем 0 (неизвестный провайдер)
        logger.warning(f"Unknown provider for cost calculation: {provider}")
        return 0.0
    
    async def get_costs(
        self,
        vault_name: str | None = None,
        provider: str | None = None,
        operation_type: OperationType | None = None,
        period: str = "month",  # day | week | month | all
    ) -> dict[str, Any]:
        """Получение затрат с фильтрацией.
        
        Args:
            vault_name: Фильтр по vault'у
            provider: Фильтр по провайдеру
            operation_type: Фильтр по типу операции
            period: Период отчёта (day | week | month | all)
            
        Returns:
            Словарь с разбивкой затрат
        """
        try:
            table = self._get_table()
            
            # Определяем период
            now = datetime.now()
            if period == "day":
                period_start = now - timedelta(days=1)
            elif period == "week":
                period_start = now - timedelta(weeks=1)
            elif period == "month":
                period_start = now - timedelta(days=30)
            else:  # all
                period_start = datetime(2000, 1, 1)
            
            def _query() -> list[dict[str, Any]]:
                arrow_table = table.to_arrow()
                data = arrow_table.to_pylist()
                
                # Фильтруем по дате
                filtered = [
                    row
                    for row in data
                    if row["timestamp"] and row["timestamp"] >= period_start
                ]
                
                # Фильтруем по vault_name
                if vault_name:
                    filtered = [
                        row
                        for row in filtered
                        if row.get("vault_name") == vault_name
                    ]
                
                # Фильтруем по provider
                if provider:
                    filtered = [
                        row
                        for row in filtered
                        if row.get("provider") == provider
                    ]
                
                # Фильтруем по operation_type
                if operation_type:
                    filtered = [
                        row
                        for row in filtered
                        if row.get("operation_type") == operation_type.value
                    ]
                
                return filtered
            
            data = await asyncio.to_thread(_query)
            
            # Агрегируем данные
            total_cost = sum(row.get("cost_usd", 0.0) for row in data)
            total_input_tokens = sum(row.get("input_tokens", 0) for row in data)
            total_output_tokens = sum(row.get("output_tokens", 0) for row in data)
            
            # Разбивка по провайдерам
            by_provider: dict[str, float] = {}
            for row in data:
                prov = row.get("provider", "unknown")
                by_provider[prov] = by_provider.get(prov, 0.0) + row.get("cost_usd", 0.0)
            
            # Разбивка по vault'ам
            by_vault: dict[str, float] = {}
            for row in data:
                vault = row.get("vault_name") or "unknown"
                by_vault[vault] = by_vault.get(vault, 0.0) + row.get("cost_usd", 0.0)
            
            # Разбивка по типам операций
            by_operation: dict[str, float] = {}
            for row in data:
                op_type = row.get("operation_type", "unknown")
                by_operation[op_type] = by_operation.get(op_type, 0.0) + row.get("cost_usd", 0.0)
            
            return {
                "total_cost_usd": total_cost,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "record_count": len(data),
                "by_provider": by_provider,
                "by_vault": by_vault,
                "by_operation": by_operation,
                "period_start": period_start.isoformat(),
                "period_end": now.isoformat(),
            }
        
        except Exception as e:
            logger.error(f"Failed to get costs: {e}", exc_info=True)
            return {
                "total_cost_usd": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "record_count": 0,
                "by_provider": {},
                "by_vault": {},
                "by_operation": {},
                "period_start": datetime.now().isoformat(),
                "period_end": datetime.now().isoformat(),
            }

