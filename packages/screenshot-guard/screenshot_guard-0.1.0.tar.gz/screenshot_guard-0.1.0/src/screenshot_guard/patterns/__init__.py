"""Secret detection patterns."""

from screenshot_guard.patterns.base import SecretPattern, PatternMatch
from screenshot_guard.patterns.registry import PatternRegistry, get_all_patterns

__all__ = ["SecretPattern", "PatternMatch", "PatternRegistry", "get_all_patterns"]
