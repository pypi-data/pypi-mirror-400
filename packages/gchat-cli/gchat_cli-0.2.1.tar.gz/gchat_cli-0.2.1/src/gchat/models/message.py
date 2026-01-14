"""Message model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Represents a Google Chat message."""

    name: str  # Resource name
    text: str
    sender_name: str
    sender_email: str | None
    create_time: datetime
    space_name: str

    @property
    def message_id(self) -> str:
        """Extract just the ID from the resource name."""
        # Format: spaces/{space}/messages/{message}
        parts = self.name.split("/")
        return parts[-1] if len(parts) >= 4 else self.name

    @classmethod
    def from_api(cls, data: dict) -> "Message":
        """Create from Google Chat API response."""
        sender = data.get("sender", {})
        sender_name = sender.get("displayName", "Unknown")
        sender_email = sender.get("name", "").replace("users/", "") or None

        create_time_str = data.get("createTime", "")
        if create_time_str:
            # Handle RFC 3339 format
            create_time = datetime.fromisoformat(create_time_str.replace("Z", "+00:00"))
        else:
            create_time = datetime.now()

        return cls(
            name=data.get("name", ""),
            text=data.get("text", ""),
            sender_name=sender_name,
            sender_email=sender_email,
            create_time=create_time,
            space_name=data.get("space", {}).get("name", ""),
        )
