"""Tests for Office document text extraction."""

import tempfile
from pathlib import Path


from preocr import office_probe


def test_extract_office_structure():
    """Test that office extraction returns correct structure."""
    # Test DOCX
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(b"PK\x03\x04")  # ZIP signature
        temp_path = f.name

    try:
        result = office_probe.extract_office_text(
            temp_path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert isinstance(result, dict)
        assert "text_length" in result
        assert "text" in result
        assert "document_type" in result
    finally:
        Path(temp_path).unlink()


def test_extract_pptx():
    """Test PPTX extraction structure."""
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        f.write(b"PK\x03\x04")
        temp_path = f.name

    try:
        result = office_probe.extract_office_text(
            temp_path, "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        assert result["document_type"] == "pptx"
    finally:
        Path(temp_path).unlink()


def test_extract_xlsx():
    """Test XLSX extraction structure."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        f.write(b"PK\x03\x04")
        temp_path = f.name

    try:
        result = office_probe.extract_office_text(
            temp_path, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert result["document_type"] == "xlsx"
    finally:
        Path(temp_path).unlink()

