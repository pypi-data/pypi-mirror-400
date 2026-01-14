#!/usr/bin/env python3
"""Тестирование поиска на тестовых данных CTO vault.

Проверяет различные сценарии поиска на структурированных тестовых данных,
имитирующих реальную базу знаний руководителя ИТ-компании.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.service_container import ServiceContainer, reset_service_container
from obsidian_kb.types import RetrievalGranularity, SearchRequest
from obsidian_kb.vault_indexer import VaultIndexer


# Путь к тестовым данным
TEST_VAULT_PATH = Path(__file__).parent / "test_data" / "cto_vault"
TEST_VAULT_NAME = "cto_test_vault"


class TestScenario:
    """Класс для описания тестового сценария."""
    
    def __init__(
        self,
        name: str,
        query: str,
        expected_intent: str | None = None,
        expected_min_results: int = 1,
        expected_file_paths: list[str] | None = None,
        description: str = "",
    ):
        self.name = name
        self.query = query
        self.expected_intent = expected_intent
        self.expected_min_results = expected_min_results
        self.expected_file_paths = expected_file_paths or []
        self.description = description


# Тестовые сценарии
TEST_SCENARIOS = [
    # Группа 1: Поиск по метаданным (METADATA_FILTER)
    TestScenario(
        name="Поиск всех профилей людей",
        query="type:person",
        expected_intent="METADATA_FILTER",
        expected_min_results=4,
        expected_file_paths=["ivanov.md", "petrov.md", "sidorov.md", "kozlov.md"],
        description="Должен найти все профили людей в vault",
    ),
    TestScenario(
        name="Поиск всех встреч 1-1",
        query="type:1-1",
        expected_intent="METADATA_FILTER",
        expected_min_results=2,
        expected_file_paths=["2024-12-15.md", "2024-12-10.md"],
        description="Должен найти все встречи 1-1",
    ),
    TestScenario(
        name="Поиск по тегу person",
        query="tags:person",
        expected_intent="METADATA_FILTER",
        expected_min_results=4,
        description="Должен найти все документы с тегом person",
    ),
    TestScenario(
        name="Поиск по тегу project",
        query="tags:project",
        expected_intent="METADATA_FILTER",
        expected_min_results=2,
        expected_file_paths=["platform-modernization.md", "integration-framework.md"],
        description="Должен найти все проекты",
    ),
    TestScenario(
        name="Поиск по тегу architecture",
        query="tags:architecture",
        expected_intent="METADATA_FILTER",
        expected_min_results=3,
        description="Должен найти документы с тегом architecture",
    ),
    
    # Группа 2: Поиск по ссылкам (METADATA_FILTER)
    TestScenario(
        name="Поиск документов со ссылкой на ivanov",
        query="links:ivanov",
        expected_intent="METADATA_FILTER",
        expected_min_results=2,
        expected_file_paths=["platform-modernization.md", "2024-12-15.md"],
        description="Должен найти документы, ссылающиеся на ivanov",
    ),
    TestScenario(
        name="Поиск документов со ссылкой на petrov",
        query="links:petrov",
        expected_intent="METADATA_FILTER",
        expected_min_results=2,
        description="Должен найти документы, ссылающиеся на petrov",
    ),
    TestScenario(
        name="Поиск документов со ссылкой на проект",
        query="links:platform-modernization",
        expected_intent="METADATA_FILTER",
        expected_min_results=1,
        description="Должен найти документы, ссылающиеся на проект",
    ),
    
    # Группа 3: Поиск по датам (METADATA_FILTER)
    TestScenario(
        name="Поиск документов за декабрь 2024",
        query="created:>=2024-12-01 created:<=2024-12-31",
        expected_intent="METADATA_FILTER",
        expected_min_results=3,
        description="Должен найти документы, созданные в декабре 2024",
    ),
    TestScenario(
        name="Поиск документов после ноября 2024",
        query="created:>2024-11-30",
        expected_intent="METADATA_FILTER",
        expected_min_results=3,
        description="Должен найти документы, созданные после ноября 2024",
    ),
    
    # Группа 4: Комбинированные фильтры (METADATA_FILTER)
    TestScenario(
        name="Поиск встреч 1-1 с ivanov",
        query="type:1-1 links:ivanov",
        expected_intent="METADATA_FILTER",
        expected_min_results=1,
        expected_file_paths=["2024-12-15.md"],
        description="Должен найти встречи 1-1 с ivanov",
    ),
    TestScenario(
        name="Поиск проектов с тегом active",
        query="type:project tags:active",
        expected_intent="METADATA_FILTER",
        expected_min_results=2,
        description="Должен найти активные проекты",
    ),
    
    # Группа 5: Поиск известных документов (KNOWN_ITEM)
    TestScenario(
        name="Поиск README",
        query="README.md",
        expected_intent="KNOWN_ITEM",
        expected_min_results=1,
        expected_file_paths=["README.md"],
        description="Должен найти файл README.md",
    ),
    TestScenario(
        name="Поиск ADR-001",
        query="ADR-001",
        expected_intent="KNOWN_ITEM",
        expected_min_results=1,
        expected_file_paths=["ADR-001.md"],
        description="Должен найти архитектурное решение ADR-001",
    ),
    TestScenario(
        name="Поиск по ID человека",
        query="ivanov",
        expected_intent="KNOWN_ITEM",
        expected_min_results=1,
        expected_file_paths=["ivanov.md"],
        description="Должен найти профиль ivanov",
    ),
    
    # Группа 6: Семантический поиск (SEMANTIC)
    TestScenario(
        name="Поиск по концепции архитектуры",
        query="архитектурные решения микросервисы",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["ADR-002.md"],
        description="Должен найти документы об архитектурных решениях",
    ),
    TestScenario(
        name="Поиск по концепции производительности",
        query="проблемы производительности оптимизация",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        description="Должен найти документы о производительности",
    ),
    TestScenario(
        name="Поиск по концепции базы данных",
        query="выбор базы данных PostgreSQL",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["ADR-001.md"],
        description="Должен найти документы о выборе базы данных",
    ),
    
    # Группа 7: Исследовательские вопросы (EXPLORATORY)
    TestScenario(
        name="Вопрос что такое",
        query="что такое микросервисная архитектура",
        expected_intent="EXPLORATORY",
        expected_min_results=1,
        description="Должен найти информацию о микросервисной архитектуре",
    ),
    TestScenario(
        name="Вопрос как работает",
        query="как работает интеграционный фреймворк",
        expected_intent="EXPLORATORY",
        expected_min_results=1,
        description="Должен найти информацию о работе интеграционного фреймворка",
    ),
    
    # Группа 8: How-to запросы (PROCEDURAL)
    TestScenario(
        name="Запрос как создать",
        query="как создать ADR",
        expected_intent="PROCEDURAL",
        expected_min_results=1,
        expected_file_paths=["template_adr.md"],
        description="Должен найти шаблон или инструкцию по созданию ADR",
    ),
    TestScenario(
        name="Запрос инструкция",
        query="управление проектом",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["project-management-guide.md"],
        description="Должен найти документ об управлении проектами",
    ),
    
    # Группа 9: Комплексные запросы
    TestScenario(
        name="Комплексный запрос с фильтрами и текстом",
        query="архитектура tags:architecture created:>2024-05-01",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        description="Должен найти архитектурные документы после мая 2024",
    ),
    TestScenario(
        name="Комплексный запрос проект и человек",
        query="platform-modernization ivanov",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        description="Должен найти информацию о проекте и человеке",
    ),
]


async def run_scenario(
    services: ServiceContainer,
    scenario: TestScenario,
    vault_name: str,
) -> dict[str, Any]:
    """Запуск одного тестового сценария.
    
    Args:
        services: Контейнер сервисов
        scenario: Тестовый сценарий
        vault_name: Имя vault'а
        
    Returns:
        Результаты тестирования сценария
    """
    try:
        request = SearchRequest(
            vault_name=vault_name,
            query=scenario.query,
            limit=20,
            granularity=RetrievalGranularity.AUTO,
        )
        
        response = await services.search_service.search(request)
        
        # Проверяем результаты
        found_file_paths = [
            result.document.file_path for result in response.results
        ]
        
        # Проверяем ожидаемые файлы (проверяем по имени файла, а не полному пути)
        expected_found = 0
        if scenario.expected_file_paths:
            for expected_path in scenario.expected_file_paths:
                # Извлекаем имя файла из полного пути
                expected_filename = Path(expected_path).name
                if any(expected_filename in Path(path).name for path in found_file_paths):
                    expected_found += 1
        
        # Проверяем intent (сравниваем в lowercase, так как enum возвращает lowercase)
        intent_match = True
        if scenario.expected_intent:
            intent_match = response.detected_intent.value.lower() == scenario.expected_intent.lower()
        
        # Проверяем минимальное количество результатов
        min_results_ok = response.total_found >= scenario.expected_min_results
        
        # Успех если:
        # 1. Найдено минимум результатов
        # 2. Intent совпадает (если указан)
        # 3. Найдены ожидаемые файлы (если указаны) - хотя бы 50%
        # 4. Для семантического поиска - просто наличие результатов
        success = (
            min_results_ok
            and intent_match
            and (
                not scenario.expected_file_paths
                or expected_found >= max(1, len(scenario.expected_file_paths) * 0.5)
            )
        )
        
        # Для семантического поиска считаем успешным, если найден хотя бы один релевантный документ
        if scenario.expected_intent and scenario.expected_intent.lower() in ["semantic", "exploratory"]:
            success = success and response.total_found > 0
        
        return {
            "name": scenario.name,
            "query": scenario.query,
            "success": success,
            "found": response.total_found,
            "expected_min": scenario.expected_min_results,
            "intent_detected": response.detected_intent.value,
            "intent_expected": scenario.expected_intent,
            "intent_match": intent_match,
            "min_results_ok": min_results_ok,
            "found_file_paths": found_file_paths[:5],  # Первые 5 для отладки
            "expected_file_paths": scenario.expected_file_paths,
            "expected_found": expected_found,
            "time_ms": response.execution_time_ms,
            "strategy": response.strategy_used,
        }
    except Exception as e:
        return {
            "name": scenario.name,
            "query": scenario.query,
            "success": False,
            "error": str(e),
        }


async def run_all_scenarios(
    services: ServiceContainer,
    vault_name: str,
) -> dict[str, Any]:
    """Запуск всех тестовых сценариев.
    
    Args:
        services: Контейнер сервисов
        vault_name: Имя vault'а
        
    Returns:
        Результаты всех тестов
    """
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ СЦЕНАРИЕВ ПОИСКА НА CTO VAULT")
    print("=" * 80)
    print()
    
    results = []
    passed = 0
    failed = 0
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"[{i}/{len(TEST_SCENARIOS)}] {scenario.name}")
        print(f"  Запрос: {scenario.query}")
        
        result = await run_scenario(services, scenario, vault_name)
        results.append(result)
        
        if result.get("success"):
            print(f"  ✅ Успешно (найдено: {result['found']}, intent: {result['intent_detected']})")
            passed += 1
        else:
            print(f"  ❌ Неудачно")
            if "error" in result:
                print(f"     Ошибка: {result['error']}")
            else:
                print(f"     Найдено: {result['found']}, ожидалось минимум: {result['expected_min']}")
                print(f"     Intent: {result['intent_detected']}, ожидался: {result['intent_expected']}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"Всего сценариев: {len(TEST_SCENARIOS)}")
    print(f"✅ Успешно: {passed}")
    print(f"❌ Неудачно: {failed}")
    print(f"Процент успеха: {passed / len(TEST_SCENARIOS) * 100:.1f}%")
    print()
    
    return {
        "total": len(TEST_SCENARIOS),
        "passed": passed,
        "failed": failed,
        "success_rate": passed / len(TEST_SCENARIOS) * 100,
        "scenarios": results,
    }


async def index_test_vault(
    services: ServiceContainer,
    vault_path: Path,
    vault_name: str,
) -> dict[str, Any]:
    """Индексация тестового vault'а.
    
    Args:
        services: Контейнер сервисов
        vault_path: Путь к vault'у
        vault_name: Имя vault'а
        
    Returns:
        Результаты индексации
    """
    print("📦 Индексация тестового vault'а")
    print("-" * 80)
    
    try:
        indexer = VaultIndexer(vault_path, vault_name)
        embedding_cache = EmbeddingCache()
        
        chunks, embeddings, stats = await index_with_cache(
            vault_name=vault_name,
            indexer=indexer,
            embedding_service=services.embedding_service,
            db_manager=services.db_manager,
            embedding_cache=embedding_cache,
            only_changed=False,
        )
        
        await services.db_manager.upsert_chunks(vault_name, chunks, embeddings)
        
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
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
        }


async def main() -> None:
    """Главная функция."""
    import tempfile
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПОИСКА НА ТЕСТОВЫХ ДАННЫХ CTO VAULT")
    print("=" * 80)
    print()
    
    if not TEST_VAULT_PATH.exists():
        print(f"❌ Тестовый vault не найден: {TEST_VAULT_PATH}")
        return
    
    # Сбрасываем глобальный контейнер
    reset_service_container()
    
    # Создаём временную БД
    temp_db_dir = tempfile.TemporaryDirectory()
    db_path = Path(temp_db_dir.name) / "test_db.lance"
    
    # Инициализируем сервисы
    services = ServiceContainer(db_path=db_path)
    
    try:
        # Индексируем vault
        indexing_result = await index_test_vault(
            services,
            TEST_VAULT_PATH,
            TEST_VAULT_NAME,
        )
        
        if not indexing_result.get("success"):
            print("❌ Индексация не удалась, прерывание тестирования")
            return
        
        # Запускаем тестовые сценарии
        test_results = await run_all_scenarios(services, TEST_VAULT_NAME)
        
        # Сохраняем результаты
        output_file = Path(__file__).parent / "cto_vault_test_results.json"
        output_file.write_text(
            json.dumps(
                {
                    "indexing": indexing_result,
                    "test_results": test_results,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        print(f"💾 Результаты сохранены в {output_file}")
        
    finally:
        await services.cleanup()
        reset_service_container()
        temp_db_dir.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

