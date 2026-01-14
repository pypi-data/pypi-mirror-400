"""Conversation query model."""

from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class ConversationQueryParameters(BaseQueryParameters):
    """Conversation query model."""

    user_id: str | None = None
    agent_id: str | None = None
    project_id: str | None = None
    starred: bool | None = None
