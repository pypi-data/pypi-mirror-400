"""Tests for signal collection."""

import tempfile
from pathlib import Path

from preocr import filetype, signals


def test_collect_signals():
    """Test signal collection."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Test content")
        temp_path = f.name

    try:
        file_info = filetype.detect_file_type(temp_path)
        text_result = {"text_length": 12, "text": "Test content"}

        result = signals.collect_signals(temp_path, file_info, text_result)

        assert "mime" in result
        assert "extension" in result
        assert "is_binary" in result
        assert "text_length" in result
        assert "file_size" in result
        assert "has_text" in result
        assert result["text_length"] == 12
        assert result["has_text"] is True
    finally:
        Path(temp_path).unlink()


def test_collect_signals_with_image():
    """Test signal collection with image data."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake image")
        temp_path = f.name

    try:
        file_info = filetype.detect_file_type(temp_path)
        image_result = {"entropy": 5.2, "width": 100, "height": 100}

        result = signals.collect_signals(temp_path, file_info, image_result=image_result)

        assert result["image_entropy"] == 5.2
        assert result["text_length"] == 0
        assert result["has_text"] is False
    finally:
        Path(temp_path).unlink()

