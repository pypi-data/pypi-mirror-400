"""Agent profile query."""

from __future__ import annotations

from enum import Enum

from pydantic import model_validator

from axmp_ai_agent_core.entity.agent_profile import (
    ProfileStatus,
    ProfileType,
    RuntimeType,
    UsageType,
)
from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class AgentProfileSortField(str, Enum):
    """Agent profile sort field."""

    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class AgentProfileListType(str, Enum):
    """Agent profile list type."""

    MY_AGENTS = "my-agents"
    SHARED_AGENTS = "shared-agents"


class AgentProfileQueryParameters(BaseQueryParameters):
    """Agent profile query."""

    keyword: str | None = None
    types: list[ProfileType] | None = None
    statuses: list[ProfileStatus] | None = None
    runtime_types: list[RuntimeType] | None = None
    usage_types: list[UsageType] | None = None
    created_by: str | None = None
    updated_by: str | None = None
    list_type: AgentProfileListType | None = None
    # provisioned: bool | None = None
    is_published_to_workspace: bool | None = None

    @model_validator(mode="after")
    def validate_list_type(self) -> AgentProfileQueryParameters:
        """Validate the list type."""
        if self.list_type is not None:
            if self.created_by is None:
                raise ValueError("created_by is required when list_type is not None")
        return self
