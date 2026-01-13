"""Reason code definitions and descriptions."""

from .constants import ReasonCode

# Human-readable descriptions for reason codes
REASON_DESCRIPTIONS = {
    # No OCR needed
    ReasonCode.TEXT_FILE: "Plain text file with extractable content",
    ReasonCode.OFFICE_WITH_TEXT: "Office document contains sufficient text",
    ReasonCode.PDF_DIGITAL: "Digital PDF with extractable text",
    ReasonCode.STRUCTURED_DATA: "Structured data file (JSON/XML)",
    ReasonCode.HTML_WITH_TEXT: "HTML file with sufficient text content",

    # OCR needed
    ReasonCode.IMAGE_FILE: "Image file (no text extraction possible)",
    ReasonCode.OFFICE_NO_TEXT: "Office document with insufficient text",
    ReasonCode.PDF_SCANNED: "PDF appears to be scanned (no extractable text)",
    ReasonCode.HTML_MINIMAL: "HTML file with minimal content",
    ReasonCode.UNKNOWN_BINARY: "Unknown binary file type",
    ReasonCode.UNRECOGNIZED_TYPE: "Unrecognized file type",

    # Page-level codes
    ReasonCode.PDF_PAGE_DIGITAL: "PDF page contains extractable text",
    ReasonCode.PDF_PAGE_SCANNED: "PDF page appears to be scanned",
    ReasonCode.PDF_MIXED: "PDF contains both digital and scanned pages",
}


def get_reason_description(code: str) -> str:
    """Get human-readable description for a reason code."""
    return REASON_DESCRIPTIONS.get(code, f"Unknown reason code: {code}")

