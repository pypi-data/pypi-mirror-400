"""Account management."""

import shutil
from datetime import datetime
from pathlib import Path

from gchat.core.auth import AuthManager
from gchat.core.client import ChatClient
from gchat.core.config import Config
from gchat.models.account import Account
from gchat.utils.errors import AccountNotFoundError, NoActiveAccountError
from gchat.utils.paths import get_account_dir


class AccountManager:
    """Manages multiple Google Chat accounts."""

    def __init__(self):
        self.config = Config.load()

    def add_account(self, name: str, credentials_path: Path | str) -> Account:
        """Add a new account with OAuth flow."""
        # Set up the auth manager and credentials
        auth = AuthManager(name)
        auth.setup_credentials_file(credentials_path)

        # Run OAuth flow
        auth.authenticate()

        # Create account record
        account = Account(
            name=name,
            email=None,  # Could extract from token info if needed
            created_at=datetime.now(),
            last_used=datetime.now(),
        )

        # Try to get email from user info
        try:
            # The email might be available in the credentials
            pass  # TODO: Extract email if possible
        except Exception:
            pass

        # Save to config
        self.config.add_account(account)

        return account

    def remove_account(self, name: str) -> None:
        """Remove an account and its credentials."""
        if name not in self.config.accounts:
            raise AccountNotFoundError(f"Account '{name}' not found")

        # Remove account directory
        account_dir = get_account_dir(name)
        if account_dir.exists():
            shutil.rmtree(account_dir)

        # Remove from config
        self.config.remove_account(name)

    def list_accounts(self) -> list[Account]:
        """List all configured accounts."""
        return list(self.config.accounts.values())

    def switch_account(self, name: str) -> None:
        """Switch the active account."""
        if name not in self.config.accounts:
            raise AccountNotFoundError(f"Account '{name}' not found")

        self.config.set_active_account(name)

    def get_active_account(self) -> Account:
        """Get the currently active account."""
        account = self.config.get_active_account()
        if not account:
            raise NoActiveAccountError(
                "No active account. Run 'gchat init' or 'gchat account add' to set up an account."
            )
        return account

    def get_client(self, account_name: str | None = None) -> ChatClient:
        """Get authenticated client for an account."""
        if account_name is None:
            account = self.get_active_account()
            account_name = account.name

        if account_name not in self.config.accounts:
            raise AccountNotFoundError(f"Account '{account_name}' not found")

        # Update last used
        self.config.accounts[account_name].last_used = datetime.now()
        self.config.save()

        auth = AuthManager(account_name)
        creds = auth.get_credentials()

        return ChatClient(creds)

    def get_auth_manager(self, account_name: str) -> AuthManager:
        """Get auth manager for an account."""
        return AuthManager(account_name)
