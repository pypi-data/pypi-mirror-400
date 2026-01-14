"""Тесты для vault_indexer.py"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from obsidian_kb.types import IndexingError
from obsidian_kb.vault_indexer import VaultIndexer

# Используем фикстуру temp_vault из conftest.py


@pytest.fixture
def sample_markdown_file(temp_vault):
    """Создание тестового markdown файла."""
    file_path = temp_vault / "test.md"
    content = """---
title: Test Document
tags: [test, example]
created: 2024-01-01T10:00:00
---

# Test Document

This is a test document with some content.

## Section 1

Some content in section 1.

## Section 2

More content here. #important-tag
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.mark.asyncio
async def test_scan_file_basic(sample_markdown_file, temp_vault):
    """Тест базового сканирования файла."""
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(sample_markdown_file)

    assert len(chunks) > 0
    assert all(chunk.vault_name == "test_vault" for chunk in chunks)
    assert all(chunk.title == "Test Document" for chunk in chunks)
    assert all("test" in chunk.tags for chunk in chunks)
    assert all("example" in chunk.tags for chunk in chunks)
    assert all("important-tag" in chunk.tags for chunk in chunks)


@pytest.mark.asyncio
async def test_scan_file_without_frontmatter(temp_vault):
    """Тест сканирования файла без frontmatter."""
    file_path = temp_vault / "no_frontmatter.md"
    content = """# My Document

Some content here.
"""
    file_path.write_text(content, encoding="utf-8")

    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)

    assert len(chunks) > 0
    assert all(chunk.title == "My Document" for chunk in chunks)


@pytest.mark.asyncio
async def test_scan_all(temp_vault):
    """Тест сканирования всех файлов в vault."""
    # Создаём несколько файлов
    for i in range(3):
        file_path = temp_vault / f"file_{i}.md"
        content = f"""---
title: File {i}
---

# File {i}

Content of file {i}.
"""
        file_path.write_text(content, encoding="utf-8")

    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_all()

    assert len(chunks) >= 3  # Минимум по одному чанку на файл


@pytest.mark.asyncio
async def test_vault_not_exists():
    """Тест ошибки при несуществующем vault."""
    with pytest.raises(Exception):  # IndexingError
        VaultIndexer(Path("/nonexistent/path"), "test_vault")


@pytest.mark.asyncio
async def test_scan_file_with_obsidian_templates(temp_vault):
    """Тест сканирования файла с шаблонами Obsidian в frontmatter."""
    file_path = temp_vault / "template_file.md"
    content = """---
title: Template Document
date: {{date:YYYY-MM-DD}}
created: {{date:YYYY-MM-DD}}
since: {{date:YYYY-MM-DD}}
tags: [test]
---
# Template Document

Content with template.
"""
    file_path.write_text(content, encoding="utf-8")

    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)

    assert len(chunks) > 0
    assert all(chunk.title == "Template Document" for chunk in chunks)
    # Проверяем, что шаблоны сохранены в metadata как строки
    # Поля date и since должны быть в metadata
    assert "{{date:YYYY-MM-DD}}" in str(chunks[0].metadata.get("date", ""))
    assert "{{date:YYYY-MM-DD}}" in str(chunks[0].metadata.get("since", ""))
    # Поле created обрабатывается отдельно и не попадает в metadata
    # но должно быть обработано без ошибок (created_at будет None, так как шаблон не парсится как дата)


@pytest.mark.asyncio
async def test_scan_file_with_complex_obsidian_templates(temp_vault):
    """Тест сканирования файла с различными шаблонами Obsidian в frontmatter."""
    file_path = temp_vault / "complex_template.md"
    content = """---
title: Complex Template
date: {{date:YYYY-MM-DD}}
card_data: {{ card_data }}
start_date: {{date:YYYY-MM-DD}}
tags: [template]
---
# Complex Template

Content.
"""
    file_path.write_text(content, encoding="utf-8")

    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)

    assert len(chunks) > 0
    assert all(chunk.title == "Complex Template" for chunk in chunks)
    # Проверяем, что все шаблоны сохранены в metadata
    assert "{{date:YYYY-MM-DD}}" in str(chunks[0].metadata.get("date", ""))
    assert "{{ card_data }}" in str(chunks[0].metadata.get("card_data", ""))
    assert "{{date:YYYY-MM-DD}}" in str(chunks[0].metadata.get("start_date", ""))


def test_watcher_start_stop(temp_vault):
    """Тест запуска и остановки watcher."""
    indexer = VaultIndexer(temp_vault, "test_vault")

    def dummy_callback(path: Path):
        pass

    indexer.start_watcher(dummy_callback)
    assert indexer.observer is not None
    assert indexer.observer.is_alive()

    indexer.stop_watcher()
    assert indexer.observer is None


@pytest.mark.asyncio
async def test_scan_all_with_max_workers(temp_vault):
    """Тест сканирования с настраиваемым max_workers."""
    # Создаём несколько файлов для параллельной обработки
    for i in range(15):
        file_path = temp_vault / f"file_{i}.md"
        content = f"""# File {i}

Content of file {i}.
"""
        file_path.write_text(content, encoding="utf-8")

    indexer = VaultIndexer(temp_vault, "test_vault")
    
    # Тест с разными значениями max_workers
    chunks1 = await indexer.scan_all(max_workers=5)
    chunks2 = await indexer.scan_all(max_workers=1)
    chunks3 = await indexer.scan_all(max_workers=20)
    
    # Все должны обработать одинаковое количество файлов
    assert len(chunks1) == len(chunks2) == len(chunks3)
    assert len(chunks1) >= 15  # Минимум по одному чанку на файл


@pytest.mark.asyncio
async def test_scan_all_with_default_max_workers(temp_vault):
    """Тест сканирования с дефолтным max_workers (из настроек)."""
    # Создаём несколько файлов
    for i in range(5):
        file_path = temp_vault / f"file_{i}.md"
        content = f"# File {i}\n\nContent."
        file_path.write_text(content, encoding="utf-8")

    indexer = VaultIndexer(temp_vault, "test_vault")
    
    # Вызываем без max_workers - должен использоваться дефолт из настроек
    chunks = await indexer.scan_all()
    
    assert len(chunks) >= 5


@pytest.mark.asyncio
@patch("obsidian_kb.vault_indexer.extract_text_from_file")
async def test_scan_pdf_file(mock_extract, temp_vault):
    """Тест сканирования PDF файла."""
    mock_extract.return_value = "PDF content with some text for indexing."
    
    file_path = temp_vault / "test.pdf"
    file_path.touch()
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    assert len(chunks) > 0
    assert all(chunk.vault_name == "test_vault" for chunk in chunks)
    assert all(chunk.title == "test" for chunk in chunks)  # Имя файла без расширения
    assert all(chunk.tags == [] for chunk in chunks)  # PDF не имеет тегов
    assert all(chunk.links == [] for chunk in chunks)  # PDF не имеет wikilinks
    assert all(chunk.metadata.get("file_type") == "pdf" for chunk in chunks)
    assert "PDF content" in chunks[0].content


@pytest.mark.asyncio
@patch("obsidian_kb.vault_indexer.extract_text_from_file")
async def test_scan_docx_file(mock_extract, temp_vault):
    """Тест сканирования DOCX файла."""
    mock_extract.return_value = "DOCX content with paragraphs and tables."
    
    file_path = temp_vault / "document.docx"
    file_path.touch()
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    assert len(chunks) > 0
    assert all(chunk.vault_name == "test_vault" for chunk in chunks)
    assert all(chunk.title == "document" for chunk in chunks)  # Имя файла без расширения
    assert all(chunk.tags == [] for chunk in chunks)  # DOCX не имеет тегов
    assert all(chunk.links == [] for chunk in chunks)  # DOCX не имеет wikilinks
    assert all(chunk.metadata.get("file_type") == "docx" for chunk in chunks)
    assert "DOCX content" in chunks[0].content


@pytest.mark.asyncio
@patch("obsidian_kb.vault_indexer.extract_text_from_file")
async def test_scan_pdf_file_empty(mock_extract, temp_vault):
    """Тест сканирования пустого PDF файла."""
    mock_extract.return_value = None
    
    file_path = temp_vault / "empty.pdf"
    file_path.touch()
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    assert len(chunks) == 0


@pytest.mark.asyncio
@patch("obsidian_kb.vault_indexer.extract_text_from_file")
async def test_scan_all_with_pdf_and_docx(mock_extract, temp_vault):
    """Тест сканирования всех файлов включая PDF и DOCX."""
    mock_extract.return_value = "Content from PDF or DOCX file."
    
    # Создаём файлы разных форматов
    (temp_vault / "file1.md").write_text("# Markdown file\n\nContent.", encoding="utf-8")
    (temp_vault / "file2.pdf").touch()
    (temp_vault / "file3.docx").touch()
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_all()
    
    # Должны быть чанки из всех трёх файлов
    assert len(chunks) >= 3
    
    # Проверяем, что есть чанки из markdown
    md_chunks = [c for c in chunks if c.file_path == "file1.md"]
    assert len(md_chunks) > 0
    
    # Проверяем, что есть чанки из PDF
    pdf_chunks = [c for c in chunks if c.file_path == "file2.pdf"]
    assert len(pdf_chunks) > 0
    assert pdf_chunks[0].metadata.get("file_type") == "pdf"
    
    # Проверяем, что есть чанки из DOCX
    docx_chunks = [c for c in chunks if c.file_path == "file3.docx"]
    assert len(docx_chunks) > 0
    assert docx_chunks[0].metadata.get("file_type") == "docx"


@pytest.mark.asyncio
async def test_scan_file_unsupported_format(temp_vault):
    """Тест сканирования неподдерживаемого формата."""
    file_path = temp_vault / "test.txt"
    file_path.write_text("Some text content", encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_scan_file_size_check(temp_vault):
    """Тест проверки размера файла."""
    from obsidian_kb.config import settings
    
    # Создаём файл, превышающий максимальный размер
    file_path = temp_vault / "large_file.md"
    # Создаём файл размером больше max_file_size
    large_content = "x" * (settings.max_file_size + 1)
    file_path.write_text(large_content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Файл должен быть пропущен из-за размера
    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_scan_file_streaming_for_large_file(temp_vault):
    """Тест потоковой обработки для большого файла."""
    from obsidian_kb.config import settings
    
    # Создаём файл, требующий потоковой обработки
    file_path = temp_vault / "medium_file.md"
    # Создаём файл размером больше max_file_size_streaming, но меньше max_file_size
    medium_size = settings.max_file_size_streaming + 1024  # Немного больше порога
    medium_content = "---\ntitle: Medium File\ntags: [test]\n---\n\n"
    medium_content += "# Medium File\n\n" + "x" * (medium_size - len(medium_content))
    file_path.write_text(medium_content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Файл должен быть обработан с использованием потокового чтения
    assert len(chunks) > 0
    assert all(chunk.title == "Medium File" for chunk in chunks)


@pytest.mark.asyncio
async def test_scan_file_streaming_frontmatter_parsing(temp_vault):
    """Тест парсинга frontmatter при потоковой обработке."""
    from obsidian_kb.config import settings
    
    file_path = temp_vault / "streaming_test.md"
    # Создаём файл с frontmatter, требующий потоковой обработки
    frontmatter = "---\ntitle: Streaming Test\ntags: [streaming, test]\ncreated: 2024-01-01\n---\n\n"
    body = "# Streaming Test\n\n" + "Content line.\n" * 1000
    content = frontmatter + body
    # Увеличиваем размер до порога потоковой обработки
    while len(content.encode("utf-8")) < settings.max_file_size_streaming:
        content += "Additional content line.\n" * 100
    
    file_path.write_text(content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Файл должен быть обработан корректно
    assert len(chunks) > 0
    assert all(chunk.title == "Streaming Test" for chunk in chunks)
    assert all("streaming" in chunk.tags for chunk in chunks)
    assert all("test" in chunk.tags for chunk in chunks)


@pytest.mark.asyncio
async def test_scan_file_normal_size_no_streaming(temp_vault):
    """Тест обычной обработки для файла нормального размера."""
    from obsidian_kb.config import settings
    
    # Создаём файл нормального размера (меньше порога потоковой обработки)
    file_path = temp_vault / "normal_file.md"
    content = "---\ntitle: Normal File\ntags: [normal]\n---\n\n# Normal File\n\nNormal content."
    file_path.write_text(content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Файл должен быть обработан обычным способом
    assert len(chunks) > 0
    assert all(chunk.title == "Normal File" for chunk in chunks)


@pytest.mark.asyncio
async def test_scan_file_with_code_blocks(temp_vault):
    """Тест индексации файла с code blocks."""
    file_path = temp_vault / "code_blocks_test.md"
    content = """---
title: Code Blocks Test
tags: [code, test]
---

# Code Blocks Test

This is a regular text section.

## Python Example

Here's some Python code:

```python
def hello_world():
    print("Hello, World!")
    return True
```

## JavaScript Example

And some JavaScript:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

## Plain Code Block

```bash
echo "Hello from bash"
```

More regular text here.
"""
    file_path.write_text(content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Должны быть чанки для обычного текста и для code blocks
    assert len(chunks) > 0
    
    # Проверяем, что есть чанки с code blocks
    code_block_chunks = [
        chunk for chunk in chunks 
        if chunk.metadata.get("content_type") == "code_block"
    ]
    
    assert len(code_block_chunks) >= 3, "Должно быть минимум 3 code block чанка"
    
    # Проверяем метаданные code blocks
    languages = {chunk.metadata.get("code_language") for chunk in code_block_chunks}
    assert "python" in languages
    assert "javascript" in languages
    assert "bash" in languages or "plain" in languages
    
    # Проверяем, что code blocks содержат код
    python_chunk = next(
        (chunk for chunk in code_block_chunks if chunk.metadata.get("code_language") == "python"),
        None
    )
    assert python_chunk is not None
    assert "def hello_world" in python_chunk.content
    assert "print" in python_chunk.content
    
    # Проверяем, что обычные чанки не имеют content_type code_block
    regular_chunks = [
        chunk for chunk in chunks 
        if chunk.metadata.get("content_type") != "code_block"
    ]
    assert len(regular_chunks) > 0, "Должны быть обычные чанки с текстом"
    
    # Проверяем, что обычные чанки не содержат code blocks
    for chunk in regular_chunks:
        assert "```" not in chunk.content or chunk.content.count("```") == 0


@pytest.mark.asyncio
async def test_scan_file_with_code_blocks_no_language(temp_vault):
    """Тест индексации code block без указания языка."""
    file_path = temp_vault / "code_no_lang.md"
    content = """---
title: Code No Language
---

# Test

Some text.

```
This is a code block without language
specification.
```

More text.
"""
    file_path.write_text(content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Находим code block чанки
    code_block_chunks = [
        chunk for chunk in chunks 
        if chunk.metadata.get("content_type") == "code_block"
    ]
    
    assert len(code_block_chunks) >= 1
    assert code_block_chunks[0].metadata.get("code_language") == "plain"
    assert "This is a code block" in code_block_chunks[0].content


@pytest.mark.asyncio
async def test_scan_file_with_quotes_in_frontmatter(temp_vault):
    """Тест индексации файла с кавычками в frontmatter title."""
    file_path = temp_vault / "quotes_test.md"
    content = """---
type: document
title: "Глубокий анализ встречи "Стратегический продуктовый комит""
tags: [meeting]
---

# Test Document

Content here.
"""
    file_path.write_text(content, encoding="utf-8")
    
    indexer = VaultIndexer(temp_vault, "test_vault")
    chunks = await indexer.scan_file(file_path)
    
    # Должен успешно проиндексироваться без ошибок
    assert len(chunks) > 0
    
    # Проверяем, что title правильно извлечен
    assert chunks[0].title == 'Глубокий анализ встречи "Стратегический продуктовый комит"'
    
    # Проверяем, что metadata содержит правильный type
    assert chunks[0].metadata.get("type") == "document"


class TestVaultIndexerParsing:
    """Тесты для методов парсинга VaultIndexer."""
    
    def test_parse_date_iso_format(self, temp_vault):
        """Тест парсинга даты в ISO формате."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        # ISO 8601 с timezone
        date1 = indexer._parse_date("2024-01-01T10:30:00+00:00")
        assert date1 is not None
        assert date1.year == 2024
        assert date1.month == 1
        assert date1.day == 1
        
        # ISO 8601 без timezone
        date2 = indexer._parse_date("2024-01-01T10:30:00")
        assert date2 is not None
        assert date2.year == 2024
        
        # ISO 8601 только дата
        date3 = indexer._parse_date("2024-01-01")
        assert date3 is not None
        assert date3.year == 2024
    
    def test_parse_date_timestamp(self, temp_vault):
        """Тест парсинга даты из timestamp."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        # Unix timestamp
        timestamp = 1704110400  # 2024-01-01 10:00:00 UTC
        date = indexer._parse_date(timestamp)
        assert date is not None
        assert date.year == 2024
        
        # Float timestamp
        float_timestamp = 1704110400.0
        date2 = indexer._parse_date(float_timestamp)
        assert date2 is not None
    
    def test_parse_date_alternative_formats(self, temp_vault):
        """Тест парсинга даты в альтернативных форматах."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        # DD.MM.YYYY
        date1 = indexer._parse_date("01.01.2024")
        assert date1 is not None
        assert date1.year == 2024
        
        # DD/MM/YYYY
        date2 = indexer._parse_date("01/01/2024")
        assert date2 is not None
        
        # MM/DD/YYYY
        date3 = indexer._parse_date("12/31/2024")
        assert date3 is not None
        assert date3.year == 2024
    
    def test_parse_date_with_time(self, temp_vault):
        """Тест парсинга даты с временем."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        # ISO формат с временем
        date1 = indexer._parse_date("2024-01-01 10:30:00")
        assert date1 is not None
        assert date1.hour == 10
        assert date1.minute == 30
        
        # Альтернативный формат с временем
        date2 = indexer._parse_date("01.01.2024 10:30:00")
        assert date2 is not None
        assert date2.hour == 10
    
    def test_parse_date_invalid(self, temp_vault):
        """Тест парсинга невалидной даты."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        # Невалидная дата должна вернуть None
        date = indexer._parse_date("invalid-date")
        assert date is None
        
        # Пустая строка
        date2 = indexer._parse_date("")
        assert date2 is None
    
    def test_extract_wikilinks_simple(self, temp_vault):
        """Тест извлечения простых wikilinks."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        text = "This is a link to [[note1]] and another [[note2]]."
        links = indexer._extract_wikilinks(text)
        
        assert len(links) == 2
        assert "note1" in links
        assert "note2" in links
    
    def test_extract_wikilinks_with_paths(self, temp_vault):
        """Тест извлечения wikilinks с путями."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        text = "Link to [[path/to/note]] and [[another/path/to/file]]."
        links = indexer._extract_wikilinks(text)
        
        # Ссылки должны быть нормализованы (извлечено имя файла)
        assert len(links) == 2
        assert "note" in links or "file" in links
    
    def test_extract_wikilinks_with_aliases(self, temp_vault):
        """Тест извлечения wikilinks с алиасами."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        text = "Link [[note|Display Text]] and [[another|Another Display]]."
        links = indexer._extract_wikilinks(text)
        
        # Алиасы должны быть обработаны при нормализации
        assert len(links) == 2
        assert "note" in links
        assert "another" in links
    
    def test_extract_wikilinks_empty(self, temp_vault):
        """Тест извлечения wikilinks из текста без ссылок."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        text = "This is plain text without any links."
        links = indexer._extract_wikilinks(text)
        
        assert len(links) == 0
    
    def test_extract_inline_tags(self, temp_vault):
        """Тест извлечения inline тегов."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        text = "This is text with #tag1 and #tag-2 and #another_tag."
        tags = indexer._extract_inline_tags(text)
        
        assert len(tags) == 3
        assert "tag1" in tags
        assert "tag-2" in tags
        assert "another_tag" in tags
    
    def test_parse_frontmatter_separates_type_and_tags(self, temp_vault):
        """Тест что frontmatter разделяет type и tags."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        content = """---
type: person
tags: [person, meeting]
---
# Content
"""
        frontmatter_data, body = indexer._parse_frontmatter(content)
        
        # type должен быть в metadata, не в tags
        assert frontmatter_data.metadata.get("type") == "person"
        # tags должны быть в frontmatter_data.tags
        assert "person" in frontmatter_data.tags
        assert "meeting" in frontmatter_data.tags
    
    def test_parse_frontmatter_with_inline_tags(self, temp_vault):
        """Тест парсинга frontmatter с разделением frontmatter и inline тегов."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        content = """---
tags: [frontmatter-tag]
---
# Content

This has #inline-tag in the text.
"""
        frontmatter_data, body = indexer._parse_frontmatter(content)
        
        # Frontmatter теги должны быть в frontmatter_data.tags
        assert "frontmatter-tag" in frontmatter_data.tags
        
        # Inline теги должны быть извлечены из body отдельно
        inline_tags = indexer._extract_inline_tags(body)
        assert "inline-tag" in inline_tags
    
    def test_parse_frontmatter_date_priority(self, temp_vault):
        """Тест что даты из frontmatter имеют приоритет над filesystem."""
        indexer = VaultIndexer(temp_vault, "test_vault")
        
        content = """---
created: 2024-01-01T10:00:00
modified: 2024-12-31T20:00:00
---
# Content
"""
        frontmatter_data, body = indexer._parse_frontmatter(content)
        
        # Даты должны быть распарсены из frontmatter
        assert frontmatter_data.created_at is not None
        assert frontmatter_data.created_at.year == 2024
        assert frontmatter_data.created_at.month == 1
        
        assert frontmatter_data.modified_at is not None
        assert frontmatter_data.modified_at.year == 2024
        assert frontmatter_data.modified_at.month == 12

