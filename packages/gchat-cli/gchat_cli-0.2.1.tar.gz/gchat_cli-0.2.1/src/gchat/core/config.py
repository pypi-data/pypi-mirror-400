"""Configuration management."""

import tomllib
from dataclasses import dataclass, field
from datetime import datetime

import tomli_w

from gchat.models.account import Account
from gchat.utils.paths import CONFIG_FILE, ensure_directories


@dataclass
class Config:
    """Application configuration."""

    active_account: str | None = None
    default_format: str = "table"
    color_output: bool = True
    accounts: dict[str, Account] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Config":
        """Load config from ~/.gchat/config.toml."""
        ensure_directories()

        if not CONFIG_FILE.exists():
            return cls()

        with open(CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)

        general = data.get("general", {})
        accounts_data = data.get("accounts", {})

        accounts = {
            name: Account.from_dict(name, acc_data)
            for name, acc_data in accounts_data.items()
        }

        return cls(
            active_account=general.get("active_account"),
            default_format=general.get("default_format", "table"),
            color_output=general.get("color_output", True),
            accounts=accounts,
        )

    def save(self) -> None:
        """Save config to disk."""
        ensure_directories()

        data = {
            "general": {
                "active_account": self.active_account,
                "default_format": self.default_format,
                "color_output": self.color_output,
            },
            "accounts": {name: acc.to_dict() for name, acc in self.accounts.items()},
        }

        with open(CONFIG_FILE, "wb") as f:
            tomli_w.dump(data, f)

    def set_active_account(self, name: str) -> None:
        """Set the active account and save."""
        self.active_account = name
        if name in self.accounts:
            self.accounts[name].last_used = datetime.now()
        self.save()

    def add_account(self, account: Account) -> None:
        """Add an account to the config."""
        self.accounts[account.name] = account
        if self.active_account is None:
            self.active_account = account.name
        self.save()

    def remove_account(self, name: str) -> None:
        """Remove an account from the config."""
        if name in self.accounts:
            del self.accounts[name]
        if self.active_account == name:
            # Set to first available or None
            self.active_account = next(iter(self.accounts.keys()), None)
        self.save()

    def get_active_account(self) -> Account | None:
        """Get the currently active account."""
        if self.active_account and self.active_account in self.accounts:
            return self.accounts[self.active_account]
        return None
