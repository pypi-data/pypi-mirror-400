"""Tests for the file scanner."""

import pytest
from pathlib import Path
import tempfile
import os

from screenshot_guard.scanner import Scanner, DEFAULT_IGNORE_PATTERNS


class TestScanner:
    """Tests for Scanner class."""

    def test_scan_file_with_secrets(self, tmp_path):
        """Test scanning a single file with secrets."""
        # Create test file
        test_file = tmp_path / "config.py"
        test_file.write_text('API_KEY = "AKIAIOSFODNN7EXAMPLE"')

        scanner = Scanner()
        findings = scanner.scan(test_file)

        assert len(findings) >= 1
        assert findings[0].file_path == test_file

    def test_scan_clean_file(self, tmp_path):
        """Test scanning a file without secrets."""
        test_file = tmp_path / "clean.py"
        test_file.write_text('DEBUG = True\nPORT = 8080')

        scanner = Scanner()
        findings = scanner.scan(test_file)

        assert len(findings) == 0

    def test_scan_directory(self, tmp_path):
        """Test scanning a directory."""
        # Create multiple files
        (tmp_path / "file1.py").write_text('x = 1')
        (tmp_path / "file2.py").write_text('API = "AKIAIOSFODNN7EXAMPLE"')
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.py").write_text('TOKEN = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"')

        scanner = Scanner()
        findings = scanner.scan(tmp_path)

        assert len(findings) >= 2  # At least AWS key and GitHub token

    def test_ignore_patterns(self, tmp_path):
        """Test that ignore patterns work."""
        # Create files that should be ignored
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "secret.js").write_text('KEY = "AKIAIOSFODNN7EXAMPLE"')

        # Create file that should be scanned
        (tmp_path / "app.py").write_text('KEY = "AKIAIOSFODNN7EXAMPLE"')

        scanner = Scanner()
        findings = scanner.scan(tmp_path)

        # Should only find the one in app.py, not in node_modules
        assert all("node_modules" not in str(f.file_path) for f in findings)

    def test_binary_files_skipped(self, tmp_path):
        """Test that binary files are skipped."""
        # Create a binary file
        binary_file = tmp_path / "image.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03AKIAIOSFODNN7EXAMPLE')

        scanner = Scanner()
        findings = scanner.scan(binary_file)

        assert len(findings) == 0

    def test_scanner_stats(self, tmp_path):
        """Test that scanner stats are tracked."""
        (tmp_path / "file1.py").write_text('x = 1')
        (tmp_path / "file2.py").write_text('y = 2')

        scanner = Scanner()
        scanner.scan(tmp_path)

        assert scanner.stats["files_scanned"] == 2
        assert scanner.stats["total_files"] == 2


class TestIgnorePatterns:
    """Tests for default ignore patterns."""

    def test_git_ignored(self):
        assert ".git" in DEFAULT_IGNORE_PATTERNS

    def test_node_modules_ignored(self):
        assert "node_modules" in DEFAULT_IGNORE_PATTERNS

    def test_pycache_ignored(self):
        assert "__pycache__" in DEFAULT_IGNORE_PATTERNS

    def test_lock_files_ignored(self):
        assert "*.lock" in DEFAULT_IGNORE_PATTERNS
