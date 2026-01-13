"""Generic secret patterns for common credentials."""

import re
from screenshot_guard.patterns.base import SecretPattern

GENERIC_PATTERNS = [
    # API Keys (generic)
    SecretPattern(
        name="Generic API Key",
        pattern=re.compile(r"(?i)(?:api[_\-\.]?key|apikey)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]{20,})['\"]?"),
        severity="high",
        description="Generic API key pattern",
        provider="generic",
    ),
    SecretPattern(
        name="Generic Secret Key",
        pattern=re.compile(r"(?i)(?:secret[_\-\.]?key|secretkey)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]{20,})['\"]?"),
        severity="high",
        description="Generic secret key pattern",
        provider="generic",
    ),
    SecretPattern(
        name="Generic Access Token",
        pattern=re.compile(r"(?i)(?:access[_\-\.]?token|accesstoken)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_.-]{20,})['\"]?"),
        severity="high",
        description="Generic access token",
        provider="generic",
    ),

    # Passwords
    SecretPattern(
        name="Password in URL",
        pattern=re.compile(r"(?i)(?:https?|ftp)://[^:]+:([^@]+)@"),
        severity="critical",
        description="Password embedded in URL",
        provider="generic",
    ),
    SecretPattern(
        name="Password Assignment",
        pattern=re.compile(r"(?i)(?:password|passwd|pwd)['\"]?\s*[:=]\s*['\"]([^'\"]{8,})['\"]"),
        severity="high",
        description="Hardcoded password",
        provider="generic",
    ),

    # Private Keys
    SecretPattern(
        name="RSA Private Key",
        pattern=re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
        severity="critical",
        description="RSA private key",
        provider="generic",
    ),
    SecretPattern(
        name="OpenSSH Private Key",
        pattern=re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"),
        severity="critical",
        description="OpenSSH private key",
        provider="generic",
    ),
    SecretPattern(
        name="PGP Private Key",
        pattern=re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----"),
        severity="critical",
        description="PGP private key block",
        provider="generic",
    ),

    # Database
    SecretPattern(
        name="Database Connection String",
        pattern=re.compile(r"(?i)(?:mongodb|postgres|mysql|redis)://[^:]+:[^@]+@[^\s]+"),
        severity="critical",
        description="Database connection string with credentials",
        provider="generic",
    ),

    # JWT
    SecretPattern(
        name="JWT Token",
        pattern=re.compile(r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"),
        severity="medium",
        description="JSON Web Token (may contain sensitive claims)",
        provider="generic",
    ),

    # Slack
    SecretPattern(
        name="Slack Bot Token",
        pattern=re.compile(r"xoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*"),
        severity="high",
        description="Slack Bot Token",
        provider="slack",
    ),
    SecretPattern(
        name="Slack Webhook URL",
        pattern=re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),
        severity="medium",
        description="Slack Webhook URL",
        provider="slack",
    ),

    # Stripe
    SecretPattern(
        name="Stripe Secret Key",
        pattern=re.compile(r"sk_live_[A-Za-z0-9]{24,}"),
        severity="critical",
        description="Stripe live secret key",
        provider="stripe",
    ),
    SecretPattern(
        name="Stripe Restricted Key",
        pattern=re.compile(r"rk_live_[A-Za-z0-9]{24,}"),
        severity="high",
        description="Stripe restricted API key",
        provider="stripe",
    ),

    # Twilio
    SecretPattern(
        name="Twilio API Key",
        pattern=re.compile(r"SK[0-9a-fA-F]{32}"),
        severity="high",
        description="Twilio API key",
        provider="twilio",
    ),

    # SendGrid
    SecretPattern(
        name="SendGrid API Key",
        pattern=re.compile(r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}"),
        severity="high",
        description="SendGrid API key",
        provider="sendgrid",
    ),

    # npm
    SecretPattern(
        name="npm Token",
        pattern=re.compile(r"npm_[A-Za-z0-9]{36}"),
        severity="high",
        description="npm access token",
        provider="npm",
    ),

    # Discord
    SecretPattern(
        name="Discord Bot Token",
        pattern=re.compile(r"[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27}"),
        severity="high",
        description="Discord bot token",
        provider="discord",
    ),
    SecretPattern(
        name="Discord Webhook",
        pattern=re.compile(r"https://discord(?:app)?\.com/api/webhooks/\d+/[\w-]+"),
        severity="medium",
        description="Discord webhook URL",
        provider="discord",
    ),
]
