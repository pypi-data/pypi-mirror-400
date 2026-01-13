"""File scanner for secret detection."""

from pathlib import Path
from typing import List, Set, Callable, Optional
import logging
import fnmatch

from screenshot_guard.detector import SecretDetector, Finding
from screenshot_guard.ocr import OCREngine

logger = logging.getLogger(__name__)

# Default patterns to ignore
DEFAULT_IGNORE_PATTERNS = {
    # Directories
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env",
    "env",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "*.egg-info",
    # Files
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.dll",
    "*.exe",
    "*.bin",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "Cargo.lock",
    "poetry.lock",
}

# Text file extensions to scan
TEXT_EXTENSIONS = {
    # Code
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".kt", ".scala",
    ".go", ".rs", ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php",
    ".swift", ".m", ".mm", ".sh", ".bash", ".zsh", ".fish", ".ps1",
    ".pl", ".pm", ".lua", ".r", ".R", ".jl", ".ex", ".exs", ".erl",
    ".hs", ".ml", ".fs", ".clj", ".cljs", ".elm", ".dart", ".v",
    # Config
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".env", ".envrc", ".properties", ".xml", ".plist",
    # Docs/Data
    ".md", ".rst", ".txt", ".csv", ".sql", ".graphql",
    # Web
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    # Other
    ".tf", ".hcl", ".dockerfile", ".dockerignore", ".gitignore",
    ".editorconfig", ".prettierrc", ".eslintrc",
}


class Scanner:
    """Scans files and directories for secrets."""

    def __init__(
        self,
        detector: SecretDetector | None = None,
        ocr_engine: OCREngine | None = None,
        ignore_patterns: Set[str] | None = None,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> None:
        """Initialize scanner.

        Args:
            detector: Secret detector instance
            ocr_engine: Optional OCR engine for image scanning
            ignore_patterns: Patterns to ignore (defaults to common patterns)
            progress_callback: Optional callback for progress updates
        """
        self.detector = detector or SecretDetector()
        self.ocr_engine = ocr_engine
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        self.progress_callback = progress_callback
        self._files_scanned = 0
        self._total_files = 0

    def scan(self, path: Path) -> List[Finding]:
        """Scan a file or directory for secrets.

        Args:
            path: Path to file or directory

        Returns:
            List of findings
        """
        path = Path(path).resolve()

        if path.is_file():
            return self._scan_file(path)
        elif path.is_dir():
            return self._scan_directory(path)
        else:
            logger.warning(f"Path does not exist: {path}")
            return []

    def _scan_directory(self, directory: Path) -> List[Finding]:
        """Scan all files in a directory."""
        findings: List[Finding] = []

        # Collect all files first
        files_to_scan = list(self._collect_files(directory))
        self._total_files = len(files_to_scan)
        self._files_scanned = 0

        logger.info(f"Scanning {self._total_files} files in {directory}")

        for file_path in files_to_scan:
            file_findings = self._scan_file(file_path)
            findings.extend(file_findings)

            self._files_scanned += 1
            if self.progress_callback:
                self.progress_callback(
                    str(file_path), self._files_scanned, self._total_files
                )

        return findings

    def _collect_files(self, directory: Path):
        """Collect all scannable files in directory."""
        for item in directory.rglob("*"):
            if item.is_file() and self._should_scan(item):
                yield item

    def _should_scan(self, path: Path) -> bool:
        """Check if a file should be scanned."""
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return False
            # Check if any parent matches directory patterns
            for parent in path.parents:
                if fnmatch.fnmatch(parent.name, pattern):
                    return False

        return True

    def _scan_file(self, file_path: Path) -> List[Finding]:
        """Scan a single file for secrets."""
        findings: List[Finding] = []

        # Check if it's an image (for OCR)
        if self.ocr_engine and self.ocr_engine.supports_file(file_path):
            ocr_findings = self._scan_image(file_path)
            findings.extend(ocr_findings)
            return findings

        # Check if it's a text file
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            # Try to detect if it's a text file anyway
            if not self._is_text_file(file_path):
                return findings

        # Scan text content
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            file_findings = self.detector.detect(content, file_path)
            findings.extend(file_findings)

        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")

        return findings

    def _scan_image(self, file_path: Path) -> List[Finding]:
        """Scan an image file using OCR."""
        if not self.ocr_engine:
            return []

        try:
            logger.debug(f"Running OCR on {file_path}")
            text = self.ocr_engine.extract_text(file_path)

            if text:
                findings = self.detector.detect(text, file_path, from_ocr=True)
                if findings:
                    logger.info(f"Found {len(findings)} secrets in image {file_path}")
                return findings

        except Exception as e:
            logger.warning(f"OCR failed for {file_path}: {e}")

        return []

    def _is_text_file(self, path: Path, sample_size: int = 8192) -> bool:
        """Check if a file appears to be text."""
        try:
            with open(path, "rb") as f:
                sample = f.read(sample_size)

            # Check for null bytes (binary indicator)
            if b"\x00" in sample:
                return False

            # Try to decode as UTF-8
            try:
                sample.decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False

        except Exception:
            return False

    @property
    def stats(self) -> dict:
        """Get scanning statistics."""
        return {
            "files_scanned": self._files_scanned,
            "total_files": self._total_files,
        }
