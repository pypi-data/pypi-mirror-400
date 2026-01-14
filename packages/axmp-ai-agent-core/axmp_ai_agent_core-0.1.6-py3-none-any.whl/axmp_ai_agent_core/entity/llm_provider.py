"""LLM provider entity."""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel

from axmp_ai_agent_core.entity.base_model import CoreBaseModel


class LlmProviderStatus(str, Enum):
    """LLM provider status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class LlmModelStatus(str, Enum):
    """LLM model status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class LlmModel(BaseModel):
    """LLM model information."""

    id: str
    display_name: str
    status: LlmModelStatus = LlmModelStatus.ACTIVE
    order: int | None = None


class LlmProvider(CoreBaseModel):
    """LLM provider entity."""

    key: str  # openai, anthropic, google, etc.
    display_name: str
    description: str | None = None
    icon_url: str | None = None
    base_url: str | None = None
    status: LlmProviderStatus | None = None
    models: List[LlmModel] | None = None
