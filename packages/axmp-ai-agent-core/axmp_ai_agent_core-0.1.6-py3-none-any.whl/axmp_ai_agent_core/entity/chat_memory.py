"""LLM provider entity."""

from __future__ import annotations

from enum import Enum

from axmp_ai_agent_spec.types import AgentMemoryType

from axmp_ai_agent_core.entity.base_model import CoreBaseModel


class ChatMemoryStatus(str, Enum):
    """Chat memory status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ChatMemory(CoreBaseModel):
    """Chat memory entity."""

    name: str
    memory_type: AgentMemoryType | None = None
    status: ChatMemoryStatus | None = None
    icon_url: str | None = None
    db_uri: str | None = None
