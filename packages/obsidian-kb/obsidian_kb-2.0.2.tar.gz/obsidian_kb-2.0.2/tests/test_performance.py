"""Тесты производительности поиска после оптимизации.

Измеряет время ответа (P50, P95, P99) для различных типов запросов:
- Процедурные запросы (цель: <1s)
- Known Item запросы (цель: <200ms)
- Семантический поиск (цель: <1s)
- Фильтры по метаданным (цель: <500ms)
"""

import asyncio
import json
import statistics
import time
from pathlib import Path
from typing import Any

from obsidian_kb.service_container import get_service_container, reset_service_container
from obsidian_kb.types import SearchRequest


# Тестовые запросы для разных типов
PERFORMANCE_TEST_QUERIES = {
    "procedural": [
        "how to install",
        "как создать ADR",
        "how to setup",
        "инструкция по установке",
        "guide for beginners",
    ],
    "known_item": [
        "README.md",
        "SETUP_GUIDE.md",
        "ADR-001",
        "PROJ-123",
    ],
    "semantic": [
        "python programming",
        "database optimization",
        "machine learning algorithms",
        "web development best practices",
    ],
    "metadata_filter": [
        "tags:python",
        "type:person",
        "type:project",
        "tags:meeting tags:important",
    ],
}


def calculate_percentiles(times: list[float]) -> dict[str, float]:
    """Вычисление перцентилей времени выполнения.
    
    Args:
        times: Список времени выполнения в миллисекундах
        
    Returns:
        Словарь с перцентилями (p50, p95, p99, avg, min, max)
    """
    if not times:
        return {}
    
    sorted_times = sorted(times)
    n = len(sorted_times)
    
    return {
        "p50": sorted_times[int(n * 0.50)],
        "p95": sorted_times[int(n * 0.95)],
        "p99": sorted_times[int(n * 0.99)],
        "avg": statistics.mean(times),
        "min": min(times),
        "max": max(times),
        "count": n,
    }


async def measure_query_performance(
    vault_name: str,
    query: str,
    search_type: str = "hybrid",
    iterations: int = 10,
    warmup_iterations: int = 2,
) -> dict[str, Any]:
    """Измерение производительности одного запроса.
    
    Args:
        vault_name: Имя vault'а
        query: Поисковый запрос
        search_type: Тип поиска
        iterations: Количество итераций для измерения
        warmup_iterations: Количество итераций для разогрева
        
    Returns:
        Словарь с метриками производительности
    """
    reset_service_container()
    services = get_service_container()
    
    times = []
    results_count = []
    
    # Разогрев
    for _ in range(warmup_iterations):
        try:
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                search_type=search_type,
            )
            await services.search_service.search(request)
        except Exception:
            pass
    
    # Измерение
    for _ in range(iterations):
        start_time = time.time()
        try:
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                search_type=search_type,
            )
            response = await services.search_service.search(request)
            elapsed = (time.time() - start_time) * 1000  # В миллисекундах
            times.append(elapsed)
            results_count.append(len(response.results))
        except Exception as e:
            print(f"⚠️  Ошибка при измерении запроса '{query}': {e}")
            continue
    
    if not times:
        return {}
    
    percentiles = calculate_percentiles(times)
    percentiles["avg_results"] = statistics.mean(results_count) if results_count else 0
    
    return {
        "query": query,
        "search_type": search_type,
        "times_ms": times,
        "percentiles": percentiles,
    }


async def run_performance_tests(
    vault_name: str,
    output_file: Path | None = None,
) -> dict[str, Any]:
    """Запуск тестов производительности для всех типов запросов.
    
    Args:
        vault_name: Имя vault'а
        output_file: Путь к файлу для сохранения результатов
        
    Returns:
        Сводная статистика по всем тестам
    """
    print("\n" + "=" * 80)
    print("🚀 ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ ПОИСКА")
    print("=" * 80)
    print(f"Vault: {vault_name}\n")
    
    all_results = {}
    summary = {
        "vault_name": vault_name,
        "timestamp": time.time(),
        "test_results": {},
        "summary": {},
    }
    
    # Целевые значения производительности (в миллисекундах)
    targets = {
        "procedural": 1000,  # <1s
        "known_item": 200,   # <200ms
        "semantic": 1000,    # <1s
        "metadata_filter": 500,  # <500ms
    }
    
    for query_type, queries in PERFORMANCE_TEST_QUERIES.items():
        print(f"\n📊 Тестирование: {query_type.upper()}")
        print("-" * 80)
        
        query_results = []
        all_times = []
        
        for query in queries:
            print(f"  Запрос: '{query}'...", end=" ", flush=True)
            
            result = await measure_query_performance(
                vault_name=vault_name,
                query=query,
                search_type="hybrid" if query_type != "metadata_filter" else "hybrid",
                iterations=5,
            )
            
            if result and "percentiles" in result:
                p95 = result["percentiles"]["p95"]
                avg = result["percentiles"]["avg"]
                target = targets.get(query_type, 1000)
                status = "✅" if p95 < target else "⚠️"
                
                print(f"{status} P95: {p95:.1f}ms (цель: <{target}ms)")
                
                query_results.append(result)
                all_times.extend(result["times_ms"])
            else:
                print("❌ Ошибка")
        
        if all_times:
            type_percentiles = calculate_percentiles(all_times)
            target = targets.get(query_type, 1000)
            
            print(f"\n  📈 Сводка по типу '{query_type}':")
            print(f"     P50: {type_percentiles['p50']:.1f}ms")
            print(f"     P95: {type_percentiles['p95']:.1f}ms (цель: <{target}ms)")
            print(f"     P99: {type_percentiles['p99']:.1f}ms")
            print(f"     Среднее: {type_percentiles['avg']:.1f}ms")
            
            all_results[query_type] = {
                "queries": query_results,
                "summary": type_percentiles,
                "target": target,
                "meets_target": type_percentiles['p95'] < target,
            }
    
    # Общая сводка
    print("\n" + "=" * 80)
    print("📊 ОБЩАЯ СВОДКА")
    print("=" * 80)
    
    for query_type, result in all_results.items():
        summary_data = result["summary"]
        target = result["target"]
        meets = "✅" if result["meets_target"] else "⚠️"
        
        print(f"{meets} {query_type.upper()}:")
        print(f"   P95: {summary_data['p95']:.1f}ms (цель: <{target}ms)")
        print(f"   Среднее: {summary_data['avg']:.1f}ms")
    
    summary["test_results"] = all_results
    
    # Сохранение результатов
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Результаты сохранены: {output_file}")
    
    # Закрываем соединения
    try:
        services = get_service_container()
        await services.cleanup()
    except Exception:
        pass
    
    return summary


async def main():
    """Основная функция для запуска тестов."""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  {sys.argv[0]} <vault_name> [output_file]")
        print("\nПример:")
        print(f"  {sys.argv[0]} my-vault performance_results.json")
        sys.exit(1)
    
    vault_name = sys.argv[1]
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("performance_test_results.json")
    
    await run_performance_tests(vault_name, output_file)


if __name__ == "__main__":
    asyncio.run(main())

