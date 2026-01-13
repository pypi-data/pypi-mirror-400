"""Azure secret patterns."""

import re
from screenshot_guard.patterns.base import SecretPattern

AZURE_PATTERNS = [
    SecretPattern(
        name="Azure Storage Account Key",
        pattern=re.compile(r"(?i)(?:DefaultEndpointsProtocol|AccountKey)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9+/=]{88})['\"]?"),
        severity="critical",
        description="Azure Storage Account access key",
        provider="azure",
    ),
    SecretPattern(
        name="Azure Connection String",
        pattern=re.compile(r"DefaultEndpointsProtocol=https?;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88}"),
        severity="critical",
        description="Full Azure Storage connection string",
        provider="azure",
    ),
    SecretPattern(
        name="Azure SAS Token",
        pattern=re.compile(r"[?&]sig=[A-Za-z0-9%]+(&|$)"),
        severity="high",
        description="Azure Shared Access Signature token",
        provider="azure",
    ),
    SecretPattern(
        name="Azure Service Principal",
        pattern=re.compile(r"(?i)azure[_\-\.]?(?:client[_\-\.]?)?secret['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9~._-]{34,})['\"]?"),
        severity="critical",
        description="Azure Service Principal secret",
        provider="azure",
    ),
    SecretPattern(
        name="Azure Subscription ID",
        pattern=re.compile(r"(?i)subscription[_\-\.]?id['\"]?\s*[:=]\s*['\"]?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})['\"]?"),
        severity="medium",
        description="Azure Subscription ID",
        provider="azure",
    ),
]
