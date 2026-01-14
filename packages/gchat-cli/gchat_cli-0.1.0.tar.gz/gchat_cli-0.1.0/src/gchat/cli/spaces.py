"""Spaces commands."""

import json
from typing import Annotated

import typer

from gchat.core.accounts import AccountManager
from gchat.ui.console import console, print_error, print_info
from gchat.ui.tables import format_spaces_table
from gchat.utils.errors import GChatError

app = typer.Typer(help="Browse Google Chat spaces")


@app.command("list")
def list_spaces(
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
    account: Annotated[str | None, typer.Option("--account", "-a", help="Account to use")] = None,
) -> None:
    """List all spaces you're a member of."""
    manager = AccountManager()

    try:
        client = manager.get_client(account)
        spaces = client.list_spaces()

        if not spaces:
            print_info("No spaces found. You may not be a member of any spaces.")
            return

        if format == "json":
            data = [
                {
                    "id": s.name,
                    "name": s.display_name,
                    "type": s.space_type.value,
                    "members": s.member_count,
                }
                for s in spaces
            ]
            console.print_json(json.dumps(data))
        else:
            table = format_spaces_table(spaces)
            console.print(table)

    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)


@app.command("info")
def space_info(
    space_id: Annotated[str, typer.Argument(help="Space ID")],
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
    account: Annotated[str | None, typer.Option("--account", "-a", help="Account to use")] = None,
) -> None:
    """Get details about a specific space."""
    manager = AccountManager()

    try:
        client = manager.get_client(account)
        space = client.get_space(space_id)

        if format == "json":
            data = {
                "id": space.name,
                "name": space.display_name,
                "type": space.space_type.value,
                "members": space.member_count,
            }
            console.print_json(json.dumps(data))
        else:
            console.print(f"[bold]Space:[/bold] {space.display_name}")
            console.print(f"[bold]ID:[/bold] {space.name}")
            console.print(f"[bold]Type:[/bold] {space.space_type.value}")
            if space.member_count:
                console.print(f"[bold]Members:[/bold] {space.member_count}")

    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)
