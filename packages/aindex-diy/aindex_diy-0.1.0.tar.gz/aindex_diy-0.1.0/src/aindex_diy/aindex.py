"""
AIndex - AI Agent Index.

A simple, flexible framework for indexing and routing to AI agents.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class AIndex:
    """
    AI Agent Index for routing queries to the right agent.

    Create your own agent registry with capabilities, keywords, and routing rules.

    Example index.json:
    {
        "agents": [
            {
                "agent_id": "vision_agent",
                "name": "Vision Agent",
                "capabilities": ["vision", "image-analysis"],
                "keywords": ["image", "picture", "photo", "diagram"],
                "status": "approved",
                "state": {"health": "ok"}
            }
        ],
        "indices": {
            "by_capability": {"vision": ["vision_agent"]},
            "by_keyword": {"image": ["vision_agent"]},
            "by_alias": {"img": "vision_agent"}
        }
    }

    Usage:
        aindex = AIndex("agents.json")

        # Find by capability
        agents = aindex.find_by_capability("vision")

        # Route query
        best = aindex.route("analyze this screenshot")

        # Get agent info
        agent = aindex.get_agent("vision_agent")
    """

    def __init__(
        self,
        index_path: Optional[str] = None,
        index_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize AIndex.

        Args:
            index_path: Path to JSON index file
            index_data: Or provide index data directly as dict
        """
        self.index_path = Path(index_path) if index_path else None
        self._data: Optional[Dict[str, Any]] = index_data

        # Default routing keywords (customize as needed)
        self.routing_rules: Dict[str, List[str]] = {
            "vision": ["image", "visual", "diagram", "picture", "screenshot", "photo"],
            "code": ["code", "implement", "build", "create", "write", "fix", "debug"],
            "research": ["analyze", "research", "structure", "pattern", "study"],
            "fast": ["fast", "quick", "local", "validate", "check", "simple"],
        }

    @property
    def data(self) -> Dict[str, Any]:
        """Load index data (cached)."""
        if self._data is None:
            self.reload()
        return self._data or {"agents": [], "indices": {}}

    def reload(self) -> None:
        """Reload index from disk."""
        if self.index_path and self.index_path.exists():
            self._data = json.loads(self.index_path.read_text())
        else:
            self._data = {"agents": [], "indices": {}}

    def save(self) -> None:
        """Save index to disk."""
        if self.index_path:
            self.index_path.write_text(json.dumps(self._data, indent=2))

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

    def add_agent(self, agent: Dict[str, Any]) -> None:
        """Add or update an agent in the index."""
        if self._data is None:
            self._data = {"agents": [], "indices": {}}

        # Remove existing if present
        self._data["agents"] = [
            a for a in self._data["agents"]
            if a.get("agent_id") != agent.get("agent_id")
        ]

        # Add new
        self._data["agents"].append(agent)

        # Rebuild indices
        self._rebuild_indices()

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the index."""
        if self._data is None:
            return False

        original_count = len(self._data.get("agents", []))
        self._data["agents"] = [
            a for a in self._data["agents"]
            if a.get("agent_id") != agent_id
        ]

        if len(self._data["agents"]) < original_count:
            self._rebuild_indices()
            return True
        return False

    def _rebuild_indices(self) -> None:
        """Rebuild capability and keyword indices."""
        by_capability: Dict[str, List[str]] = {}
        by_keyword: Dict[str, List[str]] = {}
        by_alias: Dict[str, str] = {}

        for agent in self._data.get("agents", []):
            agent_id = agent.get("agent_id")
            if not agent_id:
                continue

            # Index by capabilities
            for cap in agent.get("capabilities", []):
                if cap not in by_capability:
                    by_capability[cap] = []
                if agent_id not in by_capability[cap]:
                    by_capability[cap].append(agent_id)

            # Index by keywords
            for kw in agent.get("keywords", []):
                if kw not in by_keyword:
                    by_keyword[kw] = []
                if agent_id not in by_keyword[kw]:
                    by_keyword[kw].append(agent_id)

            # Index by aliases
            for alias in agent.get("aliases", []):
                by_alias[alias] = agent_id

        self._data["indices"] = {
            "by_capability": by_capability,
            "by_keyword": by_keyword,
            "by_alias": by_alias,
        }

    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all agents, optionally filtered by status."""
        agents = self.data.get("agents", [])
        if status:
            agents = [a for a in agents if a.get("status") == status]
        return agents

    def find_by_capability(self, capability: str) -> List[str]:
        """Find agents with a capability."""
        by_cap = self.data.get("indices", {}).get("by_capability", {})
        return by_cap.get(capability, [])

    def find_by_keyword(self, keyword: str) -> List[str]:
        """Find agents by keyword."""
        by_kw = self.data.get("indices", {}).get("by_keyword", {})
        return by_kw.get(keyword, [])

    def route(
        self,
        query: str,
        default: Optional[str] = None,
        capability_map: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Route a query to the best agent.

        Uses keyword matching against routing_rules to determine
        which capability is needed, then finds an agent with that capability.

        Args:
            query: The query to route
            default: Default agent if no match found
            capability_map: Override capability->agent mapping

        Returns:
            Agent ID or default
        """
        query_lower = query.lower()

        # Check each capability's keywords
        for capability, keywords in self.routing_rules.items():
            if any(kw in query_lower for kw in keywords):
                # Find agent with this capability
                agents = self.find_by_capability(capability)
                if agents:
                    # Use capability_map override if provided
                    if capability_map and capability in capability_map:
                        return capability_map[capability]
                    return agents[0]

        return default

    def who_is_online(self) -> List[str]:
        """Return list of agents that are online/healthy."""
        online = []
        for agent in self.data.get("agents", []):
            state = agent.get("state", {})
            health = state.get("health", "unknown")
            if health in ("ok", "degraded"):
                online.append(agent["agent_id"])
        return online

    def team_status(self) -> Dict[str, str]:
        """Get health status of all agents."""
        status = {}
        for agent in self.data.get("agents", []):
            state = agent.get("state", {})
            status[agent["agent_id"]] = state.get("health", "unknown")
        return status

    def to_dict(self) -> Dict[str, Any]:
        """Export index as dictionary."""
        return self.data.copy()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIndex":
        """Create AIndex from dictionary."""
        return cls(index_data=data)
