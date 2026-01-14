"""Модуль индексирования Obsidian vault'ов."""

import asyncio
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from obsidian_kb.batch_processor import BatchProcessor
from obsidian_kb.config import settings
from obsidian_kb.file_parsers import extract_text_from_file
from obsidian_kb.frontmatter_parser import FrontmatterData, FrontmatterParser
from obsidian_kb.ignore_patterns import load_ignore_patterns
from obsidian_kb.normalization import DataNormalizer
from obsidian_kb.structured_logging import get_logger, LogContext
from obsidian_kb.types import DocumentChunk, IndexingError

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IEmbeddingCache

logger = get_logger(__name__)


class ProcessedMarkdownContent(TypedDict):
    """Результат обработки markdown контента."""

    title: str
    frontmatter_tags: list[str]
    inline_tags: list[str]
    all_tags: list[str]
    wikilinks: list[str]
    code_blocks: list[tuple[str, str, str]]  # (language, code_content, section_context)
    sections: list[tuple[str, str]]  # (section_title, section_content)
    created_at: datetime
    modified_at: datetime


# FrontmatterData импортируется из frontmatter_parser


class VaultIndexer:
    """Индексатор Obsidian vault'ов."""

    def __init__(
        self,
        vault_path: Path,
        vault_name: str,
        embedding_cache: "IEmbeddingCache | None" = None,
    ) -> None:
        """Инициализация индексатора.

        Args:
            vault_path: Путь к vault'у
            vault_name: Имя vault'а
            embedding_cache: Кэш embeddings для инвалидации при изменении файлов (опционально)
        """
        self.vault_path = Path(vault_path).resolve()
        self.vault_name = vault_name
        self.observer: Observer | None = None
        self.embedding_cache: "IEmbeddingCache | None" = embedding_cache
        # Путь к текущему файлу (для контекста при парсинге frontmatter)
        self._current_file_path: str | None = None

        # Загружаем паттерны игнорирования
        self.ignore_matcher = load_ignore_patterns(self.vault_path)

        if not self.vault_path.exists():
            raise IndexingError(f"Vault path does not exist: {self.vault_path}")

        if not self.vault_path.is_dir():
            raise IndexingError(f"Vault path is not a directory: {self.vault_path}")

    def _sanitize_frontmatter(self, frontmatter_text: str) -> str:
        """Предобработка frontmatter: замена шаблонов Obsidian и исправление кавычек.

        Args:
            frontmatter_text: Исходный текст frontmatter

        Returns:
            Обработанный текст frontmatter с заменёнными шаблонами и исправленными кавычками
        """
        return FrontmatterParser.sanitize_frontmatter(frontmatter_text)

    def _parse_frontmatter_from_text(self, frontmatter_text: str, body: str) -> FrontmatterData:
        """Парсинг frontmatter из отдельного текста (для потокового чтения).

        Args:
            frontmatter_text: Текст frontmatter
            body: Тело документа (не используется, для совместимости)

        Returns:
            FrontmatterData
        """
        return FrontmatterParser.parse_frontmatter_text(frontmatter_text, self._current_file_path)

    def _parse_frontmatter(self, content: str) -> tuple[FrontmatterData, str]:
        """Парсинг frontmatter из markdown файла.

        Args:
            content: Содержимое файла

        Returns:
            Кортеж (FrontmatterData, остальной контент без frontmatter)
        """
        return FrontmatterParser.parse(content, self._current_file_path)

    def _parse_date(self, date_value: Any) -> datetime | None:
        """Парсинг даты из различных форматов.

        Args:
            date_value: Значение даты (может быть строкой, datetime, timestamp)

        Returns:
            datetime или None
        """
        # Используем FrontmatterParser для парсинга дат
        return FrontmatterParser._parse_date(date_value)

    def _extract_inline_tags(self, text: str) -> list[str]:
        """Извлечение inline-тегов из текста.

        Args:
            text: Текст для поиска тегов

        Returns:
            Список найденных нормализованных тегов
        """
        # Регулярное выражение для тегов: #tag или #tag-name
        pattern = r"#([\w-]+)"
        raw_tags = re.findall(pattern, text)
        # Нормализуем теги
        return DataNormalizer.normalize_tags(raw_tags)

    def _extract_wikilinks(self, text: str) -> list[str]:
        """Извлечение wikilinks из текста.

        Args:
            text: Текст для поиска wikilinks

        Returns:
            Список найденных нормализованных wikilinks (без [[ и ]])
        """
        # Регулярное выражение для wikilinks: [[link]] или [[link|display]]
        # Игнорируем вложенные [[]] и обрабатываем только простые случаи
        pattern = r"\[\[([^\]]+)\]\]"
        matches = re.findall(pattern, text)
        
        # Нормализуем ссылки
        return DataNormalizer.normalize_links(matches)

    def _extract_h1_title(self, content: str) -> str:
        """Извлечение заголовка H1 из markdown.

        Args:
            content: Содержимое файла

        Returns:
            Заголовок H1 или пустая строка
        """
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return ""

    def _extract_code_blocks(self, content: str) -> list[tuple[str, str, str]]:
        """Извлечение code blocks из markdown контента.

        Args:
            content: Содержимое файла

        Returns:
            Список кортежей (language, code_content, section_context)
            где section_context - название секции, в которой находится блок
        """
        code_blocks: list[tuple[str, str, str]] = []
        lines = content.split("\n")
        
        current_section = "Introduction"
        in_code_block = False
        code_language = ""
        code_lines: list[str] = []
        
        for line in lines:
            stripped = line.strip()
            
            # Обновляем текущую секцию при встрече заголовков
            if stripped.startswith("# "):
                current_section = stripped[2:].strip()
            elif stripped.startswith("## ") and not in_code_block:
                current_section = stripped[3:].strip()
            elif stripped.startswith("### ") and not in_code_block:
                current_section = stripped[4:].strip()
            
            # Проверяем начало code block: ```language или ```
            if stripped.startswith("```"):
                if in_code_block:
                    # Конец code block
                    if code_lines:
                        code_content = "\n".join(code_lines)
                        code_blocks.append((code_language, code_content, current_section))
                    in_code_block = False
                    code_language = ""
                    code_lines = []
                else:
                    # Начало code block
                    in_code_block = True
                    # Извлекаем язык из ```language или ```language:title
                    language_part = stripped[3:].strip()
                    if language_part:
                        # Убираем возможные дополнительные параметры после :
                        code_language = language_part.split(":")[0].split()[0]
                    else:
                        code_language = ""  # Без указания языка
            elif in_code_block:
                # Содержимое code block
                code_lines.append(line)
        
        # Обрабатываем случай, если файл заканчивается незакрытым code block
        if in_code_block and code_lines:
            code_content = "\n".join(code_lines)
            code_blocks.append((code_language, code_content, current_section))
        
        return code_blocks

    def _remove_code_blocks_from_text(self, content: str) -> str:
        """Удаление code blocks из текста для обработки остального контента.

        Args:
            content: Содержимое файла

        Returns:
            Текст без code blocks
        """
        lines = content.split("\n")
        result_lines: list[str] = []
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                # Не добавляем строки с ``` в результат
                continue
            
            if not in_code_block:
                result_lines.append(line)
        
        return "\n".join(result_lines)

    def _split_into_sections(self, content: str) -> list[tuple[str, str]]:
        """Разбивка контента на секции по заголовкам H1-H3.

        Args:
            content: Содержимое файла

        Returns:
            Список кортежей (section_title, section_content)
        """
        sections: list[tuple[str, str]] = []
        current_section = "Introduction"
        current_content: list[str] = []

        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            # Проверяем заголовки H1, H2, H3
            if stripped.startswith("# "):
                # Сохраняем предыдущую секцию
                if current_content:
                    sections.append((current_section, "\n".join(current_content)))
                current_section = stripped[2:].strip()
                current_content = []
            elif stripped.startswith("## ") and not current_content:
                # H2 как начало секции, если секция пустая
                current_section = stripped[3:].strip()
            elif stripped.startswith("### ") and not current_content:
                # H3 как начало секции, если секция пустая
                current_section = stripped[4:].strip()
            else:
                current_content.append(line)

        # Добавляем последнюю секцию
        if current_content:
            sections.append((current_section, "\n".join(current_content)))

        # Если секций нет, возвращаем весь контент как одну секцию
        if not sections:
            sections.append(("Introduction", content))

        return sections

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Разбивка текста на чанки с overlap.

        Args:
            text: Текст для разбивки
            chunk_size: Максимальный размер чанка
            overlap: Размер overlap между чанками

        Returns:
            Список чанков
        """
        if len(text) <= chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Если не последний чанк, пытаемся разбить по границе слова/предложения
            if end < len(text):
                # Ищем последний перенос строки или пробел
                last_newline = chunk.rfind("\n")
                last_space = chunk.rfind(" ")

                # Выбираем лучшую границу
                if last_newline > chunk_size * 0.7:
                    chunk = text[start : start + last_newline + 1]
                    start += last_newline + 1 - overlap
                elif last_space > chunk_size * 0.7:
                    chunk = text[start : start + last_space + 1]
                    start += last_space + 1 - overlap
                else:
                    start = end - overlap
            else:
                start = len(text)

            chunks.append(chunk.strip())

        return chunks

    async def _check_file_size(self, file_path: Path) -> tuple[bool, int]:
        """Проверка размера файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Кортеж (разрешен ли файл, размер в байтах)
        """
        loop = asyncio.get_event_loop()
        try:
            stat = await loop.run_in_executor(None, file_path.stat)
            file_size = stat.st_size

            if file_size > settings.max_file_size:
                logger.warning(
                    "File too large, skipping",
                    vault_name=self.vault_name,
                    file_path=str(file_path),
                    file_size_mb=round(file_size / 1024 / 1024, 1),
                    max_size_mb=round(settings.max_file_size / 1024 / 1024, 1),
                )
                return False, file_size

            return True, file_size
        except Exception as e:
            logger.error(
                "Error checking file size",
                vault_name=self.vault_name,
                file_path=str(file_path),
                error=str(e),
            )
            return False, 0

    async def scan_file(self, file_path: Path) -> list[DocumentChunk]:
        """Сканирование одного файла (markdown, PDF, DOCX).

        Args:
            file_path: Путь к файлу

        Returns:
            Список чанков документа
        """
        # Проверяем размер файла
        allowed, file_size = await self._check_file_size(file_path)
        if not allowed:
            return []

        suffix = file_path.suffix.lower()

        if suffix == ".md":
            # Используем потоковую обработку для больших файлов
            use_streaming = file_size > settings.max_file_size_streaming
            return await self._scan_markdown_file(file_path, use_streaming=use_streaming)
        elif suffix == ".pdf":
            return await self._scan_pdf_file(file_path)
        elif suffix == ".docx":
            return await self._scan_docx_file(file_path)
        else:
            logger.warning(
                "Unsupported file format",
                vault_name=self.vault_name,
                file_path=str(file_path),
                file_extension=suffix,
            )
            return []

    def _read_file_streaming(self, file_path: Path) -> tuple[str, str]:
        """Потоковое чтение markdown файла с разделением на frontmatter и body.

        Args:
            file_path: Путь к файлу

        Returns:
            Кортеж (frontmatter_text, body_text)
        """
        frontmatter_lines: list[str] = []
        body_lines: list[str] = []
        in_frontmatter = False
        frontmatter_started = False

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Проверяем разделитель frontmatter: "---" в начале строки
                # Обрабатываем разные варианты окончаний строк: \n, \r\n, или без перевода строки в конце файла
                stripped_line = line.rstrip('\r\n')
                if stripped_line == "---":
                    if not frontmatter_started:
                        frontmatter_started = True
                        in_frontmatter = True
                    elif in_frontmatter:
                        in_frontmatter = False
                    continue

                if in_frontmatter:
                    frontmatter_lines.append(line)
                else:
                    body_lines.append(line)

        frontmatter_text = "".join(frontmatter_lines)
        body_text = "".join(body_lines)
        return frontmatter_text, body_text

    async def _scan_markdown_file(self, file_path: Path, use_streaming: bool = False) -> list[DocumentChunk]:
        """Сканирование markdown файла.

        Args:
            file_path: Путь к файлу
            use_streaming: Использовать потоковое чтение для больших файлов

        Returns:
            Список чанков документа
        """
        # Сохраняем путь к текущему файлу для логирования
        self._current_file_path = str(file_path)
        
        # Выполняем I/O в executor, чтобы не блокировать event loop
        loop = asyncio.get_event_loop()

        try:
            if use_streaming:
                logger.info(
                    "Using streaming for large file",
                    vault_name=self.vault_name,
                    file_path=str(file_path),
                )
                frontmatter_text, body = await loop.run_in_executor(
                    None, self._read_file_streaming, file_path
                )
                # Парсим frontmatter из отдельного текста
                frontmatter = self._parse_frontmatter_from_text(frontmatter_text, body)
            else:
                content = await loop.run_in_executor(None, file_path.read_text, "utf-8")
                # Парсим frontmatter
                frontmatter, body = self._parse_frontmatter(content)
        except Exception as e:
            logger.error(
                "Failed to read file",
                vault_name=self.vault_name,
                file_path=str(file_path),
                error=str(e),
                exc_info=True,
            )
            raise IndexingError(f"Failed to read file {file_path}: {e}") from e
        finally:
            # Очищаем путь к текущему файлу
            self._current_file_path = None

        # Получаем метаданные файла
        file_modified_at, file_created_at = await self._get_file_metadata(file_path)

        # Обрабатываем контент markdown файла
        processed_data = self._process_markdown_content(file_path, frontmatter, body, file_created_at, file_modified_at)
        
        # Извлекаем значения из обработанных данных
        title = processed_data["title"]
        frontmatter_tags_normalized = processed_data["frontmatter_tags"]
        inline_tags_normalized = processed_data["inline_tags"]
        all_tags = processed_data["all_tags"]
        all_wikilinks = processed_data["wikilinks"]
        code_blocks = processed_data["code_blocks"]
        sections = processed_data["sections"]
        created_at = processed_data["created_at"]

        # Создаем чанки из обычного контента
        chunks = self._create_chunks_from_content(
            file_path=file_path,
            title=title,
            sections=sections,
            tags=all_tags,
            frontmatter_tags=frontmatter_tags_normalized,
            inline_tags=inline_tags_normalized,
            links=all_wikilinks,
            created_at=created_at,
            modified_at=processed_data["modified_at"],
            metadata=frontmatter.metadata,
        )
        
        # Добавляем отдельные чанки для code blocks
        # Используем количество обычных чанков как смещение для индексов
        code_chunks = self._create_code_block_chunks(
            file_path=file_path,
            title=title,
            code_blocks=code_blocks,
            tags=all_tags,
            frontmatter_tags=frontmatter_tags_normalized,
            inline_tags=inline_tags_normalized,
            links=all_wikilinks,
            created_at=created_at,
            modified_at=processed_data["modified_at"],
            base_metadata=frontmatter.metadata,
            start_index=len(chunks),
        )
        
        # Объединяем обычные чанки и code block чанки
        chunks.extend(code_chunks)
        
        return chunks

    async def _get_file_metadata(self, file_path: Path) -> tuple[datetime, datetime]:
        """Получить метаданные файла (даты модификации и создания).

        Args:
            file_path: Путь к файлу

        Returns:
            Кортеж (modified_at, created_at)
        """
        loop = asyncio.get_event_loop()
        stat = await loop.run_in_executor(None, file_path.stat)
        file_modified_at = datetime.fromtimestamp(stat.st_mtime)
        file_created_at = datetime.fromtimestamp(stat.st_ctime)
        return file_modified_at, file_created_at

    def _process_markdown_content(
        self,
        file_path: Path,
        frontmatter: FrontmatterData,
        body: str,
        file_created_at: datetime,
        file_modified_at: datetime,
    ) -> ProcessedMarkdownContent:
        """Обработать контент markdown файла и извлечь все необходимые данные.

        Args:
            file_path: Путь к файлу
            frontmatter: Распарсенные данные frontmatter
            body: Тело документа
            file_created_at: Дата создания файла (из filesystem)
            file_modified_at: Дата модификации файла (из filesystem)

        Returns:
            ProcessedMarkdownContent с обработанными данными
        """
        # Извлекаем title (из frontmatter или H1)
        title = frontmatter.title
        if not title:
            title = self._extract_h1_title(body)
        if not title:
            title = file_path.stem

        # Извлекаем inline теги
        inline_tags = self._extract_inline_tags(body)

        # Нормализуем теги раздельно
        frontmatter_tags_normalized = DataNormalizer.normalize_tags(frontmatter.tags)
        inline_tags_normalized = DataNormalizer.normalize_tags(inline_tags)
        
        # Объединяем теги для обратной совместимости (поле tags)
        all_tags = DataNormalizer.normalize_tags(frontmatter_tags_normalized + inline_tags_normalized)

        # Извлекаем wikilinks
        all_wikilinks = self._extract_wikilinks(body)

        # Извлекаем code blocks отдельно
        code_blocks = self._extract_code_blocks(body)
        
        # Удаляем code blocks из body для обработки остального текста
        body_without_code = self._remove_code_blocks_from_text(body)

        # Разбиваем на секции (без code blocks)
        sections = self._split_into_sections(body_without_code)

        # Используем created из frontmatter или ctime как fallback
        created_at = frontmatter.created_at or file_created_at
        modified_at = frontmatter.modified_at or file_modified_at

        return {
            "title": title,
            "frontmatter_tags": frontmatter_tags_normalized,
            "inline_tags": inline_tags_normalized,
            "all_tags": all_tags,
            "wikilinks": all_wikilinks,
            "code_blocks": code_blocks,
            "sections": sections,
            "created_at": created_at,
            "modified_at": modified_at,
        }

    async def _scan_binary_file(self, file_path: Path, file_type: str) -> list[DocumentChunk]:
        """Сканирование бинарного файла (PDF, DOCX и т.д.).

        Args:
            file_path: Путь к файлу
            file_type: Тип файла ("pdf", "docx" и т.д.)

        Returns:
            Список чанков документа
        """
        loop = asyncio.get_event_loop()

        # Получаем метаданные файла
        stat = await loop.run_in_executor(None, file_path.stat)
        file_modified_at = datetime.fromtimestamp(stat.st_mtime)

        # Извлекаем текст из файла
        try:
            content = await loop.run_in_executor(None, extract_text_from_file, file_path)
            if not content:
                logger.warning(
                    "Failed to extract text from binary file",
                    vault_name=self.vault_name,
                    file_path=str(file_path),
                    file_type=file_type.upper(),
                )
                return []
        except Exception as e:
            logger.error(
                "Error extracting text from binary file",
                vault_name=self.vault_name,
                file_path=str(file_path),
                file_type=file_type.upper(),
                error=str(e),
            )
            return []

        # Используем имя файла как title
        title = file_path.stem

        # Для бинарных файлов нет frontmatter, тегов и wikilinks
        # Разбиваем весь текст на секции по параграфам
        assert content is not None
        sections = [("Content", content)]

        return self._create_chunks_from_content(
            file_path=file_path,
            title=title,
            sections=sections,
            tags=[],
            frontmatter_tags=[],
            inline_tags=[],
            links=[],
            created_at=None,
            modified_at=file_modified_at,
            metadata={"file_type": file_type},
        )

    async def _scan_pdf_file(self, file_path: Path) -> list[DocumentChunk]:
        """Сканирование PDF файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Список чанков документа
        """
        return await self._scan_binary_file(file_path, "pdf")

    async def _scan_docx_file(self, file_path: Path) -> list[DocumentChunk]:
        """Сканирование DOCX файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Список чанков документа
        """
        return await self._scan_binary_file(file_path, "docx")

    def _create_chunks_from_content(
        self,
        file_path: Path,
        title: str,
        sections: list[tuple[str, str]],
        tags: list[str],
        frontmatter_tags: list[str],
        inline_tags: list[str],
        links: list[str],
        created_at: datetime | None,
        modified_at: datetime,
        metadata: dict[str, Any],
    ) -> list[DocumentChunk]:
        """Создание чанков из контента.

        Args:
            file_path: Путь к файлу
            title: Заголовок документа
            sections: Список кортежей (section_title, section_content)
            tags: Список тегов
            links: Список ссылок
            created_at: Дата создания
            modified_at: Дата модификации
            metadata: Дополнительные метаданные

        Returns:
            Список чанков документа
        """
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for section_title, section_content in sections:
            # Разбиваем секцию на чанки
            section_chunks = self._chunk_text(
                section_content,
                settings.chunk_size,
                settings.chunk_overlap,
            )

            for chunk_text in section_chunks:
                if not chunk_text.strip():
                    continue

                # Нормализуем пути для корректного relative_to на macOS
                file_path_resolved = file_path.resolve()
                vault_path_resolved = self.vault_path.resolve()

                try:
                    relative_path = file_path_resolved.relative_to(vault_path_resolved)
                except ValueError:
                    # Fallback: используем имя файла если пути не связаны
                    relative_path = Path(file_path.name)

                chunk_id = f"{self.vault_name}::{relative_path}::{chunk_index}"
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    vault_name=self.vault_name,
                    file_path=str(relative_path),
                    title=title,
                    section=section_title,
                    content=chunk_text,
                    tags=tags,  # Объединенные теги для обратной совместимости
                    frontmatter_tags=frontmatter_tags,
                    inline_tags=inline_tags,
                    links=links,
                    created_at=created_at,
                    modified_at=modified_at,
                    metadata=metadata,
                    # УДАЛЕНЫ денормализованные поля: author, status, priority, project (v4)
                )
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _create_code_block_chunks(
        self,
        file_path: Path,
        title: str,
        code_blocks: list[tuple[str, str, str]],
        tags: list[str],
        frontmatter_tags: list[str],
        inline_tags: list[str],
        links: list[str],
        created_at: datetime | None,
        modified_at: datetime,
        base_metadata: dict[str, Any],
        start_index: int = 0,
    ) -> list[DocumentChunk]:
        """Создание отдельных чанков для code blocks.

        Args:
            file_path: Путь к файлу
            title: Заголовок документа
            code_blocks: Список кортежей (language, code_content, section_context)
            tags: Список тегов (объединенные для обратной совместимости)
            frontmatter_tags: Теги из frontmatter
            inline_tags: Inline теги из текста
            links: Список ссылок
            created_at: Дата создания
            modified_at: Дата модификации
            base_metadata: Базовые метаданные из frontmatter
            start_index: Начальный индекс для чанков (после обычных чанков)

        Returns:
            Список чанков для code blocks
        """
        chunks: list[DocumentChunk] = []
        
        chunk_index = start_index
        
        # Нормализуем пути для корректного relative_to на macOS
        file_path_resolved = file_path.resolve()
        vault_path_resolved = self.vault_path.resolve()

        try:
            relative_path = file_path_resolved.relative_to(vault_path_resolved)
        except ValueError:
            # Fallback: используем имя файла если пути не связаны
            relative_path = Path(file_path.name)

        for language, code_content, section_context in code_blocks:
            if not code_content.strip():
                continue

            # Создаем метаданные для code block
            code_metadata = base_metadata.copy()
            code_metadata["content_type"] = "code_block"
            if language:
                code_metadata["code_language"] = language
            else:
                code_metadata["code_language"] = "plain"
            
            # Формируем section title с указанием типа контента
            section_title = f"{section_context} [Code: {language or 'plain'}]"

            # Для code blocks не разбиваем на чанки, если они не слишком большие
            # Если код очень длинный, разбиваем его
            if len(code_content) > settings.chunk_size:
                # Разбиваем длинный код на чанки
                code_chunks = self._chunk_text(
                    code_content,
                    settings.chunk_size,
                    settings.chunk_overlap,
                )
                
                for code_chunk in code_chunks:
                    if not code_chunk.strip():
                        continue
                    
                    chunk_id = f"{self.vault_name}::{relative_path}::{chunk_index}"
                    
                    chunk = DocumentChunk(
                        id=chunk_id,
                        vault_name=self.vault_name,
                        file_path=str(relative_path),
                        title=title,
                        section=section_title,
                        content=code_chunk,
                        tags=tags,  # Объединенные теги для обратной совместимости
                        frontmatter_tags=frontmatter_tags,
                        inline_tags=inline_tags,
                        links=links,
                        created_at=created_at,
                        modified_at=modified_at,
                        metadata=code_metadata,
                        # УДАЛЕНЫ денормализованные поля: author, status, priority, project (v4)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            else:
                # Короткий код - один чанк
                chunk_id = f"{self.vault_name}::{relative_path}::{chunk_index}"
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    vault_name=self.vault_name,
                    file_path=str(relative_path),
                    title=title,
                    section=section_title,
                    content=code_content,
                    tags=tags,  # Объединенные теги для обратной совместимости
                    frontmatter_tags=frontmatter_tags,
                    inline_tags=inline_tags,
                    links=links,
                    created_at=created_at,
                    modified_at=modified_at,
                    metadata=code_metadata,
                    # УДАЛЕНЫ денормализованные поля: author, status, priority, project (v4)
                )
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _get_files_to_scan(
        self,
        only_changed: bool = False,
        indexed_files: dict[str, datetime] | None = None,
    ) -> list[Path]:
        """Получение списка файлов для индексации (синхронный метод).
        
        Args:
            only_changed: Если True, сканировать только изменённые файлы
            indexed_files: Словарь {file_path: modified_at} для сравнения
            
        Returns:
            Список путей к файлам для индексации
        """
        # Находим все поддерживаемые файлы
        supported_extensions = {".md", ".pdf", ".docx"}
        all_files: list[Path] = []
        for ext in supported_extensions:
            all_files.extend(self.vault_path.rglob(f"*{ext}"))
        
        # Фильтруем файлы по паттернам игнорирования
        filtered_files: list[Path] = []
        for file_path in all_files:
            try:
                relative_path = file_path.resolve().relative_to(self.vault_path.resolve())
                relative_path_str = str(relative_path).replace("\\", "/")
            except ValueError:
                relative_path_str = file_path.name
            
            if not self.ignore_matcher.should_ignore(relative_path_str):
                filtered_files.append(file_path)
        
        all_files = filtered_files
        
        # Фильтруем файлы если нужно инкрементальное индексирование
        if only_changed and indexed_files:
            files_to_scan: list[Path] = []
            
            for file_path in all_files:
                try:
                    relative_path = file_path.resolve().relative_to(self.vault_path.resolve())
                    relative_path_str = str(relative_path)
                except ValueError:
                    relative_path_str = file_path.name
                
                should_index = True
                if relative_path_str in indexed_files:
                    stat = file_path.stat()
                    file_mtime = datetime.fromtimestamp(stat.st_mtime)
                    indexed_mtime = indexed_files[relative_path_str]
                    should_index = file_mtime > indexed_mtime
                
                if should_index:
                    files_to_scan.append(file_path)
            
            return files_to_scan
        
        return all_files

    async def scan_all(
        self, 
        only_changed: bool = False, 
        indexed_files: dict[str, datetime] | None = None,
        max_workers: int | None = None,
        progress_callback: Callable[[int, int, float], None] | None = None,
        batch_processor: BatchProcessor[Path, list[DocumentChunk]] | None = None,
    ) -> list[DocumentChunk]:
        """Сканирование всех поддерживаемых файлов в vault'е (markdown, PDF, DOCX).

        Args:
            only_changed: Если True, сканировать только изменённые файлы
            indexed_files: Словарь {file_path: modified_at} для сравнения (если only_changed=True)
            max_workers: Максимальное количество параллельных файлов (по умолчанию из settings)
            progress_callback: Callback для отслеживания прогресса (current, total, percentage)
            batch_processor: BatchProcessor для обработки файлов (опционально, создаётся автоматически)

        Returns:
            Список всех чанков
        """
        from obsidian_kb.config import settings
        
        if max_workers is None:
            max_workers = settings.max_workers
        
        all_chunks: list[DocumentChunk] = []

        # Получаем список файлов для индексации
        all_files = self._get_files_to_scan(only_changed=only_changed, indexed_files=indexed_files)
        
        if all_files:
            md_count = sum(1 for f in all_files if f.suffix.lower() == ".md")
            pdf_count = sum(1 for f in all_files if f.suffix.lower() == ".pdf")
            docx_count = sum(1 for f in all_files if f.suffix.lower() == ".docx")
            logger.info(
                "Found files to index",
                vault_name=self.vault_name,
                total_files=len(all_files),
                md_count=md_count,
                pdf_count=pdf_count,
                docx_count=docx_count,
                only_changed=only_changed,
            )

        if not all_files:
            logger.info("No files to index", vault_name=self.vault_name)
            return []

        # Используем BatchProcessor для обработки файлов с отслеживанием прогресса
        if batch_processor is None:
            batch_processor = BatchProcessor(batch_size=32, max_workers=max_workers)

        # Callback для обработки ошибок
        def error_callback(file_path: Path, exception: Exception) -> None:
            logger.error(
                "Error scanning file",
                vault_name=self.vault_name,
                file_path=str(file_path),
                error=str(exception),
            )

        # Обрабатываем файлы через BatchProcessor
        results = await batch_processor.process(
            items=all_files,
            processor=self.scan_file,  # scan_file уже async метод
            progress_callback=progress_callback,
            error_callback=error_callback,
        )

        # Собираем все чанки из результатов
        for chunks in results:
            if chunks:  # Пропускаем None результаты (ошибки)
                all_chunks.extend(chunks)

        logger.info(
            "Indexing completed",
            vault_name=self.vault_name,
            total_chunks=len(all_chunks),
            total_files=len(all_files),
        )
        return all_chunks

    def start_watcher(self, on_change: Callable[[Path], None]) -> None:
        """Запуск watchdog observer для отслеживания изменений.

        Args:
            on_change: Callback функция, вызываемая при изменении файла
        """
        if self.observer is not None:
            logger.warning("Watcher already started", vault_name=self.vault_name)
            return

        vault_name = self.vault_name  # Capture for inner class

        class VaultEventHandler(FileSystemEventHandler):
            def __init__(self, indexer: VaultIndexer, callback: Callable[[Path], None]) -> None:
                self.indexer = indexer
                self.callback = callback
                self.supported_extensions = {".md", ".pdf", ".docx"}

            def _is_supported_file(self, path: str) -> bool:
                """Проверка, поддерживается ли формат файла."""
                return any(path.endswith(ext) for ext in self.supported_extensions)

            def on_modified(self, event: FileSystemEvent) -> None:
                if event.is_directory:
                    return
                if not self._is_supported_file(event.src_path):
                    return
                try:
                    path = Path(event.src_path)
                    if path.is_file():
                        self.callback(path)
                except Exception as e:
                    logger.error(
                        "Error in file watcher on_modified",
                        vault_name=vault_name,
                        file_path=event.src_path,
                        error=str(e),
                    )

            def on_created(self, event: FileSystemEvent) -> None:
                self.on_modified(event)

            def on_deleted(self, event: FileSystemEvent) -> None:
                if event.is_directory:
                    return
                if not self._is_supported_file(event.src_path):
                    return
                try:
                    path = Path(event.src_path)
                    self.callback(path)
                except Exception as e:
                    logger.error(
                        "Error in file watcher on_deleted",
                        vault_name=vault_name,
                        file_path=event.src_path,
                        error=str(e),
                    )

        event_handler = VaultEventHandler(self, on_change)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.vault_path), recursive=True)
        self.observer.start()
        logger.info(
            "Started file watcher",
            vault_name=self.vault_name,
            vault_path=str(self.vault_path),
        )

    def stop_watcher(self) -> None:
        """Остановка watchdog observer."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Stopped file watcher", vault_name=self.vault_name)

