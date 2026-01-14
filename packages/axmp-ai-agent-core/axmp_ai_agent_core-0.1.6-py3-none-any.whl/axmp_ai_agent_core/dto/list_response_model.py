"""This module contains the list response model for the entity type."""

from __future__ import annotations

from ast import TypeVar

from pydantic import BaseModel, ConfigDict, Field

from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)

EntityType = TypeVar("EntityType")


class ListResponseModel[EntityType](BaseModel):
    """List response model for the entity type."""

    current_page: int = Field(DEFAULT_PAGE_NUMBER, ge=DEFAULT_PAGE_NUMBER)
    """The current page number."""
    page_size: int = Field(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE)
    """The page size."""
    total: int = Field(0, ge=0)
    """The total number of items."""
    data: list[EntityType]
    """The list of items."""

    model_config = ConfigDict(exclude_none=True)
    """The model config."""
