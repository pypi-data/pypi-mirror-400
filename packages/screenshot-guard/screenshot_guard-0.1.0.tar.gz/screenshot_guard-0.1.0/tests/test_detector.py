"""Tests for the secret detector."""

import pytest
from pathlib import Path

from screenshot_guard.detector import SecretDetector, Finding


class TestSecretDetector:
    """Tests for SecretDetector class."""

    def test_detect_aws_access_key(self):
        """Test detection of AWS Access Key ID."""
        detector = SecretDetector()
        content = 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"'

        findings = detector.detect(content, Path("test.py"))

        assert len(findings) >= 1
        assert any(f.pattern_name == "AWS Access Key ID" for f in findings)

    def test_detect_github_pat(self):
        """Test detection of GitHub Personal Access Token."""
        detector = SecretDetector()
        content = 'token = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"'

        findings = detector.detect(content, Path("test.py"))

        assert len(findings) >= 1
        assert any(f.pattern_name == "GitHub Personal Access Token" for f in findings)

    def test_detect_private_key(self):
        """Test detection of RSA private key."""
        detector = SecretDetector()
        content = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAK...\n-----END RSA PRIVATE KEY-----"

        findings = detector.detect(content, Path("test.py"))

        assert len(findings) >= 1
        assert any("Private Key" in f.pattern_name for f in findings)

    def test_no_false_positives_on_clean_code(self, sample_code_clean):
        """Test that clean code produces no findings."""
        detector = SecretDetector()

        findings = detector.detect(sample_code_clean, Path("clean.py"))

        assert len(findings) == 0

    def test_severity_filtering(self, sample_code_with_secrets):
        """Test that severity filtering works."""
        detector_all = SecretDetector(min_severity="low")
        detector_critical = SecretDetector(min_severity="critical")

        findings_all = detector_all.detect(sample_code_with_secrets, Path("test.py"))
        findings_critical = detector_critical.detect(sample_code_with_secrets, Path("test.py"))

        assert len(findings_all) >= len(findings_critical)
        assert all(f.severity == "critical" for f in findings_critical)

    def test_finding_redaction(self):
        """Test that matched text is properly redacted."""
        finding = Finding(
            file_path=Path("test.py"),
            pattern_name="Test",
            severity="high",
            provider="test",
            line_number=1,
            column=1,
            matched_text="AKIAIOSFODNN7EXAMPLE",
            context="",
        )

        redacted = finding.redacted_match()

        assert redacted.startswith("AKIA")
        assert redacted.endswith("MPLE")
        assert "*" in redacted
        assert len(redacted) == len(finding.matched_text)

    def test_multiline_content(self):
        """Test detection across multiple lines."""
        detector = SecretDetector()
        content = """
line 1
line 2
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
line 4
"""
        findings = detector.detect(content, Path("test.py"))

        assert len(findings) >= 1
        assert findings[0].line_number == 4
