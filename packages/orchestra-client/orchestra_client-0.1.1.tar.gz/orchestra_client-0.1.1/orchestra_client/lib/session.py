"""Simple Session dataclass for client-side use."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Session:
    """Client-side session representation.

    This is a simple data container for session info from the API.
    No agent logic - just holds the response attributes.
    """
    session_name: str
    agent_type: str = "executor"
    parent_session_name: Optional[str] = None
    instance_id: Optional[str] = None
    children: list["Session"] = field(default_factory=list)

    @property
    def is_root(self) -> bool:
        """Whether this is a root session (no parent)."""
        return self.parent_session_name is None

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create Session from API response dict."""
        return cls(
            session_name=data["session_name"],
            agent_type=data.get("agent_type", "executor"),
            parent_session_name=data.get("parent_session_name"),
            instance_id=data.get("instance_id"),
        )
