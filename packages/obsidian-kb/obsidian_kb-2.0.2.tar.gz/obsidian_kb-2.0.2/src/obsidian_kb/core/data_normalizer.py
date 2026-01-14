"""Модуль для нормализации данных при индексации и поиске.

Обеспечивает консистентную нормализацию тегов, ссылок, типов документов
и других данных для корректной работы фильтров поиска.
"""

import hashlib
import json
from datetime import date, datetime
from typing import Any


class DataNormalizer:
    """Централизованная нормализация данных для obsidian-kb."""

    @staticmethod
    def normalize_tag(tag: str) -> str:
        """Нормализация тега: lowercase, trim, удаление пустых значений.

        Args:
            tag: Исходный тег

        Returns:
            Нормализованный тег или пустая строка
        """
        if not tag or not isinstance(tag, str):
            return ""
        return tag.strip().lower()

    @staticmethod
    def normalize_tags(tags: list[str] | str | None) -> list[str]:
        """Нормализация списка тегов.

        Args:
            tags: Список тегов или строка

        Returns:
            Список нормализованных тегов без дубликатов
        """
        if not tags:
            return []

        if isinstance(tags, str):
            tags = [tags]

        normalized = [DataNormalizer.normalize_tag(tag) for tag in tags]
        # Убираем пустые и дубликаты, сохраняем порядок
        seen: set[str] = set()
        result: list[str] = []
        for tag in normalized:
            if tag and tag not in seen:
                seen.add(tag)
                result.append(tag)

        return result

    @staticmethod
    def normalize_link(link: str) -> str:
        """Нормализация wikilink: извлечение имени файла, lowercase, trim.

        Args:
            link: Wikilink в формате [[link]] или [[path/to/file]] или [[link|display]]

        Returns:
            Нормализованное имя файла (без пути и расширения)
        """
        if not link or not isinstance(link, str):
            return ""

        # Убираем отображение если есть: [[link|display]] -> link
        link = link.split("|")[0].strip()

        # Извлекаем имя файла из пути: path/to/file -> file
        if "/" in link:
            link = link.split("/")[-1]

        # Убираем расширение .md если есть
        if link.endswith(".md"):
            link = link[:-3]

        return link.strip().lower()

    @staticmethod
    def normalize_links(links: list[str] | None) -> list[str]:
        """Нормализация списка wikilinks.

        Args:
            links: Список wikilinks

        Returns:
            Список нормализованных ссылок без дубликатов
        """
        if not links:
            return []

        normalized = [DataNormalizer.normalize_link(link) for link in links]
        # Убираем пустые и дубликаты
        seen: set[str] = set()
        result: list[str] = []
        for link in normalized:
            if link and link not in seen:
                seen.add(link)
                result.append(link)

        return result

    @staticmethod
    def normalize_doc_type(doc_type: str | None) -> str:
        """Нормализация типа документа: lowercase, trim.

        Args:
            doc_type: Тип документа из frontmatter

        Returns:
            Нормализованный тип документа или пустая строка
        """
        if not doc_type or not isinstance(doc_type, str):
            return ""
        return doc_type.strip().lower()

    @staticmethod
    def normalize_string(value: str) -> str:
        """Нормализация строкового значения: lowercase, trim.

        Args:
            value: Исходная строка

        Returns:
            Нормализованная строка
        """
        if not value or not isinstance(value, str):
            return ""
        return value.strip().lower()

    @staticmethod
    def escape_sql_string(value: str) -> str:
        """Экранирование строки для SQL запросов.

        Args:
            value: Строка для экранирования

        Returns:
            Экранированная строка
        """
        if not value:
            return ""
        return value.replace("'", "''")

    @staticmethod
    def normalize_property_value(value: Any) -> str:
        """Нормализация значения свойства для индексации.

        Args:
            value: Значение свойства

        Returns:
            Нормализованное строковое значение
        """
        if isinstance(value, str):
            return DataNormalizer.normalize_string(value)
        elif isinstance(value, (int, float)):
            return str(value).lower()
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, list):
            # Для массивов нормализуем каждый элемент
            normalized_items = [DataNormalizer.normalize_property_value(item) for item in value]
            return ",".join(normalized_items)
        else:
            return str(value).lower()

    @staticmethod
    def get_property_type(value: Any) -> str:
        """Определение типа значения свойства.

        Args:
            value: Значение свойства

        Returns:
            Тип значения (string, number, date, array, boolean)
        """
        if isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            # Важно: проверка bool должна быть перед int/float,
            # т.к. bool является подклассом int в Python
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, (date, datetime)):
            return "date"
        elif isinstance(value, list):
            return "array"
        else:
            return "string"

    @staticmethod
    def serialize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        """Сериализация метаданных для хранения.

        Преобразует datetime/date объекты в ISO формат.

        Args:
            metadata: Словарь метаданных

        Returns:
            Словарь с сериализованными значениями
        """
        result: dict[str, Any] = {}
        for key, value in metadata.items():
            if isinstance(value, (date, datetime)):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = DataNormalizer.serialize_metadata(value)
            elif isinstance(value, list):
                result[key] = [
                    item.isoformat() if isinstance(item, (date, datetime)) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    @staticmethod
    def compute_metadata_hash(metadata: dict[str, Any]) -> str:
        """Вычисление хеша метаданных для отслеживания изменений.

        Args:
            metadata: Метаданные документа

        Returns:
            SHA256 хеш метаданных
        """
        serialized = DataNormalizer.serialize_metadata(metadata)
        metadata_str = json.dumps(serialized, sort_keys=True)
        return hashlib.sha256(metadata_str.encode()).hexdigest()

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Вычисление хеша контента.

        Args:
            content: Строка контента

        Returns:
            SHA256 хеш (первые 16 символов)
        """
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @staticmethod
    def normalize_vault_name(name: str) -> str:
        """Нормализация имени vault: lowercase, trim, замена пробелов.

        Args:
            name: Исходное имя vault'а

        Returns:
            Нормализованное имя
        """
        if not name or not isinstance(name, str):
            return ""
        # Убираем пробелы по краям, приводим к нижнему регистру
        normalized = name.strip().lower()
        # Заменяем пробелы на подчёркивания для безопасного использования в путях
        normalized = normalized.replace(" ", "_")
        return normalized
