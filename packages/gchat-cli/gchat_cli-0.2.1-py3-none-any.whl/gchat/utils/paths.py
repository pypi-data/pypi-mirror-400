"""Path constants for gchat configuration."""

from pathlib import Path

# Base configuration directory
GCHAT_DIR = Path.home() / ".gchat"

# Subdirectories
ACCOUNTS_DIR = GCHAT_DIR / "accounts"
CACHE_DIR = GCHAT_DIR / "cache"

# Main config file
CONFIG_FILE = GCHAT_DIR / "config.toml"


def get_account_dir(account_name: str) -> Path:
    """Get the directory for a specific account."""
    return ACCOUNTS_DIR / account_name


def get_credentials_file(account_name: str) -> Path:
    """Get the credentials.json path for an account."""
    return get_account_dir(account_name) / "credentials.json"


def get_token_file(account_name: str) -> Path:
    """Get the token.json path for an account."""
    return get_account_dir(account_name) / "token.json"


def ensure_directories() -> None:
    """Create all necessary directories if they don't exist."""
    GCHAT_DIR.mkdir(exist_ok=True)
    ACCOUNTS_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
