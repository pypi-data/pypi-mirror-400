"""Search query."""

from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class ChatFilesQueryParameters(BaseQueryParameters):
    """Chat files query."""

    file_ids: list[str] | None = None
