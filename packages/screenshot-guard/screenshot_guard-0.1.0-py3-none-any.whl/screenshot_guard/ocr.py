"""German-OCR powered screenshot text extraction."""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".tif"}


class OCREngine:
    """German-OCR powered screenshot text extraction.

    Supports multiple backends:
    - llamacpp: Local inference with llama.cpp (default)
    - ollama: Local inference via Ollama
    - cloud: Remote API at app.german-ocr.de
    """

    def __init__(
        self,
        backend: str = "llamacpp",
        model_path: Optional[str] = None,
    ):
        """Initialize OCR Engine.

        Args:
            backend: OCR backend to use ('llamacpp', 'ollama', 'cloud')
            model_path: Optional custom model path for llamacpp
        """
        self.backend = backend
        self.model_path = model_path
        self._ocr = None
        self._initialized = False

    def _lazy_init(self) -> None:
        """Lazy initialization - only load model when first needed."""
        if self._initialized:
            return

        try:
            from german_ocr import GermanOCR

            kwargs = {"backend": self.backend}
            if self.model_path:
                kwargs["model_path"] = self.model_path

            self._ocr = GermanOCR(**kwargs)
            self._initialized = True
            logger.info(f"OCR Engine initialized with {self.backend} backend")

        except ImportError as e:
            raise ImportError(
                f"german-ocr not installed for {self.backend} backend. "
                f"Run: pip install german-ocr[{self.backend}]"
            ) from e

    def extract_text(self, image_path: Path) -> str:
        """Extract text from image using german-ocr.

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text from the image
        """
        self._lazy_init()

        if not self.supports_file(image_path):
            logger.warning(f"Unsupported file type: {image_path.suffix}")
            return ""

        try:
            result = self._ocr.extract(str(image_path))
            char_count = len(result) if result else 0
            logger.debug(f"Extracted {char_count} chars from {image_path.name}")
            return result or ""

        except Exception as e:
            logger.warning(f"OCR failed for {image_path}: {e}")
            return ""

    def supports_file(self, path: Path) -> bool:
        """Check if file type is supported for OCR.

        Args:
            path: Path to check

        Returns:
            True if file extension is supported
        """
        return path.suffix.lower() in SUPPORTED_EXTENSIONS

    @property
    def is_available(self) -> bool:
        """Check if OCR engine is available."""
        try:
            self._lazy_init()
            return True
        except ImportError:
            return False
