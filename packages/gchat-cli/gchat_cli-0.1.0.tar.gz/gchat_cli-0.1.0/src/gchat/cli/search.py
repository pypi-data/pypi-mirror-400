"""Search commands."""

import json
from datetime import datetime
from typing import Annotated

import typer

from gchat.core.accounts import AccountManager
from gchat.ui.console import console, print_error, print_info
from gchat.ui.tables import format_messages_table
from gchat.utils.errors import GChatError

app = typer.Typer(help="Search messages")


@app.command("search")
def search_messages(
    space_id: Annotated[str, typer.Argument(help="Space ID to search in")],
    keyword: Annotated[str | None, typer.Argument(help="Keyword to search")] = None,
    sender: Annotated[str | None, typer.Option("--from")] = None,
    after: Annotated[str | None, typer.Option("--after", help="YYYY-MM-DD")] = None,
    before: Annotated[str | None, typer.Option("--before", help="YYYY-MM-DD")] = None,
    num: Annotated[int, typer.Option("-n", "--num")] = 25,
    account: Annotated[str | None, typer.Option("--account", "-a")] = None,
    format: Annotated[str, typer.Option("--format", "-f")] = "table",
) -> None:
    """Search messages in a space.

    Date filtering (--after, --before) is done server-side.
    Keyword and sender filtering is done client-side.
    """
    manager = AccountManager()

    # Parse dates
    after_dt = None
    before_dt = None

    if after:
        try:
            after_dt = datetime.fromisoformat(after)
        except ValueError:
            print_error(f"Invalid date format for --after: {after}. Use YYYY-MM-DD")
            raise typer.Exit(1)

    if before:
        try:
            before_dt = datetime.fromisoformat(before)
        except ValueError:
            print_error(f"Invalid date format for --before: {before}. Use YYYY-MM-DD")
            raise typer.Exit(1)

    # Require at least one filter
    if not any([keyword, sender, after_dt, before_dt]):
        print_error("At least one filter required (keyword, --from, --after, --before)")
        raise typer.Exit(1)

    try:
        client = manager.get_client(account)
        messages = client.search_messages(
            space_id=space_id,
            keyword=keyword,
            sender=sender,
            after=after_dt,
            before=before_dt,
            limit=num,
        )

        if not messages:
            print_info("No messages found matching your criteria")
            return

        if format == "json":
            data = [
                {
                    "id": m.name,
                    "text": m.text,
                    "sender": m.sender_name,
                    "sender_email": m.sender_email,
                    "time": m.create_time.isoformat(),
                }
                for m in messages
            ]
            console.print_json(json.dumps(data))
        else:
            console.print(f"[dim]Found {len(messages)} message(s)[/dim]\n")
            table = format_messages_table(messages)
            console.print(table)

    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)
