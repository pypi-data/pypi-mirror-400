"""Tests for decision engine."""

from preocr import decision


def test_plain_text_no_ocr():
    """Test that plain text files don't need OCR."""
    signals = {
        "mime": "text/plain",
        "extension": "txt",
        "text_length": 100,
        "is_binary": False,
    }

    needs, reason, confidence, category, reason_code = decision.decide(signals)
    assert needs is False
    assert category == "structured"
    assert confidence >= 0.9
    assert reason_code is not None


def test_image_needs_ocr():
    """Test that images always need OCR."""
    signals = {
        "mime": "image/png",
        "extension": "png",
        "text_length": 0,
        "is_binary": True,
    }

    needs, reason, confidence, category, reason_code = decision.decide(signals)
    assert needs is True
    assert category == "unstructured"
    assert "image" in reason.lower()
    assert reason_code is not None


def test_pdf_with_text_no_ocr():
    """Test that PDFs with text don't need OCR."""
    signals = {
        "mime": "application/pdf",
        "extension": "pdf",
        "text_length": 500,
        "is_binary": True,
    }

    needs, reason, confidence, category, reason_code = decision.decide(signals)
    assert needs is False
    assert category == "structured"
    assert reason_code is not None


def test_pdf_without_text_needs_ocr():
    """Test that PDFs without text need OCR."""
    signals = {
        "mime": "application/pdf",
        "extension": "pdf",
        "text_length": 10,
        "is_binary": True,
    }

    needs, reason, confidence, category, reason_code = decision.decide(signals)
    assert needs is True
    assert category == "unstructured"
    assert reason_code is not None


def test_office_doc_with_text_no_ocr():
    """Test that office docs with text don't need OCR."""
    signals = {
        "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "extension": "docx",
        "text_length": 200,
        "is_binary": True,
    }

    needs, reason, confidence, category, reason_code = decision.decide(signals)
    assert needs is False
    assert category == "structured"
    assert reason_code is not None


def test_unknown_binary_needs_ocr():
    """Test that unknown binaries default to needing OCR."""
    signals = {
        "mime": "application/octet-stream",
        "extension": "bin",
        "text_length": 0,
        "is_binary": True,
    }

    needs, reason, confidence, category, reason_code = decision.decide(signals)
    assert needs is True
    assert category == "unstructured"
    assert reason_code is not None
