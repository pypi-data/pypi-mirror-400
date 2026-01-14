"""Exceptions for AI Agent Studio."""

from enum import Enum
from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel


class Error(BaseModel):
    """Error model."""

    http_status: int | None
    code: str | None
    message: str | None


class CoreError(Enum):
    """Core error model."""

    ID_NOT_FOUND = Error(
        code="E001",
        http_status=HTTPStatus.NOT_FOUND,
        message="The item was not found. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    INVALID_OBJECTID = Error(
        code="E002",
        http_status=HTTPStatus.BAD_REQUEST,
        message="The input value was invalid. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    DUPLICATE_FOUND = Error(
        code="E004",
        http_status=HTTPStatus.CONFLICT,
        message="Duplicate item found. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    BAD_REQUEST = Error(
        code="E003",
        http_status=HTTPStatus.BAD_REQUEST,
        message="Bad request. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    PERMISSION_DENIED = Error(
        code="E005",
        http_status=HTTPStatus.FORBIDDEN,
        message="Permission denied. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    SESSION_EXPIRED = Error(
        code="E007",
        http_status=HTTPStatus.UNAUTHORIZED,
        message="The session is expired. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    INTERNAL_SERVER_ERROR = Error(
        code="E500",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message="Internal server error. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    MESSAGE_NOT_FOUND = Error(
        code="E008",
        http_status=HTTPStatus.NOT_FOUND,
        message="The message was not found. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    NOT_PUBLISHED_TO_WORKSPACE = Error(
        code="E009",
        http_status=HTTPStatus.FORBIDDEN,
        message="The agent profile is not published to the workspace. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""

    NO_STABLE_VERSION_FOUND = Error(
        code="E010",
        http_status=HTTPStatus.BAD_REQUEST,
        message="The agent profile has no stable version. Details: {details}",
    )
    """The keyword argument '{details}' should be present in the message string"""


class CoreServiceException(HTTPException):
    """Core service exception."""

    def __init__(self, error: CoreError, **kwargs):
        """Initialize the Core service exception."""
        self.status_code = error.value.http_status
        self.code = error.value.code
        self.detail = error.value.message.format(**kwargs)
        super().__init__(status_code=self.status_code, detail=self.detail)
