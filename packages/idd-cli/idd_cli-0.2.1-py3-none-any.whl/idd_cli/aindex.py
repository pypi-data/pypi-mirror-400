"""
AIndex Client - AI Index lookup.

Query capabilities, find experts, route tasks.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class AIndex:
    """
    AIndex client for IDD routing.

    Usage:
        aindex = AIndex()

        # Find by capability
        experts = aindex.find_by_capability("vision")
        # Returns: ["gemini"]

        # Find by keyword
        agents = aindex.find_by_keyword("security")
        # Returns: ["root_ai", "sentinel"]

        # Get agent card
        card = aindex.get_agent("codex")

        # Who can handle this?
        best = aindex.route("analyze this image")
        # Returns: "gemini" (has vision capability)
    """

    def __init__(
        self,
        index_path: str = "/srv/jtel-stack/brain_api/aindex.json"
    ):
        self.index_path = Path(index_path)
        self._data: Optional[Dict[str, Any]] = None

    @property
    def data(self) -> Dict[str, Any]:
        """Load index data (cached)."""
        if self._data is None:
            self.reload()
        return self._data

    def reload(self) -> None:
        """Reload index from disk."""
        if self.index_path.exists():
            self._data = json.loads(self.index_path.read_text())
        else:
            self._data = {"agents": [], "indices": {}}

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent card by ID or alias."""
        # Check aliases first
        by_alias = self.data.get("indices", {}).get("by_alias", {})
        if agent_id in by_alias:
            agent_id = by_alias[agent_id]

        # Find in agents list
        for agent in self.data.get("agents", []):
            if agent.get("agent_id") == agent_id:
                return agent
        return None

    def list_agents(self, status: str = "approved") -> List[Dict[str, Any]]:
        """List all agents with given status."""
        return [
            a for a in self.data.get("agents", [])
            if a.get("status") == status
        ]

    def find_by_capability(self, capability: str) -> List[str]:
        """Find agents with a capability."""
        by_cap = self.data.get("indices", {}).get("by_capability", {})
        return by_cap.get(capability, [])

    def find_by_keyword(self, keyword: str) -> List[str]:
        """Find agents by keyword."""
        by_kw = self.data.get("indices", {}).get("by_keyword", {})
        return by_kw.get(keyword, [])

    def route(self, query: str, kit_available: bool = False) -> Optional[str]:
        """
        Route a query to the best IDD.

        Simple keyword matching for now.
        KmBiT Kernel does the heavy lifting.

        Args:
            query: The query to route
            kit_available: Whether Kit (local inference) is available
        """
        query_lower = query.lower()

        # Vision keywords -> Gemini
        vision_words = ["image", "visual", "diagram", "picture", "screenshot", "photo"]
        if any(w in query_lower for w in vision_words):
            return "gemini"

        # Research keywords -> Codex
        research_words = ["analyze", "research", "structure", "pattern", "index"]
        if any(w in query_lower for w in research_words):
            return "codex"

        # Code keywords -> Root AI
        code_words = ["code", "implement", "build", "create", "write", "fix"]
        if any(w in query_lower for w in code_words):
            return "root_ai"

        # Fast/local -> Kit (if available) or Root AI
        fast_words = ["fast", "quick", "local", "validate", "check"]
        if any(w in query_lower for w in fast_words):
            return "kit" if kit_available else "root_ai"

        # Default: Root AI handles complex/unknown
        return "root_ai"

    def who_is_online(self) -> List[str]:
        """Return list of IDDs that are online/healthy."""
        online = []
        for agent in self.data.get("agents", []):
            state = agent.get("state", {})
            health = state.get("health", "unknown")
            if health in ("ok", "degraded"):
                online.append(agent["agent_id"])
        return online

    def team_status(self) -> Dict[str, str]:
        """Get health status of all team members."""
        status = {}
        for agent in self.data.get("agents", []):
            state = agent.get("state", {})
            status[agent["agent_id"]] = state.get("health", "unknown")
        return status
