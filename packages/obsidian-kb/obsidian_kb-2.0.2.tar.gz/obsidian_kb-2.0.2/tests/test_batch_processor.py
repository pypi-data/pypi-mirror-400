"""Тесты для batch_processor.py"""

import asyncio
import pytest

from obsidian_kb.batch_processor import BatchProcessor


@pytest.mark.asyncio
async def test_process_simple():
    """Тест простой обработки элементов."""
    processor = BatchProcessor(batch_size=5)
    
    items = list(range(10))
    
    async def process_item(item: int) -> int:
        await asyncio.sleep(0.01)  # Имитация работы
        return item * 2
    
    results = await processor.process(items, process_item)
    
    assert len(results) == 10
    assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


@pytest.mark.asyncio
async def test_process_with_progress():
    """Тест обработки с callback прогресса."""
    processor = BatchProcessor(batch_size=3)
    
    items = list(range(10))
    progress_calls = []
    
    def progress_callback(current: int, total: int, percentage: float) -> None:
        progress_calls.append((current, total, percentage))
    
    async def process_item(item: int) -> int:
        return item * 2
    
    results = await processor.process(items, process_item, progress_callback=progress_callback)
    
    assert len(results) == 10
    assert len(progress_calls) > 0
    # Проверяем, что последний вызов показывает 100%
    assert progress_calls[-1][0] == 10
    assert progress_calls[-1][1] == 10


@pytest.mark.asyncio
async def test_process_with_errors():
    """Тест обработки с ошибками."""
    processor = BatchProcessor(batch_size=5)
    
    items = list(range(10))
    errors = []
    
    def error_callback(item: int, exception: Exception) -> None:
        errors.append((item, str(exception)))
    
    async def process_item(item: int) -> int:
        if item == 5:
            raise ValueError("Test error")
        return item * 2
    
    results = await processor.process(items, process_item, error_callback=error_callback)
    
    # Должно быть 9 результатов (10 - 1 ошибка)
    assert len(results) == 9
    assert len(errors) == 1
    assert errors[0][0] == 5


@pytest.mark.asyncio
async def test_process_sync_function():
    """Тест обработки с синхронной функцией."""
    processor = BatchProcessor(batch_size=5)
    
    items = list(range(10))
    
    def process_item(item: int) -> int:
        return item * 2
    
    results = await processor.process(items, process_item)
    
    assert len(results) == 10
    assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


@pytest.mark.asyncio
async def test_process_cancellation():
    """Тест отмены обработки."""
    processor = BatchProcessor(batch_size=3)
    
    items = list(range(10))
    
    async def process_item(item: int) -> int:
        await asyncio.sleep(0.1)
        return item * 2
    
    # Запускаем обработку и отменяем через небольшое время
    async def cancel_after_delay():
        await asyncio.sleep(0.2)
        processor.cancel()
    
    # Запускаем обработку и отмену параллельно
    results, _ = await asyncio.gather(
        processor.process(items, process_item),
        cancel_after_delay(),
        return_exceptions=True,
    )
    
    # Должно быть обработано меньше элементов из-за отмены
    assert isinstance(results, list)
    assert len(results) < 10


@pytest.mark.asyncio
async def test_process_with_retry():
    """Тест обработки с повторными попытками."""
    processor = BatchProcessor(batch_size=5)
    
    items = list(range(5))
    attempts = {}
    
    async def process_item(item: int) -> int:
        attempts[item] = attempts.get(item, 0) + 1
        if item == 2 and attempts[item] < 3:
            raise ValueError("Temporary error")
        return item * 2
    
    results = await processor.process_with_retry(
        items,
        process_item,
        max_retries=3,
    )
    
    # Все элементы должны быть обработаны после retry
    assert len(results) == 5
    assert attempts[2] == 3  # Элемент 2 должен был обработаться с 3-й попытки


@pytest.mark.asyncio
async def test_process_empty_list():
    """Тест обработки пустого списка."""
    processor = BatchProcessor()
    
    async def process_item(item: int) -> int:
        return item * 2
    
    results = await processor.process([], process_item)
    
    assert len(results) == 0


@pytest.mark.asyncio
async def test_process_large_batch():
    """Тест обработки большого батча."""
    processor = BatchProcessor(batch_size=100, max_workers=5)
    
    items = list(range(1000))
    
    async def process_item(item: int) -> int:
        await asyncio.sleep(0.001)
        return item
    
    results = await processor.process(items, process_item)
    
    assert len(results) == 1000
    assert results == items

