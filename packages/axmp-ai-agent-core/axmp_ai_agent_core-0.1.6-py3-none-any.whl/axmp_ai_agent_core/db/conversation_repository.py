"""Conversation repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult

from axmp_ai_agent_core.db.base_repository import BaseRepository
from axmp_ai_agent_core.entity.chat_conversation import Conversation
from axmp_ai_agent_core.exception.db_exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
    ValueErrorException,
)
from axmp_ai_agent_core.filter.chat_conversation_query import (
    ConversationQueryParameters,
)
from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_LIMIT,
    SortDirection,
)
from axmp_ai_agent_core.util.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger(__name__)


class ConversationRepository(BaseRepository[Conversation]):
    """Conversation repository."""

    async def insert(
        self, *, item: Conversation, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new conversation into the repository."""
        if item.created_at is None:
            item.created_at = datetime.now(DEFAULT_TIME_ZONE)

        conversation_dict = item.model_dump(by_alias=True, exclude=["id"])
        conversation_dict["created_at"] = item.created_at
        conversation_dict["updated_at"] = item.created_at

        try:
            result: InsertOneResult = await self._collection.insert_one(
                conversation_dict, session=session
            )

            return str(result.inserted_id)
        except DuplicateKeyError as e:
            raise ValueErrorException(
                f"Conversation thread_id {item.thread_id} already exists. Details: {e}"
            )

    async def update(
        self, *, item: Conversation, session: AsyncIOMotorClientSession | None = None
    ) -> Conversation | None:
        """Update a conversation in the repository."""
        try:
            filter = {"_id": ObjectId(item.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if item.updated_at is None:
            item.updated_at = datetime.now(DEFAULT_TIME_ZONE)

        conversation_dict = item.model_dump(
            by_alias=True,
            exclude=[
                "id",
                "created_at",
                "created_by",
            ],
        )
        conversation_dict["updated_at"] = item.updated_at

        update = {"$set": conversation_dict}

        document = await self._collection.find_one_and_update(
            filter=filter,
            update=update,
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        if document is None:
            raise ObjectNotFoundException(item.id)

        return Conversation(**document)

    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete a conversation from the repository."""
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
    ) -> Conversation | None:
        """Find a conversation by ID."""
        try:
            filter = {"_id": ObjectId(item_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(item_id)

        return Conversation(**document)

    async def find_by_thread_id(
        self, *, thread_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> Conversation | None:
        """Find a conversation by thread ID."""
        filter = {"thread_id": thread_id}

        document = await self._collection.find_one(filter=filter, session=session)

        if document is None:
            raise ObjectNotFoundException(thread_id)

        return Conversation(**document)

    async def find_all(
        self,
        *,
        query_parameters: ConversationQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_PAGE_SIZE,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Conversation]:
        """Find all conversations in the repository."""
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

        conversations = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    conversations.append(Conversation(**document))

        return conversations

    async def find_all_without_pagination(
        self,
        *,
        query_parameters: ConversationQueryParameters,
        max_limit: int = MAX_LIMIT,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Conversation]:
        """Find all conversations in the repository without pagination."""
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

        cursor = (
            self._collection.find(filter, projection=projection, session=session)
            .sort(sort_field, direction)
            .limit(max_limit)
        )

        conversations = []
        if cursor is not None:
            async for document in cursor:
                if document is not None:
                    conversations.append(Conversation(**document))

        logger.debug(f"Found {len(conversations)} conversations")

        return conversations

    async def count(
        self,
        *,
        query_parameters: ConversationQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of conversations in the repository."""
        filter = await self.find_all_query(query_parameters=query_parameters)

        logger.debug(f"Filter: {filter}")

        return await self._collection.count_documents(filter=filter, session=session)

    async def find_all_query(
        self, *, query_parameters: ConversationQueryParameters
    ) -> Dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        filter: Dict[str, Any] = {}

        # if query_parameters.keyword:
        #     keyword_regex = {
        #         "$regex": get_escaped_regex_pattern(query_parameters.keyword),
        #         "$options": "i",
        #     }
        #     filter["$or"] = [
        #         {"title": keyword_regex},
        #         {"message": keyword_regex},
        #     ]

        if hasattr(query_parameters, "user_id") and query_parameters.user_id:
            filter["user_id"] = query_parameters.user_id

        if hasattr(query_parameters, "agent_id") and query_parameters.agent_id:
            filter["agent_id"] = query_parameters.agent_id

        if hasattr(query_parameters, "project_id") and query_parameters.project_id:
            filter["project_id"] = query_parameters.project_id

        if (
            hasattr(query_parameters, "starred")
            and query_parameters.starred is not None
        ):
            filter["starred"] = query_parameters.starred

        return filter
