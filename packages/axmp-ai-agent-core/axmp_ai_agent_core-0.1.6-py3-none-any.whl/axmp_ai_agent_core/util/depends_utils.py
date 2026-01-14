"""Depends utils."""

from fastapi import HTTPException, Request

from axmp_ai_agent_core.agent.util.agent_cache import AsyncTTLQueue


async def get_agent_cache(request: Request) -> AsyncTTLQueue:
    """Get the agent cache."""
    cache = getattr(request.app.state, "agent_cache", None)
    if not cache:
        raise HTTPException(
            status_code=500,
            detail="Cache(agent_cache) is not available in the request state. "
            "You should set the cache in the request state.",
        )
    return cache
