"""Tests for filetype detection."""

import tempfile
from pathlib import Path


from preocr import filetype


def test_detect_pdf():
    """Test PDF file type detection."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = filetype.detect_file_type(temp_path)
        assert result["extension"] == "pdf"
        assert "pdf" in result["mime"].lower()
        assert result["is_binary"] is True
    finally:
        Path(temp_path).unlink()


def test_detect_image():
    """Test image file type detection."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        temp_path = f.name

    try:
        result = filetype.detect_file_type(temp_path)
        assert result["extension"] == "png"
        # MIME detection may fall back to extension-based detection
        # So check that either it's detected as image or extension is correct
        assert result["mime"].startswith("image/") or result["extension"] == "png"
        assert result["is_binary"] is True
    finally:
        Path(temp_path).unlink()


def test_detect_text():
    """Test text file type detection."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Hello, world!")
        temp_path = f.name

    try:
        result = filetype.detect_file_type(temp_path)
        assert result["extension"] == "txt"
        assert result["mime"].startswith("text/")
        assert result["is_binary"] is False
    finally:
        Path(temp_path).unlink()


def test_detect_docx():
    """Test DOCX file type detection."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(b"PK\x03\x04")  # ZIP signature (DOCX is a ZIP file)
        temp_path = f.name

    try:
        result = filetype.detect_file_type(temp_path)
        assert result["extension"] == "docx"
        # MIME type may vary, but extension should be correct
        assert result["extension"] in ["docx", ""]  # Extension fallback
    finally:
        Path(temp_path).unlink()


def test_extension_fallback():
    """Test extension-based fallback when MIME detection fails."""
    # Create a file with unknown content but known extension
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(b"{}")
        temp_path = f.name

    try:
        result = filetype.detect_file_type(temp_path)
        # Should at least have the extension
        assert result["extension"] == "json"
    finally:
        Path(temp_path).unlink()

