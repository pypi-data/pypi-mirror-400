"""Agent profile history repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.collation import Collation
from pymongo.results import InsertOneResult

from axmp_ai_agent_core.db.base_repository import BaseRepository
from axmp_ai_agent_core.entity.agent_profile_history import AgentProfileHistory
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
    ValueErrorException,
)
from axmp_ai_agent_core.filter.agent_profile_history_query import (
    AgentProfileHistoryQueryParameters,
)
from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_LIMIT,
    SortDirection,
)
from axmp_ai_agent_core.util.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger(__name__)


class AgentProfileHistoryRepository(BaseRepository[AgentProfileHistory]):
    """Agent profile history repository."""

    async def insert(
        self,
        *,
        item: AgentProfileHistory,
        session: AsyncIOMotorClientSession | None = None,
    ) -> str:
        """Insert a new agent profile history into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        history_dict = item.model_dump(by_alias=True, exclude=["id"])
        history_dict["created_at"] = item.created_at

        result: InsertOneResult = await self._collection.insert_one(
            history_dict, session=session
        )

        return str(result.inserted_id)

    async def update(
        self,
        *,
        item: AgentProfileHistory,
        session: AsyncIOMotorClientSession | None = None,
    ) -> AgentProfileHistory | None:
        """Update an agent profile history in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        history_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
            ],
        )
        history_dict["updated_at"] = item.updated_at

        update = [{"$set": history_dict}]

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )

        if document is None:
            raise ObjectNotFoundException(item.id)

        return AgentProfileHistory(**document)

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete an agent profile history from the repository."""
        try:
            query = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one_and_delete(query, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return True

    async def delete_by_agent_profile_id(
        self, *, agent_profile_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> int:
        """Delete all agent profile histories by agent profile ID."""
        filter = {"agent_profile_id": agent_profile_id}

        # Get count before deletion for return value
        count = await self._collection.count_documents(filter, session=session)

        if count == 0:
            raise ObjectNotFoundException(
                f"No agent profile histories found for profile ID: {agent_profile_id}"
            )

        # Delete all matching documents
        result = await self._collection.delete_many(filter, session=session)

        logger.debug(
            f"Deleted {result.deleted_count} agent profile histories for profile ID: {agent_profile_id}"
        )

        return result.deleted_count

    async def find_by_id(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> AgentProfileHistory | None:
        """Find an agent profile history by ID."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return AgentProfileHistory(**document)

    async def find_by_profile_id_and_version(
        self,
        *,
        profile_id: str,
        version: int,
        session: AsyncIOMotorClientSession | None = None,
    ) -> AgentProfileHistory | None:
        """Find an agent profile history by profile_id and version."""
        try:
            filter = {"agent_profile_id": profile_id, "version": version}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(f"{profile_id}:{version}")

        return AgentProfileHistory(**document)

    async def find_all(
        self,
        *,
        query_parameters: AgentProfileHistoryQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = ["agent_profile_data"],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[AgentProfileHistory]:
        """Find all agent profile histories in the repository."""
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

        sort_field = query_parameters.sort_field or "created_at"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(
            query_parameters=query_parameters,
        )

        logger.debug(f"Filter: {filter}")

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        base_cursor = self._collection.find(
            filter, projection=projection, session=session
        )
        if (getattr(sort_field, "value", sort_field)) == "version":
            base_cursor = base_cursor.collation(
                Collation(locale="en", numericOrdering=True)
            )
        cursor = base_cursor.sort(sort_field, direction).skip(skip).limit(limit)

        agent_profile_histories = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    agent_profile_histories.append(AgentProfileHistory(**document))

        return agent_profile_histories

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: AgentProfileHistoryQueryParameters,
        max_limit: int = MAX_LIMIT,  # if max_limit is 0, don't apply limit
        exclude_fields: list[str] = ["agent_profile_data"],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[AgentProfileHistory]:
        """Find all agent profile histories in the repository without pagination."""
        if exclude_fields and include_fields:
            if len(exclude_fields) > 0 and len(include_fields) > 0:
                raise ValueErrorException(
                    "exclude_fields and include_fields cannot be used together"
                )

        direction = (
            pymongo.ASCENDING
            if query_parameters.sort_direction == SortDirection.ASC
            else pymongo.DESCENDING
        )

        sort_field = query_parameters.sort_field or "created_at"

        logger.debug(
            f"sort_field: {query_parameters.sort_field}, direction: {query_parameters.sort_direction} ({direction})"
        )

        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        # Build projection
        projection = await self._build_projection(
            exclude_fields=exclude_fields, include_fields=include_fields
        )

        # Create base cursor without limit
        base_cursor = self._collection.find(
            filter, projection=projection, session=session
        )
        if (getattr(sort_field, "value", sort_field)) == "version":
            base_cursor = base_cursor.collation(
                Collation(locale="en", numericOrdering=True)
            )
        cursor = base_cursor.sort(sort_field, direction)

        # Apply limit only if max_limit > 0
        if max_limit > 0:
            cursor = cursor.limit(max_limit)

        agent_profile_histories = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    agent_profile_histories.append(AgentProfileHistory(**document))

        logger.debug(f"Found {len(agent_profile_histories)} agent profile histories")

        return agent_profile_histories

    async def count(
        self,
        *,
        query_parameters: AgentProfileHistoryQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of agent profile histories in the repository."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    async def find_all_query(
        self, *, query_parameters: AgentProfileHistoryQueryParameters
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: Dict[str, Any] = {}

        if query_parameters.agent_profile_id:
            filter["agent_profile_id"] = query_parameters.agent_profile_id

        if query_parameters.version:
            filter["version"] = query_parameters.version

        if query_parameters.created_by:
            filter["created_by"] = query_parameters.created_by

        if query_parameters.updated_by:
            filter["updated_by"] = query_parameters.updated_by

        return filter

    async def get_max_version(
        self, *, agent_profile_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> int:
        """Get the max version of the agent profile history."""
        cursor = self._collection.aggregate(
            [
                {"$match": {"agent_profile_id": agent_profile_id}},
                {"$group": {"_id": None, "maxVersion": {"$max": "$version"}}},
            ],
            session=session,
        )
        documents = await cursor.to_list(length=1)
        if not documents or len(documents) == 0:
            return 0
        document = documents[0]
        return document["maxVersion"]
