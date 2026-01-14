"""Тестирование размера ответа поиска v5.

Измеряет размер ответа для разных типов запросов:
- Metadata-only запросы (document-level)
- Semantic запросы (chunk-level)
- Hybrid запросы (chunk-level)

Цель: ~1KB/doc для metadata-only вместо ~2KB/чанк
"""

import asyncio
import json
import statistics
from pathlib import Path
from typing import Any

from obsidian_kb.service_container import ServiceContainer
from obsidian_kb.types import RetrievalGranularity, SearchRequest


# Тестовые запросы
TEST_QUERIES = {
    "metadata_only": [
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
    "semantic": [
        "Python async programming",
        "database optimization techniques",
        "REST API design patterns",
        "machine learning algorithms",
        "web development best practices",
    ],
    "hybrid": [
        "Python async programming",
        "database optimization techniques",
        "REST API design patterns",
        "machine learning algorithms",
        "web development best practices",
    ],
}


def measure_response_size(response: Any, formatter: Any, format_type: str = "markdown") -> dict[str, int]:
    """Измерение размера ответа в разных форматах.
    
    Args:
        response: SearchResponse объект
        formatter: Форматтер результатов
        format_type: Тип формата ("markdown" или "json")
        
    Returns:
        Словарь с размерами в байтах
    """
    sizes = {}
    
    # Размер всего ответа
    if format_type == "markdown":
        formatted = formatter.format_markdown(response)
        sizes["total_bytes"] = len(formatted.encode("utf-8"))
        sizes["total_chars"] = len(formatted)
    else:
        formatted = formatter.format_json(response)
        formatted_str = json.dumps(formatted, ensure_ascii=False)
        sizes["total_bytes"] = len(formatted_str.encode("utf-8"))
        sizes["total_chars"] = len(formatted_str)
    
    # Размер на документ
    if response.total_found > 0:
        sizes["bytes_per_doc"] = sizes["total_bytes"] / response.total_found
        sizes["chars_per_doc"] = sizes["total_chars"] / response.total_found
    else:
        sizes["bytes_per_doc"] = 0
        sizes["chars_per_doc"] = 0
    
    # Размер метаданных (заголовок + метаинформация)
    header_size = len(f"## Результаты поиска: \"{response.request.query}\"\n".encode("utf-8"))
    meta_size = len(
        f"*{response.detected_intent.value} | {response.total_found} документов | {response.execution_time_ms:.0f} мс*\n"
        .encode("utf-8")
    )
    sizes["header_bytes"] = header_size + meta_size
    
    # Размер результатов (без заголовка)
    sizes["results_bytes"] = sizes["total_bytes"] - sizes["header_bytes"]
    if response.total_found > 0:
        sizes["bytes_per_result"] = sizes["results_bytes"] / response.total_found
    else:
        sizes["bytes_per_result"] = 0
    
    return sizes


async def _run_response_size_test(
    vault_name: str,
    iterations: int = 5,
) -> dict[str, Any]:
    """Тестирование размера ответа для разных типов запросов.
    
    Args:
        vault_name: Имя vault'а для тестирования
        iterations: Количество итераций для каждого запроса
        
    Returns:
        Словарь с результатами тестирования
    """
    print("📏 Запуск тестирования размера ответа поиска v5")
    print("=" * 80)
    print()
    
    # Инициализация сервисов
    print("📦 Инициализация сервисов...")
    services = ServiceContainer()
    search_service = services.search_service
    formatter = services.formatter
    
    results: dict[str, Any] = {
        "vault_name": vault_name,
        "timestamp": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
        "iterations": iterations,
        "tests": {},
    }
    
    # Тест 1: Metadata-only запросы (document-level)
    print("📋 Тест 1: Metadata-only запросы (document-level)")
    print("-" * 80)
    metadata_sizes_md = []
    metadata_sizes_json = []
    
    for query in TEST_QUERIES["metadata_only"]:
        request = SearchRequest(
            vault_name=vault_name,
            query=query,
            limit=10,
            granularity=RetrievalGranularity.DOCUMENT,
            include_content=False,  # Без контента для metadata-only
        )
        
        response = await search_service.search(request)
        
        # Измеряем размер в markdown
        sizes_md = measure_response_size(response, formatter, "markdown")
        metadata_sizes_md.append(sizes_md)
        
        # Измеряем размер в JSON
        sizes_json = measure_response_size(response, formatter, "json")
        metadata_sizes_json.append(sizes_json)
        
        print(f"  Запрос: {query[:50]}")
        print(f"    Найдено: {response.total_found} документов")
        print(f"    Markdown: {sizes_md['bytes_per_doc']:.0f} байт/док | {sizes_md['total_bytes']} байт всего")
        print(f"    JSON: {sizes_json['bytes_per_doc']:.0f} байт/док | {sizes_json['total_bytes']} байт всего")
    
    # Статистика для metadata-only
    if metadata_sizes_md:
        avg_bytes_per_doc_md = statistics.mean([s["bytes_per_doc"] for s in metadata_sizes_md])
        avg_bytes_per_doc_json = statistics.mean([s["bytes_per_doc"] for s in metadata_sizes_json])
        
        results["tests"]["metadata_only"] = {
            "markdown": {
                "avg_bytes_per_doc": avg_bytes_per_doc_md,
                "median_bytes_per_doc": statistics.median([s["bytes_per_doc"] for s in metadata_sizes_md]),
                "min_bytes_per_doc": min([s["bytes_per_doc"] for s in metadata_sizes_md]),
                "max_bytes_per_doc": max([s["bytes_per_doc"] for s in metadata_sizes_md]),
                "target_bytes_per_doc": 1024,  # 1KB
                "meets_target": avg_bytes_per_doc_md < 1024,
            },
            "json": {
                "avg_bytes_per_doc": avg_bytes_per_doc_json,
                "median_bytes_per_doc": statistics.median([s["bytes_per_doc"] for s in metadata_sizes_json]),
                "min_bytes_per_doc": min([s["bytes_per_doc"] for s in metadata_sizes_json]),
                "max_bytes_per_doc": max([s["bytes_per_doc"] for s in metadata_sizes_json]),
                "target_bytes_per_doc": 1024,
                "meets_target": avg_bytes_per_doc_json < 1024,
            },
        }
        
        print(f"\n  Средний размер (Markdown): {avg_bytes_per_doc_md:.0f} байт/док")
        print(f"  Средний размер (JSON): {avg_bytes_per_doc_json:.0f} байт/док")
        print(f"  Цель: <1024 байт/док (1KB)")
        status_md = "✅" if avg_bytes_per_doc_md < 1024 else "❌"
        status_json = "✅" if avg_bytes_per_doc_json < 1024 else "❌"
        print(f"  Статус (Markdown): {status_md}")
        print(f"  Статус (JSON): {status_json}")
    print()
    
    # Тест 2: Semantic запросы (chunk-level)
    print("🔍 Тест 2: Semantic запросы (chunk-level)")
    print("-" * 80)
    semantic_sizes_md = []
    semantic_sizes_json = []
    
    for query in TEST_QUERIES["semantic"]:
        request = SearchRequest(
            vault_name=vault_name,
            query=query,
            limit=10,
            granularity=RetrievalGranularity.CHUNK,
            search_type="vector",
            include_content=True,  # С контентом для chunk-level
        )
        
        response = await search_service.search(request)
        
        sizes_md = measure_response_size(response, formatter, "markdown")
        semantic_sizes_md.append(sizes_md)
        
        sizes_json = measure_response_size(response, formatter, "json")
        semantic_sizes_json.append(sizes_json)
        
        print(f"  Запрос: {query[:50]}")
        print(f"    Найдено: {response.total_found} документов")
        print(f"    Markdown: {sizes_md['bytes_per_doc']:.0f} байт/док | {sizes_md['total_bytes']} байт всего")
        print(f"    JSON: {sizes_json['bytes_per_doc']:.0f} байт/док | {sizes_json['total_bytes']} байт всего")
    
    if semantic_sizes_md:
        avg_bytes_per_doc_md = statistics.mean([s["bytes_per_doc"] for s in semantic_sizes_md])
        avg_bytes_per_doc_json = statistics.mean([s["bytes_per_doc"] for s in semantic_sizes_json])
        
        results["tests"]["semantic"] = {
            "markdown": {
                "avg_bytes_per_doc": avg_bytes_per_doc_md,
                "median_bytes_per_doc": statistics.median([s["bytes_per_doc"] for s in semantic_sizes_md]),
            },
            "json": {
                "avg_bytes_per_doc": avg_bytes_per_doc_json,
                "median_bytes_per_doc": statistics.median([s["bytes_per_doc"] for s in semantic_sizes_json]),
            },
        }
        
        print(f"\n  Средний размер (Markdown): {avg_bytes_per_doc_md:.0f} байт/док")
        print(f"  Средний размер (JSON): {avg_bytes_per_doc_json:.0f} байт/док")
    print()
    
    # Тест 3: Hybrid запросы (chunk-level)
    print("🔀 Тест 3: Hybrid запросы (chunk-level)")
    print("-" * 80)
    hybrid_sizes_md = []
    hybrid_sizes_json = []
    
    for query in TEST_QUERIES["hybrid"]:
        request = SearchRequest(
            vault_name=vault_name,
            query=query,
            limit=10,
            granularity=RetrievalGranularity.CHUNK,
            search_type="hybrid",
            include_content=True,
        )
        
        response = await search_service.search(request)
        
        sizes_md = measure_response_size(response, formatter, "markdown")
        hybrid_sizes_md.append(sizes_md)
        
        sizes_json = measure_response_size(response, formatter, "json")
        hybrid_sizes_json.append(sizes_json)
        
        print(f"  Запрос: {query[:50]}")
        print(f"    Найдено: {response.total_found} документов")
        print(f"    Markdown: {sizes_md['bytes_per_doc']:.0f} байт/док | {sizes_md['total_bytes']} байт всего")
        print(f"    JSON: {sizes_json['bytes_per_doc']:.0f} байт/док | {sizes_json['total_bytes']} байт всего")
    
    if hybrid_sizes_md:
        avg_bytes_per_doc_md = statistics.mean([s["bytes_per_doc"] for s in hybrid_sizes_md])
        avg_bytes_per_doc_json = statistics.mean([s["bytes_per_doc"] for s in hybrid_sizes_json])
        
        results["tests"]["hybrid"] = {
            "markdown": {
                "avg_bytes_per_doc": avg_bytes_per_doc_md,
                "median_bytes_per_doc": statistics.median([s["bytes_per_doc"] for s in hybrid_sizes_md]),
            },
            "json": {
                "avg_bytes_per_doc": avg_bytes_per_doc_json,
                "median_bytes_per_doc": statistics.median([s["bytes_per_doc"] for s in hybrid_sizes_json]),
            },
        }
        
        print(f"\n  Средний размер (Markdown): {avg_bytes_per_doc_md:.0f} байт/док")
        print(f"  Средний размер (JSON): {avg_bytes_per_doc_json:.0f} байт/док")
    print()
    
    # Итоговая статистика
    print("=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print()
    
    if "metadata_only" in results["tests"]:
        md_meta = results["tests"]["metadata_only"]["markdown"]
        json_meta = results["tests"]["metadata_only"]["json"]
        
        print("Metadata-only запросы (document-level):")
        print(f"  Markdown: {md_meta['avg_bytes_per_doc']:.0f} байт/док (цель: <1024)")
        print(f"  JSON: {json_meta['avg_bytes_per_doc']:.0f} байт/док (цель: <1024)")
        print()
        
        # Сравнение с chunk-level (если есть)
        if "semantic" in results["tests"]:
            md_sem = results["tests"]["semantic"]["markdown"]
            reduction = ((md_sem["avg_bytes_per_doc"] - md_meta["avg_bytes_per_doc"]) / md_sem["avg_bytes_per_doc"] * 100) if md_sem["avg_bytes_per_doc"] > 0 else 0
            print(f"  Уменьшение размера по сравнению с chunk-level: {reduction:.1f}%")
            print()
    
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
        "# Отчёт о размере ответа поиска v5",
        "",
        f"**Дата:** {results['timestamp']}",
        f"**Vault:** {results['vault_name']}",
        "",
        "## Результаты",
        "",
        "| Тип запроса | Формат | Средний размер (байт/док) | Медиана | Цель <1KB |",
        "|-------------|--------|---------------------------|---------|-----------|",
    ]
    
    for test_name, test_data in results["tests"].items():
        for format_type in ["markdown", "json"]:
            if format_type in test_data:
                fmt_data = test_data[format_type]
                target = fmt_data.get("target_bytes_per_doc", None)
                meets_target = fmt_data.get("meets_target", None)
                status = "✅" if meets_target else ("N/A" if target is None else "❌")
                target_str = f"<{target}" if target else "N/A"
                
                lines.append(
                    f"| {test_name} | {format_type} | {fmt_data['avg_bytes_per_doc']:.0f} | "
                    f"{fmt_data['median_bytes_per_doc']:.0f} | {status} |"
                )
    
    lines.extend([
        "",
        "## Детализация",
        "",
    ])
    
    for test_name, test_data in results["tests"].items():
        lines.extend([
            f"### {test_name}",
            "",
        ])
        
        for format_type in ["markdown", "json"]:
            if format_type in test_data:
                fmt_data = test_data[format_type]
                lines.extend([
                    f"#### {format_type.upper()}",
                    "",
                    f"- **Средний размер:** {fmt_data['avg_bytes_per_doc']:.0f} байт/док",
                    f"- **Медиана:** {fmt_data['median_bytes_per_doc']:.0f} байт/док",
                ])
                
                if "min_bytes_per_doc" in fmt_data:
                    lines.extend([
                        f"- **Мин:** {fmt_data['min_bytes_per_doc']:.0f} байт/док",
                        f"- **Макс:** {fmt_data['max_bytes_per_doc']:.0f} байт/док",
                    ])
                
                if "target_bytes_per_doc" in fmt_data:
                    lines.append(f"- **Цель:** <{fmt_data['target_bytes_per_doc']} байт/док")
                    lines.append(f"- **Статус:** {'✅ Достигнуто' if fmt_data.get('meets_target') else '❌ Не достигнуто'}")
                
                lines.append("")
    
    output_file.write_text("\n".join(lines))
    print(f"📄 Markdown отчёт сохранён в {output_file}")


async def main() -> None:
    """Главная функция."""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python test_response_size.py <vault_name>")
        print("\nПример:")
        print("  python test_response_size.py test_vault")
        sys.exit(1)
    
    vault_name = sys.argv[1]
    
    results = await _run_response_size_test(vault_name)
    
    # Сохраняем результаты
    output_dir = Path(__file__).parent
    json_file = output_dir / "response_size_test_results.json"
    markdown_file = output_dir / "response_size_test_results.md"
    
    save_results(results, json_file)
    create_markdown_report(results, markdown_file)


if __name__ == "__main__":
    asyncio.run(main())

