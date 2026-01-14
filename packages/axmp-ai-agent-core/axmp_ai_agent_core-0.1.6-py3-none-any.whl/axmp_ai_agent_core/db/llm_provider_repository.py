"""LLM provider repository."""

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
from axmp_ai_agent_core.entity.llm_provider import LlmProvider
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
    ValueErrorException,
)
from axmp_ai_agent_core.filter.configuration_query import (
    LlmProviderQueryParameters,
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


class LlmProviderRepository(BaseRepository[LlmProvider]):
    """LLM provider repository."""

    async def insert(
        self, *, item: LlmProvider, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new LLM provider into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        llm_provider_dict = item.model_dump(by_alias=True, exclude=["id"])
        llm_provider_dict["created_at"] = item.created_at

        result: InsertOneResult = await self._collection.insert_one(
            llm_provider_dict, session=session
        )

        return str(result.inserted_id)

    async def update(
        self, *, item: LlmProvider, session: AsyncIOMotorClientSession | None = None
    ) -> LlmProvider | None:
        """Update an LLM provider in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        llm_provider_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
            ],
        )
        llm_provider_dict["updated_at"] = item.updated_at

        update = {"$set": llm_provider_dict}

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        if document is None:
            raise ObjectNotFoundException(item.id)

        return LlmProvider(**document)

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete an LLM provider from the repository."""
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
    ) -> LlmProvider | None:
        """Find an LLM provider by ID."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return LlmProvider(**document)

    async def get_id_by_key(
        self, *, key: str, session: AsyncIOMotorClientSession | None = None
    ) -> str | None:
        """Get the ID of an LLM provider by key."""
        try:
            filter = {"key": key}
        except InvalidId:
            return None

        document = await self._collection.find_one(filter=filter, session=session)
        if document is None:
            raise ObjectNotFoundException(key)

        logger.debug(f"document: {document}")
        document_id = document["_id"] if document else None
        return str(document_id)

    async def find_all(
        self,
        *,
        query_parameters: LlmProviderQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[LlmProvider]:
        """Find all LLM providers in the repository."""
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

        llm_providers = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    llm_providers.append(LlmProvider(**document))

        return llm_providers

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: LlmProviderQueryParameters,
        max_limit: int = MAX_LIMIT,  # if max_limit is 0, don't apply limit
        exclude_fields: list[str] = [],
        include_fields: list[str] = [
            "key",
            "display_name",
            "icon_url",
            "base_url",
            "status",
        ],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[LlmProvider]:
        """Find all LLM providers in the repository without pagination."""
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
            .limit(max_limit)
        )

        llm_providers = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    llm_providers.append(LlmProvider(**document))

        logger.debug(f"Found {len(llm_providers)} LLM providers")

        return llm_providers

    async def count(
        self,
        *,
        query_parameters: LlmProviderQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of LLM providers in the repository."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    async def find_all_query(
        self, *, query_parameters: LlmProviderQueryParameters
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: Dict[str, Any] = {}

        if query_parameters.keyword:
            keyword_regex = {
                "$regex": get_escaped_regex_pattern(query_parameters.keyword),
                "$options": "i",
            }
            filter["$or"] = [
                {"key": keyword_regex},
                {"display_name": keyword_regex},
            ]

        if hasattr(query_parameters, "created_by") and query_parameters.created_by:
            filter["created_by"] = query_parameters.created_by

        if hasattr(query_parameters, "updated_by") and query_parameters.updated_by:
            filter["updated_by"] = query_parameters.updated_by

        if query_parameters.statuses:
            filter["status"] = {
                "$in": [status.value for status in query_parameters.statuses]
            }

        return filter
