"""Tests for image analysis."""

import tempfile
from pathlib import Path


from preocr import image_probe


def test_is_image_file():
    """Test image file detection."""
    assert image_probe.is_image_file("image/png") is True
    assert image_probe.is_image_file("image/jpeg") is True
    assert image_probe.is_image_file("application/pdf") is False
    assert image_probe.is_image_file("text/plain") is False


def test_analyze_image_structure():
    """Test that image analysis returns correct structure."""
    # Create a minimal PNG file
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
        result = image_probe.analyze_image(temp_path)
        assert isinstance(result, dict)
        assert "entropy" in result
        assert "width" in result
        assert "height" in result
        assert "mode" in result
        assert result["is_image"] is True
    finally:
        Path(temp_path).unlink()


def test_analyze_invalid_image():
    """Test handling of invalid image files."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"Not an image")
        temp_path = f.name

    try:
        result = image_probe.analyze_image(temp_path)
        # Should return structure even if analysis fails
        assert result["is_image"] is True
    finally:
        Path(temp_path).unlink()
