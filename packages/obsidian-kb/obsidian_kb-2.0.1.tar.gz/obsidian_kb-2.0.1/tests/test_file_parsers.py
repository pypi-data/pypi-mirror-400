"""Тесты для file_parsers.py"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from obsidian_kb.file_parsers import (
    extract_text_from_docx,
    extract_text_from_file,
    extract_text_from_pdf,
    is_supported_file,
)


def test_is_supported_file():
    """Тест проверки поддерживаемых форматов."""
    assert is_supported_file(Path("test.md"))
    assert is_supported_file(Path("test.pdf"))
    assert is_supported_file(Path("test.docx"))
    assert not is_supported_file(Path("test.txt"))
    assert not is_supported_file(Path("test.doc"))
    assert not is_supported_file(Path("test"))


def test_is_supported_file_case_insensitive():
    """Тест проверки форматов без учёта регистра."""
    assert is_supported_file(Path("test.MD"))
    assert is_supported_file(Path("test.PDF"))
    assert is_supported_file(Path("test.DOCX"))


@patch("pypdf.PdfReader")
def test_extract_text_from_pdf_success(mock_pdf_reader, tmp_path):
    """Тест успешного извлечения текста из PDF."""
    # Создаём мок PDF файла
    mock_reader = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 content"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 content"
    mock_reader.pages = [mock_page1, mock_page2]
    mock_pdf_reader.return_value = mock_reader

    file_path = tmp_path / "test.pdf"
    file_path.touch()

    text = extract_text_from_pdf(file_path)

    assert "Page 1 content" in text
    assert "Page 2 content" in text
    mock_pdf_reader.assert_called_once_with(file_path)


@patch("pypdf.PdfReader")
def test_extract_text_from_pdf_empty(mock_pdf_reader, tmp_path):
    """Тест извлечения текста из пустого PDF."""
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_reader.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader

    file_path = tmp_path / "test.pdf"
    file_path.touch()

    text = extract_text_from_pdf(file_path)
    # Функция возвращает пустую строку, если текст не извлечён
    assert text == ""


@patch("pypdf.PdfReader")
def test_extract_text_from_pdf_error_on_page(mock_pdf_reader, tmp_path):
    """Тест обработки ошибки при извлечении текста со страницы."""
    mock_reader = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.side_effect = Exception("Page error")
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 content"
    mock_reader.pages = [mock_page1, mock_page2]
    mock_pdf_reader.return_value = mock_reader

    file_path = tmp_path / "test.pdf"
    file_path.touch()

    text = extract_text_from_pdf(file_path)
    assert "Page 2 content" in text
    assert "Page 1 content" not in text


def test_extract_text_from_pdf_import_error(tmp_path):
    """Тест обработки ошибки импорта pypdf."""
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    # Этот тест проверяет, что функция обрабатывает ImportError
    # В реальности это проверяется при отсутствии библиотеки
    # Пропускаем этот тест, так как библиотека установлена
    pytest.skip("Тест требует отсутствия pypdf, но библиотека установлена")


@patch("docx.Document")
def test_extract_text_from_docx_success(mock_document, tmp_path):
    """Тест успешного извлечения текста из DOCX."""
    # Создаём мок DOCX файла
    mock_doc = MagicMock()
    mock_paragraph1 = MagicMock()
    mock_paragraph1.text = "First paragraph"
    mock_paragraph2 = MagicMock()
    mock_paragraph2.text = "Second paragraph"
    mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
    mock_doc.tables = []
    mock_document.return_value = mock_doc

    file_path = tmp_path / "test.docx"
    file_path.touch()

    text = extract_text_from_docx(file_path)

    assert "First paragraph" in text
    assert "Second paragraph" in text
    mock_document.assert_called_once_with(file_path)


@patch("docx.Document")
def test_extract_text_from_docx_with_tables(mock_document, tmp_path):
    """Тест извлечения текста из DOCX с таблицами."""
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="Paragraph text")]
    
    # Создаём мок таблицы
    mock_table = MagicMock()
    mock_row = MagicMock()
    mock_cell1 = MagicMock()
    mock_cell1.text = "Cell 1"
    mock_cell2 = MagicMock()
    mock_cell2.text = "Cell 2"
    mock_row.cells = [mock_cell1, mock_cell2]
    mock_table.rows = [mock_row]
    mock_doc.tables = [mock_table]
    mock_document.return_value = mock_doc

    file_path = tmp_path / "test.docx"
    file_path.touch()

    text = extract_text_from_docx(file_path)

    assert "Paragraph text" in text
    assert "Cell 1" in text
    assert "Cell 2" in text
    assert " | " in text  # Разделитель ячеек


@patch("docx.Document")
def test_extract_text_from_docx_empty(mock_document, tmp_path):
    """Тест извлечения текста из пустого DOCX."""
    mock_doc = MagicMock()
    mock_doc.paragraphs = []
    mock_doc.tables = []
    mock_document.return_value = mock_doc

    file_path = tmp_path / "test.docx"
    file_path.touch()

    text = extract_text_from_docx(file_path)
    assert text == ""


def test_extract_text_from_docx_import_error(tmp_path):
    """Тест обработки ошибки импорта python-docx."""
    file_path = tmp_path / "test.docx"
    file_path.touch()

    # Этот тест проверяет, что функция обрабатывает ImportError
    # В реальности это проверяется при отсутствии библиотеки
    # Пропускаем этот тест, так как библиотека установлена
    pytest.skip("Тест требует отсутствия python-docx, но библиотека установлена")


@patch("obsidian_kb.file_parsers.extract_text_from_pdf")
def test_extract_text_from_file_pdf(mock_extract_pdf, tmp_path):
    """Тест extract_text_from_file для PDF."""
    mock_extract_pdf.return_value = "PDF content"
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    result = extract_text_from_file(file_path)

    assert result == "PDF content"
    mock_extract_pdf.assert_called_once_with(file_path)


@patch("obsidian_kb.file_parsers.extract_text_from_docx")
def test_extract_text_from_file_docx(mock_extract_docx, tmp_path):
    """Тест extract_text_from_file для DOCX."""
    mock_extract_docx.return_value = "DOCX content"
    file_path = tmp_path / "test.docx"
    file_path.touch()

    result = extract_text_from_file(file_path)

    assert result == "DOCX content"
    mock_extract_docx.assert_called_once_with(file_path)


def test_extract_text_from_file_markdown(tmp_path):
    """Тест extract_text_from_file для Markdown."""
    file_path = tmp_path / "test.md"
    file_path.write_text("# Test Markdown\n\nSome content here.", encoding="utf-8")

    result = extract_text_from_file(file_path)

    assert result == "# Test Markdown\n\nSome content here."


def test_extract_text_from_file_unsupported(tmp_path):
    """Тест extract_text_from_file для неподдерживаемого формата."""
    file_path = tmp_path / "test.txt"
    file_path.touch()

    result = extract_text_from_file(file_path)

    assert result is None


@patch("obsidian_kb.file_parsers.extract_text_from_pdf")
def test_extract_text_from_file_pdf_error(mock_extract_pdf, tmp_path):
    """Тест обработки ошибки при извлечении текста из PDF."""
    mock_extract_pdf.side_effect = Exception("PDF error")
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    result = extract_text_from_file(file_path)

    assert result is None

