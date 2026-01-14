#!/usr/bin/env python3
"""Тестирование проблемных кейсов из Round 5.

Проверяет критические проблемы, выявленные в тестировании Intent Detection Раунд 5:
- Поиск людей по имени (P0)
- Фильтр дат (P1)
- Релевантность PROCEDURAL (P1)
- KNOWN_ITEM при отсутствии документа (P2)
- Релевантность EXPLORATORY (P2)
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


class Round5TestScenario:
    """Класс для описания тестового сценария Round 5."""
    
    def __init__(
        self,
        name: str,
        query: str,
        expected_intent: str | None = None,
        expected_min_results: int = 1,
        expected_file_paths: list[str] | None = None,
        expected_max_position: int | None = None,  # Максимальная позиция ожидаемого файла (1 = топ-1)
        description: str = "",
        priority: str = "P0",  # P0, P1, P2
    ):
        self.name = name
        self.query = query
        self.expected_intent = expected_intent
        self.expected_min_results = expected_min_results
        self.expected_file_paths = expected_file_paths or []
        self.expected_max_position = expected_max_position  # Позиция в топе (1 = первое место)
        self.description = description
        self.priority = priority


# Тестовые сценарии для проблемных кейсов Round 5
ROUND5_TEST_SCENARIOS = [
    # ========== P0: Поиск людей по имени (КРИТИЧНО) ==========
    
    Round5TestScenario(
        name="P0: Поиск по полному имени - Александр Волков",
        query="Александр Волков",
        expected_intent="SEMANTIC",  # Может быть SEMANTIC или KNOWN_ITEM
        expected_min_results=1,
        expected_file_paths=["volkov.md"],
        expected_max_position=3,  # Должен быть в топ-3
        description="КРИТИЧНО: Поиск по полному имени должен находить профиль",
        priority="P0",
    ),
    
    Round5TestScenario(
        name="P0: Поиск по фамилии - Волков",
        query="Волков",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["volkov.md"],
        expected_max_position=3,  # Профиль должен быть выше упоминаний
        description="КРИТИЧНО: Поиск по фамилии должен находить профиль в топе",
        priority="P0",
    ),
    
    Round5TestScenario(
        name="P0: Поиск по должности из профиля",
        query="Руководитель AI офиса",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["volkov.md"],
        expected_max_position=3,  # Должен быть в топ-3
        description="КРИТИЧНО: Поиск по должности должен находить профиль",
        priority="P0",
    ),
    
    Round5TestScenario(
        name="P0: Поиск по ID профиля - volkov",
        query="volkov",
        expected_intent="KNOWN_ITEM",
        expected_min_results=1,
        expected_file_paths=["volkov.md"],
        expected_max_position=1,  # Должен быть на первом месте
        description="КРИТИЧНО: Поиск по ID профиля должен находить профиль",
        priority="P0",
    ),
    
    Round5TestScenario(
        name="P0: Поиск по имени - Александр",
        query="Александр",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["volkov.md"],
        expected_max_position=3,  # Должен быть в топ-3
        description="КРИТИЧНО: Поиск по имени должен находить профиль",
        priority="P0",
    ),
    
    Round5TestScenario(
        name="P0: Поиск с фильтром type:person - Александр Волков",
        query="type:person Александр Волков",
        expected_intent="SEMANTIC",
        expected_min_results=1,
        expected_file_paths=["volkov.md"],
        expected_max_position=1,  # Должен быть на первом месте
        description="КРИТИЧНО: Поиск с фильтром type:person должен находить профиль",
        priority="P0",
    ),
    
    # ========== P1: Фильтр дат ==========
    
    Round5TestScenario(
        name="P1: Фильтр дат - больше 2024-12-20",
        query="created:>2024-12-20",
        expected_intent="METADATA_FILTER",
        expected_min_results=1,
        expected_file_paths=["2024-12-25_project-update.md"],  # Документ от 2024-12-25 (должен быть включен)
        description="P1: Фильтр 'больше' должен корректно отсекать документы до указанной даты (ADR-003 от 2024-11-27 должен быть исключен)",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: Фильтр дат - больше или равно 2024-12-01",
        query="created:>=2024-12-01",
        expected_intent="METADATA_FILTER",
        expected_min_results=3,
        description="P1: Фильтр 'больше или равно' должен включать документы от указанной даты",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: Фильтр дат - меньше 2024-12-01",
        query="created:<2024-12-01",
        expected_intent="METADATA_FILTER",
        expected_min_results=1,
        expected_file_paths=["ADR-003.md"],  # Документ от 2024-11-27 (должен быть включен, так как < 2024-12-01)
        description="P1: Фильтр 'меньше' должен включать только документы до указанной даты",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: Комбинированный фильтр дат - декабрь 2024",
        query="created:>=2024-12-01 created:<=2024-12-31",
        expected_intent="METADATA_FILTER",
        expected_min_results=3,
        description="P1: Комбинированные фильтры дат должны работать корректно",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: Фильтр дат с type - встречи после декабря",
        query="type:1-1 created:>=2024-12-20",
        expected_intent="METADATA_FILTER",
        expected_min_results=1,
        expected_file_paths=["2024-12-20.md"],  # Встреча от 2024-12-20
        description="P1: Фильтр дат в комбинации с другими фильтрами должен работать",
        priority="P1",
    ),
    
    # ========== P1: Релевантность PROCEDURAL ==========
    
    Round5TestScenario(
        name="P1: PROCEDURAL - как создать ADR",
        query="как создать ADR",
        expected_intent="PROCEDURAL",
        expected_min_results=1,
        expected_file_paths=["guide_adr.md"],
        expected_max_position=3,  # Должен быть в топ-3
        description="P1: PROCEDURAL запрос должен находить гайд в топе",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: PROCEDURAL - как провести 1-1",
        query="как провести 1-1",
        expected_intent="PROCEDURAL",
        expected_min_results=1,
        expected_file_paths=["template_1-1.md"],
        expected_max_position=3,  # Должен быть в топ-3
        description="P1: PROCEDURAL запрос должен находить шаблон в топе",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: PROCEDURAL - инструкция по созданию ADR",
        query="инструкция по созданию ADR",
        expected_intent="PROCEDURAL",
        expected_min_results=1,
        expected_file_paths=["guide_adr.md"],
        expected_max_position=3,
        description="P1: PROCEDURAL запрос с синонимами должен находить гайд",
        priority="P1",
    ),
    
    Round5TestScenario(
        name="P1: PROCEDURAL - шаблон для 1-1",
        query="шаблон для 1-1",
        expected_intent="PROCEDURAL",
        expected_min_results=1,
        expected_file_paths=["template_1-1.md"],
        expected_max_position=3,
        description="P1: PROCEDURAL запрос должен находить шаблон",
        priority="P1",
    ),
    
    # ========== P2: KNOWN_ITEM при отсутствии документа ==========
    
    Round5TestScenario(
        name="P2: KNOWN_ITEM - несуществующий ADR",
        query="ADR-999",
        expected_intent="KNOWN_ITEM",
        expected_min_results=0,  # Должно быть 0 результатов
        expected_file_paths=[],
        description="P2: Несуществующий документ должен возвращать 0 результатов",
        priority="P2",
    ),
    
    Round5TestScenario(
        name="P2: KNOWN_ITEM - существующий ADR",
        query="ADR-003",
        expected_intent="KNOWN_ITEM",
        expected_min_results=1,
        expected_file_paths=["ADR-003.md"],
        expected_max_position=1,  # Должен быть на первом месте
        description="P2: Существующий документ должен находиться корректно",
        priority="P2",
    ),
    
    Round5TestScenario(
        name="P2: KNOWN_ITEM - несуществующий человек",
        query="nonexistent-person",
        expected_intent="KNOWN_ITEM",
        expected_min_results=0,  # Должно быть 0 результатов
        expected_file_paths=[],
        description="P2: Несуществующий профиль должен возвращать 0 результатов",
        priority="P2",
    ),
    
    # ========== P2: Релевантность EXPLORATORY ==========
    
    Round5TestScenario(
        name="P2: EXPLORATORY - что такое Naumen SMP",
        query="что такое Naumen SMP",
        expected_intent="EXPLORATORY",
        expected_min_results=1,
        expected_file_paths=["smp.md"],
        expected_max_position=3,  # Должен быть в топ-3
        description="P2: EXPLORATORY запрос должен находить релевантный документ в топе",
        priority="P2",
    ),
    
    Round5TestScenario(
        name="P2: EXPLORATORY - что такое SMP",
        query="что такое SMP",
        expected_intent="EXPLORATORY",
        expected_min_results=1,
        expected_file_paths=["smp.md"],
        expected_max_position=3,
        description="P2: EXPLORATORY запрос должен находить документ",
        priority="P2",
    ),
    
    Round5TestScenario(
        name="P2: EXPLORATORY - зачем нужна централизация",
        query="зачем нужна централизация",
        expected_intent="EXPLORATORY",
        expected_min_results=1,
        description="P2: EXPLORATORY запрос должен находить релевантные документы",
        priority="P2",
    ),
]


async def run_scenario(
    services: ServiceContainer,
    scenario: Round5TestScenario,
    vault_name: str,
) -> dict[str, Any]:
    """Запуск одного тестового сценария Round 5.
    
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
        
        # Проверяем ожидаемые файлы и их позиции
        expected_found = 0
        position_ok = True
        
        if scenario.expected_file_paths:
            for expected_path in scenario.expected_file_paths:
                expected_filename = Path(expected_path).name
                for idx, found_path in enumerate(found_file_paths, 1):
                    if expected_filename in Path(found_path).name:
                        expected_found += 1
                        # Проверяем позицию
                        if scenario.expected_max_position and idx > scenario.expected_max_position:
                            position_ok = False
                        break
        
        # Проверяем intent
        intent_match = True
        if scenario.expected_intent:
            intent_match = response.detected_intent.value.lower() == scenario.expected_intent.lower()
        
        # Проверяем минимальное количество результатов
        min_results_ok = response.total_found >= scenario.expected_min_results
        
        # Для P0 и P1 критично проверить позицию
        if scenario.priority in ["P0", "P1"] and scenario.expected_max_position:
            success = (
                min_results_ok
                and intent_match
                and expected_found > 0
                and position_ok
            )
        else:
            # Для P2 и случаев без проверки позиции
            success = (
                min_results_ok
                and intent_match
                and (
                    not scenario.expected_file_paths
                    or expected_found > 0
                )
            )
        
        # Для KNOWN_ITEM с expected_min_results=0 проверяем, что результатов действительно 0
        if scenario.expected_min_results == 0:
            success = success and response.total_found == 0
        
        return {
            "name": scenario.name,
            "query": scenario.query,
            "priority": scenario.priority,
            "success": success,
            "found": response.total_found,
            "expected_min": scenario.expected_min_results,
            "intent_detected": response.detected_intent.value,
            "intent_expected": scenario.expected_intent,
            "intent_match": intent_match,
            "min_results_ok": min_results_ok,
            "found_file_paths": found_file_paths[:10],  # Первые 10 для отладки
            "expected_file_paths": scenario.expected_file_paths,
            "expected_found": expected_found,
            "position_ok": position_ok if scenario.expected_max_position else None,
            "expected_max_position": scenario.expected_max_position,
            "time_ms": response.execution_time_ms,
            "strategy": response.strategy_used,
            "description": scenario.description,
        }
    except Exception as e:
        return {
            "name": scenario.name,
            "query": scenario.query,
            "priority": scenario.priority,
            "success": False,
            "error": str(e),
        }


async def run_all_scenarios(
    services: ServiceContainer,
    vault_name: str,
) -> dict[str, Any]:
    """Запуск всех тестовых сценариев Round 5.
    
    Args:
        services: Контейнер сервисов
        vault_name: Имя vault'а
        
    Returns:
        Результаты всех тестов
    """
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПРОБЛЕМНЫХ КЕЙСОВ ROUND 5")
    print("=" * 80)
    print()
    
    results = []
    passed = 0
    failed = 0
    
    # Группируем по приоритетам
    by_priority = {"P0": [], "P1": [], "P2": []}
    for scenario in ROUND5_TEST_SCENARIOS:
        by_priority[scenario.priority].append(scenario)
    
    for priority in ["P0", "P1", "P2"]:
        scenarios = by_priority[priority]
        if not scenarios:
            continue
            
        print(f"\n{'=' * 80}")
        print(f"ПРИОРИТЕТ {priority} ({len(scenarios)} сценариев)")
        print(f"{'=' * 80}\n")
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"[{i}/{len(scenarios)}] {scenario.name}")
            print(f"  Запрос: {scenario.query}")
            
            result = await run_scenario(services, scenario, vault_name)
            results.append(result)
            
            if result.get("success"):
                print(f"  ✅ Успешно (найдено: {result['found']}, intent: {result['intent_detected']})")
                if result.get("position_ok") is not None:
                    if result.get("position_ok"):
                        print(f"     Позиция: OK (макс. {result['expected_max_position']})")
                    else:
                        print(f"     ⚠️ Позиция: не в топе (макс. {result['expected_max_position']})")
                passed += 1
            else:
                print(f"  ❌ Неудачно")
                if "error" in result:
                    print(f"     Ошибка: {result['error']}")
                else:
                    print(f"     Найдено: {result['found']}, ожидалось минимум: {result['expected_min']}")
                    print(f"     Intent: {result['intent_detected']}, ожидался: {result['intent_expected']}")
                    if result.get("position_ok") is False:
                        print(f"     ⚠️ Позиция: не в топе (макс. {result['expected_max_position']})")
                failed += 1
            
            print()
    
    print("=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"Всего сценариев: {len(ROUND5_TEST_SCENARIOS)}")
    print(f"✅ Успешно: {passed}")
    print(f"❌ Неудачно: {failed}")
    print(f"Процент успеха: {passed / len(ROUND5_TEST_SCENARIOS) * 100:.1f}%")
    print()
    
    # Статистика по приоритетам
    for priority in ["P0", "P1", "P2"]:
        priority_results = [r for r in results if r.get("priority") == priority]
        if priority_results:
            priority_passed = sum(1 for r in priority_results if r.get("success"))
            print(f"{priority}: {priority_passed}/{len(priority_results)} ({priority_passed / len(priority_results) * 100:.1f}%)")
    
    return {
        "total": len(ROUND5_TEST_SCENARIOS),
        "passed": passed,
        "failed": failed,
        "success_rate": passed / len(ROUND5_TEST_SCENARIOS) * 100,
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
    print("ТЕСТИРОВАНИЕ ПРОБЛЕМНЫХ КЕЙСОВ ROUND 5")
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
        output_file = Path(__file__).parent / "round5_test_results.json"
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

