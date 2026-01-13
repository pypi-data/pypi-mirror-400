"""Constants and configuration for preocr."""

# Minimum text length to consider a file as having meaningful text
MIN_TEXT_LENGTH = 50

# Minimum text length for office documents to skip OCR
MIN_OFFICE_TEXT_LENGTH = 100

# File type categories
CATEGORY_STRUCTURED = "structured"
CATEGORY_UNSTRUCTURED = "unstructured"

# Confidence thresholds
HIGH_CONFIDENCE = 0.9
MEDIUM_CONFIDENCE = 0.7
LOW_CONFIDENCE = 0.5

# Confidence threshold for triggering OpenCV layout analysis
# If initial confidence is below this, use OpenCV for refinement
LAYOUT_REFINEMENT_THRESHOLD = 0.9

# Reason codes for structured decision tracking
class ReasonCode:
    """Structured reason codes for OCR detection decisions."""

    # No OCR needed
    TEXT_FILE = "TEXT_FILE"
    OFFICE_WITH_TEXT = "OFFICE_WITH_TEXT"
    PDF_DIGITAL = "PDF_DIGITAL"
    STRUCTURED_DATA = "STRUCTURED_DATA"
    HTML_WITH_TEXT = "HTML_WITH_TEXT"

    # OCR needed
    IMAGE_FILE = "IMAGE_FILE"
    OFFICE_NO_TEXT = "OFFICE_NO_TEXT"
    PDF_SCANNED = "PDF_SCANNED"
    HTML_MINIMAL = "HTML_MINIMAL"
    UNKNOWN_BINARY = "UNKNOWN_BINARY"
    UNRECOGNIZED_TYPE = "UNRECOGNIZED_TYPE"

    # Page-level codes
    PDF_PAGE_DIGITAL = "PDF_PAGE_DIGITAL"
    PDF_PAGE_SCANNED = "PDF_PAGE_SCANNED"
    PDF_MIXED = "PDF_MIXED"

