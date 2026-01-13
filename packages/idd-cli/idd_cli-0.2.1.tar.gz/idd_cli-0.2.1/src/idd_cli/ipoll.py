"""
I-Poll Client - Inter-agent communication.

Messages flow between IDDs without human intervention.
"""

import json
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """An I-Poll message."""
    id: str
    from_agent: str
    to_agent: str
    content: str
    poll_type: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            id=data.get("id", ""),
            from_agent=data.get("from", data.get("from_agent", "")),
            to_agent=data.get("to", data.get("to_agent", "")),
            content=data.get("content", ""),
            poll_type=data.get("type", data.get("poll_type", "PUSH")),
            created_at=data.get("created_at", ""),
            metadata=data.get("metadata")
        )


class IPoll:
    """
    I-Poll client for IDD communication.

    Usage:
        ipoll = IPoll()

        # Check inbox
        messages = ipoll.pull("root_ai")

        # Send message
        ipoll.push("root_ai", "gemini", "Can you analyze this image?")

        # Send task
        ipoll.task("root_ai", "kit", "Validate this JSON schema")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/ipoll",
        external_url: str = "https://brein.jaspervandemeent.nl/api/ipoll"
    ):
        self.base_url = base_url
        self.external_url = external_url
        self.client = httpx.Client(timeout=30.0)

    def pull(
        self,
        agent_id: str,
        mark_read: bool = False,
        limit: int = 10
    ) -> List[Message]:
        """Pull messages from inbox."""
        try:
            url = f"{self.base_url}/pull/{agent_id}"
            params = {"mark_read": str(mark_read).lower()}

            response = self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            polls = data.get("polls", data.get("messages", []))

            return [Message.from_dict(p) for p in polls[:limit]]
        except Exception as e:
            return []

    def push(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        poll_type: str = "PUSH"
    ) -> Optional[str]:
        """Send a message to another IDD."""
        try:
            response = self.client.post(
                f"{self.base_url}/push",
                json={
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "content": content,
                    "poll_type": poll_type
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("id")
        except Exception as e:
            return None

    def task(
        self,
        from_agent: str,
        to_agent: str,
        task_content: str
    ) -> Optional[str]:
        """Send a task request to another IDD."""
        return self.push(from_agent, to_agent, task_content, poll_type="TASK")

    def ack(
        self,
        from_agent: str,
        to_agent: str,
        ack_content: str
    ) -> Optional[str]:
        """Acknowledge a message or task."""
        return self.push(from_agent, to_agent, ack_content, poll_type="ACK")

    def sync(
        self,
        from_agent: str,
        to_agent: str,
        sync_content: str
    ) -> Optional[str]:
        """Sync state with another IDD."""
        return self.push(from_agent, to_agent, sync_content, poll_type="SYNC")

    def status(self) -> Dict[str, Any]:
        """Get I-Poll system status."""
        try:
            response = self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except Exception:
            return {"status": "offline"}

    def close(self):
        """Close the client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
