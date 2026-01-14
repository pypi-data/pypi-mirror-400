"""Тестирование производительности поиска v5.

Измеряет время ответа (P50, P95, P99) для:
- Document-level поиск
- Chunk-level поиск (vector, fts, hybrid)

Цель: P95 <400ms
"""

import asyncio
import json
import statistics
import time
from pathlib import Path
from typing import Any

from obsidian_kb.service_container import ServiceContainer
from obsidian_kb.types import RetrievalGranularity, SearchIntent, SearchRequest


# Тестовые запросы для разных типов поиска
TEST_QUERIES = {
    "document_level": [
        "tags:python",
        "tags:meeting tags:important",
        "type:note",
        "tags:project tags:active",
        "type:meeting",
        "tags:todo tags:urgent",
        "type:document",
        "tags:reference",
        "tags:personal tags:private",
        "type:guide",
    ],
    "chunk_level_vector": [
        "Python async programming",
        "database optimization techniques",
        "REST API design patterns",
        "machine learning algorithms",
        "web development best practices",
        "distributed systems architecture",
        "security best practices",
        "performance optimization",
        "code review guidelines",
        "microservices architecture",
    ],
    "chunk_level_fts": [
        "Python async programming",
        "database optimization",
        "REST API design",
        "machine learning",
        "web development",
        "distributed systems",
        "security practices",
        "performance optimization",
        "code review",
        "microservices",
    ],
    "chunk_level_hybrid": [
        "Python async programming",
        "database optimization techniques",
        "REST API design patterns",
        "machine learning algorithms",
        "web development best practices",
        "distributed systems architecture",
        "security best practices",
        "performance optimization",
        "code review guidelines",
        "microservices architecture",
    ],
}


async def measure_search_performance(
    search_service: Any,
    vault_name: str,
    query: str,
    search_type: str,
    granularity: RetrievalGranularity,
    iterations: int = 10,
) -> list[float]:
    """Измерение времени выполнения поиска.
    
    Args:
        search_service: Сервис поиска
        vault_name: Имя vault'а
        query: Поисковый запрос
        search_type: Тип поиска (vector, fts, hybrid)
        granularity: Гранулярность (DOCUMENT, CHUNK)
        iterations: Количество итераций для усреднения
        
    Returns:
        Список времени выполнения в миллисекундах
    """
    times = []
    
    for _ in range(iterations):
        request = SearchRequest(
            vault_name=vault_name,
            query=query,
            limit=10,
            search_type=search_type if granularity == RetrievalGranularity.CHUNK else None,
            granularity=granularity,
            include_content=False,  # Без контента для чистого измерения поиска
        )
        
        start_time = time.time()
        response = await search_service.search(request)
        elapsed_ms = (time.time() - start_time) * 1000
        
        times.append(elapsed_ms)
        
        # Небольшая пауза между запросами
        await asyncio.sleep(0.1)
    
    return times


def calculate_percentiles(times: list[float]) -> dict[str, float]:
    """Вычисление перцентилей времени выполнения.
    
    Args:
        times: Список времени выполнения в миллисекундах
        
    Returns:
        Словарь с P50, P95, P99
    """
    if not times:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
    
    sorted_times = sorted(times)
    n = len(sorted_times)
    
    return {
        "p50": sorted_times[int(n * 0.50)],
        "p95": sorted_times[int(n * 0.95)] if n > 1 else sorted_times[0],
        "p99": sorted_times[int(n * 0.99)] if n > 1 else sorted_times[0],
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
    }


async def _run_performance_test(
    vault_name: str,
    iterations_per_query: int = 10,
    warmup_iterations: int = 3,
) -> dict[str, Any]:
    """Тестирование производительности всех типов поиска.
    
    Args:
        vault_name: Имя vault'а для тестирования
        iterations_per_query: Количество итераций для каждого запроса
        warmup_iterations: Количество разогревочных итераций
        
    Returns:
        Словарь с результатами тестирования
    """
    print("🚀 Запуск тестирования производительности поиска v5")
    print("=" * 80)
    print()
    
    # Инициализация сервисов
    print("📦 Инициализация сервисов...")
    services = ServiceContainer()
    search_service = services.search_service
    
    # Разогрев
    print(f"🔥 Разогрев ({warmup_iterations} итераций)...")
    warmup_query = "test"
    warmup_request = SearchRequest(
        vault_name=vault_name,
        query=warmup_query,
        limit=10,
        granularity=RetrievalGranularity.CHUNK,
    )
    for _ in range(warmup_iterations):
        await search_service.search(warmup_request)
        await asyncio.sleep(0.1)
    print("✅ Разогрев завершён\n")
    
    results: dict[str, Any] = {
        "vault_name": vault_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "iterations_per_query": iterations_per_query,
        "tests": {},
    }
    
    # Тест 1: Document-level поиск
    print("📋 Тест 1: Document-level поиск")
    print("-" * 80)
    doc_times = []
    for query in TEST_QUERIES["document_level"]:
        times = await measure_search_performance(
            search_service,
            vault_name,
            query,
            "hybrid",
            RetrievalGranularity.DOCUMENT,
            iterations_per_query,
        )
        doc_times.extend(times)
        print(f"  Запрос: {query[:50]}... | Среднее: {statistics.mean(times):.1f} мс")
    
    doc_stats = calculate_percentiles(doc_times)
    results["tests"]["document_level"] = {
        "times": doc_times,
        "stats": doc_stats,
        "target_p95": 400.0,
        "meets_target": doc_stats["p95"] < 400.0,
    }
    print(f"\n  P50: {doc_stats['p50']:.1f} мс")
    print(f"  P95: {doc_stats['p95']:.1f} мс {'✅' if doc_stats['p95'] < 400 else '❌'}")
    print(f"  P99: {doc_stats['p99']:.1f} мс")
    print(f"  Среднее: {doc_stats['mean']:.1f} мс")
    print()
    
    # Тест 2: Chunk-level vector поиск
    print("🔍 Тест 2: Chunk-level vector поиск")
    print("-" * 80)
    vector_times = []
    for query in TEST_QUERIES["chunk_level_vector"]:
        times = await measure_search_performance(
            search_service,
            vault_name,
            query,
            "vector",
            RetrievalGranularity.CHUNK,
            iterations_per_query,
        )
        vector_times.extend(times)
        print(f"  Запрос: {query[:50]}... | Среднее: {statistics.mean(times):.1f} мс")
    
    vector_stats = calculate_percentiles(vector_times)
    results["tests"]["chunk_level_vector"] = {
        "times": vector_times,
        "stats": vector_stats,
        "target_p95": 400.0,
        "meets_target": vector_stats["p95"] < 400.0,
    }
    print(f"\n  P50: {vector_stats['p50']:.1f} мс")
    print(f"  P95: {vector_stats['p95']:.1f} мс {'✅' if vector_stats['p95'] < 400 else '❌'}")
    print(f"  P99: {vector_stats['p99']:.1f} мс")
    print(f"  Среднее: {vector_stats['mean']:.1f} мс")
    print()
    
    # Тест 3: Chunk-level FTS поиск
    print("🔎 Тест 3: Chunk-level FTS поиск")
    print("-" * 80)
    fts_times = []
    for query in TEST_QUERIES["chunk_level_fts"]:
        times = await measure_search_performance(
            search_service,
            vault_name,
            query,
            "fts",
            RetrievalGranularity.CHUNK,
            iterations_per_query,
        )
        fts_times.extend(times)
        print(f"  Запрос: {query[:50]}... | Среднее: {statistics.mean(times):.1f} мс")
    
    fts_stats = calculate_percentiles(fts_times)
    results["tests"]["chunk_level_fts"] = {
        "times": fts_times,
        "stats": fts_stats,
        "target_p95": 400.0,
        "meets_target": fts_stats["p95"] < 400.0,
    }
    print(f"\n  P50: {fts_stats['p50']:.1f} мс")
    print(f"  P95: {fts_stats['p95']:.1f} мс {'✅' if fts_stats['p95'] < 400 else '❌'}")
    print(f"  P99: {fts_stats['p99']:.1f} мс")
    print(f"  Среднее: {fts_stats['mean']:.1f} мс")
    print()
    
    # Тест 4: Chunk-level hybrid поиск
    print("🔀 Тест 4: Chunk-level hybrid поиск")
    print("-" * 80)
    hybrid_times = []
    for query in TEST_QUERIES["chunk_level_hybrid"]:
        times = await measure_search_performance(
            search_service,
            vault_name,
            query,
            "hybrid",
            RetrievalGranularity.CHUNK,
            iterations_per_query,
        )
        hybrid_times.extend(times)
        print(f"  Запрос: {query[:50]}... | Среднее: {statistics.mean(times):.1f} мс")
    
    hybrid_stats = calculate_percentiles(hybrid_times)
    results["tests"]["chunk_level_hybrid"] = {
        "times": hybrid_times,
        "stats": hybrid_stats,
        "target_p95": 400.0,
        "meets_target": hybrid_stats["p95"] < 400.0,
    }
    print(f"\n  P50: {hybrid_stats['p50']:.1f} мс")
    print(f"  P95: {hybrid_stats['p95']:.1f} мс {'✅' if hybrid_stats['p95'] < 400 else '❌'}")
    print(f"  P99: {hybrid_stats['p99']:.1f} мс")
    print(f"  Среднее: {hybrid_stats['mean']:.1f} мс")
    print()
    
    # Итоговая статистика
    print("=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print()
    
    all_meet_target = all(
        test["meets_target"] for test in results["tests"].values()
    )
    
    print(f"Целевой P95: <400 мс")
    print()
    print("Результаты:")
    for test_name, test_data in results["tests"].items():
        status = "✅" if test_data["meets_target"] else "❌"
        print(f"  {test_name:30} P95: {test_data['stats']['p95']:6.1f} мс {status}")
    
    print()
    if all_meet_target:
        print("✅ ВСЕ ТЕСТЫ ПРОШЛИ ЦЕЛЕВОЙ ПОРОГ P95 <400 мс")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ ЦЕЛЕВОЙ ПОРОГ")
    
    # Очистка ресурсов
    await services.cleanup()
    
    return results


def save_results(results: dict[str, Any], output_file: Path) -> None:
    """Сохранение результатов в JSON."""
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n💾 Результаты сохранены в {output_file}")


def create_markdown_report(results: dict[str, Any], output_file: Path) -> None:
    """Создание markdown отчёта."""
    lines = [
        "# Отчёт о производительности поиска v5",
        "",
        f"**Дата:** {results['timestamp']}",
        f"**Vault:** {results['vault_name']}",
        f"**Итераций на запрос:** {results['iterations_per_query']}",
        "",
        "## Результаты",
        "",
        "| Тип поиска | P50 (мс) | P95 (мс) | P99 (мс) | Среднее (мс) | Цель P95 <400мс |",
        "|-------------|----------|----------|----------|--------------|-----------------|",
    ]
    
    for test_name, test_data in results["tests"].items():
        stats = test_data["stats"]
        status = "✅" if test_data["meets_target"] else "❌"
        lines.append(
            f"| {test_name} | {stats['p50']:.1f} | {stats['p95']:.1f} | "
            f"{stats['p99']:.1f} | {stats['mean']:.1f} | {status} |"
        )
    
    lines.extend([
        "",
        "## Детализация",
        "",
    ])
    
    for test_name, test_data in results["tests"].items():
        stats = test_data["stats"]
        lines.extend([
            f"### {test_name}",
            "",
            f"- **P50:** {stats['p50']:.1f} мс",
            f"- **P95:** {stats['p95']:.1f} мс",
            f"- **P99:** {stats['p99']:.1f} мс",
            f"- **Среднее:** {stats['mean']:.1f} мс",
            f"- **Медиана:** {stats['median']:.1f} мс",
            f"- **Мин:** {stats['min']:.1f} мс",
            f"- **Макс:** {stats['max']:.1f} мс",
            f"- **Целевой P95:** {'✅ Достигнуто' if test_data['meets_target'] else '❌ Не достигнуто'}",
            "",
        ])
    
    output_file.write_text("\n".join(lines))
    print(f"📄 Markdown отчёт сохранён в {output_file}")


async def main() -> None:
    """Главная функция."""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python test_performance_v5.py <vault_name> [iterations]")
        print("\nПример:")
        print("  python test_performance_v5.py test_vault 10")
        sys.exit(1)
    
    vault_name = sys.argv[1]
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    results = await _run_performance_test(vault_name, iterations_per_query=iterations)
    
    # Сохраняем результаты
    output_dir = Path(__file__).parent
    json_file = output_dir / "performance_test_results.json"
    markdown_file = output_dir / "performance_test_results.md"
    
    save_results(results, json_file)
    create_markdown_report(results, markdown_file)


if __name__ == "__main__":
    asyncio.run(main())

