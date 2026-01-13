"""Screenshot Guard - Secret Scanner with OCR Superpowers."""

__version__ = "0.1.0"

from screenshot_guard.scanner import Scanner
from screenshot_guard.detector import SecretDetector, Finding
from screenshot_guard.ocr import OCREngine

__all__ = ["Scanner", "SecretDetector", "Finding", "OCREngine", "__version__"]
