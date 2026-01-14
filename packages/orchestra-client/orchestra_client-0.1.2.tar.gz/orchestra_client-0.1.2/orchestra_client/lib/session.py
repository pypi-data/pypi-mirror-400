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
    id: Optional[str] = None
    agent_type: str = "executor"
    parent_id: Optional[str] = None
    instance_id: Optional[str] = None
    children: list["Session"] = field(default_factory=list)

    @property
    def is_root(self) -> bool:
        """Whether this is a root session (no parent)."""
        return self.parent_id is None

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create Session from API response dict."""
        # Handle both old (parent_session_name) and new (parent_id) formats
        parent_id = data.get("parent_id") or data.get("parent_session_name")
        return cls(
            session_name=data["session_name"],
            id=data.get("id"),
            agent_type=data.get("agent_type", "executor"),
            parent_id=parent_id,
            instance_id=data.get("instance_id"),
        )
