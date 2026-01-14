"""Main CLI application."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

from gchat import __version__
from gchat.cli import account, messages, search, spaces
from gchat.core.accounts import AccountManager
from gchat.ui import prompts
from gchat.ui.console import console, print_error, print_info, print_success
from gchat.utils.errors import GChatError, NoActiveAccountError
from gchat.utils.paths import GCHAT_DIR

app = typer.Typer(
    name="gchat",
    help="Google Chat CLI - Send messages from the command line",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(account.app, name="account", help="Manage accounts")
app.add_typer(spaces.app, name="spaces", help="Browse spaces and rooms")

# Add message commands directly to root
app.command("send")(messages.send_message)
app.command("read")(messages.read_messages)
app.command("search")(search.search_messages)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"gchat version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Google Chat CLI - Send messages from the command line."""
    pass


@app.command()
def init() -> None:
    """First-time setup wizard."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]Welcome to gchat![/bold cyan]\n\n"
            "This wizard will help you set up your first Google Chat account.",
            border_style="cyan",
        )
    )
    console.print()

    manager = AccountManager()
    existing = manager.list_accounts()

    if existing:
        print_info(f"You have {len(existing)} account(s) configured already.")
        if not prompts.prompt_confirm("Would you like to add another account?"):
            console.print("Run [bold]gchat account list[/bold] to see your accounts.")
            return

    # Show setup instructions
    console.print(
        Panel(
            "[bold]Before you begin, you'll need:[/bold]\n\n"
            "1. A Google Cloud project with the Chat API enabled\n"
            "2. OAuth 2.0 credentials (Desktop app type)\n\n"
            "[bold]To get credentials:[/bold]\n"
            "1. Go to [link]https://console.cloud.google.com/apis/credentials[/link]\n"
            "2. Click 'Create Credentials' → 'OAuth client ID'\n"
            "3. Select 'Desktop app' as the application type\n"
            "4. Download the JSON file",
            title="Setup Requirements",
            border_style="yellow",
        )
    )
    console.print()

    if not prompts.prompt_continue_setup():
        console.print("Run [bold]gchat init[/bold] when you're ready to set up.")
        return

    # Get account name
    existing_names = [a.name for a in existing]
    name = prompts.prompt_account_name(existing_names)
    if name is None:
        raise typer.Abort()

    # Get credentials path
    creds_path = prompts.prompt_credentials_path()
    if creds_path is None:
        raise typer.Abort()

    try:
        print_info(f"Setting up account '{name}'...")
        account_obj = manager.add_account(name, Path(creds_path).expanduser())
        console.print()
        print_success(f"Account '{account_obj.name}' is now set up and active!")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  • [cyan]gchat spaces list[/cyan] - See your spaces")
        console.print("  • [cyan]gchat send -i[/cyan] - Send a message interactively")
        console.print("  • [cyan]gchat --help[/cyan] - See all commands")
    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)


@app.command()
def status(
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
) -> None:
    """Show current status and account info."""
    manager = AccountManager()

    try:
        account_obj = manager.get_active_account()
        auth = manager.get_auth_manager(account_obj.name)
        authenticated = auth.is_authenticated()

        if format == "json":
            data = {
                "active_account": account_obj.name,
                "email": account_obj.email,
                "authenticated": authenticated,
                "config_dir": str(GCHAT_DIR),
                "total_accounts": len(manager.list_accounts()),
            }
            console.print_json(json.dumps(data))
        else:
            console.print(f"[bold]Active account:[/bold] [account]{account_obj.name}[/account]")
            if account_obj.email:
                console.print(f"[bold]Email:[/bold] {account_obj.email}")
            console.print(
                f"[bold]Authenticated:[/bold] "
                f"{'[green]Yes[/green]' if authenticated else '[red]No[/red]'}"
            )
            console.print(f"[bold]Config directory:[/bold] {GCHAT_DIR}")
            console.print(f"[bold]Total accounts:[/bold] {len(manager.list_accounts())}")

    except NoActiveAccountError:
        if format == "json":
            data = {
                "active_account": None,
                "authenticated": False,
                "config_dir": str(GCHAT_DIR),
                "total_accounts": len(manager.list_accounts()),
            }
            console.print_json(json.dumps(data))
        else:
            print_info("No active account configured.")
            console.print("Run [bold]gchat init[/bold] to set up an account.")


if __name__ == "__main__":
    app()
