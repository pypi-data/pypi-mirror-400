"""PreOCR - A fast, CPU-only library that detects whether files need OCR processing."""

from .version import __version__
from .detector import needs_ocr
from .batch import BatchProcessor, BatchResults

__all__ = ["needs_ocr", "__version__", "BatchProcessor", "BatchResults"]
