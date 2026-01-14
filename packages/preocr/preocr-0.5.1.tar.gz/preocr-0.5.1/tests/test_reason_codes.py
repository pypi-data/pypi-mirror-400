"""Tests for reason codes."""

from preocr import reason_codes
from preocr.constants import ReasonCode


def test_reason_code_descriptions():
    """Test that all reason codes have descriptions."""
    assert reason_codes.get_reason_description(ReasonCode.TEXT_FILE) is not None
    assert reason_codes.get_reason_description(ReasonCode.IMAGE_FILE) is not None
    assert reason_codes.get_reason_description(ReasonCode.PDF_DIGITAL) is not None
    assert reason_codes.get_reason_description(ReasonCode.PDF_SCANNED) is not None
    assert reason_codes.get_reason_description(ReasonCode.PDF_MIXED) is not None


def test_unknown_reason_code():
    """Test handling of unknown reason codes."""
    description = reason_codes.get_reason_description("UNKNOWN_CODE")
    assert "Unknown reason code" in description


def test_reason_code_in_result():
    """Test that detector returns reason_code in result."""
    import tempfile
    from pathlib import Path

    from preocr import detector

    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Test content")
        temp_path = f.name

    try:
        result = detector.needs_ocr(temp_path)
        assert "reason_code" in result
        assert result["reason_code"] is not None
        assert isinstance(result["reason_code"], str)
    finally:
        Path(temp_path).unlink()
