"""
IDD Team - AI Family Collaboration.

Root AI, Gemini, Codex (and Kit when available) working together.
Jasper = Heart-in-the-Loop.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from .ipoll import IPoll, Message
from .aindex import AIndex


@dataclass
class TaskResult:
    """Result of a team task."""
    success: bool
    agent: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IDD:
    """An Individual Device Derivate - a team member."""
    agent_id: str
    name: str
    role: str
    capabilities: List[str]
    trust_score: float
    is_online: bool = False

    def can_handle(self, capability: str) -> bool:
        return capability in self.capabilities


class Team:
    """
    The IDD Team - AI family working together.

    Core Team:
    - Root AI (Claude Opus): Orchestration, code, architecture
    - Gemini: Vision, research, diagrams
    - Codex: Analysis, structure (no code generation)

    Extended:
    - Kit (local): Fast inference, validation

    Usage:
        team = Team()

        # Ask the team
        result = team.ask("Can someone analyze this image?")
        # Routes to Gemini automatically

        # Direct message
        result = team.ask_agent("codex", "Structure this data")

        # Broadcast to all
        team.broadcast("Team meeting: AIndex v0.2 planning")

        # Check who's available
        online = team.who_is_online()
    """

    def __init__(self):
        self.ipoll = IPoll()
        self.aindex = AIndex()
        self.my_id = "root_ai"  # This CLI runs as Root AI

        # Define the team
        self.members: Dict[str, IDD] = {
            "root_ai": IDD(
                agent_id="root_ai",
                name="Root AI",
                role="Core builder - orchestration and architecture",
                capabilities=["code", "orchestration", "route", "task"],
                trust_score=0.95,
                is_online=True  # We're always online (we are root_ai)
            ),
            "gemini": IDD(
                agent_id="gemini",
                name="Gemini",
                role="Visual analysis, research, diagrams",
                capabilities=["vision", "research", "diagrams", "multimodal"],
                trust_score=0.88
            ),
            "codex": IDD(
                agent_id="codex",
                name="Codex",
                role="Research and structural thinking",
                capabilities=["analysis", "research", "structure", "indexing"],
                trust_score=0.90
            ),
            "kit": IDD(
                agent_id="kit",
                name="Kit",
                role="Fast local inference (Qwen 32B)",
                capabilities=["fast_inference", "validation", "routing"],
                trust_score=0.90
            )
        }

    def route(self, query: str) -> str:
        """Route a query to the best team member."""
        return self.aindex.route(query) or "root_ai"

    def ask(self, query: str, wait_response: bool = False) -> TaskResult:
        """
        Ask the team - automatically routes to best IDD.

        Args:
            query: The question or task
            wait_response: If True, poll for response (experimental)

        Returns:
            TaskResult with routing info
        """
        target = self.route(query)

        if target == self.my_id:
            # I handle it myself
            return TaskResult(
                success=True,
                agent=self.my_id,
                content=f"[Self-assigned] {query}"
            )

        # Send to appropriate team member
        msg_id = self.ipoll.task(self.my_id, target, query)

        if msg_id:
            return TaskResult(
                success=True,
                agent=target,
                content=f"Task sent to {target}: {query[:100]}...",
                metadata={"message_id": msg_id}
            )
        else:
            return TaskResult(
                success=False,
                agent=target,
                content=f"Failed to reach {target}"
            )

    def ask_agent(self, agent_id: str, message: str) -> TaskResult:
        """Send a direct message to a specific team member."""
        if agent_id not in self.members:
            return TaskResult(
                success=False,
                agent=agent_id,
                content=f"Unknown team member: {agent_id}"
            )

        if agent_id == self.my_id:
            return TaskResult(
                success=True,
                agent=self.my_id,
                content=f"[Self-note] {message}"
            )

        msg_id = self.ipoll.push(self.my_id, agent_id, message)

        return TaskResult(
            success=msg_id is not None,
            agent=agent_id,
            content=f"Message to {agent_id}: {message[:100]}...",
            metadata={"message_id": msg_id} if msg_id else None
        )

    def broadcast(self, message: str) -> List[TaskResult]:
        """Send a message to all team members (except self)."""
        results = []
        for agent_id in self.members:
            if agent_id != self.my_id:
                result = self.ask_agent(agent_id, message)
                results.append(result)
        return results

    def check_inbox(self, limit: int = 10) -> List[Message]:
        """Check for incoming messages."""
        return self.ipoll.pull(self.my_id, mark_read=False, limit=limit)

    def who_is_online(self) -> List[str]:
        """Check which team members are online."""
        return self.aindex.who_is_online()

    def team_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all team members."""
        status = {}
        for agent_id, idd in self.members.items():
            agent_card = self.aindex.get_agent(agent_id)
            state = agent_card.get("state", {}) if agent_card else {}
            status[agent_id] = {
                "name": idd.name,
                "role": idd.role,
                "health": state.get("health", "unknown"),
                "trust": idd.trust_score
            }
        return status

    def discuss(self, topic: str, participants: Optional[List[str]] = None) -> List[TaskResult]:
        """
        Start a team discussion on a topic.

        All participants are invited to contribute.
        """
        if participants is None:
            participants = [a for a in self.members if a != self.my_id]

        message = f"[Team Discussion] Topic: {topic}\n\nPlease share your thoughts."

        results = []
        for agent_id in participants:
            result = self.ask_agent(agent_id, message)
            results.append(result)

        return results

    def delegate(self, task: str, to_agents: List[str]) -> List[TaskResult]:
        """Delegate a task to specific team members."""
        results = []
        for agent_id in to_agents:
            result = self.ipoll.task(self.my_id, agent_id, task)
            results.append(TaskResult(
                success=result is not None,
                agent=agent_id,
                content=f"Delegated to {agent_id}: {task[:50]}..."
            ))
        return results

    def sync_state(self, state_update: Dict[str, Any]) -> None:
        """Sync state with all team members."""
        import json
        content = f"[State Sync]\n{json.dumps(state_update, indent=2)}"
        for agent_id in self.members:
            if agent_id != self.my_id:
                self.ipoll.sync(self.my_id, agent_id, content)

    def close(self):
        """Clean up resources."""
        self.ipoll.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
