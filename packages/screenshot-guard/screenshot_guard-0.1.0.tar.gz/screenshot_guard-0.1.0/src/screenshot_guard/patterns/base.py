"""Base classes for secret patterns."""

import re
from dataclasses import dataclass
from typing import Pattern, Optional


@dataclass(frozen=True)
class SecretPattern:
    """Definition of a secret detection pattern."""

    name: str
    pattern: Pattern[str]
    severity: str  # critical, high, medium, low
    description: str
    provider: str  # aws, azure, gcp, github, generic, etc.

    def __post_init__(self) -> None:
        if self.severity not in ("critical", "high", "medium", "low"):
            raise ValueError(f"Invalid severity: {self.severity}")


@dataclass
class PatternMatch:
    """A matched secret pattern."""

    pattern: SecretPattern
    matched_text: str
    line_number: int
    column: int
    context: str  # surrounding text for context

    @property
    def name(self) -> str:
        return self.pattern.name

    @property
    def severity(self) -> str:
        return self.pattern.severity

    @property
    def provider(self) -> str:
        return self.pattern.provider

    def redacted_match(self, visible_chars: int = 4) -> str:
        """Return match with middle characters redacted."""
        if len(self.matched_text) <= visible_chars * 2:
            return "*" * len(self.matched_text)
        return (
            self.matched_text[:visible_chars]
            + "*" * (len(self.matched_text) - visible_chars * 2)
            + self.matched_text[-visible_chars:]
        )
