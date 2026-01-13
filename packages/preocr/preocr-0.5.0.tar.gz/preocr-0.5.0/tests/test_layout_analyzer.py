"""Tests for layout analyzer."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


from preocr import layout_analyzer


def test_analyze_pdf_layout_structure():
    """Test that layout analysis returns correct structure."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = layout_analyzer.analyze_pdf_layout(temp_path)

        assert isinstance(result, dict)
        assert "text_coverage" in result
        assert "image_coverage" in result
        assert "has_images" in result
        assert "text_density" in result
        assert "layout_type" in result
        assert "is_mixed_content" in result
    finally:
        Path(temp_path).unlink()


def test_analyze_pdf_layout_page_level():
    """Test page-level layout analysis."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = layout_analyzer.analyze_pdf_layout(temp_path, page_level=True)

        assert "pages" in result
        assert isinstance(result["pages"], list)
    finally:
        Path(temp_path).unlink()


@patch("preocr.layout_analyzer.pdfplumber")
def test_analyze_with_pdfplumber(mock_pdfplumber):
    """Test layout analysis with pdfplumber."""
    # Mock pdfplumber
    mock_page = MagicMock()
    mock_page.width = 612
    mock_page.height = 792
    mock_page.chars = [
        {"x0": 100, "x1": 200, "top": 100, "bottom": 120},
        {"x0": 100, "x1": 200, "top": 130, "bottom": 150},
    ]
    mock_page.words = []
    mock_page.images = []

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = layout_analyzer.analyze_pdf_layout(temp_path)

        assert result["layout_type"] in ["text_only", "image_only", "mixed", "unknown"]
        assert result["text_coverage"] >= 0
        assert result["image_coverage"] >= 0
    finally:
        Path(temp_path).unlink()


def test_determine_layout_type():
    """Test layout type determination."""
    # Text-only
    assert layout_analyzer._determine_layout_type(20.0, 2.0, 100) == "text_only"

    # Image-only
    assert layout_analyzer._determine_layout_type(2.0, 20.0, 10) == "image_only"

    # Mixed
    assert layout_analyzer._determine_layout_type(15.0, 15.0, 50) == "mixed"

    # Text with enough chars
    assert layout_analyzer._determine_layout_type(5.0, 2.0, 100) == "text_only"

    # Unknown
    assert layout_analyzer._determine_layout_type(2.0, 2.0, 10) == "unknown"


def test_analyze_pdf_layout_no_libraries():
    """Test layout analysis when no PDF libraries are available."""
    with patch("preocr.layout_analyzer.pdfplumber", None):
        with patch("preocr.layout_analyzer.fitz", None):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(b"%PDF-1.4\n")
                temp_path = f.name

            try:
                result = layout_analyzer.analyze_pdf_layout(temp_path)

                assert result["layout_type"] == "unknown"
                assert result["text_coverage"] == 0.0
                assert result["image_coverage"] == 0.0
                assert result["is_mixed_content"] is False
            finally:
                Path(temp_path).unlink()

