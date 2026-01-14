"""Автоматизированное тестирование Intent Detection.

Скрипт для проверки точности определения intent для различных типов запросов.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from obsidian_kb.search.intent_detector import IntentDetector
from obsidian_kb.types import SearchIntent


# Тестовые запросы
TEST_QUERIES = {
    SearchIntent.METADATA_FILTER: [
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
        "tags:work tags:priority",
        "type:article",
        "tags:archive",
        "tags:project tags:completed",
        "type:template",
        "tags:learning",
        "tags:health tags:exercise",
        "type:recipe",
        "tags:finance tags:budget",
        "tags:travel tags:planning",
    ],
    SearchIntent.KNOWN_ITEM: [
        "README.md",
        "CHANGELOG",
        "LICENSE",
        "CONTRIBUTING.md",
        "INSTALLATION",
        "TODO.md",
        "api_design.md",
        "configuration.md",
        "database_queries.md",
        "docker_setup.md",
        "javascript_guide.md",
        "python_tutorial.md",
        "ARCHITECTURE.md",
        "DEVELOPER_GUIDE.md",
        "API_DOCUMENTATION.md",
        "QUICK_START.md",
        "TROUBLESHOOTING.md",
        "BEST_PRACTICES.md",
        "FAQ.md",
        "README",
    ],
    SearchIntent.PROCEDURAL: [
        "how to install",
        "как настроить",
        "steps to configure",
        "guide to setup",
        "tutorial on using",
        "инструкция по установке",
        "how to use",
        "как создать",
        "setup guide",
        "installation instructions",
        "how to configure settings",
        "настроить подключение",
        "tutorial for beginners",
        "how to deploy",
        "инструкция по настройке",
        "guide to getting started",
        "how to build",
        "как установить",
        "setup tutorial",
        "how to get started",
    ],
    SearchIntent.EXPLORATORY: [
        "что такое",
        "what is",
        "как работает",
        "how does it work",
        "почему используется",
        "why use",
        "когда применять",
        "when to use",
        "где найти",
        "where to find",
        "кто использует",
        "who uses",
        "какой выбрать",
        "which one to choose",
        "сколько стоит",
        "how much does it cost",
        "зачем нужен",
        "what is the purpose",
        "как выбрать",
        "how to choose",
    ],
    SearchIntent.SEMANTIC: [
        "Python async programming",
        "database optimization techniques",
        "REST API design patterns",
        "machine learning algorithms",
        "web development best practices",
        "контейнеризация приложений",
        "distributed systems architecture",
        "security best practices",
        "performance optimization",
        "code review guidelines",
        "тестирование программного обеспечения",
        "microservices architecture",
        "data structures and algorithms",
        "cloud computing strategies",
        "agile development methodologies",
        "continuous integration and deployment",
        "системы управления версиями",
        "monitoring and logging",
        "scalability patterns",
        "user interface design principles",
    ],
}


def parse_filters(query: str) -> dict[str, Any]:
    """Парсинг фильтров из запроса."""
    filters: dict[str, Any] = {}
    
    # Простой парсинг тегов
    if "tags:" in query:
        tags = []
        for part in query.split():
            if part.startswith("tags:"):
                tag = part.replace("tags:", "").strip()
                if tag:
                    tags.append(tag)
        if tags:
            filters["tags"] = tags
    
    # Парсинг типа
    if "type:" in query:
        for part in query.split():
            if part.startswith("type:"):
                doc_type = part.replace("type:", "").strip()
                if doc_type:
                    filters["doc_type"] = doc_type
    
    return filters


@pytest.mark.asyncio
async def test_intent_detection() -> dict[str, Any]:
    """Тестирование Intent Detection."""
    detector = IntentDetector()
    results: dict[str, Any] = {
        "total": 0,
        "correct": 0,
        "incorrect": 0,
        "by_intent": {},
        "details": [],
    }
    
    for expected_intent, queries in TEST_QUERIES.items():
        intent_name = expected_intent.value
        results["by_intent"][intent_name] = {
            "total": len(queries),
            "correct": 0,
            "incorrect": 0,
            "low_confidence": 0,
        }
        
        for query in queries:
            results["total"] += 1
            
            # Парсим фильтры
            parsed_filters = parse_filters(query)
            
            # Извлекаем текстовый запрос (без фильтров)
            text_query = query
            for part in query.split():
                if part.startswith("tags:") or part.startswith("type:"):
                    text_query = text_query.replace(part, "").strip()
            
            # Определяем intent
            intent_result = detector.detect(text_query, parsed_filters)
            
            # Проверяем результат
            is_correct = intent_result.intent == expected_intent
            has_low_confidence = intent_result.confidence < 0.7
            
            if is_correct:
                results["correct"] += 1
                results["by_intent"][intent_name]["correct"] += 1
            else:
                results["incorrect"] += 1
                results["by_intent"][intent_name]["incorrect"] += 1
            
            if has_low_confidence:
                results["by_intent"][intent_name]["low_confidence"] += 1
            
            # Сохраняем детали
            results["details"].append({
                "query": query,
                "expected": expected_intent.value,
                "detected": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "correct": is_correct,
                "low_confidence": has_low_confidence,
                "signals": intent_result.signals,
            })
    
    # Вычисляем точность
    results["accuracy"] = (results["correct"] / results["total"] * 100) if results["total"] > 0 else 0
    
    return results


def print_results(results: dict[str, Any]) -> None:
    """Вывод результатов тестирования."""
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ INTENT DETECTION")
    print("=" * 80)
    print()
    
    print(f"Всего запросов: {results['total']}")
    print(f"Правильных: {results['correct']}")
    print(f"Неправильных: {results['incorrect']}")
    print(f"Точность: {results['accuracy']:.2f}%")
    print(f"Целевая точность: >90%")
    print()
    
    if results['accuracy'] >= 90:
        print("✅ ЦЕЛЬ ДОСТИГНУТА!")
    else:
        print("❌ Цель не достигнута")
    print()
    
    print("-" * 80)
    print("ДЕТАЛИЗАЦИЯ ПО ТИПАМ INTENT:")
    print("-" * 80)
    print()
    
    for intent_name, stats in results["by_intent"].items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{intent_name}:")
        print(f"  Всего: {stats['total']}")
        print(f"  Правильных: {stats['correct']}")
        print(f"  Неправильных: {stats['incorrect']}")
        print(f"  Низкий confidence: {stats['low_confidence']}")
        print(f"  Точность: {accuracy:.2f}%")
        print()
    
    # Проблемные случаи
    incorrect = [r for r in results["details"] if not r["correct"]]
    low_confidence = [r for r in results["details"] if r["low_confidence"]]
    
    if incorrect:
        print("-" * 80)
        print("ПРОБЛЕМНЫЕ СЛУЧАИ (неправильное определение):")
        print("-" * 80)
        for r in incorrect:
            print(f"  Запрос: {r['query']}")
            print(f"    Ожидалось: {r['expected']}")
            print(f"    Определено: {r['detected']}")
            print(f"    Confidence: {r['confidence']:.2f}")
            print()
    
    if low_confidence:
        print("-" * 80)
        print("СЛУЧАИ С НИЗКИМ CONFIDENCE (<0.7):")
        print("-" * 80)
        for r in low_confidence:
            print(f"  Запрос: {r['query']}")
            print(f"    Intent: {r['detected']}")
            print(f"    Confidence: {r['confidence']:.2f}")
            print()


def save_results(results: dict[str, Any], output_file: Path) -> None:
    """Сохранение результатов в JSON."""
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Результаты сохранены в {output_file}")


async def main() -> None:
    """Главная функция."""
    print("Запуск тестирования Intent Detection...")
    print()
    
    results = await test_intent_detection()
    print_results(results)
    
    # Сохраняем результаты
    output_file = Path(__file__).parent / "intent_test_results.json"
    save_results(results, output_file)
    
    # Создаём markdown отчёт
    markdown_file = Path(__file__).parent / "intent_test_results.md"
    create_markdown_report(results, markdown_file)


def create_markdown_report(results: dict[str, Any], output_file: Path) -> None:
    """Создание markdown отчёта."""
    lines = [
        "# Результаты тестирования Intent Detection",
        "",
        f"**Дата:** {results.get('date', 'N/A')}",
        f"**Всего запросов:** {results['total']}",
        f"**Правильных:** {results['correct']}",
        f"**Неправильных:** {results['incorrect']}",
        f"**Точность:** {results['accuracy']:.2f}%",
        f"**Целевая точность:** >90%",
        "",
        "## Детализация по типам intent",
        "",
    ]
    
    for intent_name, stats in results["by_intent"].items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        lines.extend([
            f"### {intent_name}",
            "",
            f"- Всего: {stats['total']}",
            f"- Правильных: {stats['correct']}",
            f"- Неправильных: {stats['incorrect']}",
            f"- Низкий confidence: {stats['low_confidence']}",
            f"- Точность: {accuracy:.2f}%",
            "",
        ])
    
    # Проблемные случаи
    incorrect = [r for r in results["details"] if not r["correct"]]
    if incorrect:
        lines.extend([
            "## Проблемные случаи (неправильное определение)",
            "",
            "| Запрос | Ожидалось | Определено | Confidence |",
            "|--------|-----------|------------|------------|",
        ])
        for r in incorrect:
            lines.append(
                f"| {r['query']} | {r['expected']} | {r['detected']} | {r['confidence']:.2f} |"
            )
        lines.append("")
    
    output_file.write_text("\n".join(lines))
    print(f"Markdown отчёт сохранён в {output_file}")


if __name__ == "__main__":
    asyncio.run(main())

