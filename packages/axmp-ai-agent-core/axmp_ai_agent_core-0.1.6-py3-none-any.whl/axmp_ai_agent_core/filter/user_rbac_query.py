"""OAuth user entity."""

from __future__ import annotations

from enum import Enum

from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters


class GroupSortField(str, Enum):
    """Group sort field enum."""

    CODE = "code"
    NAME = "name"


class GroupQueryParameters(BaseQueryParameters):
    """Group query parameters."""

    sort_field: GroupSortField = GroupSortField.CODE
    keyword: str | None = None
    parent_code: str | None = None


class UserSortField(str, Enum):
    """User sort field enum."""

    USERNAME = "username"
    EMAIL = "email"
    GIVEN_NAME = "given_name"  # first_name
    FAMILY_NAME = "family_name"  # last_name


class UserQueryParameters(BaseQueryParameters):
    """User query parameters."""

    sort_field: UserSortField = UserSortField.USERNAME
    keyword: str | None = None
    group_code: str | None = None
