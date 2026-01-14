"""This is the router module for the axmp-ai-workspace project."""

from fastapi import HTTPException, Request
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.base import BaseStore


async def get_checkpointer(request: Request) -> AsyncPostgresSaver:
    """Get the checkpointer."""
    checkpointer = getattr(request.app.state, "checkpointer", None)
    if not checkpointer:
        raise HTTPException(
            status_code=500,
            detail="Checkpointer(postgres) is not available in the request state. "
            "You should set the checkpointer in the request state.",
        )
    return checkpointer


async def get_store(request: Request) -> BaseStore:
    """Get the store."""
    store = getattr(request.app.state, "store", None)
    if not store:
        raise HTTPException(
            status_code=500,
            detail="Store(memory) is not available in the request state. "
            "You should set the store in the request state.",
        )
    return store
