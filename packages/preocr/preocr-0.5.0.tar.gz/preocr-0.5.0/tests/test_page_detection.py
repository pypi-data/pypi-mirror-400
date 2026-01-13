"""Tests for page-level detection."""

import tempfile
from pathlib import Path


from preocr import detector, page_detection
from preocr.constants import ReasonCode


def test_page_detection_structure():
    """Test that page detection returns correct structure."""
    # Mock PDF result with pages
    file_info = {"mime": "application/pdf", "extension": "pdf", "is_binary": True}
    pdf_result = {
        "text_length": 100,
        "page_count": 3,
        "pages": [
            {"page_number": 1, "text_length": 50, "needs_ocr": False, "has_text": True},
            {"page_number": 2, "text_length": 0, "needs_ocr": True, "has_text": False},
            {"page_number": 3, "text_length": 50, "needs_ocr": False, "has_text": True},
        ],
    }

    result = page_detection.analyze_pdf_pages("test.pdf", file_info, pdf_result)

    assert "overall_needs_ocr" in result
    assert "overall_confidence" in result
    assert "overall_reason_code" in result
    assert "pages" in result
    assert "page_count" in result
    assert len(result["pages"]) == 3
    assert result["overall_needs_ocr"] is True  # At least one page needs OCR


def test_page_detection_all_digital():
    """Test page detection when all pages are digital."""
    file_info = {"mime": "application/pdf", "extension": "pdf", "is_binary": True}
    pdf_result = {
        "text_length": 200,
        "page_count": 2,
        "pages": [
            {"page_number": 1, "text_length": 100, "needs_ocr": False, "has_text": True},
            {"page_number": 2, "text_length": 100, "needs_ocr": False, "has_text": True},
        ],
    }

    result = page_detection.analyze_pdf_pages("test.pdf", file_info, pdf_result)

    assert result["overall_needs_ocr"] is False
    assert result["overall_reason_code"] == ReasonCode.PDF_DIGITAL
    assert result["pages_needing_ocr"] == 0


def test_page_detection_all_scanned():
    """Test page detection when all pages are scanned."""
    file_info = {"mime": "application/pdf", "extension": "pdf", "is_binary": True}
    pdf_result = {
        "text_length": 0,
        "page_count": 2,
        "pages": [
            {"page_number": 1, "text_length": 0, "needs_ocr": True, "has_text": False},
            {"page_number": 2, "text_length": 0, "needs_ocr": True, "has_text": False},
        ],
    }

    result = page_detection.analyze_pdf_pages("test.pdf", file_info, pdf_result)

    assert result["overall_needs_ocr"] is True
    assert result["overall_reason_code"] == ReasonCode.PDF_SCANNED
    assert result["pages_needing_ocr"] == 2


def test_page_detection_mixed():
    """Test page detection with mixed digital and scanned pages."""
    file_info = {"mime": "application/pdf", "extension": "pdf", "is_binary": True}
    pdf_result = {
        "text_length": 100,
        "page_count": 3,
        "pages": [
            {"page_number": 1, "text_length": 100, "needs_ocr": False, "has_text": True},
            {"page_number": 2, "text_length": 0, "needs_ocr": True, "has_text": False},
            {"page_number": 3, "text_length": 100, "needs_ocr": False, "has_text": True},
        ],
    }

    result = page_detection.analyze_pdf_pages("test.pdf", file_info, pdf_result)

    assert result["overall_needs_ocr"] is True
    assert result["overall_reason_code"] == ReasonCode.PDF_MIXED
    assert result["pages_needing_ocr"] == 1
    assert result["pages_with_text"] == 2


def test_detector_with_page_level():
    """Test detector API with page_level=True."""
    # Create a minimal PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\n")
        temp_path = f.name

    try:
        result = detector.needs_ocr(temp_path, page_level=True)

        # Should have reason_code
        assert "reason_code" in result

        # If PDF has pages, should have page-level data
        if result.get("page_count", 0) > 0:
            assert "pages" in result
    finally:
        Path(temp_path).unlink()

