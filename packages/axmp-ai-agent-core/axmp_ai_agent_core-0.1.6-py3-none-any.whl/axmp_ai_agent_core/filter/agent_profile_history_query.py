"""Agent profile history query parameters."""

from enum import Enum

from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class AgentProfileHistorySortField(str, Enum):
    """Agent Profile History sort field enum."""

    VERSION = "version"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class AgentProfileHistoryQueryParameters(BaseQueryParameters):
    """Agent Profile History query parameters."""

    agent_profile_id: str | None = None
    version: str | None = None
    created_by: str | None = None
    updated_by: str | None = None
    sort_field: AgentProfileHistorySortField = AgentProfileHistorySortField.CREATED_AT
