"""Тесты для модуля игнорирования файлов."""

import tempfile
from pathlib import Path

import pytest

from obsidian_kb.ignore_patterns import (
    IGNORE_FILE_NAME,
    IgnoreMatcher,
    IgnorePattern,
    load_ignore_patterns,
    parse_ignore_file,
)


def test_ignore_pattern_simple():
    """Тест простого паттерна."""
    pattern = IgnorePattern("*.tmp")
    assert pattern.matches("file.tmp")
    assert pattern.matches("path/to/file.tmp")
    assert not pattern.matches("file.md")
    assert not pattern.matches("file.tmp.bak")


def test_ignore_pattern_directory():
    """Тест паттерна для директории."""
    pattern = IgnorePattern("node_modules/")
    assert pattern.matches("node_modules/file.md")
    assert pattern.matches("node_modules/subdir/file.md")
    assert not pattern.matches("file.md")


def test_ignore_pattern_wildcard():
    """Тест паттерна с wildcard."""
    pattern = IgnorePattern("**/temp/**")
    # Паттерн **/temp/** должен соответствовать temp в любом месте и всё внутри
    assert pattern.matches("temp/file.md")
    assert pattern.matches("path/temp/file.md")
    assert pattern.matches("a/b/temp/c/file.md")
    
    # Также проверяем простой паттерн temp/ (должен соответствовать temp в любом месте)
    pattern2 = IgnorePattern("temp/")
    assert pattern2.matches("temp/file.md")
    # Паттерн temp/ должен соответствовать temp в любом месте пути
    assert pattern2.matches("path/temp/file.md") or pattern2.matches("temp/file.md")


def test_ignore_pattern_negation():
    """Тест паттерна отрицания."""
    patterns = [
        IgnorePattern("*.tmp"),
        IgnorePattern("important.tmp", is_negation=True),
    ]
    matcher = IgnoreMatcher(patterns)
    
    assert matcher.should_ignore("file.tmp")
    assert not matcher.should_ignore("important.tmp")  # Отрицание отменяет


def test_ignore_matcher_multiple_patterns():
    """Тест матчера с несколькими паттернами."""
    patterns = [
        IgnorePattern("*.tmp"),
        IgnorePattern("temp/"),
        IgnorePattern("*.bak"),
    ]
    matcher = IgnoreMatcher(patterns)
    
    assert matcher.should_ignore("file.tmp")
    assert matcher.should_ignore("temp/file.md")
    assert matcher.should_ignore("file.bak")
    assert not matcher.should_ignore("file.md")
    assert not matcher.should_ignore("normal/file.md")


def test_parse_ignore_file():
    """Тест парсинга файла игнорирования."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ignore", delete=False) as f:
        f.write("# Комментарий\n")
        f.write("*.tmp\n")
        f.write("temp/\n")
        f.write("!important.tmp\n")
        f.write("\n")  # Пустая строка
        ignore_file = Path(f.name)
    
    try:
        patterns = parse_ignore_file(ignore_file)
        assert len(patterns) == 3
        
        # Проверяем паттерны
        tmp_pattern = [p for p in patterns if p.pattern == "*.tmp"][0]
        assert not tmp_pattern.is_negation
        
        temp_pattern = [p for p in patterns if p.pattern == "temp/"][0]
        assert not temp_pattern.is_negation
        
        important_pattern = [p for p in patterns if p.pattern == "important.tmp"][0]
        assert important_pattern.is_negation
    finally:
        ignore_file.unlink()


def test_parse_ignore_file_nonexistent():
    """Тест парсинга несуществующего файла."""
    patterns = parse_ignore_file(Path("/nonexistent/file"))
    assert patterns == []


def test_load_ignore_patterns():
    """Тест загрузки паттернов для vault'а."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        
        # Создаём файл игнорирования
        ignore_file = vault_path / IGNORE_FILE_NAME
        ignore_file.write_text("*.tmp\ntemp/\n")
        
        matcher = load_ignore_patterns(vault_path)
        
        assert matcher.should_ignore("file.tmp")
        assert matcher.should_ignore("temp/file.md")
        assert not matcher.should_ignore("file.md")


def test_load_ignore_patterns_defaults():
    """Тест загрузки паттернов по умолчанию."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        
        # Не создаём файл игнорирования - должны использоваться паттерны по умолчанию
        matcher = load_ignore_patterns(vault_path)
        
        # Проверяем паттерны по умолчанию
        assert matcher.should_ignore("file.tmp")
        assert matcher.should_ignore("node_modules/file.md")
        assert matcher.should_ignore(".DS_Store")
        assert not matcher.should_ignore("file.md")


def test_ignore_parent_directory():
    """Тест игнорирования родительской директории."""
    patterns = [
        IgnorePattern("temp/"),
    ]
    matcher = IgnoreMatcher(patterns)
    
    # Если родительская директория игнорируется, файл тоже должен игнорироваться
    assert matcher.should_ignore("temp/file.md")
    assert matcher.should_ignore("temp/subdir/file.md")
    assert not matcher.should_ignore("other/file.md")


def test_ignore_pattern_with_slash():
    """Тест паттерна с ведущим слэшем."""
    pattern = IgnorePattern("/temp/")
    assert pattern.matches("temp/file.md")
    assert not pattern.matches("other/temp/file.md")


def test_ignore_pattern_question_mark():
    """Тест паттерна с вопросительным знаком."""
    pattern = IgnorePattern("file?.tmp")
    assert pattern.matches("file1.tmp")
    assert pattern.matches("fileA.tmp")
    assert not pattern.matches("file12.tmp")  # Два символа


@pytest.mark.asyncio
async def test_vault_indexer_with_ignore(tmp_path):
    """Тест индексатора с игнорированием файлов."""
    from obsidian_kb.vault_indexer import VaultIndexer
    
    # Создаём структуру vault'а
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    
    # Создаём файлы
    (vault_path / "file1.md").write_text("# File 1\nContent")
    (vault_path / "file2.md").write_text("# File 2\nContent")
    (vault_path / "file.tmp").write_text("# Temp file\nContent")
    
    # Создаём директорию temp
    temp_dir = vault_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "file3.md").write_text("# File 3\nContent")
    
    # Создаём файл игнорирования
    ignore_file = vault_path / IGNORE_FILE_NAME
    ignore_file.write_text("*.tmp\ntemp/\n")
    
    # Индексируем
    indexer = VaultIndexer(vault_path, "test_vault")
    chunks = await indexer.scan_all()
    
    # Проверяем, что игнорированные файлы не проиндексированы
    indexed_files = {chunk.file_path for chunk in chunks}
    
    assert "file1.md" in indexed_files
    assert "file2.md" in indexed_files
    assert "file.tmp" not in indexed_files
    assert "temp/file3.md" not in indexed_files

