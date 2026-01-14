"""User credential repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import pymongo
from axmp_openapi_helper import AuthenticationType
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult
from zmp_authentication_provider.utils.encryption_utils import decrypt, encrypt

from axmp_ai_agent_core.db.base_repository import BaseRepository
from axmp_ai_agent_core.entity.user_credential import (
    AWS_BEDROCK,
    UserCredential,
    UserCredentialType,
)
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
    ValueErrorException,
)
from axmp_ai_agent_core.filter.user_credential_query import (
    UserCredentialQueryParameters,
)
from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_LIMIT,
    SortDirection,
)
from axmp_ai_agent_core.util.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger(__name__)


class UserCredentialRepository(BaseRepository[UserCredential]):
    """User credential repository."""

    async def insert(
        self, *, item: UserCredential, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new user credential into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        user_credential_dict = item.model_dump(by_alias=True, exclude=["id"])
        user_credential_dict["created_at"] = item.created_at

        if item.credential_type == UserCredentialType.LLM_PROVIDER:
            if item.provider == AWS_BEDROCK:
                user_credential_dict["aws_access_key_id"] = encrypt(
                    item.aws_access_key_id
                ).hex()
                user_credential_dict["aws_secret_access_key"] = encrypt(
                    item.aws_secret_access_key
                ).hex()
                user_credential_dict["region_name"] = item.region_name
            else:
                user_credential_dict["llm_api_key"] = encrypt(item.llm_api_key).hex()
        else:
            if item.auth_config is not None:
                if item.auth_config.type == AuthenticationType.BASIC:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                        "username": item.auth_config.username,
                        "password": encrypt(item.auth_config.password).hex(),
                    }
                elif item.auth_config.type == AuthenticationType.BEARER:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                        "bearer_token": encrypt(item.auth_config.bearer_token).hex(),
                    }
                elif item.auth_config.type == AuthenticationType.API_KEY:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                        "api_key_name": item.auth_config.api_key_name,
                        "api_key_value": encrypt(item.auth_config.api_key_value).hex(),
                    }
                elif item.auth_config.type == AuthenticationType.NONE:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                    }
                else:
                    raise ValueErrorException(
                        f"Unsupported authentication type: {item.auth_config.type}"
                    )

        result: InsertOneResult = await self._collection.insert_one(
            user_credential_dict, session=session
        )

        return str(result.inserted_id)

    async def update(
        self, *, item: UserCredential, session: AsyncIOMotorClientSession | None = None
    ) -> UserCredential | None:
        """Update a user credential in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        user_credential_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
            ],
        )
        user_credential_dict["updated_at"] = item.updated_at

        update = {"$set": user_credential_dict}

        if item.credential_type == UserCredentialType.LLM_PROVIDER:
            if item.provider == AWS_BEDROCK:
                user_credential_dict["aws_access_key_id"] = encrypt(
                    item.aws_access_key_id
                ).hex()
                user_credential_dict["aws_secret_access_key"] = encrypt(
                    item.aws_secret_access_key
                ).hex()
                user_credential_dict["region_name"] = item.region_name
            else:
                user_credential_dict["llm_api_key"] = encrypt(item.llm_api_key).hex()
        else:
            if item.auth_config is not None:
                if item.auth_config.type == AuthenticationType.BASIC:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                        "username": item.auth_config.username,
                        "password": encrypt(item.auth_config.password).hex(),
                    }
                elif item.auth_config.type == AuthenticationType.BEARER:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                        "bearer_token": encrypt(item.auth_config.bearer_token).hex(),
                    }
                elif item.auth_config.type == AuthenticationType.API_KEY:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                        "api_key_name": item.auth_config.api_key_name,
                        "api_key_value": encrypt(item.auth_config.api_key_value).hex(),
                    }
                elif item.auth_config.type == AuthenticationType.NONE:
                    user_credential_dict["auth_config"] = {
                        "type": item.auth_config.type,
                    }
                else:
                    raise ValueErrorException(
                        f"Unsupported authentication type: {item.auth_config.type}"
                    )

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        if document is None:
            raise ObjectNotFoundException(item.id)

        updated = UserCredential(**document)

        if updated.credential_type == UserCredentialType.LLM_PROVIDER:
            if updated.provider == AWS_BEDROCK:
                if updated.aws_access_key_id is not None:
                    updated.aws_access_key_id = decrypt(
                        bytes.fromhex(updated.aws_access_key_id)
                    )
                if updated.aws_secret_access_key is not None:
                    updated.aws_secret_access_key = decrypt(
                        bytes.fromhex(updated.aws_secret_access_key)
                    )
            else:
                if updated.llm_api_key is not None:
                    updated.llm_api_key = decrypt(bytes.fromhex(updated.llm_api_key))
        else:
            if updated.auth_config is not None:
                if updated.auth_config.type == AuthenticationType.BASIC:
                    updated.auth_config = {
                        "type": updated.auth_config.type,
                        "username": updated.auth_config.username,
                        "password": decrypt(
                            bytes.fromhex(updated.auth_config.password)
                        ),
                    }
                elif updated.auth_config.type == AuthenticationType.BEARER:
                    updated.auth_config = {
                        "type": updated.auth_config.type,
                        "bearer_token": decrypt(
                            bytes.fromhex(updated.auth_config.bearer_token)
                        ),
                    }
                elif updated.auth_config.type == AuthenticationType.API_KEY:
                    updated.auth_config = {
                        "type": updated.auth_config.type,
                        "api_key_name": updated.auth_config.api_key_name,
                        "api_key_value": decrypt(
                            bytes.fromhex(updated.auth_config.api_key_value)
                        ),
                    }
                elif updated.auth_config.type == AuthenticationType.NONE:
                    updated.auth_config = {
                        "type": updated.auth_config.type,
                    }
                else:
                    raise ValueErrorException(
                        f"Unsupported authentication type: {updated.auth_config.type}"
                    )

        return updated

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete a user credential from the repository."""
        try:
            query = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one_and_delete(query, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return True

    async def find_by_id(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> UserCredential | None:
        """Find a user credential by ID."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        user_credential = UserCredential(**document)

        if user_credential.credential_type == UserCredentialType.LLM_PROVIDER:
            if user_credential.provider == AWS_BEDROCK:
                if user_credential.aws_access_key_id is not None:
                    user_credential.aws_access_key_id = decrypt(
                        bytes.fromhex(user_credential.aws_access_key_id)
                    )
                if user_credential.aws_secret_access_key is not None:
                    user_credential.aws_secret_access_key = decrypt(
                        bytes.fromhex(user_credential.aws_secret_access_key)
                    )
            else:
                if user_credential.llm_api_key is not None:
                    user_credential.llm_api_key = decrypt(
                        bytes.fromhex(user_credential.llm_api_key)
                    )
        else:
            if user_credential.auth_config is not None:
                if user_credential.auth_config.type == AuthenticationType.BASIC:
                    user_credential.auth_config = {
                        "type": user_credential.auth_config.type,
                        "username": user_credential.auth_config.username,
                        "password": decrypt(
                            bytes.fromhex(user_credential.auth_config.password)
                        ),
                    }
                elif user_credential.auth_config.type == AuthenticationType.BEARER:
                    user_credential.auth_config = {
                        "type": user_credential.auth_config.type,
                        "bearer_token": decrypt(
                            bytes.fromhex(user_credential.auth_config.bearer_token)
                        ),
                    }
                elif user_credential.auth_config.type == AuthenticationType.API_KEY:
                    user_credential.auth_config = {
                        "type": user_credential.auth_config.type,
                        "api_key_name": user_credential.auth_config.api_key_name,
                        "api_key_value": decrypt(
                            bytes.fromhex(user_credential.auth_config.api_key_value)
                        ),
                    }
                elif user_credential.auth_config.type == AuthenticationType.NONE:
                    user_credential.auth_config = {
                        "type": user_credential.auth_config.type,
                    }
                else:
                    raise ValueErrorException(
                        f"Unsupported authentication type: {user_credential.auth_config.type}"
                    )

        return user_credential

    async def find_all(
        self,
        *,
        query_parameters: UserCredentialQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = [
            "llm_api_key",
            "auth_config.api_key_value",
            "auth_config.password",
            "auth_config.bearer_token",
        ],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[UserCredential]:
        """Find all user credentials in the repository."""
        if exclude_fields and include_fields:
            if len(exclude_fields) > 0 and len(include_fields) > 0:
                raise ValueErrorException(
                    "exclude_fields and include_fields cannot be used together"
                )

        if page_number < 1:
            page_number = DEFAULT_PAGE_NUMBER
        if page_size < 1:
            page_size = DEFAULT_PAGE_SIZE

        skip, limit = (page_size * (page_number - 1), page_size)

        logger.debug(
            f"page_number={page_number}, page_size={page_size} so skip: {skip}, limit: {limit}"
        )

        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "display_name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        cursor = (
            self._collection.find(filter, projection=projection, session=session)
            .sort(sort_field, direction)
            .skip(skip)
            .limit(limit)
        )

        user_credentials = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    user_credentials.append(UserCredential(**document))

        return user_credentials

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: UserCredentialQueryParameters,
        max_limit: int = MAX_LIMIT,  # if max_limit is 0, don't apply limit
        exclude_fields: list[str] = [
            "llm_api_key",
        ],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[UserCredential]:
        """Find all user credentials in the repository without pagination."""
        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "display_name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        cursor = self._collection.find(
            filter, projection=projection, session=session
        ).sort(sort_field, direction)

        if max_limit > 0:
            cursor = cursor.limit(max_limit)

        user_credentials = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    user_credentials.append(UserCredential(**document))

        logger.debug(f"Found {len(user_credentials)} user credentials")

        return user_credentials

    async def count(
        self,
        *,
        query_parameters: UserCredentialQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of user credentials in the repository."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    async def find_all_query(
        self, *, query_parameters: UserCredentialQueryParameters
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: Dict[str, Any] = {}

        if query_parameters.username:
            filter["username"] = query_parameters.username

        if query_parameters.credential_type:
            filter["credential_type"] = query_parameters.credential_type.value

        return filter
