"""Custom exceptions for PreOCR library."""


class PreOCRError(Exception):
    """Base exception for all PreOCR errors."""

    pass


class FileTypeDetectionError(PreOCRError):
    """Raised when file type detection fails."""

    pass


class TextExtractionError(PreOCRError):
    """Raised when text extraction fails."""

    pass


class LayoutAnalysisError(PreOCRError):
    """Raised when layout analysis fails."""

    pass


class PDFProcessingError(PreOCRError):
    """Raised when PDF processing fails."""

    pass


class OfficeDocumentError(PreOCRError):
    """Raised when Office document processing fails."""

    pass


class ImageProcessingError(PreOCRError):
    """Raised when image processing fails."""

    pass
