"""OAuth user entity."""

from __future__ import annotations

from enum import Enum

from pydantic import computed_field
from zmp_authentication_provider.scheme.auth_model import OAuthUser

from axmp_ai_agent_core.entity.base_model import CoreBaseModel
from axmp_ai_agent_core.entity.shared_target import (
    AccessType,
    SharedTarget,
    SharedType,
)


class MenuAccessType(str, Enum):
    """Menu access type."""

    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ALL = "ALL"


class MenuPermission(CoreBaseModel):
    """Menu permission entity."""

    menu_id: str
    access_types: list[MenuAccessType]


class APIMethod(str, Enum):
    """API method."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    ALL = "ALL"


class APIResourcePermission(CoreBaseModel):
    """Permission entity."""

    api_path: str
    method: APIMethod


class RoleType(str, Enum):
    """Role type."""

    SYSTEM = "SYSTEM"
    CUSTOM = "CUSTOM"


class SystemPredefinedRole(str, Enum):
    """System predefined role."""

    SYSTEM_ADMINISTRATOR = "System Administrator"
    BACKEND_SERVER_ADMIN = "Backend Server Admin"
    MCP_SERVER_ADMIN = "MCP Server Admin"
    AGENT_ADMIN = "Agent Admin"
    AGENT_DEVELOPER = "Agent Developer"


class Role(CoreBaseModel):
    """Role entity."""

    name: str
    type: RoleType = RoleType.CUSTOM
    description: str | None = None
    # TODO: implement menu and api resource permissions
    # menu_permissions: list[MenuPermission] | None = None
    # api_resource_permissions: list[APIResourcePermission] | None = None


class Group(CoreBaseModel):
    """Group entity."""

    code: str
    name: str
    description: str | None = None
    parent_code: str | None = None
    # for roles
    roles: list[Role] | None = None
    role_ids: list[str] | None = None


class AccessPermission(CoreBaseModel):
    """Access permission entity."""

    username: str
    group_ids: list[str] | None = None


class User(OAuthUser):
    """OAuth user entity."""

    created_by: str | None = None
    updated_by: str | None = None
    # for groups
    group_ids: list[str] | None = None
    groups: list[Group] | None = None
    # for roles
    role_ids: list[str] | None = None
    roles: list[Role] | None = None

    def has_role(self, system_predefined_role: SystemPredefinedRole) -> bool:
        """Check if the user is in the system predefined role."""
        result = False
        if self.roles is not None:
            result = any(
                role.name == system_predefined_role.value for role in self.roles
            )
        if not result and self.groups is not None:
            for group in self.groups:
                if group.roles is not None:
                    result = any(
                        role.name == system_predefined_role.value
                        for role in group.roles
                    )
                    if result:
                        return True
        return result

    @computed_field
    @property
    def is_system_administrator(self) -> bool:
        """Check if the user is a system administrator."""
        return self.has_role(SystemPredefinedRole.SYSTEM_ADMINISTRATOR)

    @computed_field
    @property
    def is_backend_server_admin(self) -> bool:
        """Check if the user is a backend server administrator."""
        return self.has_role(SystemPredefinedRole.BACKEND_SERVER_ADMIN)

    @computed_field
    @property
    def is_mcp_server_admin(self) -> bool:
        """Check if the user is a MCP server administrator."""
        return self.has_role(SystemPredefinedRole.MCP_SERVER_ADMIN)

    @computed_field
    @property
    def is_agent_admin(self) -> bool:
        """Check if the user is a agent administrator."""
        return self.has_role(SystemPredefinedRole.AGENT_ADMIN)

    @computed_field
    @property
    def is_agent_developer(self) -> bool:
        """Check if the user is a agent developer."""
        return self.has_role(SystemPredefinedRole.AGENT_DEVELOPER)

    @property
    def access_permission(self) -> AccessPermission:
        """Get the access permission of the user."""
        group_ids = []
        if self.group_ids is not None:
            group_ids = self.group_ids
        else:
            if self.groups is not None:
                for group in self.groups:
                    group_ids.append(group.id)

        return AccessPermission(
            username=self.username,
            group_ids=group_ids,
        )

    def has_read_permission(self, shared_target: SharedTarget) -> bool:
        """Check if the user is granted the shared target for read permission."""
        if shared_target.shared_type == SharedType.PUBLIC:
            return True
        elif shared_target.shared_type == SharedType.RESTRICTED:
            if shared_target.shared_users is not None:
                for shared_user in shared_target.shared_users:
                    if (
                        shared_user.username == self.username
                        and shared_user.access_type
                        in [AccessType.READ, AccessType.WRITE, AccessType.ALL]
                    ):
                        return True
            if (
                shared_target.shared_groups is not None
                and self.access_permission.group_ids is not None
            ):
                for my_group_id in self.access_permission.group_ids:
                    for shared_group in shared_target.shared_groups:
                        if (
                            shared_group.group_id == my_group_id
                            and shared_group.access_type
                            in [AccessType.READ, AccessType.WRITE, AccessType.ALL]
                        ):
                            return True
            return False
        else:
            return False

    def has_write_permission(self, shared_target: SharedTarget) -> bool:
        """Check if the user is granted the shared target for write permission."""
        if shared_target.shared_type == SharedType.RESTRICTED:
            if shared_target.shared_users is not None:
                for shared_user in shared_target.shared_users:
                    if (
                        shared_user.username == self.username
                        and shared_user.access_type
                        in [AccessType.WRITE, AccessType.ALL]
                    ):
                        return True
            if (
                shared_target.shared_groups is not None
                and self.access_permission.group_ids is not None
            ):
                for my_group_id in self.access_permission.group_ids:
                    for shared_group in shared_target.shared_groups:
                        if (
                            shared_group.group_id == my_group_id
                            and shared_group.access_type
                            in [AccessType.WRITE, AccessType.ALL]
                        ):
                            return True
            return False
        else:
            return False
