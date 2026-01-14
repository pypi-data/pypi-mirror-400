"""Тесты для performance_monitor.py"""

import asyncio
import pytest
import time

from obsidian_kb.performance_monitor import PerformanceMonitor


@pytest.mark.asyncio
async def test_measure_operation():
    """Тест измерения времени операции."""
    monitor = PerformanceMonitor()
    
    async with monitor.measure("test_operation"):
        await asyncio.sleep(0.1)
    
    metrics = monitor.get_metrics("test_operation")
    assert metrics is not None
    assert metrics.count == 1
    assert metrics.avg_time >= 0.1
    assert metrics.avg_time < 0.2


@pytest.mark.asyncio
async def test_record_multiple():
    """Тест записи нескольких операций."""
    monitor = PerformanceMonitor()
    
    for _ in range(10):
        async with monitor.measure("test_operation"):
            await asyncio.sleep(0.01)
    
    metrics = monitor.get_metrics("test_operation")
    assert metrics is not None
    assert metrics.count == 10
    assert metrics.avg_time >= 0.01


@pytest.mark.asyncio
async def test_percentiles():
    """Тест вычисления перцентилей."""
    monitor = PerformanceMonitor()
    
    # Создаём операции с разным временем выполнения
    times = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    
    for duration in times:
        await monitor.record("test_operation", duration)
    
    metrics = monitor.get_metrics("test_operation")
    assert metrics is not None
    
    # Проверяем перцентили
    assert metrics.p50 > 0
    assert metrics.p95 > metrics.p50
    assert metrics.p99 >= metrics.p95


@pytest.mark.asyncio
async def test_get_report():
    """Тест получения отчета."""
    monitor = PerformanceMonitor()
    
    for _ in range(5):
        async with monitor.measure("test_operation"):
            await asyncio.sleep(0.01)
    
    report = monitor.get_report("test_operation")
    assert report is not None
    assert report.operation_name == "test_operation"
    assert report.count == 5
    assert report.avg_time > 0
    assert report.p50 > 0
    assert report.p95 > 0
    assert report.p99 > 0


@pytest.mark.asyncio
async def test_get_all_reports():
    """Тест получения всех отчетов."""
    monitor = PerformanceMonitor()
    
    async with monitor.measure("operation1"):
        await asyncio.sleep(0.01)
    
    async with monitor.measure("operation2"):
        await asyncio.sleep(0.02)
    
    reports = monitor.get_all_reports()
    assert len(reports) == 2
    
    operation_names = {r.operation_name for r in reports}
    assert "operation1" in operation_names
    assert "operation2" in operation_names


@pytest.mark.asyncio
async def test_reset():
    """Тест сброса метрик."""
    monitor = PerformanceMonitor()
    
    async with monitor.measure("test_operation"):
        await asyncio.sleep(0.01)
    
    assert monitor.get_metrics("test_operation") is not None
    
    monitor.reset("test_operation")
    
    assert monitor.get_metrics("test_operation") is None


@pytest.mark.asyncio
async def test_reset_all():
    """Тест сброса всех метрик."""
    monitor = PerformanceMonitor()
    
    async with monitor.measure("operation1"):
        await asyncio.sleep(0.01)
    
    async with monitor.measure("operation2"):
        await asyncio.sleep(0.01)
    
    assert len(monitor.get_all_reports()) == 2
    
    monitor.reset()
    
    assert len(monitor.get_all_reports()) == 0


@pytest.mark.asyncio
async def test_get_summary():
    """Тест получения сводки."""
    monitor = PerformanceMonitor()
    
    async with monitor.measure("operation1"):
        await asyncio.sleep(0.01)
    
    async with monitor.measure("operation2"):
        await asyncio.sleep(0.02)
    
    summary = monitor.get_summary()
    
    assert "operations" in summary
    assert "total_operations" in summary
    assert summary["total_operations"] == 2
    assert "operation1" in summary["operations"]
    assert "operation2" in summary["operations"]


@pytest.mark.asyncio
async def test_min_max_time():
    """Тест вычисления минимального и максимального времени."""
    monitor = PerformanceMonitor()
    
    times = [0.01, 0.05, 0.03, 0.02, 0.04]
    
    for duration in times:
        await monitor.record("test_operation", duration)
    
    metrics = monitor.get_metrics("test_operation")
    assert metrics is not None
    assert metrics.min_time == 0.01
    assert metrics.max_time == 0.05


@pytest.mark.asyncio
async def test_nonexistent_operation():
    """Тест работы с несуществующей операцией."""
    monitor = PerformanceMonitor()
    
    metrics = monitor.get_metrics("nonexistent")
    assert metrics is None
    
    report = monitor.get_report("nonexistent")
    assert report is None


@pytest.mark.asyncio
async def test_alert_threshold(caplog):
    """Тест алерта на медленные операции."""
    import logging
    
    caplog.set_level(logging.WARNING)
    monitor = PerformanceMonitor(alert_threshold_seconds=1.0)
    
    # Быстрая операция - не должно быть алерта
    await monitor.record("fast_op", 0.5)
    assert "Медленная операция" not in caplog.text
    
    # Медленная операция - должен быть алерт
    await monitor.record("slow_op", 2.0)
    assert "Медленная операция" in caplog.text
    assert "slow_op" in caplog.text
    assert "2.00" in caplog.text


@pytest.mark.asyncio
async def test_alert_callback():
    """Тест callback для алертов."""
    alert_calls = []
    
    def alert_callback(operation: str, duration: float, threshold: float) -> None:
        alert_calls.append((operation, duration, threshold))
    
    monitor = PerformanceMonitor(
        alert_threshold_seconds=1.0,
        alert_callback=alert_callback,
    )
    
    # Медленная операция
    await monitor.record("slow_op", 2.0)
    
    assert len(alert_calls) == 1
    assert alert_calls[0][0] == "slow_op"
    assert alert_calls[0][1] == 2.0
    assert alert_calls[0][2] == 1.0

