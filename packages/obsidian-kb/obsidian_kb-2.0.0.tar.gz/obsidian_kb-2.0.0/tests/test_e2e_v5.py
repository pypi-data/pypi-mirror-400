"""End-to-end тестирование системы поиска v5.

Проверяет полный flow:
- Индексация vault'а
- Различные типы поисковых запросов
- Multi-vault поиск
- Форматирование результатов
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any

from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.service_container import ServiceContainer, reset_service_container
from obsidian_kb.types import RetrievalGranularity, SearchRequest
from obsidian_kb.vault_indexer import VaultIndexer


def create_test_vault(vault_path: Path) -> None:
    """Создание тестового vault'а с разнообразными файлами.
    
    Args:
        vault_path: Путь к vault'у
    """
    vault_path.mkdir(parents=True, exist_ok=True)
    
    # Файл 1: Metadata-only документ
    (vault_path / "person1.md").write_text("""---
type: person
tags: [person, team, developer]
created: 2024-01-01
status: active
---

# Иван Иванов

Разработчик команды. Работает над проектом X.

[[project-x]] [[meeting-2024-01-15]]
""")
    
    # Файл 2: Документ с тегами
    (vault_path / "person2.md").write_text("""---
type: person
tags: [person, manager]
created: 2024-02-01
---

# Петр Петров

Менеджер проекта. Участвует в #meeting-2024-01-15.
""")
    
    # Файл 3: Meeting документ
    (vault_path / "meeting.md").write_text("""---
type: meeting
tags: [meeting, important]
created: 2024-01-15
---

# Встреча команды

Участники: [[person1]] [[person2]]

Обсуждали проект X и планы на будущее.
""")
    
    # Файл 4: Технический документ (для semantic поиска)
    (vault_path / "python_guide.md").write_text("""---
type: guide
tags: [python, programming, tutorial]
created: 2024-01-10
---

# Python Async Programming Guide

## Introduction

Python async programming позволяет писать асинхронный код с использованием async/await.

## Основы

```python
import asyncio

async def main():
    await asyncio.sleep(1)
    print("Hello, async world!")

asyncio.run(main())
```

## Best Practices

- Используйте async/await для I/O операций
- Избегайте блокирующих операций в async функциях
- Используйте asyncio.gather() для параллельного выполнения
""")
    
    # Файл 5: README файл (для known-item поиска)
    (vault_path / "README.md").write_text("""---
type: documentation
tags: [readme, docs]
---

# Test Vault

Это тестовый vault для E2E тестирования.

## Features

- Индексация документов
- Поиск по метаданным
- Семантический поиск
""")
    
    # Файл 6: How-to документ (для procedural поиска)
    (vault_path / "how_to_setup.md").write_text("""---
type: guide
tags: [setup, tutorial]
---

# How to Setup

## Шаги установки

1. Установите зависимости
2. Настройте конфигурацию
3. Запустите индексацию

## Требования

- Python 3.12+
- Ollama сервер
""")


async def _run_indexing_test(
    services: ServiceContainer,
    vault_path: Path,
    vault_name: str,
) -> dict[str, Any]:
    """Тест индексации vault'а.
    
    Args:
        services: Контейнер сервисов
        vault_path: Путь к vault'у
        vault_name: Имя vault'а
        
    Returns:
        Результаты тестирования
    """
    print("📦 Тест 1: Индексация vault'а")
    print("-" * 80)
    
    try:
        indexer = VaultIndexer(vault_path, vault_name)
        embedding_cache = EmbeddingCache()
        
        # Индексируем vault
        chunks, embeddings, stats = await index_with_cache(
            vault_name=vault_name,
            indexer=indexer,
            embedding_service=services.embedding_service,
            db_manager=services.db_manager,
            embedding_cache=embedding_cache,
            only_changed=False,
        )
        
        # Сохраняем в БД
        await services.db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
        # Проверяем статистику
        vault_stats = await services.db_manager.get_vault_stats(vault_name)
        
        print(f"✅ Индексация завершена успешно")
        print(f"   Файлов: {vault_stats.file_count}")
        print(f"   Чанков: {vault_stats.chunk_count}")
        print(f"   Тегов: {len(vault_stats.tags)}")
        print()
        
        return {
            "success": True,
            "files_indexed": vault_stats.file_count,
            "chunks_indexed": vault_stats.chunk_count,
            "tags_found": len(vault_stats.tags),
        }
    except Exception as e:
        print(f"❌ Ошибка индексации: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def _run_metadata_search_test(
    services: ServiceContainer,
    vault_name: str,
) -> dict[str, Any]:
    """Тест metadata-only поиска (document-level).
    
    Args:
        services: Контейнер сервисов
        vault_name: Имя vault'а
        
    Returns:
        Результаты тестирования
    """
    print("📋 Тест 2: Metadata-only поиск (document-level)")
    print("-" * 80)
    
    test_queries = [
        "tags:person",
        "type:meeting",
        "tags:meeting tags:important",
    ]
    
    results = []
    for query in test_queries:
        try:
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                limit=10,
                granularity=RetrievalGranularity.DOCUMENT,
                include_content=False,
            )
            
            response = await services.search_service.search(request)
            
            print(f"  Запрос: {query}")
            print(f"    Найдено: {response.total_found} документов")
            print(f"    Intent: {response.detected_intent.value}")
            print(f"    Strategy: {response.strategy_used}")
            print(f"    Время: {response.execution_time_ms:.1f} мс")
            
            results.append({
                "query": query,
                "success": True,
                "found": response.total_found,
                "intent": response.detected_intent.value,
                "strategy": response.strategy_used,
                "time_ms": response.execution_time_ms,
            })
        except Exception as e:
            print(f"  ❌ Ошибка для запроса '{query}': {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e),
            })
    
    print()
    return {"queries": results}


async def _run_semantic_search_test(
    services: ServiceContainer,
    vault_name: str,
) -> dict[str, Any]:
    """Тест семантического поиска (chunk-level).
    
    Args:
        services: Контейнер сервисов
        vault_name: Имя vault'а
        
    Returns:
        Результаты тестирования
    """
    print("🔍 Тест 3: Семантический поиск (chunk-level)")
    print("-" * 80)
    
    test_queries = [
        "Python async programming",
        "meeting participants",
        "project development",
    ]
    
    results = []
    for query in test_queries:
        try:
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                limit=10,
                granularity=RetrievalGranularity.CHUNK,
                search_type="vector",
                include_content=True,
            )
            
            response = await services.search_service.search(request)
            
            print(f"  Запрос: {query}")
            print(f"    Найдено: {response.total_found} документов")
            print(f"    Intent: {response.detected_intent.value}")
            print(f"    Strategy: {response.strategy_used}")
            print(f"    Время: {response.execution_time_ms:.1f} мс")
            
            if response.results:
                print(f"    Топ результат: {response.results[0].document.title}")
                print(f"    Score: {response.results[0].score.value:.2f}")
            
            results.append({
                "query": query,
                "success": True,
                "found": response.total_found,
                "intent": response.detected_intent.value,
                "strategy": response.strategy_used,
                "time_ms": response.execution_time_ms,
                "top_score": response.results[0].score.value if response.results else 0.0,
            })
        except Exception as e:
            print(f"  ❌ Ошибка для запроса '{query}': {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e),
            })
    
    print()
    return {"queries": results}


async def _run_hybrid_search_test(
    services: ServiceContainer,
    vault_name: str,
) -> dict[str, Any]:
    """Тест гибридного поиска (chunk-level hybrid).
    
    Args:
        services: Контейнер сервисов
        vault_name: Имя vault'а
        
    Returns:
        Результаты тестирования
    """
    print("🔀 Тест 4: Гибридный поиск (chunk-level hybrid)")
    print("-" * 80)
    
    test_queries = [
        "Python async",
        "meeting team",
    ]
    
    results = []
    for query in test_queries:
        try:
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                limit=10,
                granularity=RetrievalGranularity.CHUNK,
                search_type="hybrid",
                include_content=True,
            )
            
            response = await services.search_service.search(request)
            
            print(f"  Запрос: {query}")
            print(f"    Найдено: {response.total_found} документов")
            print(f"    Intent: {response.detected_intent.value}")
            print(f"    Strategy: {response.strategy_used}")
            print(f"    Время: {response.execution_time_ms:.1f} мс")
            
            results.append({
                "query": query,
                "success": True,
                "found": response.total_found,
                "intent": response.detected_intent.value,
                "strategy": response.strategy_used,
                "time_ms": response.execution_time_ms,
            })
        except Exception as e:
            print(f"  ❌ Ошибка для запроса '{query}': {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e),
            })
    
    print()
    return {"queries": results}


async def _run_multi_vault_search_test(
    services: ServiceContainer,
    vault_names: list[str],
) -> dict[str, Any]:
    """Тест multi-vault поиска.
    
    Args:
        services: Контейнер сервисов
        vault_names: Список имён vault'ов
        
    Returns:
        Результаты тестирования
    """
    print("🌐 Тест 5: Multi-vault поиск")
    print("-" * 80)
    
    if len(vault_names) < 2:
        print("⚠️  Недостаточно vault'ов для multi-vault теста (нужно минимум 2)")
        return {"skipped": True, "reason": "insufficient_vaults"}
    
    try:
        request = SearchRequest(
            vault_name=vault_names[0],  # Используем первый vault для запроса
            query="person",
            limit=10,
            granularity=RetrievalGranularity.AUTO,
        )
        
        response = await services.search_service.search_multi_vault(
            vault_names=vault_names,
            request=request,
        )
        
        print(f"  Запрос: 'person'")
        print(f"  Vault'ов: {len(vault_names)}")
        print(f"    Найдено: {response.total_found} документов")
        print(f"    Intent: {response.detected_intent.value}")
        print(f"    Strategy: {response.strategy_used}")
        print(f"    Время: {response.execution_time_ms:.1f} мс")
        print()
        
        return {
            "success": True,
            "vaults": len(vault_names),
            "found": response.total_found,
            "time_ms": response.execution_time_ms,
        }
    except Exception as e:
        print(f"  ❌ Ошибка multi-vault поиска: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def _run_formatting_test(
    services: ServiceContainer,
    vault_name: str,
) -> dict[str, Any]:
    """Тест форматирования результатов.
    
    Args:
        services: Контейнер сервисов
        vault_name: Имя vault'а
        
    Returns:
        Результаты тестирования
    """
    print("📄 Тест 6: Форматирование результатов")
    print("-" * 80)
    
    try:
        request = SearchRequest(
            vault_name=vault_name,
            query="tags:person",
            limit=5,
            granularity=RetrievalGranularity.DOCUMENT,
        )
        
        response = await services.search_service.search(request)
        formatter = services.formatter
        
        # Тест Markdown форматирования
        markdown = formatter.format_markdown(response)
        markdown_size = len(markdown.encode("utf-8"))
        
        # Тест JSON форматирования
        json_data = formatter.format_json(response)
        json_str = json.dumps(json_data, ensure_ascii=False)
        json_size = len(json_str.encode("utf-8"))
        
        print(f"  Markdown размер: {markdown_size} байт")
        print(f"  JSON размер: {json_size} байт")
        print(f"  Результатов: {response.total_found}")
        print()
        
        # Проверяем структуру
        markdown_valid = "## Результаты поиска" in markdown
        json_valid = "query" in json_data and "results" in json_data
        
        return {
            "success": True,
            "markdown_size": markdown_size,
            "json_size": json_size,
            "markdown_valid": markdown_valid,
            "json_valid": json_valid,
        }
    except Exception as e:
        print(f"  ❌ Ошибка форматирования: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def run_e2e_tests(
    vault_path: Path | None = None,
    vault_name: str = "test_vault_e2e",
    use_temp_vault: bool = True,
) -> dict[str, Any]:
    """Запуск всех E2E тестов.
    
    Args:
        vault_path: Путь к vault'у (если None, создаётся временный)
        vault_name: Имя vault'а
        use_temp_vault: Использовать временный vault
        
    Returns:
        Результаты всех тестов
    """
    print("=" * 80)
    print("END-TO-END ТЕСТИРОВАНИЕ СИСТЕМЫ ПОИСКА V5")
    print("=" * 80)
    print()
    
    # Создаём временный vault если нужно
    temp_dir = None
    if use_temp_vault and vault_path is None:
        temp_dir = tempfile.TemporaryDirectory()
        vault_path = Path(temp_dir.name) / vault_name
        create_test_vault(vault_path)
        print(f"📁 Создан временный vault: {vault_path}")
        print()
    
    if vault_path is None:
        raise ValueError("vault_path должен быть указан или use_temp_vault=True")
    
    # Сбрасываем глобальный контейнер
    reset_service_container()
    
    # Создаём временную БД
    temp_db_dir = tempfile.TemporaryDirectory()
    db_path = Path(temp_db_dir.name) / "test_db.lance"
    
    # Инициализируем сервисы
    services = ServiceContainer(db_path=db_path)
    
    results: dict[str, Any] = {
        "vault_name": vault_name,
        "vault_path": str(vault_path),
        "tests": {},
    }
    
    try:
        # Тест 1: Индексация
        indexing_result = await _run_indexing_test(services, vault_path, vault_name)
        results["tests"]["indexing"] = indexing_result
        
        if not indexing_result.get("success"):
            print("❌ Индексация не удалась, пропускаем остальные тесты")
            return results
        
        # Тест 2: Metadata поиск
        metadata_result = await _run_metadata_search_test(services, vault_name)
        results["tests"]["metadata_search"] = metadata_result
        
        # Тест 3: Semantic поиск
        semantic_result = await _run_semantic_search_test(services, vault_name)
        results["tests"]["semantic_search"] = semantic_result
        
        # Тест 4: Hybrid поиск
        hybrid_result = await _run_hybrid_search_test(services, vault_name)
        results["tests"]["hybrid_search"] = hybrid_result
        
        # Тест 5: Multi-vault поиск (только если есть несколько vault'ов)
        # Для теста создаём второй vault
        if use_temp_vault and temp_dir:
            vault2_path = Path(temp_dir.name) / f"{vault_name}_2"
            create_test_vault(vault2_path)
            vault2_name = f"{vault_name}_2"
            
            # Индексируем второй vault
            indexer2 = VaultIndexer(vault2_path, vault2_name)
            embedding_cache2 = EmbeddingCache()
            chunks2, embeddings2, _ = await index_with_cache(
                vault_name=vault2_name,
                indexer=indexer2,
                embedding_service=services.embedding_service,
                db_manager=services.db_manager,
                embedding_cache=embedding_cache2,
                only_changed=False,
            )
            await services.db_manager.upsert_chunks(vault2_name, chunks2, embeddings2)
            
            multi_vault_result = await _run_multi_vault_search_test(
                services,
                [vault_name, vault2_name],
            )
            results["tests"]["multi_vault_search"] = multi_vault_result
        
        # Тест 6: Форматирование
        formatting_result = await _run_formatting_test(services, vault_name)
        results["tests"]["formatting"] = formatting_result
        
    finally:
        # Очистка ресурсов
        await services.cleanup()
        reset_service_container()
        if temp_dir:
            temp_dir.cleanup()
        temp_db_dir.cleanup()
    
    # Итоговая оценка
    print("=" * 80)
    print("ИТОГОВАЯ ОЦЕНКА")
    print("=" * 80)
    print()
    
    all_passed = True
    for test_name, test_result in results["tests"].items():
        if isinstance(test_result, dict):
            success = test_result.get("success", False)
            if "queries" in test_result:
                # Для тестов с несколькими запросами
                queries = test_result.get("queries", [])
                success = all(q.get("success", False) for q in queries)
            
            status = "✅" if success else "❌"
            print(f"{test_name:30} {status}")
            if not success:
                all_ok = False
        else:
            print(f"{test_name:30} ⚠️  Неожиданный формат результата")
    
    print()
    if all_passed:
        print("✅ ВСЕ E2E ТЕСТЫ ПРОШЛИ УСПЕШНО")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    
    return results


def save_results(results: dict[str, Any], output_file: Path) -> None:
    """Сохранение результатов в JSON."""
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n💾 Результаты сохранены в {output_file}")


async def main() -> None:
    """Главная функция."""
    import sys
    
    if len(sys.argv) > 1:
        # Использовать существующий vault
        vault_path = Path(sys.argv[1])
        vault_name = sys.argv[2] if len(sys.argv) > 2 else vault_path.name
        results = await run_e2e_tests(
            vault_path=vault_path,
            vault_name=vault_name,
            use_temp_vault=False,
        )
    else:
        # Использовать временный vault
        results = await run_e2e_tests()
    
    # Сохраняем результаты
    output_dir = Path(__file__).parent
    json_file = output_dir / "e2e_test_results.json"
    save_results(results, json_file)


if __name__ == "__main__":
    asyncio.run(main())

