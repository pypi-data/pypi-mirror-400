"""Table formatting for CLI output."""

from datetime import datetime

from rich.table import Table

from gchat.models.account import Account
from gchat.models.message import Message
from gchat.models.space import Space, SpaceType


def format_accounts_table(accounts: list[Account], active_name: str | None) -> Table:
    """Format accounts as a Rich table."""
    table = Table(title="Configured Accounts", box=None)
    table.add_column("", style="green", width=2)
    table.add_column("Account", style="account")
    table.add_column("Email")
    table.add_column("Last Used", style="timestamp")

    for acc in accounts:
        is_active = acc.name == active_name
        marker = "→" if is_active else ""
        last_used = _format_relative_time(acc.last_used) if acc.last_used else "never"

        table.add_row(marker, acc.name, acc.email or "-", last_used)

    return table


def format_spaces_table(spaces: list[Space]) -> Table:
    """Format spaces as a Rich table."""
    table = Table(title="Spaces", box=None)
    table.add_column("ID", style="dim")
    table.add_column("Name", style="space")
    table.add_column("Type")
    table.add_column("Members", justify="right")

    for space in spaces:
        type_str = _format_space_type(space.space_type)
        members = str(space.member_count) if space.member_count else "-"

        table.add_row(space.space_id, space.display_name, type_str, members)

    return table


def format_messages_table(messages: list[Message]) -> Table:
    """Format messages as a Rich table."""
    table = Table(box=None, show_header=True, padding=(0, 1))
    table.add_column("Time", style="timestamp", width=12)
    table.add_column("Sender", style="sender", width=20)
    table.add_column("Message")

    for msg in messages:
        time_str = msg.create_time.strftime("%H:%M %b %d")
        # Truncate long messages
        text = msg.text[:100] + "..." if len(msg.text) > 100 else msg.text
        text = text.replace("\n", " ")

        table.add_row(time_str, msg.sender_name, text)

    return table


def _format_space_type(space_type: SpaceType) -> str:
    """Format space type for display."""
    type_map = {
        SpaceType.DIRECT_MESSAGE: "[dim]DM[/dim]",
        SpaceType.GROUP_CHAT: "[yellow]Group[/yellow]",
        SpaceType.SPACE: "[blue]Space[/blue]",
        SpaceType.UNKNOWN: "[dim]?[/dim]",
    }
    return type_map.get(space_type, str(space_type))


def _format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time."""
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        return dt.strftime("%Y-%m-%d")
