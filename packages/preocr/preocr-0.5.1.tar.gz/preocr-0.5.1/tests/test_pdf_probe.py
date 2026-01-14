"""Tests for PDF text extraction."""

import tempfile
from pathlib import Path


from preocr import pdf_probe


def test_extract_pdf_no_libraries():
    """Test PDF extraction when libraries are not available."""
    # Create a dummy file (not a real PDF, but tests the fallback)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"Not a real PDF")
        temp_path = f.name

    try:
        result = pdf_probe.extract_pdf_text(temp_path)
        # Should return a result dict even if extraction fails
        assert "text_length" in result
        assert "text" in result
        assert "page_count" in result
        assert "method" in result
    finally:
        Path(temp_path).unlink()


def test_extract_pdf_structure():
    """Test that PDF extraction returns correct structure."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = pdf_probe.extract_pdf_text(temp_path)
        assert isinstance(result, dict)
        assert "text_length" in result
        assert "text" in result
        assert "page_count" in result
        assert "method" in result
    finally:
        Path(temp_path).unlink()
