"""This module contains the service for the user."""

from __future__ import annotations

import logging

from motor.motor_asyncio import AsyncIOMotorClient
from zmp_authentication_provider.scheme.auth_model import TokenData

from axmp_ai_agent_core.db.group_repository import GroupRepository
from axmp_ai_agent_core.db.user_credential_repository import UserCredentialRepository
from axmp_ai_agent_core.db.user_repository import UserRepository
from axmp_ai_agent_core.entity.shared_target import SharedTarget, SharedType
from axmp_ai_agent_core.entity.user_credential import (
    UserCredential,
    UserCredentialType,
)
from axmp_ai_agent_core.entity.user_rbac import (
    Group,
    SystemPredefinedRole,
    User,
)
from axmp_ai_agent_core.exception.db_exceptions import (
    ObjectNotFoundException,
)
from axmp_ai_agent_core.exception.service_exceptions import (
    CoreError,
    CoreServiceException,
)
from axmp_ai_agent_core.filter.user_credential_query import (
    UserCredentialQueryParameters,
)

logger = logging.getLogger(__name__)


class UserService:
    """The service for the user."""

    def __init__(
        self,
        client: AsyncIOMotorClient,
        user_repository: UserRepository,
        group_repository: GroupRepository,
        user_credential_repository: UserCredentialRepository,
    ):
        """Initialize the user service."""
        self._client = client
        self._user_repository: UserRepository = user_repository
        self._group_repository: GroupRepository = group_repository
        self._user_credential_repository: UserCredentialRepository = (
            user_credential_repository
        )

    async def create_user_credential(self, *, user_credential: UserCredential) -> str:
        """Create a new user credential."""
        return await self._user_credential_repository.insert(item=user_credential)

    async def get_user_credential_by_id(self, *, id: str) -> UserCredential:
        """Get a user credential by ID."""
        try:
            user_credential = await self._user_credential_repository.find_by_id(
                item_id=id
            )

        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User credential not found: {id}",
            )

        return user_credential

    async def modify_user_credential(
        self, *, user_credential: UserCredential
    ) -> UserCredential:
        """Update a user credential."""
        try:
            updated_user_credential = await self._user_credential_repository.update(
                item=user_credential
            )
            return updated_user_credential
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User credential not found: {user_credential.id}",
            )

    async def remove_user_credential_by_id(self, *, id: str) -> bool:
        """Delete a user credential."""
        try:
            return await self._user_credential_repository.delete(item_id=id)
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User credential not found: {id}",
            )

    async def get_user_credentials_by_username(
        self, *, username: str
    ) -> list[UserCredential]:
        """Get user credentials by username."""
        query_parameters = UserCredentialQueryParameters(username=username)
        return await self._user_credential_repository.find_all_without_pagination(
            query_parameters=query_parameters,
        )

    async def get_user_credentials_by_username_and_type(
        self, *, username: str, credential_type: UserCredentialType
    ) -> list[UserCredential]:
        """Get user credentials by username and credential type."""
        try:
            query_parameters = UserCredentialQueryParameters(
                username=username, credential_type=credential_type
            )
            return await self._user_credential_repository.find_all_without_pagination(
                query_parameters=query_parameters,
            )
        except ValueError:
            logger.warning(f"Invalid credential type: {credential_type}")
            return []

    async def get_user_by_id(self, *, id: str) -> User:
        """Get a user by ID."""
        try:
            user = await self._user_repository.find_by_id(item_id=id)
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User not found: {id}",
            )

        # NOTE: user.groups does not have the role details. so we need to get the groups from the database
        if user.groups is not None:
            detail_groups = await self._get_user_detail_groups(user=user)
            # re-assign the groups
            user.groups = detail_groups

        user.group_ids = None
        user.role_ids = None
        return user

    async def get_user_by_email(self, *, email: str) -> User:
        """Get a user by email."""
        try:
            user = await self._user_repository.find_by_email(email=email)
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User not found: {email}",
            )

        # NOTE: user.groups does not have the role details. so we need to get the groups from the database
        if user.groups is not None:
            detail_groups = await self._get_user_detail_groups(user=user)
            # re-assign the groups
            user.groups = detail_groups

        user.group_ids = None
        user.role_ids = None
        return user

    async def get_user_by_username(self, *, username: str) -> User:
        """Get a user by username."""
        try:
            user = await self._user_repository.find_by_username(username=username)
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User not found: {username}",
            )

        # NOTE: user.groups does not have the role details. so we need to get the groups from the database
        if user.groups is not None:
            detail_groups = await self._get_user_detail_groups(user=user)
            # re-assign the groups
            user.groups = detail_groups

        user.group_ids = None
        user.role_ids = None
        return user

    async def get_user_by_iss_sub(self, *, iss: str, sub: str) -> User:
        """Get a user by iss and sub."""
        try:
            user = await self._user_repository.find_by_iss_sub(iss=iss, sub=sub)
        except ObjectNotFoundException:
            raise CoreServiceException(
                CoreError.ID_NOT_FOUND,
                details=f"User not found: {iss}:{sub}",
            )

        # NOTE: user.groups does not have the role details. so we need to get the groups from the database
        if user.groups is not None:
            detail_groups = await self._get_user_detail_groups(user=user)
            # re-assign the groups
            user.groups = detail_groups

        user.group_ids = None
        user.role_ids = None
        return user

    async def _get_user_detail_groups(self, *, user: User) -> list[Group]:
        """Get the detail groups of the user."""
        if user.groups is None:
            return []

        detail_groups: list[Group] = []
        for group in user.groups:
            detail_group: Group = await self._group_repository.find_by_id(
                item_id=group.id
            )
            detail_groups.append(detail_group)
        return detail_groups

    async def check_read_permission(
        self,
        *,
        oauth_user: TokenData,
        shared_target: SharedTarget,
        create_by: str,
        system_defined_role: list[SystemPredefinedRole] = [
            SystemPredefinedRole.SYSTEM_ADMINISTRATOR
        ],
    ) -> None:
        """Check if the user has read permission for the shared target."""
        if shared_target.shared_type == SharedType.PUBLIC:
            return
        else:
            user = await self.get_user_by_iss_sub(
                iss=oauth_user.iss, sub=oauth_user.sub
            )
            if shared_target.shared_type == SharedType.RESTRICTED:
                if (
                    not any(user.has_role(role) for role in system_defined_role)
                    and user.username != create_by
                    and not user.has_read_permission(shared_target)
                ):
                    raise CoreServiceException(
                        CoreError.PERMISSION_DENIED,
                        details="You are not authorized to read this shared target.",
                    )
            elif shared_target.shared_type == SharedType.PRIVATE:
                if (
                    not any(user.has_role(role) for role in system_defined_role)
                    and user.username != create_by
                ):
                    raise CoreServiceException(
                        CoreError.PERMISSION_DENIED,
                        details="You are not authorized to read this shared target.",
                    )
            else:
                raise CoreServiceException(
                    CoreError.INVALID_OBJECTID,
                    details="Invalid shared target type.",
                )

    async def check_write_permission(
        self,
        *,
        oauth_user: TokenData,
        shared_target: SharedTarget,
        create_by: str,
        system_defined_role: list[SystemPredefinedRole] = [
            SystemPredefinedRole.SYSTEM_ADMINISTRATOR
        ],
    ) -> None:
        """Check if the user has write permission for the shared target."""
        user = await self.get_user_by_iss_sub(iss=oauth_user.iss, sub=oauth_user.sub)
        if shared_target.shared_type in [SharedType.PUBLIC, SharedType.PRIVATE]:
            # NOTE: The user who is owner or has system predefined role
            # can only write the shared target when the shared data is public or private
            if (
                not any(user.has_role(role) for role in system_defined_role)
                and user.username != create_by
            ):
                raise CoreServiceException(
                    CoreError.PERMISSION_DENIED,
                    details="You are not authorized to write this shared target.",
                )

        elif shared_target.shared_type in [SharedType.RESTRICTED]:
            # NOTE: The user who is owner or has system predefined role or has write permission
            # can only write the shared target when the shared target is restricted
            if (
                not any(user.has_role(role) for role in system_defined_role)
                and user.username != create_by
                and not user.has_write_permission(shared_target)
            ):
                raise CoreServiceException(
                    CoreError.PERMISSION_DENIED,
                    details="You are not authorized to write this shared target.",
                )
        else:
            raise CoreServiceException(
                CoreError.INVALID_OBJECTID,
                details="Invalid shared target type.",
            )
