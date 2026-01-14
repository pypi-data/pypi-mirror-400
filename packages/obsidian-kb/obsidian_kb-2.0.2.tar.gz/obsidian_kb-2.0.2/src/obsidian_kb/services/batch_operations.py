"""BatchOperations для массовых операций над vault'ами.

Предоставляет экспорт данных в CSV и сравнение схем frontmatter между vault'ами.
"""

import asyncio
import csv
import logging
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from obsidian_kb.interfaces import IBatchOperations
from obsidian_kb.query.where_parser import WhereParser
from obsidian_kb.types import VaultNotFoundError

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager

logger = logging.getLogger(__name__)


class BatchOperations(IBatchOperations):
    """Реализация массовых операций над vault'ами."""

    def __init__(self) -> None:
        """Инициализация BatchOperations."""
        self._services = None  # Lazy initialization

    @property
    def _get_services(self):
        """Получить ServiceContainer (lazy import для избежания циклических зависимостей)."""
        if self._services is None:
            from obsidian_kb.service_container import get_service_container
            self._services = get_service_container()
        return self._services

    @property
    def _db_manager(self) -> "LanceDBManager":
        """Получить менеджер БД."""
        return self._get_services.db_manager

    async def export_to_csv(
        self,
        vault_name: str,
        output_path: str | None = None,
        doc_type: str | None = None,
        fields: str | None = None,
        where: str | None = None,
    ) -> str:
        """Экспорт данных vault'а в CSV файл.

        Args:
            vault_name: Имя vault'а
            output_path: Путь для сохранения (если не указан — временный файл)
            doc_type: Опционально — фильтр по типу документа
            fields: Поля через запятую (если не указано — все поля)
            where: Условия фильтрации (SQL-like WHERE clause)

        Returns:
            Путь к созданному CSV файлу

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
            IOError: При ошибке записи файла
        """
        try:
            # Получаем таблицы
            documents_table = await self._db_manager._ensure_table(vault_name, "documents")
            properties_table = await self._db_manager._ensure_table(
                vault_name, "document_properties"
            )

            def _export_data() -> str:
                def _filter_by_doc_type(all_docs: list, all_props: list, doc_type: str) -> tuple[list, list]:
                    """Фильтрует документы и свойства по типу в Python."""
                    props_by_doc_temp: dict[str, dict[str, Any]] = {}
                    for prop in all_props:
                        d_id = prop["document_id"]
                        if d_id not in props_by_doc_temp:
                            props_by_doc_temp[d_id] = {}
                        props_by_doc_temp[d_id][prop["property_key"]] = prop.get("property_value")
                    doc_ids_with_type = {d_id for d_id, props in props_by_doc_temp.items()
                                        if props.get("type") == doc_type}
                    return (
                        [d for d in all_docs if d["document_id"] in doc_ids_with_type],
                        [p for p in all_props if p["document_id"] in doc_ids_with_type]
                    )

                try:
                    # Шаг 1 и 2: Получаем документы и свойства
                    # Если указан doc_type, пробуем WHERE фильтрацию для оптимизации
                    if doc_type:
                        try:
                            # Сначала получаем document_ids с нужным типом
                            doc_type_escaped = doc_type.replace("'", "''")
                            type_where = f"property_key = 'type' AND property_value = '{doc_type_escaped}'"
                            type_docs = properties_table.search().where(type_where).to_arrow().to_pylist()

                            # Проверяем, что результат — это список, а не MagicMock
                            if not isinstance(type_docs, list):
                                raise TypeError("Expected list, got mock")

                            doc_ids_with_type = {d["document_id"] for d in type_docs}

                            if not doc_ids_with_type:
                                all_docs = []
                                all_props = []
                            else:
                                # Получаем только нужные документы
                                doc_ids_list = list(doc_ids_with_type)
                                if len(doc_ids_list) <= 100:
                                    # Для небольшого количества используем IN
                                    placeholders = ", ".join([f"'{d.replace(chr(39), chr(39)+chr(39))}'" for d in doc_ids_list])
                                    doc_where = f"document_id IN ({placeholders})"
                                    all_docs = documents_table.search().where(doc_where).to_arrow().to_pylist()
                                    all_props = properties_table.search().where(doc_where).to_arrow().to_pylist()
                                else:
                                    # Для большого количества загружаем всё и фильтруем
                                    all_docs = [d for d in documents_table.to_arrow().to_pylist()
                                               if d["document_id"] in doc_ids_with_type]
                                    all_props = [p for p in properties_table.to_arrow().to_pylist()
                                                if p["document_id"] in doc_ids_with_type]
                        except (AttributeError, TypeError):
                            # Fallback для тестов с моками без .search()
                            all_docs = documents_table.to_arrow().to_pylist()
                            all_props = properties_table.to_arrow().to_pylist()
                            all_docs, all_props = _filter_by_doc_type(all_docs, all_props, doc_type)
                    else:
                        # Без фильтра по типу — загружаем всё
                        all_docs = documents_table.to_arrow().to_pylist()
                        all_props = properties_table.to_arrow().to_pylist()

                    props_by_doc: dict[str, dict[str, Any]] = {}

                    for prop in all_props:
                        doc_id = prop["document_id"]
                        if doc_id not in props_by_doc:
                            props_by_doc[doc_id] = {}
                        props_by_doc[doc_id][prop["property_key"]] = prop.get(
                            "property_value"
                        )

                    # Шаг 3: Объединяем документы с их свойствами
                    enriched_docs = []
                    for doc in all_docs:
                        doc_id = doc["document_id"]
                        enriched = {**doc}

                        if doc_id in props_by_doc:
                            enriched.update(props_by_doc[doc_id])

                        enriched_docs.append(enriched)

                    # Шаг 4: Фильтрация по doc_type (уже сделана на уровне БД если указан)

                    # Шаг 5: Фильтрация по WHERE условиям
                    if where:
                        where_conditions = WhereParser.parse(where)
                        if where_conditions:
                            filtered_docs = []
                            for doc in enriched_docs:
                                if where_conditions.evaluate(doc):
                                    filtered_docs.append(doc)
                            enriched_docs = filtered_docs

                    if not enriched_docs:
                        logger.warning(f"No documents found for export in vault {vault_name}")
                        # Создаём пустой CSV файл
                        if output_path:
                            csv_path = Path(output_path)
                        else:
                            csv_file = tempfile.NamedTemporaryFile(
                                mode="w", suffix=".csv", delete=False
                            )
                            csv_path = Path(csv_file.name)
                            csv_file.close()

                        with open(csv_path, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(["No documents found"])

                        return str(csv_path)

                    # Шаг 6: Определяем поля для экспорта
                    if fields:
                        field_list = [f.strip() for f in fields.split(",")]
                    else:
                        # Собираем все уникальные поля из всех документов
                        all_fields = set()
                        for doc in enriched_docs:
                            all_fields.update(doc.keys())
                        field_list = sorted(all_fields)

                    # Шаг 7: Создаём CSV файл
                    if output_path:
                        csv_path = Path(output_path)
                    else:
                        csv_file = tempfile.NamedTemporaryFile(
                            mode="w", suffix=".csv", delete=False
                        )
                        csv_path = Path(csv_file.name)
                        csv_file.close()

                    with open(csv_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=field_list, extrasaction="ignore")
                        writer.writeheader()

                        for doc in enriched_docs:
                            # Преобразуем значения в строки для CSV
                            row = {}
                            for field in field_list:
                                value = doc.get(field)
                                if value is None:
                                    row[field] = ""
                                elif isinstance(value, (list, dict)):
                                    row[field] = str(value)
                                else:
                                    row[field] = str(value)
                            writer.writerow(row)

                    logger.info(
                        f"Exported {len(enriched_docs)} documents to {csv_path}"
                    )
                    return str(csv_path)

                except Exception as e:
                    logger.error(f"Error exporting to CSV: {e}")
                    raise

            return await asyncio.to_thread(_export_data)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error exporting to CSV for vault {vault_name}: {e}")
            raise

    async def compare_schemas(
        self,
        vault_names: list[str],
    ) -> dict[str, Any]:
        """Сравнить схемы frontmatter нескольких vault'ов.

        Показывает общие поля, уникальные поля и различия в значениях.

        Args:
            vault_names: Список имён vault'ов для сравнения

        Returns:
            Словарь с результатами сравнения:
            - "common_fields": список общих полей
            - "unique_fields": словарь {vault_name: [поля]}
            - "field_differences": словарь {field: {vault_name: пример_значения}}
            - "vault_stats": словарь {vault_name: количество_документов}

        Raises:
            VaultNotFoundError: Если хотя бы один vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            frontmatter_api = self._get_services.frontmatter_api

            # Получаем схемы для всех vault'ов
            schemas = {}
            for vault_name in vault_names:
                schema = await frontmatter_api.get_schema(vault_name)
                schemas[vault_name] = schema

            def _compare() -> dict[str, Any]:
                # Собираем все поля из всех vault'ов
                all_fields: dict[str, set[str]] = {}
                vault_stats: dict[str, int] = {}
                field_examples: dict[str, dict[str, Any]] = defaultdict(dict)

                for vault_name, schema in schemas.items():
                    vault_stats[vault_name] = schema.total_documents
                    vault_fields = set(schema.fields.keys())
                    all_fields[vault_name] = vault_fields

                    # Сохраняем примеры значений для каждого поля
                    for field_name, field_info in schema.fields.items():
                        if field_info.unique_values:
                            field_examples[field_name][vault_name] = field_info.unique_values[
                                :3
                            ]  # Первые 3 значения

                # Находим общие поля (присутствуют во всех vault'ах)
                if not all_fields:
                    return {
                        "common_fields": [],
                        "unique_fields": {},
                        "field_differences": {},
                        "vault_stats": vault_stats,
                    }

                common_fields = set.intersection(*all_fields.values())

                # Находим уникальные поля для каждого vault'а
                unique_fields: dict[str, list[str]] = {}
                for vault_name, fields in all_fields.items():
                    unique = fields - common_fields
                    unique_fields[vault_name] = sorted(unique)

                # Формируем различия в значениях для общих полей
                field_differences: dict[str, dict[str, Any]] = {}
                for field in common_fields:
                    if field in field_examples:
                        field_differences[field] = field_examples[field]

                return {
                    "common_fields": sorted(common_fields),
                    "unique_fields": unique_fields,
                    "field_differences": field_differences,
                    "vault_stats": vault_stats,
                }

            return await asyncio.to_thread(_compare)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error comparing schemas: {e}")
            raise

