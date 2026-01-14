"""Message commands (send, read)."""

import json
from typing import Annotated

import typer

from gchat.core.accounts import AccountManager
from gchat.ui import prompts
from gchat.ui.console import console, print_error, print_info, print_success
from gchat.ui.tables import format_messages_table
from gchat.utils.errors import GChatError

app = typer.Typer()


@app.command("send")
def send_message(
    space_id: Annotated[str | None, typer.Argument(help="Space ID")] = None,
    message: Annotated[str | None, typer.Argument(help="Message text")] = None,
    interactive: Annotated[bool, typer.Option("-i", "--interactive")] = False,
    no_confirm: Annotated[bool, typer.Option("--no-confirm")] = False,
    account: Annotated[str | None, typer.Option("--account", "-a")] = None,
    format: Annotated[str, typer.Option("--format", "-f")] = "table",
) -> None:
    """Send a message to a Google Chat space."""
    manager = AccountManager()

    try:
        client = manager.get_client(account)

        # Interactive mode: select space and enter message
        if interactive or (space_id is None and message is None):
            spaces = client.list_spaces()
            if not spaces:
                print_error("No spaces available to send to")
                raise typer.Exit(1)

            space = prompts.prompt_select_space(spaces)
            if space is None:
                raise typer.Abort()
            space_id = space.name

            message = prompts.prompt_message()
            if message is None:
                raise typer.Abort()

        # Validate inputs
        if not space_id:
            print_error("Space ID is required")
            raise typer.Exit(1)

        if not message:
            print_error("Message text is required")
            raise typer.Exit(1)

        # Confirm before sending (unless --no-confirm)
        if not no_confirm:
            # Get space name for confirmation
            try:
                space = client.get_space(space_id)
                space_name = space.display_name
            except Exception:
                space_name = space_id

            if not prompts.prompt_confirm(f"Send message to '{space_name}'?"):
                raise typer.Abort()

        # Send the message
        result = client.send_message(space_id, message)

        if format == "json":
            data = {
                "success": True,
                "message_id": result.name,
                "space": result.space_name,
            }
            console.print_json(json.dumps(data))
        else:
            print_success("Message sent!")

    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)


@app.command("read")
def read_messages(
    space_id: Annotated[str, typer.Argument(help="Space ID to read from")],
    num: Annotated[int, typer.Option("-n", "--num", help="Number of messages")] = 10,
    account: Annotated[str | None, typer.Option("--account", "-a", help="Account to use")] = None,
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "table",
) -> None:
    """Read recent messages from a space."""
    manager = AccountManager()

    try:
        client = manager.get_client(account)
        messages = client.list_messages(space_id, limit=num)

        if not messages:
            print_info("No messages found in this space")
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
            table = format_messages_table(messages)
            console.print(table)

    except GChatError as e:
        print_error(str(e))
        raise typer.Exit(e.exit_code)
