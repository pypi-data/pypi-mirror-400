"""Agent cache key format."""

AGENT_CACHE_KEY_FORMAT = "agent-{agent_id}"
"""Agent cache key format."""


def agent_cache_key(agent_id: str) -> str:
    """Format the agent cache key."""
    return AGENT_CACHE_KEY_FORMAT.format(agent_id=agent_id)
