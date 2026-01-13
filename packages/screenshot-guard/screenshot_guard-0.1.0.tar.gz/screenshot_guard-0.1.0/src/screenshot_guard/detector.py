"""Secret detection engine."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import logging

from screenshot_guard.patterns import SecretPattern, get_all_patterns

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """A secret finding in a file."""

    file_path: Path
    pattern_name: str
    severity: str
    provider: str
    line_number: int
    column: int
    matched_text: str
    context: str
    from_ocr: bool = False
    description: str = ""

    def redacted_match(self, visible_chars: int = 4) -> str:
        """Return match with middle characters redacted."""
        text = self.matched_text
        if len(text) <= visible_chars * 2:
            return "*" * len(text)
        return text[:visible_chars] + "*" * (len(text) - visible_chars * 2) + text[-visible_chars:]


class SecretDetector:
    """Detects secrets in text content using pattern matching."""

    def __init__(
        self,
        patterns: List[SecretPattern] | None = None,
        min_severity: str = "low",
    ) -> None:
        """Initialize the detector.

        Args:
            patterns: Optional list of patterns (defaults to all registered)
            min_severity: Minimum severity level to report
        """
        self.patterns = patterns or get_all_patterns()
        self.min_severity = min_severity
        self._severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}

    def detect(
        self,
        content: str,
        file_path: Path,
        from_ocr: bool = False,
    ) -> List[Finding]:
        """Detect secrets in text content.

        Args:
            content: Text content to scan
            file_path: Path to the source file
            from_ocr: Whether content came from OCR

        Returns:
            List of Finding objects
        """
        findings: List[Finding] = []
        lines = content.split("\n")

        for pattern in self.patterns:
            if not self._meets_severity(pattern.severity):
                continue

            for line_num, line in enumerate(lines, start=1):
                for match in pattern.pattern.finditer(line):
                    # Get the actual matched text (first group or whole match)
                    matched_text = match.group(1) if match.groups() else match.group(0)

                    # Skip very short matches (likely false positives)
                    if len(matched_text) < 8:
                        continue

                    finding = Finding(
                        file_path=file_path,
                        pattern_name=pattern.name,
                        severity=pattern.severity,
                        provider=pattern.provider,
                        line_number=line_num,
                        column=match.start() + 1,
                        matched_text=matched_text,
                        context=self._get_context(line, match.start(), match.end()),
                        from_ocr=from_ocr,
                        description=pattern.description,
                    )
                    findings.append(finding)
                    logger.debug(f"Found {pattern.name} in {file_path}:{line_num}")

        return findings

    def _meets_severity(self, severity: str) -> bool:
        """Check if severity meets minimum threshold."""
        return self._severity_levels.get(severity, 0) >= self._severity_levels.get(
            self.min_severity, 0
        )

    def _get_context(self, line: str, start: int, end: int, context_chars: int = 20) -> str:
        """Get surrounding context for a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(line), end + context_chars)

        prefix = "..." if ctx_start > 0 else ""
        suffix = "..." if ctx_end < len(line) else ""

        return prefix + line[ctx_start:ctx_end] + suffix

    def detect_file(self, file_path: Path) -> List[Finding]:
        """Detect secrets in a file.

        Args:
            file_path: Path to file to scan

        Returns:
            List of Finding objects
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return self.detect(content, file_path)
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return []


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of text.

    Higher entropy suggests random/secret data.
    """
    import math
    from collections import Counter

    if not text:
        return 0.0

    counter = Counter(text)
    length = len(text)
    entropy = 0.0

    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy


class EntropyDetector:
    """Detect high-entropy strings that may be secrets."""

    def __init__(
        self,
        min_entropy: float = 4.5,
        min_length: int = 20,
        max_length: int = 200,
    ) -> None:
        """Initialize entropy detector.

        Args:
            min_entropy: Minimum entropy threshold
            min_length: Minimum string length to check
            max_length: Maximum string length to check
        """
        self.min_entropy = min_entropy
        self.min_length = min_length
        self.max_length = max_length

        # Pattern to find potential secrets (alphanumeric strings)
        self.pattern = re.compile(r"[A-Za-z0-9+/=_-]{20,}")

    def detect(self, content: str, file_path: Path) -> List[Finding]:
        """Detect high-entropy strings.

        Args:
            content: Text to analyze
            file_path: Source file path

        Returns:
            List of potential secret findings
        """
        findings: List[Finding] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            for match in self.pattern.finditer(line):
                text = match.group(0)

                if len(text) < self.min_length or len(text) > self.max_length:
                    continue

                entropy = calculate_entropy(text)

                if entropy >= self.min_entropy:
                    finding = Finding(
                        file_path=file_path,
                        pattern_name="High Entropy String",
                        severity="medium",
                        provider="entropy",
                        line_number=line_num,
                        column=match.start() + 1,
                        matched_text=text,
                        context=line[max(0, match.start() - 10) : match.end() + 10],
                        description=f"High entropy string detected (entropy: {entropy:.2f})",
                    )
                    findings.append(finding)

        return findings
