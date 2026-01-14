"""OAuth user entity."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class AccessType(str, Enum):
    """Access type."""

    READ = "READ"
    WRITE = "WRITE"
    ALL = "ALL"


class SharedUser(BaseModel):
    """Shared user entity."""

    username: str
    access_type: AccessType = AccessType.READ


class SharedGroup(BaseModel):
    """Shared group entity."""

    group_id: str
    access_type: AccessType = AccessType.READ


class SharedType(str, Enum):
    """Shared type."""

    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    RESTRICTED = "RESTRICTED"


class SharedTarget(BaseModel):
    """Shared target entity."""

    shared_type: SharedType = SharedType.PRIVATE
    shared_users: list[SharedUser] | None = None
    shared_groups: list[SharedGroup] | None = None
