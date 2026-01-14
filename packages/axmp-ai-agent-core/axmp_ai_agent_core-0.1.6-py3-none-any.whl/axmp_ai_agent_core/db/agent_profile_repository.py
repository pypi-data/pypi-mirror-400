"""Agent profile repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from axmp_ai_agent_core.db.base_repository import BaseRepository
from axmp_ai_agent_core.entity.agent_profile import (
    AgentProfile,
)
from axmp_ai_agent_core.entity.shared_target import SharedTarget
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from axmp_ai_agent_core.filter.agent_profile_query import (
    AgentProfileListType,
    AgentProfileQueryParameters,
)
from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_LIMIT,
    SortDirection,
)
from axmp_ai_agent_core.util.search_utils import get_escaped_regex_pattern
from axmp_ai_agent_core.util.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger(__name__)


class AgentProfileRepository(BaseRepository[AgentProfile]):
    """Agent profile repository."""

    async def insert(
        self, *, item: AgentProfile, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new agent profile into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        # model_dump will convert datetime to string
        # so we need to set again datetime filed with datetime object
        agent_profile_dict = item.model_dump(by_alias=True, exclude=["id"])
        agent_profile_dict["created_at"] = item.created_at

        result: InsertOneResult = await self._collection.insert_one(
            agent_profile_dict, session=session
        )

        return str(result.inserted_id)

    async def update(
        self, *, item: AgentProfile, session: AsyncIOMotorClientSession | None = None
    ) -> AgentProfile | None:
        """Update an agent profile in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        # model_dump will convert datetime to string
        # so we need to set again datetime filed with datetime object
        agent_profile_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
            ],
        )
        agent_profile_dict["updated_at"] = item.updated_at

        update = [{"$set": agent_profile_dict}]

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if document is None:
            raise ObjectNotFoundException(item.id)

        return AgentProfile(**document)

    async def update_is_published_to_workspace(
        self,
        *,
        item_id: str,
        is_published_to_workspace: bool,
        updated_by: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> AgentProfile:
        """Update the is_published_to_workspace field for an agent profile."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        updated_at = datetime.now(DEFAULT_TIME_ZONE)

        update = [
            {
                "$set": {
                    "is_published_to_workspace": is_published_to_workspace,
                    "updated_by": updated_by,
                    "updated_at": updated_at,
                }
            }
        ]

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if document is None:
            raise ObjectNotFoundException(item_id)

        return AgentProfile(**document)

    async def update_shared_target(
        self,
        *,
        item_id: str,
        shared_target: SharedTarget,
        updated_by: str,
        session: AsyncIOMotorClientSession | None = None,
    ) -> AgentProfile:
        """Update only shared_target and audit fields for an agent profile."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        updated_at = datetime.now(DEFAULT_TIME_ZONE)

        update = [
            {
                "$set": {
                    "shared_target": shared_target.model_dump(),
                    "updated_by": updated_by,
                    "updated_at": updated_at,
                }
            }
        ]

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if document is None:
            raise ObjectNotFoundException(item_id)

        return AgentProfile(**document)

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete an agent profile from the repository."""
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
    ) -> AgentProfile | None:
        """Find an agent profile by ID with root node information extracted using pipeline."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return AgentProfile(**document)

    async def find_by_name(
        self, *, name: str, session: AsyncIOMotorClientSession | None = None
    ) -> AgentProfile | None:
        """Find an agent profile by root node name."""
        filter = {"name": name}

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            return None

        return AgentProfile(**document)

    async def find_by_system_name(
        self, *, system_name: str, session: AsyncIOMotorClientSession | None = None
    ) -> AgentProfile | None:
        """Find an agent profile by root node system name."""
        filter = {"system_name": system_name}

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            return None

        return AgentProfile(**document)

    async def find_all(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = ["flow"],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[AgentProfile]:
        """Find all agent profiles with root node information extracted using pipeline."""
        if page_number < 1:
            page_number = DEFAULT_PAGE_NUMBER
        if page_size < 1:
            page_size = DEFAULT_PAGE_SIZE

        filter = await self.find_all_query(
            query_parameters=query_parameters,
        )

        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        sort_field = query_parameters.sort_field
        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        skip = (page_number - 1) * page_size
        limit = min(page_size, MAX_LIMIT)

        cursor = (
            self._collection.find(filter, projection=projection, session=session)
            .sort(sort_field, direction)
            .skip(skip)
            .limit(limit)
        )

        # convert cursor to list of agent profiles
        agent_profiles = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    agent_profiles.append(AgentProfile(**document))

        return agent_profiles

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        max_limit: int = MAX_LIMIT,
        exclude_fields: list[str] = ["flow"],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[AgentProfile]:
        """Find all agent profiles in the repository without pagination."""
        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "name"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        cursor = (
            self._collection.find(
                filter, projection=projection if projection else None, session=session
            )
            .sort(sort_field, direction)
            .limit(max_limit)
        )

        # convert cursor to list of agent profiles
        agent_profiles = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    agent_profiles.append(AgentProfile(**document))

        logger.debug(f"Found {len(agent_profiles)} agent profiles")

        return agent_profiles

    async def count(
        self,
        *,
        query_parameters: AgentProfileQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of agent profiles in the repository."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    async def find_all_query(
        self, *, query_parameters: AgentProfileQueryParameters
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: Dict[str, Any] = {}

        if query_parameters.keyword:
            keyword_regex = {
                "$regex": get_escaped_regex_pattern(query_parameters.keyword),
                "$options": "i",
            }
            filter["$or"] = [
                {"name": keyword_regex},
                {"system_name": keyword_regex},
                {"description": keyword_regex},
            ]
        if query_parameters.list_type:
            if query_parameters.list_type == AgentProfileListType.MY_AGENTS:
                filter["created_by"] = query_parameters.created_by
            elif query_parameters.list_type == AgentProfileListType.SHARED_AGENTS:
                filter["created_by"] = {"$ne": query_parameters.created_by}
        else:
            if query_parameters.created_by:
                filter["created_by"] = query_parameters.created_by

        if query_parameters.updated_by:
            filter["updated_by"] = query_parameters.updated_by

        if query_parameters.statuses:
            filter["status"] = {"$in": query_parameters.statuses}

        if query_parameters.types:
            filter["type"] = {"$in": query_parameters.types}

        if query_parameters.runtime_types:
            filter["runtime_type"] = {"$in": query_parameters.runtime_types}

        if query_parameters.usage_types:
            filter["usage_type"] = {"$in": query_parameters.usage_types}

        if query_parameters.provisioned is not None:
            if query_parameters.provisioned:
                filter["provisioned_version"] = {"$ne": None, "$exists": True}
            else:
                filter["provisioned_version"] = {"$eq": None, "$exists": True}

        if query_parameters.labels and query_parameters.parsed_labels:
            for label in query_parameters.parsed_labels:
                filter.update({f"labels.{label.key}": label.value})

        if query_parameters.access_permission:
            shared_target_filter = await self._build_shared_target_filter(
                access_permission=query_parameters.access_permission
            )
            # Combine existing filter and shared_target_filter with $and
            if filter:
                filter = {"$and": [filter, shared_target_filter]}
            else:
                filter = shared_target_filter

        logger.debug(f"Filter: {filter}")

        return filter
