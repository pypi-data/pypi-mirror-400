"""
AIndex-DIY - AI Agent Index Framework.

Build your own AI agent registry for routing queries to the right agent.

Usage:
    from aindex_diy import AIndex

    # Load your agent index
    aindex = AIndex("path/to/your/agents.json")

    # Find agents by capability
    vision_agents = aindex.find_by_capability("vision")

    # Route a query to best agent
    best_agent = aindex.route("analyze this image")

    # Get agent details
    agent = aindex.get_agent("my_agent")
"""

from .aindex import AIndex

__version__ = "0.1.0"
__all__ = ["AIndex"]
