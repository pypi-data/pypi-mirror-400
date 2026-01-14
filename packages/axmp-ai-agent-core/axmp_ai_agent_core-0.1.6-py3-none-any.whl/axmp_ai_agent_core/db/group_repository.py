"""Group repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult

from axmp_ai_agent_core.db.base_repository import BaseRepository
from axmp_ai_agent_core.entity.user_rbac import Group
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
    ValueErrorException,
)
from axmp_ai_agent_core.filter.user_rbac_query import GroupQueryParameters
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


class GroupRepository(BaseRepository[Group]):
    """Group repository."""

    async def insert(
        self, *, item: Group, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new group into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        group_dict = item.model_dump(by_alias=True, exclude=["id", "roles"])
        group_dict["created_at"] = item.created_at

        try:
            result: InsertOneResult = await self._collection.insert_one(
                group_dict, session=session
            )

            return str(result.inserted_id)
        except DuplicateKeyError as e:
            raise ValueErrorException(
                f"Group code {item.code} already exists. Details: {e}"
            )

    async def update(
        self, *, item: Group, session: AsyncIOMotorClientSession | None = None
    ) -> Group | None:
        """Update a group in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        group_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
                "roles",
            ],
        )
        group_dict["updated_at"] = item.updated_at

        update = {"$set": group_dict}

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if document is None:
            raise ObjectNotFoundException(item.id)

        return Group(**document)

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete a group from the repository."""
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
    ) -> Group | None:
        """Find a group by ID."""
        try:
            match_filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        pipeline = self._build_group_aggregation_pipeline(match_filter=match_filter)

        cursor = self._collection.aggregate(pipeline, session=session)
        documents = await cursor.to_list(length=1)

        if not documents:
            raise ObjectNotFoundException(item_id)

        return Group(**documents[0])

    async def find_by_code(
        self, *, code: str, session: AsyncIOMotorClientSession | None = None
    ) -> Group | None:
        """Find a group by code."""
        match_filter = {"code": code}

        pipeline = self._build_group_aggregation_pipeline(match_filter=match_filter)

        cursor = self._collection.aggregate(pipeline, session=session)
        documents = await cursor.to_list(length=1)

        if not documents:
            raise ObjectNotFoundException(code)

        return Group(**documents[0])

    async def find_by_parent_code(
        self, *, parent_code: str, session: AsyncIOMotorClientSession | None = None
    ) -> list[Group]:
        """Find all groups by parent code."""
        match_filter = {"parent_code": parent_code}

        pipeline = self._build_group_aggregation_pipeline(match_filter=match_filter)

        cursor = self._collection.aggregate(pipeline, session=session)
        groups = []
        async for document in cursor:
            if document is not None:
                groups.append(Group(**document))

        return groups

    async def find_all(
        self,
        *,
        query_parameters: GroupQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Group]:
        """Find all groups with pagination."""
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

        sort_field = query_parameters.sort_field or "name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        match_filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {match_filter}")

        additional_stages = [
            {"$sort": {sort_field: direction}},
            {"$skip": skip},
            {"$limit": limit},
        ]

        pipeline = self._build_group_aggregation_pipeline(
            match_filter=match_filter, additional_stages=additional_stages
        )

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        if projection:
            pipeline.append({"$project": projection})

        logger.debug(f"Pipeline: {pipeline}")

        cursor = self._collection.aggregate(pipeline, session=session)

        # convert cursor to list of groups
        groups = []
        async for document in cursor:
            if document is not None:
                groups.append(Group(**document))

        logger.debug(f"Found {len(groups)} groups")

        return groups

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: GroupQueryParameters,
        max_limit: int = MAX_LIMIT,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Group]:
        """Find all groups without pagination."""
        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        match_filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {match_filter}")

        additional_stages = [
            {"$sort": {sort_field: direction}},
            {"$limit": max_limit},
        ]

        pipeline = self._build_group_aggregation_pipeline(
            match_filter=match_filter, additional_stages=additional_stages
        )

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        if projection:
            pipeline.append({"$project": projection})

        logger.debug(f"Pipeline: {pipeline}")

        cursor = self._collection.aggregate(pipeline, session=session)

        # convert cursor to list of groups
        groups = []
        async for document in cursor:
            if document is not None:
                groups.append(Group(**document))

        logger.debug(f"Found {len(groups)} groups")

        return groups

    async def count(
        self,
        *,
        query_parameters: GroupQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of groups."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    def _build_group_aggregation_pipeline(
        self, *, match_filter: dict[str, Any], additional_stages: list[dict] = None
    ) -> list[dict]:
        """Build common aggregation pipeline for group queries with roles lookup."""
        pipeline = [
            {"$match": match_filter},
            {
                "$addFields": {
                    "role_object_ids": {
                        "$map": {
                            "input": {"$ifNull": ["$role_ids", []]},
                            "as": "roleId",
                            "in": {"$toObjectId": "$$roleId"},
                        }
                    }
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
            {"$unset": ["role_object_ids"]},
        ]

        # Add additional stages if provided
        if additional_stages:
            pipeline.extend(additional_stages)

        return pipeline

    async def find_all_query(
        self, *, query_parameters: GroupQueryParameters
    ) -> dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: dict[str, Any] = {}

        if query_parameters.keyword:
            keyword_regex = {
                "$regex": get_escaped_regex_pattern(query_parameters.keyword),
                "$options": "i",
            }
            filter["$or"] = [
                {"code": keyword_regex},
                {"name": keyword_regex},
            ]

        if query_parameters.parent_code:
            filter["parent_code"] = query_parameters.parent_code

        return filter
