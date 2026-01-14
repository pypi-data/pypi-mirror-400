"""Модуль для batch processing с отслеживанием прогресса."""

import asyncio
import logging
from typing import Callable, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class BatchProcessor(Generic[T, R]):
    """Процессор для пакетной обработки с отслеживанием прогресса.
    
    Позволяет обрабатывать большие наборы данных с callback'ами прогресса
    и возможностью отмены операции.
    """
    
    def __init__(
        self,
        batch_size: int = 32,
        max_workers: int = 10,
    ) -> None:
        """Инициализация процессора.
        
        Args:
            batch_size: Размер батча для обработки
            max_workers: Максимальное количество параллельных воркеров
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self._cancelled = False
    
    def cancel(self) -> None:
        """Отмена текущей операции."""
        self._cancelled = True
        logger.info("Batch processing cancelled")
    
    def is_cancelled(self) -> bool:
        """Проверка, была ли операция отменена.
        
        Returns:
            True если операция отменена
        """
        return self._cancelled
    
    async def process(
        self,
        items: list[T],
        processor: Callable[[T], R | asyncio.Future[R]],
        progress_callback: Callable[[int, int, float], None] | None = None,
        error_callback: Callable[[T, Exception], None] | None = None,
    ) -> list[R]:
        """Обработка списка элементов с отслеживанием прогресса.
        
        Args:
            items: Список элементов для обработки
            processor: Функция обработки одного элемента (может быть async или sync)
            progress_callback: Callback для отслеживания прогресса (current, total, percentage)
            error_callback: Callback для обработки ошибок (item, exception)
            
        Returns:
            Список результатов обработки
            
        Examples:
            >>> async def process_file(file_path):
            ...     # Обработка файла
            ...     return result
            ...
            >>> def on_progress(current, total, percentage):
            ...     print(f"Progress: {current}/{total} ({percentage:.1f}%)")
            ...
            >>> processor = BatchProcessor(batch_size=10)
            >>> results = await processor.process(
            ...     files,
            ...     process_file,
            ...     progress_callback=on_progress
            ... )
        """
        if not items:
            return []
        
        total = len(items)
        results: list[R] = []
        processed = 0
        start_time = asyncio.get_event_loop().time()
        
        # Разбиваем на батчи
        batches = [
            items[i : i + self.batch_size]
            for i in range(0, total, self.batch_size)
        ]
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_item(item: T) -> R | None:
            """Обработка одного элемента с ограничением параллелизма."""
            if self._cancelled:
                return None
            
            async with semaphore:
                try:
                    # Проверяем, является ли processor async функцией
                    if asyncio.iscoroutinefunction(processor):
                        result = await processor(item)
                    else:
                        # Синхронная функция - выполняем в executor
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, processor, item)
                    
                    return result
                except Exception as e:
                    logger.error(f"Error processing item: {e}", exc_info=True)
                    if error_callback:
                        try:
                            error_callback(item, e)
                        except Exception as callback_error:
                            logger.warning(f"Error in error_callback: {callback_error}")
                    return None
        
        # Обрабатываем батчи последовательно, элементы в батче - параллельно
        for batch_idx, batch in enumerate(batches):
            if self._cancelled:
                logger.info(f"Processing cancelled at batch {batch_idx + 1}/{len(batches)}")
                break
            
            # Обрабатываем элементы батча параллельно
            batch_results = await asyncio.gather(
                *[process_item(item) for item in batch],
                return_exceptions=True,
            )
            
            # Фильтруем результаты (убираем None и исключения)
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Exception in batch processing: {result}")
                    continue
                if result is not None:
                    results.append(result)
            
            processed += len(batch)
            
            # Вызываем callback прогресса
            if progress_callback:
                try:
                    percentage = (processed / total) * 100 if total > 0 else 0
                    progress_callback(processed, total, percentage)
                except Exception as e:
                    logger.warning(f"Error in progress_callback: {e}")
        
        if self._cancelled:
            logger.info(f"Processing cancelled: processed {processed}/{total} items")
        else:
            logger.info(f"Processing completed: {processed}/{total} items")
        
        return results
    
    async def process_with_retry(
        self,
        items: list[T],
        processor: Callable[[T], R | asyncio.Future[R]],
        max_retries: int = 3,
        progress_callback: Callable[[int, int, float], None] | None = None,
        error_callback: Callable[[T, Exception], None] | None = None,
    ) -> list[R]:
        """Обработка с повторными попытками при ошибках.
        
        Args:
            items: Список элементов для обработки
            processor: Функция обработки одного элемента
            max_retries: Максимальное количество попыток для каждого элемента
            progress_callback: Callback для отслеживания прогресса
            error_callback: Callback для обработки ошибок
            
        Returns:
            Список результатов обработки
        """
        async def processor_with_retry(item: T) -> R:
            """Процессор с retry логикой."""
            last_error = None
            for attempt in range(max_retries):
                try:
                    if asyncio.iscoroutinefunction(processor):
                        return await processor(item)
                    else:
                        loop = asyncio.get_event_loop()
                        return await loop.run_in_executor(None, processor, item)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            f"Error processing item (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Failed to process item after {max_retries} attempts: {e}")
            
            # Если все попытки неудачны, пробрасываем последнюю ошибку
            raise last_error  # type: ignore
        
        return await self.process(
            items,
            processor_with_retry,
            progress_callback=progress_callback,
            error_callback=error_callback,
        )

