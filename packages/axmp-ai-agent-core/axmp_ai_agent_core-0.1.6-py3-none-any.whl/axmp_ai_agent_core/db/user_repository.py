"""User repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from axmp_ai_agent_core.db.base_repository import BaseRepository
from axmp_ai_agent_core.entity.user_rbac import User
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from axmp_ai_agent_core.filter.user_rbac_query import UserQueryParameters
from axmp_ai_agent_core.setting import mongodb_settings
from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_LIMIT,
    SortDirection,
)
from axmp_ai_agent_core.util.search_utils import get_escaped_regex_pattern
from axmp_ai_agent_core.util.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """User repository."""

    async def insert(
        self, *, item: User, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new user into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        user_dict = item.model_dump(by_alias=True, exclude=["id", "groups", "roles"])
        user_dict["created_at"] = item.created_at

        result: InsertOneResult = await self._collection.insert_one(
            user_dict, session=session
        )

        return str(result.inserted_id)

    async def update(
        self, *, item: User, session: AsyncIOMotorClientSession | None = None
    ) -> User | None:
        """Update a user in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        user_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "groups",
                "roles",
                "created_at",
                "created_by",
            ],
        )
        user_dict["updated_at"] = item.updated_at

        update = {"$set": user_dict}

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if document is None:
            raise ObjectNotFoundException(item.id)

        return User(**document)

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete a user from the repository."""
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
    ) -> User | None:
        """Find a user by ID with groups information from aggregation."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        pipeline = self._build_user_aggregation_pipeline(match_filter=filter)

        cursor = self._collection.aggregate(pipeline, session=session)

        document = None
        async for doc in cursor:
            document = doc
            break

        if document is None:
            raise ObjectNotFoundException(item_id)

        return User(**document)

    async def find_by_email(
        self, *, email: str, session: AsyncIOMotorClientSession | None = None
    ) -> User | None:
        """Find a user by email with groups information from aggregation."""
        filter = {"email": email}

        pipeline = self._build_user_aggregation_pipeline(match_filter=filter)

        cursor = self._collection.aggregate(pipeline, session=session)

        document = None
        async for doc in cursor:
            document = doc
            break

        if document is None:
            raise ObjectNotFoundException(email)

        return User(**document)

    async def find_by_username(
        self, *, username: str, session: AsyncIOMotorClientSession | None = None
    ) -> User | None:
        """Find a user by username with groups information from aggregation."""
        filter = {"username": username}

        pipeline = self._build_user_aggregation_pipeline(match_filter=filter)

        cursor = self._collection.aggregate(pipeline, session=session)

        document = None
        async for doc in cursor:
            document = doc
            break

        if document is None:
            raise ObjectNotFoundException(username)

        return User(**document)

    async def find_by_iss_sub(
        self, *, iss: str, sub: str, session: AsyncIOMotorClientSession | None = None
    ) -> User | None:
        """Find a user by iss and sub with groups information from aggregation."""
        filter = {"iss": iss, "sub": sub}

        pipeline = self._build_user_aggregation_pipeline(match_filter=filter)

        cursor = self._collection.aggregate(pipeline, session=session)

        document = None
        async for doc in cursor:
            document = doc
            break

        if document is None:
            raise ObjectNotFoundException(f"{iss}:{sub}")

        return User(**document)

    async def find_all(
        self,
        *,
        query_parameters: UserQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[User]:
        """Find all users with pagination."""
        if page_number < 1:
            page_number = DEFAULT_PAGE_NUMBER
        if page_size < 1:
            page_size = DEFAULT_PAGE_SIZE

        skip, limit = (page_size * (page_number - 1), page_size)

        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "username"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        additional_stages = [
            {"$sort": {sort_field: direction}},
            {"$skip": skip},
            {"$limit": limit},
        ]

        pipeline = self._build_user_aggregation_pipeline(
            match_filter=filter, additional_stages=additional_stages
        )

        # Build projection if needed
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )
        if projection:
            pipeline.append({"$project": projection})

        logger.debug(f"Pipeline: {pipeline}")

        cursor = self._collection.aggregate(pipeline, session=session)

        # convert cursor to list of users
        users = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    users.append(User(**document))

        logger.debug(f"Found {len(users)} users")

        return users

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: UserQueryParameters,
        max_limit: int = MAX_LIMIT,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[User]:
        """Find all users without pagination."""
        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "username"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        additional_stages = [
            {"$sort": {sort_field: direction}},
            {"$limit": max_limit},
        ]

        pipeline = self._build_user_aggregation_pipeline(
            match_filter=filter, additional_stages=additional_stages
        )

        # Build projection if needed
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )
        if projection:
            pipeline.append({"$project": projection})

        logger.debug(f"Pipeline: {pipeline}")

        cursor = self._collection.aggregate(pipeline, session=session)

        # convert cursor to list of users
        users = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    users.append(User(**document))

        logger.debug(f"Found {len(users)} users")

        return users

    async def count(
        self,
        *,
        query_parameters: UserQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of users."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    def _build_user_aggregation_pipeline(
        self, *, match_filter: dict[str, Any], additional_stages: list[dict] = None
    ) -> list[dict]:
        """Build common aggregation pipeline for user queries with groups and roles lookup."""
        pipeline = [
            {"$match": match_filter},
            {
                "$addFields": {
                    "group_object_ids": {
                        "$map": {
                            "input": {"$ifNull": ["$group_ids", []]},
                            "as": "groupId",
                            "in": {"$toObjectId": "$$groupId"},
                        }
                    },
                    "role_object_ids": {
                        "$map": {
                            "input": {"$ifNull": ["$role_ids", []]},
                            "as": "roleId",
                            "in": {"$toObjectId": "$$roleId"},
                        }
                    },
                }
            },
            {
                "$lookup": {
                    "from": mongodb_settings.collection_group,
                    "localField": "group_object_ids",
                    "foreignField": "_id",
                    "as": "groups",
                }
            },
            {
                "$lookup": {
                    "from": mongodb_settings.collection_role,
                    "localField": "role_object_ids",
                    "foreignField": "_id",
                    "as": "roles",
                }
            },
            {"$unset": ["group_object_ids", "role_object_ids"]},
        ]

        # Add additional stages if provided
        if additional_stages:
            pipeline.extend(additional_stages)

        return pipeline

    async def find_all_query(
        self, *, query_parameters: UserQueryParameters
    ) -> dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: dict[str, Any] = {}

        if query_parameters.keyword:
            keyword_regex = {
                "$regex": get_escaped_regex_pattern(query_parameters.keyword),
                "$options": "i",
            }
            filter["$or"] = [
                {"username": keyword_regex},
                {"email": keyword_regex},
                {"given_name": keyword_regex},
                {"family_name": keyword_regex},
            ]

        if query_parameters.group_code:
            filter["group_ids"] = {"$in": [query_parameters.group_code]}

        return filter
