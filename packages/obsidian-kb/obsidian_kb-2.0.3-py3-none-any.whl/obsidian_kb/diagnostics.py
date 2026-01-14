"""Модуль диагностики и мониторинга системы."""

import asyncio
import json
import logging
import platform
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
import lancedb

from obsidian_kb.config import settings
from obsidian_kb.metrics import MetricsCollector
from obsidian_kb.types import HealthCheck, HealthStatus, SystemHealth

logger = logging.getLogger(__name__)


class DiagnosticsService:
    """Сервис диагностики системы obsidian-kb."""

    def __init__(self) -> None:
        """Инициализация сервиса диагностики."""
        self.ollama_url = settings.ollama_url
        self.embedding_model = settings.embedding_model
        self.db_path = settings.db_path
        self.vaults_config = settings.vaults_config

    def _load_vaults_config(self) -> list[dict[str, Any]]:
        """Загрузка конфигурации vault'ов из файла.

        Returns:
            Список vault'ов из конфига
        """
        if not self.vaults_config.exists():
            return []

        try:
            with open(self.vaults_config, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("vaults", [])
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load vaults config: {e}")
            return []

    async def check_ollama(self) -> HealthCheck:
        """Проверка доступности Ollama.

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.ollama_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m["name"] for m in data.get("models", [])]
                        # Проверяем точное совпадение или совпадение с суффиксом :latest
                        model_found = (
                            self.embedding_model in models
                            or f"{self.embedding_model}:latest" in models
                            or any(m.startswith(f"{self.embedding_model}:") for m in models)
                        )
                        if model_found:
                            return HealthCheck(
                                "ollama",
                                HealthStatus.OK,
                                "Ollama доступна",
                                {"models": models, "embedding_model": self.embedding_model},
                            )
                        return HealthCheck(
                            "ollama",
                            HealthStatus.WARNING,
                            f"Модель {self.embedding_model} не найдена",
                            {"available": models, "required": self.embedding_model},
                        )
                    return HealthCheck(
                        "ollama",
                        HealthStatus.ERROR,
                        f"Ollama вернул статус {resp.status}",
                    )
        except asyncio.TimeoutError:
            return HealthCheck("ollama", HealthStatus.ERROR, "Ollama не отвечает (timeout)")
        except aiohttp.ClientError as e:
            return HealthCheck("ollama", HealthStatus.ERROR, f"Ollama недоступна: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking Ollama: {e}")
            return HealthCheck("ollama", HealthStatus.ERROR, f"Ошибка проверки Ollama: {e}")

    async def check_lancedb(self) -> HealthCheck:
        """Проверка базы данных LanceDB.

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            # Выполняем синхронную операцию в отдельном потоке
            def _check() -> tuple[bool, str, dict[str, Any] | None]:
                try:
                    db = lancedb.connect(str(self.db_path))
                    # Используем новый API
                    try:
                        result = db.list_tables()
                        if hasattr(result, "tables"):
                            tables = result.tables
                        else:
                            tables = result
                    except AttributeError:
                        # Fallback для старых версий
                        tables = db.table_names()
                    return True, f"LanceDB OK, {len(tables)} таблиц", {"tables": list(tables)}
                except Exception as e:
                    return False, f"LanceDB ошибка: {e}", None

            success, message, details = await asyncio.to_thread(_check)
            status = HealthStatus.OK if success else HealthStatus.ERROR
            return HealthCheck("lancedb", status, message, details)

        except Exception as e:
            logger.error(f"Unexpected error checking LanceDB: {e}")
            return HealthCheck("lancedb", HealthStatus.ERROR, f"Ошибка проверки LanceDB: {e}")

    async def check_vaults(self) -> HealthCheck:
        """Проверка доступности vault'ов.

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            vaults = self._load_vaults_config()
            if not vaults:
                return HealthCheck(
                    "vaults",
                    HealthStatus.WARNING,
                    "Конфигурация vault'ов не найдена",
                    {"config_path": str(self.vaults_config)},
                )

            issues: list[str] = []
            for vault in vaults:
                vault_name = vault.get("name", "unknown")
                vault_path = vault.get("path", "")
                if not vault_path:
                    issues.append(f"{vault_name}: путь не указан")
                    continue

                path = Path(vault_path)
                if not path.exists():
                    issues.append(f"{vault_name}: путь не существует ({vault_path})")
                elif not path.is_dir():
                    issues.append(f"{vault_name}: путь не является директорией ({vault_path})")
                elif not any(path.glob("*.md")):
                    issues.append(f"{vault_name}: нет .md файлов ({vault_path})")

            if not issues:
                return HealthCheck(
                    "vaults",
                    HealthStatus.OK,
                    f"Все {len(vaults)} vault'ов доступны",
                    {"vault_count": len(vaults)},
                )
            return HealthCheck(
                "vaults",
                HealthStatus.WARNING,
                "Проблемы с vault'ами",
                {"issues": issues, "vault_count": len(vaults)},
            )

        except Exception as e:
            logger.error(f"Unexpected error checking vaults: {e}")
            return HealthCheck("vaults", HealthStatus.ERROR, f"Ошибка проверки vault'ов: {e}")

    async def check_disk_space(self) -> HealthCheck:
        """Проверка свободного места на диске.

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            # Выполняем синхронную операцию в отдельном потоке
            def _check() -> tuple[float, float, float]:
                total, used, free = shutil.disk_usage(self.db_path.parent)
                return total, used, free

            total, used, free = await asyncio.to_thread(_check)
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)

            if free_gb < 1:
                return HealthCheck(
                    "disk",
                    HealthStatus.ERROR,
                    f"Мало места: {free_gb:.1f} GB свободно",
                    {"free_gb": free_gb, "total_gb": total_gb, "used_gb": used_gb},
                )
            if free_gb < 5:
                return HealthCheck(
                    "disk",
                    HealthStatus.WARNING,
                    f"Свободно {free_gb:.1f} GB",
                    {"free_gb": free_gb, "total_gb": total_gb, "used_gb": used_gb},
                )
            return HealthCheck(
                "disk",
                HealthStatus.OK,
                f"Свободно {free_gb:.1f} GB",
                {"free_gb": free_gb, "total_gb": total_gb, "used_gb": used_gb},
            )

        except Exception as e:
            logger.error(f"Unexpected error checking disk space: {e}")
            return HealthCheck("disk", HealthStatus.ERROR, f"Ошибка проверки диска: {e}")

    async def check_memory(self) -> HealthCheck:
        """Проверка использования памяти.

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            def _check() -> tuple[float, float, float]:
                if platform.system() == "Darwin":  # macOS
                    import psutil

                    mem = psutil.virtual_memory()
                    total_gb = mem.total / (1024**3)
                    used_gb = mem.used / (1024**3)
                    available_gb = mem.available / (1024**3)
                    return total_gb, used_gb, available_gb
                else:
                    # Для других платформ используем psutil если доступен
                    try:
                        import psutil

                        mem = psutil.virtual_memory()
                        total_gb = mem.total / (1024**3)
                        used_gb = mem.used / (1024**3)
                        available_gb = mem.available / (1024**3)
                        return total_gb, used_gb, available_gb
                    except ImportError:
                        # Fallback: используем системные вызовы
                        # Для Linux можно использовать /proc/meminfo
                        return 0.0, 0.0, 0.0

            total_gb, used_gb, available_gb = await asyncio.to_thread(_check)

            if total_gb == 0.0:
                return HealthCheck(
                    "memory",
                    HealthStatus.WARNING,
                    "Не удалось получить информацию о памяти (установите psutil для полной диагностики)",
                    {},
                )

            percent_used = (used_gb / total_gb) * 100 if total_gb > 0 else 0

            if percent_used > 90:
                return HealthCheck(
                    "memory",
                    HealthStatus.ERROR,
                    f"Критическое использование памяти: {percent_used:.1f}%",
                    {
                        "total_gb": total_gb,
                        "used_gb": used_gb,
                        "available_gb": available_gb,
                        "percent_used": percent_used,
                    },
                )
            if percent_used > 75:
                return HealthCheck(
                    "memory",
                    HealthStatus.WARNING,
                    f"Высокое использование памяти: {percent_used:.1f}%",
                    {
                        "total_gb": total_gb,
                        "used_gb": used_gb,
                        "available_gb": available_gb,
                        "percent_used": percent_used,
                    },
                )
            return HealthCheck(
                "memory",
                HealthStatus.OK,
                f"Память: {percent_used:.1f}% использовано",
                {
                    "total_gb": total_gb,
                    "used_gb": used_gb,
                    "available_gb": available_gb,
                    "percent_used": percent_used,
                },
            )

        except ImportError:
            return HealthCheck(
                "memory",
                HealthStatus.WARNING,
                "psutil не установлен, проверка памяти недоступна",
                {},
            )
        except Exception as e:
            logger.error(f"Unexpected error checking memory: {e}")
            return HealthCheck("memory", HealthStatus.ERROR, f"Ошибка проверки памяти: {e}")

    async def check_cpu(self) -> HealthCheck:
        """Проверка нагрузки на CPU.

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            def _check() -> tuple[float, int]:
                try:
                    import psutil

                    # Получаем загрузку CPU за последнюю секунду
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    cpu_count = psutil.cpu_count()
                    return cpu_percent, cpu_count
                except ImportError:
                    return 0.0, 0

            cpu_percent, cpu_count = await asyncio.to_thread(_check)

            if cpu_count == 0:
                return HealthCheck(
                    "cpu",
                    HealthStatus.WARNING,
                    "Не удалось получить информацию о CPU (установите psutil для полной диагностики)",
                    {},
                )

            if cpu_percent > 90:
                return HealthCheck(
                    "cpu",
                    HealthStatus.WARNING,
                    f"Высокая нагрузка на CPU: {cpu_percent:.1f}%",
                    {"cpu_percent": cpu_percent, "cpu_count": cpu_count},
                )
            return HealthCheck(
                "cpu",
                HealthStatus.OK,
                f"CPU: {cpu_percent:.1f}%",
                {"cpu_percent": cpu_percent, "cpu_count": cpu_count},
            )

        except ImportError:
            return HealthCheck(
                "cpu",
                HealthStatus.WARNING,
                "psutil не установлен, проверка CPU недоступна",
                {},
            )
        except Exception as e:
            logger.error(f"Unexpected error checking CPU: {e}")
            return HealthCheck("cpu", HealthStatus.ERROR, f"Ошибка проверки CPU: {e}")

    async def check_performance(self) -> HealthCheck:
        """Проверка производительности системы (время ответа БД).

        Returns:
            HealthCheck с результатом проверки
        """
        try:
            def _check() -> tuple[bool, float]:
                start_time = time.time()
                try:
                    db = lancedb.connect(str(self.db_path))
                    # Простая операция для проверки производительности
                    try:
                        result = db.list_tables()
                        if hasattr(result, "tables"):
                            _ = result.tables
                        else:
                            _ = result
                    except AttributeError:
                        _ = db.table_names()
                    elapsed = time.time() - start_time
                    return True, elapsed
                except Exception:
                    elapsed = time.time() - start_time
                    return False, elapsed

            success, elapsed_ms = await asyncio.to_thread(_check)
            elapsed_ms = elapsed_ms * 1000  # Конвертируем в миллисекунды

            if not success:
                return HealthCheck(
                    "performance",
                    HealthStatus.ERROR,
                    "Ошибка при проверке производительности БД",
                    {"response_time_ms": elapsed_ms},
                )

            if elapsed_ms > 1000:
                return HealthCheck(
                    "performance",
                    HealthStatus.WARNING,
                    f"Медленный ответ БД: {elapsed_ms:.1f} мс",
                    {"response_time_ms": elapsed_ms},
                )
            return HealthCheck(
                "performance",
                HealthStatus.OK,
                f"Производительность БД: {elapsed_ms:.1f} мс",
                {"response_time_ms": elapsed_ms},
            )

        except Exception as e:
            logger.error(f"Unexpected error checking performance: {e}")
            return HealthCheck("performance", HealthStatus.ERROR, f"Ошибка проверки производительности: {e}")

    async def full_check(self, send_notifications: bool = False) -> SystemHealth:
        """Полная диагностика системы.

        Args:
            send_notifications: Отправлять ли уведомления о проблемах

        Returns:
            SystemHealth с результатами всех проверок
        """
        checks = await asyncio.gather(
            self.check_ollama(),
            self.check_lancedb(),
            self.check_vaults(),
            self.check_disk_space(),
            self.check_memory(),
            self.check_cpu(),
            self.check_performance(),
        )

        # Определяем общий статус
        if any(c.status == HealthStatus.ERROR for c in checks):
            overall = HealthStatus.ERROR
        elif any(c.status == HealthStatus.WARNING for c in checks):
            overall = HealthStatus.WARNING
        else:
            overall = HealthStatus.OK

        # Отправляем уведомления при необходимости
        if send_notifications:
            error_checks = [c for c in checks if c.status == HealthStatus.ERROR]
            if error_checks:
                error_names = [c.component for c in error_checks]
                send_notification(
                    "obsidian-kb: Критические проблемы",
                    f"Обнаружены проблемы: {', '.join(error_names)}",
                    sound=True,
                )
            elif overall == HealthStatus.WARNING:
                warning_checks = [c for c in checks if c.status == HealthStatus.WARNING]
                warning_names = [c.component for c in warning_checks]
                send_notification(
                    "obsidian-kb: Предупреждения",
                    f"Предупреждения: {', '.join(warning_names)}",
                    sound=False,
                )

        return SystemHealth(overall=overall, checks=list(checks), timestamp=datetime.now())
    
    async def index_coverage(self, vault_name: str) -> dict[str, Any]:
        """Проверка покрытия индекса для vault'а.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Словарь со статистикой покрытия индекса
        """
        try:
            # Lazy import для избежания циклического импорта
            from obsidian_kb.lance_db import LanceDBManager
            db_manager = LanceDBManager()
            vaults = self._load_vaults_config()
            
            # Находим vault в конфиге
            vault_config = next((v for v in vaults if v.get("name") == vault_name), None)
            if not vault_config:
                return {
                    "error": f"Vault '{vault_name}' не найден в конфигурации",
                    "vault_name": vault_name,
                }
            
            vault_path = Path(vault_config["path"])
            if not vault_path.exists():
                return {
                    "error": f"Путь к vault'у не существует: {vault_path}",
                    "vault_name": vault_name,
                }
            
            # Получаем статистику из БД (v4 - используем 4 таблицы)
            try:
                # Получаем таблицы v4
                documents_table = await db_manager._ensure_table(vault_name, "documents")
                chunks_table = await db_manager._ensure_table(vault_name, "chunks")
                metadata_table = await db_manager._ensure_table(vault_name, "metadata")
                properties_table = await db_manager._ensure_table(vault_name, "document_properties")
                
                # Подсчитываем документы по типам из таблицы properties
                type_stats = {}
                try:
                    properties_arrow = properties_table.to_arrow()
                    if properties_arrow.num_rows > 0 and "property_key" in properties_arrow.column_names:
                        # Фильтруем только type свойства
                        type_properties = [
                            (properties_arrow["property_key"][i].as_py(), properties_arrow["property_value"][i].as_py())
                            for i in range(properties_arrow.num_rows)
                            if properties_arrow["property_key"][i].as_py() == "type"
                        ]
                        type_counts = {}
                        for _, type_value in type_properties:
                            type_counts[type_value] = type_counts.get(type_value, 0) + 1
                        type_stats = {str(k): int(v) for k, v in type_counts.items() if k is not None}
                except Exception as e:
                    logger.debug(f"Could not get type stats from properties: {e}")
                
                # Статистика по тегам из таблицы metadata (frontmatter) и chunks (inline)
                tag_stats = {"frontmatter": {}, "inline": {}}
                try:
                    # Frontmatter теги из metadata
                    metadata_arrow = metadata_table.to_arrow()
                    if metadata_arrow.num_rows > 0 and "frontmatter_tags" in metadata_arrow.column_names:
                        frontmatter_tags = []
                        tags_list = metadata_arrow["frontmatter_tags"].to_pylist()
                        for tags in tags_list:
                            if isinstance(tags, list):
                                frontmatter_tags.extend(tags)
                        tag_stats["frontmatter"] = {tag: frontmatter_tags.count(tag) for tag in set(frontmatter_tags)}
                    
                    # Inline теги из chunks
                    chunks_arrow = chunks_table.to_arrow()
                    if chunks_arrow.num_rows > 0 and "inline_tags" in chunks_arrow.column_names:
                        inline_tags = []
                        tags_list = chunks_arrow["inline_tags"].to_pylist()
                        for tags in tags_list:
                            if isinstance(tags, list):
                                inline_tags.extend(tags)
                        tag_stats["inline"] = {tag: inline_tags.count(tag) for tag in set(inline_tags)}
                except Exception as e:
                    logger.debug(f"Could not get tag stats: {e}")
                
                # Статистика по ссылкам из chunks
                link_stats = {}
                try:
                    chunks_arrow = chunks_table.to_arrow()
                    if chunks_arrow.num_rows > 0 and "links" in chunks_arrow.column_names:
                        links = []
                        links_list = chunks_arrow["links"].to_pylist()
                        for link_list in links_list:
                            if isinstance(link_list, list):
                                links.extend(link_list)
                        link_stats = {link: links.count(link) for link in set(links)}
                except Exception as e:
                    logger.debug(f"Could not get link stats: {e}")
                
                # Подсчитываем файлы в vault'е
                md_files = list(vault_path.rglob("*.md"))
                total_files = len(md_files)
                
                # Подсчитываем индексированные файлы из таблицы documents
                documents_arrow = documents_table.to_arrow()
                indexed_files = documents_arrow.num_rows if documents_arrow.num_rows > 0 else 0
                
                # Количество чанков из chunks
                chunks_arrow = chunks_table.to_arrow()
                total_chunks = chunks_arrow.num_rows if chunks_arrow.num_rows > 0 else 0
                
                return {
                    "vault_name": vault_name,
                    "vault_path": str(vault_path),
                    "total_files": total_files,
                    "indexed_files": indexed_files,
                    "coverage_percent": (indexed_files / total_files * 100) if total_files > 0 else 0,
                    "total_chunks": total_chunks,
                    "type_stats": type_stats,
                    "tag_stats": tag_stats,
                    "link_stats": link_stats,
                }
            except Exception as e:
                logger.error(f"Error getting index coverage: {e}")
                return {
                    "error": f"Ошибка получения статистики: {e}",
                    "vault_name": vault_name,
                }
        except Exception as e:
            logger.error(f"Unexpected error in index_coverage: {e}")
            return {
                "error": f"Ошибка проверки покрытия индекса: {e}",
                "vault_name": vault_name,
            }
    
    async def check_metrics(self, days: int = 1) -> dict[str, Any]:
        """Проверка записи метрик.
        
        Args:
            days: Количество дней для проверки
            
        Returns:
            Словарь со статистикой метрик
        """
        try:
            metrics_collector = MetricsCollector()
            metrics = metrics_collector.get_metrics(days=days)
            
            return {
                "total_queries": metrics.get("total_queries", 0),
                "total_searches": metrics.get("total_searches", 0),
                "average_response_time": metrics.get("average_response_time", 0),
                "days": days,
                "metrics_db_exists": metrics_collector.db_path.exists() if hasattr(metrics_collector, "db_path") else False,
            }
        except Exception as e:
            logger.error(f"Error checking metrics: {e}")
            return {
                "error": f"Ошибка проверки метрик: {e}",
                "days": days,
            }
    
    async def check_index(self, vault_name: str) -> dict[str, Any]:
        """Проверка индексации vault'а.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Словарь с результатами проверки индексации
        """
        try:
            # Lazy import для избежания циклического импорта
            from obsidian_kb.lance_db import LanceDBManager
            db_manager = LanceDBManager()
            vaults = self._load_vaults_config()
            
            # Находим vault в конфиге
            vault_config = next((v for v in vaults if v.get("name") == vault_name), None)
            if not vault_config:
                return {
                    "error": f"Vault '{vault_name}' не найден в конфигурации",
                    "vault_name": vault_name,
                }
            
            vault_path = Path(vault_config["path"])
            if not vault_path.exists():
                return {
                    "error": f"Путь к vault'у не существует: {vault_path}",
                    "vault_name": vault_name,
                }
            
            # Проверяем наличие таблиц в БД (v4 - используем 4 таблицы)
            try:
                documents_table = await db_manager._ensure_table(vault_name, "documents")
                chunks_table = await db_manager._ensure_table(vault_name, "chunks")
                metadata_table = await db_manager._ensure_table(vault_name, "metadata")
            except Exception as e:
                return {
                    "error": f"Таблицы для vault '{vault_name}' не найдены в БД: {e}",
                    "vault_name": vault_name,
                    "needs_indexing": True,
                }
            
            # Получаем статистику индексации
            try:
                issues = []
                
                # Проверяем таблицу documents
                documents_arrow = documents_table.to_arrow()
                total_documents = documents_arrow.num_rows
                
                if total_documents == 0:
                    issues.append("Нет проиндексированных документов")
                else:
                    # Проверяем индексацию дат в documents
                    if "created_at" in documents_arrow.column_names:
                        created_ats = documents_arrow["created_at"].to_pylist()
                        docs_without_created = sum(1 for ca in created_ats if not ca or ca == "")
                        if docs_without_created > 0:
                            issues.append(f"Документов без даты создания: {docs_without_created}")
                    
                    if "modified_at" in documents_arrow.column_names:
                        modified_ats = documents_arrow["modified_at"].to_pylist()
                        docs_without_modified = sum(1 for ma in modified_ats if not ma or ma == "")
                        if docs_without_modified > 0:
                            issues.append(f"Документов без даты модификации: {docs_without_modified}")
                
                # Проверяем таблицу chunks
                chunks_arrow = chunks_table.to_arrow()
                total_chunks = chunks_arrow.num_rows
                
                if total_chunks == 0:
                    issues.append("Нет проиндексированных чанков")
                else:
                    # Проверяем индексацию links в chunks
                    if "links" in chunks_arrow.column_names:
                        links_list = chunks_arrow["links"].to_pylist()
                        chunks_without_links = sum(1 for links in links_list if not links or len(links) == 0)
                        if chunks_without_links > 0:
                            issues.append(f"Чанков без ссылок: {chunks_without_links}")
                    
                    # Проверяем индексацию inline тегов в chunks
                    if "inline_tags" in chunks_arrow.column_names:
                        inline_tags_list = chunks_arrow["inline_tags"].to_pylist()
                        chunks_without_inline_tags = sum(1 for tags in inline_tags_list if not tags or len(tags) == 0)
                        if chunks_without_inline_tags > 0:
                            issues.append(f"Чанков без inline тегов: {chunks_without_inline_tags}")
                
                # Проверяем таблицу metadata
                metadata_arrow = metadata_table.to_arrow()
                if metadata_arrow.num_rows > 0:
                    if "frontmatter_tags" in metadata_arrow.column_names:
                        frontmatter_tags_list = metadata_arrow["frontmatter_tags"].to_pylist()
                        docs_without_frontmatter_tags = sum(1 for tags in frontmatter_tags_list if not tags or len(tags) == 0)
                        if docs_without_frontmatter_tags > 0:
                            issues.append(f"Документов без frontmatter тегов: {docs_without_frontmatter_tags}")
                
                return {
                    "vault_name": vault_name,
                    "indexed": True,
                    "total_documents": total_documents,
                    "total_chunks": total_chunks,
                    "issues": issues,
                    "status": "ok" if not issues else "warning",
                }
            except Exception as e:
                logger.error(f"Error checking index: {e}")
                return {
                    "error": f"Ошибка проверки индекса: {e}",
                    "vault_name": vault_name,
                }
        except Exception as e:
            logger.error(f"Unexpected error in check_index: {e}")
            return {
                "error": f"Ошибка проверки индексации: {e}",
                "vault_name": vault_name,
            }


def send_notification(title: str, message: str, sound: bool = True) -> None:
    """Отправить системное уведомление macOS.

    Args:
        title: Заголовок уведомления
        message: Текст уведомления
        sound: Воспроизводить ли звук
    """
    import subprocess

    script = f'display notification "{message}" with title "{title}"'
    if sound:
        script += ' sound name "Funk"'

    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except Exception as e:
        logger.warning(f"Failed to send macOS notification: {e}")

