"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_code_with_secrets() -> str:
    """Sample code containing various secrets for testing."""
    return '''
# AWS credentials (test values)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# GitHub token
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Generic API key
api_key = "sk_live_1234567890abcdefghijklmnop"

# Database URL
DATABASE_URL = "postgres://user:password123@localhost:5432/mydb"

# Private key
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn...
-----END RSA PRIVATE KEY-----
'''


@pytest.fixture
def sample_code_clean() -> str:
    """Sample code without any secrets."""
    return '''
# Configuration
DEBUG = True
PORT = 8080
HOST = "0.0.0.0"

def hello():
    return "Hello, World!"
'''
