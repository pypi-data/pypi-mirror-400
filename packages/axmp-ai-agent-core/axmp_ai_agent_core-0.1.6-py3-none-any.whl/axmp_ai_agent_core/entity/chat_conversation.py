"""Conversation model."""

from axmp_ai_agent_core.entity.base_model import CoreBaseModel


class Conversation(CoreBaseModel):
    """Conversation model."""

    thread_id: str | None = None
    agent_id: str | None = None
    user_id: str | None = None
    """This is the sub of the oauth user."""
    title: str | None = None
    project_id: str | None = None
    starred: bool = False
    message: str | None = None
