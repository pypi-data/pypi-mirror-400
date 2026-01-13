"""AWS secret patterns."""

import re
from screenshot_guard.patterns.base import SecretPattern

AWS_PATTERNS = [
    SecretPattern(
        name="AWS Access Key ID",
        pattern=re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        severity="critical",
        description="AWS Access Key ID - can provide full AWS account access",
        provider="aws",
    ),
    SecretPattern(
        name="AWS Secret Access Key",
        pattern=re.compile(r"(?i)aws[_\-\.]?secret[_\-\.]?(?:access[_\-\.]?)?key['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"),
        severity="critical",
        description="AWS Secret Access Key - together with Access Key enables full access",
        provider="aws",
    ),
    SecretPattern(
        name="AWS Session Token",
        pattern=re.compile(r"(?i)aws[_\-\.]?session[_\-\.]?token['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{100,})['\"]?"),
        severity="high",
        description="Temporary AWS session token",
        provider="aws",
    ),
    SecretPattern(
        name="AWS Account ID",
        pattern=re.compile(r"(?i)(?:aws[_\-\.]?)?account[_\-\.]?id['\"]?\s*[:=]\s*['\"]?(\d{12})['\"]?"),
        severity="medium",
        description="AWS Account ID - useful for targeted attacks",
        provider="aws",
    ),
    SecretPattern(
        name="AWS MWS Auth Token",
        pattern=re.compile(r"amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
        severity="high",
        description="Amazon Marketplace Web Service authentication token",
        provider="aws",
    ),
]
