"""Парсер frontmatter для markdown файлов.

Отвечает за извлечение и парсинг frontmatter из Obsidian markdown файлов.
"""

import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import yaml

from obsidian_kb.normalization import DataNormalizer

logger = logging.getLogger(__name__)


@dataclass
class FrontmatterData:
    """Распарсенные данные frontmatter."""

    title: str
    tags: list[str]
    created_at: datetime | None
    modified_at: datetime | None
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Конвертация в словарь."""
        return asdict(self)


class FrontmatterParser:
    """Парсер frontmatter из markdown файлов."""

    @staticmethod
    def sanitize_frontmatter(frontmatter_text: str) -> str:
        """Предобработка frontmatter: замена шаблонов Obsidian и исправление кавычек.

        Args:
            frontmatter_text: Исходный текст frontmatter

        Returns:
            Обработанный текст frontmatter с заменёнными шаблонами и исправленными кавычками
        """
        # Заменяем шаблоны Obsidian {{...}} на строки-заглушки
        def replace_template(match: re.Match[str]) -> str:
            """Заменяет шаблон на корректную YAML строку."""
            template_content = match.group(0)
            escaped = template_content.replace('"', '\\"')
            return f'"{escaped}"'

        # Обрабатываем случаи с двойными кавычками
        sanitized = re.sub(r'""(\{\{[^}]+\}\})""', r'\1', frontmatter_text)
        sanitized = re.sub(r'"(\{\{[^}]+\}\})"', r'\1', sanitized)
        sanitized = re.sub(r'\{\{[^}]+\}\}', replace_template, sanitized)

        # Исправляем проблемные кавычки в строках YAML
        lines = sanitized.split('\n')
        fixed_lines = []

        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                fixed_lines.append(line)
                continue

            if ':' in line:
                key_part, value_part = line.split(':', 1)
                value_part = value_part.strip()

                if value_part.startswith('"'):
                    quote_count = value_part.count('"')
                    if quote_count > 2 or (quote_count % 2 != 0 and quote_count > 1):
                        # Экранируем внутренние кавычки
                        key_colon = line.find(':')
                        first_quote_pos = line.find('"', key_colon)
                        if first_quote_pos != -1:
                            last_quote_pos = line.rfind('"')
                            if last_quote_pos > first_quote_pos:
                                before = line[:first_quote_pos + 1]
                                middle = line[first_quote_pos + 1:last_quote_pos]
                                after = line[last_quote_pos:]
                                middle_escaped = middle.replace('"', '\\"')
                                line = before + middle_escaped + after

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    @staticmethod
    def parse_frontmatter_dict(
        frontmatter: dict[str, Any], file_path: str | None = None
    ) -> FrontmatterData:
        """Парсинг frontmatter из словаря (после YAML парсинга).

        Args:
            frontmatter: Словарь с данными frontmatter
            file_path: Путь к файлу (для логирования)

        Returns:
            FrontmatterData с распарсенными данными
        """
        # Извлекаем title
        title = frontmatter.get("title", "")
        if not title and isinstance(frontmatter.get("aliases"), list):
            title = frontmatter["aliases"][0] if frontmatter["aliases"] else ""

        # Извлекаем теги с нормализацией
        raw_tags = frontmatter.get("tags", [])
        tags = DataNormalizer.normalize_tags(raw_tags)

        if raw_tags and not tags:
            logger.debug(
                f"Теги не были нормализованы (file: {file_path or 'unknown'}, raw_tags: {raw_tags})"
            )

        # Парсим даты
        created_at = None
        if "created" in frontmatter:
            created_at = FrontmatterParser._parse_date(frontmatter["created"])

        modified_at = None
        if "modified" in frontmatter:
            modified_at = FrontmatterParser._parse_date(frontmatter["modified"])

        # Остальные поля в metadata
        metadata = {
            k: v
            for k, v in frontmatter.items()
            if k not in ("title", "tags", "created", "modified", "aliases")
        }

        # Нормализуем поле type если оно есть
        if "type" in metadata:
            raw_type = metadata["type"]
            normalized_type = DataNormalizer.normalize_doc_type(raw_type)
            metadata["type"] = normalized_type

            if raw_type and not normalized_type:
                logger.debug(
                    f"Тип документа не был нормализован (file: {file_path or 'unknown'}, raw_type: {raw_type})"
                )

        return FrontmatterData(
            title=title,
            tags=tags,
            created_at=created_at,
            modified_at=modified_at,
            metadata=metadata,
        )

    @staticmethod
    def parse_frontmatter_text(
        frontmatter_text: str, file_path: str | None = None
    ) -> FrontmatterData:
        """Парсинг frontmatter из текста.

        Args:
            frontmatter_text: Текст frontmatter
            file_path: Путь к файлу (для логирования)

        Returns:
            FrontmatterData с распарсенными данными
        """
        if not frontmatter_text.strip():
            return FrontmatterData(
                title="",
                tags=[],
                created_at=None,
                modified_at=None,
                metadata={},
            )

        # Предобрабатываем frontmatter
        sanitized_frontmatter = FrontmatterParser.sanitize_frontmatter(frontmatter_text)

        try:
            parsed = yaml.safe_load(sanitized_frontmatter)
            if isinstance(parsed, dict):
                frontmatter = parsed
            else:
                logger.warning(
                    f"Frontmatter parsed as {type(parsed).__name__}, expected dict (file: {file_path or 'unknown'})"
                )
                frontmatter = {}
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse frontmatter: {e} (file: {file_path or 'unknown'})")
            frontmatter = {}

        return FrontmatterParser.parse_frontmatter_dict(frontmatter, file_path)

    @staticmethod
    def extract_frontmatter(content: str) -> tuple[str, str]:
        """Извлечение frontmatter из содержимого markdown файла.

        Args:
            content: Содержимое файла

        Returns:
            Кортеж (текст frontmatter, остальной контент без frontmatter)
        """
        # Проверяем наличие frontmatter
        if not (content.startswith("---\n") or content.startswith("---\r\n") or content.startswith("---")):
            return ("", content)

        # Ищем закрывающий ---
        end_idx = -1
        for pattern in ["\n---\n", "\r\n---\r\n", "\n---\r\n", "\r\n---\n", "\n---"]:
            idx = content.find(pattern, 4)
            if idx != -1:
                end_idx = idx
                break

        if end_idx == -1:
            logger.warning("Frontmatter не закрыт правильно (нет закрывающего '---')")
            return ("", content)

        # Определяем смещения
        if content.startswith("---\r\n"):
            start_offset = 5
        elif content.startswith("---\n"):
            start_offset = 4
        else:
            start_offset = 3

        if content[end_idx : end_idx + 5] == "\n---\n":
            end_offset = 5
        elif content[end_idx : end_idx + 6] == "\r\n---\r\n":
            end_offset = 6
        elif content[end_idx : end_idx + 5] == "\n---\r\n":
            end_offset = 5
        elif content[end_idx : end_idx + 6] == "\r\n---\n":
            end_offset = 6
        elif content[end_idx : end_idx + 4] == "\n---":
            end_offset = 4
        else:
            end_offset = 5

        frontmatter_text = content[start_offset:end_idx]
        body = content[end_idx + end_offset :]

        return (frontmatter_text, body)

    @staticmethod
    def parse(content: str, file_path: str | None = None) -> tuple[FrontmatterData, str]:
        """Полный парсинг frontmatter из содержимого файла.

        Args:
            content: Содержимое файла
            file_path: Путь к файлу (для логирования)

        Returns:
            Кортеж (FrontmatterData, остальной контент без frontmatter)
        """
        frontmatter_text, body = FrontmatterParser.extract_frontmatter(content)
        frontmatter_data = FrontmatterParser.parse_frontmatter_text(frontmatter_text, file_path)
        return (frontmatter_data, body)

    @staticmethod
    def _parse_date(date_value: Any) -> datetime | None:
        """Парсинг даты из различных форматов.

        Args:
            date_value: Значение даты (может быть строкой, datetime, timestamp)

        Returns:
            datetime объект или None если не удалось распарсить
        """
        if date_value is None:
            return None

        # Если уже datetime объект (YAML автоматически парсит даты)
        if isinstance(date_value, datetime):
            return date_value
        
        # Если date объект (YAML автоматически парсит даты в date)
        from datetime import date as date_type
        if isinstance(date_value, date_type):
            return datetime.combine(date_value, datetime.min.time())

        # Если строка
        if isinstance(date_value, str):
            date_value = date_value.strip()
            if not date_value:
                return None

            # Пробуем различные форматы
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d.%m.%Y",
                "%d.%m.%Y %H:%M:%S",
                "%d/%m/%Y",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y",
                "%m/%d/%Y %H:%M:%S",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

            # Пробуем ISO формат
            try:
                return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
            except ValueError:
                pass

            # Пробуем timestamp (число)
            try:
                timestamp = float(date_value)
                return datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                pass

        # Если число (timestamp)
        if isinstance(date_value, (int, float)):
            try:
                return datetime.fromtimestamp(float(date_value))
            except (OSError, ValueError):
                pass

        logger.warning(f"Не удалось распарсить дату: {date_value} (тип: {type(date_value).__name__})")
        return None

