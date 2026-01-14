"""Exceptions for DB operations."""

from bson.errors import InvalidId


class ObjectNotFoundException(Exception):
    """Object not found exception."""

    def __init__(self, object_id: str):
        """Initialize the ObjectNotFoundException."""
        self.object_id = object_id
        self.message = f"The ID '{object_id}' was not found"
        super().__init__(self.message)


class InvalidObjectIDException(InvalidId):
    """Invalid ObjectId exception."""


class ValueErrorException(Exception):
    """Value Error exception."""

    def __init__(self, message: str):
        """Initialize the ValueErrorException."""
        self.message = message
        super().__init__(self.message)
