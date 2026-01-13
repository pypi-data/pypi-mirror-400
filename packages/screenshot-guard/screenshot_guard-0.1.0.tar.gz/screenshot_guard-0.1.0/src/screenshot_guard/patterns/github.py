"""GitHub secret patterns."""

import re
from screenshot_guard.patterns.base import SecretPattern

GITHUB_PATTERNS = [
    SecretPattern(
        name="GitHub Personal Access Token",
        pattern=re.compile(r"ghp_[A-Za-z0-9]{36}"),
        severity="critical",
        description="GitHub Personal Access Token (classic)",
        provider="github",
    ),
    SecretPattern(
        name="GitHub Fine-Grained PAT",
        pattern=re.compile(r"github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}"),
        severity="critical",
        description="GitHub Fine-Grained Personal Access Token",
        provider="github",
    ),
    SecretPattern(
        name="GitHub OAuth Access Token",
        pattern=re.compile(r"gho_[A-Za-z0-9]{36}"),
        severity="critical",
        description="GitHub OAuth Access Token",
        provider="github",
    ),
    SecretPattern(
        name="GitHub App Token",
        pattern=re.compile(r"(?:ghu|ghs)_[A-Za-z0-9]{36}"),
        severity="critical",
        description="GitHub App user-to-server or server-to-server token",
        provider="github",
    ),
    SecretPattern(
        name="GitHub Refresh Token",
        pattern=re.compile(r"ghr_[A-Za-z0-9]{36}"),
        severity="high",
        description="GitHub OAuth refresh token",
        provider="github",
    ),
    SecretPattern(
        name="GitHub App Private Key",
        pattern=re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
        severity="critical",
        description="GitHub App private key (RSA)",
        provider="github",
    ),
]
