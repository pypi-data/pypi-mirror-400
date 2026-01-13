"""Google Cloud Platform secret patterns."""

import re
from screenshot_guard.patterns.base import SecretPattern

GCP_PATTERNS = [
    SecretPattern(
        name="GCP API Key",
        pattern=re.compile(r"AIza[0-9A-Za-z_-]{35}"),
        severity="high",
        description="Google Cloud Platform API key",
        provider="gcp",
    ),
    SecretPattern(
        name="GCP Service Account",
        pattern=re.compile(r'"type"\s*:\s*"service_account"'),
        severity="critical",
        description="GCP Service Account JSON key file",
        provider="gcp",
    ),
    SecretPattern(
        name="GCP Private Key ID",
        pattern=re.compile(r'"private_key_id"\s*:\s*"([a-f0-9]{40})"'),
        severity="high",
        description="GCP Service Account private key ID",
        provider="gcp",
    ),
    SecretPattern(
        name="GCP OAuth Client Secret",
        pattern=re.compile(r"(?i)client[_\-\.]?secret['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]{24})['\"]?"),
        severity="high",
        description="Google OAuth client secret",
        provider="gcp",
    ),
    SecretPattern(
        name="Firebase Database URL",
        pattern=re.compile(r"https://[a-z0-9-]+\.firebaseio\.com"),
        severity="medium",
        description="Firebase Realtime Database URL",
        provider="gcp",
    ),
]
