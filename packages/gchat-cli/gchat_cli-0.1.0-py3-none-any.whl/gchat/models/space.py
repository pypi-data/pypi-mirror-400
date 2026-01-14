"""Space model."""

from dataclasses import dataclass
from enum import Enum


class SpaceType(str, Enum):
    """Type of Google Chat space."""

    DIRECT_MESSAGE = "DIRECT_MESSAGE"
    GROUP_CHAT = "GROUP_CHAT"
    SPACE = "SPACE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Space:
    """Represents a Google Chat space."""

    name: str  # Resource name like "spaces/AAAA123"
    display_name: str
    space_type: SpaceType
    member_count: int | None = None

    @property
    def space_id(self) -> str:
        """Extract just the ID from the resource name."""
        return self.name.split("/")[-1] if "/" in self.name else self.name

    @classmethod
    def from_api(cls, data: dict) -> "Space":
        """Create from Google Chat API response."""
        space_type_str = data.get("spaceType", "UNKNOWN")
        try:
            space_type = SpaceType(space_type_str)
        except ValueError:
            space_type = SpaceType.UNKNOWN

        # membershipCount is a dict like {"joinedDirectHumanUserCount": 4}
        membership = data.get("membershipCount", {})
        if isinstance(membership, dict):
            member_count = membership.get("joinedDirectHumanUserCount")
        else:
            member_count = membership

        return cls(
            name=data.get("name", ""),
            display_name=data.get("displayName", data.get("name", "Unknown")),
            space_type=space_type,
            member_count=member_count,
        )
