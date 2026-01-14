"""Base repository for MongoDB operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorCollection

from axmp_ai_agent_core.entity.shared_target import SharedType
from axmp_ai_agent_core.entity.user_rbac import AccessPermission
from axmp_ai_agent_core.exception.db_exceptions import ValueErrorException
from axmp_ai_agent_core.filter.base_search_query import BaseQueryParameters
from axmp_ai_agent_core.util.list_utils import (
    DEFAULT_CARD_PAGE_SIZE,
    DEFAULT_PAGE_NUMBER,
    MAX_LIMIT,
)

T = TypeVar("T")


class BaseRepository[T](ABC):
    """BaseRepository class to handle MongoDB operation."""

    def __init__(
        self,
        *,
        collection: AsyncIOMotorCollection,
    ):
        """Initialize the repository with MongoDB database."""
        self._collection = collection

    # TODO: implement the initialize index function using another way instead of classmethod of this class
    # because the this class is provided in the factory pattern by DI container,
    # it is not possible to use classmethod to initialize the index.

    # @classmethod
    # async def create(cls, *, collection: AsyncIOMotorCollection) -> BaseRepository[T]:
    #     """Create a new instance of the repository."""
    #     instance = cls(collection=collection)
    #     await instance.init_index()
    #     return instance

    # @abstractmethod
    # async def init_index(self) -> None:
    #     """Initialize the index."""
    #     pass

    @abstractmethod
    async def insert(
        self, *, item: T, session: AsyncIOMotorClientSession | None = None
    ) -> str:
        """Insert a new item into the repository."""
        pass

    @abstractmethod
    async def update(
        self, *, item: T, session: AsyncIOMotorClientSession | None = None
    ) -> T | None:
        """Update an item in the repository."""
        pass

    @abstractmethod
    async def delete(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> bool:
        """Delete an item from the repository."""
        pass

    @abstractmethod
    async def find_by_id(
        self, *, item_id: str, session: AsyncIOMotorClientSession | None = None
    ) -> T | None:
        """Find one item in the repository."""
        pass

    @abstractmethod
    async def find_all(
        self,
        *,
        query_parameters: BaseQueryParameters,
        page_number: int = DEFAULT_PAGE_NUMBER,
        page_size: int = DEFAULT_CARD_PAGE_SIZE,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[T]:
        """Find all items in the repository."""
        pass

    @abstractmethod
    async def find_all_without_pagination(
        self,
        *,
        query_parameters: BaseQueryParameters,
        max_limit: int = MAX_LIMIT,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[T]:
        """Find all items in the repository without pagination."""
        pass

    @abstractmethod
    async def count(
        self,
        *,
        query_parameters: BaseQueryParameters,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Count the number of items in the repository."""
        pass

    @abstractmethod
    async def find_all_query(
        self,
        *,
        query_parameters: BaseQueryParameters,
    ) -> dict[str, Any]:
        """Generate a query for the find_all and count functions."""
        pass

    async def _build_projection(
        self,
        *,
        exclude_fields: list[str] = [],
        include_fields: list[str] = [],
    ) -> dict[str, Any]:
        """Build a projection for the find_all and count functions."""
        if exclude_fields and include_fields:
            if len(exclude_fields) > 0 and len(include_fields) > 0:
                raise ValueErrorException(
                    "The exclude_fields and include_fields cannot be used together."
                )
        projection = None
        if include_fields and len(include_fields) > 0:
            projection = {field: 1 for field in include_fields}
            if "_id" not in include_fields:
                projection["_id"] = 1

        if exclude_fields and len(exclude_fields) > 0:
            if "_id" in exclude_fields:
                del projection["_id"]
            projection = {field: 0 for field in exclude_fields}

        if projection is None:
            projection = {}

        return projection

    async def _build_shared_target_filter(
        self,
        *,
        access_permission: AccessPermission,
    ) -> dict[str, Any]:
        """Build a shared target filter for the find_all and count functions."""
        # 1st. if document's data - shared_target.accss_type == PUBLIC
        # 2nd. created_by is in the access_permission.username
        # 3rd. if the query_parameters.access_permission.username in the document's shared_target.shared_users
        # 4th. if the query_parameters.accss_permission.group_ids in the document's shared_target.group_ids
        filter = {}
        filter["$or"] = [
            {"shared_target.shared_type": SharedType.PUBLIC.value},
            {"created_by": access_permission.username},
            {
                "shared_target.shared_users": {
                    "$elemMatch": {"username": access_permission.username}
                }
            },
            {
                "shared_target.shared_groups": {
                    "$elemMatch": {
                        "group_ids": {
                            "$in": [
                                group_id for group_id in access_permission.group_ids
                            ]
                        }
                    }
                }
            },
        ]

        return filter
