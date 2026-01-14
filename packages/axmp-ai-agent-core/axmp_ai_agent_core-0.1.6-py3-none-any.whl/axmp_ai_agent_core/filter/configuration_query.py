"""Configuration query parameters."""

from enum import Enum

from axmp_ai_agent_spec.types import AgentMemoryType

from axmp_ai_agent_core.entity.chat_memory import ChatMemoryStatus
from axmp_ai_agent_core.entity.llm_provider import LlmProviderStatus
from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class ChatMemorySortField(str, Enum):
    """Sort field for chat memory query."""

    NAME = "name"
    STATUS = "status"
    MEMORY_TYPE = "memory_type"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ChatMemoryQueryParameters(BaseQueryParameters):
    """Query parameters for chat memory."""

    keyword: str | None = None
    statuses: list[ChatMemoryStatus] | None = None
    memory_types: list[AgentMemoryType] | None = None
    created_by: str | None = None
    updated_by: str | None = None


class LlmProviderSortField(str, Enum):
    """Sort field for LLM provider query."""

    DISPLAY_NAME = "display_name"
    STATUS = "status"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class LlmProviderQueryParameters(BaseQueryParameters):
    """Query parameters for LLM provider."""

    keyword: str | None = None
    statuses: list[LlmProviderStatus] | None = None
    created_by: str | None = None
    updated_by: str | None = None
