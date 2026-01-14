"""Interactive prompts using questionary."""

from pathlib import Path

import questionary
from questionary import Style

from gchat.models.account import Account
from gchat.models.space import Space

# Custom style for prompts
GCHAT_STYLE = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "bold"),
        ("answer", "fg:green"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:green"),
    ]
)


def prompt_account_name(existing_names: list[str] | None = None) -> str | None:
    """Prompt for account name."""
    existing = existing_names or []

    def validate(text: str) -> bool | str:
        if not text.strip():
            return "Account name cannot be empty"
        if text in existing:
            return f"Account '{text}' already exists"
        if not text.isalnum() and "-" not in text and "_" not in text:
            return "Account name can only contain letters, numbers, hyphens, and underscores"
        return True

    return questionary.text(
        "Enter a name for this account:",
        validate=validate,
        style=GCHAT_STYLE,
    ).ask()


def prompt_credentials_path() -> str | None:
    """Prompt for credentials.json path."""

    def validate(text: str) -> bool | str:
        path = Path(text).expanduser()
        if not path.exists():
            return f"File not found: {path}"
        if not path.suffix == ".json":
            return "File must be a .json file"
        return True

    return questionary.path(
        "Path to credentials.json from Google Cloud Console:",
        validate=validate,
        style=GCHAT_STYLE,
    ).ask()


def prompt_select_account(accounts: list[Account]) -> Account | None:
    """Prompt to select an account."""
    if not accounts:
        return None

    choices = [questionary.Choice(title=acc.name, value=acc) for acc in accounts]

    return questionary.select(
        "Select an account:",
        choices=choices,
        style=GCHAT_STYLE,
    ).ask()


def prompt_select_space(spaces: list[Space]) -> Space | None:
    """Prompt to select a space."""
    if not spaces:
        return None

    choices = [
        questionary.Choice(
            title=f"{s.display_name} ({s.space_type.value})",
            value=s,
        )
        for s in spaces
    ]

    return questionary.select(
        "Select a space:",
        choices=choices,
        style=GCHAT_STYLE,
    ).ask()


def prompt_message() -> str | None:
    """Prompt for message text."""
    return questionary.text(
        "Enter your message:",
        multiline=False,
        style=GCHAT_STYLE,
    ).ask()


def prompt_confirm(message: str, default: bool = True) -> bool:
    """Prompt for confirmation."""
    result = questionary.confirm(
        message,
        default=default,
        style=GCHAT_STYLE,
    ).ask()
    return result if result is not None else False


def prompt_continue_setup() -> bool:
    """Ask if user wants to continue with setup."""
    return prompt_confirm("Would you like to set up an account now?", default=True)
