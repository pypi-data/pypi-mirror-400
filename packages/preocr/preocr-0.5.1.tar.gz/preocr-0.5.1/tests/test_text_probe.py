"""Tests for text extraction probes."""

import tempfile
from pathlib import Path

from preocr import text_probe


def test_extract_plain_text():
    """Test plain text extraction."""
    content = "This is a test file with some text content."
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        result = text_probe.extract_text_from_file(temp_path, "text/plain")
        assert result["text_length"] == len(content)
        assert result["text"] == content
        assert result["encoding"] is not None
    finally:
        Path(temp_path).unlink()


def test_extract_html():
    """Test HTML text extraction."""
    html_content = "<html><body><p>Hello World</p></body></html>"
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = text_probe.extract_text_from_file(temp_path, "text/html")
        assert result["text_length"] > 0
        assert "Hello World" in result["text"]
    finally:
        Path(temp_path).unlink()


def test_has_meaningful_text():
    """Test meaningful text detection."""
    long_text = (
        "This is a long text with enough characters to pass the minimum threshold of 50 characters."
    )
    assert text_probe.has_meaningful_text(long_text, 50) is True
    assert text_probe.has_meaningful_text("Short", 50) is False
    assert text_probe.has_meaningful_text("", 50) is False
    assert text_probe.has_meaningful_text("   ", 50) is False


def test_empty_file():
    """Test handling of empty files."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        temp_path = f.name

    try:
        result = text_probe.extract_text_from_file(temp_path, "text/plain")
        assert result["text_length"] == 0
    finally:
        Path(temp_path).unlink()
