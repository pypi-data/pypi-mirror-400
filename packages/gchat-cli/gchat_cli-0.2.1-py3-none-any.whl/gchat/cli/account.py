"""Account management commands."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

from gchat.core.accounts import AccountManager
from gchat.ui import prompts
from gchat.ui.console import console, print_error, print_info, print_success
from gchat.ui.tables import format_accounts_table
from gchat.utils.errors import AccountNotFoundError, GChatError

app = typer.Typer(help="Manage Google Chat accounts")


@app.command("add")
def add_account(
    name: Annotated[str | None, typer.Argument(help="Account name")] = None,
    credentials: Annotated[
        Path | None,
        typer.Option("--credentials", "-c", help="Path to credentials.json"),
    ] = None,
) -> None:
    """Add a new Google Chat account."""
    manager = AccountManager()
    existing_names = [a.name for a in manager.list_accounts()]

    # Get account name
    if name is None:
        name = prompts.prompt_account_name(existing_names)
        if name is None:
            raise typer.Abort()
    elif name in existing_names:
        print_error(f"Account '{name}' already exists")
        raise typer.Exit(1)

    # Get credentials path
    if credentials is None:
        console.print()
        console.print(
            Panel(
                "[bold]To authenticate, you need a credentials.json file "
                "from Google Cloud Console.[/bold]\n\n"
                "1. Go to [link]https://console.cloud.google.com/apis/credentials[/link]\n"
                "2. Create OAuth 2.0 Client ID (Desktop app)\n"
                "3. Download the JSON file",
                title="Setup Instructions",
                border_style="cyan",
            )
        )
        console.print()
        creds_path = prompts.prompt_credentials_path()
        if creds_path is None:
            raise typer.Abort()
        credentials = Path(creds_path).expanduser()

    try:
        print_info(f"Adding account '{name}'...")
        account = manager.add_account(name, credentials)
        print_success(f"Account '{account.name}' added and set as active")
    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)


@app.command("remove")
def remove_account(
    name: Annotated[str, typer.Argument(help="Account name to remove")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Remove a Google Chat account."""
    manager = AccountManager()

    try:
        if not force:
            if not prompts.prompt_confirm(f"Remove account '{name}'?", default=False):
                raise typer.Abort()

        manager.remove_account(name)
        print_success(f"Account '{name}' removed")
    except AccountNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)


@app.command("list")
def list_accounts(
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
) -> None:
    """List all configured accounts."""
    manager = AccountManager()
    accounts = manager.list_accounts()

    if not accounts:
        print_info("No accounts configured. Run 'gchat init' to set up an account.")
        return

    if format == "json":
        data = [
            {
                "name": a.name,
                "email": a.email,
                "active": a.name == manager.config.active_account,
                "last_used": a.last_used.isoformat() if a.last_used else None,
            }
            for a in accounts
        ]
        console.print_json(json.dumps(data))
    else:
        table = format_accounts_table(accounts, manager.config.active_account)
        console.print(table)


@app.command("switch")
def switch_account(
    name: Annotated[str | None, typer.Argument(help="Account name to switch to")] = None,
) -> None:
    """Switch the active account."""
    manager = AccountManager()
    accounts = manager.list_accounts()

    if not accounts:
        print_error("No accounts configured. Run 'gchat init' to set up an account.")
        raise typer.Exit(1)

    # If no name provided, prompt for selection
    if name is None:
        account = prompts.prompt_select_account(accounts)
        if account is None:
            raise typer.Abort()
        name = account.name

    try:
        manager.switch_account(name)
        print_success(f"Switched to account '{name}'")
    except AccountNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)


@app.command("current")
def current_account(
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
) -> None:
    """Show the current active account."""
    manager = AccountManager()

    try:
        account = manager.get_active_account()

        if format == "json":
            data = {
                "name": account.name,
                "email": account.email,
                "last_used": account.last_used.isoformat() if account.last_used else None,
            }
            console.print_json(json.dumps(data))
        else:
            console.print(f"Active account: [account]{account.name}[/account]")
            if account.email:
                console.print(f"Email: {account.email}")
    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)
