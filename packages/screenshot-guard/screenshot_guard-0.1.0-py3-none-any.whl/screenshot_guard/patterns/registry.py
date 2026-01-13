"""Pattern registry for managing all secret patterns."""

from typing import List, Dict, Set
from screenshot_guard.patterns.base import SecretPattern
from screenshot_guard.patterns.aws import AWS_PATTERNS
from screenshot_guard.patterns.azure import AZURE_PATTERNS
from screenshot_guard.patterns.gcp import GCP_PATTERNS
from screenshot_guard.patterns.github import GITHUB_PATTERNS
from screenshot_guard.patterns.generic import GENERIC_PATTERNS


class PatternRegistry:
    """Registry for managing secret detection patterns."""

    def __init__(self) -> None:
        self._patterns: Dict[str, List[SecretPattern]] = {
            "aws": AWS_PATTERNS,
            "azure": AZURE_PATTERNS,
            "gcp": GCP_PATTERNS,
            "github": GITHUB_PATTERNS,
            "generic": GENERIC_PATTERNS,
        }
        self._enabled_providers: Set[str] = set(self._patterns.keys())

    def get_patterns(self, providers: List[str] | None = None) -> List[SecretPattern]:
        """Get all patterns, optionally filtered by provider.

        Args:
            providers: Optional list of providers to include

        Returns:
            List of SecretPattern objects
        """
        if providers is None:
            providers = list(self._enabled_providers)

        patterns = []
        for provider in providers:
            if provider in self._patterns:
                patterns.extend(self._patterns[provider])
        return patterns

    def get_pattern_by_name(self, name: str) -> SecretPattern | None:
        """Get a specific pattern by name."""
        for patterns in self._patterns.values():
            for pattern in patterns:
                if pattern.name == name:
                    return pattern
        return None

    def enable_provider(self, provider: str) -> None:
        """Enable a provider for pattern matching."""
        if provider in self._patterns:
            self._enabled_providers.add(provider)

    def disable_provider(self, provider: str) -> None:
        """Disable a provider from pattern matching."""
        self._enabled_providers.discard(provider)

    @property
    def providers(self) -> List[str]:
        """Get list of all available providers."""
        return list(self._patterns.keys())

    @property
    def enabled_providers(self) -> List[str]:
        """Get list of enabled providers."""
        return list(self._enabled_providers)

    def add_custom_pattern(self, pattern: SecretPattern) -> None:
        """Add a custom pattern to the registry."""
        provider = pattern.provider
        if provider not in self._patterns:
            self._patterns[provider] = []
            self._enabled_providers.add(provider)
        self._patterns[provider].append(pattern)

    def get_stats(self) -> Dict[str, int]:
        """Get pattern counts per provider."""
        return {provider: len(patterns) for provider, patterns in self._patterns.items()}


# Global registry instance
_registry = PatternRegistry()


def get_all_patterns() -> List[SecretPattern]:
    """Get all registered patterns."""
    return _registry.get_patterns()


def get_registry() -> PatternRegistry:
    """Get the global pattern registry."""
    return _registry
