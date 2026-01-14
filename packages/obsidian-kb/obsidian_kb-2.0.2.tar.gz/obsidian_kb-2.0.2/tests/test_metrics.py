"""Тесты для модуля метрик."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from obsidian_kb.metrics import MetricsCollector, MetricsSummary


@pytest.mark.asyncio
async def test_record_search(temp_db):
    """Тест записи метрики поиска."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    await metrics.record_search(
        vault_name="test_vault",
        query="Python",
        search_type="hybrid",
        result_count=5,
        execution_time_ms=34.5,
    )
    
    # Проверяем, что метрика записана
    summary = await metrics.get_summary(days=1, limit=10)
    assert summary.total_searches == 1
    assert summary.avg_execution_time_ms == 34.5


@pytest.mark.asyncio
async def test_record_multiple_searches(temp_db):
    """Тест записи нескольких метрик."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Записываем несколько метрик
    for i in range(5):
        await metrics.record_search(
            vault_name="test_vault",
            query=f"query_{i}",
            search_type="hybrid",
            result_count=i,
            execution_time_ms=10.0 + i,
        )
    
    summary = await metrics.get_summary(days=1, limit=10)
    assert summary.total_searches == 5
    assert summary.searches_by_type["hybrid"] == 5


@pytest.mark.asyncio
async def test_get_summary_empty(temp_db):
    """Тест получения сводки при отсутствии метрик."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    summary = await metrics.get_summary(days=7, limit=10)
    assert summary.total_searches == 0
    assert summary.searches_by_type == {}
    assert summary.popular_queries == []
    assert summary.popular_vaults == []
    assert summary.avg_execution_time_ms == 0.0


@pytest.mark.asyncio
async def test_get_summary_with_data(temp_db):
    """Тест получения сводки с данными."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Записываем метрики с разными типами поиска
    await metrics.record_search("vault1", "Python", "hybrid", 5, 30.0)
    await metrics.record_search("vault1", "Python", "hybrid", 3, 25.0)
    await metrics.record_search("vault2", "JavaScript", "fts", 2, 15.0)
    await metrics.record_search("vault1", "TypeScript", "vector", 4, 40.0)
    
    summary = await metrics.get_summary(days=1, limit=10)
    
    assert summary.total_searches == 4
    assert summary.searches_by_type["hybrid"] == 2
    assert summary.searches_by_type["fts"] == 1
    assert summary.searches_by_type["vector"] == 1
    assert summary.total_vaults_searched == 2
    
    # Проверяем популярные запросы
    assert len(summary.popular_queries) > 0
    assert summary.popular_queries[0][0] == "Python"  # Самый популярный
    assert summary.popular_queries[0][1] == 2
    
    # Проверяем популярные vault'ы
    assert len(summary.popular_vaults) > 0
    assert summary.popular_vaults[0][0] == "vault1"
    assert summary.popular_vaults[0][1] == 3


@pytest.mark.asyncio
async def test_export_to_json(temp_db, tmp_path):
    """Тест экспорта метрик в JSON."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Записываем несколько метрик
    await metrics.record_search("vault1", "Python", "hybrid", 5, 30.0)
    await metrics.record_search("vault2", "JavaScript", "fts", 3, 20.0)
    
    output_path = tmp_path / "metrics.json"
    await metrics.export_to_json(output_path, days=1)
    
    assert output_path.exists()
    
    import json
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "popular_queries" in data
    assert "popular_vaults" in data
    assert data["summary"]["total_searches"] == 2


@pytest.mark.asyncio
async def test_export_to_csv(temp_db, tmp_path):
    """Тест экспорта метрик в CSV."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Записываем несколько метрик
    await metrics.record_search("vault1", "Python", "hybrid", 5, 30.0)
    await metrics.record_search("vault2", "JavaScript", "fts", 3, 20.0)
    
    output_path = tmp_path / "metrics.csv"
    await metrics.export_to_csv(output_path, days=1)
    
    assert output_path.exists()
    
    content = output_path.read_text(encoding="utf-8")
    assert "timestamp" in content
    assert "vault_name" in content
    assert "query" in content
    assert "Python" in content
    assert "JavaScript" in content


@pytest.mark.asyncio
async def test_clear_old_metrics(temp_db):
    """Тест очистки старых метрик."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Записываем метрику
    await metrics.record_search("vault1", "Python", "hybrid", 5, 30.0)
    
    # Очищаем метрики старше 0 дней (все)
    deleted = await metrics.clear_old_metrics(days_to_keep=0)
    
    # Проверяем, что метрики удалены
    summary = await metrics.get_summary(days=1, limit=10)
    assert summary.total_searches == 0
    assert deleted >= 0  # Может быть 0 или 1 в зависимости от времени


@pytest.mark.asyncio
async def test_popular_queries_limit(temp_db):
    """Тест ограничения количества популярных запросов."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Записываем много разных запросов
    for i in range(20):
        await metrics.record_search("vault1", f"query_{i}", "hybrid", 1, 10.0)
    
    summary = await metrics.get_summary(days=1, limit=5)
    
    # Должно быть максимум 5 популярных запросов
    assert len(summary.popular_queries) <= 5


@pytest.mark.asyncio
async def test_multi_vault_search_metric(temp_db):
    """Тест метрики для multi-vault поиска."""
    metrics = MetricsCollector(db_path=temp_db.parent / "metrics.lance")
    
    # Multi-vault поиск (vault_name = None)
    await metrics.record_search(
        vault_name=None,
        query="Python",
        search_type="hybrid",
        result_count=10,
        execution_time_ms=50.0,
    )
    
    summary = await metrics.get_summary(days=1, limit=10)
    assert summary.total_searches == 1
    # Multi-vault поиск не должен попадать в popular_vaults
    assert summary.total_vaults_searched == 0

