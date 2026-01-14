#!/usr/bin/env python3
"""Скрипт для профилирования производительности поиска.

Использует cProfile для детального анализа производительности поисковых запросов.
"""

import asyncio
import cProfile
import json
import pstats
import sys
import time
from pathlib import Path
from typing import Any

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from obsidian_kb.service_container import get_service_container, reset_service_container
from obsidian_kb.types import SearchRequest


async def profile_search(
    vault_name: str,
    query: str,
    search_type: str = "hybrid",
    iterations: int = 5,
    output_file: str | None = None,
) -> dict[str, Any]:
    """Профилирование поискового запроса.
    
    Args:
        vault_name: Имя vault'а
        query: Поисковый запрос
        search_type: Тип поиска (hybrid, vector, fts)
        iterations: Количество итераций для усреднения
        output_file: Путь к файлу для сохранения результатов профилирования
        
    Returns:
        Словарь с результатами профилирования
    """
    reset_service_container()
    services = get_service_container()
    
    # Создаем профилер
    profiler = cProfile.Profile()
    
    times = []
    results_count = []
    
    print(f"\n🔍 Профилирование поиска: '{query}'")
    print(f"   Vault: {vault_name}")
    print(f"   Тип поиска: {search_type}")
    print(f"   Итераций: {iterations}")
    print("=" * 80)
    
    # Разогрев (warmup)
    print("🔥 Разогрев...")
    try:
        request = SearchRequest(
            vault_name=vault_name,
            query=query,
            search_type=search_type,
        )
        await services.search_service.search(request)
    except Exception as e:
        print(f"⚠️  Ошибка при разогреве: {e}")
        return {}
    
    # Профилирование
    print(f"\n📊 Профилирование {iterations} итераций...")
    profiler.enable()
    
    for i in range(iterations):
        start_time = time.time()
        try:
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                search_type=search_type,
            )
            response = await services.search_service.search(request)
            elapsed = time.time() - start_time
            times.append(elapsed * 1000)  # В миллисекундах
            results_count.append(len(response.results))
            print(f"   Итерация {i+1}/{iterations}: {elapsed*1000:.1f} мс, найдено: {len(response.results)}")
        except Exception as e:
            print(f"   ⚠️  Ошибка на итерации {i+1}: {e}")
            profiler.disable()
            return {}
    
    profiler.disable()
    
    # Статистика времени выполнения
    if times:
        times_sorted = sorted(times)
        p50 = times_sorted[int(len(times_sorted) * 0.50)]
        p95 = times_sorted[int(len(times_sorted) * 0.95)]
        p99 = times_sorted[int(len(times_sorted) * 0.99)]
        avg = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print("\n" + "=" * 80)
        print("📈 СТАТИСТИКА ВРЕМЕНИ ВЫПОЛНЕНИЯ")
        print("=" * 80)
        print(f"   Среднее:     {avg:.1f} мс")
        print(f"   Минимум:     {min_time:.1f} мс")
        print(f"   Максимум:    {max_time:.1f} мс")
        print(f"   P50:         {p50:.1f} мс")
        print(f"   P95:         {p95:.1f} мс")
        print(f"   P99:         {p99:.1f} мс")
        print(f"   Найдено результатов (среднее): {sum(results_count) / len(results_count):.1f}")
    else:
        print("⚠️  Нет данных для статистики")
        return {}
    
    # Анализ профиля
    print("\n" + "=" * 80)
    print("🔬 ТОП-20 ФУНКЦИЙ ПО ВРЕМЕНИ ВЫПОЛНЕНИЯ")
    print("=" * 80)
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    
    # Сохранение результатов
    results = {
        "query": query,
        "vault_name": vault_name,
        "search_type": search_type,
        "iterations": iterations,
        "times_ms": times,
        "statistics": {
            "avg": avg,
            "min": min_time,
            "max": max_time,
            "p50": p50,
            "p95": p95,
            "p99": p99,
        },
        "results_count": results_count,
        "avg_results": sum(results_count) / len(results_count) if results_count else 0,
    }
    
    if output_file:
        # Сохраняем статистику профилирования
        stats_file = output_file.replace('.json', '_profile.stats')
        profiler.dump_stats(stats_file)
        print(f"\n💾 Статистика профилирования сохранена: {stats_file}")
        print(f"   Для просмотра: python -m pstats {stats_file}")
        
        # Сохраняем метрики
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Метрики сохранены: {output_file}")
    
    return results


async def profile_multiple_queries(
    vault_name: str,
    queries: list[str],
    search_type: str = "hybrid",
    iterations: int = 3,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Профилирование нескольких запросов.
    
    Args:
        vault_name: Имя vault'а
        queries: Список поисковых запросов
        search_type: Тип поиска
        iterations: Количество итераций для каждого запроса
        output_dir: Директория для сохранения результатов
        
    Returns:
        Сводная статистика по всем запросам
    """
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    all_times = []
    all_results = {}
    
    print(f"\n🚀 Профилирование {len(queries)} запросов")
    print("=" * 80)
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Запрос: '{query}'")
        
        output_file = None
        if output_dir:
            safe_query = query.replace('/', '_').replace(' ', '_')[:50]
            output_file = str(output_dir / f"profile_{safe_query}.json")
        
        result = await profile_search(
            vault_name=vault_name,
            query=query,
            search_type=search_type,
            iterations=iterations,
            output_file=output_file,
        )
        
        if result and "times_ms" in result:
            all_times.extend(result["times_ms"])
            all_results[query] = result
    
    # Сводная статистика
    if all_times:
        all_times_sorted = sorted(all_times)
        p50 = all_times_sorted[int(len(all_times_sorted) * 0.50)]
        p95 = all_times_sorted[int(len(all_times_sorted) * 0.95)]
        p99 = all_times_sorted[int(len(all_times_sorted) * 0.99)]
        avg = sum(all_times) / len(all_times)
        
        summary = {
            "total_queries": len(queries),
            "total_iterations": len(all_times),
            "statistics": {
                "avg": avg,
                "min": min(all_times),
                "max": max(all_times),
                "p50": p50,
                "p95": p95,
                "p99": p99,
            },
            "queries": all_results,
        }
        
        print("\n" + "=" * 80)
        print("📊 СВОДНАЯ СТАТИСТИКА ПО ВСЕМ ЗАПРОСАМ")
        print("=" * 80)
        print(f"   Всего запросов: {len(queries)}")
        print(f"   Всего итераций: {len(all_times)}")
        print(f"   Среднее время:  {avg:.1f} мс")
        print(f"   P50:            {p50:.1f} мс")
        print(f"   P95:            {p95:.1f} мс")
        print(f"   P99:            {p99:.1f} мс")
        
        if output_dir:
            summary_file = output_dir / "profile_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Сводная статистика сохранена: {summary_file}")
        
        return summary
    
    return {}


async def main():
    """Основная функция."""
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  {sys.argv[0]} <vault_name> [query] [search_type] [iterations]")
        print("\nПримеры:")
        print(f"  {sys.argv[0]} my-vault 'python programming' hybrid 5")
        print(f"  {sys.argv[0]} my-vault --queries-file queries.json")
        sys.exit(1)
    
    vault_name = sys.argv[1]
    
    # Проверяем, есть ли файл с запросами
    if len(sys.argv) > 2 and sys.argv[2] == "--queries-file":
        queries_file = Path(sys.argv[3])
        if not queries_file.exists():
            print(f"⚠️  Файл не найден: {queries_file}")
            sys.exit(1)
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            queries = data.get("queries", [])
        
        output_dir = Path("profile_results")
        await profile_multiple_queries(
            vault_name=vault_name,
            queries=queries,
            search_type=sys.argv[4] if len(sys.argv) > 4 else "hybrid",
            iterations=int(sys.argv[5]) if len(sys.argv) > 5 else 3,
            output_dir=output_dir,
        )
    else:
        # Один запрос
        query = sys.argv[2] if len(sys.argv) > 2 else "python programming"
        search_type = sys.argv[3] if len(sys.argv) > 3 else "hybrid"
        iterations = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        
        output_file = f"profile_{query.replace(' ', '_')[:30]}.json"
        await profile_search(
            vault_name=vault_name,
            query=query,
            search_type=search_type,
            iterations=iterations,
            output_file=output_file,
        )
    
    # Закрываем соединения
    try:
        services = get_service_container()
        await services.cleanup()
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())

