"""Base model for the AI Core."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_serializer

PyObjectId = Annotated[str, BeforeValidator(str)]


class CoreBaseModel(BaseModel):
    """Core Base Model.

    mongodb objectId _id issues

    refence:
    https://github.com/tiangolo/fastapi/issues/1515
    https://github.com/mongodb-developer/mongodb-with-fastapi
    """

    id: PyObjectId | None = Field(default=None, alias="_id")

    created_by: str | None = None
    updated_by: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )

    @field_serializer("id")
    def _serialize_id(self, id: PyObjectId | None) -> str | None:
        if id is None:
            return None
        else:
            return str(id)

    @field_serializer("created_at", "updated_at")
    def _serialize_created_updated_at(self, dt: datetime | None) -> str | None:
        return dt.isoformat(timespec="milliseconds") if dt else None


class NamedCoreBaseModel(CoreBaseModel):
    """Named Core Base Model.

    A model that inherits from CoreBaseModel and adds name and system_name fields.
    """

    name: str | None = Field(
        None, max_length=255, description="Entity name for display"
    )
    system_name: str | None = Field(
        None, max_length=255, description="System name for internal use"
    )
