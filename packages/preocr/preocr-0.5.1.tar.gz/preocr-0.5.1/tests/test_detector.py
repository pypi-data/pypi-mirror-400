"""Tests for main detector API."""

import tempfile
from pathlib import Path

import pytest

from preocr import detector


def test_needs_ocr_text_file():
    """Test needs_ocr with a text file."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("This is a test file with enough text content.")
        temp_path = f.name

    try:
        result = detector.needs_ocr(temp_path)

        assert "needs_ocr" in result
        assert "file_type" in result
        assert "category" in result
        assert "confidence" in result
        assert "reason" in result
        assert "signals" in result

        assert result["needs_ocr"] is False
        assert result["file_type"] == "text"
        assert result["category"] == "structured"
    finally:
        Path(temp_path).unlink()


def test_needs_ocr_nonexistent_file():
    """Test needs_ocr with non-existent file."""
    with pytest.raises(FileNotFoundError):
        detector.needs_ocr("/nonexistent/file.txt")


def test_needs_ocr_structure():
    """Test that needs_ocr returns correct structure."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Test")
        temp_path = f.name

    try:
        result = detector.needs_ocr(temp_path)

        # Check all required keys
        required_keys = [
            "needs_ocr",
            "file_type",
            "category",
            "confidence",
            "reason",
            "reason_code",
            "signals",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

        # Check types
        assert isinstance(result["needs_ocr"], bool)
        assert isinstance(result["file_type"], str)
        assert isinstance(result["category"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["reason"], str)
        assert isinstance(result["reason_code"], str)
        assert isinstance(result["signals"], dict)
    finally:
        Path(temp_path).unlink()


def test_needs_ocr_with_path_object():
    """Test needs_ocr accepts Path objects."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Test content")
        temp_path = Path(f.name)

    try:
        result = detector.needs_ocr(temp_path)
        assert "needs_ocr" in result
    finally:
        temp_path.unlink()
