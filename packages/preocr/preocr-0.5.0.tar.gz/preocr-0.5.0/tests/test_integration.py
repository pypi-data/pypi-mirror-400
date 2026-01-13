"""Integration tests for the full OCR detection pipeline."""

import tempfile
from pathlib import Path


from preocr import needs_ocr


def test_integration_text_file():
    """Test full pipeline with a text file."""
    content = "This is a comprehensive test document with enough text to be meaningful."
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        result = needs_ocr(temp_path)

        # Verify complete result structure
        assert result["needs_ocr"] is False
        assert result["file_type"] == "text"
        assert result["category"] == "structured"
        assert result["confidence"] >= 0.9
        assert "text" in result["reason"].lower()

        # Verify signals
        signals = result["signals"]
        assert signals["text_length"] > 0
        assert signals["has_text"] is True
    finally:
        Path(temp_path).unlink()


def test_integration_html_file():
    """Test full pipeline with an HTML file."""
    html_content = """
    <html>
    <head><title>Test</title></head>
    <body>
        <p>This is a test HTML document with sufficient content.</p>
        <p>It has multiple paragraphs to ensure meaningful text extraction.</p>
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = needs_ocr(temp_path)
        assert result["needs_ocr"] is False
        assert result["file_type"] == "text"
    finally:
        Path(temp_path).unlink()


def test_integration_pdf_simulation():
    """Test full pipeline with a PDF-like file (simulated)."""
    # Create a file that will be detected as PDF but won't have extractable text
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = needs_ocr(temp_path)

        # Should detect as PDF
        assert result["file_type"] == "pdf"

        # Result should be consistent (either needs OCR or not, but structure should be correct)
        assert isinstance(result["needs_ocr"], bool)
        assert result["category"] in ["structured", "unstructured"]
    finally:
        Path(temp_path).unlink()


def test_integration_image_file():
    """Test full pipeline with an image file."""
    # Create a minimal valid PNG
    png_data = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(png_data)
        temp_path = f.name

    try:
        result = needs_ocr(temp_path)

        assert result["needs_ocr"] is True
        assert result["file_type"] == "image"
        assert result["category"] == "unstructured"
        assert "image" in result["reason"].lower()
    finally:
        Path(temp_path).unlink()


def test_integration_empty_file():
    """Test full pipeline with an empty file."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        temp_path = f.name

    try:
        result = needs_ocr(temp_path)
        # Should handle empty file gracefully
        assert "needs_ocr" in result
        assert "signals" in result
    finally:
        Path(temp_path).unlink()


def test_integration_unknown_binary():
    """Test full pipeline with unknown binary file."""
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
        f.write(b"\x00\x01\x02\x03\x04\x05")
        temp_path = f.name

    try:
        result = needs_ocr(temp_path)

        # Unknown binaries should default to needing OCR (conservative)
        assert result["needs_ocr"] is True
        assert result["category"] == "unstructured"
    finally:
        Path(temp_path).unlink()

