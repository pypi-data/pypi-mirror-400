"""Гибридный сервис chunking для markdown-aware разбиения документов."""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from obsidian_kb.config.schema import IndexingConfig

if TYPE_CHECKING:
    from obsidian_kb.providers.interfaces import IChatCompletionProvider

logger = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    """Стратегия разбиения документов на чанки."""
    
    AUTO = "auto"
    HEADERS = "headers"
    SEMANTIC = "semantic"
    FIXED = "fixed"


@dataclass
class ChunkInfo:
    """Информация о чанке документа."""
    
    text: str
    headers: list[str]  # Иерархия заголовков (H1, H2, H3...)
    start_char: int  # Начальная позиция в исходном тексте
    end_char: int  # Конечная позиция в исходном тексте
    token_count: int  # Примерное количество токенов
    chunk_type: str  # Тип чанка: header_section | paragraph | code_block | list


class ChunkingService:
    """Гибридный сервис для chunking документов.
    
    Стратегия AUTO:
    1. Markdown header split как base layer
    2. Recursive split для секций > max_chunk_size
    3. Semantic refinement для complex документов (если complexity > threshold)
    """
    
    def __init__(
        self,
        chat_provider: "IChatCompletionProvider | None" = None,
        config: IndexingConfig | None = None,
    ) -> None:
        """Инициализация сервиса chunking.
        
        Args:
            chat_provider: Провайдер для семантического уточнения (опционально)
            config: Конфигурация индексации
        """
        self._chat = chat_provider
        self._config = config or IndexingConfig()
    
    async def chunk_document(
        self,
        content: str,
        strategy: ChunkingStrategy = ChunkingStrategy.AUTO,
    ) -> list[ChunkInfo]:
        """Разбиение документа на чанки.
        
        Args:
            content: Содержимое документа
            strategy: Стратегия разбиения
            
        Returns:
            Список ChunkInfo с информацией о чанках
        """
        if not content.strip():
            return []
        
        if strategy == ChunkingStrategy.AUTO:
            return await self._chunk_auto(content)
        elif strategy == ChunkingStrategy.HEADERS:
            return self._markdown_header_split(content)
        elif strategy == ChunkingStrategy.SEMANTIC:
            # Для semantic нужен chat_provider
            if not self._chat:
                logger.warning("Semantic strategy requires chat_provider, falling back to headers")
                return self._markdown_header_split(content)
            return await self._semantic_refine(
                self._markdown_header_split(content),
                content,
            )
        elif strategy == ChunkingStrategy.FIXED:
            return self._fixed_size_split(content)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    async def _chunk_auto(self, content: str) -> list[ChunkInfo]:
        """Автоматическая стратегия разбиения.
        
        1. Markdown header split как base layer
        2. Recursive split для секций > max_chunk_size
        3. Semantic refinement для complex документов
        """
        # Шаг 1: Разбиение по заголовкам
        chunks = self._markdown_header_split(content)
        
        # Шаг 2: Рекурсивное разбиение больших чанков
        refined_chunks = []
        for chunk in chunks:
            if chunk.token_count > self._config.chunk_size:
                # Разбиваем большие чанки рекурсивно
                split_chunks = self._recursive_split(
                    chunk,
                    self._config.chunk_size,
                )
                refined_chunks.extend(split_chunks)
            else:
                refined_chunks.append(chunk)
        
        # Шаг 3: Семантическое уточнение для сложных документов
        complexity = self._analyze_complexity(content)
        if complexity > self._config.complexity_threshold and self._chat:
            try:
                refined_chunks = await self._semantic_refine(
                    refined_chunks,
                    content,
                )
            except Exception as e:
                logger.warning(f"Semantic refinement failed: {e}, using header-based chunks")
        
        return refined_chunks
    
    def _markdown_header_split(self, content: str) -> list[ChunkInfo]:
        """Разбиение по Markdown заголовкам.
        
        Создаёт чанки для каждой секции, определённой заголовком (H1-H6).
        """
        chunks = []
        
        # Паттерн для поиска заголовков: # Заголовок
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        # Находим все заголовки с их позициями
        headers = []
        for match in header_pattern.finditer(content):
            level = len(match.group(1))  # Количество #
            text = match.group(2).strip()
            pos = match.start()
            headers.append((level, text, pos))
        
        # Если заголовков нет, создаём один чанк из всего документа
        if not headers:
            token_count = self._estimate_tokens(content)
            return [ChunkInfo(
                text=content,
                headers=[],
                start_char=0,
                end_char=len(content),
                token_count=token_count,
                chunk_type="paragraph",
            )]
        
        # Создаём чанки для каждой секции
        for i, (level, header_text, start_pos) in enumerate(headers):
            # Определяем конец секции (начало следующего заголовка того же или более высокого уровня)
            if i + 1 < len(headers):
                end_pos = headers[i + 1][2]
            else:
                end_pos = len(content)
            
            # Извлекаем текст секции
            section_text = content[start_pos:end_pos].strip()
            
            # Собираем иерархию заголовков для этой секции
            section_headers = []
            for prev_level, prev_text, _ in headers[:i + 1]:
                if prev_level <= level:
                    section_headers.append(prev_text)
            
            # Определяем тип чанка
            chunk_type = self._detect_chunk_type(section_text)
            
            token_count = self._estimate_tokens(section_text)
            
            chunks.append(ChunkInfo(
                text=section_text,
                headers=section_headers,
                start_char=start_pos,
                end_char=end_pos,
                token_count=token_count,
                chunk_type=chunk_type,
            ))
        
        return chunks
    
    def _recursive_split(
        self,
        chunk: ChunkInfo,
        max_tokens: int,
    ) -> list[ChunkInfo]:
        """Рекурсивное разбиение больших чанков.
        
        Разбивает чанк на более мелкие части, сохраняя семантическую целостность.
        """
        if chunk.token_count <= max_tokens:
            return [chunk]
        
        # Пробуем разбить по параграфам
        paragraphs = re.split(r'\n\n+', chunk.text)
        
        if len(paragraphs) > 1:
            # Разбиваем по параграфам
            result = []
            current_text = ""
            current_start = chunk.start_char
            
            for para in paragraphs:
                para_tokens = self._estimate_tokens(para)
                
                if para_tokens > max_tokens:
                    # Параграф сам слишком большой, разбиваем дальше
                    sub_chunks = self._split_large_text(
                        para,
                        max_tokens,
                        current_start,
                        chunk.headers,
                    )
                    result.extend(sub_chunks)
                    if sub_chunks:
                        current_start = sub_chunks[-1].end_char
                    current_text = ""
                elif self._estimate_tokens(current_text + "\n\n" + para) > max_tokens:
                    # Текущий накопленный текст + параграф превышает лимит
                    if current_text:
                        result.append(ChunkInfo(
                            text=current_text.strip(),
                            headers=chunk.headers,
                            start_char=current_start,
                            end_char=current_start + len(current_text),
                            token_count=self._estimate_tokens(current_text),
                            chunk_type=chunk.chunk_type,
                        ))
                    current_text = para
                    current_start = current_start + len(current_text) - len(para)
                else:
                    # Добавляем параграф к текущему тексту
                    if current_text:
                        current_text += "\n\n" + para
                    else:
                        current_text = para
                        current_start = chunk.start_char + chunk.text.find(para)
            
            # Добавляем последний накопленный текст
            if current_text:
                result.append(ChunkInfo(
                    text=current_text.strip(),
                    headers=chunk.headers,
                    start_char=current_start,
                    end_char=chunk.end_char,
                    token_count=self._estimate_tokens(current_text),
                    chunk_type=chunk.chunk_type,
                ))
            
            return result if result else [chunk]
        
        # Если параграфов нет или они не помогают, разбиваем по предложениям
        return self._split_large_text(
            chunk.text,
            max_tokens,
            chunk.start_char,
            chunk.headers,
        )
    
    def _split_large_text(
        self,
        text: str,
        max_tokens: int,
        start_char: int,
        headers: list[str],
    ) -> list[ChunkInfo]:
        """Разбиение большого текста на чанки фиксированного размера.
        
        Используется как fallback, когда другие методы не работают.
        """
        chunks = []
        overlap = self._config.chunk_overlap
        
        # Разбиваем по предложениям
        sentences = re.split(r'([.!?]\s+)', text)
        
        current_chunk = ""
        current_start = start_char
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
            
            if self._estimate_tokens(current_chunk + sentence) > max_tokens:
                if current_chunk:
                    chunks.append(ChunkInfo(
                        text=current_chunk.strip(),
                        headers=headers,
                        start_char=current_start,
                        end_char=current_start + len(current_chunk),
                        token_count=self._estimate_tokens(current_chunk),
                        chunk_type="paragraph",
                    ))
                
                # Начинаем новый чанк с overlap
                if overlap > 0 and chunks:
                    # Берём последние N символов предыдущего чанка для overlap
                    prev_chunk = chunks[-1].text
                    overlap_text = prev_chunk[-overlap * 3:] if len(prev_chunk) > overlap * 3 else prev_chunk
                    current_chunk = overlap_text + sentence
                    current_start = chunks[-1].end_char - len(overlap_text)
                else:
                    current_chunk = sentence
                    current_start = current_start + len(current_chunk) - len(sentence)
            else:
                current_chunk += sentence
        
        # Добавляем последний чанк
        if current_chunk:
            chunks.append(ChunkInfo(
                text=current_chunk.strip(),
                headers=headers,
                start_char=current_start,
                end_char=start_char + len(text),
                token_count=self._estimate_tokens(current_chunk),
                chunk_type="paragraph",
            ))
        
        return chunks if chunks else [ChunkInfo(
            text=text,
            headers=headers,
            start_char=start_char,
            end_char=start_char + len(text),
            token_count=self._estimate_tokens(text),
            chunk_type="paragraph",
        )]
    
    def _fixed_size_split(self, content: str) -> list[ChunkInfo]:
        """Разбиение на чанки фиксированного размера (без учёта структуры)."""
        chunks = []
        chunk_size = self._config.chunk_size
        overlap = self._config.chunk_overlap
        
        # Простое разбиение по символам с учётом токенов
        current_pos = 0
        while current_pos < len(content):
            # Оцениваем размер чанка в символах (примерно)
            # Для русского текста: 1 токен ≈ 2.5 символа
            chunk_chars = int(chunk_size * 2.5)
            end_pos = min(current_pos + chunk_chars, len(content))
            
            chunk_text = content[current_pos:end_pos]
            
            # Добавляем overlap с предыдущим чанком
            if overlap > 0 and chunks:
                overlap_chars = int(overlap * 2.5)
                overlap_text = chunks[-1].text[-overlap_chars:]
                chunk_text = overlap_text + chunk_text
            
            chunks.append(ChunkInfo(
                text=chunk_text.strip(),
                headers=[],
                start_char=current_pos,
                end_char=end_pos,
                token_count=self._estimate_tokens(chunk_text),
                chunk_type="paragraph",
            ))
            
            current_pos = end_pos - (int(overlap * 2.5) if overlap > 0 else 0)
        
        return chunks
    
    async def _semantic_refine(
        self,
        chunks: list[ChunkInfo],
        document_context: str,
    ) -> list[ChunkInfo]:
        """Семантическое уточнение границ чанков через LLM.
        
        Использует LLM для улучшения границ чанков с учётом семантики.
        """
        if not self._chat:
            return chunks
        
        # Для простоты пока возвращаем исходные чанки
        # В будущем можно добавить LLM-запрос для оптимизации границ
        logger.debug("Semantic refinement not fully implemented, using header-based chunks")
        return chunks
    
    def _analyze_complexity(self, content: str) -> float:
        """Оценка сложности документа (0.0 - 1.0).
        
        Факторы:
        - Количество секций
        - Вариативность размеров секций
        - Наличие code blocks
        - Глубина вложенности
        """
        # Подсчитываем заголовки
        header_pattern = re.compile(r'^(#{1,6})\s+', re.MULTILINE)
        headers = header_pattern.findall(content)
        
        # Подсчитываем code blocks
        code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
        code_blocks = len(code_block_pattern.findall(content))
        
        # Подсчитываем списки
        list_pattern = re.compile(r'^[\s]*[-*+]\s+', re.MULTILINE)
        lists = len(list_pattern.findall(content))
        
        # Оцениваем сложность
        complexity = 0.0
        
        # Фактор 1: Количество секций (нормализуем до 0-0.3)
        section_factor = min(0.3, len(headers) / 20.0)
        complexity += section_factor
        
        # Фактор 2: Code blocks (нормализуем до 0-0.2)
        code_factor = min(0.2, code_blocks / 10.0)
        complexity += code_factor
        
        # Фактор 3: Глубина вложенности заголовков (нормализуем до 0-0.2)
        if headers:
            max_depth = max(len(h) for h in headers)
            depth_factor = min(0.2, (max_depth - 1) / 5.0)
            complexity += depth_factor
        
        # Фактор 4: Вариативность размеров (нормализуем до 0-0.3)
        # Разбиваем на секции и анализируем размеры
        sections = re.split(r'^(#{1,6})\s+', content, flags=re.MULTILINE)
        if len(sections) > 1:
            section_sizes = [len(s) for s in sections[1::2]]  # Берём только тексты секций
            if section_sizes:
                avg_size = sum(section_sizes) / len(section_sizes)
                variance = sum((s - avg_size) ** 2 for s in section_sizes) / len(section_sizes)
                variance_factor = min(0.3, variance / (avg_size ** 2) if avg_size > 0 else 0)
                complexity += variance_factor
        
        return min(1.0, complexity)
    
    def _detect_chunk_type(self, text: str) -> str:
        """Определение типа чанка."""
        if re.search(r'```[\s\S]*?```', text):
            return "code_block"
        elif re.search(r'^[\s]*[-*+]\s+', text, re.MULTILINE):
            return "list"
        elif re.search(r'^(#{1,6})\s+', text, re.MULTILINE):
            return "header_section"
        else:
            return "paragraph"
    
    def _estimate_tokens(self, text: str) -> int:
        """Оценка количества токенов в тексте.
        
        Использует приблизительную формулу:
        - Для русского текста: 1 токен ≈ 2.5 символа
        - Для английского: 1 токен ≈ 4 символа
        
        Используем среднее значение для смешанного текста.
        """
        # Простая оценка: считаем среднее между русским и английским
        # Для смешанного текста используем 3 символа на токен
        return len(text) // 3

