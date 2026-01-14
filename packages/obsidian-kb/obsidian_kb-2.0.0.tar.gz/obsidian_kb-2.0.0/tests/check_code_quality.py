#!/usr/bin/env python3
"""Проверка качества кода: code coverage и cyclomatic complexity.

Цели:
- Code coverage >80%
- Cyclomatic complexity <10 для всех методов
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def check_coverage(target: float = 80.0) -> dict[str, Any]:
    """Проверка code coverage.
    
    Args:
        target: Целевой процент покрытия
        
    Returns:
        Словарь с результатами проверки
    """
    print("📊 Проверка code coverage...")
    print("-" * 80)
    
    # Запускаем pytest с coverage
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/",
                "--cov=src/obsidian_kb",
                "--cov-report=json",
                "--cov-report=term-missing",
                "-v",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        # Читаем результаты coverage
        coverage_file = Path(__file__).parent.parent / "coverage.json"
        if coverage_file.exists():
            coverage_data = json.loads(coverage_file.read_text())
            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0.0)
            
            print(f"Общее покрытие: {total_coverage:.2f}%")
            print(f"Целевое покрытие: >{target}%")
            
            meets_target = total_coverage >= target
            status = "✅" if meets_target else "❌"
            print(f"Статус: {status}")
            print()
            
            # Детализация по файлам
            files = coverage_data.get("files", {})
            low_coverage_files = []
            
            for file_path, file_data in files.items():
                file_coverage = file_data.get("summary", {}).get("percent_covered", 0.0)
                if file_coverage < target:
                    low_coverage_files.append({
                        "file": file_path,
                        "coverage": file_coverage,
                    })
            
            if low_coverage_files:
                print("Файлы с низким покрытием (<80%):")
                for item in sorted(low_coverage_files, key=lambda x: x["coverage"]):
                    print(f"  {item['file']}: {item['coverage']:.2f}%")
                print()
            
            return {
                "total_coverage": total_coverage,
                "target": target,
                "meets_target": meets_target,
                "low_coverage_files": low_coverage_files,
                "files_analyzed": len(files),
            }
        else:
            print("⚠️  Файл coverage.json не найден")
            print("Запустите: pytest --cov=src/obsidian_kb --cov-report=json")
            return {
                "total_coverage": 0.0,
                "target": target,
                "meets_target": False,
                "error": "coverage.json not found",
            }
            
    except Exception as e:
        print(f"❌ Ошибка при проверке coverage: {e}")
        return {
            "total_coverage": 0.0,
            "target": target,
            "meets_target": False,
            "error": str(e),
        }


def check_complexity(target: int = 10) -> dict[str, Any]:
    """Проверка cyclomatic complexity.
    
    Args:
        target: Целевая максимальная сложность
        
    Returns:
        Словарь с результатами проверки
    """
    print("🔍 Проверка cyclomatic complexity...")
    print("-" * 80)
    
    try:
        # Пытаемся использовать radon для проверки complexity
        result = subprocess.run(
            [
                sys.executable, "-m", "radon", "cc",
                "src/obsidian_kb",
                "--min", "B",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        if result.returncode == 0:
            complexity_data = json.loads(result.stdout)
            
            high_complexity = []
            total_functions = 0
            
            for file_path, functions in complexity_data.items():
                for func in functions:
                    total_functions += 1
                    complexity = func.get("complexity", 0)
                    if complexity > target:
                        high_complexity.append({
                            "file": file_path,
                            "function": func.get("name", "unknown"),
                            "complexity": complexity,
                            "line": func.get("lineno", 0),
                        })
            
            print(f"Всего функций проверено: {total_functions}")
            print(f"Функций с complexity >{target}: {len(high_complexity)}")
            
            if high_complexity:
                print("\nФункции с высокой сложностью:")
                for item in sorted(high_complexity, key=lambda x: x["complexity"], reverse=True):
                    print(f"  {item['file']}:{item['line']} {item['function']}() - complexity {item['complexity']}")
                print()
            else:
                print("✅ Все функции соответствуют целевой сложности")
                print()
            
            return {
                "total_functions": total_functions,
                "high_complexity_count": len(high_complexity),
                "target": target,
                "meets_target": len(high_complexity) == 0,
                "high_complexity": high_complexity,
            }
        else:
            print("⚠️  Radon не установлен или произошла ошибка")
            print("Установите: pip install radon")
            print("Или запустите: python -m pip install radon")
            return {
                "total_functions": 0,
                "high_complexity_count": 0,
                "target": target,
                "meets_target": False,
                "error": "radon not available",
            }
            
    except FileNotFoundError:
        print("⚠️  Radon не установлен")
        print("Установите: pip install radon")
        return {
            "total_functions": 0,
            "high_complexity_count": 0,
            "target": target,
            "meets_target": False,
            "error": "radon not installed",
        }
    except Exception as e:
        print(f"❌ Ошибка при проверке complexity: {e}")
        return {
            "total_functions": 0,
            "high_complexity_count": 0,
            "target": target,
            "meets_target": False,
            "error": str(e),
        }


def check_linters() -> dict[str, Any]:
    """Проверка линтеров (ruff, mypy).
    
    Returns:
        Словарь с результатами проверки
    """
    print("🔧 Проверка линтеров...")
    print("-" * 80)
    
    results = {}
    
    # Проверка ruff
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "src/obsidian_kb"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        if result.returncode == 0:
            print("✅ Ruff: нет ошибок")
            results["ruff"] = {"status": "ok", "errors": 0}
        else:
            errors = len(result.stdout.split("\n")) - 1
            print(f"❌ Ruff: найдено {errors} ошибок")
            print(result.stdout[:500])  # Первые 500 символов
            results["ruff"] = {"status": "errors", "errors": errors, "output": result.stdout}
    except FileNotFoundError:
        print("⚠️  Ruff не установлен")
        results["ruff"] = {"status": "not_installed"}
    except Exception as e:
        print(f"❌ Ошибка при проверке ruff: {e}")
        results["ruff"] = {"status": "error", "error": str(e)}
    
    print()
    
    # Проверка mypy (опционально)
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "mypy",
                "src/obsidian_kb",
                "--ignore-missing-imports",
                "--no-strict-optional",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        if result.returncode == 0:
            print("✅ Mypy: нет ошибок типов")
            results["mypy"] = {"status": "ok", "errors": 0}
        else:
            errors = len([l for l in result.stdout.split("\n") if "error:" in l])
            print(f"⚠️  Mypy: найдено {errors} предупреждений типов")
            results["mypy"] = {"status": "warnings", "errors": errors}
    except FileNotFoundError:
        print("⚠️  Mypy не установлен (опционально)")
        results["mypy"] = {"status": "not_installed"}
    except Exception as e:
        print(f"⚠️  Ошибка при проверке mypy: {e}")
        results["mypy"] = {"status": "error", "error": str(e)}
    
    print()
    
    return results


def main() -> None:
    """Главная функция."""
    print("=" * 80)
    print("ПРОВЕРКА КАЧЕСТВА КОДА")
    print("=" * 80)
    print()
    
    results = {
        "coverage": check_coverage(),
        "complexity": check_complexity(),
        "linters": check_linters(),
    }
    
    # Итоговая оценка
    print("=" * 80)
    print("ИТОГОВАЯ ОЦЕНКА")
    print("=" * 80)
    print()
    
    all_ok = True
    
    # Coverage
    coverage_ok = results["coverage"].get("meets_target", False)
    coverage_pct = results["coverage"].get("total_coverage", 0.0)
    status = "✅" if coverage_ok else "❌"
    print(f"Code Coverage: {coverage_pct:.2f}% (цель: >80%) {status}")
    if not coverage_ok:
        all_ok = False
    
    # Complexity
    complexity_ok = results["complexity"].get("meets_target", False)
    high_complexity_count = results["complexity"].get("high_complexity_count", 0)
    status = "✅" if complexity_ok else "❌"
    print(f"Cyclomatic Complexity: {high_complexity_count} функций >10 (цель: 0) {status}")
    if not complexity_ok:
        all_ok = False
    
    # Linters
    ruff_ok = results["linters"].get("ruff", {}).get("status") == "ok"
    status = "✅" if ruff_ok else "⚠️"
    print(f"Linters (Ruff): {status}")
    if not ruff_ok:
        all_ok = False
    
    print()
    
    if all_ok:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ")
        print("\nРекомендации:")
        
        if not coverage_ok:
            print("- Увеличьте code coverage до >80%")
            print("  Запустите: pytest --cov=src/obsidian_kb --cov-report=html")
            print("  Откройте htmlcov/index.html для детального анализа")
        
        if not complexity_ok:
            print("- Упростите функции с высокой сложностью")
            print("  Разбейте сложные функции на более мелкие")
        
        if not ruff_ok:
            print("- Исправьте ошибки линтера")
            print("  Запустите: ruff check --fix src/obsidian_kb")
    
    # Сохраняем результаты
    output_file = Path(__file__).parent / "code_quality_results.json"
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n💾 Результаты сохранены в {output_file}")


if __name__ == "__main__":
    main()

