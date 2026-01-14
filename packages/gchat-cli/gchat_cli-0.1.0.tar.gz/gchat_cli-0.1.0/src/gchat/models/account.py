"""Account model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Account:
    """Represents a configured Google Chat account."""

    name: str
    email: str | None = None
    created_at: datetime | None = None
    last_used: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for config storage."""
        data: dict = {}
        if self.email:
            data["email"] = self.email
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.last_used:
            data["last_used"] = self.last_used.isoformat()
        return data

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "Account":
        """Create from config dictionary."""
        return cls(
            name=name,
            email=data.get("email"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            last_used=datetime.fromisoformat(data["last_used"])
            if data.get("last_used")
            else None,
        )
