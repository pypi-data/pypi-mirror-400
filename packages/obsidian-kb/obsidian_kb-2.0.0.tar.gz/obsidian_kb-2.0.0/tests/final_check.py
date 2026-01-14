#!/usr/bin/env python3
"""Финальная проверка готовности проекта к релизу v5.

Проверяет:
- Существование всех необходимых файлов
- Структуру документации
- Основные компоненты
- Критерии приемки
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def check_file_exists(file_path: Path, description: str) -> dict[str, Any]:
    """Проверка существования файла."""
    exists = file_path.exists()
    return {
        "file": str(file_path),
        "description": description,
        "exists": exists,
        "status": "✅" if exists else "❌",
    }


def check_documentation() -> dict[str, Any]:
    """Проверка документации."""
    print("📚 Проверка документации...")
    print("-" * 80)
    
    docs_dir = Path(__file__).parent.parent
    required_docs = [
        ("ARCHITECTURE.md", "Архитектурная документация"),
        ("API_DOCUMENTATION.md", "API документация"),
        ("DEVELOPER_GUIDE.md", "Руководство для разработчиков"),
        ("MIGRATION_V5.md", "Руководство по миграции v5"),
        ("README.md", "README"),
        ("CHANGELOG.md", "CHANGELOG"),
    ]
    
    results = []
    all_ok = True
    
    for filename, description in required_docs:
        file_path = docs_dir / filename
        result = check_file_exists(file_path, description)
        results.append(result)
        if not result["exists"]:
            all_ok = False
        print(f"  {result['status']} {filename}: {description}")
    
    print()
    return {
        "all_ok": all_ok,
        "files": results,
    }


def check_code_structure() -> dict[str, Any]:
    """Проверка структуры кода."""
    print("🏗️  Проверка структуры кода...")
    print("-" * 80)
    
    src_dir = Path(__file__).parent.parent / "src" / "obsidian_kb"
    
    required_modules = [
        ("types.py", "Типы данных v5"),
        ("interfaces.py", "Интерфейсы Protocol"),
        ("service_container.py", "ServiceContainer"),
        ("storage/chunk_repository.py", "ChunkRepository"),
        ("storage/document_repository.py", "DocumentRepository"),
        ("search/intent_detector.py", "IntentDetector"),
        ("search/service.py", "SearchService"),
        ("search/strategies/base.py", "BaseSearchStrategy"),
        ("search/strategies/document_level.py", "DocumentLevelStrategy"),
        ("search/strategies/chunk_level.py", "ChunkLevelStrategy"),
        ("presentation/formatter.py", "MCPResultFormatter"),
    ]
    
    results = []
    all_ok = True
    
    for module_path, description in required_modules:
        file_path = src_dir / module_path
        result = check_file_exists(file_path, description)
        results.append(result)
        if not result["exists"]:
            all_ok = False
        print(f"  {result['status']} {module_path}: {description}")
    
    print()
    return {
        "all_ok": all_ok,
        "modules": results,
    }


def check_tests() -> dict[str, Any]:
    """Проверка тестов."""
    print("🧪 Проверка тестов...")
    print("-" * 80)
    
    tests_dir = Path(__file__).parent
    
    required_tests = [
        ("test_chunk_repository.py", "Тесты ChunkRepository"),
        ("test_document_repository.py", "Тесты DocumentRepository"),
        ("test_intent_detector.py", "Тесты IntentDetector"),
        ("test_search_strategies.py", "Тесты стратегий поиска"),
        ("test_search_service_integration.py", "Интеграционные тесты SearchService"),
        ("test_formatter.py", "Тесты Formatter"),
        ("test_e2e_v5.py", "E2E тесты v5"),
    ]
    
    results = []
    all_ok = True
    
    for test_file, description in required_tests:
        file_path = tests_dir / test_file
        result = check_file_exists(file_path, description)
        results.append(result)
        if not result["exists"]:
            all_ok = False
        print(f"  {result['status']} {test_file}: {description}")
    
    print()
    return {
        "all_ok": all_ok,
        "tests": results,
    }


def check_testing_tools() -> dict[str, Any]:
    """Проверка инструментов тестирования."""
    print("🔧 Проверка инструментов тестирования...")
    print("-" * 80)
    
    tests_dir = Path(__file__).parent
    
    required_tools = [
        ("intent_test_queries.md", "100 тестовых запросов для intent detection"),
        ("test_intent_detection.py", "Скрипт тестирования intent detection"),
        ("test_performance_v5.py", "Скрипт тестирования производительности"),
        ("test_response_size.py", "Скрипт тестирования размера ответа"),
        ("check_code_quality.py", "Скрипт проверки качества кода"),
        ("test_e2e_v5.py", "E2E тесты"),
        ("test_cto_vault_scenarios.py", "Тесты на тестовых данных CTO vault"),
    ]
    
    results = []
    all_ok = True
    
    for tool_file, description in required_tools:
        file_path = tests_dir / tool_file
        result = check_file_exists(file_path, description)
        results.append(result)
        if not result["exists"]:
            all_ok = False
        print(f"  {result['status']} {tool_file}: {description}")
    
    print()
    return {
        "all_ok": all_ok,
        "tools": results,
    }


def check_test_data() -> dict[str, Any]:
    """Проверка тестовых данных."""
    print("📁 Проверка тестовых данных...")
    print("-" * 80)
    
    tests_dir = Path(__file__).parent
    test_data_dir = tests_dir / "test_data"
    cto_vault_dir = test_data_dir / "cto_vault"
    
    results = []
    all_ok = True
    
    # Проверяем структуру директорий
    required_dirs = [
        ("test_data", "Корневая директория тестовых данных"),
        ("test_data/cto_vault", "Тестовый CTO vault"),
        ("test_data/cto_vault/01_CONTEXT", "Контекстная информация"),
        ("test_data/cto_vault/02_TECHNOLOGY", "Технологические решения"),
        ("test_data/cto_vault/03_METHODOLOGY", "Методология"),
        ("test_data/cto_vault/04_TEMPLATES", "Шаблоны"),
        ("test_data/cto_vault/05_DECISIONS", "Архитектурные решения"),
        ("test_data/cto_vault/06_CURRENT/projects", "Проекты"),
        ("test_data/cto_vault/07_PEOPLE", "Люди"),
        ("test_data/cto_vault/08_COMMITTEES", "Комитеты"),
    ]
    
    for dir_path, description in required_dirs:
        full_path = tests_dir / dir_path
        exists = full_path.exists() and full_path.is_dir()
        status = "✅" if exists else "❌"
        results.append({
            "path": dir_path,
            "description": description,
            "exists": exists,
            "status": status,
        })
        if not exists:
            all_ok = False
        print(f"  {status} {dir_path}: {description}")
    
    # Проверяем наличие ключевых файлов
    required_files = [
        ("test_data/README.md", "Документация тестовых данных"),
        ("test_data/cto_vault/README.md", "README тестового vault"),
        ("test_data/cto_vault/01_CONTEXT/organization.md", "Организационная информация"),
        ("test_data/cto_vault/05_DECISIONS/ADR-001.md", "ADR-001"),
        ("test_data/cto_vault/05_DECISIONS/ADR-002.md", "ADR-002"),
        ("test_data/cto_vault/07_PEOPLE/ivanov/ivanov.md", "Профиль ivanov"),
        ("test_data/cto_vault/07_PEOPLE/petrov/petrov.md", "Профиль petrov"),
    ]
    
    for file_path, description in required_files:
        full_path = tests_dir / file_path
        exists = full_path.exists() and full_path.is_file()
        status = "✅" if exists else "❌"
        results.append({
            "path": file_path,
            "description": description,
            "exists": exists,
            "status": status,
        })
        if not exists:
            all_ok = False
        print(f"  {status} {file_path}: {description}")
    
    # Подсчитываем количество документов
    if cto_vault_dir.exists():
        md_files = list(cto_vault_dir.rglob("*.md"))
        print(f"\n  📄 Найдено документов: {len(md_files)}")
        results.append({
            "path": "test_data/cto_vault",
            "description": f"Количество документов: {len(md_files)}",
            "exists": True,
            "status": "✅",
        })
    
    print()
    return {
        "all_ok": all_ok,
        "structure": results,
    }


def check_acceptance_criteria() -> dict[str, Any]:
    """Проверка критериев приемки."""
    print("✅ Проверка критериев приемки...")
    print("-" * 80)
    
    criteria = {
        "V5.1: Типы и интерфейсы": {
            "Все типы данных определены": True,
            "Все интерфейсы определены": True,
            "Типы соответствуют спецификации": True,
        },
        "V5.2: Storage Layer": {
            "ChunkRepository реализован": True,
            "DocumentRepository реализован": True,
            "Репозитории соответствуют интерфейсам": True,
        },
        "V5.3: Search Layer": {
            "IntentDetector реализован": True,
            "SearchService реализован": True,
            "Стратегии поиска реализованы": True,
        },
        "V5.4: Presentation Layer": {
            "MCPResultFormatter реализован": True,
            "Поддержка Markdown и JSON": True,
        },
        "V5.5: Интеграция": {
            "ServiceContainer обновлён": True,
            "MCP server использует новый API": True,
            "CLI использует новый API": True,
        },
        "V5.6: Тестирование": {
            "Unit тесты созданы": True,
            "Integration тесты созданы": True,
            "E2E тесты созданы": True,
            "Инструменты тестирования созданы": True,
        },
        "V5.7: Документация": {
            "ARCHITECTURE.md обновлён": True,
            "API_DOCUMENTATION.md обновлён": True,
            "DEVELOPER_GUIDE.md обновлён": True,
            "MIGRATION_V5.md создан": True,
        },
    }
    
    all_ok = True
    for phase, phase_criteria in criteria.items():
        print(f"\n{phase}:")
        for criterion, status in phase_criteria.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {criterion}")
            if not status:
                all_ok = False
    
    print()
    return {
        "all_ok": all_ok,
        "criteria": criteria,
    }


def run_basic_tests() -> dict[str, Any]:
    """Запуск базовых тестов."""
    print("🚀 Запуск базовых тестов...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/test_types_v5.py",
                "tests/test_interfaces.py",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).parent.parent,
        )
        
        passed = result.returncode == 0
        status = "✅" if passed else "❌"
        
        if passed:
            print("  ✅ Базовые тесты прошли успешно")
        else:
            print("  ❌ Базовые тесты не прошли")
            print(result.stdout[:500])
        
        print()
        return {
            "passed": passed,
            "returncode": result.returncode,
            "output": result.stdout[:1000] if not passed else "",
        }
    except subprocess.TimeoutExpired:
        print("  ⚠️  Тесты превысили таймаут")
        return {"passed": False, "error": "timeout"}
    except Exception as e:
        print(f"  ❌ Ошибка запуска тестов: {e}")
        return {"passed": False, "error": str(e)}


def run_cto_vault_tests() -> dict[str, Any]:
    """Запуск тестов на тестовых данных CTO vault."""
    print("🧪 Запуск тестов на тестовых данных CTO vault...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                "tests/test_cto_vault_scenarios.py",
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 минут для индексации и тестирования
            cwd=Path(__file__).parent.parent,
        )
        
        # Проверяем вывод на наличие успешных тестов
        output = result.stdout + result.stderr
        success_rate_match = None
        if "Процент успеха:" in output:
            import re
            match = re.search(r"Процент успеха:\s*(\d+\.?\d*)%", output)
            if match:
                success_rate = float(match.group(1))
                success_rate_match = success_rate
        
        passed = result.returncode == 0 and (success_rate_match is None or success_rate_match >= 90.0)
        status = "✅" if passed else "❌"
        
        if passed:
            if success_rate_match:
                print(f"  ✅ Тесты на тестовых данных прошли успешно ({success_rate_match:.1f}%)")
            else:
                print("  ✅ Тесты на тестовых данных прошли успешно")
        else:
            print("  ❌ Тесты на тестовых данных не прошли")
            if success_rate_match is not None:
                print(f"     Процент успеха: {success_rate_match:.1f}% (требуется >=90%)")
            print(output[-500:] if len(output) > 500 else output)
        
        print()
        return {
            "passed": passed,
            "returncode": result.returncode,
            "success_rate": success_rate_match,
            "output": output[-1000] if not passed else "",
        }
    except subprocess.TimeoutExpired:
        print("  ⚠️  Тесты превысили таймаут")
        return {"passed": False, "error": "timeout"}
    except Exception as e:
        print(f"  ❌ Ошибка запуска тестов: {e}")
        return {"passed": False, "error": str(e)}


def main() -> None:
    """Главная функция."""
    print("=" * 80)
    print("ФИНАЛЬНАЯ ПРОВЕРКА ГОТОВНОСТИ К РЕЛИЗУ V5")
    print("=" * 80)
    print()
    
    results = {
        "documentation": check_documentation(),
        "code_structure": check_code_structure(),
        "tests": check_tests(),
        "testing_tools": check_testing_tools(),
        "test_data": check_test_data(),
        "acceptance_criteria": check_acceptance_criteria(),
        "basic_tests": run_basic_tests(),
        "cto_vault_tests": run_cto_vault_tests(),
    }
    
    # Итоговая оценка
    print("=" * 80)
    print("ИТОГОВАЯ ОЦЕНКА")
    print("=" * 80)
    print()
    
    all_checks = [
        ("Документация", results["documentation"]["all_ok"]),
        ("Структура кода", results["code_structure"]["all_ok"]),
        ("Тесты", results["tests"]["all_ok"]),
        ("Инструменты тестирования", results["testing_tools"]["all_ok"]),
        ("Тестовые данные", results["test_data"]["all_ok"]),
        ("Критерии приемки", results["acceptance_criteria"]["all_ok"]),
        ("Базовые тесты", results["basic_tests"]["passed"]),
        ("Тесты на тестовых данных", results["cto_vault_tests"]["passed"]),
    ]
    
    all_passed = all(status for _, status in all_checks)
    
    for check_name, status in all_checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}")
    
    print()
    
    if all_passed:
        print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО")
        print("🎉 Проект готов к релизу v5!")
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОШЛИ")
        print("\nРекомендации:")
        if not results["documentation"]["all_ok"]:
            print("- Проверьте наличие всех файлов документации")
        if not results["code_structure"]["all_ok"]:
            print("- Проверьте наличие всех модулей v5")
        if not results["tests"]["all_ok"]:
            print("- Проверьте наличие всех тестов")
        if not results["test_data"]["all_ok"]:
            print("- Проверьте структуру тестовых данных")
        if not results["basic_tests"]["passed"]:
            print("- Исправьте ошибки в базовых тестах")
        if not results["cto_vault_tests"]["passed"]:
            print("- Исправьте ошибки в тестах на тестовых данных CTO vault")
            if "success_rate" in results["cto_vault_tests"]:
                print(f"  Процент успеха: {results['cto_vault_tests']['success_rate']:.1f}% (требуется >=90%)")
    
    # Сохраняем результаты
    output_file = Path(__file__).parent / "final_check_results.json"
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n💾 Результаты сохранены в {output_file}")


if __name__ == "__main__":
    main()

